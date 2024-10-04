from datetime import datetime, date
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field
from typing_extensions import Annotated


class UserCreate(BaseModel):
    first_name: Annotated[
        str, Field(strip_whitespace=True, max_length=25, min_length=2, pattern=r'^[a-zA-ZáÁéÉíÍóÓöÖüÜőŐúÚ-]+$')]
    last_name: Annotated[
        str, Field(strip_whitespace=True, max_length=25, min_length=2, pattern=r'^[a-zA-ZáÁéÉíÍóÓöÖüÜőŐúÚ-]+$')]
    password: Annotated[str, Field(strip_whitespace=True, max_length=64, min_length=8)]
    email: EmailStr
    is_seller: bool
    password_length: Optional[int] = None


class UserUpdate(BaseModel):
    first_name: Optional[Annotated[
        str, Field(strip_whitespace=True, max_length=25, min_length=2,
                   pattern=r"^[a-zA-ZáÁéÉíÍóÓöÖüÜőŐúÚ-]+(?: [a-zA-ZáÁéÉíÍóÓöÖüÜőŐúÚ-]+)*$")]] = None
    last_name: Optional[Annotated[
        str, Field(strip_whitespace=True, max_length=25, min_length=2,
                   pattern=r"^[a-zA-ZáÁéÉíÍóÓöÖüÜőŐúÚ-]+(?: [a-zA-ZáÁéÉíÍóÓöÖüÜőŐúÚ-]+)*$")]] = None
    email: Optional[EmailStr] = None
    password: Optional[Annotated[str, Field(
        strip_whitespace=True,
        max_length=64,
        min_length=8,
    )]] = None
    password_length: Optional[int] = None


class ProductCreate(BaseModel):
    name: Annotated[str, Field(max_length=100)]
    description: Annotated[str, Field(max_length=150000)]
    price: Annotated[int, Field(gt=0)]
    stock_quantity: Annotated[int, Field(ge=0)]
    material: str
    color: str
    image_path: Optional[str] = None
    image_path2: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[Annotated[str, Field(max_length=100)]] = None
    description: Optional[Annotated[str, Field(max_length=150000)]] = None
    price: Optional[Annotated[int, Field(gt=0)]] = None
    stock_quantity: Optional[Annotated[int, Field(ge=0)]] = None
    material: Optional[str] = None
    color: Optional[str] = None
    image_path: Optional[str] = None
    image_path2: Optional[str] = None


class ProductData(BaseModel):
    id: int
    name: Annotated[str, Field(max_length=100)]
    description: Annotated[str, Field(max_length=150000)]
    price: Annotated[int, Field(gt=0)]
    stock_quantity: Annotated[int, Field(ge=0)]
    material: str
    color: str
    image_path: Optional[str] = None
    image_path2: Optional[str] = None

    class Config:
        from_attributes = True


class UserQuery(BaseModel):
    id: UUID
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: str = Field(max_length=100)
    is_seller: bool
    is_verified: bool
    is_active: bool
    last_login: Optional[datetime]
    registration_date: datetime.date

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class CartItemUpdate(BaseModel):
    product_id: int
    quantity: Annotated[int, Field(ge=0)]


class CartItemForCheckout(BaseModel):
    id: int
    name: str
    price: int
    quantity: int
    image_path: str


class CategoryUpdate(BaseModel):
    category_name: Optional[Annotated[str, Field(max_length=200)]] = None
    category_description: Optional[Annotated[str, Field(max_length=200)]] = None


class PriceFilter(BaseModel):
    min_price: Annotated[int, Field(ge=0)] = 0
    max_price: Annotated[int, Field(ge=0, le=1000000)] = 1000000


class MaterialsFilter(BaseModel):
    materials: List[str]


class MonthRequestForSellerStatistics(BaseModel):
    # format: "YYYY-MM"
    month: str
