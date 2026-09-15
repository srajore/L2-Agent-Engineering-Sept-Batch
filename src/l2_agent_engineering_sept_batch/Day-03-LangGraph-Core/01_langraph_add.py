from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class MyState(TypedDict):
    a: int
    b: int
    c: int


def input(state:MyState):
    state['a'] = 10
    state['b'] = 22
    return state
    

   
def calculate(state:MyState):
    state['c'] = state['a'] + state['b']
    return state


graph = StateGraph(MyState)
graph.add_node("node1",input)
graph.add_node("node2",calculate)

graph.add_edge(START,"node1")
graph.add_edge("node1","node2")
graph.add_edge("node2",END)

myGraph = graph.compile()

result = myGraph.invoke({"a":0,"b":0,"c":0})

print(result)
