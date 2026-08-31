import streamlit as st

from agent import agent

st.title("Library Assistant")

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
    inputs = {
        "messages": [(m["role"], m["content"]) for m in st.session_state.messages]
    }

    config = {"recursion_limit": 10}

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        # Stream response from agent
        for chunk in agent.stream(inputs, stream_mode="values", config=config):
            final_message = chunk["messages"][-1]

        response_text = final_message.content
        response_placeholder.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
