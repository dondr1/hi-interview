from pydantic import EmailStr

from server.shared.pydantic import BaseModel


class CreateClientRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str