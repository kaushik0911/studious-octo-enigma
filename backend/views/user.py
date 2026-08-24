from sqladmin import ModelView

from ..models import User


class UserView(ModelView, model=User):
    icon = "fa-solid fa-user"

    name = "Administrator"
    name_plural = "Administrators"
    column_list = ["id", "first_name", "last_name", "email"]
    column_searchable_list = ["first_name", "last_name", "email"]
    column_sortable_list = ["first_name", "last_name", "email"]

    form_columns = ["first_name", "last_name", "email"]
