from fastapi import APIRouter
from datetime import date
from routers.utils import get_capsules_to_open
from routers.email import send_capsule_email

router = APIRouter()

@router.get("/check-capsules")
def check_capsules():
    today = date.today()
    capsules = get_capsules_to_open(today)

    if not capsules:
        return {"message": "Bugün açılacak kapsül yok."}

    for capsule in capsules:
        send_capsule_email(
            to_email=capsule["user_email"],
            subject="📬 Zaman Kapsülün Açıldı!",
            body=f"Merhaba {capsule['user_name']}, bugün kapsülün açıldı! Mesajını görmek için uygulamayı ziyaret et."
        )

    return {"message": f"{len(capsules)} kapsüle e-posta gönderildi."}
