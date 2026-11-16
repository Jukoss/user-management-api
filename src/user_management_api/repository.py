from sqlalchemy import select
from sqlalchemy.orm import Session

from user_management_api.models import User
from user_management_api.schemas import UserCreate


def list_users(session: Session) -> list[User]:
    return session.scalars(select(User)).all()


def get_user_by_id(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)


def create_new_user(session: Session, user_data: UserCreate) -> User:
    user = User(**user_data.model_dump())
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_user_by_id(session: Session, user: User, user_data: UserCreate) -> User:
    for key, value in user_data.model_dump().items():
        setattr(user, key, value)
    session.commit()
    session.refresh(user)
    return user


def delete_user_by_id(session: Session, user: User) -> None:
    session.delete(user)
    session.commit()
