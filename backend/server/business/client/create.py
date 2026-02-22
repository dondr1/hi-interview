from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from server.business.client.schema import PClient
from server.data.models.client import Client


def create_client(
    session: Session,
    email: str,
    first_name: str,
    last_name: str,
) -> PClient:
    normalized_email = email.lower().strip()

    existing = (
        session.execute(select(Client).where(Client.email == normalized_email))
        .scalars()
        .one_or_none()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client with this email already exists",
        )

    client = Client(
        email=normalized_email,
        first_name=first_name.strip(),
        last_name=last_name.strip(),
    )

    session.add(client)
    session.commit()
    session.refresh(client)

    return PClient.model_validate(client)