from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    email:EmailStr
    password: str
    name: Optional [str]=None
    status:bool=True