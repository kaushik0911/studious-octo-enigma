from sqladmin import ModelView

from models import Language


class LanguageView(ModelView, model=Language):
    name_plural = "Languages"
    icon = "fa-solid fa-language"

    column_list = ["id", "name"]
    column_searchable_list = ["name"]
    column_sortable_list = ["name"]

    form_columns = ["name"]
