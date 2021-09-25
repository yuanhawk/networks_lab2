from pydantic import BaseModel
from typing import Optional, List


class Student(BaseModel):
    name: str
    id: str
    gpa: Optional[float] = None
