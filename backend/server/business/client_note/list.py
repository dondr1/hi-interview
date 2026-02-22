from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from server.business.client_note.schema import PClientNote
from server.data.models.client_note import ClientNote


def list_client_notes(session: Session, client_id: str) -> list[PClientNote]:
    notes = (
        session.execute(
            select(ClientNote)
            .where(ClientNote.client_id == client_id)
            .order_by(desc(ClientNote.created_at))
        )
        .scalars()
        .all()
    )
    return [PClientNote.model_validate(note) for note in notes]
