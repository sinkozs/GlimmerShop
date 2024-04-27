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
class AuthConfig:
    secret_key: str


@dataclass
class Config:
    db_config: DatabaseConfig
    server_config: ServerConfig
    auth_config: AuthConfig


