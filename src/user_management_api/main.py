from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from user_management_api.database import engine
from user_management_api.models import User

app = FastAPI()


class UserCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower()


class UserRead(UserCreate):
    id: int


@app.get("/users")
def get_users() -> list[UserRead]:
    with Session(engine) as session:
        users = session.scalars(select(User)).all()
        return users


@app.get("/users/{user_id}")
def get_user(user_id: int) -> UserRead:
    with Session(engine) as session:
        user = session.get(User, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user


@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate) -> UserRead:
    with Session(engine) as session:
        user = User(**user_data.model_dump())
        session.add(user)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        session.refresh(user)
        return user


@app.put("/users/{user_id}")
def update_user(user_id: int, user_data: UserCreate) -> UserRead:
    with Session(engine) as session:
        user = session.get(User, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        for key, value in user_data.model_dump().items():
            setattr(user, key, value)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        session.refresh(user)
        return user


