from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from random import randint
from config import settings

# ✅ Email config
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,         # STARTTLS
    MAIL_SSL_TLS=False,         # Not using SSL
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER="email_templates"  # Folder must exist
)

fm = FastMail(conf)

# ⚠️ For demo only — use a database in production
otp_store = {}

# ✅ Send OTP email using template
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
