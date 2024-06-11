from fastapi import APIRouter, Depends, HTTPException
from controllers.auth_controller import AuthController
from services.auth_service import AuthService
from fastapi.security import OAuth2PasswordRequestForm
from dependencies import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from services.user_service import UserService
from dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/verify-pw")
def verify_password(password1, password2,
                session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    auth_controller = AuthController(service)
    try:
        return auth_controller.verify_password(password1, password2)
    except HTTPException as e:
        raise e


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                session: AsyncSession = Depends(get_session)):
    # user_service = UserService(session)
    # organizer_service = OrganizerService(session)
    service = AuthService(session)
    auth_controller = AuthController(service)
    try:
        return await auth_controller.login_for_access_token(form_data)
    except HTTPException as e:
        raise e


@router.post("/logout")
async def user_logout(user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    auth_controller = AuthController(service)
    return await auth_controller.user_logout(user)
