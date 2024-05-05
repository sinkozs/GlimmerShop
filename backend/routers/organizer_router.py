from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_session
from controllers.organizer_controller import OrganizerController
from services.organizer_service import OrganizerService
from schemas.schemas import UserCreate, UserUpdate

from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/organizers",
    tags=["organizers"],
    responses={404: {"Organizer": "Not found"}}
)


@router.get("")
async def get_all_organizer(session: AsyncSession = Depends(get_session)):
    service = OrganizerService(session)
    organizer_controller = OrganizerController(service)
    try:
        return await organizer_controller.get_all_organizers()
    except HTTPException as e:
        raise e


@router.get("/{organizer_id}")
async def get_organizer_by_id(organizer_id, session: AsyncSession = Depends(get_session)):
    service = OrganizerService(session)
    organizer_controller = OrganizerController(service)

    try:
        return await organizer_controller.get_organizer_by_id(organizer_id)
    except HTTPException as e:
        raise e


@router.post("/new")
async def create_new_organizer(organizer: UserCreate, session: AsyncSession = Depends(get_session)):
    service = OrganizerService(session)
    organizer_controller = OrganizerController(service)
    try:
        return await organizer_controller.create_new_organizer(organizer)
    except HTTPException as e:
        raise e


@router.put("/edit")
async def edit_organizer(organizer_id: UUID, organizer: UserUpdate, session: AsyncSession = Depends(get_session)):
    service = OrganizerService(session)
    organizer_controller = OrganizerController(service)
    try:
        return await organizer_controller.edit_organizer(organizer_id, organizer)
    except HTTPException as e:
        raise e


@router.delete("/delete/{organizer_id}")
async def delete_organizer(organizer_id, session: AsyncSession = Depends(get_session)):
    service = OrganizerService(session)
    organizer_controller = OrganizerController(service)
    try:
        return await organizer_controller.delete_organizer(organizer_id)
    except HTTPException as e:
        raise e
