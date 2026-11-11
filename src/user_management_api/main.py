from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import select

from user_management_api.database import engine
from user_management_api.models import User

app = FastAPI()

users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
]


class UserCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr


class UserRead(UserCreate):
    id: int


@app.get("/users")
def get_users() -> list[UserRead]:
    with Session(engine) as session:
        users = session.scalars(select(User)).all()
        return users


@app.get("/users/{user_id}")
def get_user(user_id: int) -> UserRead:
    for user in users:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate) -> UserRead:
    with Session(engine) as session:
        user = User(**user_data.model_dump())
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@app.put("/users/{user_id}")
def update_user(user_id: int, user_data: UserCreate) -> UserRead:
    for user in users:
        if user["id"] == user_id:
            user.update(user_data.model_dump())
            return user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


