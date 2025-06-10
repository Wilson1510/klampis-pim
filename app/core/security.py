from passlib.context import CryptContext

# Membuat context untuk hashing, menentukan bcrypt sebagai algoritma default
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Memverifikasi password teks biasa dengan hash di database."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Menghasilkan hash dari password teks biasa."""
    return pwd_context.hash(password)
