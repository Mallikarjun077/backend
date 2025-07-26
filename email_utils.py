from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from random import randint
from config import settings
from pydantic import EmailStr


# ✅ Email config
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,        
    MAIL_SSL_TLS=False,         
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER="email_templates"  
)

fm = FastMail(conf)

otp_store = {}

async def send_otp(email: str,name: str):
    otp = str(randint(100000, 999999))
    otp_store[email] = otp

    msg = MessageSchema(
        subject="Your OTP Code",
        recipients=[email],
        template_body={"otp": otp, "name": name},
        subtype="html"
    )

    await fm.send_message(msg, template_name="otp_template.html")
    return otp

async def send_profile_liked_email(email: EmailStr, liker_name: str):
    try:
        message = MessageSchema(
            subject="Someone Liked Your Profile!",
            recipients=[email],
            body=f"Hi,\n\n{liker_name} liked your profile on our Matri App!\nCheck it out!",
            subtype="plain"
        )
        fm = FastMail(conf)
        await fm.send_message(message)
        print(f"✅ Email sent to {email}")
    except Exception as e:
        print(f"❌ Failed to send email to {email}: {e}")