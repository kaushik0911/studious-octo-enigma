from typing import Generator

from sqlalchemy import text
from sqlmodel import Session, create_engine

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

postgres_url = "postgresql+psycopg2://postgres:postgres@localhost:5432/library"

engine = create_engine(postgres_url, echo=True)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def db_ping():
    with engine.connect() as conn:
        _ = conn.execute(text("SELECT 1"))
        _ = conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

        conn.commit()
