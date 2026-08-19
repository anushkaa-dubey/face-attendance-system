from pydantic import BaseModel

class AttendanceCreate(BaseModel):
    person: str

class AttendanceResponse(BaseModel):
    id: int
    person_name: str
    date: str
    time: str
    status: str

    class Config:
        from_attributes = True
