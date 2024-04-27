import logging
from functools import partial
from fastapi import FastAPI
import uvicorn
from sqlalchemy.ext.asyncio import create_async_engine

from config.parser import load_config
from config.models import Config
from dependencies import get_session
from models.database import build_session_maker, build_session
from routers import auth_router


def _resolve_dependencies(app: FastAPI, config: Config) -> FastAPI:
    engine = create_async_engine(config.db_config.url)
    session_factory = build_session_maker(engine)
    get_session_fn = partial(build_session, session_factory)
    app.dependency_overrides[get_session] = get_session_fn

    return app


def _register_routers(app: FastAPI):
    app.include_router(auth_router.router)


def main():
    config = load_config()
    app = FastAPI()
    logging.info(f"Successfully initialized")

    app = _resolve_dependencies(app, config)
    _register_routers(app)
    return app


def run_server():
    server_cfg = load_config().server_config
    print(server_cfg)
    uvicorn.run(
        "main:main",
        host=server_cfg.host,
        port=server_cfg.port,
        reload=True
    )


if __name__ == '__main__':
    run_server()
