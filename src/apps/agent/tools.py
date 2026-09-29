import json
import re

from langchain_core.tools import tool
from sentence_transformers import SentenceTransformer
from sqlalchemy import text

from common.database import engine

embedder = SentenceTransformer("all-MiniLM-L6-v2")
MAX_QUERY_ROWS = 100
MAX_VECTOR_RESULTS = 20


def get_embedding_index_status() -> dict[str, int]:
    """Return read-only counts that indicate whether semantic indexing exists."""
    with engine.connect() as conn:
        row = (
            conn.execute(
                text(
                    "SELECT COUNT(*) AS total_items, "
                    "COUNT(embedding) AS embedded_items FROM item"
                )
            )
            .mappings()
            .one()
        )

    return {
        "total_items": row["total_items"],
        "embedded_items": row["embedded_items"],
    }


@tool(
    description=(
        "Find library items by meaning using their title, insights, and remarks. "
        "Use for topic, subject, or concept searches, not counts or exact metadata."
    )
)
def vector_search_items(query: str, limit: int = 5) -> str:
    """Find library items by semantic similarity to their content."""
    limit = max(1, min(limit, MAX_VECTOR_RESULTS))
    query_vector = embedder.encode(query).tolist()

    sql = text(
        """
        SELECT id, item_code, title, quick_insights, remarks,
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
        if not result:
            return "NO_RECORDS_FOUND"

        return json.dumps([dict(row._mapping) for row in result], default=str)


@tool(
    description=(
        "Answer factual questions about any library database table using one "
        "read-only SELECT or WITH query. Supports lookups, joins, counts, "
        "grouping, and date filters. Return only the columns needed and use "
        "LIMIT 100 or less for row lists."
    )
)
def run_db_query(sql_query: str) -> str:
    """Execute one bounded, read-only SQL query against the library database."""
    if not re.match(r"^(SELECT|WITH)\b", sql_query.strip(), re.IGNORECASE):
        return "QUERY_REJECTED: Only SELECT or WITH queries are permitted."

    try:
        with engine.connect() as conn:
            if engine.dialect.name == "sqlite":
                conn.exec_driver_sql("PRAGMA query_only = ON")
                try:
                    result = conn.execute(text(sql_query))
                    rows = result.mappings().fetchmany(MAX_QUERY_ROWS + 1)
                finally:
                    conn.exec_driver_sql("PRAGMA query_only = OFF")
            elif engine.dialect.name == "postgresql":
                with conn.begin():
                    conn.exec_driver_sql("SET TRANSACTION READ ONLY")
                    result = conn.execute(text(sql_query))
                    rows = result.mappings().fetchmany(MAX_QUERY_ROWS + 1)
            else:
                return f"QUERY_REJECTED: Unsupported database dialect {engine.dialect.name}."
    except Exception as error:
        return f"QUERY_ERROR: {error}"

    if not rows:
        return "NO_RECORDS_FOUND"

    truncated = len(rows) > MAX_QUERY_ROWS
    response = {
        "rows": [dict(row) for row in rows[:MAX_QUERY_ROWS]],
        "truncated": truncated,
    }
    return json.dumps(response, default=str)
