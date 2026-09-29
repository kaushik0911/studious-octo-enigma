from typing import ClassVar

from sqladmin import ModelView

from src.common.models import User


class UserView(ModelView, model=User):
    icon: ClassVar[str] = "fa-solid fa-user"

    name: ClassVar[str] = "Administrator"
    name_plural: ClassVar[str] = "Administrators"
    column_list: ClassVar[list[str]] = ["id", "first_name", "last_name", "email"]
    column_searchable_list: ClassVar[list[str]] = ["first_name", "last_name", "email"]
    column_sortable_list: ClassVar[list[str]] = ["first_name", "last_name", "email"]

    form_columns: ClassVar[list[str]] = ["first_name", "last_name", "email"]
