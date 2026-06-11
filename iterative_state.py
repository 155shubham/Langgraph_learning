from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Optional
import time

# 1. Your exact State Schema


class LoopState(TypedDict):
    # Work data
    draft: Optional[str]
    issues: List[str]
    score: float
    passed: bool

    # Stopping controls
    iteration: int
    max_iteration: int

    llm_calls: float
    max_llm_calls: float

    start_ms: int
    deadline_ms: int

# 2. Worker Node (Simulates updating work metrics and incrementing calls)


def researcher_node(state: LoopState) -> dict:
    current_iter = state["iteration"] + 1
    current_calls = state["llm_calls"] + 1

    print(f"\n🤖 [Iteration {current_iter}] Agent running generation...")

    # Simulate a draft that fails on try 1, but passes on try 2
    if current_iter == 1:
        return {
            "draft": "Draft 1: Incomplete data.",
            "issues": ["Missing citations"],
            "score": 60.0,
            "passed": False,
            "iteration": current_iter,
            "llm_calls": current_calls
        }
    else:
        return {
            "draft": "Draft 2: Comprehensive scientific breakdown.",
            "issues": [],
            "score": 92.5,
            "passed": True,
            "iteration": current_iter,
            "llm_calls": current_calls
        }

# 3. Router Function (The Conditional Edge checking your criteria)


def should_continue(state: LoopState) -> str:
    print("📋 Checking Loop State Criteria...")

    # Check 1: Did it pass the evaluation criteria?
    if state["passed"]:
        print("➡️ CRITERIA MET: Draft successfully passed inspection!")
        return "exit"

    # Check 2: Hit iteration safety limit?
    if state["iteration"] >= state["max_iteration"]:
        print("🚨 CRITERIA MET: Hard limit on iterations hit!")
        return "exit"

    # Check 3: Hit financial/LLM call budget limit?
    if state["llm_calls"] >= state["max_llm_calls"]:
        print("💸 CRITERIA MET: Out of LLM token/call budget!")
        return "exit"

    # Check 4: Time-based deadline expiration check
    current_time_ms = int(time.time() * 1000)
    if current_time_ms >= state["deadline_ms"]:
        print("⏳ CRITERIA MET: Hard time deadline expired!")
        return "exit"

    # If no stopping criteria are met, continue the loop
    print("🔄 Keep looping. Sending back to researcher...")
    return "loop"


# 4. Building the Graph
builder = StateGraph(LoopState)

builder.add_node("researcher", researcher_node)
builder.add_edge(START, "researcher")

# Connect the conditional edge directly using your routing logic
builder.add_conditional_edges(
    "researcher",
    should_continue,
    {
        "exit": END,
        "loop": "researcher"
    }
)

graph = builder.compile()

# 5. Setting up initial controls for execution
now_ms = int(time.time() * 1000)

initial_state: LoopState = {
    "draft": None,
    "issues": [],
    "score": 0.0,
    "passed": False,

    "iteration": 0,
    "max_iteration": 3,      # Allow up to 3 turns

    "start_ms": now_ms,
    "deadline_ms": now_ms + 10000,  # 10-second hard timeout deadline

    "llm_calls": 0,
    "max_llm_calls": 5       # Global safety budget for API limits
}

graph.invoke(initial_state)
