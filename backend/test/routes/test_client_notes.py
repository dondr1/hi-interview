from fastapi.testclient import TestClient

from server.data.models.client import Client
from server.data.models.client_note import ClientNote
from server.shared.databasemanager import DatabaseManager


def test_list_client_notes(
    test_client: TestClient,
    database: DatabaseManager,
    user_id: str,
) -> None:
    with database.create_session() as session:
        client = Client(
            email="noteslist@example.com",
            first_name="Notes",
            last_name="List",
            assigned_user_id=user_id,
        )
        session.add(client)
        session.commit()

        session.add(
            ClientNote(
                client_id=client.id,
                user_id=user_id,
                content="First note",
            )
        )
        session.add(
            ClientNote(
                client_id=client.id,
                user_id=user_id,
                content="Second note",
            )
        )
        session.commit()

        client_id = client.id

    response = test_client.get(f"/client/{client_id}/notes")
    assert response.status_code == 200

    data = response.json()
    assert len(data["data"]) == 2
    
    for note in data["data"]:
        assert note["client_id"] == client_id
        assert note["user_id"] == user_id
        assert "id" in note
        
        assert "created_at" in note
        assert "updated_at" in note
        

    contents = [n["content"] for n in data["data"]]
    assert "First note" in contents
    assert "Second note" in contents


def test_list_client_notes_with_assigned_user(
    test_client: TestClient,
    database: DatabaseManager,
    user_id: str,
) -> None:
    with database.create_session() as session:
        client = Client(
            email="notesassigned@example.com",
            first_name="Notes",
            last_name="Assigned",
            assigned_user_id=user_id,
        )
        session.add(client)
        session.commit()

        session.add(
            ClientNote(
                client_id=client.id,
                user_id=user_id,
                content="Assigned user note",
            )
        )
        session.commit()

        client_id = client.id

    response = test_client.get(f"/client/{client_id}/notes")
    assert response.status_code == 200

    data = response.json()["data"]
    assert len(data) == 1
    
    assert "id" in data[0]
    assert "created_at" in data[0]
    assert "updated_at" in data[0]


    assert data[0]["user_id"] == user_id
    assert data[0]["content"] == "Assigned user note"


def test_list_client_notes_unauthenticated(
    unauthenticated_test_client: TestClient,
    database: DatabaseManager,
    user_id: str,
) -> None:
    with database.create_session() as session:
        client = Client(
            email="notesunauth@example.com",
            first_name="Notes",
            last_name="Unauth",
            assigned_user_id=user_id,
        )
        session.add(client)
        session.commit()

        client_id = client.id

    response = unauthenticated_test_client.get(
        f"/client/{client_id}/notes"
    )
    assert response.status_code == 401


def test_create_client_note(
    test_client: TestClient,
    database: DatabaseManager,
    user_id: str,
) -> None:
    with database.create_session() as session:
        client = Client(
            email="notescreate@example.com",
            first_name="Notes",
            last_name="Create",
            assigned_user_id=user_id,
        )
        session.add(client)
        session.commit()
        client_id = client.id

    response = test_client.post(
        f"/client/{client_id}/notes",
        json={"content": "Created note"},
    )

    assert response.status_code == 200

    data = response.json()
    
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


    assert data["client_id"] == client_id
    assert data["user_id"] == user_id
    assert data["content"] == "Created note"


def test_create_client_note_with_assigned_user(
    test_client: TestClient,
    database: DatabaseManager,
    user_id: str,
) -> None:
    with database.create_session() as session:
        client = Client(
            email="notescreateassigned@example.com",
            first_name="Notes",
            last_name="CreateAssigned",
            assigned_user_id=user_id,
        )
        session.add(client)
        session.commit()
        client_id = client.id

    response = test_client.post(
        f"/client/{client_id}/notes",
        json={"content": "Created by assigned user"},
    )

    assert response.status_code == 200

    data = response.json()
    
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

    assert data["client_id"] == client_id
    assert data["user_id"] == user_id
    assert data["content"] == "Created by assigned user"


def test_create_client_note_unauthenticated(
    unauthenticated_test_client: TestClient,
    database: DatabaseManager,
    user_id: str,
) -> None:
    with database.create_session() as session:
        client = Client(
            email="notescreateunauth@example.com",
            first_name="Notes",
            last_name="CreateUnauth",
            assigned_user_id=user_id,
        )
        session.add(client)
        session.commit()
        client_id = client.id

    response = unauthenticated_test_client.post(
        f"/client/{client_id}/notes",
        json={"content": "Should fail"},
    )

    assert response.status_code == 401


def test_list_client_notes_ordered_desc(
    test_client: TestClient,
    database: DatabaseManager,
    user_id: str,
) -> None:
    with database.create_session() as session:
        client = Client(
            email="notesorder@example.com",
            first_name="Notes",
            last_name="Order",
            assigned_user_id=user_id,
        )
        session.add(client)
        session.commit()

        note1 = ClientNote(
            client_id=client.id,
            user_id=user_id,
            content="Older note",
        )
        session.add(note1)
        session.commit()

        note2 = ClientNote(
            client_id=client.id,
            user_id=user_id,
            content="Newer note",
        )
        session.add(note2)
        session.commit()

        client_id = client.id

    response = test_client.get(f"/client/{client_id}/notes")
    assert response.status_code == 200

    data = response.json()["data"]
    assert len(data) == 2
    
    for note in data:
        assert "id" in note
        assert "created_at" in note
        assert "updated_at" in note

    assert data[0]["content"] == "Newer note"
    assert data[1]["content"] == "Older note"


def test_create_client_note_empty_content_fails(
    test_client: TestClient,
    database: DatabaseManager,
    user_id: str,
) -> None:
    with database.create_session() as session:
        client = Client(
            email="notesempty@example.com",
            first_name="Notes",
            last_name="Empty",
            assigned_user_id=user_id,
        )
        session.add(client)
        session.commit()
        client_id = client.id

    response = test_client.post(
        f"/client/{client_id}/notes",
        json={"content": ""},
    )

    assert response.status_code == 422
