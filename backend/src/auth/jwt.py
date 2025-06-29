import os
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulama başarısız",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) #token geçerli mi diye kontrol edilir
        user_id: str = payload.get("sub")
        print("Current user:", user_id)
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception

def create_token(user_id:str):
 data = {"sub":user_id} #kullanıcı kimliğini ekle
 expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # 30 dakikayı ayarlıyoruz
 data.update({"exp": expire}) # kk'ne geçerlilik süresi ekle
 encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)  #tokenı oluşturur
 return encoded_jwt



'''def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        return user_id
    except JWTError:
        raise ValueError("Token doğrulanamadı")'''


#to_encode: Token içine koyulacak bilgiler (kullanıcı bilgileri + süre).