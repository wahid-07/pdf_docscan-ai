from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.security import verify_access_token
from database.connection import SessionLocal
from models.table_model import User

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    JWT Token verify karega aur user info return karega.
    Har protected endpoint pe use karo.

    Token ke andar user_id/role/token_version hote hain, lekin hum
    is_active aur token_version DB se dobara check karte hain — isse
    admin ke "deactivate" ya khud ke "logout all devices" action turant
    asar karte hain, purana token turant reject ho jata hai.
    """
    token = credentials.credentials
    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or Expired Token"
        )

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == payload.get("user_id")).first()

        if not user:
            raise HTTPException(status_code=401, detail="User no longer exists")

        if not user.is_active:
            raise HTTPException(status_code=401, detail="Account deactivated")

        if user.token_version != payload.get("token_version", 0):
            raise HTTPException(status_code=401, detail="Session expired. Please log in again.")

        # Role DB se fresh lo — agar admin ne role change kiya hai to purane
        # token mein purana role atka nahi rehna chahiye.
        payload["role"] = user.role
        return payload
    finally:
        db.close()


def get_current_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Sirf Admin access kar sakta hai.
    Normal user ko 403 milega.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Access denied. Admin only."
        )
    return current_user