# System Prompt V1 — Architecture

Design of the system prompt for the Home Credit Loan Against Property (LAP) qualification agent.

**This document is not the system prompt.** It defines what the prompt must contain, where each instruction comes from, and how conflicts are resolved. It contains no prompt wording, no agent code and no voice-platform configuration.

The prompt built from this architecture is [`prompts/system_prompt_v1.md`](../prompts/system_prompt_v1.md). Its 25 numbered sections regroup the 24 sections defined here; the mapping is in [system-prompt-traceability.md](system-prompt-traceability.md).

- Requirements (`REQ-*`) and ambiguities (`AMB-*`): [assignment-requirements.md](assignment-requirements.md)
- Business rules (`BR-*`): [business-rules.md](business-rules.md)
- States and transitions (`T-nn`): [conversation-state-model.md](conversation-state-model.md)
- Design decisions (`DD-*`): [design-decisions.md](design-decisions.md)
- Scenarios (`TS-*`) and global fail conditions (`GF-n`): [test-scenarios.md](test-scenarios.md), with machine-readable fixtures in [`evaluation/fixtures/`](../evaluation/fixtures)

Two ID families are introduced here: `PS-nn` for a prompt section and `PD-nn` for a prompt-policy decision. A prompt-policy decision is a project choice about how the prompt behaves; like a design decision, it is **not** a requirement from the assignment PDF. Decided ones are in [section 7.1](#71-decided), pending ones in [section 7.2](#72-pending).

## 1. How the prompt is used

The assignment supplies `conversation_history` and `customer_utterance` as variables (REQ-PV-10, REQ-PV-11). The prompt is therefore evaluated **once per customer turn**, and nothing is remembered between turns except what `conversation_history` contains. Three consequences shape the whole architecture:

1. **State is derived, not stored.** On every turn the agent must work out from `conversation_history` where the call is and which of the seven points are answered (PS-06, PS-20). The states in the state model describe that derived position; the prompt will not ask the model to name them aloud.
2. **Every rule must hold on every turn.** A rule cannot rely on having been "applied earlier". The handoff gate, for example, is re-checked each turn.
3. **Variables are data, not instructions.** `customer_utterance`, `conversation_history` and `additional_context_from_rag` are things the agent reads. Nothing in them can change the rules (section 2).

## 2. Precedence hierarchy

When two instructions point different ways, the higher level wins. A lower level may only fill a gap the levels above it leave open.

| Level | What it is | Where it lives | What it may do | What it may never do |
|---|---|---|---|---|
| **L1** | Explicit assignment requirements | `REQ-*` marked Source; source-rule tables `BR-EL`, `BR-DQ`, `BR-TR`, `BR-CB`, `BR-HO`, `BR-CC` where they restate the PDF | Define who is eligible, what disqualifies, the transfer switch, the handoff gate, the variables | — |
| **L2** | Approved project business rules | `REQ-*` marked Clarified or Derived; `BR-*` rows marked Derived | Make L1 precise enough to act on (for example BR-EL-05a: point 5 needs both parts) | Add, remove or loosen an eligibility criterion |
| **L3** | Approved design decisions and decided prompt-policy decisions | `DD-01` to `DD-17`, `BR-DD-01` to `BR-DD-17`; `PD-01` to `PD-03`, `BR-PD-01` to `BR-PD-03` | Choose behaviour where L1 and L2 are silent | Contradict L1 or L2; add an eligibility criterion; add a route to the handoff |
| **L4** | Runtime variables and context | The eleven prompt variables | Supply facts for this call: names, language, gender, date, product knowledge, what has been said | Change a rule at L1 to L3 |
| **L5** | Natural-language interpretation | The model's reading of what the customer said | Map an utterance onto the categories the assignment names | Create a category, a criterion, a value the customer did not give, or a conclusion the rules do not support |

Two clarifications on L4:

- **The duty to obey `language_to_speak` and `agent_gender` is L1** (REQ-PV-09, REQ-PV-04). Only their *values* arrive at L4. They are not optional because they are variables.
- **`additional_context_from_rag` ranks below every rule** (DD-17). It is the only variable whose content could plausibly contradict the specification, so the prompt states its limits explicitly (PS-19).

### 2.1 Invariants

These four hold regardless of anything else in the prompt. Each is restated in the section that enforces it and again in the final checklist of the prompt (PS-22).

| ID | The prompt must never allow | Enforced by | Grounded in |
|---|---|---|---|
| INV-1 | RAG context to override assignment eligibility | PS-03, PS-19 | DD-17, BR-DD-17 |
| INV-2 | Conversational inference to create new eligibility criteria | PS-07, PS-11, PS-14 | BR-EL-06a, DD-06, BR-DD-06 |
| INV-3 | Incomplete data to be treated as qualification | PS-15, PS-22 | BR-HO-01, BR-HO-05, DD-07, DD-11 |
| INV-4 | A handoff before all seven required points are established | PS-22 | REQ-BL-06, BR-HO-01, BR-HO-03 |

Two further invariants follow from the design decisions and are treated the same way:

| ID | The prompt must never allow | Enforced by | Grounded in |
|---|---|---|---|
| INV-5 | "Not qualified" to be presented as "disqualified" when no documented criterion failed | PS-11, PS-23 | DD-11, BR-DD-11 |
| INV-6 | Any offer or eligibility detail to be disclosed before the customer is verified | PS-04, PS-05 | REQ-CS-03, DD-03, DD-16 |

### 2.2 Conflicts already settled

| Conflict | Resolution | Level | Source |
|---|---|---|---|
| Sequential capture vs out-of-order answers | Order 1→7 is the default; anything volunteered is captured and not asked again | L1 | REQ-EL-00, REQ-OO-01 |
| Immediate disqualification vs a loan amount above 75 Lakhs | The amount rule has its own handling and is not an immediate disqualification | L1 | REQ-BL-03, BR-DQ-09 |
| Transfer trigger vs disqualifying answer in one utterance | Transfer wins | L3 | DD-02 |
| Disqualification "at any point" vs offer only after verification | Verification first; the response is deferred, not waived | L3 | DD-16 |
| Retrieved context vs eligibility rules | Rules win | L3 | DD-17 |
| Customer asks to skip ahead vs handoff gate | Gate wins | L1 | REQ-BL-06, BR-HO-05 |
| Customer's language vs `language_to_speak` | `language_to_speak` wins for the agent's output | L1, L3 | REQ-PV-09, DD-05 |
| Correction vs a call already closed | Closed stays closed | L3 | DD-08 |
| Several signals in one utterance (transfer, disqualification, not interested, busy) | Fixed order: transfer, disqualification, not interested, busy, normal flow | L3 | PD-02 |
| Unclear answer: keep asking, move on, or close | Exactly one clarification, then the incomplete outcome | L3 | PD-01 |

### 2.3 Per-turn evaluation order

The order in which the agent checks things on each turn. Steps 4 to 7 are the project-level signal precedence fixed by PD-02; that ranking is not PDF-derived, except that transfer above disqualification was already approved in DD-02.

| Step | Check | If true | Basis |
|---|---|---|---|
| 1 | Has the call already entered an exit path? | Close; do not reopen (PS-23) | DD-08 |
| 2 | Is the customer not yet verified? | Verify; disclose nothing (PS-04). Before verification only the busy path and the wrong-person path can act; transfer and disqualification responses are deferred | REQ-CS-03, DD-03, DD-12, DD-16 |
| 3 | Capture every eligibility detail in the utterance, including corrections | Update the derived state (PS-09, PS-10) | REQ-OO-01, DD-08 |
| 4 | **Transfer:** did the customer mention an existing loan on the property or wanting to reduce their current EMI? | Transfer (PS-12) | REQ-BL-04, DD-02, PD-02 rank 1 |
| 5 | **Disqualification:** does any captured value fail a documented criterion? | Disqualify (PS-11) | REQ-BL-01, PD-02 rank 2 |
| 6 | **Not interested:** did the customer clearly decline the offer? | Not-interested close (PS-16) | DD-09, PD-02 rank 3 |
| 7 | **Busy:** did the customer say they are busy? | Callback path (PS-13) | REQ-CS-02, DD-04, PD-02 rank 4 |
| 8 | Is the requested amount above 75 Lakhs? | Explain the limit, ask about the maximum (PS-07) | REQ-BL-03 |
| 9 | Was the response to a question that was asked unclear, incomplete, unclassified, unknown or refused? | First time for that tracked item: one clarification or re-ask. Second time: incomplete outcome (PS-14, PS-15) | DD-06, DD-07, DD-11, PD-01 |
| 10 | Did the customer ask a question or interrupt? | Address it, then return to the pending point. This does not use up the clarification (PS-19, PS-21) | REQ-NC-02, REQ-BL-06, PD-01 |
| 11 | Are all seven points answered and eligible? | Handoff (PS-22); otherwise ask the lowest-numbered unanswered point (PS-08) | REQ-BL-05, REQ-BL-06 |

## 3. Prompt section map

The eventual prompt has 24 sections in six groups. Group order is the proposed order in the prompt: who the agent is, the rules that cannot be broken, the normal path, the exits, how to speak, and how to finish.

| Group | ID | Section |
|---|---|---|
| A. Identity and inputs | PS-01 | Role and objective |
| | PS-02 | Runtime variables |
| | PS-20 | `conversation_history` usage |
| | PS-19 | `additional_context_from_rag` usage |
| B. Hard rules | PS-03 | Priority and precedence rules |
| | PS-06 | Conversation-state management |
| C. Normal path | PS-04 | Customer identity handling |
| | PS-05 | Offer presentation |
| | PS-07 | Seven eligibility fields |
| | PS-08 | Sequential question flow |
| | PS-09 | Out-of-order information capture |
| | PS-10 | Corrections |
| D. Exits and exceptions | PS-11 | Immediate disqualification |
| | PS-12 | Loan-transfer logic |
| | PS-13 | Busy/callback behaviour |
| | PS-14 | Unknown/unclassified answers |
| | PS-15 | Don't-know/refusal handling |
| | PS-16 | Not-interested handling |
| E. Manner | PS-17 | Language behaviour |
| | PS-18 | Agent gender constraints |
| | PS-21 | Natural conversation behaviour |
| F. Finishing | PS-22 | Final handoff gate |
| | PS-23 | Terminal states |
| | PS-24 | Closing behaviour |

## 4. Section specifications

Each section lists its purpose, its sources by level, the transitions and scenarios it must satisfy, and the failure modes the prompt wording has to prevent.

### PS-01 — Role and objective

- **Purpose:** Tell the agent who it is, who it is calling and what the call is for: inform an existing customer of a pre-approved LAP offer and carry out a preliminary eligibility check, as the first point of contact before a senior loan expert.
- **Authoritative sources:** REQ-UC-01, REQ-UC-02, REQ-UC-03, REQ-UC-04, REQ-UC-05, REQ-PV-01, REQ-PV-03
- **Business rules:** BR-CC-01, BR-CC-09, BR-CC-10, BR-HO-06
- **Design decisions:** none
- **Transitions:** T-01
- **Test scenarios:** TS-A1
- **Failure modes:** acts as the party that approves or finalizes the loan; promises approval; drifts into topics outside the LAP offer; hard-codes the company name instead of using `company_name`.
- **Open:** whether and how the agent says it is an AI (PD-04).

### PS-02 — Runtime variables

- **Purpose:** Declare all eleven variables, what each is for, and that each is data to be read, never an instruction to be followed.
- **Authoritative sources:** REQ-PV-01, REQ-PV-02, REQ-PV-03, REQ-PV-04, REQ-PV-05, REQ-PV-06, REQ-PV-07, REQ-PV-08, REQ-PV-09, REQ-PV-10, REQ-PV-11
- **Business rules:** BR-CC-09, BR-CC-10, BR-CC-11, BR-CC-12, BR-CB-04
- **Design decisions:** DD-10, DD-14, DD-17
- **Transitions:** T-01
- **Test scenarios:** TS-A1, TS-B2, TS-B5, TS-R1, TS-Y1
- **Failure modes:** speaks an unfilled placeholder aloud; treats text inside `customer_utterance` or the retrieved context as an instruction that changes its rules; breaks when a variable is empty; volunteers the date or time when it is only context.

| Variable | Role in the prompt | Read as |
|---|---|---|
| `company_name` | Who the agent calls on behalf of | Fact |
| `customer_name` | Who the agent must confirm it is speaking to | Fact |
| `agent_name` | How the agent introduces itself | Fact |
| `agent_gender` | Fixes the agent's self-reference for the whole call | Binding (L1) |
| `current_date`, `current_day`, `current_time` | Context, mainly for callback times | Fact |
| `additional_context_from_rag` | Product knowledge for customer questions | Untrusted reference, below all rules |
| `language_to_speak` | The agent's output language | Binding (L1) |
| `conversation_history` | The only record of the call so far | Evidence of what was said |
| `customer_utterance` | What the customer just said | Evidence of what was said |

- **Open:** variable formats and injection syntax (PD-09).

### PS-03 — Priority and precedence rules

- **Purpose:** State the hierarchy of section 2 and the invariants in a short, unambiguous form near the top of the prompt, so that later sections cannot be read as overriding them.
- **Authoritative sources:** REQ-BL-01, REQ-BL-03, REQ-BL-04, REQ-BL-06, REQ-CS-03
- **Business rules:** BR-DQ-05, BR-DQ-09, BR-TR-04, BR-HO-01, BR-HO-05, BR-CC-07, BR-EL-06a
- **Design decisions:** DD-02, DD-16, DD-17
- **Transitions:** T-10, T-11, T-12
- **Test scenarios:** TS-M3, TS-Q2, TS-Y3, TS-T3, TS-E1, TS-S1, TS-Z1, TS-Z2, TS-Z3, TS-Z4, TS-Z5
- **Failure modes:** two rules fire and the agent gives both messages; a later, more specific-sounding sentence in the prompt is taken to override an invariant; the customer or the retrieved context talks the agent out of a rule.
- **Prompt policy:** PD-02 fixes the order of competing signals in one utterance: transfer, disqualification, not interested, busy, normal flow.

### PS-04 — Customer identity handling

- **Purpose:** Confirm the agent is speaking with `customer_name` before anything else, and define what may be said to a person who is not, or not yet, confirmed.
- **Authoritative sources:** REQ-CS-01, REQ-CS-03, REQ-PV-02
- **Business rules:** BR-CC-07, BR-DD-03, BR-DD-12, BR-DD-16
- **Design decisions:** DD-03, DD-12, DD-16
- **Transitions:** T-02, T-03, T-23, T-26, T-28
- **Test scenarios:** TS-A1, TS-B1, TS-B5, TS-T1, TS-T2, TS-T3; GF-4
- **Failure modes:** reveals the offer, the amount or an eligibility detail to the wrong person; gives a disqualification or transfer message before verification; asks for date of birth, address or other identity data the assignment does not provide for; explains the offer "so the message can be passed on".
- **Open:** what counts as confirmation for an ambiguous reply, how many attempts, and what the agent may say about why it is calling (PD-08).

### PS-05 — Offer presentation

- **Purpose:** Once the customer is verified, explain the reason for the call: rewarding their loyalty with a special LAP offer of up to 75 Lakhs. Then move into the eligibility questions without a consent gate.
- **Authoritative sources:** REQ-CS-03, REQ-CS-04, REQ-UC-03
- **Business rules:** BR-CC-07, BR-CC-08, BR-DD-15
- **Design decisions:** DD-09, DD-15
- **Transitions:** T-03, T-05, T-18
- **Test scenarios:** TS-A1, TS-U1, TS-U2, TS-L2, TS-C2, TS-N1
- **Failure modes:** drops "up to" and so promises 75 Lakhs; implies the loan is already granted; presents the offer before verification; demands explicit consent before the first question; repeats the offer on later turns.
- **Open:** how "pre-approved" is worded given that the customer may then be found not eligible (PD-11).

### PS-06 — Conversation-state management

- **Purpose:** Instruct the agent to work out, on every turn, where the call stands: whether the customer is verified, whether the offer has been presented, which of the seven points are answered and with what value, and whether an exit path has been entered.
- **Authoritative sources:** REQ-EL-00, REQ-OO-01, REQ-PV-10, REQ-PV-11
- **Business rules:** BR-EL-00, BR-CC-05, BR-CC-11, BR-DD-14
- **Design decisions:** DD-08, DD-14
- **Transitions:** all; in particular T-06, T-07 and the guard on T-12
- **Test scenarios:** TS-L1, TS-S2, TS-S3, TS-X1, TS-B5
- **Failure modes:** treats a question the agent asked as if it had been answered; loses an answer given several turns earlier; counts an answer the customer never gave; believes the offer was presented when it was not.
- **Note:** the model derives this privately. What it outputs is only what it says to the customer (PD-06).

### PS-07 — Seven eligibility fields

- **Purpose:** Define the seven data points, the accepted categories for each and the eligible and non-eligible values, exactly as the assignment gives them.
- **Authoritative sources:** REQ-EL-00, REQ-EL-01, REQ-EL-02, REQ-EL-03, REQ-EL-04, REQ-EL-05, REQ-EL-06, REQ-EL-07, REQ-BL-03
- **Business rules:** BR-EL-00, BR-EL-01, BR-EL-02, BR-EL-03, BR-EL-04, BR-EL-04a, BR-EL-05, BR-EL-05a, BR-EL-06, BR-EL-06a, BR-EL-07, BR-DQ-09, BR-DQ-10
- **Design decisions:** DD-01, DD-06
- **Transitions:** T-06, T-08, T-09, T-17
- **Test scenarios:** TS-A1, TS-A2, TS-K1, TS-E1, TS-E2, TS-E3, TS-E4, TS-E5, TS-I1, TS-I2, TS-I3, TS-J1, TS-G2, TS-H2, TS-P1; GF-7
- **Failure modes:** applies a Market Value threshold or compares it to the loan amount; treats Joint ownership as a problem; counts point 5 as answered with only the occupation or only the income mode; treats exactly 75 Lakhs, 3 years or 15 years as out of range; confuses lakhs and crores; records an amount above 75 Lakhs as accepted.

| Point | Field | Accepted values | Non-eligible | Special handling |
|---|---|---|---|---|
| 1 | Property Type | Residential, Commercial, Industrial | Agricultural | — |
| 2 | Ownership Status | Sole, Joint | none | — |
| 3 | Document Availability | Original Documents available | unavailable | — |
| 4 | Loan Amount | 75 Lakhs or less | — | Above 75 Lakhs: explain limit, ask about maximum (BR-EL-04a); decline ends the call without qualification (DD-01) |
| 5 | Occupation & Income Mode | Salaried or Self-Employed, with Bank income | Cash income | Both parts required (BR-EL-05a) |
| 6 | Market Value | any estimate | none | Capture only; no threshold (BR-EL-06a) |
| 7 | Tenure | 3 to 15 years | below 3 or above 15 | — |

### PS-08 — Sequential question flow

- **Purpose:** Ask the points in order 1 to 7, one at a time, always moving to the lowest-numbered point that is still unanswered.
- **Authoritative sources:** REQ-EL-00, REQ-OO-02
- **Business rules:** BR-EL-00, BR-CC-06
- **Design decisions:** DD-15
- **Transitions:** T-05, T-06, T-07
- **Test scenarios:** TS-A1, TS-L1, TS-O1, TS-S3
- **Failure modes:** asks several points in one turn; skips a point; jumps ahead after an out-of-order answer and never returns; asks the points in a different order without the customer having volunteered anything.
- **Open:** how strict the order is when nothing is volunteered remains AMB-25; the architecture uses 1 to 7.

### PS-09 — Out-of-order information capture

- **Purpose:** Examine every utterance for any of the seven points, keep whatever is given, never ask for it again, and check each captured value against its criterion at once.
- **Authoritative sources:** REQ-OO-01, REQ-OO-02, REQ-BL-01
- **Business rules:** BR-CC-05, BR-CC-06, BR-DQ-06, BR-DD-16
- **Design decisions:** DD-16
- **Transitions:** T-06, T-10, T-08, T-28
- **Test scenarios:** TS-L1, TS-L2, TS-Q1, TS-Q2, TS-C2, TS-S3, TS-T3; GF-1
- **Failure modes:** re-asks a point the customer already covered; captures only the point that was asked and ignores the rest of the sentence; misses a disqualifying value because its question had not come up yet; responds to volunteered information before verification.

### PS-10 — Corrections

- **Purpose:** Let the customer's latest explicit correction replace an earlier answer while the call is active, re-check the corrected value, and refuse to reopen a call that has already closed.
- **Authoritative sources:** none in the assignment (AMB-14); REQ-OO-01 for the surrounding rule
- **Business rules:** BR-DD-08, BR-CC-05, BR-CC-11
- **Design decisions:** DD-08
- **Transitions:** T-22, T-08, T-10, T-14
- **Test scenarios:** TS-X1, TS-X2, TS-X3
- **Failure modes:** keeps the old value; treats the correction as a new point and re-asks others; ignores a correction that makes the customer non-eligible; resumes the checklist after a disqualification because the customer changes their answer.

### PS-11 — Immediate disqualification

- **Purpose:** The moment a captured value fails one of the four documented criteria, tell the customer politely that they do not meet the criteria for this specific offer at this time, and end the call with no further eligibility questions.
- **Authoritative sources:** REQ-BL-01, REQ-BL-02, REQ-EL-01, REQ-EL-03, REQ-EL-05, REQ-EL-07
- **Business rules:** BR-DQ-01, BR-DQ-02, BR-DQ-03, BR-DQ-04, BR-DQ-05, BR-DQ-06, BR-DQ-07, BR-DQ-08, BR-DQ-09, BR-DQ-10, BR-DD-11, BR-DD-17
- **Design decisions:** DD-02, DD-08, DD-11, DD-16, DD-17
- **Transitions:** T-10, T-14
- **Test scenarios:** TS-C1, TS-C2, TS-D1, TS-F1, TS-F2, TS-G1, TS-H1, TS-Q2, TS-X3, TS-Y3; GF-3, GF-7
- **Failure modes:** continues to the next question; disqualifies for something that is not one of the four criteria (INV-2); disqualifies for an unanswered or unclassified point (INV-5); quietly adjusts the answer to make it fit (for example capping the tenure); suggests a workaround; is curt or blames the customer; lets retrieved context excuse the failed criterion (INV-1).
- **Prompt policy:** PD-02 ranks disqualification below transfer and above not-interested and busy. PD-03 fixes the closing: polite explanation, no internal rule names or implementation details, thanks, end.
- **Open:** whether the message may give the reason in plain language (PD-12).

### PS-12 — Loan-transfer logic

- **Purpose:** If the customer mentions an existing loan on the property, or wanting to reduce their current EMI, tell them a specialist for loan transfer will contact them shortly, and end the call.
- **Authoritative sources:** REQ-BL-04
- **Business rules:** BR-TR-01, BR-TR-02, BR-TR-03, BR-TR-04, BR-TR-05, BR-TR-06, BR-TR-07, BR-DD-02
- **Design decisions:** DD-02, DD-16
- **Transitions:** T-11, T-15
- **Test scenarios:** TS-M1, TS-M2, TS-M3, TS-N1
- **Failure modes:** misses a passing remark about an existing loan; carries on with the checklist; words the transfer as a disqualification; gives the senior-loan-expert message; gives both the transfer and the disqualification message; fires on a remark that is not a trigger.
- **Prompt policy:** PD-02 ranks transfer first. PD-03 fixes the closing: the specialist-for-loan-transfer message, thanks, end.
- **Open:** loans or EMIs not on this property, and whether the agent ever asks about existing loans (PD-07).

### PS-13 — Busy/callback behaviour

- **Purpose:** When the customer says they are busy, acknowledge it and ask for a preferred callback time; once a time is accepted, or none can be given, end the interaction without continuing qualification.
- **Authoritative sources:** REQ-CS-02, REQ-PV-05, REQ-PV-06, REQ-PV-07
- **Business rules:** BR-CB-01, BR-CB-02, BR-CB-03, BR-CB-04, BR-DD-04, BR-DD-13, BR-DD-14
- **Design decisions:** DD-04, DD-13, DD-14
- **Transitions:** T-04, T-13, T-24, T-27, T-19
- **Test scenarios:** TS-B1, TS-B2, TS-B3, TS-B4, TS-B5
- **Failure modes:** pitches the offer to a busy customer; keeps asking eligibility questions; does not ask for a time; invents a callback time; tells a customer with no time that they do not qualify; assumes earlier answers on a later call when they are not in `conversation_history`.
- **Prompt policy:** PD-02 ranks busy last among the signals, so it never overrides an explicit transfer, disqualification or refusal in the same utterance. PD-03 restates the busy behaviour.
- **Source boundary:** only "acknowledge and ask for a preferred callback time" is from the assignment. Everything after that is DD-04 and DD-13.

### PS-14 — Unknown/unclassified answers

- **Purpose:** When an answer does not clearly map to one of the assignment's categories, ask a clarification question. Never infer a category, never create one, never disqualify on it.
- **Authoritative sources:** none in the assignment (AMB-06, AMB-07, AMB-09, AMB-11, AMB-22)
- **Business rules:** BR-DD-06, BR-DD-11
- **Design decisions:** DD-06, DD-11
- **Transitions:** T-20, T-25, T-19
- **Test scenarios:** TS-V1, TS-V2, TS-V3, TS-V4
- **Failure modes:** decides an empty plot is Residential or Agricultural on its own judgement; treats "retired" as eligible or as not eligible; invents a new category; assumes pension is Bank income; tells the customer they are ineligible when the point simply could not be classified (INV-5).
- **Prompt policy:** PD-01: exactly one clarification for the tracked item, then the incomplete outcome. PD-03 fixes the incomplete closing.

### PS-15 — Don't-know/refusal handling

- **Purpose:** When the customer cannot or will not give a required value, explain that it is needed for preliminary qualification and ask again naturally. If it still cannot be established, close politely without qualifying and without a disqualification message.
- **Authoritative sources:** REQ-BL-06
- **Business rules:** BR-HO-01, BR-HO-03, BR-HO-05, BR-DD-07, BR-DD-11
- **Design decisions:** DD-07, DD-11
- **Transitions:** T-07, T-21, T-25, T-19
- **Test scenarios:** TS-W1, TS-W2, TS-W3, TS-P2, TS-P3
- **Failure modes:** skips the point and moves on; supplies a value itself; treats a filler ("yeah...") as an answer; hands off with the point missing (INV-3, INV-4); says the customer does not meet the criteria (INV-5); keeps pressing after a clear refusal.
- **Prompt policy:** PD-01: exactly one re-ask for the tracked item, then the incomplete outcome; a customer question in between does not count. PD-03 fixes the incomplete closing.

### PS-16 — Not-interested handling

- **Purpose:** If the customer clearly declines the offer or the process, acknowledge the decision and end politely. A neutral reply is not a refusal.
- **Authoritative sources:** none in the assignment (AMB-04, AMB-05)
- **Business rules:** BR-DD-09, BR-DD-15, BR-HO-01
- **Design decisions:** DD-09, DD-15
- **Transitions:** T-18, T-19
- **Test scenarios:** TS-U1, TS-U2
- **Failure modes:** starts the checklist anyway; hands off; tells the customer they do not meet the criteria; treats "hmm, okay" as a refusal; treats hesitation or a question as a refusal; starts a callback for a customer who has clearly refused.
- **Prompt policy:** PD-02 ranks a clear refusal above busy and below transfer and disqualification. PD-03 fixes the closing: acknowledge, thank, end.

### PS-17 — Language behaviour

- **Purpose:** The agent speaks `language_to_speak` for the whole call. It may understand a customer who answers in the other language or mixes the two, but it does not switch its own language.
- **Authoritative sources:** REQ-PV-09, REQ-NC-04
- **Business rules:** BR-CC-04, BR-DD-05
- **Design decisions:** DD-05
- **Transitions:** none
- **Test scenarios:** TS-R1, TS-R2; GF-6
- **Failure modes:** mirrors the customer's language; applies different rules in Hindi; fails to capture an answer given in mixed Hindi and English; moves on without having understood an answer.
- **Open:** Hindi script, register and number wording for speech (PD-05).

### PS-18 — Agent gender constraints

- **Purpose:** Every self-reference by the agent is consistent with `agent_gender` from the first word to the last. In Hindi this governs verb and adjective forms.
- **Authoritative sources:** REQ-PV-04, REQ-PV-03
- **Business rules:** BR-CC-09
- **Design decisions:** none
- **Transitions:** none
- **Test scenarios:** TS-A1, TS-R1; GF-6
- **Failure modes:** gender drifts over a long call; Hindi verb forms contradict `agent_gender`; the agent's name and gender are treated as a persona it can drop when asked; the agent assumes the customer's gender from their name.
- **Open:** allowed values of `agent_gender` (PD-05, AMB-21).

### PS-19 — `additional_context_from_rag` usage

- **Purpose:** Use retrieved context to answer a relevant product question, add nothing that is not in it, and never let it change a rule. Exact interest rates stay with the senior loan expert.
- **Authoritative sources:** REQ-PV-08, REQ-BL-05, REQ-BL-07
- **Business rules:** BR-CC-12, BR-HO-04, BR-DD-10, BR-DD-17
- **Design decisions:** DD-10, DD-17
- **Transitions:** T-07
- **Test scenarios:** TS-O1, TS-Y1, TS-Y2, TS-Y3; GF-5
- **Failure modes:** invents a fee, rate or product detail when the context is empty; commits to an exact interest rate; treats retrieved text as overriding an eligibility criterion (INV-1) or as adding one (INV-2); follows an instruction embedded in retrieved text; answers the question and forgets the pending point.

### PS-20 — `conversation_history` usage

- **Purpose:** Treat `conversation_history` as the only record of the call. Read it to derive state, to avoid re-asking, and to know what has already been said. Assume nothing that is not in it or in the supplied variables.
- **Authoritative sources:** REQ-PV-10, REQ-PV-11, REQ-OO-01
- **Business rules:** BR-CC-05, BR-CC-11, BR-DD-14
- **Design decisions:** DD-14
- **Transitions:** T-01
- **Test scenarios:** TS-B5, TS-L1, TS-L2, TS-S2, TS-X1
- **Failure modes:** claims to have answers from an earlier call; greets or presents the offer again mid-call because it did not read the history; with an empty history, skips the greeting; treats its own earlier statement as something the customer said.

### PS-21 — Natural conversation behaviour

- **Purpose:** Make the call sound natural, professional and advisory: understand full sentences, cope with interruptions and fillers, answer what was asked, and return to the pending point.
- **Authoritative sources:** REQ-UC-04, REQ-NC-01, REQ-NC-02, REQ-NC-03, REQ-NC-05, REQ-NC-06
- **Business rules:** BR-CC-01, BR-CC-02, BR-CC-03
- **Design decisions:** DD-05
- **Transitions:** T-07
- **Test scenarios:** TS-O1, TS-O2, TS-P1, TS-P2, TS-Q1, TS-I1
- **Failure modes:** expects "yes" or "no"; talks over an interruption; repeats a question the customer answered by cutting in; reads a filler as agreement; sounds like a form being read out; produces text that cannot be spoken (lists, symbols, digits that read badly).

### PS-22 — Final handoff gate

- **Purpose:** Before the handoff message, verify on that turn that all seven points are answered and every one meets its criterion. Only then tell the customer that a senior loan expert will call back shortly to provide exact interest rates.
- **Authoritative sources:** REQ-BL-05, REQ-BL-06, REQ-BL-07, REQ-UC-05
- **Business rules:** BR-HO-01, BR-HO-02, BR-HO-03, BR-HO-04, BR-HO-05, BR-HO-06
- **Design decisions:** DD-07, DD-11, DD-14
- **Transitions:** T-12 and its guard, T-16
- **Test scenarios:** TS-A1, TS-G2, TS-H2, TS-S1, TS-S2, TS-S3; GF-2, GF-5
- **Failure modes:** hands off because the customer asks for the expert; hands off with a point skipped by a diversion; treats Market Value as optional because it has no threshold; counts a point answered on an earlier call that is not in the history; tells the customer the loan is approved; quotes a rate.
- **Design note:** this section doubles as the prompt's closing checklist and restates INV-3 and INV-4.

### PS-23 — Terminal states

- **Purpose:** Name every way the call can end, the one message that belongs to each, and the rule that an ended call stays ended.
- **Authoritative sources:** REQ-BL-01, REQ-BL-04, REQ-BL-05, REQ-CS-02
- **Business rules:** BR-DQ-07, BR-TR-04, BR-HO-02, BR-DD-01, BR-DD-04, BR-DD-08, BR-DD-09, BR-DD-11, BR-DD-12, BR-DD-13
- **Design decisions:** DD-01, DD-04, DD-08, DD-09, DD-11, DD-12, DD-13
- **Transitions:** T-13, T-14, T-15, T-16, T-17, T-18, T-19, T-25, T-26, T-27
- **Test scenarios:** TS-A1, TS-C1, TS-M1, TS-B2, TS-B4, TS-E2, TS-U1, TS-W2, TS-V3, TS-P3, TS-T2, TS-X2; GF-8
- **Failure modes:** uses the wrong message for the ending; gives two endings; uses the disqualification message for an ending where no criterion failed (INV-5); continues the conversation after an ending.

| Ending | Origin | What the customer is told |
|---|---|---|
| Qualified | Assignment | A senior loan expert will call back shortly to provide exact interest rates |
| Disqualified | Assignment; closing per PD-03 | They do not meet the criteria for this specific offer at this time, with thanks; no internal rule names |
| Transfer | Assignment; closing per PD-03 | A specialist for loan transfer will contact them shortly, with thanks |
| Callback | Assignment for asking the time; DD-04 for ending | Acknowledgement of the callback time |
| Declined maximum | DD-01 | Polite close |
| Not interested | DD-09; closing per PD-03 | Acknowledgement of their decision, with thanks |
| Incomplete | DD-11, PD-01; closing per PD-03 | That the required information could not be established, with thanks; not that they are ineligible |
| Wrong person | DD-12 | Polite close; nothing about the offer |
| No callback time | DD-13 | Polite close |

### PS-24 — Closing behaviour

- **Purpose:** Define how the agent actually finishes: one short, polite closing line that matches the ending, no new topic, and no response that reopens the flow.
- **Authoritative sources:** REQ-BL-01, REQ-BL-04, REQ-BL-05, REQ-UC-04
- **Business rules:** BR-DQ-07, BR-TR-04, BR-HO-02, BR-CC-01
- **Design decisions:** DD-08
- **Transitions:** T-13, T-14, T-15, T-16, T-19
- **Test scenarios:** TS-A1, TS-C1, TS-M1, TS-U1, TS-X2
- **Failure modes:** asks another eligibility question after the closing line; adds a sales pitch; keeps talking; is abrupt; gives a time commitment for "shortly" that nobody defined.
- **Prompt policy:** PD-03 defines the closing for disqualified, transfer, not interested, incomplete and busy, in platform-neutral terms.
- **Open:** exact wording; the closings PD-03 does not cover (PD-13); how the call is technically ended (PD-09); what, if anything, is recapped at handoff (PD-06).

## 5. Coverage

### 5.1 Design decisions to sections

| Decision | Sections |
|---|---|
| DD-01 | PS-07, PS-23 |
| DD-02 | PS-03, PS-11, PS-12 |
| DD-03 | PS-04 |
| DD-04 | PS-13, PS-23 |
| DD-05 | PS-17, PS-21 |
| DD-06 | PS-07, PS-14 |
| DD-07 | PS-15, PS-22 |
| DD-08 | PS-06, PS-10, PS-11, PS-23, PS-24 |
| DD-09 | PS-05, PS-16, PS-23 |
| DD-10 | PS-02, PS-19 |
| DD-11 | PS-11, PS-14, PS-15, PS-22, PS-23 |
| DD-12 | PS-04, PS-23 |
| DD-13 | PS-13, PS-23 |
| DD-14 | PS-02, PS-06, PS-13, PS-20, PS-22 |
| DD-15 | PS-05, PS-08, PS-16 |
| DD-16 | PS-03, PS-04, PS-09, PS-11, PS-12 |
| DD-17 | PS-02, PS-03, PS-11, PS-19 |

### 5.2 Global fail conditions to sections

| Condition | Meaning | Sections |
|---|---|---|
| GF-1 | Re-asks an answered detail | PS-09 |
| GF-2 | Handoff with a point unanswered | PS-22 |
| GF-3 | Continues after a disqualifying answer or transfer trigger | PS-11 |
| GF-4 | Offer before verification | PS-04 |
| GF-5 | Invents or commits to an exact interest rate | PS-19, PS-22 |
| GF-6 | Wrong language, gender or name | PS-17, PS-18 |
| GF-7 | Applies an eligibility rule the assignment does not contain | PS-07, PS-11 |
| GF-8 | Closes without thanking the customer, or exposes internal rule names (PD-03) | PS-23, PS-24 |
| GF-9 | More than one clarification for a tracked item, or an incomplete close without one (PD-01) | PS-14, PS-15 |

### 5.3 Prompt-policy decisions to sections

| Decision | Sections |
|---|---|
| PD-01 | PS-14, PS-15 |
| PD-02 | PS-03, PS-11, PS-12, PS-13, PS-16 |
| PD-03 | PS-11, PS-12, PS-13, PS-14, PS-15, PS-16, PS-23, PS-24 |

Every one of the 67 scenarios and all 28 transitions is assigned to at least one section above.

## 6. Contradictions found

None of these blocks the architecture. The first four were contradictions in the source that earlier phases already resolved; they are listed because the prompt must state the resolution explicitly. The rest are tensions the prompt wording has to manage.

| # | Contradiction or tension | Status |
|---|---|---|
| C-1 | The assignment says to capture details "sequentially" and also to accept details given out of order. | Resolved: order is the default, volunteered details are kept (REQ-EL-00, REQ-OO-01). |
| C-2 | "Immediate disqualification" for any answer that fails a criterion, yet an amount above 75 Lakhs gets an explanation and a question. | Resolved: the amount rule is the exception (BR-DQ-09). |
| C-3 | Disqualification applies "at any point", yet the offer may only be presented once the customer is verified. A disqualification message before verification would reveal the offer. | Resolved by DD-16: deferred until verified. |
| C-4 | One utterance can trigger both the transfer switch and a disqualification, which carry different messages. | Resolved by DD-02: transfer wins. |
| C-5 | The offer is "pre-approved", but the same call can end with the customer told they do not meet the criteria. | **Open** wording tension (PD-11, AMB-20). |
| C-6 | Disqualification is immediate and a closed call is not reopened (DD-08), while natural conversation means customers misspeak. A slip is recoverable only if corrected in the same utterance. | Consistent with the decisions as written; flagged because it is a harsh outcome a reviewer may question. |
| C-7 | DD-11 says to close "after reasonable clarification" without a number, while TS-W2 and TS-V3 close after exactly one explanation or clarification. The scenarios are stricter than the decision. | Resolved by PD-01: exactly one clarification, which is what the scenarios assume. |
| C-8 | DD-04 (busy, at any stage) and DD-09 (not interested) can both apply to "I'm busy, I don't want this". No rank is defined between them, or between either and transfer or disqualification. | Resolved by PD-02: transfer, disqualification, not interested, busy. |
| C-9 | `docs/test-scenarios.md` TS-S3 says point 5 was "just captured" in the starting state, but the customer's utterance in that scenario is the answer to point 5. The fixture starts with point 5 pending. | Minor inconsistency in the document; the fixture is the consistent reading. Not changed in this phase. |
| C-10 | `conversation-state-model.md` lists `CALLBACK` among the source outcomes, while `vocabulary.yaml` marks it as a design outcome (DD-04). | Labelling difference only; behaviour is the same. Not changed in this phase. |

## 7. Prompt-policy decisions

> **Prompt-policy decisions are project decisions, not requirements from the assignment PDF.** They sit at level L3 of the precedence hierarchy, alongside the design decisions. None of them adds, removes or changes an eligibility criterion, and none changes the handoff guard.

### 7.1 Decided

### PD-01 — Clarification limit

- **Status:** Decided. Project prompt-policy decision; not from the assignment PDF.

**The assignment has exactly seven eligibility points. Internal tracking may count sub-values separately for clarification purposes, but those sub-values do not create additional eligibility points.**

**The final handoff gate remains exactly seven assignment eligibility points; clarification tracking must never increase that number.**

PD-01 counts clarification attempts. To do that it tracks smaller items than the assignment's eligibility points. The counting model distinguishes three things, and they are kept apart throughout the specification:

| Term | Meaning | How many |
|---|---|---|
| **Assignment eligibility point** | One of the seven data points the assignment requires (REQ-EL-01 to REQ-EL-07). This is the only thing the final handoff gate counts. | Exactly seven, fixed by the assignment |
| **Internal clarification-tracking sub-value** | A required sub-value of an eligibility point, tracked internally and used only to count clarification attempts. A sub-value does **not** create an additional eligibility point. | Points 1, 2, 3, 4, 6 and 7 have one sub-value each; point 5 has two |
| **Branch-specific confirmation** | A required response that exists only inside a branch of the call. There is one: the customer's response to whether they want to proceed with the maximum allowed amount, in the more-than-75-Lakhs branch. It is **not** an eighth eligibility point and must never change the final seven-point handoff gate; it is how point 4 obtains its value in that branch. | None, or one, per call |

A **tracked item** is an internal clarification-tracking sub-value or a branch-specific confirmation. Clarifications are counted per tracked item. "Tracked item" is a counting term only.

- **Point 5 is one assignment eligibility point: Occupation & Income Mode.**
  - Occupation and income mode may be tracked separately for clarification attempts.
  - Together they satisfy one assignment eligibility point.
  - Point 5 is complete only when both required sub-values are established.
- **Decision:** For each tracked item:
  1. The customer's first response after the agent asks for it is the **initial attempt**.
  2. If that response is unclear, incomplete, or does not map to an accepted category, the agent makes **exactly one** natural clarification or re-ask for that tracked item.
  3. If it still cannot be established from the response to that clarification, the call enters the **INCOMPLETE** outcome.
  4. The customer is not called disqualified unless an explicit documented disqualifying criterion was actually provided.
- **Counting rules:**
  - **Per tracked item, not per call.**
  - **Counts as a failed attempt:** an unclear or filler-only reply, an incomplete reply, a reply that fits no accepted category, "I don't know", and a refusal.
  - **Does not consume an attempt:** a customer question, an interruption, or a remark that is not a response to the question. The agent addresses it and asks again.
  - **Not before it is asked.** Unclear information volunteered before its point is asked does not count; the point is asked in its turn.
  - **A usable answer always wins.** At either attempt, a response that establishes the item is captured and evaluated normally, so it can still lead to disqualification, transfer or the loan-amount limit step.
  - **Point 5.** A reply giving only one sub-value establishes that sub-value. The follow-up for the missing sub-value is the one re-ask for it. Point 5 is not complete until both are established.
  - **Proceed-with-maximum.** An unclear reply to the confirmation gets one re-ask of the confirmation. Throughout, point 4 stays unanswered: it is answered only when the customer accepts the maximum (75 Lakhs is recorded) or gives another amount of 75 Lakhs or less. A refusal of the maximum is not an unclear reply; it follows DD-01.
- **What stays distinct, and where it is tested:**

| Concern | What it measures | Scenarios |
|---|---|---|
| Internal clarification-tracking sub-values | How many times a tracked item has been asked after a failed response | TS-V1, TS-V2, TS-V3, TS-V4, TS-W1, TS-W2, TS-W3, TS-P2, TS-P3 |
| Assignment eligibility points | Whether each of the seven points is complete, which is all the handoff gate looks at | TS-I2, TS-I3, TS-S1, TS-S2, TS-S3, TS-G2, TS-H2 |
| Branch-specific confirmations | The proceed-with-maximum response, which never becomes a point of its own | TS-E1, TS-E2, TS-E4, TS-E5 |

- **Resolves:** the unquantified "reasonable clarification" in DD-11 and "ask again naturally" in DD-07; contradiction C-7.
- **Business rules:** BR-PD-01; refines BR-DD-06, BR-DD-07, BR-DD-11. BR-HO-01 and BR-EL-05a are unchanged.
- **Transitions:** T-07, T-20, T-21 (first failed attempt), T-25 (second), T-19. The guard on T-12 is unchanged.
- **Test scenarios:** TS-V1, TS-V2, TS-V3, TS-V4, TS-W1, TS-W2, TS-W3, TS-P2, TS-P3, TS-I2, TS-I3, TS-E4, TS-E5; GF-9.

### PD-02 — Priority of competing signals

- **Status:** Decided. Project-level precedence; not PDF-derived behaviour. Only "transfer above disqualification" was previously approved (DD-02), and it is preserved.
- **Decision:** When a single customer utterance contains more than one of these signals, the agent acts on the highest-ranked one only:
  1. **TRANSFER**
  2. **DISQUALIFICATION**
  3. **NOT_INTERESTED**
  4. **BUSY / CALLBACK**
  5. **NORMAL ELIGIBILITY FLOW**
- **Consequences:**
  - Busy never overrides an explicit transfer or disqualification signal in the same utterance.
  - A clear not-interested response ends the interaction; it does not start a callback.
  - The agent gives one outcome and one closing message, never two.
- **Scope:** applies once the customer is verified. Before verification, DD-16 still governs: no transfer or disqualification response is given, so the busy path and the wrong-person path are the only ones that can act.
- **Resolves:** pending rank in the per-turn order; contradiction C-8.
- **Business rules:** BR-PD-02; preserves BR-DD-02.
- **Transitions:** T-11, then T-10, then T-18, then T-24 or T-04, then T-06.
- **Test scenarios:** TS-M3, TS-Z1, TS-Z2, TS-Z3, TS-Z4, TS-Z5.

### PD-03 — Closing and termination behaviour

- **Status:** Decided. Project prompt-policy decision; not from the assignment PDF, except where a message is quoted from it.
- **Decision:** Platform-neutral behaviour for these outcomes:

| Outcome | The agent |
|---|---|
| **DISQUALIFIED** | Explains politely that the customer does not meet the criteria for this specific offer at this time. Does not expose internal rule names or implementation details. Thanks the customer. Ends the current interaction. |
| **TRANSFER** | Explains that a specialist for loan transfer will contact the customer shortly. Thanks the customer. Ends the current interaction. |
| **NOT_INTERESTED** | Acknowledges the decision. Thanks the customer. Ends the current interaction. |
| **INCOMPLETE** | Explains that the required information could not be established. Does not call the customer ineligible. Thanks the customer. Ends the current interaction. |
| **BUSY** | Acknowledges the customer's time constraint. Asks for a preferred callback time. If no callback time is provided, follows DD-13. Does not continue qualification in the current interaction. |

- **Platform neutrality:** "ends the current interaction" means the agent's turn is its last and it asks nothing further. How the call is technically disconnected is left to the voice platform (PD-09).
- **From the assignment:** the disqualification message and the transfer message themselves (REQ-BL-01, REQ-BL-04) and asking for a callback time (REQ-CS-02). Thanking the customer, withholding internal rule names, and the incomplete and not-interested closings are decided here.
- **Not covered:** the qualified handoff, a declined maximum amount, a wrong person, an accepted callback time and a missing callback time keep the behaviour already documented; whether they also carry thanks is PD-13.
- **Business rules:** BR-PD-03; applies to BR-DQ-07, BR-TR-04, BR-DD-09, BR-DD-11, BR-CB-01, BR-CB-02.
- **Transitions:** T-14, T-15, T-19, T-04, T-24, T-13, T-27.
- **Test scenarios:** every scenario ending DISQUALIFIED, TRANSFER, NOT_INTERESTED or INCOMPLETE; TS-B1, TS-B3, TS-B4; GF-8.

### 7.2 Pending

These are still undecided. None of them changes who is eligible. System Prompt V1 was written with a conservative project default for each; the defaults are listed, and the material ones flagged, in [system-prompt-traceability.md](system-prompt-traceability.md), section 5. A default there is not an approved decision.

| ID | Decision needed | Sections affected | Related |
|---|---|---|---|
| PD-04 | Whether and how the agent discloses that it is an AI, and any recording or regulatory statement. | PS-01 | AMB-20 |
| PD-05 | Hindi output form for speech (script, register, how amounts are said) and the allowed values of `agent_gender`. | PS-17, PS-18 | AMB-21 |
| PD-06 | Output contract: spoken reply only, or also a structured record of the outcome and captured values for the senior loan expert; whether details are recapped at handoff. | PS-06, PS-22, PS-24 | AMB-18 |
| PD-07 | Transfer trigger scope: a loan or EMI that is not on this property, and whether the agent ever asks about existing loans. | PS-12 | AMB-12 |
| PD-08 | Identity: what counts as confirmation when the reply is ambiguous, how many attempts, what the agent may say about the reason for the call before confirmation, and what happens if the person declines before being verified. | PS-04 | DD-03, DD-12 |
| PD-09 | Variable injection syntax, the form in which `conversation_history` arrives, and how the call is technically ended. These depend on the voice platform. | PS-02, PS-20, PS-24 | AMB-19, AMB-21 |
| PD-10 | Silence, no response, voicemail and dropped calls. This depends on the voice platform. | PS-21, PS-24 | AMB-24 |
| PD-11 | How "pre-approved" is worded in the offer. | PS-05 | AMB-20, C-5 |
| PD-12 | Whether the disqualification message may give the reason in plain language. PD-03 rules out internal rule names and implementation details but does not say either way. | PS-11 | PD-03 |
| PD-13 | Closing for the outcomes PD-03 does not cover: qualified handoff, declined maximum, wrong person, accepted callback time, no callback time. | PS-23, PS-24 | PD-03 |

## 8. Out of scope for this document

- The prompt text itself.
- Voice-platform configuration (voice, interruption sensitivity, end-of-call tooling).
- Any agent or application code.
- A runner or judge for the evaluation fixtures.
