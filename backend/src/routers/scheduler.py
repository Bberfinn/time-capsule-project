from apscheduler.schedulers.asyncio import AsyncIOScheduler
from routers.utils import get_capsules_to_open
from routers.email import send_capsule_email
from datetime import date

scheduler = AsyncIOScheduler()

def daily_capsule_check():
    print("Scheduler çalıştı, kapsüller kontrol ediliyor...")
    today = date.today()
    capsules = get_capsules_to_open(today)
    if not capsules:
        print("Bugün açılacak kapsül yok.")
        return

    for capsule in capsules:
        send_capsule_email(
            to_email=capsule["user_email"],
            subject="📬 Zaman Kapsülün Açıldı!",
            body=f"Merhaba {capsule['user_name']}, bugün kapsülün açıldı! Mesajını görmek için uygulamayı ziyaret et."
        )
    print(f"{len(capsules)} kapsüle e-posta gönderildi.")

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(daily_capsule_check, 'cron', hour=0, minute=0)
        scheduler.start()
        print("Scheduler başladı.")
