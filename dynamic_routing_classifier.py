from typing import TypedDict, Literal, Optional
from langgraph import StateGraph, START, END

Intent = Literal['billing', 'tech', 'sales']

# State schema


class State(TypedDict):
    user_txt: str
    intent: Optional[Intent]
    description: Optional[str]

# Classifier node (LLM or rules)


def classify_intent(state: State):
    text = state['user_txt'].lower()

    # Simple rule-based classifier for demo purposes
    if 'refund' in text or "invoice" in text:
        intent: Intent = 'billing'
    elif 'bug' in text or 'error' in text:
        intent: Intent = 'tech'
    else:
        intent: Intent = 'sales'
    return intent

# Routing function


def routing_by_intent(state: State) -> Intent:
    return state['intent'] or "sales"

# Destination nodes


def billing_flow(state: State):
    return {"final": "Routing to billing department."}


def tech_flow(state: State):
    return {"final": "Routing to technical support flow."}


def sales_flow(state: State):
    return {"final": "Routing to sales workflow."}


# Write it up with conditional routing
builder = StateGraph()
builder.add_node("classify", classify_intent)
builder.add_node("route", routing_by_intent)
builder.add_node("billing", billing_flow)
builder.add_node("tech", tech_flow)
builder.add_node("sales", sales_flow)

builder.add_edge(START, "classify")
builder.add_conditional_edge("classify", routing_by_intent, {
    'billing': "billing",
    'tech': "tech",
    'sales': "sales"
})

builder.add_edge("billing", END)
builder.add_edge("tech", END)
builder.add_edge("sales", END)

graph = builder.compile()
