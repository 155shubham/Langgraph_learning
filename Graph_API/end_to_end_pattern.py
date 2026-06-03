import json
from typing  import TypedDict
from pydantic import BaseModel, ValidationError

class State(TypedDict):
    question: str
    draft_raw: str
    draft:str

class DraftModel(BaseModel):
    draft: str

def generate_draft(state: State):
    # Pretend this is the LLM output (must be json)
    raw = '{"draft": "This is a draft answer"}'
    return {"draft_raw": raw}

def validate_and_update(state: State):
    try:
        obj = json.loads(state["draft_raw"])
        parsed = DraftModel.model_validate(obj)
        return {"draft": parsed.draft}
    except (json.JSONDecodeError, ValidationError) as e:
        # In a real graph you would route to a repair node
        return {"draft": "Invalid draft format"}