from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from typing import Optional
from datetime import date, datetime
import uuid


class Capsule(BaseModel):
    category: Optional[str] = Field(default="")
    message: str
    send_date: date
    user_id: Optional[str]
    id: str = Field(default_factory=lambda: str(uuid.uuid4())) #kapsül idsi
    created_at: datetime = Field(default_factory=datetime.utcnow) #oluşturulma zamanı otomatik atanır


