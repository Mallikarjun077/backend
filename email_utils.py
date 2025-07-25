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

async def send_profile_liked_email(to_email: EmailStr, liker_name: str):
    message = MessageSchema(
        subject="Someone liked your profile!",
        recipients=[to_email],
        body=f"""
        Hello,
        {liker_name}

        liked your profile on Nekar Vivah Vedike App!
        Open the app and see who is interested in you.

        Regards,
        Nekar Vivah Vedike Team
        """,
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
