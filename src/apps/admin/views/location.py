from typing import ClassVar

from sqladmin import ModelView

from src.common.models import Location


class LocationView(ModelView, model=Location):
    name_plural: ClassVar[str] = "Locations"
    icon: ClassVar[str] = "fa-solid fa-location-dot"

    column_list: ClassVar[list[str]] = ["id", "name"]
    column_searchable_list: ClassVar[list[str]] = ["name"]
    column_sortable_list: ClassVar[list[str]] = ["name"]

    form_columns: ClassVar[list[str]] = ["name"]
