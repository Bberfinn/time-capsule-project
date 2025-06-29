from fastapi import APIRouter, HTTPException
from database.db_connection import DBConnection
from models.users import User
from auth.password_utils import get_password_hash


router = APIRouter()


@router.post("/register")
def register(user: User):
    existing_user = DBConnection.find_one("users", {'email': user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Bu e-posta zaten kayıtlı")

    hashed_password = get_password_hash(user.password)  # Şifreyi hashle
    user_dict = dict(user)
    user_dict["password"] = hashed_password  # Hash’lenmiş şifreyi ata

    DBConnection.insert("users", user_dict)  
    return {"success": True, "message": "Kayıt başarılı."}
