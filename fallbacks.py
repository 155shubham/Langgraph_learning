from typing import TypedDict, Optional, Literal, List
from langgraph.graph import START, END, StateGraph

Next = Literal["use_result", "try_alternate", "safe_response"]


class State(TypedDict):
    query: str
    result: Optional[str]

    # tool outcomes
    primary_ok: bool
    alterate_ok: bool
    error: Optional[str]

    # control
    attempts: int
    max_attempts: int

# dd
def primary_tool(state: State):
    q = state["query"].strip()
    # Fake failure condition for demo
    if "fail_also" in q:
        return {"primary_ok": False, "error": "Primary tool failed"}
    return {"primary_ok": True, "result": f"Primary tool result for query: {q}"}


def alternative_tool(state: State):
    q = state["query"].strip()
    # Fake failure condition for demo
    if "fail" in q:
        return {"alterate_ok": False, "error": "Alternative tool failed"}
    return {"alterate_ok": True, "result": f"Alternative tool result for query: {q}"}


def route_after_primary(state: State) -> Next:
    if state["primary_ok"]:
        return "use_result"
    # if primary failed, try alternate (but only if we still have attempts left)
    if state["attempts"] < state["max_attempts"]:
        return "try_alternate"
    return "safe_response"


def route_after_alternate(state: State) -> Next:
    if state["alterate_ok"]:
        return "use_result"
    return "safe_response"


def bump_attempts(state: State):
    return {"attempts": state["attempts"] + 1}


def use_result(state: State):
    return {"result": state["result"] or "No result"}


def safe_response(state: State):
    # Safe response should be helpful and non-hallucination
    msg = ("Sorry, I'm having trouble finding the information you need."
           "Please try again later, or share more details so I can help without tools.")
    return {"result": msg}


builder = StateGraph(State)
builder.add_node("primary", primary_tool)
builder.add_node("alternate", alternative_tool)
builder.add_node("bump_attempts", bump_attempts)
builder.add_node("use_result", use_result)
builder.add_node("safe_response", safe_response)

builder.add_edge(START, "primary")

builder.add_conditional_edges(
    "primary",
    route_after_primary,
    {
        "use_result": "use_result",
        "try_alternate": "bump_attempts",
        "safe_response": "safe_response"
    }
)

builder.add_conditional_edges(
    "alternate",
    route_after_alternate,
    {
        "use_result": "use_result",
        "try_alternate": "bump_attempts",
        "safe_response": "safe_response"
    }
)

builder.add_edge("use_result", END)
builder.add_edge("safe_response", END)

graph = builder.compile()
