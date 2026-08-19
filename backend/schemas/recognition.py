from pydantic import BaseModel
from typing import Optional

class RecognizeResponse(BaseModel):
    recognized: bool
    person: Optional[str] = None
    similarity: Optional[float] = None
    message: Optional[str] = None
