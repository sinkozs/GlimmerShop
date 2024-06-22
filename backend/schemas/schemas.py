from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from typing_extensions import Annotated


class UserCreate(BaseModel):
    first_name: Annotated[str, Field(strip_whitespace=True, max_length=25, min_length=3, pattern=r'^[a-zA-ZáÁéÉíÍóÓöÖüÜőŐúÚ-]+$')]
    last_name: Annotated[str, Field(strip_whitespace=True, max_length=25, min_length=3, pattern=r'^[a-zA-ZáÁéÉíÍóÓöÖüÜőŐúÚ-]+$')]
    password: Annotated[str, Field(strip_whitespace=True, max_length=64, min_length=8)]
    email: EmailStr
    is_seller: bool


class UserUpdate(BaseModel):
    first_name: Optional[Annotated[str, Field(strip_whitespace=True, max_length=25, min_length=3, pattern=r'^[a-zA-ZáÁéÉíÍóÓöÖüÜőŐúÚ-]+$')]] = None
    last_name: Optional[Annotated[str, Field(strip_whitespace=True, max_length=25, min_length=3, pattern=r'^[a-zA-ZáÁéÉíÍóÓöÖüÜőŐúÚ-]+$')]] = None
    email: Optional[EmailStr] = None
    password: Optional[Annotated[str, Field(strip_whitespace=True, max_length=64, min_length=8)]] = None


class ProductCreate(BaseModel):
    name: Annotated[str, Field(max_length=100)]
    description: Annotated[str, Field(max_length=150000)]
    price: Annotated[int, Field(gt=0)]
    stock_quantity: Annotated[int, Field(ge=0)]
    material: str
    color: str
    image_path: str
    image_path2: str


class ProductUpdate(BaseModel):
    name: Optional[Annotated[str, Field(max_length=100)]] = None
    description: Optional[Annotated[str, Field(max_length=150000)]] = None
    price: Optional[Annotated[int, Field(gt=0)]] = None
    stock_quantity: Optional[Annotated[int, Field(ge=0)]] = None
    material: Optional[str] = None
    color: Optional[str] = None
    image_path: Optional[str] = None
    image_path2: Optional[str] = None


class CartItemUpdate(BaseModel):
    product_id: int
    quantity: Annotated[int, Field(ge=0)]
