from passlib.context import CryptContext
from fastapi import APIRouter, HTTPException


# Şifreleme algoritması (bcrypt kullanıyoruz)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Şifre hashleme
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Şifre doğrulama
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        # Logla veya özel hata fırlat
        raise HTTPException(status_code=400, detail="Şifre doğrulama başarısız: hash formatı geçersiz")
