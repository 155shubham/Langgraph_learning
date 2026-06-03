from typing import TypedDict
from langgraph.graph import START, END, StateGraph

# 1) Define the state your graph carries around


class MyState(TypedDict):
    name: str
    message: str

# 2) Define node functions (each node receives state and returns updated state)


def greet(state: MyState):
    state['message'] = f"Hello {state['name']}"
    return state


def add_followup(state: MyState):
    state["message"] += ", How can I help today?"
    return state


# 3) Build the graph
builder = StateGraph(MyState)
builder.add_node("greet", greet)
builder.add_node("followup", add_followup)

# 4) Wire edges (control the execution order)
builder.add_edge(START, "greet")
builder.add_edge("greet", "followup")
builder.add_edge("followup", END)

# 5) Compile into an executable graph
graph = builder.compile()

# 6) Run it
result = graph.invoke({"name": "sb", "message": ""})
print(result["message"])
