from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt

from passlib.context import CryptContext

# Membuat context untuk hashing, menentukan bcrypt sebagai algoritma default
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Memverifikasi password teks biasa dengan hash di database."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Menghasilkan hash dari password teks biasa."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Membuat JWT access token."""
    SECRET_KEY = "KUNCI_RAHASIA_ANDA_YANG_SANGAT_SULIT_DITEBAK"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode({None: None}, None, algorithm=ALGORITHM)
    return encoded_jwt