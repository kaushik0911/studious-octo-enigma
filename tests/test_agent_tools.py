import json
import unittest
from unittest.mock import MagicMock, Mock, patch

from sentence_transformers import SentenceTransformer

with patch.object(SentenceTransformer, "__init__", return_value=None):
    from apps.agent import tools as agent_tools

agent_tools.embedder = Mock()

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from apps.agent.responses import (
    NO_MATCHES_RESPONSE,
    QUERY_UNAVAILABLE_RESPONSE,
    format_item_search_result,
    is_semantic_item_request,
    validate_agent_tool_results,
)


class AgentToolTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        with self.engine.begin() as connection:
            connection.exec_driver_sql(
                "CREATE TABLE itemtype (id INTEGER PRIMARY KEY, type TEXT)"
            )
            connection.exec_driver_sql(
                "CREATE TABLE item (id INTEGER PRIMARY KEY, type_id INTEGER, embedding BLOB)"
            )
            connection.exec_driver_sql(
                "INSERT INTO itemtype (id, type) VALUES (1, 'Book'), (2, 'Magazine')"
            )
            connection.exec_driver_sql(
                "INSERT INTO item (id, type_id) VALUES (1, 1), (2, 1), (3, 2)"
            )
        self.engine_patch = patch.object(agent_tools, "engine", self.engine)
        self.engine_patch.start()

    def tearDown(self):
        self.engine_patch.stop()
        self.engine.dispose()

    def vector_search_with_rows(self, rows):
        connection = Mock()
        connection.execute.return_value.fetchall.return_value = rows
        mock_engine = Mock()
        connection_context = MagicMock()
        connection_context.__enter__.return_value = connection
        mock_engine.connect.return_value = connection_context
        mock_embedder = Mock()
        mock_embedder.encode.return_value.tolist.return_value = [0.0] * 384
        with (
            patch.object(agent_tools, "engine", mock_engine),
            patch.object(agent_tools, "embedder", mock_embedder),
        ):
            return agent_tools.vector_search_items.func("community health")

    def test_sql_tool_returns_joined_book_count(self):
        result = agent_tools.run_db_query.func(
            "SELECT COUNT(*) AS book_count "
            "FROM item JOIN itemtype ON item.type_id = itemtype.id "
            "WHERE itemtype.type = 'Book'"
        )

        self.assertEqual(json.loads(result)["rows"][0]["book_count"], 2)

    def test_embedding_index_status_is_read_only_and_reports_missing_vectors(self):
        status = agent_tools.get_embedding_index_status()

        self.assertEqual(status, {"total_items": 3, "embedded_items": 0})

    def test_sql_tool_returns_no_records_for_empty_lookup(self):
        result = agent_tools.run_db_query.func("SELECT id FROM item WHERE id = -1")

        self.assertEqual(result, "NO_RECORDS_FOUND")

    def test_sql_tool_rejects_writes_even_through_a_cte(self):
        result = agent_tools.run_db_query.func(
            "WITH candidate AS (SELECT 1) UPDATE item SET type_id = 2"
        )

        self.assertTrue(result.startswith("QUERY_ERROR:"))
        count_result = agent_tools.run_db_query.func(
            "SELECT COUNT(*) AS item_count FROM item"
        )
        self.assertEqual(json.loads(count_result)["rows"][0]["item_count"], 3)

    def test_vector_search_returns_sentinel_for_empty_rows(self):
        result = self.vector_search_with_rows([])

        self.assertEqual(result, "NO_RECORDS_FOUND")

    def test_vector_search_returns_item_code(self):
        result = self.vector_search_with_rows(
            [
                Mock(
                    _mapping={
                        "id": 5,
                        "item_code": "LIB-005",
                        "title": "Community Health",
                        "quick_insights": "A public health text.",
                        "remarks": "",
                        "similarity": 0.82,
                    }
                )
            ]
        )
        result = json.loads(result)

        self.assertEqual(result[0]["item_code"], "LIB-005")

    def test_recommendation_question_uses_semantic_search_route(self):
        self.assertTrue(
            is_semantic_item_request(
                "Find me any recommended items related to community health"
            )
        )

    def test_aggregate_question_does_not_use_semantic_search_route(self):
        self.assertFalse(
            is_semantic_item_request("How many books are in the database?")
        )

    def test_item_search_formats_only_returned_records(self):
        result = format_item_search_result(
            json.dumps(
                [
                    {
                        "item_code": "LIB-005",
                        "title": "Community Health",
                        "quick_insights": "A public health text.",
                    }
                ]
            )
        )

        self.assertIn("Community Health", result)
        self.assertNotIn("Historical Perspective", result)
        self.assertIn("LIB-005", result)

    def test_empty_or_missing_agent_tool_result_cannot_become_a_guess(self):
        self.assertEqual(
            format_item_search_result("NO_RECORDS_FOUND"), NO_MATCHES_RESPONSE
        )
        self.assertEqual(validate_agent_tool_results([]), QUERY_UNAVAILABLE_RESPONSE)

    def test_agent_tool_errors_cannot_become_a_guess(self):
        tool_error = Mock(type="tool", content="SQL failed", status="error")

        self.assertEqual(
            validate_agent_tool_results([tool_error]), QUERY_UNAVAILABLE_RESPONSE
        )


if __name__ == "__main__":
    unittest.main()
