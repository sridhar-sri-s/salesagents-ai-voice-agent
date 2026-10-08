# Evaluation fixtures

Machine-readable synthetic test data for the Home Credit Loan Against Property (LAP) qualification call, and the checks that keep it consistent with the specification in [`docs/`](../docs).

This folder contains **no voice-agent implementation**. The system prompt lives in [`prompts/system_prompt_v1.md`](../prompts/system_prompt_v1.md); these fixtures are the input a future automated evaluation will run it against.

**All customer data here is synthetic.** No real customer, phone number, address or account detail is stored.

## Files

| File | Contents |
|---|---|
| `fixtures/scenarios.yaml` | The 67 scenarios of [`docs/test-scenarios.md`](../docs/test-scenarios.md), one entry per scenario ID. |
| `fixtures/profiles.yaml` | Synthetic prompt-variable sets (English/Hindi, female/male agent). |
| `fixtures/vocabulary.yaml` | The allowed states, call outcomes, fields, field values and behaviour labels, each pointing to the rule or decision it comes from. |
| `fixture_loader.py` | Loads the fixtures and validates them against each other and against `docs/`. |

The documents stay the authority. The fixtures do not restate the prose of a scenario (expected behaviour, pass and fail conditions); they carry the same scenario in a form a program can use, and refer back by ID.

## Scenario format

```yaml
- id: TS-E1                      # same ID as in docs/test-scenarios.md
  title: Above 75 Lakhs, accepts the maximum
  basis: source                  # or a list of design decisions, e.g. [DD-01]
  profile: default_en            # optional; prompt variables from profiles.yaml
  rag_context: ""                # optional; overrides additional_context_from_rag
  start:
    state: ELIGIBILITY_COLLECTION
    identity_verified: true
    offer_presented: true
    answered: {...}              # fields already captured
    pending: loan_amount         # the point the agent has just asked, or null
    clarified: []                # optional; tracked items whose one clarification is already used (PD-01)
  customer_turns:                # what the customer says, one entry per turn
    - "I need about one crore for my business expansion."
    - "Hmm, okay, seventy-five is fine then, let's go with that."
  expected:
    end_state: ELIGIBILITY_COLLECTION
    call_outcome: null           # set only when end_state is CALL_TERMINATION
    fields: {loan_amount: 75}    # values captured or replaced in this scenario
    control: {loan_amount_requested: 100}
    next_pending: occupation     # the point the agent should ask next
    transitions: [T-08, T-09]    # from docs/conversation-state-model.md
    must: [explain_loan_limit, ask_proceed_with_maximum, ask_pending_point]
    must_not: [disqualification_message, accept_amount_above_limit]
```

- Amounts are in Lakhs and tenure is in years. A spoken range is written `{min: 80, max: 85}`.
- `basis: source` means the expected behaviour rests on the assignment alone. A list of `DD-*` (design decision) or `PD-*` (prompt-policy decision) IDs means it rests on project decisions, which are not requirements from the assignment PDF.
- `optional_fields` holds values the agent may capture but is not required to.
- `clarified` lists tracked items: a field name (an internal clarification-tracking sub-value) or a branch-specific confirmation such as `proceed_with_maximum`. It is bookkeeping for the clarification limit. The eight field entries cover seven eligibility points, because point 5 has two sub-values (`occupation`, `income_mode`).
- `must` and `must_not` use the behaviour labels defined in `vocabulary.yaml`. They are what an evaluator will look for in a transcript.

## Validation

```bash
python -m evaluation.fixture_loader   # prints a summary and any problems
pytest                                # runs the same checks, plus the tests below
```

The checks confirm that:

- every documented scenario has exactly one fixture, and every fixture is documented;
- customer utterances, RAG fixture text and the design-decision basis match the document word for word;
- every state, field, behaviour, transition and design decision referenced exists;
- the listed transitions form a path the state model allows, from the starting state to `end_state`;
- each outcome is reached by its own documented transition, so `INCOMPLETE`, `WRONG_PERSON`, `NOT_INTERESTED`, `DECLINED_MAXIMUM` and the callback outcomes stay distinct from `DISQUALIFIED` and from each other;
- a `QUALIFIED` outcome has all seven points answered with eligible values;
- a `DISQUALIFIED` outcome has a value the assignment names as disqualifying, and no other outcome continues past one;
- a `TRANSFER` outcome records one of the two documented transfer triggers;
- there is exactly one clarification per tracked item: no second clarification, and no `INCOMPLETE` close without one (PD-01);
- clarification tracking never adds an eligibility point: a `QUALIFIED` outcome is checked against the seven points only, and the proceed-with-maximum confirmation is a branch response, not a field;
- disqualified, transfer, not-interested and incomplete closings require thanking the customer (PD-03);
- a loan amount above 75 Lakhs is never recorded as the answer;
- the vocabulary holds only the eligibility values documented in `docs/business-rules.md`;
- the fixtures contain no phone-number-like digit sequences, email addresses or credential-like entries.

Validation reads only files in this repository. It needs no network access, API keys or external services.

## How fixtures map to the specification

| Fixture element | Defined in |
|---|---|
| Scenario `id`, customer turns, RAG text | [`docs/test-scenarios.md`](../docs/test-scenarios.md) |
| `basis` (`DD-*`) | [`docs/design-decisions.md`](../docs/design-decisions.md) |
| `basis` (`PD-*`) | [`docs/system-prompt-architecture.md`](../docs/system-prompt-architecture.md), section 7.1 |
| States, fields, `transitions` (`T-nn`), `call_outcome` | [`docs/conversation-state-model.md`](../docs/conversation-state-model.md) |
| Eligible and disqualifying values, behaviour `ref` (`BR-*`) | [`docs/business-rules.md`](../docs/business-rules.md) |
| Prompt variables in profiles | [`docs/assignment-requirements.md`](../docs/assignment-requirements.md), section 5 |

## Adding a scenario

1. Write the scenario in `docs/test-scenarios.md` first: a `### TS-Xn` heading, an index row, and the usual lines (starting state, customer utterance, expected behaviour, expected state change, pass, fail). Add a **Basis** line if it rests on a design decision.
2. Add an entry with the same `id` to `fixtures/scenarios.yaml`. Copy the customer's words exactly. Reuse a preset (`*p1_p3` and so on) for the starting answers where one fits.
3. List the transitions the call takes, in order, using the tables in `docs/conversation-state-model.md`.
4. Pick `must` and `must_not` labels from `fixtures/vocabulary.yaml`. Add a new label there only if none fits, with a `ref` to an existing rule.
5. Run `python -m evaluation.fixture_loader`. Each problem is reported with the scenario ID and what is wrong.

Do not add a field value, outcome or disqualifying condition to `vocabulary.yaml` unless the specification in `docs/` already contains it.

## Not here yet

- A runner that plays these scenarios against an agent.
- A judge that scores a transcript against `must` and `must_not`.
- Any voice-platform integration.
