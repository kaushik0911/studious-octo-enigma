from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.apps.api.routers import categories, items, languages, users
from src.common.database import db_ping


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_ping()
    yield


app = FastAPI(title="Library Item Management API", version="1.0.0")

app.include_router(items.router)
app.include_router(languages.router)
app.include_router(users.router)
app.include_router(categories.router)


@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
