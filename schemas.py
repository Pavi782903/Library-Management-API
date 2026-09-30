from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============================================================
# BOOK SCHEMAS
# ============================================================

class BookBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Book name",
    )

    author: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Book author",
    )

    category: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Book category",
    )

    isbn: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique ISBN",
    )

    price: float = Field(
        ...,
        gt=0,
        description="Price must be greater than 0",
    )

    available_quantity: int = Field(
        ...,
        ge=0,
        description="Quantity must be greater than or equal to 0",
    )


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    author: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    category: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    isbn: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    price: float | None = Field(
        default=None,
        gt=0,
    )

    available_quantity: int | None = Field(
        default=None,
        ge=0,
    )


class BookResponse(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# ============================================================
# MEMBER SCHEMAS
# ============================================================

class MemberBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Member name",
    )

    email: EmailStr = Field(
        ...,
        description="Unique member email",
    )

    phone: str | None = Field(
        default=None,
        max_length=30,
        description="Phone number",
    )

    membership_type: str = Field(
        default="Standard",
        min_length=1,
        max_length=50,
        description="Membership type",
    )


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        max_length=30,
    )

    membership_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )


class MemberResponse(MemberBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# ============================================================
# BORROW / RETURN RESPONSE
# ============================================================

class BorrowResponse(BaseModel):
    message: str
    member_id: int
    book_id: int
    book_name: str
    available_quantity: int
    borrowed_at: datetime


class ReturnResponse(BaseModel):
    message: str
    member_id: int
    book_id: int
    book_name: str
    available_quantity: int
    returned_at: datetime