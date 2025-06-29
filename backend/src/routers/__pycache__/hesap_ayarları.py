from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from auth.jwt import get_current_user  # Kullanıcının token ile doğrulaması
from database.db_connection import DBConnection
from bson import ObjectId
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Modeller
class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)


class ChangeEmailRequest(BaseModel):
    new_email: EmailStr
    current_password: str = Field(min_length=8)


class DeleteAccountRequest(BaseModel):
    current_password: str = Field(min_length=8)
    confirm: bool  # Kullanıcı onayı


# Yardımcı fonksiyon: şifre doğrulama
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Yardımcı fonksiyon: şifre hashleme
def get_password_hash(password):
    return pwd_context.hash(password)


# Şifre değiştirme
@router.post("/account/change-password")
def change_password(data: ChangePasswordRequest, current_user=Depends(get_current_user)):
    user = DBConnection.find_one("users", {"_id": ObjectId(current_user)})
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    if not verify_password(data.current_password, user["password"]):
        raise HTTPException(status_code=400, detail="Mevcut şifre yanlış")

    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Yeni şifre ve onay uyuşmuyor")

    # Şifre güvenlik kuralları buraya eklenebilir (opsiyonel)

    hashed_new_password = get_password_hash(data.new_password)
    DBConnection.update_one("users", {"_id": ObjectId(current_user)}, {"$set": {"password": hashed_new_password}})

    return {"message": "Şifre başarıyla değiştirildi"}


# E-posta değiştirme
@router.post("/account/change-email")
def change_email(data: ChangeEmailRequest, current_user=Depends(get_current_user)):
    user = DBConnection.find_one("users", {"_id": ObjectId(current_user)})
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    if not verify_password(data.current_password, user["password"]):
        raise HTTPException(status_code=400, detail="Şifre yanlış")

    # Aynı e-posta kontrolü
    if user.get("email") == data.new_email:
        raise HTTPException(status_code=400, detail="Yeni e-posta mevcut e-posta ile aynı")

    # Burada e-posta doğrulama maili gönderme işlemi yapılabilir (opsiyonel)

    DBConnection.update_one("users", {"_id": ObjectId(current_user)}, {"$set": {"email": data.new_email}})

    return {"message": "E-posta başarıyla değiştirildi"}


# Hesap silme / devre dışı bırakma
@router.post("/account/delete")
def delete_account(data: DeleteAccountRequest, current_user=Depends(get_current_user)):
    user = DBConnection.find_one("users", {"_id": ObjectId(current_user)})
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    if not data.confirm:
        raise HTTPException(status_code=400, detail="Hesap silme onayı gerekli")

    if not verify_password(data.current_password, user["password"]):
        raise HTTPException(status_code=400, detail="Şifre yanlış")

    # Hesabı kalıcı silmek istiyorsan:
    DBConnection.delete_one("users", {"_id": ObjectId(current_user)})

    # Veya devre dışı bırakmak istersen, örn:
    # DBConnection.update_one("users", {"_id": ObjectId(current_user)}, {"$set": {"active": False}})

    return {"message": "Hesap başarıyla silindi"}


# Router'ı ana uygulamaya eklemeyi unutma
# app.include_router(router, prefix="/api")
