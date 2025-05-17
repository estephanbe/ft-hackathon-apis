from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from utils.auth import decode_access_token
from DB.models.users import User
from mongoengine.errors import DoesNotExist

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = decode_access_token(token)
    if not payload or "user_id" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    try:
        user = User.objects.get(id=payload["user_id"])
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def check_is_om(current: User = Depends(get_current_user)) -> User:
    if current.role != "OM":
        raise HTTPException(403, "OM privileges required")
    return current
