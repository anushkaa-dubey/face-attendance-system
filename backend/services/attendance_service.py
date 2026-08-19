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

