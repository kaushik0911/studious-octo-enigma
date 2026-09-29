from datetime import datetime

from pydantic import BaseModel, EmailStr


# --- User Schemas ---
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class UserRead(UserCreate):
    id: int


# --- Lookup Schemas ---
class NamedEntityCreate(BaseModel):
    name: str


class NamedEntityRead(NamedEntityCreate):
    id: int


# --- Item Schemas ---
class ItemCreate(BaseModel):
    pmd_number: str
    item_code: str
    title: str
    sender_id: int
    location_id: int
    released_to: int
    approved_by: int
    type_id: int
    author_id: int
    remarks: str | None = ""
    quick_insights: str | None = ""


class ItemRead(ItemCreate):
    id: int
    received_at: datetime
    acknowledgement_sent: datetime
    released_at: datetime


class ItemReadWithDetails(ItemRead):
    languages: list[NamedEntityRead] = []
    categories: list[NamedEntityRead] = []


class ItemUpdate(BaseModel):
    title: str | None = None
    remarks: str | None = None
    quick_insights: str | None = None
    location_id: int | None = None


class M2MAssignment(BaseModel):
    target_id: int  # language_id or category_id
