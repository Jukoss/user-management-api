from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from user_management_api.database import SessionDep
from user_management_api.repository import (
    create_new_user,
    get_all_users,
    get_user_by_id,
    update_user_by_id,
)
from user_management_api.schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
def get_users(session: SessionDep) -> list[UserRead]:
    return get_all_users(session)


@router.get("/{user_id}")
def get_user(user_id: int, session: SessionDep) -> UserRead:
    user = get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, session: SessionDep) -> UserRead:
    try:
        user = create_new_user(session, user_data)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    return user


@router.put("/{user_id}")
def update_user(user_id: int, user_data: UserCreate, session: SessionDep) -> UserRead:
    user = get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    try:
        user = update_user_by_id(session, user, user_data)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    return user