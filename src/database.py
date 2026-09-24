import os
from collections.abc import Generator

import sqlite_vec
from dotenv import load_dotenv
from sqlalchemy import event
from sqlmodel import Session, create_engine, text

load_dotenv()


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

host = os.getenv("PGHOST")
username = os.getenv("PGUSER")
password = os.getenv("PGPASSWORD")
port = os.getenv("PORT")
database = os.getenv("PGDATABASE")

postgres_url = f"postgresql+psycopg2://{username}:{password}@{host}/{database}"

engine = create_engine(sqlite_url, echo=True)


def get_session() -> Generator[Session]:
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
