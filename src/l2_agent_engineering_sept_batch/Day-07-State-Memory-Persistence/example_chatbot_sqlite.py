"""Day 7 (flavor 3): a chatbot whose memory survives a restart, using SqliteSaver."""

import sys

import ollama
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from typing import TypedDict

sys.stdout.reconfigure(encoding="utf-8")


class ChatState(TypedDict, total=False):
    user_message: str
    chat_history: list[dict]
    reply: str


def chatbot(state):
    history = state.get("chat_history", []) + [{"role": "user", "content": state["user_message"]}]
    response = ollama.chat(model="gpt-oss:120b-cloud", messages=history)
    reply = response["message"]["content"]
    history = history + [{"role": "assistant", "content": reply}]
    return {"chat_history": history, "reply": reply}


graph_builder = StateGraph(ChatState)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# Same thread_id every run -> SqliteSaver reloads chat_history even after a restart,
# because the checkpoint is written to a database file on disk, not to process memory.
settings = {"configurable": {"thread_id": "student-1"}}



with SqliteSaver.from_conn_string("day7_chatbot_memory.db") as checkpointer:
    graph = graph_builder.compile(checkpointer=checkpointer)

    print("Chatbot ready. Type 'bye' or 'quit' to stop.")
    while True:
        user_message = input("You: ")
        if user_message.strip().lower() in ("bye", "quit"):
            print("Chatbot: Goodbye!")
            break

        result = graph.invoke({"user_message": user_message}, config=settings)
        print("Chatbot:", result["reply"])
