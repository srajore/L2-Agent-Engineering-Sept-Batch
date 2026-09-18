"""Day 7 (flavor 2): the same chatbot, but WITH memory via a checkpointer + thread_id."""

import sys

import ollama
from langgraph.checkpoint.memory import InMemorySaver
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
graph = graph_builder.compile(checkpointer=InMemorySaver())

# Same thread_id on every call -> the checkpointer reloads chat_history each time.
settings = {"configurable": {"thread_id": "student-1"}}

print("Chatbot ready (in-memory chat). Type 'bye' or 'quit' to stop.")
while True:
    user_message = input("You: ")
    if user_message.strip().lower() in ("bye", "quit"):
        print("Chatbot: Goodbye!")
        break

    # Same thread_id -> the checkpointer reloads chat_history from earlier turns.
    result = graph.invoke({"user_message": user_message}, config=settings)
    print("Chatbot:", result["reply"])
