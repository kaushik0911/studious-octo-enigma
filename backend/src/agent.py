from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

from tools import run_db_query, vector_search_books

llm = ChatOllama(model="qwen3.5:0.8b", temperature=0)

tools = [vector_search_books, run_db_query]

system_prompt = """
You are a library assistant. Match user requests to books(items) using tools.

### DATABASE SCHEMA
- item (id, title, quick_insights, remarks, author_id, location_id, type_id)
- author (id, first_name, last_name)
- category (id, name) | language (id, name)

### TOOL ROUTING RULES
1. IF searching by plot, topic, summary, or concept -> USE `vector_search_books(query, limit=5)`.
   - Focus search terms on key concepts stored in `quick_insights`.
2. IF searching by exact metadata (author name, category, location, language) -> USE `run_db_query`.
3. Default `limit=5` for all queries.

### EXECUTION RULES
- Execute AT MOST ONE tool call per turn.
- After receiving tool results, respond immediately to the user.
- NEVER display raw SQL, code, or JSON to the user.

### RESPONSE FORMAT
Format every recommendation as:
- **[Book Title]**
- **Quick Insights**: (Extract summary from quick_insights)
- **Why It Matches**: (Brief reason it fits the request)
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
