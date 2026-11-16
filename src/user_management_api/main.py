from fastapi import FastAPI

from user_management_api.routes import router

app = FastAPI()

app.include_router(router)
