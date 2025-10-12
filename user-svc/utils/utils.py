from pydantic import Field, PostgresDsn, RedisDsn, EmailStr, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Application configuration settings.

    Attributes:
        database_url (PostgresDsn): Connection string for this service's database.
        redis_url (RedisDsn): Redis connection string for caching or queues.

        jwt_secret (str): Secret key for signing JWT access tokens.
        verify_token_secret (str): Secret key for email verification tokens.
        reset_token_secret (str): Secret key for password reset tokens.
        verify_token_expire_seconds (int): Token lifetime (seconds) for verification links.
        reset_token_expire_seconds (int): Token lifetime (seconds) for password resets.

        default_role_id (int): Default role assigned to newly registered users.

        log_name (str): Identifier name for the log file or log source.
        log_level (str): Logging verbosity level.
        log_dir (str): Directory where log files are stored.
    """
    # Database & Redis Configuration
    database_url: PostgresDsn
    redis_url: RedisDsn

    # Authentication & Token Configuration
    jwt_secret: str = Field(min_length=32, description="Secret for JWT access tokens")
    verify_token_secret: str = Field(min_length=32, description="Secret for email verification tokens")
    reset_token_secret: str = Field(min_length=32, description="Secret for password reset tokens")

    verify_token_expire_seconds: int = Field(default=3600, description="Lifetime (s) of email verification tokens")
    reset_token_expire_seconds: int = Field(default=3600, description="Lifetime (s) of password reset tokens")

    # User Service Configuration
    default_role_id: int = Field(default=1, description="Default role ID for new users")
    verify_email_base: str = Field(
        default="http://localhost:8000/verify", description="Base URL for email verification links"
    )
    password_reset_base: str = Field(
        default="http://localhost:8000/reset-password", description="Base URL for password reset links"
    )

    # Email Configuration
    mail_from_address: EmailStr = Field(description="Email address used in the 'from' field of emails")
    mail_from_name: str = Field(description="Name displayed in the 'from' field of emails")
    mail_host: str = Field(description="SMTP server host for sending emails")
    mail_port: int = Field(default=587, description="SMTP server port for sending emails")
    mail_username: str = Field(description="SMTP server username for authentication")
    mail_password: SecretStr = Field(description="SMTP server password for authentication")
    mail_starttls: bool = Field(default=True, description="Whether to use STARTTLS for SMTP connection")
    mail_ssl_tls: bool = Field(default=False, description="Whether to use SSL/TLS")

    # Logging config
    log_name: str = Field(description="Service log name (used for file naming or context)")
    log_level: str = Field(default="INFO", description="Logging verbosity level")
    log_dir: str = Field(default="./logs", description="Directory where logs are stored")

    # Meta Config
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
