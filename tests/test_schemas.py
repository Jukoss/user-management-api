from user_management_api.schemas import UserCreate


def test_normalize_email():
    result = UserCreate(name="test", email="TEST@TEST.COM").email

    assert result == "test@test.com"