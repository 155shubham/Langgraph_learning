from typing import List, Literal, TypedDict, Optional
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    question: str
    draft: Optional[str]
    issues: List[str]
    passed: bool
    retry_count: int
    max_retries: int


def generate(state: State):
    # In reality, call your LLM here
    q = state["question"]
    draft = f"Draft answer to: {q}"
    return {"draft": draft}


def critique(state: State):
    draft = state["draft"] or ""
    issues = []
    if len(draft) < 30:
        issues.append("Draft is too short.")
    passed = len(issues) == 0
    return {"issues": issues, "passed": passed}


def route(state: State) -> Literal["finish", "retry"]:
    if state["passed"]:
        return "finish"
    if state["retry_count"] >= state["max_retries"]:
        return "finish"  # hard stop, even if not perfect
    return "retry"


def retry(state: State):
    return {"retry_count": state["retry_count"] + 1}


def finish(state: State):
    # You might also set a final field here
    return {}


builder = StateGraph(State)
builder.add_node("generate", generate)
builder.add_node("critique", critique)
builder.add_node("route", route)
builder.add_node("retry", retry)
builder.add_node("finish", finish)

builder.add_edge(START, "generate")
builder.add_edge("generate", "critique")

builder.add_conditional_edges("critique", route, {
    "retry": "retry",
    "finish": "finish",
})

builder.add_edge("retry", "generate")
builder.add_edge("finish", END)

graph = builder.compile()

graph.invoke({"question": "What is the capital of France?",
             "draft": None, "issues": [], "passed": False, "retry_count": 0, "max_retries": 3})
