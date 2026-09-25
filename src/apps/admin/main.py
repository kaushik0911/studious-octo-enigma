from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqladmin import Admin
from starlette.applications import Starlette

from src.apps.admin.views.author import AuthorView
from src.apps.admin.views.category import CategoryView
from src.apps.admin.views.item import ItemView
from src.apps.admin.views.item_type import ItemTypeView
from src.apps.admin.views.language import LanguageView
from src.apps.admin.views.location import LocationView
from src.apps.admin.views.user import UserView
from src.common.database import db_ping, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_ping()
    yield


app = Starlette()


admin = Admin(app, engine)

admin.add_view(CategoryView)
admin.add_view(LanguageView)
admin.add_view(UserView)
admin.add_view(ItemView)
admin.add_view(LocationView)
admin.add_view(ItemTypeView)
admin.add_view(AuthorView)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
