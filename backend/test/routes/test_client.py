
from fastapi.testclient import TestClient
from sqlalchemy import text

from server.data.models.client import Client
from server.shared.databasemanager import DatabaseManager


def test_list_clients(test_client: TestClient, database: DatabaseManager) -> None:
    with database.create_session() as session:
        session.add(Client(email="alice@example.com", first_name="Alice", last_name="Smith"))
        session.add(Client(email="bob@example.com", first_name="Bob", last_name="Jones"))
        session.commit()

    response = test_client.get("/client")
    assert response.status_code == 200

    data = response.json()
    assert len(data["data"]) >= 2

    emails = [c["email"] for c in data["data"]]
    assert "alice@example.com" in emails
    assert "bob@example.com" in emails


def test_list_clients_unauthenticated(unauthenticated_test_client: TestClient) -> None:
    response = unauthenticated_test_client.get("/client")
    assert response.status_code == 401


def test_list_clients_with_assigned_user(
    test_client: TestClient, database: DatabaseManager, user_id: str
) -> None:
    with database.create_session() as session:
        session.add(
            Client(
                email="assigned@example.com",
                first_name="Charlie",
                last_name="Brown",
                assigned_user_id=user_id,
            )
        )
        session.commit()

    response = test_client.get("/client")
    assert response.status_code == 200

    data = response.json()
    assigned = [c for c in data["data"] if c["email"] == "assigned@example.com"]
    assert len(assigned) == 1
    assert assigned[0]["assigned_user_id"] == user_id


def test_list_clients_orders_newest_first(
    test_client: TestClient,
    database: DatabaseManager,
) -> None:
    with database.create_session() as session:
        old_client = Client(
            email="older@example.com",
            first_name="Old",
            last_name="Client",
        )
        new_client = Client(
            email="newer@example.com",
            first_name="New",
            last_name="Client",
        )
        session.add(old_client)
        session.add(new_client)
        session.commit()

        # Force deterministic timestamps for ordering assertion.
        session.execute(
            text(
                """
                UPDATE client
                SET created_at = now() - interval '1 day'
                WHERE id = :id
                """
            ),
            {"id": old_client.id},
        )
        session.execute(
            text(
                """
                UPDATE client
                SET created_at = now()
                WHERE id = :id
                """
            ),
            {"id": new_client.id},
        )
        session.commit()

    response = test_client.get("/client")
    assert response.status_code == 200

    data = response.json()["data"]
    older_index = next(i for i, c in enumerate(data) if c["email"] == "older@example.com")
    newer_index = next(i for i, c in enumerate(data) if c["email"] == "newer@example.com")

    assert newer_index < older_index
