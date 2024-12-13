from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from dependencies import get_session, get_current_user
from controllers.user_controller import UserController
from services.user_service import UserService
from schemas.schemas import UserCreate, UserUpdate, UserQuery, UserVerification
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/users", tags=["users"], responses={404: {"User": "Not found"}}
)


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(session)


def get_user_controller(
        user_service: UserService = Depends(get_user_service)
) -> UserController:
    return UserController(user_service)


@router.get("")
async def get_all_users(user_controller: UserController = Depends(get_user_controller)) -> JSONResponse:
    return await user_controller.get_all_users()


@router.get("/users-by-role")
async def get_users_by_role(is_seller: bool, user_controller: UserController = Depends(get_user_controller)):
    return await user_controller.get_users_by_role(is_seller)


@router.get("/search/", response_model=List[UserQuery])
async def search_products(
        query: str = Query(...), session: AsyncSession = Depends(get_session)
):
    service = UserService(session)
    user_controller = UserController(service)
    try:
        return await user_controller.search_sellers(query)
    except HTTPException as e:
        raise e


@router.get("/{user_id}")
async def get_user_by_id(user_id, user_controller: UserController = Depends(get_user_controller)) -> JSONResponse:
    return await user_controller.get_user_by_id(user_id)


@router.get("/check-seller/{seller_id}")
async def check_if_seller_exists(seller_id, session: AsyncSession = Depends(get_session)) -> JSONResponse:
    service = UserService(session)
    user_controller = UserController(service)
    try:
        return await user_controller.check_if_seller_exists(seller_id)
    except HTTPException as e:
        raise e


@router.post("/new")
async def create_new_user(user: UserCreate,
                          user_controller: UserController = Depends(get_user_controller)) -> JSONResponse:
    return await user_controller.create_new_user(user)


@router.post("/verify-account")
async def verify_account(ver: UserVerification, user_controller: UserController = Depends(get_user_controller)):
    return await user_controller.verify_user(ver)


@router.post("/resend-verification-email")
async def verify_account(email: str, user_controller: UserController = Depends(get_user_controller)):
    return await user_controller.resend_verification_email(email)


@router.put("/edit")
async def edit_user(
        user_update: UserUpdate,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
):
    service = UserService(session)
    user_controller = UserController(service)
    try:
        user_id: UUID = current_user["user_id"]
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing user ID")
        return await user_controller.edit_user(user_id, user_update)
    except HTTPException as e:
        raise e


@router.delete("/delete")
async def delete_user(
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
):
    service = UserService(session)
    user_controller = UserController(service)
    try:
        user_id: UUID = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing user ID")
        return await user_controller.delete_user(user_id)
    except HTTPException as e:
        raise e
