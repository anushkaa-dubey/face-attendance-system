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

