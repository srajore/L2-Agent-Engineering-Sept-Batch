"""Day 7 (flavor 4 UI): Streamlit chat window for the graph in example_chatbot_streamlit.py."""

import streamlit as st

from example_chatbot_streamlit import graph

st.title("Day 7 Chatbot (SQLite memory)")
thread_id = st.sidebar.text_input("Thread ID", value="student-1")
settings = {"configurable": {"thread_id": thread_id}}

if "stopped" not in st.session_state:
    st.session_state.stopped = False

if not st.session_state.stopped:
    user_message = st.chat_input("Type a message ('bye' or 'quit' to stop)")
    if user_message:
        if user_message.strip().lower() in ("bye", "quit"):
            st.session_state.stopped = True
        else:
            graph.invoke({"user_message": user_message}, config=settings)

saved_state = graph.get_state(settings)
chat_history = saved_state.values.get("chat_history", [])
for message in chat_history:
    st.chat_message(message["role"]).write(message["content"])

if st.session_state.stopped:
    st.chat_message("assistant").write("Goodbye!")
