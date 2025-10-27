from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from typing_extensions import Annotated


class UserCreate(BaseModel):
    first_name: Annotated[
        str,
        Field(
            strip_whitespace=True,
            max_length=25,
            min_length=2,
            pattern=r"^[a-zA-ZáÁéÉíÍóÓöÖüÜőŐúÚ-]+$",
        ),
    ]
    last_name: Annotated[
        str,
        Field(
            strip_whitespace=True,
            max_length=25,
            min_length=2,
            pattern=r"^[a-zA-ZáÁéÉíÍóÓöÖüÜőŐúÚ-]+$",
        ),
    ]
    email: EmailStr
    password: Annotated[str, Field(strip_whitespace=True, max_length=128, min_length=8)]
    is_seller: bool

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    first_name: Optional[
        Annotated[
            str,
            Field(
                strip_whitespace=True,
                max_length=25,
                min_length=2,
                pattern=r"^[a-zA-ZáÁéÉíÍóÓöÖüÜőŐúÚ-]+(?: [a-zA-ZáÁéÉíÍóÓöÖüÜőŐúÚ-]+)*$",
            ),
        ]
    ] = None
    last_name: Optional[
        Annotated[
            str,
            Field(
                strip_whitespace=True,
                max_length=25,
                min_length=2,
                pattern=r"^[a-zA-ZáÁéÉíÍóÓöÖüÜőŐúÚ-]+(?: [a-zA-ZáÁéÉíÍóÓöÖüÜőŐúÚ-]+)*$",
            ),
        ]
    ] = None
    email: Optional[EmailStr] = None
    password: Optional[
        Annotated[
            str,
            Field(
                strip_whitespace=True,
                max_length=128,
                min_length=8,
            ),
        ]
    ] = None


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
    id: Optional[int] = None
    name: Annotated[str, Field(max_length=100)]
    description: Annotated[str, Field(max_length=150000)]
    price: Annotated[int, Field(gt=0)]
    stock_quantity: Annotated[int, Field(ge=0)]
    material: str
    color: str
    categories: Optional[List[int]] = None
    image_path: Optional[str] = None
    image_path2: Optional[str] = None

    class Config:
        from_attributes = True


class UserVerification(BaseModel):
    email: EmailStr
    code: str


class CategoryQuery(BaseModel):
    id: int
    category_name: str = Field(max_length=200)

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class CategoryIdentifiers(BaseModel):
    category_id: Optional[int] = None
    category_name: Optional[str] = None

    # @field_validator('*', mode='after')
    # @classmethod
    # def validate_at_least_one_field(cls, _, info):
    #     values = info.data
    #     if values.get('category_id') is None and values.get('category_name') is None:
    #         raise ValueError("At least one of category_id or category_name must be provided")
    #     return _


class CategoryToProductRequest(BaseModel):
    product_id: int
    category_id: int


class CartItemForCheckout(BaseModel):
    id: int
    name: str
    price: int
    category: List[int]
    quantity: int
    image_path: str


class CategoryUpdate(BaseModel):
    category_name: Optional[Annotated[str, Field(max_length=200)]] = None


class PriceFilter(BaseModel):
    min_price: Annotated[int, Field(ge=0)] = 0
    max_price: Annotated[int, Field(ge=0, le=1000000)] = 1000000


class MaterialsFilter(BaseModel):
    materials: List[str]


class SellerFilter(BaseModel):
    seller_id: Optional[UUID] = None


class ProductFilterRequest(BaseModel):
    category_id: int
    materials: MaterialsFilter
    price_range: PriceFilter
    seller: SellerFilter


class SelectedMonthForSellerStatistics(BaseModel):
    year: str
    month: str


class OrderData(BaseModel):
    product_id: int
    price: float
    quantity: int


class GuestUserInfo(BaseModel):
    user_id: Optional[UUID] = None
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    shipping_address: str
