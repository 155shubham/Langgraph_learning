from typing import TypedDict, List
from operator import add
from typing_extensions import Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

# 1. Define the Global Memory (State)


class OverallState(TypedDict):
    topics: List[str]
    jokes: Annotated[List[str], add]  # Automatically appends parallel answers

# 2. Define the State for individual parallel workers


class WorkerState(TypedDict):
    topic: str

# 3. FIXED: The Node just passes through (Nodes MUST return a dict!)


def start_node(state: OverallState):
    print(f"--- Manager: Preparing topics {state['topics']} ---")
    return {}  # Keeps the graph happy by returning a dict

# 4. FIXED: The routing function (Edges are allowed to return lists of Send!)


def spawn_joke_writers(state: OverallState):
    print("--- Edge: Creating parallel Send tasks ---")
    # Edges can return a list of Send objects safely
    return [Send("generate_joke", {"topic": t}) for t in state["topics"]]

# 5. The Worker Node (Runs in parallel)


def generate_joke(state: WorkerState):
    topic = state["topic"]
    print(f"--- Worker: Writing a joke about {topic} ---")
    fake_joke = f"Why did the {topic} cross the road? To get to the other side!"
    return {"jokes": [fake_joke]}

# 6. The Fan-In Node (Gathers all results)


def collect_results(state: OverallState):
    print("--- Collector: All workers finished! ---")
    print(f"Final Joke List: {state['jokes']}")
    return state


# 7. Build the Graph
builder = StateGraph(OverallState)

# Add our nodes
builder.add_node("start_node", start_node)
builder.add_node("generate_joke", generate_joke)
builder.add_node("collect_results", collect_results)

# Wire the entry point
builder.add_edge(START, "start_node")

# FIXED: We use a conditional edge to trigger the Send fan-out!
builder.add_conditional_edges(
    "start_node",
    spawn_joke_writers,
    ["generate_joke"]  # Declares where this conditional edge is allowed to go
)

# Wire the exit
builder.add_edge("generate_joke", "collect_results")
builder.add_edge("collect_results", END)

graph = builder.compile()

# 8. Run the Graph
inputs = {"topics": ["cats", "coding", "coffee"], "jokes": []}
graph.invoke(inputs)
