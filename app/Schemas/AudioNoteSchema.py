from pydantic import BaseModel
from typing import List


class AudioNoteResponse(BaseModel):
    id: int
    title: str
    description: str
    tags: List[str]
    duration: float
