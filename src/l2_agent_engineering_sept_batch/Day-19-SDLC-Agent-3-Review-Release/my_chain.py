# AGENT FILE
"""Day 19 (part 2): the SDLC agent chain.

Agent 1 (Day 17, requirements) -> handoff -> Agent 2 (Day 18, code + tests) -> handoff
-> Agent 3 (Day 19, review + release). The node code of each agent is copied from
my_agent1.py, my_agent2.py and my_agent3.py. Each agent is its own compiled graph used as
one node of the parent graph. The parent stops if an agent does not finish successfully.
"""

import ast
import json
import re
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, List, TypedDict

import ollama
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


sys.stdout.reconfigure(encoding="utf-8")  # Windows cmd can crash on model punctuation

MODEL = "gpt-oss:120b-cloud"
MAX_TRIES = 3


# ================================================================ Agent 1: requirements -> design
class Agent1State(TypedDict, total=False):
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
    status: str


def number(state: Agent1State) -> Agent1State:
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


def analyze(state: Agent1State) -> Agent1State:
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


def validate(state: Agent1State) -> Agent1State:
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


def present(state: Agent1State) -> Agent1State:
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

def approval(state: Agent1State) -> Agent1State:
    """Ask the human for approval."""
    answer = interrupt("Approve these stories and criteria? (yes/no):")
    approved = answer is True or str(answer).strip().lower() == "yes"
    return {"approved": approved}


def design(state: Agent1State) -> Agent1State:
    """Create a short design description after human approval."""
    design_text = (
        "Design: A web-based leave-request system with a user portal for employees, "
        "an approval dashboard for managers, and secure backend storage."
    )
    print("\nStatus: Design ready")
    print(design_text)
    return {"design": design_text, "status": "Agent 1 done"}


def stop_requirements(state: Agent1State) -> Agent1State:
    """Handle stop conditions – validation failure or human rejection."""
    if not state.get("valid", True) and state.get("attempts", 0) >= 2:
        print("\nStatus: Stopped: validation failed after 2 attempts")
    elif state.get("approved") is False:
        print("\nStatus: Stopped: human rejected the stories")
    else:
        print("\nStatus: Stopped")
    return {"status": "Stopped in Agent 1"}

# ---------------------------------------------------------------------------
# Routing helpers for conditional edges
# ---------------------------------------------------------------------------

def route_validate(state: Agent1State) -> str:
    if state.get("valid"):
        return "valid"
    # Invalid – decide whether we can retry
    if state.get("attempts", 0) < 2:
        return "invalid_retry"
    return "invalid_stop"


def route_approval(state: Agent1State) -> str:
    return "yes" if state.get("approved") else "no"


agent_1 = StateGraph(Agent1State)
agent_1.add_node("number", number)
agent_1.add_node("analyze", analyze)
agent_1.add_node("validate", validate)
agent_1.add_node("present", present)
agent_1.add_node("approval", approval)
agent_1.add_node("design", design)
agent_1.add_node("stopped", stop_requirements)
agent_1.add_edge(START, "number")
agent_1.add_edge("number", "analyze")
agent_1.add_edge("analyze", "validate")
agent_1.add_conditional_edges(
    "validate",
    route_validate,
    {"valid": "present", "invalid_retry": "analyze", "invalid_stop": "stopped"},
)
agent_1.add_edge("present", "approval")
agent_1.add_conditional_edges("approval", route_approval, {"yes": "design", "no": "stopped"})
agent_1.add_edge("design", END)
agent_1.add_edge("stopped", END)
agent1_graph = agent_1.compile()


# ================================================================ Handoff 1 -> 2

def handoff_to_developer(state):
    """Agent 1's stories and design become Agent 2's user story."""
    story = " ".join(s["text"] for s in state["stories"]) + " " + state["design"]
    note = f"Agent 1 -> Agent 2: {len(state['stories'])} stories and a design"
    return {"story": story, "tries": 0, "approved": False, "handoffs": state.get("handoffs", []) + [note]}


# ================================================================ Agent 2: design -> code -> test
SPEC = """Write ONE Python function exactly named:
def validate_leave_request(start_date: str, end_date: str, balance_days: int) -> tuple:
Dates use the format YYYY-MM-DD. Days requested = (end - start) + 1, counted inclusively.
Return (True, "") when the request is valid.
Return (False, "<reason>") when end_date is before start_date,
or when days requested is more than balance_days."""

class DevState(TypedDict, total=False):
    story: str
    code: str
    tests: str
    test_data: list
    test_data_problem: str
    data_tries: int
    explanation: str
    test_output: str
    passed: bool
    tries: int
    approved: bool
    status: str


def clean_code(text):
    """Remove markdown fences the model sometimes adds around code."""
    text = text.strip()
    text = text.removeprefix("```python").removeprefix("```").removesuffix("```")
    return text.strip()


def generate_code(state):
    prompt = f"""{SPEC}

User story: {state["story"]}
Return ONLY Python code. No explanation, no markdown, no example calls."""
    if state.get("code") and state.get("tests") and not state.get("passed", True):
        prompt += f"""

Your previous code failed these tests. Fix it.
Previous code:
{state["code"]}
Test failure:
{state["test_output"]}
Tests that must pass:
{state["tests"]}"""

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return {
        "code": clean_code(response["message"]["content"]),
        "tries": state.get("tries", 0) + 1,
    }


def generate_tests(state):
    prompt = f"""{SPEC}

Write 5 test cases for this function as plain `assert` statements.
The function already exists and will be placed above your tests: do NOT define it,
do NOT copy it, do NOT import it. No pytest. Only call validate_leave_request(...).
For invalid requests assert only the first value, for example
`assert validate_leave_request(a, b, 5)[0] is False`; never assert the reason text.
Include test data for: a valid request, exactly equal to balance, over balance,
and end date before start date.
Return ONLY Python code.
User story: {state["story"]}"""

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return {"tests": clean_code(response["message"]["content"])}


def generate_test_data(state):
    """Model step: a table of test cases (the data), separate from the assert statements."""
    prompt = f"""{SPEC}

Return ONLY a JSON list of 5 to 8 test cases for this function. Each case has exactly:
{{"name": "short label", "start": "YYYY-MM-DD", "end": "YYYY-MM-DD", "balance": 5, "expect_valid": true}}
Cover: a valid request, a request exactly equal to the balance, one over the balance,
and one where the end date is before the start date. Use only real calendar dates."""
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response["message"]["content"].strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        cases = json.loads(text)
    except json.JSONDecodeError:
        cases = []
    return {"test_data": cases, "data_tries": state.get("data_tries", 0) + 1}


def check_test_data(state):
    """Deterministic check of the test data: enough cases, both outcomes, real dates."""
    cases = state["test_data"]
    problem = ""
    if not isinstance(cases, list) or len(cases) < 4:
        problem = "need at least 4 test cases as a JSON list"
    else:
        outcomes = set()
        for case in cases:
            try:
                int(case["balance"])
                expect_valid = bool(case["expect_valid"])
                outcomes.add(expect_valid)
                for key in ("start", "end"):
                    try:
                        datetime.strptime(case[key], "%Y-%m-%d")
                    except ValueError:
                        # an unreal date is only allowed in a case that expects an invalid result
                        if expect_valid:
                            raise
            except (KeyError, TypeError, ValueError):
                problem = "a test case is missing a field or has a bad date"
                break
        if not problem and outcomes != {True, False}:
            problem = "test data must include both valid and invalid cases"
    return {"test_data_problem": problem}


def next_after_test_data(state):
    if not state["test_data_problem"]:
        return "generate_code"
    if state["data_tries"] < MAX_TRIES:
        return "generate_test_data"
    return "stop"


def explain_code(state):
    """Model step: explain the final code in plain English for the human reviewer."""
    prompt = f"""Explain this Python function in 3 to 6 short plain-English lines for a
non-programmer. Say what it checks and what it returns in each case.
{state["code"]}"""
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return {"explanation": response["message"]["content"].strip()}


def validate_artifacts(state):
    """Deterministic validation: parse both files, then run the tests in a child process."""
    try:
        ast.parse(state["code"])
        test_tree = ast.parse(state["tests"])
    except SyntaxError as error:
        return {"passed": False, "test_output": f"SyntaxError: {error}"}

    # Guard against a vacuous pass: tests must call the real function, not redefine it.
    defined = [n.name for n in ast.walk(test_tree) if isinstance(n, ast.FunctionDef)]
    asserts = [n for n in ast.walk(test_tree) if isinstance(n, ast.Assert)]
    if "validate_leave_request" in defined or len(asserts) < 4:
        return {
            "passed": False,
            "test_output": "Tests must not define the function and need at least 4 asserts",
            "tests": "",
        }

    # The test data table is run against the code as well as the assert statements.
    data_check = (
        f"\nfor case in {state['test_data']!r}:\n"
        "    ok = validate_leave_request(case['start'], case['end'], int(case['balance']))[0]\n"
        "    assert ok is bool(case['expect_valid']), 'test data case failed: ' + case['name']\n"
    )
    script = state["code"] + "\n\n" + state["tests"] + data_check + "\nprint('ALL TESTS PASSED')"
    try:
        run = subprocess.run(
            [sys.executable, "-c", script], capture_output=True, text=True, timeout=15
        )
    except subprocess.TimeoutExpired:
        return {"passed": False, "test_output": "Timed out after 15 seconds"}

    if run.returncode == 0:
        return {"passed": True, "test_output": run.stdout.strip()}
    return {"passed": False, "test_output": run.stderr.strip()[-600:]}


def next_after_validation(state):
    if state["passed"]:
        return "explain"
    if state["tries"] >= MAX_TRIES:
        return "stop"
    if state["tests"] == "":
        return "generate_tests"  # the tests were unusable, so rewrite them
    return "generate_code"  # the code failed the tests, so refine the code


def human_review(state):
    data_lines = "\n".join(
        f" {c['name']}: {c['start']} to {c['end']}, balance {c['balance']} -> valid={c['expect_valid']}"
        for c in state["test_data"]
    )
    shown = (
        "AGENT 2 - Generated code:\n" + state["code"]
        + "\n\nGenerated tests:\n" + state["tests"]
        + "\n\nTest data:\n" + data_lines
        + "\n\nExplanation of the code:\n" + state["explanation"]
        + "\n\nValidation after " + str(state["tries"]) + " attempt(s): " + state["test_output"]
        + "\n\nApprove this code and tests? (yes/no)"
    )
    approved = interrupt(shown)
    return {"approved": approved}


def next_after_review(state):
    return "finish" if state["approved"] else "stop"


def finish(state):
    return {"status": "Code and tests approved"}


def stop_agent(state):
    if state.get("test_data_problem"):
        return {"status": "Stopped: could not produce valid test data"}
    if state["passed"]:
        return {"status": "Stopped: human rejected the code"}
    return {"status": "Stopped: tests still failing after retries"}


agent_2 = StateGraph(DevState)
agent_2.add_node("generate_code", generate_code)
agent_2.add_node("generate_tests", generate_tests)
agent_2.add_node("generate_test_data", generate_test_data)
agent_2.add_node("check_test_data", check_test_data)
agent_2.add_node("validate", validate_artifacts)
agent_2.add_node("explain", explain_code)
agent_2.add_node("review", human_review)
agent_2.add_node("finish", finish)
agent_2.add_node("stop", stop_agent)
agent_2.add_edge(START, "generate_tests")
agent_2.add_edge("generate_tests", "generate_test_data")
agent_2.add_edge("generate_test_data", "check_test_data")
agent_2.add_conditional_edges("check_test_data", next_after_test_data)
agent_2.add_edge("generate_code", "validate")
agent_2.add_edge("explain", "review")
agent_2.add_conditional_edges("validate", next_after_validation)
agent_2.add_conditional_edges("review", next_after_review)
agent_2.add_edge("finish", END)
agent_2.add_edge("stop", END)
agent2_graph = agent_2.compile()


# ================================================================ Handoff 2 -> 3

def handoff_to_reviewer(state):
    """Agent 2's code is packaged as a pull request (title, description, diff of added lines)."""
    code_lines = state["code"].splitlines()
    added = "\n".join("+" + line for line in code_lines)
    diff = f"--- /dev/null\n+++ b/leave.py\n@@ -0,0 +1,{len(code_lines)} @@\n" + added
    note = f"Agent 2 -> Agent 3: pull request with {len(code_lines)} added lines, tests passed = {state['passed']}"
    return {
        "title": "Add leave request validation",
        "description": state["req_text"],
        "diff": diff,
        "tests_passed": state["passed"],
        "approved": False,
        "handoffs": state.get("handoffs", []) + [note],
    }


# ================================================================ Agent 3: review -> release
FORBIDDEN_CALLS = ["eval(", "exec(", "os.system(", "TODO"]

class ReleaseState(TypedDict, total=False):
    title: str
    description: str
    diff: str
    code: str
    tests_passed: bool
    documentation: str
    docs_tries: int
    findings: list
    gates: dict
    verification_debt: list
    changelog: str
    release_notes: str
    approved: bool
    status: str


def review_code(state):
    """Model step: review a pull request (title, description and diff) and return findings."""
    prompt = f"""You are a strict code reviewer. Review this pull request.
Title: {state["title"]}
Description: {state["description"]}
Diff (lines starting with + were added):
{state["diff"]}

Return ONLY a JSON list. Each item: {{"severity": "HIGH" | "MEDIUM" | "LOW", "issue": "...", "line": "the added line it refers to", "fix": "..."}}.
HIGH means: crashes or gives a wrong result for input that matches the type annotations, or a security flaw.
Inputs that break the type annotations (None, wrong types) are at most MEDIUM.
MEDIUM means: a likely bug for unusual input. LOW means: style or readability.
Return [] when there is nothing to report."""

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response["message"]["content"].strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        findings = json.loads(text)
    except json.JSONDecodeError:
        # An unreadable review must never count as a clean review.
        findings = [{"severity": "HIGH", "issue": "Review output was not valid JSON", "fix": "Re-run the review"}]

    return {"findings": findings}


def apply_quality_gates(state):
    """Deterministic gates: plain Python decides, not the model."""
    severities = [str(f.get("severity", "")).upper() for f in state["findings"]]
    gates = {
        "tests passed": state["tests_passed"],
        "no HIGH findings": "HIGH" not in severities,
        "no forbidden calls": not any(call in state["code"] for call in FORBIDDEN_CALLS),
    }
    debt = [f["issue"] for f in state["findings"] if str(f.get("severity", "")).upper() != "HIGH"]
    return {"gates": gates, "verification_debt": debt}


def next_after_gates(state):
    return "release_notes" if all(state["gates"].values()) else "blocked"


def write_documentation(state):
    """Model step: short user documentation for the change."""
    prompt = f"""Write short documentation for this code in markdown with exactly these four headings:
## Purpose
## Parameters
## Returns
## Example
Code:
{state["code"]}"""
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return {
        "documentation": response["message"]["content"].strip(),
        "docs_tries": state.get("docs_tries", 0) + 1,
    }


def next_after_documentation(state):
    """Deterministic check: all four headings and the function name must be present."""
    docs = state["documentation"]
    complete = all(h in docs for h in ("## Purpose", "## Parameters", "## Returns", "## Example"))
    if complete and "validate_leave_request" in docs:
        return "approval"
    if state["docs_tries"] < 2:
        return "documentation"
    return "blocked"


def write_release_notes(state):
    prompt = f"""Write release material for this change.
Code:
{state["code"]}
Use exactly this layout:
CHANGELOG: one line starting with "Added"
RELEASE NOTES: two or three plain sentences for non-technical readers."""

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response["message"]["content"].strip()
    changelog, _, notes = text.partition("RELEASE NOTES:")
    return {
        "changelog": changelog.replace("CHANGELOG:", "").strip(),
        "release_notes": notes.strip(),
    }


def human_approval(state):
    finding_lines = "\n".join(
        f" [{f['severity']}] {f['issue']}" + (f" (line: {f['line']})" if f.get("line") else "")
        for f in state["findings"]
    ) or " none"
    gate_lines = "\n".join(f" {'PASS' if ok else 'FAIL'}  {name}" for name, ok in state["gates"].items())
    shown = (
        "AGENT 3 - Reviewing PR: " + state["title"]
        + "\n\nReview findings:\n" + finding_lines
        + "\n\nQuality gates:\n" + gate_lines
        + "\n\nVerification debt (known, unresolved): " + str(state["verification_debt"] or "none")
        + "\n\nChangelog: " + state["changelog"]
        + "\nRelease notes: " + state["release_notes"]
        + "\n\nDocumentation:\n" + state["documentation"]
        + "\n\nApprove this release? (yes/no)"
    )
    approved = interrupt(shown)
    return {"approved": approved}


def next_after_approval(state):
    return "release" if state["approved"] else "stopped"


def release(state):
    return {"status": "Released"}


def stopped(state):
    return {"status": "Stopped: human declined the release"}


def blocked(state):
    failed = [name for name, ok in state["gates"].items() if not ok]
    if not failed:
        failed = ["documentation incomplete"]
    return {"status": "Blocked by quality gates: " + ", ".join(failed)}


agent_3 = StateGraph(ReleaseState)
agent_3.add_node("review", review_code)
agent_3.add_node("gates", apply_quality_gates)
agent_3.add_node("release_notes", write_release_notes)
agent_3.add_node("documentation", write_documentation)
agent_3.add_node("approval", human_approval)
agent_3.add_node("release", release)
agent_3.add_node("stopped", stopped)
agent_3.add_node("blocked", blocked)
agent_3.add_edge(START, "review")
agent_3.add_edge("review", "gates")
agent_3.add_conditional_edges("gates", next_after_gates)
agent_3.add_edge("release_notes", "documentation")
agent_3.add_conditional_edges("documentation", next_after_documentation)
agent_3.add_conditional_edges("approval", next_after_approval)
agent_3.add_edge("release", END)
agent_3.add_edge("stopped", END)
agent_3.add_edge("blocked", END)
agent3_graph = agent_3.compile()


# ================================================================ Parent graph

class ChainState(TypedDict, total=False):
    # shared with Agent 1
    req_text: str
    sentences: List[Dict[str, Any]]
    stories: List[Dict[str, Any]]
    criteria: List[Dict[str, Any]]
    questions: List[str]
    func_reqs: List[str]
    nonfunc_reqs: List[str]
    design: str
    attempts: int
    valid: bool
    # shared with Agent 2
    story: str
    code: str
    tests: str
    test_data: list
    test_data_problem: str
    data_tries: int
    explanation: str
    test_output: str
    passed: bool
    tries: int
    # shared with Agent 3
    title: str
    description: str
    diff: str
    tests_passed: bool
    documentation: str
    docs_tries: int
    findings: list
    gates: dict
    verification_debt: list
    changelog: str
    release_notes: str
    # shared by all
    approved: bool
    status: str
    handoffs: list


def stop_chain_agent1(state):
    return {"status": "Stopped in Agent 1"}


def stop_chain_agent2(state):
    return {"status": "Stopped in Agent 2"}


def continue_if_done(done_status):
    def route(state):
        return "continue" if state.get("status") == done_status else "end"
    return route


parent = StateGraph(ChainState)
parent.add_node("agent1", agent1_graph)
parent.add_node("handoff_to_developer", handoff_to_developer)
parent.add_node("agent2", agent2_graph)
parent.add_node("handoff_to_reviewer", handoff_to_reviewer)
parent.add_node("agent3", agent3_graph)
parent.add_node("stop_chain_agent1", stop_chain_agent1)
parent.add_node("stop_chain_agent2", stop_chain_agent2)
parent.add_edge(START, "agent1")
parent.add_conditional_edges(
    "agent1",
    continue_if_done("Agent 1 done"),
    {"continue": "handoff_to_developer", "end": "stop_chain_agent1"},
)
parent.add_edge("handoff_to_developer", "agent2")
parent.add_conditional_edges(
    "agent2",
    continue_if_done("Code and tests approved"),
    {"continue": "handoff_to_reviewer", "end": "stop_chain_agent2"},
)
parent.add_edge("handoff_to_reviewer", "agent3")
parent.add_edge("agent3", END)
parent.add_edge("stop_chain_agent1", END)
parent.add_edge("stop_chain_agent2", END)
chain = parent.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "chain-1"}}
    result = chain.invoke({}, config=config)
    while "__interrupt__" in result:
        print("\n" + str(result["__interrupt__"][0].value))
        answer = input("Approve? (yes/no): ")
        result = chain.invoke(Command(resume=answer.strip().lower() == "yes"), config=config)

    if result["status"].startswith("Blocked"):
        print("\nAGENT 3 - Reviewing PR:", result["title"])
        for f in result["findings"]:
            print(f" [{f['severity']}] {f['issue']}")
        for name, ok in result["gates"].items():
            print(f" {'PASS' if ok else 'FAIL'}  {name}")

    print("\nHandoffs:")
    for note in result.get("handoffs", []):
        print(" -", note)
    print("Final status:", result["status"])

# REVIEWED BY RULE
