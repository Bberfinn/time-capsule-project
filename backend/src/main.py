from fastapi import FastAPI
from routers.login import router as login
from routers.register import router as register
from routers.categories import router as categories
from routers.capsule_router import router as capsule_router
from routers.edit_profile import router as edit_profile
from routers.hesap_ayarlari import router as hesap_ayarlari
from routers.check_capsules import router as check_capsules
from database.db_connection import DBConnection
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers.scheduler import start_scheduler
import os
from dotenv import load_dotenv
load_dotenv()

load_dotenv()
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

app = FastAPI()

app.mount("/uploaded_files", StaticFiles(directory="uploaded_files"), name="uploaded_files")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Gerekirse izin verilecek domainler
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DBConnection.initialize()

app.include_router(login)
app.include_router(register)
app.include_router(categories)
app.include_router(capsule_router)
app.include_router(edit_profile)
app.include_router(hesap_ayarlari)
app.include_router(check_capsules)

@app.on_event("startup")
async def startup_event():
    start_scheduler()

@app.get("/")
def read_root():
    return {"message": "API çalışıyor!"}
