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
            1 - vec_distance_cosine(embedding, :vec) AS similarity
        FROM item
        WHERE embedding IS NOT NULL
            AND (1 - vec_distance_cosine(embedding, :vec)) >= 0.35
        ORDER BY vec_distance_cosine(embedding, :vec) ASC
        LIMIT :limit;
    """
    )
    with engine.connect() as conn:
        result = conn.execute(
            sql, {"vec": str(query_vector), "limit": limit}
        ).fetchall()
        items = str([dict(r._mapping) for r in result])

        if not items:
            return "NO_RECORDS_FOUND"

        return str(items)


@tool(description="Run a SQL query on the database and return the results.")
def run_db_query(sql_query: str):
    db = SQLDatabase(engine)

    if not sql_query.strip().lower().startswith("select"):
        return "Error: Only SELECT queries are permitted."

    result = db.run(sql_query)
    if not result or result == "[]":
        return "NO_RECORDS_FOUND"

    return result
