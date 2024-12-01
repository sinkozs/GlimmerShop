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
    frontend_port: int
    connector: str = "http"

    @property
    def frontend_domain(self) -> str:
        frontend_domain = f"{self.connector}://{self.host}:{self.frontend_port}"
        return frontend_domain


@dataclass
class RedisConfig:
    host: str
    port: int
    password: str
    connector: str = "redis"

    @property
    def url(self) -> str:
        url = f"{self.connector}://:{self.password}@{self.host}:{self.port}"
        return url


@dataclass
class SMTPConfig:
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    sender_email: str
    verification_email_subject: str
    verification_email_message: str
    verification_code_expiration_minutes: int
    password_reset_email_subject: str
    password_reset_email_message: str
    password_expiration_minutes: int


@dataclass
class AuthConfig:
    secret_key: str
    token_expiry_minutes: int
    min_password_length: int
    http_session_secret: str
    stripe_secret_key: str


@dataclass
class Config:
    db_config: DatabaseConfig
    server_config: ServerConfig
    redis_config: RedisConfig
    smtp_config: SMTPConfig
    auth_config: AuthConfig
