from sqlalchemy.orm import Session

from server.business.client_note.schema import PClientNote
from server.data.models.client_note import ClientNote


def create_client_note(
    session: Session,
    client_id: str,
    user_id: str,
    content: str,
) -> PClientNote:
    note = ClientNote(
        client_id=client_id,
        user_id=user_id,
        content=content,
    )
    session.add(note)
    session.commit()
    session.refresh(note)
    return PClientNote.model_validate(note)
