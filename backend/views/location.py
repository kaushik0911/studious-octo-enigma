from sqladmin import ModelView

from ..models import Location


class LocationView(ModelView, model=Location):
    name_plural = "Locations"
    icon = "fa-solid fa-location-dot"

    column_list = ["id", "name"]
    column_searchable_list = ["name"]
    column_sortable_list = ["name"]

    form_columns = ["name"]
