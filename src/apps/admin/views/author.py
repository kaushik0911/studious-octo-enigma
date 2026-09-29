from typing import ClassVar

from sqladmin import ModelView

from src.common.models import Author


class AuthorView(ModelView, model=Author):
    icon: ClassVar[str] = "fa-solid fa-user"

    column_list: ClassVar[list[str]] = ["id", "first_name", "last_name", "email"]
    column_searchable_list: ClassVar[list[str]] = ["first_name", "last_name", "email"]
    column_sortable_list: ClassVar[list[str]] = ["first_name", "last_name", "email"]

    form_columns: ClassVar[list[str]] = ["first_name", "last_name", "email"]
