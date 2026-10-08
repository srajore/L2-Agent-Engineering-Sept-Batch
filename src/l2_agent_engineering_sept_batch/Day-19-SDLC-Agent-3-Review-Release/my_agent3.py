# AGENT FILE
"""Day 19: SDLC Agent 3 - review code, apply quality gates, prepare release, human approval."""

import json
import sys
from typing import TypedDict

import ollama
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


sys.stdout.reconfigure(encoding="utf-8")  # Windows cmd can crash on model punctuation

MODEL = "gpt-oss:120b-cloud"

# Input from Agent 2 (Day 18), shaped like a pull request. Hard-coded so Day 19 runs on its own.
PR_TITLE = "Add leave request validation"
PR_DESCRIPTION = "Adds validate_leave_request: checks dates, order and the employee's leave balance."
PR_DIFF = '''--- /dev/null
+++ b/leave.py
@@ -0,0 +1,13 @@
+import datetime
+
+def validate_leave_request(start_date: str, end_date: str, balance_days: int) -> tuple:
+    fmt = "%Y-%m-%d"
+    try:
+        start = datetime.datetime.strptime(start_date, fmt).date()
+        end = datetime.datetime.strptime(end_date, fmt).date()
+    except ValueError:
+        return False, "invalid date format"
+    if end < start:
+        return False, "end_date is before start_date"
+    days_requested = (end - start).days + 1
+    if days_requested > balance_days:
+        return False, "requested days exceed balance"
+    return True, ""
'''
# The code being reviewed is the added lines of the diff (lines starting with "+")
CODE = "\n".join(
    line[1:] for line in PR_DIFF.splitlines() if line.startswith("+") and not line.startswith("+++")
)
TESTS_PASSED = True

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
    approved = interrupt("Approve this release? (yes/no)")
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


graph_builder = StateGraph(ReleaseState)
graph_builder.add_node("review", review_code)
graph_builder.add_node("gates", apply_quality_gates)
graph_builder.add_node("release_notes", write_release_notes)
graph_builder.add_node("documentation", write_documentation)
graph_builder.add_node("approval", human_approval)
graph_builder.add_node("release", release)
graph_builder.add_node("stopped", stopped)
graph_builder.add_node("blocked", blocked)
graph_builder.add_edge(START, "review")
graph_builder.add_edge("review", "gates")
graph_builder.add_conditional_edges("gates", next_after_gates)
graph_builder.add_edge("release_notes", "documentation")
graph_builder.add_conditional_edges("documentation", next_after_documentation)
graph_builder.add_conditional_edges("approval", next_after_approval)
graph_builder.add_edge("release", END)
graph_builder.add_edge("stopped", END)
graph_builder.add_edge("blocked", END)
graph = graph_builder.compile(checkpointer=InMemorySaver())

if __name__ == "__main__":
    settings = {"configurable": {"thread_id": "agent-3"}}
    print(f"Reviewing PR: {PR_TITLE}")
    result = graph.invoke(
        {"title": PR_TITLE, "description": PR_DESCRIPTION, "diff": PR_DIFF, "code": CODE, "tests_passed": TESTS_PASSED},
        config=settings,
    )
    print("Review findings:")
    for finding in result["findings"] or [{"severity": "-", "issue": "none", "fix": ""}]:
        line = f" (line: {finding['line']})" if finding.get("line") else ""
        print(f" [{finding['severity']}] {finding['issue']}{line}")
    print("Quality gates:")
    for name, ok in result["gates"].items():
        print(f" {'PASS' if ok else 'FAIL'}  {name}")
    print("Verification debt (known, unresolved):", result["verification_debt"] or "none")

    if "__interrupt__" in result:
        print("\nChangelog:", result["changelog"])
        print("Release notes:", result["release_notes"])
        print("\nDocumentation:\n" + result["documentation"])
        answer = input("\nApprove this release? (yes/no): ")
        result = graph.invoke(Command(resume=answer.strip().lower() == "yes"), config=settings)

    print("\nStatus:", result["status"])

# REVIEWED BY RULE
