from typing import Generator

from sqlalchemy import text
from sqlmodel import Session, create_engine

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False}, echo=True)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def db_ping():
    with engine.connect() as conn:
        _ = conn.execute(text("SELECT 1"))
