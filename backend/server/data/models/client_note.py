import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from server.data.models.base import Base


class ClientNote(Base):
    __tablename__ = "client_note"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )

    client_id: Mapped[str] = mapped_column(
        String, ForeignKey("client.id"), nullable=False
    )

    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("user.id"), nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    client = relationship("Client")
    user = relationship("User")