from typing import ClassVar

from sqladmin import ModelView

from src.common.models import Language


class LanguageView(ModelView, model=Language):
    name_plural: ClassVar[str] = "Languages"
    icon: ClassVar[str] = "fa-solid fa-language"

    column_list: ClassVar[list[str]] = ["id", "name"]
    column_searchable_list: ClassVar[list[str]] = ["name"]
    column_sortable_list: ClassVar[list[str]] = ["name"]

    form_columns: ClassVar[list[str]] = ["name"]
