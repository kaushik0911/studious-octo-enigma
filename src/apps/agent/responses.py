import json
import re
from collections.abc import Mapping
from typing import Any

NO_MATCHES_RESPONSE = "No matching records were found in the library database."
QUERY_UNAVAILABLE_RESPONSE = (
    "I couldn't verify an answer from the library database. Please try again."
)

_AGGREGATE_PATTERN = re.compile(
    r"\b(how many|count|number of|total|average|minimum|maximum)\b", re.IGNORECASE
)
_ITEM_PATTERN = re.compile(
    r"\b(items?|books?|titles?|materials?|resources?)\b", re.IGNORECASE
)
_RECOMMENDATION_PATTERN = re.compile(
    r"\b(recommend(?:ed|ation|ations)?|suggest(?:ed|ion|ions)?)\b", re.IGNORECASE
)
_SEARCH_PATTERN = re.compile(r"\b(find|search|looking for)\b", re.IGNORECASE)
_TOPIC_PATTERN = re.compile(
    r"\b(related to|about|on|topic|subject|concept|plot|theme)\b", re.IGNORECASE
)
_EXACT_FILTER_PATTERN = re.compile(
    r"\b(by|author|location|language|category|item code|exact title|item type)\b",
    re.IGNORECASE,
)


def is_semantic_item_request(question: str) -> bool:
    if _AGGREGATE_PATTERN.search(question) or not _ITEM_PATTERN.search(question):
        return False
    if _EXACT_FILTER_PATTERN.search(question):
        return False
    if _RECOMMENDATION_PATTERN.search(question):
        return True
    return bool(_SEARCH_PATTERN.search(question) and _TOPIC_PATTERN.search(question))


def format_item_search_result(result: str) -> str:
    if result == "NO_RECORDS_FOUND":
        return NO_MATCHES_RESPONSE

    try:
        records: Any = json.loads(result)
    except (TypeError, json.JSONDecodeError):
        return QUERY_UNAVAILABLE_RESPONSE

    if not isinstance(records, list) or not records:
        return NO_MATCHES_RESPONSE

    formatted_records = []
    for record in records:
        if not isinstance(record, Mapping) or not record.get("title"):
            continue

        item_code = record.get("item_code")
        title = record["title"]
        lines = [f"**{item_code or 'Item code unavailable'}** | **{title}**"]
        if insights := record.get("quick_insights"):
            lines.append(f"**Quick Insights**: {insights}")
        formatted_records.append("\n\n".join(lines))

    return "\n\n".join(formatted_records) if formatted_records else NO_MATCHES_RESPONSE


def validate_agent_tool_results(messages: list[Any]) -> str:
    tool_messages = [
        message for message in messages if getattr(message, "type", None) == "tool"
    ]
    if not tool_messages:
        return QUERY_UNAVAILABLE_RESPONSE

    for message in tool_messages:
        content = message.content
        if getattr(message, "status", "success") == "error":
            return QUERY_UNAVAILABLE_RESPONSE
        if isinstance(content, str) and content == "NO_RECORDS_FOUND":
            return NO_MATCHES_RESPONSE
        if isinstance(content, str) and content.startswith(
            ("QUERY_ERROR:", "QUERY_REJECTED:")
        ):
            return QUERY_UNAVAILABLE_RESPONSE

    return ""
