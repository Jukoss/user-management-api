def test_create_user(client):
    response = client.post("/users", json={"name": "test", "email": "test@test.com"})

    assert response.status_code == 201
    assert "id" in response.json()


def test_create_user_invalid_email(client):
    response = client.post("/users", json={"name": "test", "email": "invalid_email"})

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "email"]
