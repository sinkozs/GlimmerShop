from typing import Optional
from dataclasses import dataclass
from pydantic import BaseModel, EmailStr, StringConstraints
from typing_extensions import Annotated


class UserCreate(BaseModel):
    first_name: Annotated[str, StringConstraints(strip_whitespace=True, max_length=25, min_length=3, pattern=r'^[a-zA-ZáÁéÉíÍóÓöÖüÜőŐúÚ-]+$', strict=True)]
    last_name: Annotated[str, StringConstraints(strip_whitespace=True, max_length=25, min_length=3, pattern=r'^[a-zA-ZáÁéÉíÍóÓöÖüÜőŐúÚ-]+$', strict=True)]
    password: Annotated[str, StringConstraints(strip_whitespace=True, max_length=64, min_length=8, strict=True)]
    email: EmailStr
    is_seller: bool


class ProductCreate(BaseModel):
    name: Annotated[str, StringConstraints(max_length=100, strict=True)]
    description: Annotated[str, StringConstraints(max_length=150000, strict=True)]
    price: int
    stock_quantity: int
    material: str
    color: str
    image_path: str
    image_path2: Optional[str]

@dataclass
class UserUpdate:
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    def is_valid_update(self, field_value, original_value):
        return field_value is not None and field_value != '' and field_value != original_value
