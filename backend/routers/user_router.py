from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from dependencies import get_session, get_current_user
from controllers.user_controller import UserController
from services.user_service import UserService
from schemas.schemas import UserCreate, UserUpdate, UserQuery

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


@router.get("/search/", response_model=List[UserQuery])
async def search_products(query: str = Query(...), session: AsyncSession = Depends(get_session)):
    service = UserService(session)
    user_controller = UserController(service)
    try:
        return await user_controller.search_sellers(query)
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


@router.get("/public/{user_id}")
async def get_public_user_info_by_id(user_id,
                                     session: AsyncSession = Depends(get_session)):
    service = UserService(session)
    user_controller = UserController(service)

    try:
        return await user_controller.get_public_user_info_by_id(user_id)
    except HTTPException as e:
        raise e


@router.post("/new")
async def create_new_user(user: UserCreate, session: AsyncSession = Depends(get_session)):
    service = UserService(session)
    user_controller = UserController(service)
    print(user)
    try:
        return await user_controller.create_new_user(user)
    except HTTPException as e:
        raise e


@router.post("/verify-account")
async def verify_account(email, code, session: AsyncSession = Depends(get_session)):
    service = UserService(session)
    user_controller = UserController(service)
    try:
        print(f"Calling service.verify_user")
        return await user_controller.verify_user(email, code)
    except HTTPException as e:
        raise e


@router.put("/edit")
async def edit_user(user_update: UserUpdate, current_user: dict = Depends(get_current_user),
                    session: AsyncSession = Depends(get_session)):
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
async def delete_user(current_user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    service = UserService(session)
    user_controller = UserController(service)
    try:
        user_id: UUID = current_user["user_id"]
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing user ID")
        return await user_controller.delete_user(user_id)
    except HTTPException as e:
        raise e
