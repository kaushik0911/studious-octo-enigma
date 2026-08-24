from sqladmin import ModelView

from ..models import Category


class CategoryView(ModelView, model=Category):
    name_plural = "Categories"
    icon = "fa-solid fa-folder"

    column_list = ["id", "name"]
    column_searchable_list = ["name"]
    column_sortable_list = ["name"]

    form_columns = ["name"]
