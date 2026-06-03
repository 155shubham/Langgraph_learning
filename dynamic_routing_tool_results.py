from typing import List, Optional, TypedDict, Literal
from langgraph import StateGraph, START, END

from simple_loop import State

# Example state


class ToolState(TypedDict):
    query: str
    results: List[str]
    tool_ok: bool
    error: Optional[str]
    final: Optional[str]

# Tool Node


def run_search_tool(state: ToolState):
    q = state['query'].strip()

    # Fake tool behaviour for demo purposes
    if not q:
        return {"results": [], "tool_ok": False, "error": "Empty query", "final": None}

    results = [f"Result for '{q} #1'", f"Result for {q} #2"]
    return {"results": results, "tool_ok": True, "error": None, "final": None}

# Routing function


Next = Literal['use_results', 'fallback', "ask_user"]


def route_after_tool(state: State) -> Next:
    if not state['tool_ok']:
        return 'ask_user'  # tool failed, get clarification
    elif len(state['results']) == 0:
        return 'fallback'  # tool worked but returned nothing
    else:
        return 'use_results'  # tool worked and returned results


# Destination Nodes

def use_results(state: ToolState):
    return {"final": f"Using results {len(state['results'])} results to answer"}


def fall_back(state: ToolState):
    return {"final": "No results found.  Trying a broader query or backup tool."}


def ask_user(state: ToolState):
    return {"final": f"Tool failed with error: {state['error']}. Please clarify your query."}


# GRaph wiring
builder = StateGraph()
builder.add_node("search", run_search_tool)
builder.add_node("use_results", use_results)
builder.add_node("fallback", fall_back)
builder.add_node("ask_user", ask_user)

builder.add_edge(START, "search")
builder.add_conditional_edge("search", route_after_tool, {
    'use_results': "use_results",
    'fallback': "fallback",
    'ask_user': "ask_user"
})

builder.add_edge("use_results", END)
builder.add_edge("fallback", END)
builder.add_edge("ask_user", END)

graph = builder.compile()
