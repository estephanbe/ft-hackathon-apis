from typing import Optional

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ClaimCodeIn(BaseModel):
    code: str
    username: str
    password: str
    location: Optional[str] = None
    language: Optional[str] = None
    dialect: Optional[str] = None
    spiritual_level: int = Field(..., ge=0, le=5)
    trust_score: float = Field(50.0, ge=0.0, le=100.0)