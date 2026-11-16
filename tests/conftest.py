import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from user_management_api.database import get_session
from user_management_api.main import app
from user_management_api.models import Base

TEST_DATABASE_URL = "postgresql+psycopg://app:app@localhost:5432/users_test"

test_engine = create_engine(TEST_DATABASE_URL)


def get_test_session():
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def client():
    Base.metadata.create_all(test_engine)
    app.dependency_overrides[get_session] = get_test_session

    yield TestClient(app)

    app.dependency_overrides.clear()
    Base.metadata.drop_all(test_engine)
