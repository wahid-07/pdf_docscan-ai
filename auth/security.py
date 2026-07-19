from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
import os

"""
=========================================================
SECURITY MODULE
---------------------------------------------------------
Is file ka kaam hai:

1. Password ko Hash karna
2. Password verify karna
3. JWT Token banana aur verify karna
=========================================================
"""

# Password hashing algorithm
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# ==========================================================
# PASSWORD HASH
# ==========================================================

def hash_password(password: str) -> str:
    """
    Plain password ko hash karke return karega.
    bcrypt 72 bytes se lamba password accept nahi karta.
    """
    return pwd_context.hash(password[:72])


# ==========================================================
# PASSWORD VERIFY
# ==========================================================

def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    User ke password ko verify karega.
    """
    return pwd_context.verify(
        plain_password[:72],
        hashed_password
    )


# JWT Secret Key — .env se lo, fallback sirf development ke liye
SECRET_KEY = os.getenv("SECRET_KEY", "wahid_pdf_project_2026_secret_key")

# Algorithm
ALGORITHM = "HS256"

# Token Expiry
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(data: dict):
    """
    JWT Token Generate karega.
    """
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str):
    """
    JWT Token Verify karega.
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload

    except JWTError:
        return None


def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None