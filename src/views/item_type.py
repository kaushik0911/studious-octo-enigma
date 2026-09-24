from sqladmin import ModelView

from models import ItemType


class ItemTypeView(ModelView, model=ItemType):
    name_plural = "Item Types"
    icon = "fa-solid fa-tag"

    column_list = ["id", "type"]
    column_searchable_list = ["type"]
    column_sortable_list = ["type"]

    form_columns = ["type"]
