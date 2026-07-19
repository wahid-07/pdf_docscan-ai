import random
import string

from database.connection import SessionLocal
from models.table_model import User
from auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from datetime import datetime, timedelta


# ==========================================================
# REGISTER USER
# ==========================================================

def register_user(
    full_name: str,
    email: str,
    password: str
):
    """
    New user database me save karega.
    """

    db = SessionLocal()

    try:

        # Check email already exists
        existing = db.query(User).filter(
            User.email == email
        ).first()

        if existing:
            return {
                "success": False,
                "message": "Email already registered."
            }

        user = User(
            full_name=full_name,
            email=email,
            password_hash=hash_password(password[:72])
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "success": True,
            "message": "Registration successful."
        }

    except Exception as e:

        db.rollback()
        raise e

    finally:

        db.close()


# ==========================================================
# LOGIN USER
# ==========================================================

def login_user(
    email: str,
    password: str
):

    db = SessionLocal()

    try:

        user = db.query(User).filter(
            User.email == email
        ).first()

        if not user:

            return {
                "success": False,
                "message": "Email not found."
            }

        if not user.is_active:
            return {
                "success": False,
                "message": "This account has been deactivated. Contact an admin."
            }

        # Account Locked Check
        if user.account_locked:

            if user.lock_until and user.lock_until > datetime.now():

                return {
                    "success": False,
                    "message": f"Account locked. Try again after {user.lock_until}"
                }

            # Lock time complete
            user.account_locked = False
            user.failed_attempts = 0
            user.lock_until = None

            db.commit()

        if not verify_password(
            password[:72],
            user.password_hash
        ):

            user.failed_attempts += 1

            # 5 attempts ke baad account lock
            if user.failed_attempts >= 5:

                user.account_locked = True
                user.lock_until = datetime.now() + timedelta(minutes=15)

                db.commit()

                return {
                    "success": False,
                    "message": "Too many failed attempts. Account locked for 15 minutes."
                }

            db.commit()

            return {
                "success": False,
                "message": f"Invalid password. Attempts left: {5 - user.failed_attempts}"
            }
        
        # Successful login
        user.failed_attempts = 0
        user.account_locked = False
        user.lock_until = None
        user.last_login = datetime.now()

        db.commit()
        db.refresh(user)

        access_token = create_access_token(
            {
                "user_id": user.id,
                "email": user.email,
                "role": user.role,
                "token_version": user.token_version or 0
            }
        )
        refresh_token = create_refresh_token(
            {
                "user_id": user.id,
                "email": user.email,
                "role": user.role,
                "token_version": user.token_version or 0
            }
        )

        user.refresh_token = refresh_token
        user.refresh_token_expires_at = datetime.now() + timedelta(days=7)
        db.commit()

        return {
            "success": True,
            "message": "Login successful.",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.full_name,
                "email": user.email,
                "role": user.role
            }
        }

    finally:

        db.close()


# ==========================================================
# REFRESH TOKEN
# ==========================================================

def refresh_access_token(refresh_token: str):
    db = SessionLocal()
    try:
        payload = verify_refresh_token(refresh_token)
        if not payload:
            return {"success": False, "message": "Invalid refresh token."}

        user = db.query(User).filter(User.id == payload.get("user_id")).first()
        if not user or user.refresh_token != refresh_token:
            return {"success": False, "message": "Invalid refresh token."}
        if not user.is_active:
            return {"success": False, "message": "This account has been deactivated."}
        if user.refresh_token_expires_at and user.refresh_token_expires_at < datetime.now():
            return {"success": False, "message": "Refresh token expired."}

        access_token = create_access_token({
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
            "token_version": user.token_version or 0,
        })
        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
        }
    finally:
        db.close()


def logout_all_devices(user_id: int):
    """
    token_version ko +1 karta hai — isse is user ke saare purane
    access tokens (kisi bhi device pe) turant invalid ho jaate hain,
    kyunki get_current_user DB ke token_version se match karke check karta hai.
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"success": False, "message": "User not found."}
        user.token_version = (user.token_version or 0) + 1
        user.refresh_token = None
        user.refresh_token_expires_at = None
        db.commit()
        return {"success": True, "message": "Logged out from all devices."}
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_full_profile(user_id: int):
    """
    DB se poora profile fetch karta hai — JWT payload mein ye fields nahi hoti
    (last_login, profile_image, created_at), isliye DB query zaroori hai.
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        return {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "profile_image": user.profile_image,
            "last_login": str(user.last_login) if user.last_login else None,
            "created_at": str(user.created_at) if user.created_at else None,
        }
    finally:
        db.close()


# ==========================================================
# PROFILE + PASSWORD
# ==========================================================

def update_user_profile(user_id: int, full_name: str | None = None, profile_image: str | None = None):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        if full_name is not None:
            user.full_name = full_name
        if profile_image is not None:
            user.profile_image = profile_image
        db.commit()
        return {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "profile_image": user.profile_image,
        }
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def change_password(user_id: int, current_password: str, new_password: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"success": False, "message": "User not found."}
        if not verify_password(current_password[:72], user.password_hash):
            return {"success": False, "message": "Current password is incorrect."}
        user.password_hash = hash_password(new_password[:72])
        db.commit()
        return {"success": True, "message": "Password changed successfully."}
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def request_password_reset(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return {"success": False, "message": "Email not found."}

        otp = "".join(random.choices(string.digits, k=6))
        user.otp_code = otp
        user.otp_expires_at = datetime.now() + timedelta(minutes=10)
        db.commit()
        return {"success": True, "message": "OTP sent successfully.", "otp": otp}
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def verify_password_reset_otp(email: str, otp: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return {"success": False, "message": "Email not found."}
        if not user.otp_code or not user.otp_expires_at:
            return {"success": False, "message": "OTP not requested."}
        if user.otp_code != otp or user.otp_expires_at < datetime.now():
            return {"success": False, "message": "Invalid or expired OTP."}
        return {"success": True, "message": "OTP verified successfully."}
    finally:
        db.close()


def reset_password(email: str, otp: str, new_password: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return {"success": False, "message": "Email not found."}
        if not user.otp_code or not user.otp_expires_at:
            return {"success": False, "message": "OTP not requested."}
        if user.otp_code != otp or user.otp_expires_at < datetime.now():
            return {"success": False, "message": "Invalid or expired OTP."}

        user.password_hash = hash_password(new_password[:72])
        user.otp_code = None
        user.otp_expires_at = None
        db.commit()
        return {"success": True, "message": "Password reset successfully."}
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()