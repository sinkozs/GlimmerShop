from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response, Request

from config.parser import load_config
from config.auth_config import http_only_auth_cookie
from controllers.auth_controller import AuthController
from pydantic import EmailStr
from services.auth_service import AuthService
from fastapi.security import OAuth2PasswordRequestForm
from dependencies import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_current_user
from jose import jwt, JWTError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/verify-pw")
def verify_password(password1, password2, session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    auth_controller = AuthController(service)
    try:
        return auth_controller.verify_password(password1, password2)
    except HTTPException as e:
        raise e


@router.post("/login")
async def login(
    is_seller: bool,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    service = AuthService(session)
    auth_controller = AuthController(service)
    try:
        return await auth_controller.login_for_access_token(
            is_seller, response, form_data
        )
    except HTTPException as e:
        raise e


@router.get("/test")
async def test_cookie_jwt(request: Request):
    token = request.cookies.get(http_only_auth_cookie)

    if not token:
        raise HTTPException(status_code=403, detail="No token found")

    try:
        auth_config = load_config().auth_config
        payload = jwt.decode(token, auth_config.secret_key, algorithms=["HS256"])
        return {"token_payload": payload}
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")


@router.get("/is-authenticated")
async def check_if_user_authenticated(current_user: dict = Depends(get_current_user)):
    return {"is_authenticated": True, "user_id": current_user["user_id"]}


@router.post("/logout")
async def user_logout(
    response: Response,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = AuthService(session)
    auth_controller = AuthController(service)

    if not current_user:
        raise HTTPException(status_code=403, detail="Not authenticated")

    try:
        response.delete_cookie(key=http_only_auth_cookie, httponly=True)

        user_id: UUID = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing user ID")

        await auth_controller.user_logout(user_id)

        return {"message": "Logout successful"}
    except HTTPException as e:
        raise e


@router.post("/forgotten-password")
async def regenerate_forgotten_password(
    email: EmailStr, session: AsyncSession = Depends(get_session)
):
    service = AuthService(session)
    auth_controller = AuthController(service)
    try:
        return await auth_controller.regenerate_forgotten_password(email)
    except HTTPException as e:
        raise e
