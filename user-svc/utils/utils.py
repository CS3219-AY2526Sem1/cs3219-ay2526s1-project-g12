from pydantic import EmailStr, Field, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Application configuration settings loaded from environment variables.

    Attributes:
        database_url (PostgresDsn): PostgreSQL connection string for the service database.

        jwt_secret (str): Secret for JWT access tokens (min length 32).
        verify_token_secret (str): Secret for email verification tokens (min length 32).
        reset_token_secret (str): Secret for password reset tokens (min length 32).

        verify_token_expire_seconds (int): Token lifetime in seconds for verification links. Default: 3600.
        reset_token_expire_seconds (int): Token lifetime in seconds for password resets. Default: 3600.

        default_role_id (int): Default role ID for newly registered users. Default: 1.
        verify_email_base (str): Base URL for email verification links. Default: http://localhost:8000/verify.
        password_reset_base (str): Base URL for password reset links. Default: http://localhost:8000/reset-password.

        mail_from_address (EmailStr): Sender email address used in outbound emails.
        mail_from_name (str): Sender display name used in outbound emails.
        mail_host (str): SMTP server host.
        mail_port (int): SMTP server port. Default: 587.
        mail_username (str): SMTP username.
        mail_password (SecretStr): SMTP password.
        mail_starttls (bool): Whether to use STARTTLS. Default: True.
        mail_ssl_tls (bool): Whether to use SSL/TLS. Default: False.

        log_name (str): Service log identifier for logs.
        log_level (str): Logging verbosity level. Default: INFO.
        log_dir (str): Directory where logs are stored. Default: ./logs.
    """

    # Database & Redis Configuration
    database_url: PostgresDsn

    # Authentication & Token Configuration
    jwt_secret: str = Field(min_length=32, description="Secret for JWT access tokens")
    verify_token_secret: str = Field(
        min_length=32, description="Secret for email verification tokens"
    )
    reset_token_secret: str = Field(
        min_length=32, description="Secret for password reset tokens"
    )

    verify_token_expire_seconds: int = Field(
        default=3600, description="Lifetime (s) of email verification tokens"
    )
    reset_token_expire_seconds: int = Field(
        default=3600, description="Lifetime (s) of password reset tokens"
    )

    # User Service Configuration
    default_role_id: int = Field(default=1, description="Default role ID for new users")
    verify_email_base: str = Field(
        default="http://localhost:8000/verify",
        description="Base URL for email verification links",
    )
    password_reset_base: str = Field(
        default="http://localhost:8000/reset-password",
        description="Base URL for password reset links",
    )

    # Email Configuration
    mail_from_address: EmailStr = Field(
        description="Email address used in the 'from' field of emails"
    )
    mail_from_name: str = Field(
        description="Name displayed in the 'from' field of emails"
    )
    mail_host: str = Field(description="SMTP server host for sending emails")
    mail_port: int = Field(
        default=587, description="SMTP server port for sending emails"
    )
    mail_username: str = Field(description="SMTP server username for authentication")
    mail_password: SecretStr = Field(
        description="SMTP server password for authentication"
    )
    mail_starttls: bool = Field(
        default=True, description="Whether to use STARTTLS for SMTP connection"
    )
    mail_ssl_tls: bool = Field(default=False, description="Whether to use SSL/TLS")

    # Logging config
    log_name: str = Field(
        description="Service log name (used for file naming or context)"
    )
    log_level: str = Field(default="INFO", description="Logging verbosity level")
    log_dir: str = Field(
        default="./logs", description="Directory where logs are stored"
    )

    # Meta Config
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
