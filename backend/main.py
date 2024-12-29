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
    cart_router,
    checkout_router,
    seller_statistics_router,
)


async def initialize_categories(session_factory) -> None:
    """Initialize default categories if they don't exist."""
    default_categories = ["Necklaces", "Bracelets", "Rings", "Earrings"]
    async_session = session_factory()
    async with async_session as session:
        async with session.begin():
            result = await session.execute(select(Category))
            categories = result.scalars().all()
            print(f"categories in DB {categories}")
            if not categories:
                for category_name in default_categories:
                    print(f"Save new category: {category_name}")
                    new_category = Category(category_name=category_name)
                    session.add(new_category)


def resolve_dependencies(app: FastAPI, config: Config) -> FastAPI:
    engine = create_async_engine(config.db_config.url)
    session_factory = build_session_maker(engine)
    get_session_fn: Callable = partial(build_session, session_factory)
    app.dependency_overrides[get_session] = get_session_fn

    app.state.session_factory = session_factory

    # Add CORS middleware
    origins = [
        load_config().server_config.frontend_domain,
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


def create_app() -> FastAPI:
    config = load_config()
    app = FastAPI()

    @app.on_event("startup")
    async def startup_event():
        """Execute startup tasks."""
        await initialize_categories(app.state.session_factory)
        logging.info("Categories initialized")

    app = resolve_dependencies(app, config)
    _register_routers(app)
    logging.info("Successfully initialized")
    return app


def main():
    return create_app()


def run_server():
    server_cfg = load_config().server_config
    print(server_cfg)
    uvicorn.run("main:main", host=server_cfg.host, port=server_cfg.port, reload=True)


if __name__ == "__main__":
    if not os.path.exists("images"):
        os.makedirs("images")

    run_server()
