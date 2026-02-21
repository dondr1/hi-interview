from fastapi.testclient import TestClient

from server.data.models.client import Client
from server.shared.databasemanager import DatabaseManager


def test_get_client_detail(
    test_client: TestClient,
    database: DatabaseManager,
) -> None:
    with database.create_session() as session:
        client = Client(
            email="detail@example.com",
            first_name="Detail",
            last_name="Client",
        )
        session.add(client)
        session.commit()
        client_id = client.id

    response = test_client.get(f"/client/{client_id}")
    assert response.status_code == 200

    data = response.json()
    # Important fields
    assert data["id"] == client_id
    assert data["email"] == "detail@example.com"
    assert data["first_name"] == "Detail"
    assert data["last_name"] == "Client"

    # API Contract validation
    assert data["assigned_user_id"] is None
    assert "created_at" in data
    assert "updated_at" in data


def test_get_client_detail_unauthenticated(
    unauthenticated_test_client: TestClient,
    database: DatabaseManager,
) -> None:
    with database.create_session() as session:
        client = Client(
            email="unauthdetail@example.com",
            first_name="Unauth",
            last_name="Detail",
        )
        session.add(client)
        session.commit()
        client_id = client.id

    response = unauthenticated_test_client.get(f"/client/{client_id}")
    assert response.status_code == 401


def test_get_client_detail_not_found(
    test_client: TestClient,
) -> None:
    response = test_client.get("/client/does-not-exist")
    assert response.status_code == 404


def test_get_client_detail_with_assigned_user(
    test_client: TestClient,
    database: DatabaseManager,
    user_id: str,
) -> None:
    with database.create_session() as session:
        client = Client(
            email="assigneddetail@example.com",
            first_name="Assigned",
            last_name="Detail",
            assigned_user_id=user_id,
        )
        session.add(client)
        session.commit()
        client_id = client.id

    response = test_client.get(f"/client/{client_id}")
    assert response.status_code == 200

    data = response.json()

    assert data["assigned_user_id"] == user_id
    assert data["email"] == "assigneddetail@example.com"
    assert "created_at" in data
    assert "updated_at" in data
