# Backend Implementation & FastAPI Beginner Notes

This document provides a line-by-line explanation of the FastAPI backend implementation for the **Face Attendance System**. It covers FastAPI fundamentals, model loading lifecycle, database configuration, and logic for preventing duplicate attendance records.

---

## Table of Contents
1. [FastAPI Core Concepts (For Beginners)](#1-fastapi-core-concepts-for-beginners)
2. [Work Item #1: FastAPI Setup, Lifecycle & AI Model Loading](#2-work-item-1-fastapi-setup-lifecycle--ai-model-loading)
   - [Database Connection & Session Setup (`database/database.py`)](#database-connection--session-setup-databasedatabasepy)
   - [Application Entrypoint & Lifespan (`main.py`)](#application-entrypoint--lifespan-mainpy)
   - [AI Model Loading Architecture (`services/`)](#ai-model-loading-architecture-services)
   - [Face Recognition Endpoint (`routes/recognition.py`)](#face-recognition-endpoint-routesrecognitionpy)
3. [Work Item #2: Database Models & Duplicate Attendance Prevention](#3-work-item-2-database-models--duplicate-attendance-prevention)
   - [Database Table Model (`database/models.py`)](#database-table-model-databasemodelspy)
   - [Attendance Service Logic (`services/attendance_service.py`)](#attendance-service-logic-servicesattendance_servicepy)
   - [Attendance API Routes (`routes/attendance.py`)](#attendance-api-routes-routesattendancepy)
4. [Summary & Key Takeaways](#4-summary--key-takeaways)

---

## 1. FastAPI Core Concepts (For Beginners)

If you are new to FastAPI, here are the essential concepts used across this backend:

*   **FastAPI Instance (`FastAPI()`)**: The central application object that handles incoming HTTP requests, manages routes, middleware, and application events.
*   **Uvicorn**: An ASGI (Asynchronous Server Gateway Interface) web server implementation used to run FastAPI applications in Python.
*   **APIRouter (`APIRouter`)**: Allows you to divide your backend API into modular, manageable route files (e.g., separating recognition endpoints from attendance endpoints).
*   **Dependency Injection (`Depends`)**: A mechanism in FastAPI that automatically prepares and passes required objects (like database sessions) into request handler functions, ensuring cleanup when the request finishes.
*   **App State (`app.state`)**: A shared dictionary attached to the FastAPI application instance where heavy objects (like loaded AI neural networks) can be stored once and accessed anywhere.
*   **SQLAlchemy ORM**: An Object-Relational Mapper that translates Python classes into database tables and Python queries into SQL statements.

---

## 2. Work Item #1: FastAPI Setup, Lifecycle & AI Model Loading

### Overview of Work #1
In the first phase, we established the core FastAPI web application structure, integrated ONNX Runtime neural network models for face detection (SCRFD) and face recognition (MobileFaceNet), loaded reference facial embeddings into memory at startup, and exposed the `/recognize` POST endpoint.

---

### Configuration & Database URL (`config.py`)

Before creating database connections in `database.py`, the backend needs to know **where** the database resides. This is configured in `backend/config.py`:

```python
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database Path
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(BASE_DIR, 'attendance.db')}"
)
```

#### How `DATABASE_URL` Works:
1. **`DATABASE_URL` definition**: `os.getenv("DATABASE_URL", ...)` first checks if an environment variable named `DATABASE_URL` exists. If not, it falls back to a default SQLite connection string: `sqlite:///<path>/attendance.db`.
2. **What is SQLite?**: SQLite is a serverless, file-based SQL database built directly into Python. You do not need to install an external database server like PostgreSQL or MySQL.
3. **Automatic Creation**: The database file `attendance.db` does not need to exist initially. When FastAPI starts up and executes `Base.metadata.create_all(bind=engine)` in `main.py`, SQLite automatically creates the `attendance.db` file in your `backend` directory if it does not already exist.

---

### Database Connection & Session Setup (`database/database.py`)

Here is `backend/database/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### Line-by-Line Breakdown:
*   **Line 1–4**: Imports `create_engine`, `declarative_base`, and `sessionmaker` from SQLAlchemy, alongside `DATABASE_URL` imported from `backend.config`.
*   **Line 6–9 (`engine = create_engine(...)`)**: Creates the connection engine using `DATABASE_URL`. For SQLite (`sqlite:///...`), `check_same_thread=False` allows FastAPI asynchronous worker threads to interact with the database.
*   **Line 11 (`SessionLocal = sessionmaker(...)`)**: Defines a factory class for database sessions (`autocommit=False`, `autoflush=False`).
*   **Line 13 (`Base = declarative_base()`)**: Creates the base class for all table models.
*   **Line 15–20 (`get_db()`)**: A FastAPI **Dependency Injection** generator function:
    *   `db = SessionLocal()` creates a new session per incoming HTTP request.
    *   `yield db` delivers the session to the route function.
    *   `finally: db.close()` automatically closes the connection after the request completes.

---

### Application Entrypoint & Lifespan (`main.py`)

Here is `backend/main.py`:

```python
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.database import engine, Base
from backend.services.face_detector import FaceDetector
from backend.services.face_recognizer import FaceRecognizer
from backend.services.gallery import Gallery
from backend.routes import recognition, attendance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    logger.info("Loading AI models and gallery...")
    detector = FaceDetector()
    recognizer = FaceRecognizer()
    gallery = Gallery(detector, recognizer)
    gallery.load_gallery()

    app.state.face_detector = detector
    app.state.face_recognizer = recognizer
    app.state.gallery = gallery

    logger.info("Backend startup complete.")
    yield

app = FastAPI(
    title="Face Attendance Backend",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(recognition.router)
app.include_router(attendance.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
```

#### Line-by-Line Breakdown:
*   **Line 1–4**: Imports logging components, `asynccontextmanager` standard utility, `FastAPI`, and `CORSMiddleware`.
*   **Line 6–10**: Imports database items, model wrappers, services, and route modules.
*   **Line 15 (`@asynccontextmanager`) & Line 16 (`async def lifespan(app: FastAPI)`)**:
    *   Defines the **Lifespan Manager**. In modern FastAPI, `lifespan` replaces deprecated startup/shutdown events.
    *   Everything **before `yield`** runs once when the server starts.
    *   Everything **after `yield`** runs when the server shuts down.
*   **Line 18 (`Base.metadata.create_all(bind=engine)`)**: Checks SQLite database and creates missing tables (`attendance`) automatically on app boot.
*   **Line 21–24**: Loads ONNX AI models (`FaceDetector`, `FaceRecognizer`) and initializes `Gallery`. `gallery.load_gallery()` scans training images and indexes feature vectors in RAM.
*   **Line 26–28 (`app.state... = ...`)**: Stores instance references in `app.state`. This avoids reloading multi-megabyte AI model files on every single API request.
*   **Line 31 (`yield`)**: Hands execution control over to FastAPI to listen for incoming network traffic.
*   **Line 33–37 (`app = FastAPI(...)`)**: Creates the primary FastAPI app instance, passing metadata and our `lifespan` handler.
*   **Line 40–46 (`app.add_middleware(...)`)**: Configures Cross-Origin Resource Sharing (CORS), enabling mobile apps or web frontends on any host/port to talk to the backend API.
*   **Line 48–50 (`@app.get("/health")`)**: A simple health-check route returning `{"status": "ok"}`.
*   **Line 52–53 (`app.include_router(...)`)**: Registers modular route groups into the root application.
*   **Line 55–57**: Enables direct execution via `python backend/main.py` using Uvicorn.

---

### AI Model Loading Architecture (`services/`)

The system relies on two neural networks executed via ONNX Runtime:

1. **`FaceDetector` (`services/face_detector.py`)**: Uses the SCRFD ONNX model (`ort.InferenceSession`) to locate bounding boxes of human faces in an image matrix (OpenCV BGR numpy array).
2. **`FaceRecognizer` (`services/face_recognizer.py`)**: Uses MobileFaceNet ONNX model (`ort.InferenceSession`). Resizes cropped face images to 112x112, normalizes pixel values, and returns a 512-dimensional vector embedding representing facial features.
3. **`Gallery` (`services/gallery.py`)**: At startup, scans folders inside the dataset directory (`dataset/train`), extracts embeddings for known identities, computes average feature vectors per person, and normalizes them.
   * **Cosine Similarity**: Compares two 512-D vectors using dot products. A similarity score $\ge 0.40$ (configurable) confirms identity match.

---

### Face Recognition Endpoint (`routes/recognition.py`)

Here is `backend/routes/recognition.py`:

```python
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
    try:
        contents = await file.read()
        if not contents:
            return RecognizeResponse(recognized=False, person=None, similarity=None, message="No face detected")
        np_arr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except Exception:
        return RecognizeResponse(recognized=False, person=None, similarity=None, message="Invalid image file")

    if image is None or image.size == 0:
        return RecognizeResponse(recognized=False, person=None, similarity=None, message="Invalid image file")

    face_detector = request.app.state.face_detector
    face_recognizer = request.app.state.face_recognizer
    gallery = request.app.state.gallery

    faces = face_detector.detect_faces(image)

    if len(faces) == 0:
        return RecognizeResponse(recognized=False, person=None, similarity=None, message="No face detected")
    if len(faces) > 1:
        return RecognizeResponse(recognized=False, person=None, similarity=None, message="Multiple faces detected")

    face_crop = faces[0]["crop"]
    embedding = face_recognizer.get_embedding(face_crop)

    if embedding is None:
        return RecognizeResponse(recognized=False, person=None, similarity=None, message="Failed to generate face embedding")

    is_recognized, person_name, similarity = gallery.recognize(embedding)

    if is_recognized and person_name:
        _, created = AttendanceService.mark_attendance(db, person_name)
        msg = "Attendance marked" if created else "Attendance already marked for today"
        return RecognizeResponse(recognized=True, person=person_name, similarity=similarity, message=msg)
    else:
        return RecognizeResponse(recognized=False, person=None, similarity=similarity if similarity > 0 else None, message="Unknown person")
```

#### Line-by-Line Breakdown:
*   **Line 11 (`@router.post("/recognize", response_model=RecognizeResponse)`)**: Defines a POST endpoint at `/recognize`. FastAPI validates the return data format against `RecognizeResponse` schema.
*   **Line 12–16 (`async def recognize_face(...)`)**: Accepts `request: Request` (to access `app.state`), `file: UploadFile` (the uploaded camera frame), and `db: Session = Depends(get_db)` (injected DB session).
*   **Line 18–28**: Reads raw upload bytes asynchronously, converts them into a 1D NumPy uint8 buffer, and decodes them into an OpenCV BGR image matrix (`cv2.imdecode`).
*   **Line 46–48**: Pulls the pre-loaded instances (`face_detector`, `face_recognizer`, `gallery`) directly from `request.app.state`.
*   **Line 51**: Runs face detection algorithm on the decoded image.
*   **Line 53–67**: Checks detection results. Rejects requests with zero faces or multiple faces.
*   **Line 70–71**: Crops the single detected face bounding region and generates a 512-D embedding.
*   **Line 82**: Compares the 512-D embedding against indexed identity vectors in memory gallery using cosine similarity.
*   **Line 84–93**: If recognized, invokes `AttendanceService.mark_attendance(db, person_name)` and returns structured JSON with an informative status message.

---

## 3. Work Item #2: Database Models & Duplicate Attendance Prevention

### Overview of Work #2
In the second phase, we solved the duplicate attendance issue. Prior to this update, scanning the same face multiple times on the same date created multiple database entries. We instituted a **two-layer duplicate prevention architecture**:
1. **Database Schema Enforcement**: Enforcing a composite `UniqueConstraint` on `(person_name, date)`.
2. **Service Layer Check-Before-Insert**: Checking existing records prior to insertion, accompanied by `IntegrityError` rollback handling.

---

### Database Table Model (`database/models.py`)

Here is `backend/database/models.py`:

```python
from sqlalchemy import Column, Integer, String, UniqueConstraint
from backend.database.database import Base

class AttendanceRecord(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    person_name = Column(String, nullable=False, index=True)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    status = Column(String, default="Present", nullable=False)

    __table_args__ = (
        UniqueConstraint('person_name', 'date', name='_person_date_uc'),
    )
```

#### Line-by-Line Breakdown:
*   **Line 1–2**: Imports column types and constraint utilities from SQLAlchemy, plus our declarative `Base`.
*   **Line 4 (`class AttendanceRecord(Base)`)**: Inherits from `Base`, marking this Python class as an ORM table model.
*   **Line 5 (`__tablename__ = "attendance"`)**: Specifies the SQL table name created in SQLite.
*   **Line 7 (`id`)**: Primary key integer column, auto-incremented on each record creation.
*   **Line 8 (`person_name`)**: String column storing person's identity name (e.g., `"John Doe"`). Indexed for fast SQL query filtering.
*   **Line 9 (`date`)**: String column storing calendar date in ISO format (`"YYYY-MM-DD"`).
*   **Line 10 (`time`)**: String column storing timestamp (`"HH:MM:SS"`).
*   **Line 11 (`status`)**: String column defaulting to `"Present"`.
*   **Line 13–15 (`__table_args__`)**:
    *   Adds a **`UniqueConstraint('person_name', 'date', name='_person_date_uc')`**.
    *   **What this does**: Tells the SQL engine that the pair `(person_name, date)` MUST be unique across all rows. If the table already contains `("John Doe", "2026-08-19")`, attempting to insert another row with those exact two values will cause SQLite to abort the insert with an `IntegrityError`.

---

### Attendance Service Logic (`services/attendance_service.py`)

Here is `backend/services/attendance_service.py`:

```python
from datetime import datetime
from typing import Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.database.models import AttendanceRecord

class AttendanceService:
    @staticmethod
    def mark_attendance(db: Session, person_name: str) -> Tuple[AttendanceRecord, bool]:
        """
        Marks attendance for person_name if not already marked for today.
        Returns tuple: (record, created_flag)
        """
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        # Check if record already exists for this person on today's date
        existing_record = db.query(AttendanceRecord).filter(
            AttendanceRecord.person_name == person_name,
            AttendanceRecord.date == date_str,
            AttendanceRecord.status == "Present"
        ).first()

        if existing_record:
            return existing_record, False

        # Create new record
        try:
            record = AttendanceRecord(
                person_name=person_name,
                date=date_str,
                time=time_str,
                status="Present"
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return record, True
        except IntegrityError:
            db.rollback()
            existing_record = db.query(AttendanceRecord).filter(
                AttendanceRecord.person_name == person_name,
                AttendanceRecord.date == date_str,
                AttendanceRecord.status == "Present"
            ).first()
            return existing_record, False

    @staticmethod
    def get_attendance_records(db: Session):
        return db.query(AttendanceRecord).order_by(AttendanceRecord.id.desc()).all()
```

#### Line-by-Line Breakdown:
*   **Line 8–9 (`def mark_attendance(db: Session, person_name: str) -> Tuple[AttendanceRecord, bool]`)**:
    *   Takes database session `db` and string `person_name`.
    *   Returns a 2-element Python tuple: `(record_object, created_boolean)`.
*   **Line 14–16**: Gets system time and formats date string as `"YYYY-MM-DD"` and time string as `"HH:MM:SS"`.
*   **Line 19–23 (`Check-Before-Insert`)**:
    *   Queries `AttendanceRecord` table where `person_name == person_name` AND `date == date_str`.
    *   `.first()` executes SQL `SELECT ... LIMIT 1`.
*   **Line 25–26**: If an existing record is found, immediately returns `(existing_record, False)`. `False` indicates no new record was created.
*   **Line 30–35**: Instantiates new `AttendanceRecord` object with fields populated.
*   **Line 36–39**:
    *   `db.add(record)` stages the object for insertion.
    *   `db.commit()` executes SQL transaction to persist row to disk.
    *   `db.refresh(record)` reloads object attributes (such as auto-generated `id`) from database.
    *   Returns `(record, True)` signaling successful creation.
*   **Line 40–47 (`Race Condition Protection`)**:
    *   If two requests arrive simultaneously and pass the check at the exact same millisecond, the database's `UniqueConstraint` triggers an `IntegrityError`.
    *   `db.rollback()` cancels the failed transaction safely.
    *   Retrieves the record created by the parallel request and returns `(existing_record, False)` gracefully without crashing the server.
*   **Line 49–51 (`get_attendance_records`)**: Queries all records ordered by ID descending (newest first) for display in UI tables.

---

### Attendance API Routes (`routes/attendance.py`)

Here is `backend/routes/attendance.py`:

```python
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.schemas.attendance import AttendanceCreate, AttendanceResponse
from backend.services.attendance_service import AttendanceService

router = APIRouter(tags=["Attendance"])

@router.post("/attendance", response_model=AttendanceResponse)
def create_attendance(
    data: AttendanceCreate,
    db: Session = Depends(get_db)
):
    record, _ = AttendanceService.mark_attendance(db, data.person)
    return record


@router.get("/attendance", response_model=List[AttendanceResponse])
def get_attendance(
    db: Session = Depends(get_db)
):
    records = AttendanceService.get_attendance_records(db)
    return records
```

#### Line-by-Line Breakdown:
*   **Line 10–16 (`POST /attendance`)**: Endpoint for manually marking attendance or testing. Takes JSON payload matching `AttendanceCreate` (`{"person": "John Doe"}`), runs service logic, and returns the attendance record.
*   **Line 19–24 (`GET /attendance`)**: Endpoint for fetching attendance logs. Uses `get_db` dependency to query and return a list of records validated against `List[AttendanceResponse]`.

---

## 4. Summary & Key Takeaways

1. **Model Persistence via Lifespan**: Neural networks (SCRFD & MobileFaceNet) are heavy objects loaded ONCE during FastAPI application startup via `lifespan` and stored in `app.state`.
2. **Dependency Injection**: Database connections are created per request using `Depends(get_db)` and automatically closed upon completion via `yield`.
3. **Database Constraints + Service Check**: Preventing duplicate attendance relies on a two-tier protection strategy: Python query checking prior to insertion and SQLite `UniqueConstraint('person_name', 'date')` at schema level.
4. **Clean Code Structure**: Code logic is cleanly divided into:
   - **`main.py`**: App initialization, lifecycle, & middleware.
   - **`database/`**: Engine setup (`database.py`) and schema definitions (`models.py`).
   - **`services/`**: Core logic (AI inference, facial recognition gallery, attendance tracking).
   - **`routes/`**: API endpoint controllers (`recognition.py`, `attendance.py`).
