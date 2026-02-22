from fastapi import APIRouter

from server.business.auth.auth_verifier import AuthVerifier
from server.business.auth.schema import UserTokenInfo
from server.business.client.get import get_client
from server.business.client.list import list_clients
from server.business.client.schema import PClient
from server.business.client_note.create import create_client_note
from server.business.client_note.list import list_client_notes
from server.business.client_note.schema import CreateClientNoteRequest, PClientNote

from server.business.client.create import create_client
from server.business.client.create_schema import CreateClientRequest

from server.shared.databasemanager import DatabaseManager
from server.shared.pydantic import PList


def get_router(database: DatabaseManager, auth_verifier: AuthVerifier) -> APIRouter:
    router = APIRouter()

    @router.get("/client", response_model=PList[PClient])
    async def list_clients_route(
        _: UserTokenInfo = auth_verifier.UserTokenInfo(),
    ) -> PList[PClient]:
        with database.create_session() as session:
            clients = list_clients(session)
            return PList(data=clients)
    
    
    @router.post("/client", response_model=PClient)
    async def create_client_route(
        request: CreateClientRequest,
        _: UserTokenInfo = auth_verifier.UserTokenInfo(),
    ) -> PClient:
        with database.create_session() as session:
            return create_client(
                session=session,
                email=request.email,
                first_name=request.first_name,
                last_name=request.last_name,
            )

    @router.get("/client/{client_id}", response_model=PClient)
    async def get_client_route(
        client_id: str,
        _: UserTokenInfo = auth_verifier.UserTokenInfo(),
    ) -> PClient:
        with database.create_session() as session:
            return get_client(session, client_id)

    @router.get("/client/{client_id}/notes", response_model=PList[PClientNote])
    async def list_notes_route(
        client_id: str,
        _: UserTokenInfo = auth_verifier.UserTokenInfo(),
    ) -> PList[PClientNote]:
        with database.create_session() as session:
            notes = list_client_notes(session, client_id)
            return PList(data=notes)

    @router.post("/client/{client_id}/notes", response_model=PClientNote)
    async def create_note_route(
        client_id: str,
        request: CreateClientNoteRequest,
        user: UserTokenInfo = auth_verifier.UserTokenInfo(),
    ) -> PClientNote:
        with database.create_session() as session:
            return create_client_note(
                session=session,
                client_id=client_id,
                user_id=user.user_id,
                content=request.content,
            )

    return router
