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
    def url(self)->str:
        url = f'{self.db_backend}+{self.connector}://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}'
        return url


@dataclass
class ServerConfig:
    host: str
    port: int


@dataclass
class SMTPConfig:
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    verification_email_sender: str
    verification_email_subject: str
    verification_email_message: str
    verification_code_expiration_minutes: int


@dataclass
class AuthConfig:
    secret_key: str
    token_expiry_minutes: int


@dataclass
class Config:
    db_config: DatabaseConfig
    server_config: ServerConfig
    smtp_config: SMTPConfig
    auth_config: AuthConfig


