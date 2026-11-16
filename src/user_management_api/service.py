from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from user_management_api import repository
from user_management_api.models import User
from user_management_api.schemas import UserCreate


class UserNotFoundError(Exception):
    pass


class EmailAlreadyExistsError(Exception):
    pass


def list_users(session: Session) -> list[User]:
    return repository.list_users(session)


def get_user(session: Session, user_id: int) -> User:
    user = repository.get_user_by_id(session, user_id)
    if user is None:
        raise UserNotFoundError()
    return user


def create_user(session: Session, user_data: UserCreate) -> User:
    try:
        user = repository.create_new_user(session, user_data)
    except IntegrityError as e:
        session.rollback()
        raise EmailAlreadyExistsError() from e
    return user


def update_user(session: Session, user_id: int, user_data: UserCreate) -> User:
    user = get_user(session, user_id)
    try:
        user = repository.update_user_by_id(session, user, user_data)
    except IntegrityError as e:
        session.rollback()
        raise EmailAlreadyExistsError() from e
    return user


def delete_user(session: Session, user_id: int) -> None:
    user = get_user(session, user_id)
    repository.delete_user_by_id(session, user)
