from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Application configuration settings.

    Attributes:
        database_url (str): The database connection URL.
        redis_url (str): The Redis connection URL.
        jwt_secret (str): The secret key for JWT authentication.
        access_token_expire_seconds (int): The expiration time for access tokens in seconds.
        default_role_id (int): The default role ID for new users.
        cookie_name (str): The name of the authentication cookie.
        log_name (str): The name of the log file.
        log_level (str): The logging level (e.g., "INFO", "DEBUG").
        log_dir (str): The directory where log files are stored.
    """
    # Database config
    database_url: PostgresDsn
    redis_url: RedisDsn

    # JWT config
    jwt_secret: str = Field(min_length=32)
    access_token_expire_seconds: int

    # User service config
    default_role_id: int = 1
    cookie_name: str = "auth"

    # Logging config
    log_name: str
    log_level: str = "INFO"
    log_dir: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
