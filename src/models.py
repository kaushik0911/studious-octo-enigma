from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlmodel import Column, Field, Relationship, SQLModel

from database import engine


class Location(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    items: list["Item"] = Relationship(
        back_populates="location",
        sa_relationship_kwargs={"foreign_keys": "Item.location_id"},
    )

    def __str__(self):
        return self.name


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    email: str = Field(unique=True)

    sent_items: list["Item"] = Relationship(
        back_populates="sender",
        sa_relationship_kwargs={"foreign_keys": "Item.sender_id"},
    )

    approved_items: list["Item"] = Relationship(
        back_populates="approved_by",
        sa_relationship_kwargs={"foreign_keys": "Item.approved_by_id"},
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Author(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    email: str = Field(unique=True, nullable=True)

    items: list["Item"] = Relationship(
        back_populates="author",
        sa_relationship_kwargs={"foreign_keys": "Item.author_id"},
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class ItemType(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    type: str

    items: list["Item"] = Relationship(
        back_populates="item_type",
        sa_relationship_kwargs={"foreign_keys": "Item.type_id"},
    )

    def __str__(self):
        return self.type


# --- Link Models (Defined before parent models that use them in link_model) ---


class LanguageItem(SQLModel, table=True):
    language_id: int | None = Field(
        default=None, foreign_key="language.id", primary_key=True
    )
    item_id: int | None = Field(default=None, foreign_key="item.id", primary_key=True)


class CategoryItem(SQLModel, table=True):
    category_id: int | None = Field(
        default=None, foreign_key="category.id", primary_key=True
    )
    item_id: int | None = Field(default=None, foreign_key="item.id", primary_key=True)


# --- Parent Models ---


class Language(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    # Direct reference to linked Items
    items: list["Item"] = Relationship(
        back_populates="languages", link_model=LanguageItem
    )

    def __str__(self):
        return self.name


class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    # Direct reference to linked Items
    items: list["Item"] = Relationship(
        back_populates="categories", link_model=CategoryItem
    )

    def __str__(self):
        return self.name


# Library Items (books, magazines, etc.)
class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    dms_number: str = Field(default="", unique=True, nullable=False)
    item_code: str = Field(default="", unique=True, nullable=False)
    title: str
    sender_id: int = Field(foreign_key="user.id")
    received_at: datetime = Field(default_factory=datetime.now)
    acknowledgement_sent: datetime = Field(default_factory=datetime.now)
    location_id: int = Field(foreign_key="location.id")
    approved_by_id: int = Field(foreign_key="user.id")
    approved_at: datetime = Field(default_factory=datetime.now)
    remarks: str = Field(default="")
    quick_insights: str = Field(default="")
    type_id: int = Field(foreign_key="itemtype.id")
    author_id: int = Field(foreign_key="author.id")

    languages: list[Language] = Relationship(
        back_populates="items", link_model=LanguageItem
    )

    categories: list[Category] = Relationship(
        back_populates="items", link_model=CategoryItem
    )

    author: Author | None = Relationship(
        back_populates="items",
        sa_relationship_kwargs={"foreign_keys": "[Item.author_id]"},
    )

    sender: User | None = Relationship(
        back_populates="sent_items",
        sa_relationship_kwargs={"foreign_keys": "[Item.sender_id]"},
    )

    location: Location | None = Relationship(
        back_populates="items",
        sa_relationship_kwargs={"foreign_keys": "[Item.location_id]"},
    )

    item_type: ItemType | None = Relationship(
        back_populates="items",
        sa_relationship_kwargs={"foreign_keys": "[Item.type_id]"},
    )

    approved_by: User | None = Relationship(
        back_populates="approved_items",
        sa_relationship_kwargs={"foreign_keys": "[Item.approved_by_id]"},
    )

    embedding: list[float] | None = Field(default=None, sa_column=Column(Vector(384)))


def create_database():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_database()
