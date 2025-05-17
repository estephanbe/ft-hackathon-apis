from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class UserCreate(BaseModel):
    username: str

class UserOut(BaseModel):
    id: str
    username: str
    created_at: datetime

class CircleMemberCreate(BaseModel):
    user_id: str
    trust_score: float = Field(0.0, ge=0.0, le=100.0)
    is_flagged: bool = False
    flag_score: int = 0

class CircleMemberOut(BaseModel):
    user_id: str
    trust_score: float
    is_flagged: bool
    flag_score: int

class CircleCreate(BaseModel):
    owner_id: str

class CircleOut(BaseModel):
    id: str
    owner_id: str
    members: List[CircleMemberOut]
    created_at: datetime
