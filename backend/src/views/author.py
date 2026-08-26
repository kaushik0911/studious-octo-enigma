from sqladmin import ModelView

from models import Author


class AuthorView(ModelView, model=Author):
    icon = "fa-solid fa-user"

    column_list = ["id", "first_name", "last_name", "email"]
    column_searchable_list = ["first_name", "last_name", "email"]
    column_sortable_list = ["first_name", "last_name", "email"]

    form_columns = ["first_name", "last_name", "email"]
