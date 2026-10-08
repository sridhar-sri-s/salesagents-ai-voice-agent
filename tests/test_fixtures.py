"""Checks that the synthetic evaluation fixtures are valid and match the specification.

These tests cover the fixtures only. They do not exercise a voice agent.
"""

import copy
import re

import pytest

from evaluation import fixture_loader as fl

VOCABULARY = fl.load_vocabulary()
PROFILES = fl.load_profiles()
SCENARIOS = fl.load_scenarios()
DOC_IDS = fl.documented_ids()
DOC_SCENARIOS = fl.documented_scenarios()

by_id = pytest.mark.parametrize("scenario", SCENARIOS, ids=[s["id"] for s in SCENARIOS])


def test_fixtures_are_valid():
    assert fl.validate_fixtures() == []


def test_every_documented_scenario_has_exactly_one_fixture():
    assert sorted(s["id"] for s in SCENARIOS) == sorted(DOC_IDS["TS"])


@by_id
def test_customer_turns_match_the_document(scenario):
    documented = DOC_SCENARIOS[scenario["id"]]
    for turn in scenario["customer_turns"]:
        assert f'"{turn}"' in documented
    assert len(scenario["customer_turns"]) == len(re.findall(r'"[^"\n]+"', _utterance_lines(documented)))


def _utterance_lines(block: str) -> str:
    """The part of a scenario section that holds the customer's words."""
    lines = block.split("\n")
    start = next(i for i, line in enumerate(lines) if "Customer utterance" in line)
    end = next(i for i, line in enumerate(lines) if "Expected agent behaviour" in line)
    return "\n".join(lines[start:end])


@by_id
def test_basis_matches_the_document(scenario):
    basis_line = re.search(r"^- \*\*Basis:\*\*(.*)$", DOC_SCENARIOS[scenario["id"]], re.M)
    documented = sorted(set(re.findall(r"(?:DD|PD)-\d\d", basis_line.group(1)))) if basis_line else []
    declared = [] if scenario["basis"] == "source" else sorted(scenario["basis"])
    assert declared == documented


WITH_RAG_TEXT = [s for s in SCENARIOS if s.get("rag_context")]


@pytest.mark.parametrize("scenario", WITH_RAG_TEXT, ids=[s["id"] for s in WITH_RAG_TEXT])
def test_rag_fixture_text_matches_the_document(scenario):
    assert f'"{scenario["rag_context"]}"' in DOC_SCENARIOS[scenario["id"]]


@by_id
def test_scenario_is_valid(scenario):
    assert fl.validate_scenario(scenario, VOCABULARY, PROFILES, DOC_IDS) == []


def test_disqualified_fixtures_use_only_the_four_documented_criteria():
    failed_by = {}
    for scenario in SCENARIOS:
        if scenario["expected"]["call_outcome"] == "DISQUALIFIED":
            values = fl.final_fields(scenario)
            failed = {n for n, v in values.items() if fl.classify_value(n, v, VOCABULARY) == "disqualifying"}
            assert failed, scenario["id"]
            failed_by[scenario["id"]] = failed
    criteria = set().union(*failed_by.values())
    assert criteria == {"property_type", "documents_available", "income_mode", "tenure_years"}
    tenures = {fl.final_fields(s)["tenure_years"] for s in SCENARIOS if "tenure_years" in failed_by.get(s["id"], ())}
    assert any(t < 3 for t in tenures) and any(t > 15 for t in tenures)


def test_each_outcome_is_reached_only_by_its_documented_transition():
    for scenario in SCENARIOS:
        outcome, start_state = scenario["expected"]["call_outcome"], scenario["start"]["state"]
        if outcome and start_state != "DISQUALIFICATION":
            assert VOCABULARY["call_outcomes"][outcome]["transition"] in scenario["expected"]["transitions"]
    exercised = {s["expected"]["call_outcome"] for s in SCENARIOS} - {None}
    assert exercised == set(VOCABULARY["call_outcomes"])


def test_transition_table_is_read_from_the_state_model():
    transitions = fl.documented_transitions()
    assert len(transitions) == 28
    assert transitions["T-12"] == ({"ELIGIBILITY_COLLECTION"}, "QUALIFIED_HANDOFF")
    assert [t for t, (_, target) in transitions.items() if target == "QUALIFIED_HANDOFF"] == ["T-12"]
    assert [t for t, (_, target) in transitions.items() if target == "DISQUALIFICATION"] == ["T-10"]


def test_all_customer_data_is_synthetic():
    assert fl.load_yaml("profiles.yaml")["synthetic"] is True
    assert fl.load_yaml("scenarios.yaml")["synthetic"] is True
    for path in sorted(fl.FIXTURES_DIR.glob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"\d{7,}", text), f"{path.name} contains a long digit sequence"
        assert not re.search(r"[\w.+-]+@[\w-]+\.\w+", text), f"{path.name} contains an email address"
        assert not re.search(r"(?i)(api[_-]?key|token|password|secret)\s*[:=]", text), f"{path.name} looks like it holds a credential"


def test_profiles_supply_the_assignment_variables():
    assert fl.DEFAULT_PROFILE in PROFILES
    for profile in PROFILES.values():
        assert set(profile) == set(fl.PROFILE_VARIABLES)
    languages = {profile["language_to_speak"] for profile in PROFILES.values()}
    assert languages == {"English", "Hindi"}


def test_scenario_variables_apply_rag_override():
    with_rag = next(s for s in SCENARIOS if s.get("rag_context"))
    variables = fl.scenario_variables(with_rag, PROFILES)
    assert variables["additional_context_from_rag"] == with_rag["rag_context"]
    assert variables["company_name"] == "Home Credit"


def test_vocabulary_holds_only_the_documented_eligibility_values():
    """Guards against a new eligibility criterion entering through the fixtures."""
    fields = VOCABULARY["fields"]
    disqualifying = {name: spec["disqualifying"] for name, spec in fields.items() if spec.get("disqualifying")}
    assert disqualifying == {
        "property_type": ["Agricultural"],
        "documents_available": ["unavailable"],
        "income_mode": ["Cash"],
    }
    assert (fields["tenure_years"]["minimum"], fields["tenure_years"]["maximum"]) == (3, 15)
    assert fields["loan_amount"]["maximum"] == 75
    assert not {"minimum", "maximum"} & set(fields["market_value"])
    assert "minimum" not in fields["loan_amount"]
    assert sorted({spec["point"] for spec in fields.values()}) == [1, 2, 3, 4, 5, 6, 7]


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("property_type", "Industrial", "eligible"),
        ("property_type", "Agricultural", "disqualifying"),
        ("property_type", "Plot", "unclassified"),
        ("occupation", "Retired", "unclassified"),
        ("income_mode", "Cash", "disqualifying"),
        ("loan_amount", 75, "eligible"),
        ("loan_amount", 76, "over_limit"),
        ("market_value", 5, "eligible"),
        ("market_value", {"min": 80, "max": 85}, "eligible"),
        ("tenure_years", 3, "eligible"),
        ("tenure_years", 15, "eligible"),
        ("tenure_years", 2, "disqualifying"),
        ("tenure_years", 16, "disqualifying"),
    ],
)
def test_classify_value(field, value, expected):
    assert fl.classify_value(field, value, VOCABULARY) == expected


def _scenario(scenario_id):
    return copy.deepcopy(next(s for s in SCENARIOS if s["id"] == scenario_id))


def _problems(scenario):
    return fl.validate_scenario(scenario, VOCABULARY, PROFILES, DOC_IDS)


def test_validation_rejects_handoff_with_a_point_unanswered():
    scenario = _scenario("TS-G2")
    del scenario["start"]["answered"]["market_value"]
    assert any("QUALIFIED requires" in problem for problem in _problems(scenario))


def test_validation_rejects_disqualification_without_a_failed_criterion():
    scenario = _scenario("TS-W2")
    scenario["expected"]["call_outcome"] = "DISQUALIFIED"
    assert any("no criterion was failed" in problem for problem in _problems(scenario))


def test_validation_rejects_a_recorded_amount_above_the_limit():
    scenario = _scenario("TS-E1")
    scenario["expected"]["fields"]["loan_amount"] = 100
    assert any("above 75 Lakhs" in problem for problem in _problems(scenario))


def test_validation_rejects_continuing_after_a_disqualifying_value():
    scenario = _scenario("TS-A2")
    scenario["expected"]["fields"]["property_type"] = "Agricultural"
    assert any("disqualifying value" in problem for problem in _problems(scenario))


def test_validation_rejects_a_transition_that_cannot_be_taken():
    scenario = _scenario("TS-A2")
    scenario["expected"]["transitions"] = ["T-09"]
    assert any("T-09 cannot be taken from ELIGIBILITY_COLLECTION" in problem for problem in _problems(scenario))


def test_validation_rejects_an_end_state_the_transitions_do_not_reach():
    scenario = _scenario("TS-C1")
    scenario["expected"]["transitions"] = ["T-10"]
    assert any("transitions lead to DISQUALIFICATION" in problem for problem in _problems(scenario))


def test_validation_rejects_a_transfer_without_a_documented_trigger():
    scenario = _scenario("TS-M1")
    del scenario["expected"]["control"]["transfer_reason"]
    assert any("transfer_reason must be recorded" in problem for problem in _problems(scenario))
    scenario = _scenario("TS-M1")
    scenario["expected"]["control"]["transfer_reason"] = "has_other_loans"
    assert any("unknown transfer_reason" in problem for problem in _problems(scenario))


def test_validation_keeps_no_qualification_outcomes_apart_from_disqualification():
    scenario = _scenario("TS-V3")
    scenario["expected"]["must_not"].remove("disqualification_message")
    scenario["expected"]["must"].append("disqualification_message")
    assert any("'disqualification_message' required but outcome is INCOMPLETE" in p for p in _problems(scenario))
    scenario = _scenario("TS-U1")
    scenario["expected"]["transitions"] = ["T-25", "T-19"]
    assert any("T-18 must appear exactly when outcome is NOT_INTERESTED" in p for p in _problems(scenario))


def test_validation_enforces_the_clarification_limit():
    second_clarification = _scenario("TS-V1")
    second_clarification["start"]["clarified"] = ["property_type"]
    assert any("second clarification" in problem for problem in _problems(second_clarification))
    premature_close = _scenario("TS-W2")
    premature_close["start"]["clarified"] = []
    assert any("one clarification for the tracked item" in problem for problem in _problems(premature_close))


def test_clarification_tracking_never_adds_an_eligibility_point():
    """The handoff gate is exactly seven points; tracked items are bookkeeping (PD-01)."""
    fields, branch = VOCABULARY["fields"], VOCABULARY["branch_responses"]
    assert sorted({spec["point"] for spec in fields.values()}) == [1, 2, 3, 4, 5, 6, 7]
    assert [name for name, spec in fields.items() if spec["point"] == 5] == ["occupation", "income_mode"]
    assert not set(branch) & set(fields)
    for scenario in SCENARIOS:
        if scenario["expected"]["call_outcome"] == "QUALIFIED":
            assert set(fl.final_fields(scenario)) == set(fields)
        assert not set(branch) & set(fl.final_fields(scenario))


def test_point_five_needs_both_sub_values():
    partial = _scenario("TS-I3")
    assert "occupation" in partial["start"]["answered"] and "income_mode" not in fl.final_fields(partial)
    assert partial["expected"]["call_outcome"] == "INCOMPLETE"
    qualified = _scenario("TS-G2")
    del qualified["start"]["answered"]["income_mode"]
    assert any("QUALIFIED requires" in problem for problem in _problems(qualified))


def test_maximum_confirmation_is_tracked_as_a_branch_response():
    first, second = _scenario("TS-E4"), _scenario("TS-E5")
    assert fl.tracked_item(first["start"], VOCABULARY) == "proceed_with_maximum"
    assert "loan_amount" not in fl.final_fields(first) and "loan_amount" not in fl.final_fields(second)
    assert first["expected"]["end_state"] == "LOAN_AMOUNT_LIMIT_CONFIRMATION"
    assert second["expected"]["call_outcome"] == "INCOMPLETE"
    second["start"]["clarified"] = []
    assert any("one clarification for the tracked item" in problem for problem in _problems(second))
    unknown = _scenario("TS-E5")
    unknown["start"]["clarified"] = ["eighth_point"]
    assert any("unknown clarified items" in problem for problem in _problems(unknown))


def test_validation_requires_the_documented_closing():
    no_thanks = _scenario("TS-C1")
    no_thanks["expected"]["must"].remove("thank_customer")
    assert any("must require 'thank_customer'" in problem for problem in _problems(no_thanks))
    no_explanation = _scenario("TS-V3")
    no_explanation["expected"]["must"].remove("explain_information_not_established")
    assert any("explain_information_not_established" in problem for problem in _problems(no_explanation))


def test_competing_signals_follow_the_documented_precedence():
    expected = {"TS-M3": "TRANSFER", "TS-Z1": "TRANSFER", "TS-Z2": "DISQUALIFIED", "TS-Z3": "DISQUALIFIED",
                "TS-Z4": "NOT_INTERESTED", "TS-Z5": "TRANSFER"}
    for scenario_id, outcome in expected.items():
        scenario = _scenario(scenario_id)
        assert scenario["expected"]["call_outcome"] == outcome
        assert "ask_callback_time" not in scenario["expected"]["must"]


def test_validation_rejects_unknown_references():
    scenario = _scenario("TS-A2")
    scenario["expected"]["transitions"] = ["T-99"]
    scenario["basis"] = ["DD-99"]
    problems = _problems(scenario)
    assert any("unknown transitions" in problem for problem in problems)
    assert any("unknown design decisions" in problem for problem in problems)
