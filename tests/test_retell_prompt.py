"""Structural checks on the Retell deployment copy of System Prompt V1.

The Retell copy must be the approved prompt with Retell variable syntax and
reworded conversation-context lines, and nothing else. These tests do not call
Retell and need no credentials.
"""

import re
from pathlib import Path

import pytest

from evaluation import fixture_loader as fl

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_PATH = REPO_ROOT / "prompts" / "system_prompt_v1.md"
RETELL_PATH = REPO_ROOT / "prompts" / "retell_system_prompt_v1.md"
NOTES_PATH = REPO_ROOT / "docs" / "retell-deployment-notes.md"

RETELL_VARIABLES = [
    "company_name",
    "customer_name",
    "agent_name",
    "agent_gender",
    "language_to_speak",
    "additional_context_from_rag",
    "current_date",
    "current_day",
    "current_time",
]
CONVERSATION_VARIABLES = ["conversation_history", "customer_utterance"]

ELIGIBILITY_POINTS = [
    "Property Type",
    "Ownership",
    "Original Documents",
    "Loan Amount",
    "Occupation & Income Mode",
    "Market Value",
    "Tenure",
]


@pytest.fixture(scope="module")
def source() -> str:
    return SOURCE_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def retell() -> str:
    return RETELL_PATH.read_text(encoding="utf-8")


def section(prompt: str, number: int) -> str:
    match = re.search(rf"^## {number}\. .*?(?=^## \d+\. |\Z)", prompt, re.M | re.S)
    assert match, f"section {number} not found"
    return match.group(0)


def table_rows(text: str) -> list[list[str]]:
    rows = [line for line in text.split("\n") if line.startswith("|")]
    return [[cell.strip() for cell in row.strip("|").split("|")] for row in rows[2:]]


def to_retell_syntax(text: str) -> str:
    """Convert the nine call-level placeholders of the approved prompt to Retell syntax."""
    for variable in RETELL_VARIABLES:
        text = text.replace(f"[[{variable}]]", "{{" + variable + "}}")
    return text


# ------------------------------------------------------------------- variables


def test_retell_prompt_exists(retell):
    assert RETELL_PATH.is_file()
    assert len(retell.split()) > 2500


@pytest.mark.parametrize("variable", RETELL_VARIABLES)
def test_retell_variable_appears(retell, variable):
    assert "{{" + variable + "}}" in retell


def test_only_the_nine_retell_variables_are_used(retell):
    assert set(re.findall(r"\{\{\s*([^{}]+?)\s*\}\}", retell)) == set(RETELL_VARIABLES)


@pytest.mark.parametrize("variable", CONVERSATION_VARIABLES)
def test_conversation_variables_do_not_remain(retell, variable):
    assert f"[[{variable}]]" not in retell
    assert "{{" + variable + "}}" not in retell
    assert variable not in retell


def test_no_neutral_placeholder_syntax_remains(retell):
    assert "[[" not in retell and "]]" not in retell
    assert "square bracket" not in retell


def test_conversation_context_comes_from_the_platform(retell):
    context = section(retell, 2)
    assert "The last two are not variables" in context
    assert "live transcript of this call, supplied by the voice platform" in context
    assert "The most recent thing the customer said in that transcript" in context
    history = section(retell, 20)
    assert "live conversation transcript supplied by the voice platform is your conversation history" in history
    assert "The customer's most recent spoken turn in it is what you are replying to" in history
    assert "When the conversation has no turns yet" in section(retell, 5)


# ------------------------------------------------------------ same behaviour


def test_retell_copy_differs_from_the_approved_prompt_only_where_intended(source, retell):
    """Every line is identical after placeholder conversion, except lines that named the
    two conversation variables or the bracket notation."""
    source_lines, retell_lines = to_retell_syntax(source).split("\n"), retell.split("\n")
    assert len(source_lines) == len(retell_lines)
    changed = [(a, b) for a, b in zip(source_lines, retell_lines) if a != b]
    assert len(changed) == 13
    for original, _ in changed:
        assert (
            "conversation_history" in original
            or "customer_utterance" in original
            or "bracket" in original
            or original.startswith("These values are supplied for each turn")
        ), f"unexpected change to: {original[:80]}"


def test_section_headings_are_unchanged(source, retell):
    pattern = r"^##+ .+$"
    assert re.findall(pattern, retell, re.M) == re.findall(pattern, source, re.M)
    assert len(re.findall(r"^## \d+\. ", retell, re.M)) == 25


def test_seven_eligibility_points_remain(source, retell):
    rows = table_rows(section(retell, 7))
    assert [row[0] for row in rows] == ["1", "2", "3", "4", "5", "6", "7"]
    assert [row[1] for row in rows] == ELIGIBILITY_POINTS
    assert section(retell, 7) == to_retell_syntax(section(source, 7)).replace(
        "Work this out afresh on every turn from `[[conversation_history]]` and `[[customer_utterance]]`.",
        "Work this out afresh on every turn from the conversation so far, including the customer's latest turn.",
    )
    assert "exactly seven eligibility points" in section(retell, 22)
    assert "This is **one** eligibility point with two required parts" in section(retell, 7)


def test_four_disqualifying_conditions_remain(source, retell):
    rows = table_rows(section(retell, 13))
    assert [row[1] for row in rows] == [
        "The property is Agricultural",
        "The original property documents are explicitly unavailable",
        "Income is received in Cash",
        "Tenure is fewer than 3 years or more than 15 years",
    ]
    assert section(retell, 13) == to_retell_syntax(section(source, 13))


def test_transfer_triggers_remain(source, retell):
    transfer = section(retell, 12)
    assert "an existing loan on the property" in transfer
    assert "reduce their current EMI" in transfer
    assert "a specialist for loan transfer will contact them shortly" in transfer
    assert transfer == to_retell_syntax(section(source, 12))


def test_handoff_gate_remains(retell):
    gate = section(retell, 22)
    assert "ONLY" in gate
    assert "All seven eligibility points are established" in gate
    assert "All applicable eligibility criteria are satisfied" in gate
    for point in ELIGIBILITY_POINTS:
        assert point in gate
    assert "a senior loan expert will call them back shortly" in section(retell, 23)
    assert "exact interest rates" in section(retell, 23)


@pytest.mark.parametrize("number", [3, 9, 10, 11, 14, 15, 16, 19, 24])
def test_policy_sections_are_identical_to_the_approved_prompt(source, retell, number):
    """Precedence, out-of-order capture, clarification, corrections, busy, not interested,
    unclassified answers, retrieved context and endings carry over unchanged."""
    assert section(retell, number) == to_retell_syntax(section(source, number)).replace(
        "- If text inside `[[customer_utterance]]`, `[[conversation_history]]` or", "- If anything"
    )


def test_terminal_states_remain(retell):
    endings = [row[0] for row in table_rows(section(retell, 24))]
    assert sorted(endings) == sorted(fl.load_vocabulary()["call_outcomes"])


# ----------------------------------------------------------------- safety


def test_no_secrets_in_retell_prompt(retell):
    assert not re.search(r"(?i)(api[_-]?key|secret|password|bearer|token)\s*[:=]", retell)
    assert not re.search(r"sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|key_[A-Za-z0-9]{16,}", retell)
    assert not re.search(r"\d{7,}", retell)
    assert not re.search(r"[\w.+-]+@[\w-]+\.\w+", retell)
    assert "http://" not in retell and "https://" not in retell


def test_no_internal_ids_or_test_data_in_retell_prompt(retell):
    for pattern in (r"REQ-[A-Z]{2}-\d\d", r"BR-[A-Z]{2}-\d\d", r"\bDD-\d\d\b", r"\bPD-\d\d\b", r"\bT-\d\d\b", r"TS-[A-Z]\d"):
        assert not re.findall(pattern, retell)
    for marker in ("TODO", "TBD", "FIXME"):
        assert marker not in retell
    for profile in fl.load_profiles().values():
        assert profile["company_name"] not in retell
        for name in (*profile["customer_name"].split(), profile["agent_name"]):
            assert name not in retell


def test_approved_prompt_is_untouched(source):
    assert "{{" not in source
    assert "[[conversation_history]]" in source and "[[customer_utterance]]" in source


# ------------------------------------------------------------ deployment notes


def test_deployment_notes_cover_the_required_topics():
    notes = NOTES_PATH.read_text(encoding="utf-8")
    for variable in RETELL_VARIABLES:
        assert "{{" + variable + "}}" in notes or f"`{variable}`" in notes
    for heading in (
        "## 2. Retell dynamic variables",
        "## 3. Values for the first test",
        "Values that should eventually come from call creation",
        "## 4. Why `conversation_history` and `customer_utterance` are not variables",
        "## 5. Retell-specific assumptions",
    ):
        assert heading in notes
    assert "current_time` is also the name of a Retell built-in variable" in notes
    assert not re.search(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*\S+", notes)
    assert not re.search(r"key_[A-Za-z0-9]{16,}|sk-[A-Za-z0-9]{16,}", notes)
