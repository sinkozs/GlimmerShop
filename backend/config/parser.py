from configparser import ConfigParser
import os

from dotenv import load_dotenv
from config.models import DatabaseConfig, ServerConfig, AuthConfig, SMTPConfig, Config

DEFAULT_ENV_PATH = ".env"  # for sensitive info + info for docker containers
DEFAULT_CONFIG_PATH = "config/local.ini"  # for public application info


def load_config(config_path: str = DEFAULT_CONFIG_PATH, env_path: str = DEFAULT_ENV_PATH) -> Config:
    load_dotenv(env_path)
    parser = ConfigParser()
    parser.read(config_path)

    db_config = DatabaseConfig(
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=int(os.getenv("POSTGRES_PORT")),
        database=os.getenv("POSTGRES_DB")
    )

    server_config = ServerConfig(
        host=parser.get("server", "Host"),
        port=int(parser.get("server", "Port"))
    )

    smtp_config = SMTPConfig(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        smtp_username=os.getenv("SMTP_USERNAME"),
        smtp_password=os.getenv("SMTP_PASSWORD"),
        email_sender=parser.get("smtp-account-verification", "Sender"),
        verification_email_subject=parser.get("smtp-account-verification", "Subject"),
        verification_email_message=parser.get("smtp-account-verification", "Message"),
        verification_code_expiration_minutes=int(parser.get("smtp-account-verification", "CodeExpirationMinutes")),
        password_reset_email_subject=parser.get("smtp-forgotten-password", "Subject"),
        password_reset_email_message=parser.get("smtp-forgotten-password", "Message"),
        password_expiration_minutes=int(parser.get("smtp-forgotten-password", "PasswordExpirationMinutes")),
    )

    auth_config = AuthConfig(
        secret_key=os.getenv("SECRET_KEY"),
        token_expiry_minutes=int(os.getenv("TOKEN_EXPIRY_MINUTES")),
        min_password_length=int(parser.get("auth", "MinPasswordLength"))
    )

    config = Config(
        db_config=db_config,
        server_config=server_config,
        smtp_config=smtp_config,
        auth_config=auth_config
    )

    return config
