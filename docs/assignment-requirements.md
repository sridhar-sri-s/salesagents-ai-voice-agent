# Assignment Requirements

Formal requirements specification for the SalesAgents AI Voice Agent assignment.

- **Authoritative source:** *SalesAgents AI Hiring Assignment — "Assignment: Voice Agent Design"* (PDF, 5 pages). Section references below (`§1`–`§6`) refer to that document.
- **Scope of this document:** requirements only. It contains no system prompt, no platform integration and no application code.
- **Related documents:** [business-rules.md](business-rules.md), [conversation-state-model.md](conversation-state-model.md), [test-scenarios.md](test-scenarios.md), [design-decisions.md](design-decisions.md).

## Conventions

| Marker | Meaning |
|---|---|
| **Source** | Stated in the assignment PDF. |
| **Clarified** | Not worded this way in the PDF, but stated by the project owner in the requirements brief as the intended reading. |
| **Derived** | A logical consequence of source requirements, recorded so it can be tested. Not a new business rule. |
| `AMB-nn` | An ambiguity or unspecified point. See [section 9](#9-ambiguities-and-unspecified-information). The assignment does not decide it. |
| `DD-nn` | A project design decision that chooses a behaviour for an `AMB` point. Defined in [design-decisions.md](design-decisions.md). **Never a source requirement.** |

Amounts are written as the source writes them: `75,00,000 (75 Lakhs)`.

## 1. Use case (§1)

| ID | Requirement | Type |
|---|---|---|
| REQ-UC-01 | The use case is Home Credit Loan Against Property (LAP) qualification. | Source |
| REQ-UC-02 | An automated AI Voice Agent for "Home Credit" contacts the company's existing, valued customers. | Source |
| REQ-UC-03 | The agent's primary purpose is to inform the customer of a pre-approved LAP offer and conduct a preliminary eligibility check. | Source |
| REQ-UC-04 | The conversation must feel natural, professional and advisory. | Source |
| REQ-UC-05 | The agent is the first point of contact and "qualifies" the lead; qualified customers are transitioned to a senior human loan expert who finalizes the application. | Source |

## 2. Call stages (§2A, §2B)

| ID | Requirement | Type |
|---|---|---|
| REQ-CS-01 | Greeting and identification: verify that the agent is speaking with the correct customer. | Source |
| REQ-CS-02 | If the customer is busy, acknowledge this and ask for a preferred callback time. | Source |
| REQ-CS-03 | Present the offer only once the customer is verified. | Source |
| REQ-CS-04 | The offer presentation explains the reason for the call: rewarding the customer's loyalty with a special Loan Against Property offer of up to 75,00,000 (75 Lakhs). | Source |

## 3. Eligibility checklist (§2C)

| ID | Requirement | Type |
|---|---|---|
| REQ-EL-00 | The agent gathers 7 specific data points to determine whether the customer qualifies, and captures them sequentially (in the order 1–7 below). | Source |
| REQ-EL-01 | **Property Type.** Confirm whether the property is Residential (house/flat), Commercial (shop/office) or Industrial (factory). Only Residential, Commercial and Industrial are eligible. Agricultural is not eligible. | Source |
| REQ-EL-02 | **Ownership Status.** Find out whether the customer is the sole owner or it is a joint property (with family/partners). Both Sole and Joint ownership are eligible. | Source |
| REQ-EL-03 | **Document Availability.** Confirm whether the customer has the original property documents ready for verification. Original documents must be available to proceed; if unavailable, the customer is not eligible. | Source (ineligibility wording: Clarified) |
| REQ-EL-04 | **Loan Amount.** Ask how much money the customer is looking to borrow. The amount must be 75,00,000 (75 Lakhs) or less. See REQ-BL-03 for amounts above the limit. | Source |
| REQ-EL-05 | **Occupation & Income Mode.** Determine whether the customer is Salaried (has a job) or Self-Employed (runs a business), and whether income is received in the bank or in cash. Both Salaried and Self-Employed are eligible, but income must be received via Bank. Cash income is not eligible. | Source |
| REQ-EL-06 | **Market Value.** Get an estimated current market value of the property. The assignment gives no eligibility threshold for this value; none is to be applied. | Source (no-threshold note: Clarified) |
| REQ-EL-07 | **Tenure.** Ask how many years the customer would like to take to repay the loan. The repayment period must be between 3 and 15 years (minimum 3, maximum 15). Outside that range is not eligible. | Source (min/max wording: Clarified) |
| REQ-OO-01 | If the customer provides a detail out of order, the agent must note it and must not ask that specific question again. | Source |
| REQ-OO-02 | After capturing an out-of-order detail, the agent remembers it and continues with the next unanswered required point. | Clarified |

## 4. Business logic and boundaries (§3, §5)

| ID | Requirement | Type |
|---|---|---|
| REQ-BL-01 | **Immediate disqualification.** At any point in the conversation, if the customer provides an answer that does not meet the eligibility criteria (e.g. income in cash, agricultural property), the agent must politely inform them that they do not meet the criteria for this specific offer at this time and end the call. | Source |
| REQ-BL-02 | After a disqualifying answer the agent does not continue asking the remaining eligibility questions. | Clarified |
| REQ-BL-03 | **Loan amount limits.** If the customer requests more than 75 Lakhs, the agent explains the limit and asks whether they would like to proceed with the maximum allowed amount. | Source |
| REQ-BL-04 | **Transfer logic switch.** The standard flow is for a "Fresh Loan". If the customer mentions they already have an existing loan on the property, or want to reduce their current EMI, the agent must inform the customer that a specialist for loan transfer will contact them shortly and then end the call. | Source |
| REQ-BL-05 | **Post-qualification handoff.** Once all 7 points are answered and the criteria are met, the agent informs the customer that a senior loan expert will call them back shortly to provide exact interest rates. | Source |
| REQ-BL-06 | **Handoff gate.** The agent can only move to the final handoff once all eligibility questions are asked and answered. If any were skipped earlier due to a diversion, the agent must go back and ask them. | Source |
| REQ-BL-07 | Exact interest rates are provided by the senior loan expert. The agent does not invent or commit to an exact rate. Whether it may relay rate information found in `additional_context_from_rag` is not specified (AMB-17). | First sentence: Source (§3). Second: Derived from REQ-BL-05 |

## 5. Prompt variables (§4)

The system prompt logic must account for each of these variables.

| ID | Variable | Source description |
|---|---|---|
| REQ-PV-01 | `company_name` | Name of the company. |
| REQ-PV-02 | `customer_name` | The name of the customer being called. |
| REQ-PV-03 | `agent_name` | The agent's name as the AI assistant. |
| REQ-PV-04 | `agent_gender` | The agent's gender. Must be adhered to strictly. |
| REQ-PV-05 | `current_date` | For context. |
| REQ-PV-06 | `current_day` | For context. |
| REQ-PV-07 | `current_time` | For context. |
| REQ-PV-08 | `additional_context_from_rag` | Specific product knowledge retrieved. |
| REQ-PV-09 | `language_to_speak` | The language the agent must use (English or Hindi). |
| REQ-PV-10 | `conversation_history` | The log of the current chat. |
| REQ-PV-11 | `customer_utterance` | The latest thing the customer said. |

## 6. Natural conversation and quality (§5)

| ID | Requirement | Type |
|---|---|---|
| REQ-NC-01 | The agent must not be designed to handle only "Yes"/"No" answers; it must handle full-sentence answers. | Source |
| REQ-NC-02 | The agent must handle interruptions. | Source |
| REQ-NC-03 | The agent must handle conversational fillers. | Source |
| REQ-NC-04 | The agent speaks English or Hindi according to `language_to_speak`. | Source |
| REQ-NC-05 | The focus is absolute accuracy and coverage of every edge case (disqualifications, transfers, busy states). There is no limit on system prompt length. | Source |
| REQ-NC-06 | Testing is done by talking like real customers. | Source |

## 7. Testing and submission (§6)

Recorded for completeness. **Out of scope for the current phase.**

| ID | Requirement | Type |
|---|---|---|
| REQ-SB-01 | Implement the prompt on a voice platform of choice (Retell AI, Bolna or similar): create an agent, paste the system prompt into the instructions, select a professional voice. | Source |
| REQ-SB-02 | Conduct multiple calls acting like a real customer to test logic accuracy across different scenarios. | Source |
| REQ-SB-03 | Submit the system prompt text and a public link to the call recording and call logs (audio + transcript). | Source |

## 8. Traceability table

Rule IDs (`BR-*`) are defined in [business-rules.md](business-rules.md); scenario IDs (`TS-*`) in [test-scenarios.md](test-scenarios.md).

| Requirement ID | Source requirement | Implementation implication | Test scenario IDs |
|---|---|---|---|
| REQ-UC-01 | §1 — Home Credit LAP qualification | Agent's domain is limited to the LAP offer and its qualification. | TS-A1 |
| REQ-UC-02 | §1 — AI voice agent contacts existing customers | Call is outbound; agent opens the call and addresses a named existing customer. | TS-A1 |
| REQ-UC-03 | §1 — inform of pre-approved offer, preliminary eligibility check | Call has two jobs in order: present offer, then collect eligibility data. | TS-A1 |
| REQ-UC-04 | §1 — natural, professional, advisory | Tone constraint on every agent turn (BR-CC-01). | TS-A1, TS-P1, TS-O1 |
| REQ-UC-05 | §1 — first point of contact; senior human expert finalizes | Agent never finalizes an application; the positive outcome is a handoff. | TS-A1, TS-S1 |
| REQ-CS-01 | §2A — verify correct customer | Identity must be verified before any offer content (BR-CC-07). | TS-A1, TS-B1 |
| REQ-CS-02 | §2A — busy: acknowledge, ask callback time | Busy detection leads to the callback path (BR-CB-01, BR-CB-02). | TS-B1, TS-B2 |
| REQ-CS-03 | §2B — offer only once verified | Offer presentation is gated on `identity_verified` (BR-CC-07). | TS-A1, TS-B1 |
| REQ-CS-04 | §2B — loyalty reward, LAP up to 75,00,000 (75 Lakhs) | Offer statement includes the loyalty reason and the "up to 75 Lakhs" amount (BR-CC-08). | TS-A1 |
| REQ-EL-00 | §2C — 7 data points, sequentially | Default question order is 1→7; all 7 are mandatory (BR-EL-00). | TS-A1, TS-S3 |
| REQ-EL-01 | §2C.1 — property type | Residential/Commercial/Industrial continue; Agricultural disqualifies (BR-EL-01, BR-DQ-01). | TS-A1, TS-A2, TS-C1, TS-C2 |
| REQ-EL-02 | §2C.2 — ownership status | Sole and Joint both continue; no disqualifying value is named (BR-EL-02). | TS-A1, TS-K1 |
| REQ-EL-03 | §2C.3 — original documents | Available continues; unavailable disqualifies (BR-EL-03, BR-DQ-02). | TS-A1, TS-D1 |
| REQ-EL-04 | §2C.4 — loan amount ≤ 75 Lakhs | Amounts ≤ 75 Lakhs continue; above goes to the limit rule (BR-EL-04, BR-EL-04a). | TS-A1, TS-E1, TS-E2, TS-E3 |
| REQ-EL-05 | §2C.5 — occupation and income mode | Two components must both be captured; Cash disqualifies (BR-EL-05, BR-DQ-03). | TS-A1, TS-F1, TS-F2, TS-I1, TS-I2, TS-J1 |
| REQ-EL-06 | §2C.6 — market value | Captured as a value; never used to disqualify (BR-EL-06). | TS-A1, TS-S3 |
| REQ-EL-07 | §2C.7 — tenure 3–15 years | 3–15 continues; outside disqualifies (BR-EL-07, BR-DQ-04). | TS-A1, TS-G1, TS-G2, TS-H1, TS-H2 |
| REQ-OO-01 | §2C — out-of-order detail noted, not asked again | Every utterance is checked for any of the 7 points, not just the one asked (BR-CC-05). | TS-L1, TS-L2, TS-Q1 |
| REQ-OO-02 | Clarified — continue with next unanswered point | Next question is always the lowest-numbered unanswered point (BR-CC-06). | TS-L1, TS-L2, TS-Q1 |
| REQ-BL-01 | §3 — immediate disqualification, at any point | Disqualification check runs on every captured value, including out-of-order ones (BR-DQ-05, BR-DQ-06). | TS-C1, TS-C2, TS-D1, TS-F1, TS-F2, TS-G1, TS-H1, TS-Q2 |
| REQ-BL-02 | Clarified — no further questions after disqualification | Disqualification is terminal (BR-DQ-07). | TS-C1, TS-D1, TS-F1, TS-G1, TS-H1 |
| REQ-BL-03 | §3 — above 75 Lakhs: explain limit, ask about maximum | Over-limit amount is not an immediate disqualification; a confirmation step follows (BR-EL-04a). | TS-E1, TS-E2 |
| REQ-BL-04 | §3 — transfer logic switch | Existing loan on the property or wish to reduce EMI ends the fresh-loan flow (BR-TR-01–BR-TR-04). | TS-M1, TS-M2, TS-N1 |
| REQ-BL-05 | §3 — post-qualification handoff | Handoff message names a senior loan expert, a callback "shortly" and exact interest rates (BR-HO-02). | TS-A1, TS-G2, TS-H2 |
| REQ-BL-06 | §5 — handoff gate | Handoff is blocked while any of the 7 points is unanswered; skipped questions are revisited (BR-HO-01, BR-HO-03). | TS-S1, TS-S2, TS-S3 |
| REQ-BL-07 | §3, and derived from it | Agent points to the senior loan expert for exact interest rates and does not invent one (BR-HO-04). | TS-A1, TS-O1 |
| REQ-PV-01 | §4 — `company_name` | Company is referred to through the variable, not hard-coded. | TS-A1 |
| REQ-PV-02 | §4 — `customer_name` | Used for identification of the correct customer. | TS-A1, TS-B1 |
| REQ-PV-03 | §4 — `agent_name` | Agent introduces itself with this name. | TS-A1 |
| REQ-PV-04 | §4 — `agent_gender`, strict | Agent's self-references are consistent with this gender throughout. | TS-A1, TS-R1 |
| REQ-PV-05–07 | §4 — `current_date` / `current_day` / `current_time` | Available as context. The source names no specific use; a relative callback time ("tomorrow evening") is one place it applies. | TS-B2 |
| REQ-PV-08 | §4 — `additional_context_from_rag` | Product knowledge is available to the agent. How it is to be used is not specified by the source (AMB-17); the behaviour tested is set by design decision DD-10. | TS-Y1, TS-Y2 (via DD-10) |
| REQ-PV-09 | §4 — `language_to_speak` | Agent's output language is set by this variable (BR-CC-04). | TS-R1, TS-R2 |
| REQ-PV-10 | §4 — `conversation_history` | The record of what has already been asked and answered; the basis for not re-asking. | TS-L1, TS-L2, TS-S2 |
| REQ-PV-11 | §4 — `customer_utterance` | The input each turn is evaluated against. | all |
| REQ-NC-01 | §5 — full sentences, not only yes/no | Answers are extracted from free-form speech (BR-CC-02). | TS-A1, TS-Q1 |
| REQ-NC-02 | §5 — interruptions | Agent addresses the interruption, then returns to the pending point (BR-CC-03). | TS-O1, TS-O2 |
| REQ-NC-03 | §5 — conversational fillers | Fillers are not treated as answers (BR-CC-03). | TS-P1, TS-P2 |
| REQ-NC-04 | §4, §5 — English or Hindi | Same rules apply in both languages (BR-CC-04). | TS-R1, TS-R2 |
| REQ-NC-05 | §5 — accuracy, every edge case | Disqualification, transfer and busy paths each have explicit rules and tests. | TS-B1–TS-N1 |
| REQ-NC-06 | §5 — talk like real customers when testing | Test utterances are written as natural speech. | all |
| REQ-SB-01–03 | §6 — platform, test calls, submission | Out of scope for this phase. | — |

### 8.1 End-to-end chain

Requirement → business rule → state transition → test scenario, for every requirement that drives call flow. Transition IDs (`T-nn`) are defined in [conversation-state-model.md](conversation-state-model.md). Requirements that constrain *how* the agent speaks rather than *where* the call goes have no transition and show "—".

| Requirement | Business rules | Transitions | Test scenarios |
|---|---|---|---|
| REQ-CS-01 | BR-CC-07 | T-02, T-03 | TS-A1 |
| REQ-CS-02 | BR-CB-01, BR-CB-02 | T-04 | TS-B1, TS-B2 |
| REQ-CS-03, REQ-CS-04 | BR-CC-07, BR-CC-08 | T-03 | TS-A1 |
| REQ-EL-00 | BR-EL-00, BR-CC-06 | T-05, T-06 | TS-A1, TS-S3 |
| REQ-EL-01 | BR-EL-01, BR-DQ-01 | T-06, T-10 | TS-A1, TS-A2, TS-C1, TS-C2 |
| REQ-EL-02 | BR-EL-02 | T-06 | TS-A1, TS-K1 |
| REQ-EL-03 | BR-EL-03, BR-DQ-02 | T-06, T-10 | TS-A1, TS-D1 |
| REQ-EL-04, REQ-BL-03 | BR-EL-04, BR-EL-04a, BR-DQ-09 | T-06, T-08, T-09 | TS-E1, TS-E2, TS-E3 |
| REQ-EL-05 | BR-EL-05, BR-EL-05a, BR-DQ-03 | T-06, T-10 | TS-F1, TS-F2, TS-I1, TS-I2, TS-J1 |
| REQ-EL-06 | BR-EL-06, BR-EL-06a | T-06 | TS-A1, TS-P1, TS-S3 |
| REQ-EL-07 | BR-EL-07, BR-DQ-04 | T-06, T-10, T-12 | TS-G1, TS-G2, TS-H1, TS-H2 |
| REQ-OO-01, REQ-OO-02 | BR-CC-05, BR-CC-06 | T-06 | TS-L1, TS-L2, TS-Q1 |
| REQ-BL-01, REQ-BL-02 | BR-DQ-05, BR-DQ-06, BR-DQ-07, BR-DQ-08 | T-10, T-14 | TS-C1, TS-C2, TS-D1, TS-F1, TS-F2, TS-G1, TS-H1, TS-Q2 |
| REQ-BL-04 | BR-TR-01 to BR-TR-07 | T-11, T-15 | TS-M1, TS-M2, TS-N1 |
| REQ-BL-05 | BR-HO-01, BR-HO-02 | T-12, T-16 | TS-A1, TS-G2, TS-H2 |
| REQ-BL-06 | BR-HO-01, BR-HO-03, BR-HO-05 | T-07, guard on T-12 | TS-S1, TS-S2, TS-S3 |
| REQ-BL-07 | BR-HO-04 | — | TS-O1 |
| REQ-NC-01 | BR-CC-02 | — | TS-A1, TS-I1, TS-Q1 |
| REQ-NC-02, REQ-NC-03 | BR-CC-03 | T-07 | TS-O1, TS-O2, TS-P1, TS-P2 |
| REQ-NC-04, REQ-PV-09 | BR-CC-04 | — | TS-R1, TS-R2 |
| REQ-PV-01 to REQ-PV-04 | BR-CC-09, BR-CC-10 | — | TS-A1, TS-R1 |
| REQ-PV-10, REQ-PV-11 | BR-CC-11 | — | TS-L1, TS-L2, TS-S2 |

## 9. Ambiguities and unspecified information

The assignment does not specify the points below. They are not requirements, and nothing in sections 1–8 resolves them.

Where the project has chosen a behaviour for one, that choice is a **design decision** recorded in [design-decisions.md](design-decisions.md) and named in the last column. A design decision is a project choice, not something the assignment says. "Open" means no behaviour has been chosen.

| ID | Not specified by the assignment | Design decision |
|---|---|---|
| AMB-01 | **How identity is verified.** What counts as "verified" (name confirmation only, or more). `customer_name` is the only identifying variable provided. | DD-03 |
| AMB-02 | **Wrong person.** What to do if someone else answers, the customer is unavailable, or the person denies being the customer. | DD-03, DD-12 |
| AMB-03 | **Busy/callback details.** Whether "busy" applies only during the greeting or at any point; what the agent says after a callback time is given, and whether the call then ends (the source says only "acknowledge this and ask for a preferred callback time"); what happens if the customer gives no time; who calls back (AI or human); how the time is recorded; whether the time is checked against `current_date`/`current_time`. | DD-04, DD-13, DD-14 (partly) |
| AMB-04 | **Customer not interested.** What to do if the customer declines the offer or asks not to be called. | DD-09 |
| AMB-05 | **Consent to proceed.** Whether the agent needs the customer's agreement after the offer before starting the eligibility questions. | DD-15 |
| AMB-06 | **Other property types.** Handling of types outside the four named (e.g. vacant plot/land, mixed-use, under-construction). The word "Only" implies they are not eligible, but this is not stated per type. | DD-06 |
| AMB-07 | **"Documents ready for verification."** Handling when original documents exist but are not at hand, can be arranged later, or are held by another lender (which may also indicate an existing loan on the property). | DD-06 (partly) |
| AMB-08 | **Declining the maximum amount.** The outcome when the customer asks for more than 75 Lakhs and does not want to proceed with the maximum. Also unspecified: any minimum loan amount, and a customer who does not know how much they want. | DD-01, DD-07 (partly) |
| AMB-09 | **Other occupations and mixed income.** Occupations other than Salaried/Self-Employed (retired, homemaker, unemployed, etc.) and income received partly in bank and partly in cash. | DD-06 |
| AMB-10 | **Market value.** No threshold, no stated relationship to the loan amount, and no handling for a customer who does not know the value. | DD-07, DD-11 |
| AMB-11 | **Tenure details.** Whether 3 and 15 are inclusive (this specification reads "minimum 3, maximum 15" as inclusive); fractional years or answers in months; whether the customer may revise an out-of-range tenure (the loan amount has an adjustment step, tenure does not). | DD-06 (partly) |
| AMB-12 | **Transfer trigger scope.** The trigger is a customer *mention*; whether the agent should ever ask about existing loans is not stated. Also: whether it applies before identity verification; loans or EMIs unrelated to this property; which path wins if one utterance contains both a transfer trigger and a disqualifying answer. | DD-02, DD-16 (partly) |
| AMB-13 | **Disqualifying information before verification or offer.** "At any point" is stated, but the offer must only follow verification. | DD-16 |
| AMB-14 | **Corrections.** Handling when the customer changes an earlier answer, including retracting a disqualifying answer given by mistake. | DD-08 |
| AMB-15 | **Unclear, refused or "don't know" answers.** How many times to re-ask and what the outcome is if a point can never be answered. | DD-07, DD-11 |
| AMB-16 | **Language mismatch.** What to do when the customer speaks the other language, mixes Hindi and English, or asks to switch, given that `language_to_speak` is "the language you must use". | DD-05 |
| AMB-17 | **Product questions and RAG.** How far the agent may answer questions (rates, fees, process) from `additional_context_from_rag`; what to do when it is empty or conflicts with the rules here. Only "exact interest rates" are explicitly assigned to the senior expert. | DD-10, DD-17 |
| AMB-18 | **Handoff mechanics.** What "shortly" means; whether the agent recaps captured details; how captured data reaches the expert (no output format or tool call is specified). The handoff is a callback, not a live transfer. | Open |
| AMB-19 | **Ending the call.** Closing wording and the mechanism for ending the call. | Open |
| AMB-20 | **Disclosures.** AI disclosure, call-recording notice and any regulatory statements. Also the relationship between "pre-approved" and a customer who is then found not eligible. | Open |
| AMB-21 | **Variable formats.** Allowed values of `agent_gender`, formats and timezone of date/day/time, and whether `company_name` will always be "Home Credit". | Open |
| AMB-22 | **Property ownership edge cases.** Multiple properties, or a property owned by someone else (e.g. a family member) rather than solely or jointly by the customer. | DD-06 (partly) |
| AMB-23 | **Currency.** The amount is written "75,00,000 (75 Lakhs)" without a currency. | Open |
| AMB-24 | **Call-level failures.** Silence, no response, voicemail, poor audio, dropped call. | Open |
| AMB-25 | **Strictness of "sequentially".** Whether order 1→7 is mandatory when the customer does not volunteer information (this specification uses 1→7 as the default order). | Open |
