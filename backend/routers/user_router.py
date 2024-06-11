from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_session
from controllers.user_controller import UserController
from services.user_service import UserService
from schemas.schemas import UserCreate, UserUpdate

from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"User": "Not found"}}
)


@router.get("")
async def get_all_users(session: AsyncSession = Depends(get_session)):
    service = UserService(session)
    user_controller = UserController(service)
    try:
        return await user_controller.get_all_users()
    except HTTPException as e:
        raise e


@router.get("/users-by-role")
async def get_users_by_role(is_seller: bool, session: AsyncSession = Depends(get_session)):
    service = UserService(session)
    user_controller = UserController(service)
    try:
        return await user_controller.get_users_by_role(is_seller)
    except HTTPException as e:
        raise e


@router.get("/{user_id}")
async def get_user_by_id(user_id,
                         session: AsyncSession = Depends(get_session)):
    service = UserService(session)
    user_controller = UserController(service)

    try:
        return await user_controller.get_user_by_id(user_id)
    except HTTPException as e:
        raise e


@router.post("/new")
async def create_new_user(user: UserCreate, session: AsyncSession = Depends(get_session)):
    service = UserService(session)
    user_controller = UserController(service)
    try:
        return await user_controller.create_new_user(user)
    except HTTPException as e:
        raise e


@router.put("/edit")
async def edit_user(user_id: UUID, user: UserUpdate, session: AsyncSession = Depends(get_session)):
    service = UserService(session)
    user_controller = UserController(service)
    try:
        return await user_controller.edit_user(user_id, user)
    except HTTPException as e:
        raise e


@router.delete("/delete")
async def delete_user(user_id, session: AsyncSession = Depends(get_session)):
    service = UserService(session)
    user_controller = UserController(service)
    try:
        return await user_controller.delete_user(user_id)
    except HTTPException as e:
        raise e
