"""Load and validate the synthetic evaluation fixtures.

This module reads the YAML fixtures in ``evaluation/fixtures/`` and checks them
against each other and against the specification in ``docs/``. It is test
infrastructure only: it does not implement the voice agent and it does not
decide eligibility for a real conversation. The eligible and disqualifying
values it uses are read from ``vocabulary.yaml``, which repeats the values
named in ``docs/business-rules.md``.

Run ``python -m evaluation.fixture_loader`` to validate the fixtures.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = REPO_ROOT / "evaluation" / "fixtures"
DOCS_DIR = REPO_ROOT / "docs"

DEFAULT_PROFILE = "default_en"
PROFILE_VARIABLES = (
    "company_name",
    "customer_name",
    "agent_name",
    "agent_gender",
    "current_date",
    "current_day",
    "current_time",
    "additional_context_from_rag",
    "language_to_speak",
)
SCENARIO_KEYS = {"id", "title", "basis", "profile", "rag_context", "start", "customer_turns", "expected"}
START_KEYS = {"state", "identity_verified", "offer_presented", "answered", "pending", "clarified", "control", "notes"}
EXPECTED_KEYS = {
    "end_state",
    "call_outcome",
    "fields",
    "optional_fields",
    "control",
    "next_pending",
    "transitions",
    "must",
    "must_not",
}


# --------------------------------------------------------------------- loading


def load_yaml(name: str) -> dict:
    with (FIXTURES_DIR / name).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_vocabulary() -> dict:
    return load_yaml("vocabulary.yaml")


def load_profiles() -> dict:
    return load_yaml("profiles.yaml")["profiles"]


def load_scenarios() -> list[dict]:
    return load_yaml("scenarios.yaml")["scenarios"]


def scenario_variables(scenario: dict, profiles: dict) -> dict:
    """Prompt variables for a scenario: its profile, with any RAG override applied."""
    variables = dict(profiles[scenario.get("profile", DEFAULT_PROFILE)])
    if "rag_context" in scenario:
        variables["additional_context_from_rag"] = scenario["rag_context"]
    return variables


def final_fields(scenario: dict) -> dict:
    """Field values expected at the end of a scenario (start values plus changes)."""
    return {**scenario["start"].get("answered", {}), **scenario["expected"].get("fields", {})}


# --------------------------------------------------------------- specification


def _read_doc(name: str) -> str:
    return (DOCS_DIR / name).read_text(encoding="utf-8")


def documented_transitions() -> dict[str, tuple[set[str], str | None]]:
    """Transition ID -> (states it can be taken from, state it leads to).

    Read from the transition tables in docs/conversation-state-model.md (the
    six-column rows: ID, From, To, Condition, Action, Rule). An empty "from"
    set means the call start; a target of None means "same state".
    """
    transitions: dict[str, tuple[set[str], str | None]] = {}
    for line in _read_doc("conversation-state-model.md").split("\n"):
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 6 and re.fullmatch(r"T-\d\d", cells[0]):
            target = re.findall(r"`([A-Z_]+)`", cells[2])
            transitions[cells[0]] = (set(re.findall(r"`([A-Z_]+)`", cells[1])), target[0] if target else None)
    return transitions


def documented_ids() -> dict:
    """IDs defined in docs/, by kind, plus the transition table under "transitions"."""
    transitions = documented_transitions()
    return {
        "TS": set(re.findall(r"^### (TS-[A-Z]\d)", _read_doc("test-scenarios.md"), re.M)),
        "T": set(transitions),
        "DD": set(re.findall(r"^## (DD-\d\d) ", _read_doc("design-decisions.md"), re.M)),
        "PD": set(re.findall(r"^### (PD-\d\d) ", _read_doc("system-prompt-architecture.md"), re.M)),
        "BR": set(re.findall(r"BR-[A-Z]{2}-\d\d[a-z]?", _read_doc("business-rules.md"))),
        "transitions": transitions,
    }


def documented_scenarios() -> dict[str, str]:
    """Scenario ID -> the text of its section in docs/test-scenarios.md."""
    blocks = re.split(r"^### (?=TS-[A-Z]\d)", _read_doc("test-scenarios.md"), flags=re.M)[1:]
    return {block[:5]: block for block in blocks}


# ------------------------------------------------------------------ validation


def classify_value(field: str, value, vocabulary: dict) -> str:
    """Classify a fixture value as eligible, disqualifying, over_limit or unclassified."""
    spec = vocabulary["fields"][field]
    if spec["type"] == "category":
        if value in spec["eligible"]:
            return "eligible"
        if value in spec["disqualifying"]:
            return "disqualifying"
        return "unclassified"
    numbers = [value["min"], value["max"]] if isinstance(value, dict) else [value]
    if not all(isinstance(n, (int, float)) and not isinstance(n, bool) and n > 0 for n in numbers):
        return "unclassified"
    if spec["type"] == "years":
        in_range = all(spec["minimum"] <= n <= spec["maximum"] for n in numbers)
        return "eligible" if in_range else "disqualifying"
    if "maximum" in spec and max(numbers) > spec["maximum"]:
        return "over_limit"
    return "eligible"


def _unknown(values, allowed) -> list:
    return sorted(set(values) - set(allowed))


def tracked_item(start: dict, vocabulary: dict) -> str | None:
    """The item the clarification limit applies to at the start of a scenario (PD-01).

    Inside a branch it is that branch's required response; otherwise it is the
    pending field. A tracked item is bookkeeping for counting clarifications.
    It is never an eligibility point, and plays no part in the handoff check.
    """
    for name, spec in vocabulary["branch_responses"].items():
        if spec["state"] == start["state"]:
            return name
    return start["pending"]


def walk_transitions(start_state: str, transition_ids: list[str], transitions: dict) -> tuple[str, list[str]]:
    """Follow transitions from a starting state. Returns (state reached, problems)."""
    state, problems = start_state, []
    for transition_id in transition_ids:
        sources, target = transitions[transition_id]
        if not sources:  # the call-start transition
            if state != target:
                problems.append(f"{transition_id} starts a call, but the scenario starts in {state}")
            continue
        if state not in sources:
            problems.append(f"{transition_id} cannot be taken from {state}")
        state = target or state
    return state, problems


def validate_scenario(scenario: dict, vocabulary: dict, profiles: dict, docs: dict) -> list[str]:
    """Return a list of problems with one scenario (empty if it is valid)."""
    sid = scenario.get("id", "<no id>")
    errors: list[str] = []

    def problem(message: str) -> None:
        errors.append(f"{sid}: {message}")

    for key in ("id", "title", "basis", "start", "customer_turns", "expected"):
        if key not in scenario:
            problem(f"missing key '{key}'")
    if errors:
        return errors
    start, expected = scenario["start"], scenario["expected"]
    for label, mapping, allowed in (
        ("scenario", scenario, SCENARIO_KEYS),
        ("start", start, START_KEYS),
        ("expected", expected, EXPECTED_KEYS),
    ):
        if _unknown(mapping, allowed):
            problem(f"unknown {label} keys {_unknown(mapping, allowed)}")
    for key in ("end_state", "call_outcome", "fields", "next_pending", "transitions", "must", "must_not"):
        if key not in expected:
            problem(f"expected is missing '{key}'")
    for key in ("state", "identity_verified", "offer_presented", "answered", "pending"):
        if key not in start:
            problem(f"start is missing '{key}'")
    if errors:
        return errors

    states, fields = vocabulary["states"], vocabulary["fields"]
    outcome = expected["call_outcome"]

    # Vocabulary
    if scenario.get("profile", DEFAULT_PROFILE) not in profiles:
        problem(f"unknown profile '{scenario.get('profile')}'")
    for state in (start["state"], expected["end_state"]):
        if state not in states:
            problem(f"unknown state '{state}'")
    if outcome is not None and outcome not in vocabulary["call_outcomes"]:
        problem(f"unknown call_outcome '{outcome}'")
    pending = [start["pending"]] if start["pending"] else []
    next_pending = expected["next_pending"] or []
    next_pending = next_pending if isinstance(next_pending, list) else [next_pending]
    field_names = [
        *start["answered"],
        *expected["fields"],
        *expected.get("optional_fields", {}),
        *pending,
        *next_pending,
    ]
    if _unknown(field_names, fields):
        problem(f"unknown fields {_unknown(field_names, fields)}")
    trackable = set(fields) | set(vocabulary["branch_responses"])
    if _unknown(start.get("clarified", []), trackable):
        problem(f"unknown clarified items {_unknown(start.get('clarified', []), trackable)}")
    for label in ("must", "must_not"):
        if _unknown(expected[label], vocabulary["behaviours"]):
            problem(f"unknown {label} behaviours {_unknown(expected[label], vocabulary['behaviours'])}")
    if set(expected["must"]) & set(expected["must_not"]):
        problem(f"behaviours both required and forbidden: {sorted(set(expected['must']) & set(expected['must_not']))}")
    controls = {**start.get("control", {}), **expected.get("control", {})}
    if _unknown(controls, vocabulary["control_fields"]):
        problem(f"unknown control fields {_unknown(controls, vocabulary['control_fields'])}")
    if "transfer_reason" in controls and controls["transfer_reason"] not in vocabulary["transfer_reasons"]:
        problem(f"unknown transfer_reason '{controls['transfer_reason']}'")
    if errors:
        return errors

    # Links to the specification
    if sid not in docs["TS"]:
        problem("not defined in docs/test-scenarios.md")
    if _unknown(expected["transitions"], docs["T"]):
        problem(f"unknown transitions {_unknown(expected['transitions'], docs['T'])}")
    basis = scenario["basis"]
    if basis != "source":
        if not isinstance(basis, list) or not basis:
            problem("basis must be 'source' or a non-empty list of DD and PD ids")
        elif _unknown(basis, docs["DD"] | docs["PD"]):
            problem(f"unknown design decisions {_unknown(basis, docs['DD'] | docs['PD'])}")

    # Customer turns
    turns = scenario["customer_turns"]
    if not turns or not all(isinstance(turn, str) and turn.strip() for turn in turns):
        problem("customer_turns must be a non-empty list of utterances")

    # Internal consistency
    is_terminal = states[expected["end_state"]].get("terminal", False)
    if is_terminal != (outcome is not None):
        problem("call_outcome must be set exactly when end_state is the terminal state")
    if is_terminal and next_pending:
        problem("a terminated call cannot have a next_pending point")
    if not start["identity_verified"] and (start["offer_presented"] or start["answered"]):
        problem("offer presented or answers captured before identity verification")
    if start["pending"] in start["answered"]:
        problem(f"pending point '{start['pending']}' is already answered at the start")

    # The listed transitions must form a documented path from start to end
    if not _unknown(expected["transitions"], docs["T"]):
        reached, path_problems = walk_transitions(start["state"], expected["transitions"], docs["transitions"])
        for path_problem in path_problems:
            problem(path_problem)
        if reached != expected["end_state"]:
            problem(f"transitions lead to {reached}, but end_state is {expected['end_state']}")

    final = final_fields(scenario)
    classes = {name: classify_value(name, value, vocabulary) for name, value in final.items()}
    for name in set(next_pending) & set(final):
        if len(next_pending) == 1:
            problem(f"next_pending '{name}' is already answered")
    for name, value in final.items():
        if classes[name] == "unclassified":
            problem(f"captured value {value!r} for '{name}' is not a classified value (DD-06)")
    if classes.get("loan_amount") == "over_limit":
        problem("a loan amount above 75 Lakhs must never be recorded as the answer (BR-EL-04a)")

    disqualifying = sorted(name for name, kind in classes.items() if kind == "disqualifying")
    if outcome == "DISQUALIFIED" and not disqualifying:
        problem("DISQUALIFIED without a disqualifying value: no criterion was failed")
    if disqualifying and outcome not in ("DISQUALIFIED", "TRANSFER"):
        problem(f"disqualifying value in {disqualifying} but outcome is {outcome}")
    if outcome == "QUALIFIED":
        missing = sorted(set(fields) - set(final))
        not_eligible = sorted(name for name, kind in classes.items() if kind != "eligible")
        if missing or not_eligible:
            problem(f"QUALIFIED requires all points answered and eligible; missing {missing}, not eligible {not_eligible}")

    # Behaviours and transitions must agree with the outcome
    messages = {
        "QUALIFIED": "handoff_message",
        "DISQUALIFIED": "disqualification_message",
        "TRANSFER": "transfer_message",
    }
    # A scenario that starts inside an exit path has already taken its transition.
    starts_in_flow = start["state"] not in ("DISQUALIFICATION", "LOAN_TRANSFER", "QUALIFIED_HANDOFF", "NO_QUALIFICATION_CLOSE")
    for result, spec in vocabulary["call_outcomes"].items():
        if messages.get(result) in expected["must"] and outcome != result:
            problem(f"'{messages[result]}' required but outcome is {outcome}")
        if starts_in_flow and (spec["transition"] in expected["transitions"]) != (outcome == result):
            problem(f"{spec['transition']} must appear exactly when outcome is {result}")
    if ("transfer_reason" in expected.get("control", {})) != (outcome == "TRANSFER"):
        problem("transfer_reason must be recorded exactly when outcome is TRANSFER")

    # PD-01: exactly one clarification or re-ask per tracked item
    clarification_used = tracked_item(start, vocabulary) in start.get("clarified", [])
    if {"T-20", "T-21"} & set(expected["transitions"]) and clarification_used:
        problem("a second clarification for the same tracked item is not allowed (PD-01)")
    if "T-25" in expected["transitions"] and not clarification_used:
        problem("INCOMPLETE requires that the one clarification for the tracked item was already used (PD-01)")

    # PD-03: closings
    if starts_in_flow and outcome in vocabulary["closings_with_thanks"] and "thank_customer" not in expected["must"]:
        problem(f"a {outcome} closing must require 'thank_customer' (PD-03)")
    if outcome == "INCOMPLETE" and "explain_information_not_established" not in expected["must"]:
        problem("an INCOMPLETE closing must require 'explain_information_not_established' (PD-03)")
    if outcome is not None and "end_call" not in expected["must"]:
        problem("a terminated call must require 'end_call'")
    return errors


def validate_fixtures() -> list[str]:
    """Validate every fixture file. Returns a list of problems (empty if valid)."""
    vocabulary, profiles, scenarios, docs = load_vocabulary(), load_profiles(), load_scenarios(), documented_ids()
    errors: list[str] = []

    for name, profile in profiles.items():
        if set(profile) != set(PROFILE_VARIABLES):
            errors.append(f"profile {name}: variables differ from the assignment's list")
        if profile.get("language_to_speak") not in vocabulary["languages"]:
            errors.append(f"profile {name}: unknown language")
    for name, spec in vocabulary["fields"].items():
        if spec["rule"] not in docs["BR"]:
            errors.append(f"vocabulary field {name}: unknown rule {spec['rule']}")
    for name, spec in vocabulary["behaviours"].items():
        if spec["ref"] not in docs["BR"]:
            errors.append(f"vocabulary behaviour {name}: unknown rule {spec['ref']}")
    for name, spec in vocabulary["call_outcomes"].items():
        if spec["origin"] == "design" and spec.get("decision") not in docs["DD"]:
            errors.append(f"vocabulary outcome {name}: unknown decision {spec.get('decision')}")
        if spec.get("transition") not in docs["T"]:
            errors.append(f"vocabulary outcome {name}: unknown transition {spec.get('transition')}")
    for name, spec in vocabulary["branch_responses"].items():
        if name in vocabulary["fields"]:
            errors.append(f"branch response {name} must not be an eligibility field")
        if spec["state"] not in vocabulary["states"] or spec["rule"] not in docs["BR"]:
            errors.append(f"branch response {name}: unknown state or rule")

    ids = Counter(scenario.get("id") for scenario in scenarios)
    errors += [f"duplicate scenario id {sid}" for sid, count in ids.items() if count > 1]
    errors += [f"{sid}: documented but has no fixture" for sid in sorted(docs["TS"] - set(ids))]
    for scenario in scenarios:
        errors += validate_scenario(scenario, vocabulary, profiles, docs)
    return errors


def main() -> int:
    errors = validate_fixtures()
    scenarios = load_scenarios()
    outcomes = Counter(s["expected"]["call_outcome"] or "call continues" for s in scenarios)
    print(f"{len(scenarios)} scenarios, {len(load_profiles())} profiles")
    for outcome, count in sorted(outcomes.items()):
        print(f"  {outcome}: {count}")
    for error in errors:
        print(f"ERROR {error}")
    print("fixtures valid" if not errors else f"{len(errors)} problem(s) found")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
