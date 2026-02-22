from datetime import datetime
from server.shared.pydantic import BaseModel
from pydantic import Field

class PClientNote(BaseModel):
    id: str
    client_id: str
    user_id: str
    content: str
    created_at: datetime
    updated_at: datetime


class CreateClientNoteRequest(BaseModel):
    content: str = Field(min_length=1)
