import os

from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

from tools import run_db_query, vector_search_books

llm = ChatOllama(model=os.getenv("LLM_NAME", ""), temperature=0.0)

tools = [vector_search_books, run_db_query]

system_prompt = open("src/system_prompt.md", "r").read()

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
