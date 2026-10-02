import logging
import smtplib
from email.message import EmailMessage
import random
import string
from datetime import datetime, timedelta, timezone
from app.database import get_db

logger = logging.getLogger(__name__)

# Basic SMTP Settings (Update these with real credentials in production/env)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
# Use app passwords if using gmail
SMTP_USERNAME = "sureshreigns220@gmail.com"
SMTP_PASSWORD = "lidfbwyucfshstir" 
SENDER_EMAIL = "sureshreigns220@gmail.com"

def generate_otp() -> str:
    """Generate a 6-digit numerical OTP."""
    return "".join(random.choices(string.digits, k=6))

async def create_and_send_otp(user_id: int, email: str) -> bool:
    """Generates an OTP, stores it in DB, and sends it via email."""
    otp_code = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    try:
        async for db in get_db():
            # Store OTP in DB
            await db.execute(
                "INSERT INTO otps (user_id, otp_code, expires_at) VALUES ($1, $2, $3)",
                user_id, otp_code, expires_at
            )
    except Exception as e:
        logger.error(f"Failed to store OTP for {email}: {e}")
        return False
        
    # Send Email
    msg = EmailMessage()
    msg.set_content(f"Your Gourmet AI verification code is: {otp_code}\n\nThis code will expire in 10 minutes.")
    msg['Subject'] = "Gourmet AI - Verification Code"
    msg['From'] = SENDER_EMAIL
    msg['To'] = email

    try:
        # In a real app, use aiosmtplib for async sending. 
        # For simplicity and robust standard library support, we use smtplib here but it will block. 
        # In production this should be offloaded to a background task or use aiosmtplib.
        # We will wrap it in a try-except to avoid crashing the flow if SMTP is not configured
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        logger.warning(f"Email could not be sent to {email}. Are SMTP credentials configured? Error: {e}")
        # Return True for development purposes even if email fails, so we can test the flow.
        # In production, return False.
        logger.info(f"DEVELOPMENT OVERRIDE: The OTP for {email} is {otp_code}")
        return True
