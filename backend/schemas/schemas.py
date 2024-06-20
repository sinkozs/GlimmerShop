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


@dataclass
class UserUpdate:
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class ProductCreate(BaseModel):
    name: Annotated[str, StringConstraints(max_length=100, strict=True)]
    description: Annotated[str, StringConstraints(max_length=150000, strict=True)]
    price: int
    stock_quantity: int
    material: str
    color: str
    image_path: str
    image_path2: str


@dataclass
class ProductUpdate:
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    stock_quantity: Optional[int] = None
    material: Optional[str] = None
    color: Optional[str] = None
    image_path: Optional[str] = None
    image_path2: Optional[str] = None
