# Business Rules

Business rules for the Home Credit Loan Against Property (LAP) qualification call, extracted from the assignment.

- Requirement IDs (`REQ-*`) and ambiguity IDs (`AMB-*`) are defined in [assignment-requirements.md](assignment-requirements.md).
- Every rule traces to a requirement. Rules marked **Derived** are logical consequences recorded for testability, not additional business rules.
- Where the assignment is silent, the rule says so and cites the `AMB` ID. No answer is assumed in sections 1–7.
- Where the project has chosen a behaviour for such a point, it is a **design decision** (`DD-*`, see [design-decisions.md](design-decisions.md)). Design-decision rules appear only in [section 8](#8-design-decision-rules), never in the source-rule tables.
- Prompt-policy decisions (`PD-*`) are project decisions defined in [system-prompt-architecture.md](system-prompt-architecture.md). Their rules appear only in [section 9](#9-prompt-policy-rules).

## 1. Eligibility rules

All seven data points are mandatory. Default asking order is 1→7.

| Rule | Data point | What is captured | Eligible | Not eligible | Source |
|---|---|---|---|---|---|
| BR-EL-00 | — | All 7 points below must be captured before qualification can be decided. | — | — | REQ-EL-00 |
| BR-EL-01 | 1. Property Type | Residential (house/flat), Commercial (shop/office), Industrial (factory) or Agricultural | Residential, Commercial, Industrial | Agricultural | REQ-EL-01 |
| BR-EL-02 | 2. Ownership Status | Sole owner or joint property (with family/partners) | Sole, Joint | none specified | REQ-EL-02 |
| BR-EL-03 | 3. Document Availability | Whether original property documents are ready for verification | Original documents available | Original documents unavailable | REQ-EL-03 |
| BR-EL-04 | 4. Loan Amount | Amount the customer wants to borrow | 75,00,000 (75 Lakhs) or less | see BR-EL-04a | REQ-EL-04 |
| BR-EL-05 | 5. Occupation & Income Mode | (a) Salaried or Self-Employed, and (b) income received in bank or cash | Salaried or Self-Employed, **with** Bank income | Cash income (either occupation) | REQ-EL-05 |
| BR-EL-06 | 6. Market Value | Estimated current market value of the property | any value (capture only) | no threshold exists | REQ-EL-06 |
| BR-EL-07 | 7. Tenure | Repayment period in years | 3 to 15 years (minimum 3, maximum 15) | below 3 or above 15 | REQ-EL-07 |

**BR-EL-04a — Loan amount above the limit** (REQ-BL-03)
If the customer requests more than 75 Lakhs, the agent:
1. explains the maximum limit, and
2. asks whether the customer would like to proceed with the maximum allowed amount.

This is the one criterion with its own handling: an over-limit request is **not** an immediate disqualification. If the customer agrees, the loan amount is recorded as the maximum allowed amount (75 Lakhs) and the point is answered *(Derived from "proceed with the maximum allowed amount")*. The outcome if the customer does not agree is **not specified** by the assignment (AMB-08); design decision DD-01 covers it (BR-DD-01).

**BR-EL-05a — Point 5 has two components.** Point 5 is answered only when both occupation and income mode are known. If only one is given, the agent asks for the other.  *(Derived from REQ-EL-05.)*

**BR-EL-06a — Market value is never a disqualifier.** The assignment gives no threshold and no relationship to the loan amount; none is applied (AMB-10).

Values the assignment does not classify are listed under AMB-06 (other property types), AMB-07 (documents not at hand), AMB-09 (other occupations, mixed income), AMB-11 (tenure format) and AMB-22 (ownership edge cases). Design decision DD-06 covers how the agent responds to them (BR-DD-06).

## 2. Disqualification rules

| Rule | Trigger | Source |
|---|---|---|
| BR-DQ-01 | Property type is Agricultural. | REQ-EL-01 |
| BR-DQ-02 | Original property documents are not available. | REQ-EL-03 |
| BR-DQ-03 | Income is received in cash. | REQ-EL-05 |
| BR-DQ-04 | Tenure is less than 3 years or more than 15 years. | REQ-EL-07 |

| Rule | Behaviour | Source |
|---|---|---|
| BR-DQ-05 | Disqualification is **immediate**: it happens as soon as the non-qualifying answer is given, at any point in the conversation. | REQ-BL-01 |
| BR-DQ-06 | It applies to answers given out of order too. A disqualifying value volunteered before its question is reached still disqualifies. | Derived from REQ-BL-01 ("at any point") |
| BR-DQ-07 | On disqualification the agent politely informs the customer that they do not meet the criteria for this specific offer at this time, and ends the call. | REQ-BL-01 |
| BR-DQ-08 | No remaining eligibility questions are asked after a disqualifying answer. | REQ-BL-02 |
| BR-DQ-09 | A loan amount above 75 Lakhs is handled by BR-EL-04a, not by BR-DQ-05. | REQ-BL-03 |
| BR-DQ-10 | Ownership status (point 2) and market value (point 6) have no disqualifying value. | REQ-EL-02, REQ-EL-06 |

Not specified: disqualifying information given before identity verification (AMB-13), and a customer who retracts a disqualifying answer (AMB-14). Design decision DD-08 covers the latter (BR-DD-08).

## 3. Transfer rules

| Rule | Statement | Source |
|---|---|---|
| BR-TR-01 | The standard flow is for a "Fresh Loan". | REQ-BL-04 |
| BR-TR-02 | **Trigger 1:** the customer mentions they already have an existing loan on the property. | REQ-BL-04 |
| BR-TR-03 | **Trigger 2:** the customer mentions they want to reduce their current EMI. | REQ-BL-04 |
| BR-TR-04 | On either trigger the agent informs the customer that a specialist for loan transfer will contact them shortly, and then ends the call. | REQ-BL-04 |
| BR-TR-05 | The remaining eligibility questions are not asked, and the senior-loan-expert handoff message is not given, on the transfer path. | Derived from REQ-BL-04 ("then end the call") |
| BR-TR-06 | The trigger is a *mention* by the customer; the agent does not need to have asked about existing loans. | REQ-BL-04 |
| BR-TR-07 | A transfer outcome is not a disqualification: the customer is not told they fail the criteria. | Derived from REQ-BL-01, REQ-BL-04 |

Not specified: the trigger's scope and its priority against a simultaneous disqualifying answer (AMB-12). Design decision DD-02 covers the priority (BR-DD-02).

## 4. Callback rules

| Rule | Statement | Source |
|---|---|---|
| BR-CB-01 | If the customer is busy, the agent acknowledges this. | REQ-CS-02 |
| BR-CB-02 | The agent then asks for a preferred callback time. | REQ-CS-02 |
| BR-CB-03 | The agent does not present the offer or start eligibility questions in response to a customer saying they are busy; it asks for the callback time instead. | Derived from REQ-CS-02 |
| BR-CB-04 | `current_date`, `current_day` and `current_time` are available as context when a callback time is discussed. | REQ-PV-05–07 |

Not specified: everything after the callback time is asked for — including whether the call then ends — and whether "busy" applies beyond the greeting stage (AMB-03). Design decision DD-04 covers both (BR-DD-04).

## 5. Handoff rules

| Rule | Statement | Source |
|---|---|---|
| BR-HO-01 | **Gate.** The final handoff can occur only when (a) all seven eligibility points have been asked and answered, **and** (b) every answer meets its criterion. | REQ-BL-05, REQ-BL-06 |
| BR-HO-02 | At handoff the agent informs the customer that a senior loan expert will call them back shortly to provide exact interest rates. | REQ-BL-05 |
| BR-HO-03 | If any eligibility question was skipped earlier because of a diversion, the agent must go back and ask it before the handoff. | REQ-BL-06 |
| BR-HO-04 | Exact interest rates are provided by the senior loan expert. The agent does not invent or commit to an exact rate *(Derived)*. Relaying rate information from `additional_context_from_rag` is not specified (AMB-17). | REQ-BL-07 |
| BR-HO-05 | The agent must not finalize qualification, or tell the customer they are qualified, while any required point is unanswered — including when the customer asks to skip ahead. | REQ-BL-06 |
| BR-HO-06 | The agent qualifies the lead only; the senior human loan expert finalizes the application. | REQ-UC-05 |

Not specified: handoff timing, recap of details, and how captured data is passed on (AMB-18).

## 6. Conversational constraints

| Rule | Statement | Source |
|---|---|---|
| BR-CC-01 | The conversation must feel natural, professional and advisory. | REQ-UC-04 |
| BR-CC-02 | The agent must handle full-sentence answers and must not depend on "Yes"/"No" replies. | REQ-NC-01 |
| BR-CC-03 | The agent must handle interruptions and conversational fillers. A question left unanswered by an interruption or diversion must still be asked before the handoff (BR-HO-03). *Derived:* a filler on its own is not an answer. | REQ-NC-02, REQ-NC-03, REQ-BL-06 |
| BR-CC-04 | The agent speaks the language given by `language_to_speak` (English or Hindi). All rules in this document apply identically in both languages. | REQ-PV-09, REQ-NC-04 |
| BR-CC-05 | **Out-of-order capture.** If the customer gives a detail before its turn, the agent notes it, remembers it and does not ask that question again. | REQ-OO-01 |
| BR-CC-06 | After an out-of-order capture, the agent continues with the next unanswered required point (lowest-numbered first). | REQ-OO-02, REQ-EL-00 |
| BR-CC-07 | The offer is presented only after the customer is verified. | REQ-CS-01, REQ-CS-03 |
| BR-CC-08 | The offer is described as rewarding the customer's loyalty with a special LAP offer of **up to** 75,00,000 (75 Lakhs). | REQ-CS-04 |
| BR-CC-09 | The agent uses `agent_name`, and adheres strictly to `agent_gender`, for the whole call. | REQ-PV-03, REQ-PV-04 |
| BR-CC-10 | The agent refers to the company by `company_name` and to the customer by `customer_name`. | Derived from REQ-PV-01, REQ-PV-02 |
| BR-CC-11 | `conversation_history` is the record of what has been asked and answered; `customer_utterance` is the latest customer input. Captured details are never lost between turns. | REQ-PV-10, REQ-PV-11, REQ-OO-01 |
| BR-CC-12 | `additional_context_from_rag` is the source of specific product knowledge. | REQ-PV-08 |

Not specified: language mismatch (AMB-16), limits on answering product questions (AMB-17), unclear or refused answers (AMB-15), disclosures (AMB-20). Design decisions cover the first three: DD-05, DD-10 and DD-07.

## 7. Rule precedence

Only the orderings below follow from the assignment.

1. **Identity before offer.** No offer content before verification (BR-CC-07).
2. **Disqualification is immediate** and overrides continuing the checklist (BR-DQ-05, BR-DQ-08).
3. **Transfer ends the fresh-loan flow** (BR-TR-04, BR-TR-05).
4. **The loan-amount limit rule overrides immediate disqualification** for point 4 only (BR-DQ-09).
5. **The handoff gate overrides any attempt to finish early** (BR-HO-01, BR-HO-05).

The relative priority of transfer and disqualification when both arise in the same utterance is **not specified** by the assignment (AMB-12). Design decision DD-02 gives the transfer path priority (BR-DD-02).

Also by design decision, not by the assignment: the rules in sections 1–5 take precedence over `additional_context_from_rag` (DD-17, BR-DD-17), and no offer, disqualification or transfer message is given before the customer is verified (DD-16, BR-DD-16).

By prompt-policy decision PD-02 (project-level, not PDF-derived), when one utterance carries several signals they rank: transfer, disqualification, not interested, busy, normal eligibility flow (BR-PD-02).

## 8. Design-decision rules

> **These rules are project design decisions, not requirements from the assignment PDF.** Each one fills a gap the assignment leaves. Full reasoning is in [design-decisions.md](design-decisions.md). None of them adds, removes or changes an eligibility criterion.

| Rule | Statement | Decision | Fills |
|---|---|---|---|
| BR-DD-01 | If the customer does not want to proceed with the maximum allowed amount after being told their requested amount exceeds 75 Lakhs, the agent respects the decision and ends the call without qualification. | DD-01 | AMB-08 |
| BR-DD-02 | If the customer explicitly indicates an existing loan on the property, or wanting to reduce their current EMI, the agent routes to the specialist for loan transfer and does not continue fresh-loan eligibility qualification, even if the same utterance contains a disqualifying answer. | DD-02 | AMB-12 |
| BR-DD-03 | The agent does not disclose the LAP offer or eligibility details until the intended customer is confirmed, and does not ask for identity-verification data the assignment does not provide for. | DD-03 | AMB-01, AMB-02 |
| BR-DD-04 | Once a busy customer's callback request is accepted, the agent does not continue the qualification flow in that interaction; the interaction ends. This applies whenever the customer says they are busy, not only at the greeting. | DD-04 | AMB-03 |
| BR-DD-05 | The agent's response language is always `language_to_speak`; it does not switch because the customer responds in another language. It may understand mixed-language customer speech where technically possible. | DD-05 | AMB-16 |
| BR-DD-06 | When an answer does not clearly map to the assignment's accepted categories, the agent asks a clarification question. It does not infer eligibility and does not create new categories. | DD-06 | AMB-06, AMB-07, AMB-09, AMB-11, AMB-22 |
| BR-DD-07 | When the customer does not provide a required value, the agent explains that it is needed for preliminary qualification and asks again naturally. If the fact still cannot be established, the customer is not qualified and not handed off. This is not a disqualification criterion. | DD-07 | AMB-08, AMB-10, AMB-15 |
| BR-DD-08 | The customer's latest explicit correction replaces the earlier answer while the conversation is active, and is checked against its criterion like any captured value. Once the call has entered disqualification, transfer or termination, the flow is not reopened. | DD-08 | AMB-14 |
| BR-DD-09 | If the customer clearly declines the offer, the agent acknowledges the decision and ends the interaction politely, without continuing qualification or handing off. | DD-09 | AMB-04 |
| BR-DD-10 | The agent uses `additional_context_from_rag` only when relevant and does not invent information outside it. It does not invent or commit to an exact interest rate; exact interest rates remain with the senior loan expert (the last clause restates REQ-BL-05). | DD-10 | AMB-17 |
| BR-DD-11 | If a required fact cannot be established after reasonable clarification, the agent closes the interaction politely without qualifying the customer. The customer is not called ineligible unless an explicit disqualifying criterion was actually provided, and the outcome is recorded separately from a disqualification. | DD-11 | AMB-15 |
| BR-DD-12 | If the person answering is not the intended customer, the agent discloses neither the LAP offer nor eligibility information. It asks to speak with the intended customer where appropriate, and otherwise closes the interaction. No additional identity-verification requirement is introduced. | DD-12 | AMB-02 |
| BR-DD-13 | If a busy customer cannot provide a preferred callback time, the agent closes politely without qualification. | DD-13 | AMB-03 |
| BR-DD-14 | The agent relies only on information actually available through `conversation_history` or supplied customer/context data. Answers from a previous interaction that are not available there are treated as unanswered. | DD-14 | AMB-03 |
| BR-DD-15 | There is no separate mandatory "consent to proceed" question. A customer who clearly declines participation, or does not want the offer or the process, follows the not-interested path (BR-DD-09). | DD-15 | AMB-05 |
| BR-DD-16 | Before the intended customer is verified, the agent discloses no offer or eligibility details, including in response to offer-related information the customer volunteers. Such information is preserved only if useful for the later verified interaction and technically available in the conversation state; once the customer is verified it is checked like any other out-of-order detail. | DD-16 | AMB-12, AMB-13 |
| BR-DD-17 | The assignment's eligibility and business rules take precedence over `additional_context_from_rag`. Retrieved context must not override or add eligibility criteria and must not justify inventing facts. | DD-17 | AMB-17 |

## 9. Prompt-policy rules

> **These rules are project prompt-policy decisions, not requirements from the assignment PDF.** They are defined in [system-prompt-architecture.md](system-prompt-architecture.md), section 7.1. None of them adds, removes or changes an eligibility criterion or the handoff gate.

| Rule | Statement | Decision | Refines |
|---|---|---|---|
| BR-PD-01 | **Clarification limit.** The customer's first response to a question is the initial attempt. If it is unclear, incomplete or maps to no accepted category, the agent makes exactly one clarification or re-ask for that tracked item. If it still cannot be established, the outcome is incomplete. A customer question or interruption does not consume an attempt, and a usable answer is always accepted. The customer is never called disqualified unless a documented disqualifying criterion was actually provided. | PD-01 | BR-DD-06, BR-DD-07, BR-DD-11 |
| BR-PD-01a | **Tracking is not eligibility.** The assignment has exactly seven eligibility points. Internal tracking may count sub-values separately for clarification purposes, but those sub-values do not create additional eligibility points. A tracked item is either an *internal clarification-tracking sub-value* or a *branch-specific confirmation*. Occupation and income mode may be tracked separately for clarification attempts, but together they satisfy one assignment eligibility point, Occupation & Income Mode, which is complete only when both required sub-values are established (BR-EL-05a). The customer's response to whether they want to proceed with the maximum allowed amount is a branch-specific confirmation that arises only above 75 Lakhs; it is not an eighth eligibility point (BR-EL-04a). The final handoff gate remains exactly seven assignment eligibility points; clarification tracking must never increase that number (BR-HO-01). | PD-01 | BR-EL-04a, BR-EL-05a, BR-HO-01 |
| BR-PD-02 | **Signal precedence.** When one utterance from a verified customer contains several signals, the agent acts on the highest-ranked only: (1) transfer, (2) disqualification, (3) not interested, (4) busy/callback, (5) normal eligibility flow. | PD-02 | BR-DD-02, BR-DD-04, BR-DD-09 |
| BR-PD-03 | **Closing.** Disqualified: polite explanation that the customer does not meet the criteria for this specific offer at this time, no internal rule names or implementation details, thanks, end. Transfer: specialist-for-loan-transfer message, thanks, end. Not interested: acknowledge, thanks, end. Incomplete: explain that the required information could not be established, never call the customer ineligible, thanks, end. Busy: acknowledge, ask for a preferred callback time, no further qualification in the interaction. How the call is technically ended is left to the voice platform. | PD-03 | BR-DQ-07, BR-TR-04, BR-DD-09, BR-DD-11, BR-CB-01, BR-CB-02 |
