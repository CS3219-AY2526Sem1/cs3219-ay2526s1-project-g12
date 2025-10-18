from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from models.db_models import User
from utils.logger import log
from utils.utils import AppConfig

config = AppConfig()

mail_conf = ConnectionConfig(
    MAIL_USERNAME=config.mail_username,
    MAIL_PASSWORD=config.mail_password,
    MAIL_FROM=config.mail_from_address,
    MAIL_FROM_NAME=config.mail_from_name,
    MAIL_PORT=config.mail_port,
    MAIL_SERVER=config.mail_host,
    MAIL_STARTTLS=config.mail_starttls,
    MAIL_SSL_TLS=config.mail_ssl_tls,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

fm = FastMail(mail_conf)

async def send_verification_email(user: User, token: str):
    """Sends a verification email to the user with the provided token.

    Args:
        user (User): The user to send the email to.
        token (str): The verification token to include in the email.
    """
    verify_link = f"{config.verify_email_base}?token={token}"
    message = MessageSchema(
        subject="Verify your email",
        recipients=[user.email],
        body=f"Hi {user.first_name}, please verify your email by clicking on the following link: {verify_link}",
        subtype=MessageType.plain,
    )
    log.info(f"Sending verification email to {user.email}.")
    await fm.send_message(message)

async def send_password_reset_email(user: User, token: str):
    """Sends a password reset email to the user with the provided token.

    Args:
        user (User): The user to send the email to.
        token (str): The password reset token to include in the email.
    """
    reset_link = f"{config.password_reset_base}?token={token}"
    message = MessageSchema(
        subject="Reset your password",
        recipients=[user.email],
        body=f"Hi {user.first_name}, you can reset your password by clicking on the following link: {reset_link}",
        subtype=MessageType.plain,
    )
    log.info(f"Sending password reset email to {user.email}.")
    await fm.send_message(message)
