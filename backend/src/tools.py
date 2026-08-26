from langchain_community.utilities import SQLDatabase
from langchain_core.tools import tool
from sentence_transformers import SentenceTransformer
from sqlalchemy import text

from database import engine

embedder = SentenceTransformer("all-MiniLM-L6-v2")


@tool(
    description="Perform semantic search on book insights and remarks using local vector embeddings."
)
def vector_search_books(query: str, limit: int = 5) -> str:
    """Perform semantic search on book insights and remarks using local vector embeddings."""
    query_vector = embedder.encode(query).tolist()

    # Replace :vec::vector with CAST(:vec AS vector)
    sql = text(
        """
        SELECT id, title, quick_insights, remarks,
                1 - (embedding <=> CAST(:vec AS vector)) AS similarity
        FROM item
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> CAST(:vec AS vector)
        LIMIT :limit;
    """
    )
    with engine.connect() as conn:
        result = conn.execute(
            sql, {"vec": str(query_vector), "limit": limit}
        ).fetchall()
        return str([dict(r._mapping) for r in result])


@tool(description="Run a SQL query on the database and return the results.")
def run_db_query(query: str):
    db = SQLDatabase(engine)

    if not query.strip().lower().startswith("select"):
        return "Error: Only SELECT queries are permitted."

    return db.run(query)
