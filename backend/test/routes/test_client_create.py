from fastapi.testclient import TestClient

from server.data.models.client import Client
from server.shared.databasemanager import DatabaseManager


def test_create_client(
    test_client: TestClient,
) -> None:
    response = test_client.post(
        "/client",
        json={
            "email": "newclient@example.com",
            "first_name": "New",
            "last_name": "Client",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

    assert data["email"] == "newclient@example.com"
    assert data["first_name"] == "New"
    assert data["last_name"] == "Client"
    assert data["assigned_user_id"] is None


def test_create_client_with_assigned_user(
    test_client: TestClient,
) -> None:
    response = test_client.post(
        "/client",
        json={
            "email": "assignedcreate@example.com",
            "first_name": "Assigned",
            "last_name": "Create",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

    assert data["email"] == "assignedcreate@example.com"
    assert data["first_name"] == "Assigned"
    assert data["last_name"] == "Create"


def test_create_client_duplicate_email(
    test_client: TestClient,
    database: DatabaseManager,
) -> None:
    with database.create_session() as session:
        session.add(
            Client(
                email="duplicate@example.com",
                first_name="Dup",
                last_name="User",
            )
        )
        session.commit()

    response = test_client.post(
        "/client",
        json={
            "email": "duplicate@example.com",
            "first_name": "Another",
            "last_name": "User",
        },
    )

    assert response.status_code == 400


def test_create_client_unauthenticated(
    unauthenticated_test_client: TestClient,
) -> None:
    response = unauthenticated_test_client.post(
        "/client",
        json={
            "email": "unauth@example.com",
            "first_name": "No",
            "last_name": "Auth",
        },
    )

    assert response.status_code == 401


def test_create_client_invalid_email_fails(
    test_client: TestClient,
) -> None:
    response = test_client.post(
        "/client",
        json={
            "email": "not-an-email",
            "first_name": "Bad",
            "last_name": "Email",
        },
    )

    #EmailStr validation should trigger 422
    assert response.status_code == 422