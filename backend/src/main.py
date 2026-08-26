from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from sqladmin import Admin

from database import db_ping, engine
from routers import categories, items, languages, users
from views.author import AuthorView
from views.category import CategoryView
from views.item import ItemView
from views.item_type import ItemTypeView
from views.language import LanguageView
from views.location import LocationView
from views.user import UserView


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_ping()
    yield


app = FastAPI(title="Library Item Management API", version="1.0.0")

app.include_router(items.router)
app.include_router(languages.router)
app.include_router(users.router)
app.include_router(categories.router)

admin = Admin(app, engine)

admin.add_view(CategoryView)
admin.add_view(LanguageView)
admin.add_view(UserView)
admin.add_view(ItemView)
admin.add_view(LocationView)
admin.add_view(ItemTypeView)
admin.add_view(AuthorView)


@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
