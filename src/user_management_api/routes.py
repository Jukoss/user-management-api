from fastapi import APIRouter, HTTPException, status

from user_management_api import service
from user_management_api.database import SessionDep
from user_management_api.schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
def get_users(session: SessionDep) -> list[UserRead]:
    return service.list_users(session)


@router.get("/{user_id}")
def get_user(user_id: int, session: SessionDep) -> UserRead:
    try:
        return service.get_user(session, user_id)
    except service.UserNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, session: SessionDep) -> UserRead:
    try:
        return service.create_user(session, user_data)
    except service.EmailAlreadyExistsError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")


@router.put("/{user_id}")
def update_user(user_id: int, user_data: UserCreate, session: SessionDep) -> UserRead:
    try:
        return service.update_user(session, user_id, user_data)
    except service.UserNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    except service.EmailAlreadyExistsError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, session: SessionDep) -> None:
    try:
        service.delete_user(session, user_id)
    except service.UserNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
