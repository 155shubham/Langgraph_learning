from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# ---- Child graph (subgraph) ----


class ChildState(TypedDict):
    name: str
    family_name: str


def set_family_name(state: ChildState):
    return {"family_name": "Smith"}


def combine_name(state: ChildState):
    return {"name": f"{state['name']} {state['family_name']}"}


child_builder = StateGraph(ChildState)
child_builder.add_node("set_family", set_family_name)
child_builder.add_node("combine", combine_name)
child_builder.add_edge(START, "set_family")
child_builder.add_edge("set_family", "combine")
child_builder.add_edge("combine", END)

child_graph = child_builder.compile()

# ---- Parent graph ----


class ParentState(TypedDict):
    name: str


parent_builder = StateGraph(ParentState)

# Add the compiled subgraph as a node
parent_builder.add_node("enrich_name", child_graph)
parent_builder.add_edge(START, "enrich_name")
parent_builder.add_edge("enrich_name", END)

parent_graph = parent_builder.compile()

result = parent_graph.invoke({"name": "John"})
print(result["name"])  # Output: "John Smith"
