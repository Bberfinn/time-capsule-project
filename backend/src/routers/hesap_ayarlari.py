from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from auth.jwt import get_current_user  # Kullanıcının token ile doğrulaması
from database.db_connection import DBConnection
from bson import ObjectId
from auth.password_utils import get_password_hash, verify_password


router = APIRouter()

# Modeller
class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=5)
    new_password: str = Field(min_length=5)
    confirm_password: str = Field(min_length=5)


class ChangeEmailRequest(BaseModel):
    new_email: EmailStr
    current_password: str = Field(min_length=5)


class DeleteAccountRequest(BaseModel):
    current_password: str = Field(min_length=5)
    confirm: bool 





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

    if user.get("email") == data.new_email:
        raise HTTPException(status_code=400, detail="Yeni e-posta mevcut e-posta ile aynı")

    DBConnection.update_one("users", {"_id": ObjectId(current_user)}, {"$set": {"email": data.new_email}})

    return {"message": "E-posta başarıyla değiştirildi"}



# Hesap silme 
@router.post("/account/delete")
def delete_account(data: DeleteAccountRequest, current_user=Depends(get_current_user)):
    user = DBConnection.find_one("users", {"_id": ObjectId(current_user)})
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    if not verify_password(data.current_password, user["password"]):
        raise HTTPException(status_code=400, detail="Şifre yanlış")

    DBConnection.delete_one("users", {"_id": ObjectId(current_user)})

    return {"message": "Hesap başarıyla silindi"}
