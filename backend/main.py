import logging
import os
from functools import partial
from typing import Callable
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine
from fastapi.middleware.cors import CORSMiddleware

from models.models import Category
from config.parser import load_config
from config.models import Config
from dependencies import get_session
from models.database import build_session_maker, build_session
from routers import (
    auth_router,
    user_router,
    product_router,
    category_router,
    order_router,
    checkout_router,
    seller_statistics_router,
)


async def initialize_categories(session_factory, default_categories: list[str]) -> None:
    async with session_factory() as session:
        async with session.begin():
            result = await session.execute(select(Category))
            categories = result.scalars().all()

            if not categories:
                for category_name in default_categories:
                    logging.info(f"Creating category: {category_name}")
                    new_category = Category(category_name=category_name, is_default=True)
                    session.add(new_category)


def resolve_dependencies(app: FastAPI, config: Config) -> FastAPI:
    engine = create_async_engine(config.db_config.url)
    session_factory = build_session_maker(engine)
    get_session_fn: Callable = partial(build_session, session_factory)

    app.dependency_overrides[get_session] = get_session_fn
    app.state.session_factory = session_factory
    app.state.config = config

    origins = [
        config.server_config.customer_frontend_domain,
        config.server_config.seller_frontend_domain,
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


def register_routers(app: FastAPI) -> None:
    app.include_router(auth_router.router)
    app.include_router(user_router.router)
    app.include_router(order_router.router)
    app.include_router(product_router.router)
    app.include_router(category_router.router)
    app.include_router(checkout_router.router)
    app.include_router(seller_statistics_router.router)


def create_app(config: Config | None = None) -> FastAPI:
    if config is None:
        config = load_config()

    app = FastAPI()
    app = resolve_dependencies(app, config)

    register_routers(app)

    @app.on_event("startup")
    async def startup_event():
        await initialize_categories(
            app.state.session_factory,
            config.app_config.default_categories
        )
        logging.info(f"Categories initialized: {config.app_config.default_categories}")
        logging.info("Application startup complete")

    return app


def main():
    return create_app()


def run_server():
    if not os.path.exists("images"):
        os.makedirs("images")

    config = load_config()
    server_cfg = config.server_config

    logging.info(f"Starting server on {server_cfg.host}:{server_cfg.port}")

    uvicorn.run(
        "main:main",
        host=server_cfg.host,
        port=server_cfg.port,
        reload=True
    )


if __name__ == "__main__":
    run_server()
