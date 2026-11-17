def create_user(client, name="test", email="test@test.com"):
    response = client.post("/users", json={"name": name, "email": email})
    assert response.status_code == 201
    assert "id" in response.json()
    return response.json()


def test_get_empty_list(client):
    response = client.get("/users")

    assert response.status_code == 200
    assert response.json() == []


def test_create_user(client):
    response = client.post("/users", json={"name": "test", "email": "test@test.com"})

    assert response.status_code == 201
    assert "id" in response.json()


def test_get_user_by_id(client):
    user = create_user(client)

    get_response = client.get(f"/users/{user['id']}")

    assert get_response.status_code == 200
    assert get_response.json()["id"] == user["id"]
    assert get_response.json()["name"] == user["name"]
    assert get_response.json()["email"] == user["email"]


def test_get_user_by_id_not_found(client):
    get_response = client.get("/users/999")

    assert get_response.status_code == 404


def test_create_user_invalid_email(client):
    response = client.post("/users", json={"name": "test", "email": "invalid_email"})

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "email"]


def test_create_user_email_already_exist(client):
    user = create_user(client)
    response_email_already_exist = client.post(
        "/users", json={"name": "test", "email": user["email"].upper()}
    )

    assert response_email_already_exist.status_code == 409


def test_update_user(client):
    user = create_user(client)

    response = client.put(
        f"/users/{user['id']}", json={"name": "test_update", "email": "test@test.com"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "test_update"


def test_update_not_found_user(client):
    response = client.put(
        "/users/999", json={"name": "test_update", "email": "test@test.com"}
    )
    assert response.status_code == 404


def test_update_wrong_user_email(client):
    first_user = create_user(client)
    second_user = create_user(client, email="test2@test.com")
    response = client.put(
        f"/users/{first_user['id']}",
        json={"name": first_user["name"], "email": second_user["email"]},
    )
    assert response.status_code == 409


def test_delete_user(client):
    user = create_user(client)
    delete_response = client.delete(f"/users/{user['id']}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/users/{user['id']}")

    assert get_response.status_code == 404
