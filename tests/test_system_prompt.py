"""Structural checks on System Prompt V1 and its traceability document.

These tests confirm that required content is present and that nothing internal
or sensitive leaked into the prompt. They do not judge the quality of the
wording, and they do not run the prompt against a model.
"""

import re
from pathlib import Path

import pytest

from evaluation import fixture_loader as fl

REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = REPO_ROOT / "prompts" / "system_prompt_v1.md"
TRACE_PATH = REPO_ROOT / "docs" / "system-prompt-traceability.md"

RUNTIME_VARIABLES = [
    "company_name",
    "customer_name",
    "agent_name",
    "agent_gender",
    "current_date",
    "current_day",
    "current_time",
    "additional_context_from_rag",
    "language_to_speak",
    "conversation_history",
    "customer_utterance",
]

SECTIONS = [
    "ROLE AND OBJECTIVE",
    "RUNTIME CONTEXT",
    "PRIORITY / PRECEDENCE",
    "IDENTITY VERIFICATION",
    "GREETING",
    "OFFER PRESENTATION",
    "ELIGIBILITY STATE",
    "SEQUENTIAL COLLECTION",
    "OUT-OF-ORDER CAPTURE",
    "INTERNAL CLARIFICATION MODEL",
    "CORRECTIONS",
    "TRANSFER",
    "DISQUALIFICATION",
    "BUSY / CALLBACK",
    "NOT INTERESTED",
    "UNKNOWN / UNCLASSIFIED ANSWERS",
    "LANGUAGE",
    "AGENT GENDER",
    "RAG",
    "CONVERSATION HISTORY",
    "NATURAL CONVERSATION",
    "HANDOFF GATE",
    "QUALIFIED HANDOFF",
    "TERMINAL STATES",
    "FINAL RESPONSE POLICY",
]

ELIGIBILITY_POINTS = [
    "Property Type",
    "Ownership",
    "Original Documents",
    "Loan Amount",
    "Occupation & Income Mode",
    "Market Value",
    "Tenure",
]

ID_PATTERNS = {
    "REQ": r"REQ-[A-Z]{2}-\d\d",
    "BR": r"BR-[A-Z]{2}-\d\d[a-z]?",
    "DD": r"\bDD-\d\d\b",
    "PD": r"\bPD-\d\d\b",
    "T": r"\bT-\d\d\b",
    "TS": r"TS-[A-Z]\d",
    "PS": r"PS-\d\d",
}


@pytest.fixture(scope="module")
def prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def trace() -> str:
    return TRACE_PATH.read_text(encoding="utf-8")


def section(prompt: str, number: int) -> str:
    """The text of one numbered top-level section of the prompt."""
    match = re.search(rf"^## {number}\. .*?(?=^## \d+\. |\Z)", prompt, re.M | re.S)
    assert match, f"section {number} not found"
    return match.group(0)


def table_rows(text: str) -> list[list[str]]:
    """Body rows of the first markdown table in a block of text."""
    rows = [line for line in text.split("\n") if line.startswith("|")]
    return [[cell.strip() for cell in row.strip("|").split("|")] for row in rows[2:]]


# ------------------------------------------------------------------ the prompt


def test_prompt_file_exists_and_is_substantial(prompt):
    assert PROMPT_PATH.is_file()
    assert len(prompt.split()) > 2500


def test_prompt_has_the_25_sections_in_order(prompt):
    headings = re.findall(r"^## (\d+)\. (.+)$", prompt, re.M)
    assert [int(number) for number, _ in headings] == list(range(1, 26))
    assert [title for _, title in headings] == SECTIONS


@pytest.mark.parametrize("variable", RUNTIME_VARIABLES)
def test_runtime_variable_appears(prompt, variable):
    assert f"[[{variable}]]" in prompt
    assert f"[[{variable}]]" in section(prompt, 1) + section(prompt, 2)


def test_only_known_placeholders_are_used(prompt):
    used = set(re.findall(r"\[\[(\w+)\]\]", prompt))
    assert used == set(RUNTIME_VARIABLES)
    assert "{{" not in prompt and "}}" not in prompt
    assert not re.search(r"<[a-z_]+>", prompt)


def test_exactly_seven_eligibility_points(prompt):
    rows = table_rows(section(prompt, 7))
    assert [row[0] for row in rows] == ["1", "2", "3", "4", "5", "6", "7"]
    assert [row[1] for row in rows] == ELIGIBILITY_POINTS
    assert "exactly seven eligibility points" in section(prompt, 7)
    assert "exactly seven eligibility points" in section(prompt, 10)
    assert "exactly seven eligibility points" in section(prompt, 22)
    assert "not** an eighth eligibility point" in section(prompt, 7)


def test_eligibility_values_match_the_specification(prompt):
    rows = {row[1]: row for row in table_rows(section(prompt, 7))}
    fields = fl.load_vocabulary()["fields"]
    for value in fields["property_type"]["eligible"]:
        assert value in rows["Property Type"][3]
    assert "Agricultural" in rows["Property Type"][4]
    assert "Sole" in rows["Ownership"][3] and "Joint" in rows["Ownership"][3]
    assert "75 Lakhs or less" in rows["Loan Amount"][3]
    assert "Salaried" in rows["Occupation & Income Mode"][3] and "Self-Employed" in rows["Occupation & Income Mode"][3]
    assert "Bank" in rows["Occupation & Income Mode"][3] and "Cash" in rows["Occupation & Income Mode"][4]
    assert "3 through 15 years inclusive" in rows["Tenure"][3]
    assert (fields["tenure_years"]["minimum"], fields["tenure_years"]["maximum"]) == (3, 15)
    assert fields["loan_amount"]["maximum"] == 75


def test_the_four_disqualifying_categories_and_no_others(prompt):
    rows = table_rows(section(prompt, 13))
    assert len(rows) == 4
    answers = " | ".join(row[1] for row in rows)
    assert "Agricultural" in answers
    assert "original property documents are explicitly unavailable" in answers
    assert "Cash" in answers
    assert "fewer than 3 years or more than 15 years" in answers
    assert "The only disqualifying answers" in section(prompt, 13)
    assert "only disqualifying answers are the four" in section(prompt, 3)


def test_market_value_and_ownership_never_disqualify(prompt):
    eligibility = section(prompt, 7)
    assert "MUST NOT apply any threshold" in eligibility
    assert "It can never disqualify" in eligibility
    assert "There is no minimum amount" in eligibility
    rows = {row[1]: row for row in table_rows(eligibility)}
    assert "No disqualifying answer exists" in rows["Market Value"][4]
    assert "No disqualifying answer exists" in rows["Ownership"][4]


def test_loan_amount_above_limit_is_not_a_disqualification(prompt):
    eligibility = section(prompt, 7)
    assert "explain that the maximum under this offer is 75 Lakhs" in eligibility
    assert "proceed with the maximum allowed amount" in eligibility
    assert "MUST NOT disqualify them for asking" in eligibility
    assert "Disqualify for a loan amount above 75 Lakhs" in section(prompt, 13)


def test_transfer_triggers_and_message(prompt):
    transfer = section(prompt, 12)
    assert "an existing loan on the property" in transfer
    assert "reduce their current EMI" in transfer
    assert "a specialist for loan transfer will contact them shortly" in transfer
    assert "Continue the fresh-loan eligibility questions" in transfer
    assert "Word it as a disqualification" in transfer
    assert "clearly indicate" in transfer
    assert "Infer a trigger from unrelated discussion" in transfer
    assert "low EMI on this new loan" not in transfer


def test_handoff_gate(prompt):
    gate = section(prompt, 22)
    assert "ONLY" in gate
    assert "All seven eligibility points are established" in gate
    assert "All applicable eligibility criteria are satisfied" in gate
    assert "No ending has been reached" in gate
    assert "No required clarification remains unresolved" in gate
    for point in ELIGIBILITY_POINTS:
        assert point in gate
    handoff = section(prompt, 23)
    assert "a senior loan expert will call them back shortly" in handoff
    assert "exact interest rates" in handoff


def test_approved_precedence_order(prompt):
    precedence = section(prompt, 3)
    ranked = re.findall(r"^\d\. \*\*([A-Z_ /]+)\*\*", precedence, re.M)
    assert ranked == ["TRANSFER", "DISQUALIFICATION", "NOT_INTERESTED", "BUSY / CALLBACK", "NORMAL ELIGIBILITY FLOW"]
    assert "highest-ranked" in precedence
    assert "Never give two" in precedence


def test_clarification_model(prompt):
    model = section(prompt, 10)
    assert "initial attempt" in model
    assert "exactly one" in model
    assert "INCOMPLETE" in model
    assert "does **not** use it up" in model
    assert "usable answer always wins" in model
    assert (
        "The assignment has exactly seven eligibility points. Internal tracking may count sub-values separately "
        "for clarification purposes, but those sub-values do not create additional eligibility points." in model
    )


def test_identity_before_offer(prompt):
    identity = section(prompt, 4)
    assert "MUST confirm" in identity
    assert "Mention a loan, an offer, an amount" in identity
    assert "date of birth" in identity
    greeting = section(prompt, 5)
    assert "Do not mention a loan or an offer in the greeting" in greeting
    assert "only after identity is confirmed" in section(prompt, 6)
    assert "up to 75 Lakhs" in section(prompt, 6)


def test_rag_cannot_override_eligibility(prompt):
    rag = section(prompt, 19)
    assert "this prompt wins" in rag
    assert "create a new eligibility criterion" in rag
    assert "exact interest rate" in rag
    assert "MUST NOT let `[[additional_context_from_rag]]` change, relax or add to the eligibility criteria" in section(prompt, 3)


def test_every_terminal_state_is_listed(prompt):
    endings = [row[0] for row in table_rows(section(prompt, 24))]
    assert sorted(endings) == sorted(fl.load_vocabulary()["call_outcomes"])


def test_no_placeholder_text_left_behind(prompt):
    for marker in ("TODO", "TBD", "FIXME", "XXX", "lorem ipsum", "PLACEHOLDER", "???"):
        assert marker.lower() not in prompt.lower(), marker


def test_no_secrets_in_prompt(prompt):
    assert not re.search(r"(?i)(api[_-]?key|secret|password|bearer|token)\s*[:=]", prompt)
    assert not re.search(r"sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}", prompt)
    assert not re.search(r"\d{7,}", prompt)
    assert not re.search(r"[\w.+-]+@[\w-]+\.\w+", prompt)
    assert "http://" not in prompt and "https://" not in prompt


def test_no_internal_ids_or_platform_names_in_prompt(prompt):
    for kind, pattern in ID_PATTERNS.items():
        assert not re.findall(pattern, prompt), f"{kind} ID found in the prompt"
    assert not re.search(r"\b(AMB|GF|INV)-\d", prompt)
    for name in ("Retell", "Bolna", "Twilio"):
        assert name.lower() not in prompt.lower()
    # State-model labels are internal. (GREETING is also an ordinary section title, so only
    # the compound labels are checked.)
    for state in fl.load_vocabulary()["states"]:
        if "_" in state:
            assert state not in prompt, f"internal state name {state} found in the prompt"


def test_no_synthetic_test_data_in_prompt(prompt):
    for profile in fl.load_profiles().values():
        assert profile["company_name"] not in prompt
        for name in (*profile["customer_name"].split(), profile["agent_name"]):
            assert name not in prompt, f"sample name {name} found in the prompt"


def test_every_turn_check_has_no_dead_ends(prompt):
    """Paths that span two turns must be picked up again on the second turn."""
    checks = section(prompt, 3).split("### 3.4")[1]
    assert "First, always take in everything the customer just said" in checks
    assert "act on the first one that applies" in checks
    assert "Did you ask for a callback time in your previous reply?" in checks
    assert "waiting for the customer's reply about the maximum allowed amount" in checks
    steps = re.findall(r"^(\d+)\. \*\*", checks, re.M)
    assert steps == [str(n) for n in range(1, 12)]
    order = [checks.index(label) for label in ("TRANSFER signal", "DISQUALIFICATION signal", "NOT_INTERESTED signal", "BUSY signal")]
    assert order == sorted(order)


def test_language_is_not_switched_on_request(prompt):
    assert "or asks you to switch" in section(prompt, 17)


# ------------------------------------------------------------ the traceability


def test_traceability_covers_every_prompt_section(prompt, trace):
    prompt_headings = re.findall(r"^## (\d+)\. (.+)$", prompt, re.M)
    trace_headings = re.findall(r"^### (\d+)\. (.+)$", trace, re.M)
    assert trace_headings == prompt_headings
    for number, _ in trace_headings:
        block = re.search(rf"^### {number}\. .*?(?=^### \d+\. |^## |\Z)", trace, re.M | re.S).group(0)
        for label in ("**REQ:**", "**BR:**", "**DD:**", "**PD:**", "**T:**", "**TS:**"):
            assert label in block, f"section {number} is missing {label}"


def test_traceability_references_resolve(trace):
    docs = fl.documented_ids()
    architecture = (REPO_ROOT / "docs" / "system-prompt-architecture.md").read_text(encoding="utf-8")
    requirements = (REPO_ROOT / "docs" / "assignment-requirements.md").read_text(encoding="utf-8")
    defined = {
        "REQ": set(re.findall(r"^\| (REQ-[A-Z]{2}-\d\d) \|", requirements, re.M)),
        "BR": docs["BR"],
        "DD": docs["DD"],
        "PD": set(re.findall(ID_PATTERNS["PD"], architecture)),
        "T": docs["T"],
        "TS": docs["TS"],
        "PS": set(re.findall(r"^### (PS-\d\d) ", architecture, re.M)),
    }
    for kind, pattern in ID_PATTERNS.items():
        assert set(re.findall(pattern, trace)) <= defined[kind], f"unresolved {kind} reference"


def test_traceability_covers_decisions_transitions_and_scenarios(trace):
    docs = fl.documented_ids()
    section_text = trace.split("## 2. Section traceability")[1].split("## 3. Invariants")[0]
    assert set(re.findall(ID_PATTERNS["DD"], section_text)) == docs["DD"]
    assert set(re.findall(ID_PATTERNS["PD"], section_text)) == docs["PD"]
    assert set(re.findall(ID_PATTERNS["T"], section_text)) == docs["T"]
    assert set(re.findall(ID_PATTERNS["TS"], section_text)) == docs["TS"]
    assert len(set(re.findall(ID_PATTERNS["PS"], trace))) == 24


def test_unapproved_defaults_are_marked_as_such(trace):
    defaults = trace.split("## 5. Project defaults that are not approved decisions")[1].split("## 6. Deployment notes")[0]
    assert "Nothing in this section is an assignment requirement" in defaults
    for number in range(4, 14):
        row = re.search(rf"^\| PD-{number:02d} .*$", defaults, re.M)
        assert row, f"PD-{number:02d} has no default recorded"
        assert row.group(0).rstrip(" |").endswith(")") or "Neutral" in row.group(0) or "Flagged" in row.group(0)
    assert len(re.findall(r"^\| .*\*\*Flagged\*\*", defaults, re.M)) == 8
    assert "### 5.3 Flagged items needing a decision" in defaults


# ---------------------------------------------------------------- repository docs


def test_readme_reflects_that_the_prompt_exists():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "prompts/system_prompt_v1.md" in readme
    assert "docs/system-prompt-traceability.md" in readme
    assert "No voice-agent\nfunctionality, system prompt" not in readme
    assert "no system prompt" not in readme.lower()
    assert "has not been run on a voice platform" in readme
    evaluation_readme = (REPO_ROOT / "evaluation" / "README.md").read_text(encoding="utf-8")
    assert "no system prompt" not in evaluation_readme.lower()
