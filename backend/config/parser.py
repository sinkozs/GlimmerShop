from configparser import ConfigParser
import os
from dotenv import load_dotenv
from config.models import (
    DatabaseConfig,
    ServerConfig,
    AuthConfig,
    SMTPConfig,
    AppConfig,
    Config
)

DEFAULT_ENV_PATH = ".env"  # for sensitive info + info for docker containers
DEFAULT_CONFIG_PATH = "config/local.ini"  # for public application info


def parse_comma_separated(value: str) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def load_config(
        config_path: str = DEFAULT_CONFIG_PATH, env_path: str = DEFAULT_ENV_PATH
) -> Config:
    load_dotenv(env_path)
    parser = ConfigParser()
    parser.read(config_path)
    db_config = DatabaseConfig(
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=int(os.getenv("POSTGRES_PORT")),
        database=os.getenv("POSTGRES_DB"),
    )
    test_db_config = DatabaseConfig(
        user=os.getenv("TEST_POSTGRES_USER"),
        password=os.getenv("TEST_POSTGRES_PASSWORD"),
        host=os.getenv("TEST_POSTGRES_HOST"),
        port=int(os.getenv("TEST_POSTGRES_PORT")),
        database=os.getenv("TEST_POSTGRES_DB"),
    )
    server_config = ServerConfig(
        host=parser.get("server", "Host"),
        port=int(parser.get("server", "Port")),
        customer_frontend_port=int(parser.get("server", "CustomerFrontendPort")),
        seller_frontend_port=int(parser.get("server", "SellerFrontendPort")),
    )

    smtp_config = SMTPConfig(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        smtp_username=os.getenv("SMTP_USERNAME"),
        smtp_password=os.getenv("SMTP_PASSWORD"),
        sender_email=parser.get("smtp-account-verification", "Sender"),
        verification_email_subject=parser.get("smtp-account-verification", "Subject"),
        verification_email_message=parser.get("smtp-account-verification", "Message"),
        verification_code_expiration_minutes=int(
            parser.get("smtp-account-verification", "CodeExpirationMinutes")
        ),
        password_reset_email_subject=parser.get("smtp-forgotten-password", "Subject"),
        password_reset_email_message=parser.get("smtp-forgotten-password", "Message"),
        password_expiration_minutes=int(
            parser.get("smtp-forgotten-password", "PasswordExpirationMinutes")
        ),
    )
    auth_config = AuthConfig(
        private_key_path=os.path.join(parser.get("auth", "RSAKeyPath"), "private.pem"),
        public_key_path=os.path.join(parser.get("auth", "RSAKeyPath"), "public.pem"),
        token_expiry_minutes=int(os.getenv("TOKEN_EXPIRY_MINUTES")),
        min_password_length=int(parser.get("auth", "MinPasswordLength")),
        http_session_secret=os.getenv("HTTP_SESSION_SECRET"),
        stripe_secret_key=os.getenv("STRIPE_API_KEY"),
    )
    app_config = AppConfig(
        default_categories=parse_comma_separated(parser.get("app-config", "DefaultCategories", fallback=""))
    )

    config = Config(
        db_config=db_config,
        test_db_config=test_db_config,
        server_config=server_config,
        smtp_config=smtp_config,
        auth_config=auth_config,
        app_config=app_config
    )
    return config
