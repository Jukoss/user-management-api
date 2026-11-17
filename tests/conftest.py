import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from user_management_api.database import get_session
from user_management_api.main import app
from user_management_api.models import Base

TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]

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
