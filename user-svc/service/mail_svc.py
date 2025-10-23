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

def create_email_with_button(
    user_name: str,
    message_text: str,
    hyperlink_text: str,
    link_url: str
) -> str:
    """Creates an HTML email template with a styled button.
    
    Args:
        user_name (str): The user's first name.
        message_text (str): The message to display above the button.
        hyperlink_text (str): The text to display on the button.
        link_url (str): The URL the button should link to.
        
    Returns:
        str: The formatted HTML email body.
    """
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <p>Hi {user_name},</p>
            <p>{message_text}</p>
            <p style="margin: 30px 0;">
                <a href="{link_url}" 
                   style="background-color: #007bff; 
                          color: white; 
                          padding: 12px 24px; 
                          text-decoration: none; 
                          border-radius: 4px; 
                          display: inline-block;">
                    {hyperlink_text}
                </a>
            </p>
        </body>
    </html>
    """


async def send_verification_email(user: User, token: str):
    """Sends a verification email to the user with the provided token.

    Args:
        user (User): The user to send the email to.
        token (str): The verification token to include in the email.
    """
    verify_link = f"{config.verify_email_base}?token={token}"
    html_body = create_email_with_button(
        user_name=user.first_name,
        message_text="Please verify your email address by clicking the link below:",
        hyperlink_text="Verify Email",
        link_url=verify_link
    )
    
    message = MessageSchema(
        subject="Verify your email",
        recipients=[user.email],
        body=html_body,
        subtype=MessageType.html,
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
    html_body = create_email_with_button(
        user_name=user.first_name,
        message_text="You can reset your password by clicking the link below:",
        hyperlink_text="Reset Password",
        link_url=reset_link
    )
    
    message = MessageSchema(
        subject="Reset your password",
        recipients=[user.email],
        body=html_body,
        subtype=MessageType.html,
    )
    log.info(f"Sending password reset email to {user.email}.")
    await fm.send_message(message)
