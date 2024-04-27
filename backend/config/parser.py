from configparser import ConfigParser
import os

from dotenv import load_dotenv
from config.models import DatabaseConfig, ServerConfig, AuthConfig, Config

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

    auth_config = AuthConfig(
        secret_key=os.getenv("SECRET_KEY")
    )

    config = Config(
        db_config=db_config,
        server_config=server_config,
        auth_config=auth_config,

    )

    return config
