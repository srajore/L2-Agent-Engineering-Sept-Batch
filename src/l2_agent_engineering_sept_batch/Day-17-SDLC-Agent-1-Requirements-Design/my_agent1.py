"""my_agent1.py - Requirements Analyst LangGraph agent

This file implements a LangGraph StateGraph that turns a sample requirement
into user stories, acceptance criteria, clarifying questions, functional and
non-functional requirements, and a short design. The graph includes human
approval via `interrupt` and `Command`.
"""

from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command, interrupt
import re

# ---------------------------------------------------------------------------
# State definition
# ---------------------------------------------------------------------------
class State(TypedDict, total=False):
    req_text: str
    sentences: List[Dict[str, Any]]  # each with id and text
    stories: List[Dict[str, Any]]   # each with id, req_id, text
    criteria: List[Dict[str, Any]]  # each with story_id, given, when, then
    questions: List[str]
    func_reqs: List[str]
    nonfunc_reqs: List[str]
    design: str
    approved: bool
    attempts: int
    valid: bool

# ---------------------------------------------------------------------------
# Node implementations
# ---------------------------------------------------------------------------

def number(state: State) -> State:
    """Provide the sample requirement and split it into sentences.
    The sample requirement is hard-coded as required by the spec.
    """
    requirement = (
        "Employees can request leave online. "
        "Managers approve or reject the request quickly. "
        "The system must be secure and easy to use."
    )
    # Split on period, keep trailing period for clarity
    raw_sentences = [s.strip() for s in requirement.split('.') if s.strip()]
    sentences = []
    for idx, txt in enumerate(raw_sentences, start=1):
        sentences.append({"id": f"R{idx}", "text": txt + "."})
    return {
        "req_text": requirement,
        "sentences": sentences,
        "attempts": 0,
        "stories": [],
        "criteria": [],
        "questions": [],
        "func_reqs": [],
        "nonfunc_reqs": [],
    }


def analyze(state: State) -> State:
    """Parse each sentence, split actions on "and"/"or", and build
    stories, acceptance criteria, clarifying questions, functional and
    non-functional requirement lists.
    """
    stories: List[Dict[str, Any]] = []
    criteria: List[Dict[str, Any]] = []
    questions: List[str] = []
    func_reqs: List[str] = []
    nonfunc_reqs: List[str] = []
    story_counter = 1

    for sent in state["sentences"]:
        text = sent["text"]
        # One clarifying question per sentence (placeholder)
        questions.append(f"Can you clarify: {text}")

        # Split actions on logical conjunctions (case-insensitive)
        actions = re.split(r"\s+(?:and|or)\s+", text, flags=re.IGNORECASE)
        # Strip punctuation for each action
        actions = [a.strip().rstrip('.') for a in actions if a.strip()]

        # Build a story per action
        for action in actions:
            story_id = f"US-{story_counter}"
            story_text = f"As a stakeholder I want {action} so that the requirement is met."
            stories.append({"id": story_id, "req_id": sent["id"], "text": story_text})
            # Simple acceptance criteria template
            criteria.append({
                "story_id": story_id,
                "given": f"Given the system knows the {action}",
                "when": f"When the user performs {action}",
                "then": f"Then the expected outcome occurs"
            })
            story_counter += 1

        # Functional requirements – each action is a functional item
        func_reqs.extend([action.capitalize() for action in actions])

        # Non-functional – look for "must be" patterns and "easy to" wording
        nf_matches = re.findall(r"must be ([^.]+)", text, flags=re.IGNORECASE)
        for nf in nf_matches:
            nonfunc_reqs.append(nf.strip().capitalize())
        if re.search(r"easy to", text, flags=re.IGNORECASE):
            nonfunc_reqs.append("Usability")

    # Deduplicate while preserving order
    func_reqs = list(dict.fromkeys(func_reqs))
    nonfunc_reqs = list(dict.fromkeys(nonfunc_reqs))

    return {
        "stories": stories,
        "criteria": criteria,
        "questions": questions,
        "func_reqs": func_reqs,
        "nonfunc_reqs": nonfunc_reqs,
    }


def validate(state: State) -> State:
    """Validate the generated artefacts and record success/failure.
    The spec limits to two analysis attempts.
    """
    attempts = state.get("attempts", 0) + 1
    state["attempts"] = attempts
    valid = True

    # 1. Every story must start with "As a"
    for s in state.get("stories", []):
        if not s["text"].startswith("As a"):
            valid = False
            break

    # 2. Each criterion needs given/when/then
    for c in state.get("criteria", []):
        if not (c.get("given") and c.get("when") and c.get("then")):
            valid = False
            break

    # 3. Each requirement ID must appear in at least one story
    req_ids_in_stories = {s["req_id"] for s in state.get("stories", [])}
    expected_ids = {sent["id"] for sent in state.get("sentences", [])}
    if req_ids_in_stories != expected_ids:
        valid = False

    # 4. Sentences containing "and"/"or" need ≥2 stories
    for sent in state.get("sentences", []):
        if re.search(r"\b(and|or)\b", sent["text"], flags=re.IGNORECASE):
            count = sum(1 for s in state["stories"] if s["req_id"] == sent["id"])
            if count < 2:
                valid = False
                break

    # 5. At least one clarifying question
    if not state.get("questions"):
        valid = False

    # 6. Functional and non-functional lists must be non-empty
    if not state.get("func_reqs") or not state.get("nonfunc_reqs"):
        valid = False

    state["valid"] = valid
    return state


def present(state: State) -> State:
    """Print artefacts before human approval."""
    print("Clarifying questions for the stakeholder:")
    for q in state.get("questions", []):
        print("- " + q)

    print("\nUser stories:")
    for s in state.get("stories", []):
        print(f"{s['id']} ({s['req_id']}): {s['text']}")

    print("\nFunctional requirements:")
    for fr in state.get("func_reqs", []):
        print("- " + fr)

    print("\nNon-functional requirements:")
    for nfr in state.get("nonfunc_reqs", []):
        print("- " + nfr)

    return state

def approval(state: State) -> State:
    """Ask the human for approval."""
    answer = interrupt("Approve these stories and criteria? (yes/no):")
    approved = str(answer).strip().lower() == "yes"
    return {"approved": approved}


def design(state: State) -> State:
    """Create a short design description after human approval."""
    design_text = (
        "Design: A web-based leave-request system with a user portal for employees, "
        "an approval dashboard for managers, and secure backend storage."
    )
    print("\nStatus: Design ready")
    print(design_text)
    return {"design": design_text}


def stopped(state: State) -> State:
    """Handle stop conditions – validation failure or human rejection."""
    if not state.get("valid", True) and state.get("attempts", 0) >= 2:
        print("\nStatus: Stopped: validation failed after 2 attempts")
    elif state.get("approved") is False:
        print("\nStatus: Stopped: human rejected the stories")
    else:
        print("\nStatus: Stopped")
    return {}

# ---------------------------------------------------------------------------
# Routing helpers for conditional edges
# ---------------------------------------------------------------------------

def route_validate(state: State) -> str:
    if state.get("valid"):
        return "valid"
    # Invalid – decide whether we can retry
    if state.get("attempts", 0) < 2:
        return "invalid_retry"
    return "invalid_stop"


def route_approval(state: State) -> str:
    return "yes" if state.get("approved") else "no"

# ---------------------------------------------------------------------------
# Build the graph
# ---------------------------------------------------------------------------
builder = StateGraph(State)
builder.add_node("number", number)
builder.add_node("analyze", analyze)
builder.add_node("validate", validate)
builder.add_node("present", present)
builder.add_node("approval", approval)
builder.add_node("design", design)
builder.add_node("stopped", stopped)

builder.add_edge(START, "number")
builder.add_edge("number", "analyze")
builder.add_edge("analyze", "validate")
builder.add_conditional_edges(
    "validate",
    route_validate,
    {
        "valid": "present",
        "invalid_retry": "analyze",
        "invalid_stop": "stopped",
    },
)
builder.add_edge("present", "approval")
builder.add_conditional_edges(
    "approval",
    route_approval,
    {"yes": "design", "no": "stopped"},
)
builder.add_edge("design", END)
builder.add_edge("stopped", END)

graph = builder.compile(checkpointer=InMemorySaver())

# ---------------------------------------------------------------------------
# Run the graph with the sample requirement when executed directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "t1"}}
    # Start with an empty state – the graph's nodes will initialise it.
    result = graph.invoke({}, config=config)

    # The graph pauses at the approval node; ask the human, then resume.
    if "__interrupt__" in result:
        answer = input("\nApprove these stories and criteria? (yes/no): ")
        graph.invoke(Command(resume=answer.strip().lower()), config=config)
