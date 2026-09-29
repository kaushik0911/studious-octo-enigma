import streamlit as st
from langchain.agents.middleware.types import InputAgentState
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from apps.agent.main import agent
from apps.agent.responses import (
    format_item_search_result,
    is_semantic_item_request,
    validate_agent_tool_results,
)
from apps.agent.tools import get_embedding_index_status, vector_search_items

MAX_AGENT_HISTORY_MESSAGES = 12

st.title("Library Assistant")

st.cache_data.clear()
st.cache_resource.clear()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle user input
if prompt := st.chat_input("Ask for a book recommendation or search the database..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Format historical context for LangGraph agent
    agent_history = st.session_state.messages[-MAX_AGENT_HISTORY_MESSAGES:]
    if agent_history and agent_history[0]["role"] != "user":
        agent_history = agent_history[1:]

    inputs: InputAgentState = {
        "messages": [
            HumanMessage(content=m["content"])
            if m["role"] == "user"
            else AIMessage(content=m["content"])
            for m in agent_history
        ]
    }

    config: RunnableConfig = {"recursion_limit": 10}

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        if is_semantic_item_request(prompt):
            try:
                search_result = vector_search_items.invoke({"query": prompt})
                response_text = format_item_search_result(search_result)
                if search_result == "NO_RECORDS_FOUND":
                    index_status = get_embedding_index_status()
                    if (
                        index_status["total_items"]
                        and not index_status["embedded_items"]
                    ):
                        st.caption(
                            "Semantic search is not indexed yet; stored items have no embeddings."
                        )
            except Exception:
                response_text = (
                    "The library search is unavailable right now. Please try again."
                )
        else:
            response = agent.invoke(input=inputs, config=config)
            messages = response["messages"]
            validation_response = validate_agent_tool_results(messages)
            if not validation_response:
                response_text = messages[-1].content
            else:
                response_text = validation_response

        response_placeholder.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
