import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, status, Depends
from DB.models.users import User, Circle, OneTimeCode
from mongoengine.errors import NotUniqueError, DoesNotExist

from routers.dep import check_is_om
from utils.auth import hash_password, create_access_token
from schemas.auth import UserCreate, UserLogin, TokenOut, ClaimCodeIn
from schemas.auth import UserCreate, TokenOut
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=TokenOut)
async def register(user_in: UserCreate):
    # Check for existing username
    if User.objects(username=user_in.username).first():
        raise HTTPException(409, "Username already taken")
    user = User(
        username=user_in.username,
        password_hash=hash_password(user_in.password)
    ).save()
    # create a circle for the user
    circle = Circle(owner=user).save()
    token = create_access_token({"user_id": str(user.id)})
    return TokenOut(access_token=token)


@router.post("/auth/login", response_model=TokenOut)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # form_data.username & form_data.password come from x-www-form-urlencoded body
    user = User.objects(username=form_data.username).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token({"user_id": str(user.id)})
    return TokenOut(access_token=access_token)

@router.post("/auth/generate-code")
async def generate_code(current_om: User = Depends(check_is_om)):
    code = secrets.token_urlsafe(8)
    OneTimeCode(code=code, om=current_om,
                expires_at=datetime.utcnow()+timedelta(hours=24)).save()
    return {"code": code}

@router.post("/auth/claim-code", response_model=TokenOut)
async def claim_code(data: ClaimCodeIn):
    otc = OneTimeCode.objects(code=data.code, claimed_by=None,
                              expires_at__gt=datetime.utcnow()).first()
    if not otc:
        raise HTTPException(400, "Invalid or expired code")

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        role="DISCIPLE",
        om_ref=otc.om,
        location=data.location,
        language=data.language,
        dialect=data.dialect,
        spiritual_level=data.spiritual_level,
        trust_score=data.trust_score,
    ).save()

    # give the disciple their personal circle
    Circle(owner=user).save()
    otc.update(set__claimed_by=user)

    token = create_access_token({"user_id": str(user.id)})
    return TokenOut(access_token=token)
