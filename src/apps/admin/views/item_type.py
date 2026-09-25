from typing import ClassVar

from sqladmin import ModelView

from src.common.models import ItemType


class ItemTypeView(ModelView, model=ItemType):
    name_plural: ClassVar[str] = "Item Types"
    icon: ClassVar[str] = "fa-solid fa-tag"

    column_list: ClassVar[list[str]] = ["id", "type"]
    column_searchable_list: ClassVar[list[str]] = ["type"]
    column_sortable_list: ClassVar[list[str]] = ["type"]

    form_columns: ClassVar[list[str]] = ["type"]
