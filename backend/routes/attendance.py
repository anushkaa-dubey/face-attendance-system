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
