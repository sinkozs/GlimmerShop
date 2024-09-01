import logging
import os
from functools import partial
from typing import Callable

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from sqlalchemy.ext.asyncio import create_async_engine
from fastapi.middleware.cors import CORSMiddleware

from config.parser import load_config
from config.models import Config
from dependencies import get_session
from models.database import build_session_maker, build_session, get_redis
from routers import auth_router, user_router, product_router, category_router, cart_router, checkout_router, seller_statistics_router


def _resolve_dependencies(app: FastAPI, config: Config) -> FastAPI:
    engine = create_async_engine(config.db_config.url)
    session_factory = build_session_maker(engine)
    get_session_fn: Callable = partial(build_session, session_factory)
    app.dependency_overrides[get_session] = get_session_fn

    get_redis_fn: Callable = partial(get_redis)
    app.dependency_overrides[get_redis] = get_redis_fn

    # Add CORS middleware
    origins = [
        "http://localhost:3000"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/images", StaticFiles(directory="images"), name="static")
    return app


def _register_routers(app: FastAPI):
    app.include_router(auth_router.router)
    app.include_router(user_router.router)
    app.include_router(product_router.router)
    app.include_router(category_router.router)
    app.include_router(cart_router.router)
    app.include_router(checkout_router.router)
    app.include_router(seller_statistics_router.router)


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
    if not os.path.exists("images"):
        os.makedirs("images")

    run_server()

