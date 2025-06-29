from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from bson import ObjectId, errors
from database.db_connection import DBConnection

router = APIRouter()

class UserProfileOut(BaseModel):
    username: str | None = None
    bio: str | None = None

class UserProfileUpdate(BaseModel):
    username: str | None = None
    bio: str | None = None


@router.get("/profile/{user_id}", response_model=UserProfileOut)
def get_profile(user_id: str):
    try:
        obj_id = ObjectId(user_id)
    except errors.InvalidId:
        raise HTTPException(400, "Geçersiz kullanıcı ID")

    user = DBConnection.find_one("users", {"_id": obj_id})

    if not user:
        raise HTTPException(404, "Kullanıcı bulunamadı")

    return UserProfileOut(username=user.get("username"), bio=user.get("bio"))



@router.put("/profile/{user_id}", response_model=UserProfileOut)
def update_profile(user_id: str, update: UserProfileUpdate):
    try:
        obj_id = ObjectId(user_id)
    except errors.InvalidId:
        raise HTTPException(400, "Geçersiz kullanıcı ID")

    update_data = {k: v for k, v in update.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(400, "Güncellenecek veri yok")

    result = DBConnection.update_one("users", {"_id": obj_id}, {"$set": update_data})

    if result.matched_count == 0:
        raise HTTPException(404, "Kullanıcı bulunamadı")

    user = DBConnection.find_one("users", {"_id": obj_id})
    return UserProfileOut(username=user.get("username"), bio=user.get("bio"))
