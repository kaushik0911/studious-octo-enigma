from typing import ClassVar

from sqladmin import ModelView

from src.common.models import Category


class CategoryView(ModelView, model=Category):
    name_plural: ClassVar[str] = "Categories"
    icon: ClassVar[str] = "fa-solid fa-folder"

    column_list: ClassVar[list[str]] = ["id", "name"]
    column_searchable_list: ClassVar[list[str]] = ["name"]
    column_sortable_list: ClassVar[list[str]] = ["name"]

    form_columns: ClassVar[list[str]] = ["name"]
