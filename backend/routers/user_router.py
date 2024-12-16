from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
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


@router.get("/by-type")
async def get_users_by_type(is_seller: bool,
                            user_controller: UserController = Depends(get_user_controller)) -> JSONResponse:
    return await user_controller.get_users_by_type(is_seller)


@router.get("/sellers/search", response_model=List[UserQuery])
async def search_products(
        query: str = Query(...), session: AsyncSession = Depends(get_session)
) -> List[UserQuery]:
    service = UserService(session)
    user_controller = UserController(service)
    try:
        return await user_controller.search_sellers(query)
    except HTTPException as e:
        raise e


@router.get("/{user_id}")
async def get_user_by_id(user_id, user_controller: UserController = Depends(get_user_controller)) -> JSONResponse:
    return await user_controller.get_user_by_id(user_id)


@router.get("/sellers/{seller_id}")
async def get_seller(seller_id, user_controller: UserController = Depends(get_user_controller)) -> JSONResponse:
    return await user_controller.check_seller_exists(seller_id)


@router.post("/create")
async def create_new_user(user: UserCreate,
                          user_controller: UserController = Depends(get_user_controller)) -> JSONResponse:
    return await user_controller.create_new_user(user)


@router.post("/verify")
async def verify_user(verification: UserVerification,
                      user_controller: UserController = Depends(get_user_controller)) -> JSONResponse:
    return await user_controller.verify_user(verification)


@router.post("/verify/resend")
async def resend_verification(email: str,
                              user_controller: UserController = Depends(get_user_controller)) -> JSONResponse:
    return await user_controller.resend_verification_email(email)


@router.put("/me")
async def edit_user(
        user_update: UserUpdate,
        current_user: dict = Depends(get_current_user),
        user_controller: UserController = Depends(get_user_controller),
) -> JSONResponse:
    user_id: UUID = current_user["user_id"]
    return await user_controller.edit_user(user_id, user_update)


@router.delete("/me")
async def delete_user(
        current_user: dict = Depends(get_current_user),
        user_controller: UserController = Depends(get_user_controller),
) -> JSONResponse:
    user_id: UUID = current_user["user_id"]
    return await user_controller.delete_user(user_id)
