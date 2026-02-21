from fastapi import HTTPException
from sqlalchemy.orm import Session

from server.data.models.client import Client
from server.business.client.schema import PClient


def get_client(session: Session, client_id: str) -> PClient:
    client = session.get(Client, client_id)
    
    #Error Handling if client not found
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    return PClient.model_validate(client)
