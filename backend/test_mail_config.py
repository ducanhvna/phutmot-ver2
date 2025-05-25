import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "HRMS")
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() == "true"

MAIL_TO = os.getenv("MAIL_TO", MAIL_FROM)  # Gửi về chính mình nếu không set

print("[INFO] Loaded mail config:")
print(f"MAIL_SERVER={MAIL_SERVER}")
print(f"MAIL_PORT={MAIL_PORT}")
print(f"MAIL_USERNAME={MAIL_USERNAME}")
print(f"MAIL_PASSWORD={'***' if MAIL_PASSWORD else None}")
print(f"MAIL_FROM={MAIL_FROM}")
print(f"MAIL_FROM_NAME={MAIL_FROM_NAME}")
print(f"MAIL_USE_TLS={MAIL_USE_TLS}")
print(f"MAIL_USE_SSL={MAIL_USE_SSL}")
print(f"MAIL_TO={MAIL_TO}")

msg = MIMEMultipart()
msg["From"] = f"{MAIL_FROM_NAME} <{MAIL_FROM}>"
msg["To"] = MAIL_TO
msg["Subject"] = "Test mail config from FastAPI project"
msg.attach(MIMEText("This is a test email from your FastAPI project mail config.", "plain"))

try:
    if MAIL_USE_SSL:
        server = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
    else:
        server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
        if MAIL_USE_TLS:
            server.starttls()
    server.login(MAIL_USERNAME, MAIL_PASSWORD)
    server.sendmail(MAIL_FROM, MAIL_TO, msg.as_string())
    server.quit()
    print(f"[OK] Test email sent successfully to {MAIL_TO}")
except Exception as e:
    print(f"[ERROR] Failed to send test email: {e}")
