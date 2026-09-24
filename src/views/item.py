from sqladmin import ModelView

from models import Item


class ItemView(ModelView, model=Item):
    icon = "fa-solid fa-book"

    column_list = ["dms_number", "item_code", "title", "author"]

    form_columns = [
        "title",
        "dms_number",
        "item_code",
        "languages",
        "categories",
        "author",
        "sender",
        "received_at",
        "acknowledgement_sent",
        "location",
        "item_type",
        "remarks",
        "quick_insights",
        "approved_by",
        "approved_at",
    ]
