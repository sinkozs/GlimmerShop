from typing import Optional

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    is_seller: bool
    is_verified: bool
    is_active: bool
    last_login: Optional[str] = None

    class Config:
        from_attributes = True
