import logging
import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from services.auth_service import (
    register_user,
    login_user,
    refresh_access_token,
    update_user_profile,
    change_password,
    request_password_reset,
    verify_password_reset_otp,
    reset_password,
    get_full_profile,
    logout_all_devices,
)
from auth.auth import get_current_user
from services.audit_logger import log_event

router = APIRouter()
logger = logging.getLogger("pdf_extractor.auth")


# ==========================================================
# Request Models
# ==========================================================

class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = None
    profile_image: str | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str
    confirm_password: str


# ==========================================================
# REGISTER API
# ==========================================================

@router.post("/register")
def register(data: RegisterRequest):
    logger.info("Register request for %s", data.email)

    if not re.fullmatch(r"[A-Za-z.' -]+", data.full_name.strip()):

        raise HTTPException(

            status_code=400,

            detail="Enter a valid Full Name."

        )
    

    password_pattern = (
        r"^(?=.*[a-z])"
        r"(?=.*[A-Z])"
        r"(?=.*\d)"
        r"(?=.*[@$!%*?&^#])"
        r"[A-Za-z\d@$!%*?&^#]{8,64}$"
    )

    if not re.fullmatch(password_pattern, data.password):

        raise HTTPException(
            status_code=400,
            detail=("Password must contain at least 8 characters, "
                    "one uppercase letter, one lowercase letter, "
                    "one number and one special character."
                                )
        )



    result = register_user(
        full_name=data.full_name,
        email=data.email,
        password=data.password
    )
    log_event("register", details=f"email={data.email}")
    return result


# ==========================================================
# LOGIN API
# ==========================================================

@router.post("/login")
def login(data: LoginRequest):
    logger.info("Login request for %s", data.email)

    result = login_user(
        email=data.email,
        password=data.password
    )
    log_event("login", details=f"email={data.email}")
    return result


# ==========================================================
# ME API — Token verify karne ke liye
# Frontend checkLogin() isse call karta hai
# ==========================================================

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "success": True,
        "user_id": current_user.get("user_id"),
        "email": current_user.get("email"),
        "role": current_user.get("role")
    }


@router.post("/refresh")
def refresh_token(data: RefreshTokenRequest):
    return refresh_access_token(data.refresh_token)


@router.get("/profile")
def get_profile(current_user: dict = Depends(get_current_user)):
    profile = get_full_profile(current_user.get("user_id"))
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True, **profile}


@router.post("/logout-all")
def logout_all(current_user: dict = Depends(get_current_user)):
    result = logout_all_devices(current_user.get("user_id"))
    log_event("logout_all", user_id=current_user.get("user_id"))
    return result


@router.put("/profile")
def update_profile(data: ProfileUpdateRequest, current_user: dict = Depends(get_current_user)):
    result = update_user_profile(current_user.get("user_id"), full_name=data.full_name, profile_image=data.profile_image)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True, "user": result}


@router.post("/change-password")
def change_password_route(data: ChangePasswordRequest, current_user: dict = Depends(get_current_user)):
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="New password and confirm password do not match")

    result = change_password(current_user.get("user_id"), data.current_password, data.new_password)
    return result


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest):
    return request_password_reset(str(data.email))


@router.post("/verify-otp")
def verify_otp(data: VerifyOTPRequest):
    return verify_password_reset_otp(str(data.email), data.otp)


@router.post("/reset-password")
def reset_password_route(data: ResetPasswordRequest):
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="New password and confirm password do not match")
    return reset_password(str(data.email), data.otp, data.new_password)