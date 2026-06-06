from typing import TypedDict, Literal, List
from langgraph.graph import START, END, StateGraph
from langgraph.types import Command

# 1. Define the Shared Memory (State)


class SupportState(TypedDict):
    user_msg: str
    internal_logs: List[str]  # We want to log what happens behind the scenes


# 2. Define the Router Node (Uses the Command API)
def inbox_router_node(state: SupportState) -> Command[Literal["billing_agent", "general_agent"]]:
    # For demo purposes, we route based on keywords in the user message
    msg = state["user_msg"].lower()

    if "refund" in msg:
        return Command(
            update={"internal_logs": [
                "Detected financial intent. Routing to Billing."]},
            goto="billing_agent"
        )
    else:
        return Command(
            update={"internal_logs": [
                "Detected normal query. Routing to General."]},
            goto="general_agent"
        )

# 3. Define the destination nodes


def billing_agent_node(state: SupportState):
    # Simulate handling the billing query
    print("--Billing Agent--")
    print(f"Internal logs so far: {state['internal_logs']}")
    return {"user_msg": " Processing your refund right now."}


def general_agent_node(state: SupportState):
    # Simulate handling a general query
    print("--General Agent--")
    print(f"Internal logs so far: {state['internal_logs']}")
    return {"user_msg": " How can I help you today?"}


# 4. Build the Graph (Notice: No conditional edges wired here!)
builder = StateGraph(SupportState)
builder.add_node("inbox_router", inbox_router_node)
builder.add_node("billing_agent", billing_agent_node)
builder.add_node("general_agent", general_agent_node)

# We only define where it starts. The 'inbox' node handles the rest!
builder.add_edge(START, "inbox_router")
builder.add_edge("billing_agent", END)
builder.add_edge("general_agent", END)

graph = builder.compile()

# 5. Let's test it out!
inputs = {"user_msg": "I want a refund for my broken shoes.", "internal_logs": []}
result = graph.invoke(inputs)

inputs = {"user_msg": "I want to buy shoes.", "internal_logs": []}
result = graph.invoke(inputs)
