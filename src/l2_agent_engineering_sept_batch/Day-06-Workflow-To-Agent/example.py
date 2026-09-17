"""Session 6: the model chooses one permitted next action."""

import ollama
from langgraph.graph import END, START, StateGraph
from dotenv import load_dotenv

load_dotenv()

#MODEL = "gpt-oss:120b-cloud"
#from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4.1-mini-2025-04-14",
)


def decide(state):
    prompt = """Choose the next action for this IT request.
Return only TOOL for a password request.
Return only ANSWER for anything else.

Request: """ + state["request"]

    response = llm.invoke(prompt)
    action = response.content.strip().upper()

    if action not in ["TOOL", "ANSWER"]:
        action = "ANSWER"

    return {"action": action}


def next_node(state):
    return state["action"].lower()


def use_tool(state):
    return {"answer": "Tool result: open the password reset page."}


def answer_directly(state):
    return {"answer": "Direct answer: your request was received."}


graph_builder = StateGraph(dict)
graph_builder.add_node("decide", decide)
graph_builder.add_node("tool", use_tool)
graph_builder.add_node("answer", answer_directly)
graph_builder.add_edge(START, "decide")
graph_builder.add_conditional_edges("decide", next_node)
graph_builder.add_edge("tool", END)
graph_builder.add_edge("answer", END)
graph = graph_builder.compile()

result = graph.invoke({"request": "how do I reset my password?"})
print(result["answer"])
