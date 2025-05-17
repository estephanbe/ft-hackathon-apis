from fastapi import APIRouter, Depends, HTTPException
from DB.models.users import User, Circle
from pydantic import BaseModel
from typing import List
from datetime import datetime

from routers.dep import get_current_user

router = APIRouter(tags=["me"])

# Pydantic models for output
class MeOut(BaseModel):
    id: str
    username: str
    created_at: datetime

class CircleMemberOut(BaseModel):
    user_id: str
    trust_score: float
    is_flagged: bool
    flag_score: int

class CircleOut(BaseModel):
    id: str
    owner_id: str
    members: List[CircleMemberOut]
    created_at: datetime

@router.get("/me", response_model=MeOut)
async def read_me(current_user: User = Depends(get_current_user)):
    return MeOut(
        id=str(current_user.id),
        username=current_user.username,
        created_at=current_user.created_at,
    )

@router.get("/me/circle", response_model=List[CircleOut])
async def my_owned_circles(current_user: User = Depends(get_current_user)):
    circles = Circle.objects(owner=current_user)
    if len(circles) == 1:
        members = [
            CircleMemberOut(
                user_id=str(m.user.id),
                trust_score=m.trust_score,
                is_flagged=m.is_flagged,
                flag_score=m.flag_score,
            ) for m in circles[0].members
        ]
        return [CircleOut(
            id=str(circles[0].id),
            owner_id=str(current_user.id),
            members=members,
            created_at=circles[0].created_at,
        )]
    else:
        raise HTTPException(404, "No circles found")

