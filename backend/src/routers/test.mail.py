from routers.email import send_capsule_email

if __name__ == "__main__":
    to = "berfinalgs@gmail.com"  
    subject = "Test Mail - Zaman Kapsülü"
    body = "Merhaba, bu test maili Zaman Kapsülü projesinden gönderildi."
    
    send_capsule_email(to, subject, body)
