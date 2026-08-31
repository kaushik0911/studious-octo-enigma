from typing import Generator

import sqlite_vec
from sqlalchemy import event
from sqlmodel import Session, create_engine, text

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

username = "postgres"
password = "postgres"
port = 5432
database = "library"

postgres_url = (
    f"postgresql+psycopg2://{username}:{password}@localhost:{port}/{database}"
)

engine = create_engine(sqlite_url, echo=True)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@event.listens_for(engine, "connect")
def load_sqlite_vec(dbapi_connection, connection_record):
    dbapi_connection.enable_load_extension(True)
    sqlite_vec.load(dbapi_connection)
    dbapi_connection.enable_load_extension(False)


def db_ping():
    with engine.connect() as conn:
        _ = conn.execute(text("SELECT 1"))
        _ = conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

        conn.commit()
