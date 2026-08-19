import cv2
import numpy as np
from fastapi import APIRouter, File, UploadFile, Depends, Request
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.schemas.recognition import RecognizeResponse
from backend.services.attendance_service import AttendanceService

router = APIRouter(tags=["Recognition"])

@router.post("/recognize", response_model=RecognizeResponse)
async def recognize_face(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. Read file bytes
    try:
        contents = await file.read()
        if not contents:
            return RecognizeResponse(
                recognized=False,
                person=None,
                similarity=None,
                message="No face detected"
            )
        np_arr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except Exception:
        return RecognizeResponse(
            recognized=False,
            person=None,
            similarity=None,
            message="Invalid image file"
        )

    if image is None or image.size == 0:
        return RecognizeResponse(
            recognized=False,
            person=None,
            similarity=None,
            message="Invalid image file"
        )

    # 2. Get services from app state
    face_detector = request.app.state.face_detector
    face_recognizer = request.app.state.face_recognizer
    gallery = request.app.state.gallery

    # 3. Detect faces
    faces = face_detector.detect_faces(image)

    if len(faces) == 0:
        return RecognizeResponse(
            recognized=False,
            person=None,
            similarity=None,
            message="No face detected"
        )

    if len(faces) > 1:
        return RecognizeResponse(
            recognized=False,
            person=None,
            similarity=None,
            message="Multiple faces detected"
        )

    # 4. Generate embedding for single detected face
    face_crop = faces[0]["crop"]
    embedding = face_recognizer.get_embedding(face_crop)

    if embedding is None:
        return RecognizeResponse(
            recognized=False,
            person=None,
            similarity=None,
            message="Failed to generate face embedding"
        )

    # 5. Recognize against gallery
    is_recognized, person_name, similarity = gallery.recognize(embedding)

    if is_recognized and person_name:
        # Mark attendance if not already marked for today
        _, created = AttendanceService.mark_attendance(db, person_name)
        msg = "Attendance marked" if created else "Attendance already marked for today"
        return RecognizeResponse(
            recognized=True,
            person=person_name,
            similarity=similarity,
            message=msg
        )
    else:
        return RecognizeResponse(
            recognized=False,
            person=None,
            similarity=similarity if similarity > 0 else None,
            message="Unknown person"
        )

