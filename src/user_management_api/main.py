from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, ConfigDict

app = FastAPI()

users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
]


class UserCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr


@app.get("/users")
def get_users():
    return users


@app.get("/users/{user_id}")
def get_user(user_id: int):
    for user in users:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate):
    user = {
        "id": max((u["id"] for u in users), default=0) + 1,
        **user_data.model_dump(),
    }
    users.append(user)
    return user


@app.put("/users/{user_id}")
def update_user(user_id: int, user_data: UserCreate):
    for user in users:
        if user["id"] == user_id:
            user.update(user_data.model_dump())
            return user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


