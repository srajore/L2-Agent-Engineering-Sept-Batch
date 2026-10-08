# AGENT FILE
"""Day 18: SDLC Agent 2 - turn a design into code and tests, validate, refine, human review."""

import ast
import json
import subprocess
import sys
from datetime import datetime
from typing import TypedDict

import ollama
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


sys.stdout.reconfigure(encoding="utf-8")  # Windows cmd can crash on model punctuation

MODEL = "gpt-oss:120b-cloud"
MAX_TRIES = 3

# Input from Agent 1 (Day 17). Hard-coded here so Day 18 runs on its own.
STORY = (
    "As an employee, I want to submit a leave request, "
    "so that my manager can approve it. "
    "Given I have 5 days balance, when I request 3 days, then the request is accepted."
)
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
    approved = interrupt("Approve this code and tests? (yes/no)")
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


graph_builder = StateGraph(DevState)
graph_builder.add_node("generate_code", generate_code)
graph_builder.add_node("generate_tests", generate_tests)
graph_builder.add_node("generate_test_data", generate_test_data)
graph_builder.add_node("check_test_data", check_test_data)
graph_builder.add_node("validate", validate_artifacts)
graph_builder.add_node("explain", explain_code)
graph_builder.add_node("review", human_review)
graph_builder.add_node("finish", finish)
graph_builder.add_node("stop", stop_agent)
graph_builder.add_edge(START, "generate_tests")
graph_builder.add_edge("generate_tests", "generate_test_data")
graph_builder.add_edge("generate_test_data", "check_test_data")
graph_builder.add_conditional_edges("check_test_data", next_after_test_data)
graph_builder.add_edge("generate_code", "validate")
graph_builder.add_edge("explain", "review")
graph_builder.add_conditional_edges("validate", next_after_validation)
graph_builder.add_conditional_edges("review", next_after_review)
graph_builder.add_edge("finish", END)
graph_builder.add_edge("stop", END)
graph = graph_builder.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    settings = {"configurable": {"thread_id": "agent-2"}}
    result = graph.invoke({"story": STORY, "tries": 0}, config=settings)

    print("Generated code:\n" + result["code"])
    print("\nGenerated tests:\n" + result["tests"])
    print("\nTest data:")
    for case in result["test_data"]:
        print(f" {case['name']}: {case['start']} to {case['end']}, balance {case['balance']} -> valid={case['expect_valid']}")
    if result.get("explanation"):
        print("\nExplanation of the code:\n" + result["explanation"])
    print(f"\nValidation after {result['tries']} attempt(s): {result['test_output']}")

    if "__interrupt__" in result:
        answer = input("\nApprove this code and tests? (yes/no): ")
        result = graph.invoke(Command(resume=answer.strip().lower() == "yes"), config=settings)

    print("\nStatus:", result["status"])

    # Try this: ask Claude Code to add a rule that weekends do not count as leave days.

# REVIEWED BY RULE
