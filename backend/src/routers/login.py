from fastapi import APIRouter, HTTPException, Body
from database.db_connection import DBConnection
from models.users import User
from auth.jwt import create_token
from auth.password_utils import verify_password

router = APIRouter()

@router.post("/login")
def login(user: User = Body(...)):
    print("Gelen veriler:", user)
  

    existing_user = DBConnection.find_one("users", {'email': user.email})
    if not existing_user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    hashed_password = existing_user.get("password")
    if not hashed_password:
        raise HTTPException(status_code=500, detail="Kullanıcının şifresi bulunamadı")

    if not verify_password(user.password, hashed_password):
        raise HTTPException(status_code=401, detail="Şifre yanlış")

    token = create_token(user_id=str(existing_user["_id"]))
    user_id = str(existing_user["_id"])

    return {
        "success": True,
        "message": "Giriş başarılı.",
        "token": token,
        "user": {
            "name": existing_user.get("name"),
            "email": existing_user.get("email"),
            "user_id": user_id
        }
    }
