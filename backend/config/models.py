from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    user: str
    password: str
    host: str
    port: int
    database: str
    db_backend: str = "postgresql"
    connector: str = "asyncpg"

    @property
    def url(self) -> str:
        url = f"{self.db_backend}+{self.connector}://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        return url


@dataclass
class ServerConfig:
    host: str
    port: int
    customer_frontend_port: int
    seller_frontend_port: int
    connector: str = "http"

    @property
    def customer_frontend_domain(self) -> str:
        customer_frontend_domain = (
            f"{self.connector}://{self.host}:{self.customer_frontend_port}"
        )
        return customer_frontend_domain

    @property
    def seller_frontend_domain(self) -> str:
        seller_frontend_domain = (
            f"{self.connector}://{self.host}:{self.seller_frontend_port}"
        )
        return seller_frontend_domain


@dataclass
class SMTPConfig:
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    sender_email: str
    verification_email_subject: str
    verification_email_message: str
    verification_email_message: str
    verification_code_expiration_minutes: int
    password_reset_email_subject: str
    password_reset_email_message: str
    password_expiration_minutes: int


@dataclass
class AuthConfig:
    private_key_path: str
    public_key_path: str
    token_expiry_minutes: int
    min_password_length: int
    http_session_secret: str
    stripe_secret_key: str

    def load_private_key(self) -> bytes:
        with open(self.private_key_path, "rb") as f:
            return f.read()

    def load_public_key(self) -> bytes:
        with open(self.public_key_path, "rb") as f:
            return f.read()


@dataclass
class AppConfig:
    default_categories: list[str]


@dataclass
class Config:
    db_config: DatabaseConfig
    test_db_config: DatabaseConfig
    server_config: ServerConfig
    smtp_config: SMTPConfig
    auth_config: AuthConfig
    app_config: AppConfig
