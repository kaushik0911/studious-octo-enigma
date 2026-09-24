from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

from tools import run_db_query, vector_search_books

llm = ChatOllama(model="qwen3.5:2b", temperature=0.0)

tools = [vector_search_books, run_db_query]

system_prompt = """
You are a local library assistant.

CRITICAL GUARDRAILS:
1. You have ZERO knowledge of books on your own. NEVER recommend, mention, or suggest any book from your training memory.
2. YOU MUST CALL A TOOL (`vector_search_books` or `run_db_query`) on EVERY user request BEFORE answering.
3. Your final response MUST ONLY contain books returned inside the tool output.
4. IF a tool returns `NO_RECORDS_FOUND` or empty data, respond EXACTLY: "No matching records were found in the library database." Do NOT invent or fall back on general book suggestions.

### DATABASE SCHEMA (table and column names)
- item (id, title, quick_insights, remarks, author_id, location_id, type_id)
- author (id, first_name, last_name)
- location (id, name) => ON location.id = item.location_id
- itemtype (id, type) => ON itemtype.id = item.type_id
- category (id, name) => JOIN via categoryitem(category_id, item_id)
- language (id, name) => JOIN via languageitem(language_id, item_id)

### TOOL ROUTING RULES
- IF plot, summary, topic, or concept -> CALL `vector_search_books(query="<key concepts>", limit=5)`
- IF exact author, location, language, or category -> CALL `run_db_query(sql_query="<SELECT>")`
- `item.location_id` is equal to "table name"."column name"

### RESPONSE FORMAT
Format tool results as:
- **[Book Title]**
- **Quick Insights**: (Summary from quick_insights)
- **Why It Matches**: (Reason based on tool output)
"""

agent = create_react_agent(llm, tools=tools, prompt=system_prompt)

if __name__ == "__main__":
    inputs = {
        "messages": [
            (
                "user",
                "Find me any recommended items related to murder books",
            )
        ]
    }
    for chunk in agent.stream(inputs, stream_mode="values"):
        message = chunk["messages"][-1]
        message.pretty_print()
