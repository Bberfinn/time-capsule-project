from fastapi import APIRouter, Depends, HTTPException, Form, status, File, UploadFile, Path
from models.capsule_model import Capsule
from bson import ObjectId
from datetime import datetime, date, timedelta
from bson.errors import InvalidId
from database.db_connection import DBConnection
from auth.jwt import get_current_user
from typing import List, Optional
from pydantic import BaseModel, Field
import os
import shutil
from uuid import uuid4
import traceback

router = APIRouter()



# Kapsül oluşturma 
@router.post("/capsules", status_code=status.HTTP_201_CREATED) 
def create_capsule(capsule: Capsule):  
    import traceback
    try:
        capsule_dict = capsule.dict()
        send_date = capsule.send_date
        capsule_dict["send_date"] = datetime(send_date.year, send_date.month, send_date.day)

        result = DBConnection.insert("capsule", capsule_dict)
        return {"message": "Kapsül kaydedildi", "id": str(result.inserted_id)}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Kapsül kaydedilirken hata oluştu: {str(e)}")




UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/capsules/upload", status_code=status.HTTP_201_CREATED)
async def create_capsule_with_file(
    category: str = Form(...),
    message: str = Form(...),
    send_date: date = Form(...),
    media: Optional[List[UploadFile]] = File(None),  
    current_user: str = Depends(get_current_user)
):
    try:
        media_url = []

        if media:
            for file in media:
                filename = f"{uuid4()}_{file.filename}"
                file_path = os.path.join(UPLOAD_DIR, filename)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                media_url.append(f"/{UPLOAD_DIR}/{filename}")

        kapsul_data = {
            "category": category,
            "message": message,
            "send_date": datetime(send_date.year, send_date.month, send_date.day),
            "created_at": datetime.utcnow(),
            "user_id": current_user,
            "media_url": media_url,  
        }

        result = DBConnection.insert("capsule", kapsul_data)
        return {"message": "Kapsül kaydedildi", "id": str(result.inserted_id)}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Kapsül kaydedilirken hata oluştu: {str(e)}")


@router.get("/capsules")
def get_my_capsules(current_user: str = Depends(get_current_user)):
    try:
        kapsuller_cursor = DBConnection.find("capsule", {"user_id": current_user})
        kapsuller = []
        for kapsul in kapsuller_cursor:
            kapsul["_id"] = str(kapsul["_id"])

            if "created_at" in kapsul:
                kapsul["created_at"] = kapsul["created_at"].isoformat()

            if "send_date" in kapsul:
                kapsul["send_date"] = kapsul["send_date"].date().isoformat()

            kapsuller.append(kapsul)

        return {
            "message": f"Kullanıcı {current_user} ait kapsüller listelendi.",
            "capsules": kapsuller
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kapsüller çekilirken hata: {str(e)}")




@router.get("/capsules/{capsule_id}")
def get_capsule(capsule_id: str):
    try:
        kapsul = DBConnection.find_one("capsule", {"_id": ObjectId(capsule_id)})
        if kapsul is None:
            raise HTTPException(status_code=404, detail="Kapsül bulunamadı")

        send_date = kapsul.get("send_date")
        if isinstance(send_date, str):
            send_date = datetime.fromisoformat(send_date)  # parse yerine
        elif isinstance(send_date, date) and not isinstance(send_date, datetime):
            send_date = datetime.combine(send_date, datetime.min.time())

        # Gün karşılaştırması (saat yok)
        if send_date.date() > datetime.utcnow().date():
            raise HTTPException(status_code=403, detail="Kapsül açılma tarihi henüz gelmedi")

        kapsul["_id"] = str(kapsul["_id"])
        kapsul["created_at"] = kapsul["created_at"].isoformat()
        kapsul["send_date"] = send_date.date().isoformat()

        return kapsul

    except HTTPException as http_error:
        raise http_error

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kapsül verisi alınamadı: {str(e)}")


from fastapi import Path

@router.put("/capsules/{capsule_id}")
def update_capsule(
    capsule_id: str = Path(...),
    category: Optional[str] = Form(None),
    message: Optional[str] = Form(None),
    send_date: Optional[date] = Form(None),
    media: Optional[UploadFile] = File(None),
    current_user: str = Depends(get_current_user)
):
    import traceback
    try:
        #kapsülü bul
        kapsul = DBConnection.find_one("capsule", {"_id": ObjectId(capsule_id), "user_id": current_user})
        if not kapsul:
            raise HTTPException(status_code=404, detail="Kapsül bulunamadı")

        # 7 gün kontrolü
        created_at = kapsul.get("created_at")
        if not created_at:
            raise HTTPException(status_code=400, detail="Kapsülün oluşturulma tarihi eksik")
        
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        if datetime.utcnow() - created_at > timedelta(days=7):
            raise HTTPException(status_code=403, detail="Kapsül yalnızca 7 gün içinde güncellenebilir")

        # yeni medya varsa 
        media_url = kapsul.get("media_url")
        if media:
            filename = f"{uuid4()}_{media.filename}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(media.file, buffer)
            media_url = f"/{UPLOAD_DIR}/{filename}"

        #güncellenecek alan
        update_data = {}
        if category is not None:
            update_data["category"] = category
        if message is not None:
            update_data["message"] = message
        if send_date is not None:
            update_data["send_date"] = datetime(send_date.year, send_date.month, send_date.day)
        if media_url is not None:
            update_data["media_url"] = media_url

        if not update_data:
            raise HTTPException(status_code=400, detail="Güncellenecek veri gönderilmedi")

        # güncelleme işlemi
        DBConnection.update("capsule", {"_id": ObjectId(capsule_id)}, {"$set": update_data})

        return {"message": "Kapsül güncellendi"}

    except InvalidId:
        raise HTTPException(status_code=400, detail="Geçersiz kapsül ID")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Kapsül güncellenirken hata oluştu: {str(e)}")



# Kapsül silme
@router.delete("/capsules/{id}")
def delete_capsule(id: str):
   
    try:
        existing_kapsul = DBConnection.find_one("capsule",  {"_id":ObjectId(id)})
        if existing_kapsul:
            DBConnection.delete("capsule", {"_id":ObjectId(id)})
        return {"message": "Kapsül başarıyla silindi"}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Geçersiz ID formatı")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sunucu hatası: {str(e)}")
