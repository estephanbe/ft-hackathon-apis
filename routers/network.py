from fastapi import APIRouter, HTTPException
from mongoengine.errors import NotUniqueError, DoesNotExist

from schemas.network import (
    UserCreate, UserOut,
    CircleCreate, CircleOut,
    CircleMemberCreate, CircleMemberOut,
)
from DB.mongodb import get_mongo_db  # ensure your DB is connected
from DB.mongodb import close_mongo_db
from DB.models.users import User, Circle, CircleMember

router = APIRouter(tags=["network"])


# ——— Users ———

@router.post("/users", response_model=UserOut)
async def create_user(user_in: UserCreate):
    try:
        user = User(**user_in.model_dump()).save()
    except NotUniqueError:
        raise HTTPException(400, "Username already exists")
    return UserOut(
        id=str(user.id),
        username=user.username,
        created_at=user.created_at,
    )


@router.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: str):
    try:
        user = User.objects.get(id=user_id)
    except DoesNotExist:
        raise HTTPException(404, "User not found")
    return UserOut(
        id=str(user.id),
        username=user.username,
        created_at=user.created_at,
    )


# get user by username
@router.get("/users/by_username/{username}", response_model=UserOut)
async def get_user_by_username(username: str):
    try:
        user = User.objects.get(username=username)
    except DoesNotExist:
        raise HTTPException(404, "User not found")
    return UserOut(
        id=str(user.id),
        username=user.username,
        created_at=user.created_at,
    )


# ——— Circles ———

@router.post("/circles", response_model=CircleOut)
async def create_circle(input: CircleCreate):
    # ensure owner exists
    try:
        owner = User.objects.get(id=input.owner_id)
    except DoesNotExist:
        raise HTTPException(404, "Owner not found")
    circle = Circle(owner=owner).save()
    return CircleOut(
        id=str(circle.id),
        owner_id=str(owner.id),
        members=[],
        created_at=circle.created_at,
    )


@router.get("/circles/{circle_id}", response_model=CircleOut)
async def get_circle(circle_id: str):
    try:
        c = Circle.objects.get(id=circle_id)
    except DoesNotExist:
        raise HTTPException(404, "Circle not found")
    members = [
        CircleMemberOut(
            user_id=str(m.user.id),
            trust_score=m.trust_score,
            is_flagged=m.is_flagged,
            flag_score=m.flag_score,
        )
        for m in c.members
    ]
    return CircleOut(
        id=str(c.id),
        owner_id=str(c.owner.id),
        members=members,
        created_at=c.created_at,
    )


@router.post("/circles/{circle_id}/members", response_model=CircleOut)
async def add_member(circle_id: str, m_in: CircleMemberCreate):
    # load circle
    try:
        circle = Circle.objects.get(id=circle_id)
    except DoesNotExist:
        raise HTTPException(404, "Circle not found")
    # load user
    try:
        user = User.objects.get(id=m_in.user_id)
    except DoesNotExist:
        raise HTTPException(404, "User not found")
    # append and save
    cm = CircleMember(
        user=user,
        trust_score=m_in.trust_score,
        is_flagged=m_in.is_flagged,
        flag_score=m_in.flag_score
    )
    circle.members.append(cm)
    circle.save()
    # return updated circle
    return await get_circle(circle_id)  # reuse the serializer above


@router.patch("/circles/{circle_id}/members/{user_id}", response_model=CircleOut)
async def update_member(circle_id: str, user_id: str, m_in: CircleMemberCreate):
    try:
        circle = Circle.objects.get(id=circle_id)
    except DoesNotExist:
        raise HTTPException(404, "Circle not found")
    # find embedded member
    member = next((m for m in circle.members if str(m.user.id) == user_id), None)
    if not member:
        raise HTTPException(404, "Member not in circle")
    # update fields

    if m_in.trust_score <= member.trust_score - 25:
        if not m_in.description:
            raise HTTPException(400, "Must supply description when trust drops >25%")
        member.last_trust_change_desc = m_in.description
    member.trust_score = m_in.trust_score
    member.is_flagged = m_in.is_flagged
    member.flag_score = m_in.flag_score
    circle.save()
    return await get_circle(circle_id)
