# System Prompt V1 — Traceability

Engineering reference for [`prompts/system_prompt_v1.md`](../prompts/system_prompt_v1.md). It maps each section of the prompt back to the specification.

**This document is not part of the prompt and must never be pasted into a voice platform.** The prompt itself contains no requirement, rule, decision, transition or scenario IDs, so that none can be spoken to a customer.

- Requirements (`REQ-*`): [assignment-requirements.md](assignment-requirements.md)
- Business rules (`BR-*`): [business-rules.md](business-rules.md)
- Design decisions (`DD-*`): [design-decisions.md](design-decisions.md)
- Prompt-policy decisions (`PD-*`) and prompt sections (`PS-*`): [system-prompt-architecture.md](system-prompt-architecture.md)
- Transitions (`T-nn`): [conversation-state-model.md](conversation-state-model.md)
- Scenarios (`TS-*`): [test-scenarios.md](test-scenarios.md)

## 1. Section map

The prompt has 25 numbered sections. The architecture defined 24 prompt sections (`PS-01` to `PS-24`); the prompt regroups them as below. "Origin" says whether the section's content comes from the assignment PDF or from a project decision. Design decisions (`DD`) and prompt-policy decisions (`PD`) are project choices, never assignment requirements.

| # | Prompt section | Architecture | Origin |
|---|---|---|---|
| 1 | ROLE AND OBJECTIVE | PS-01 | Assignment |
| 2 | RUNTIME CONTEXT | PS-02 | Assignment; data-not-instructions rule from DD-17 |
| 3 | PRIORITY / PRECEDENCE | PS-03, PS-06 | Mixed: criteria and gate from the assignment; signal ranking is PD-02 |
| 4 | IDENTITY VERIFICATION | PS-04 | Verification from the assignment; everything about what may be said is DD-03, DD-12, DD-16 |
| 5 | GREETING | PS-01, PS-04, PS-20 | Assignment |
| 6 | OFFER PRESENTATION | PS-05 | Offer from the assignment; no consent gate is DD-15 |
| 7 | ELIGIBILITY STATE | PS-07 | Assignment; declined maximum is DD-01; unclassified answers DD-06 |
| 8 | SEQUENTIAL COLLECTION | PS-08 | Assignment |
| 9 | OUT-OF-ORDER CAPTURE | PS-09 | Assignment; before-verification handling is DD-16 |
| 10 | INTERNAL CLARIFICATION MODEL | PS-14, PS-15 | Project decision (PD-01, DD-06, DD-07, DD-11) |
| 11 | CORRECTIONS | PS-10 | Project decision (DD-08) |
| 12 | TRANSFER | PS-12 | Assignment; rank is DD-02 and PD-02; thanks and closing are PD-03 |
| 13 | DISQUALIFICATION | PS-11 | Assignment; rank is PD-02; thanks and no internal names are PD-03 |
| 14 | BUSY / CALLBACK | PS-13 | Asking for a callback time is from the assignment; everything after is DD-04, DD-13 |
| 15 | NOT INTERESTED | PS-16 | Project decision (DD-09, DD-15, PD-02, PD-03) |
| 16 | UNKNOWN / UNCLASSIFIED ANSWERS | PS-14, PS-15 | Project decision (DD-06, DD-07, DD-11, PD-01, PD-03) |
| 17 | LANGUAGE | PS-17 | Assignment; not switching and mixed-language understanding are DD-05 |
| 18 | AGENT GENDER | PS-18 | Assignment |
| 19 | RAG | PS-19 | Variable from the assignment; usage limits are DD-10, DD-17 |
| 20 | CONVERSATION HISTORY | PS-20, PS-06 | Assignment; nothing assumed from earlier calls is DD-14 |
| 21 | NATURAL CONVERSATION | PS-21 | Assignment |
| 22 | HANDOFF GATE | PS-22 | Assignment; seven-points wording reinforced by PD-01 |
| 23 | QUALIFIED HANDOFF | PS-22, PS-24 | Assignment |
| 24 | TERMINAL STATES | PS-23, PS-24 | Three endings from the assignment (qualified, disqualified, transfer); the rest are project decisions |
| 25 | FINAL RESPONSE POLICY | PS-21, PS-24 | Assignment for language, name, gender and tone; no internal details is PD-03 |

## 2. Section traceability

### 1. ROLE AND OBJECTIVE

- **Architecture sections:** PS-01
- **REQ:** REQ-UC-01, REQ-UC-02, REQ-UC-03, REQ-UC-04, REQ-UC-05, REQ-PV-01, REQ-PV-02, REQ-PV-03, REQ-PV-04
- **BR:** BR-CC-01, BR-CC-09, BR-CC-10, BR-HO-06
- **DD:** —
- **PD:** —
- **T:** T-01
- **TS:** TS-A1

### 2. RUNTIME CONTEXT

- **Architecture sections:** PS-02
- **REQ:** REQ-PV-01, REQ-PV-02, REQ-PV-03, REQ-PV-04, REQ-PV-05, REQ-PV-06, REQ-PV-07, REQ-PV-08, REQ-PV-09, REQ-PV-10, REQ-PV-11
- **BR:** BR-CC-09, BR-CC-10, BR-CC-11, BR-CC-12, BR-CB-04
- **DD:** DD-10, DD-14, DD-17
- **PD:** —
- **T:** T-01
- **TS:** TS-A1, TS-B2, TS-B5, TS-R1, TS-Y1

### 3. PRIORITY / PRECEDENCE

- **Architecture sections:** PS-03, PS-06
- **REQ:** REQ-BL-01, REQ-BL-03, REQ-BL-04, REQ-BL-06, REQ-CS-03
- **BR:** BR-DQ-05, BR-DQ-09, BR-TR-04, BR-HO-01, BR-HO-05, BR-CC-07, BR-EL-06a, BR-DD-02, BR-DD-08, BR-DD-11, BR-DD-16, BR-DD-17, BR-PD-02
- **DD:** DD-02, DD-08, DD-11, DD-16, DD-17
- **PD:** PD-02
- **T:** T-04, T-10, T-11, T-12, T-18, T-24
- **TS:** TS-M3, TS-Q2, TS-Y3, TS-T3, TS-E1, TS-S1, TS-Z1, TS-Z2, TS-Z3, TS-Z4, TS-Z5

### 4. IDENTITY VERIFICATION

- **Architecture sections:** PS-04
- **REQ:** REQ-CS-01, REQ-CS-03, REQ-PV-02
- **BR:** BR-CC-07, BR-DD-03, BR-DD-12, BR-DD-16
- **DD:** DD-03, DD-12, DD-16
- **PD:** PD-02
- **T:** T-02, T-03, T-04, T-23, T-26, T-28
- **TS:** TS-A1, TS-B1, TS-B5, TS-T1, TS-T2, TS-T3

### 5. GREETING

- **Architecture sections:** PS-01, PS-04, PS-20
- **REQ:** REQ-UC-02, REQ-UC-04, REQ-CS-01, REQ-PV-01, REQ-PV-02, REQ-PV-03
- **BR:** BR-CC-01, BR-CC-07, BR-CC-09, BR-CC-10
- **DD:** DD-03
- **PD:** —
- **T:** T-01, T-02
- **TS:** TS-A1, TS-B5

### 6. OFFER PRESENTATION

- **Architecture sections:** PS-05
- **REQ:** REQ-CS-03, REQ-CS-04, REQ-UC-03
- **BR:** BR-CC-07, BR-CC-08, BR-DD-09, BR-DD-10, BR-DD-15
- **DD:** DD-09, DD-10, DD-15
- **PD:** —
- **T:** T-03, T-05, T-18
- **TS:** TS-A1, TS-U1, TS-U2, TS-L2, TS-C2, TS-N1

### 7. ELIGIBILITY STATE

- **Architecture sections:** PS-07
- **REQ:** REQ-EL-00, REQ-EL-01, REQ-EL-02, REQ-EL-03, REQ-EL-04, REQ-EL-05, REQ-EL-06, REQ-EL-07, REQ-BL-03
- **BR:** BR-EL-00, BR-EL-01, BR-EL-02, BR-EL-03, BR-EL-04, BR-EL-04a, BR-EL-05, BR-EL-05a, BR-EL-06, BR-EL-06a, BR-EL-07, BR-DQ-09, BR-DQ-10, BR-DD-01, BR-DD-06, BR-PD-01a
- **DD:** DD-01, DD-06
- **PD:** PD-01
- **T:** T-06, T-08, T-09, T-17
- **TS:** TS-A1, TS-A2, TS-K1, TS-E1, TS-E2, TS-E3, TS-E4, TS-E5, TS-I1, TS-I2, TS-I3, TS-J1, TS-G2, TS-H2, TS-P1, TS-F1, TS-F2, TS-D1

### 8. SEQUENTIAL COLLECTION

- **Architecture sections:** PS-08
- **REQ:** REQ-EL-00, REQ-OO-02, REQ-BL-06
- **BR:** BR-EL-00, BR-CC-03, BR-CC-06, BR-HO-03, BR-DD-15
- **DD:** DD-15
- **PD:** —
- **T:** T-05, T-06, T-07
- **TS:** TS-A1, TS-L1, TS-O1, TS-S3

### 9. OUT-OF-ORDER CAPTURE

- **Architecture sections:** PS-09
- **REQ:** REQ-OO-01, REQ-OO-02, REQ-BL-01
- **BR:** BR-CC-05, BR-CC-06, BR-DQ-06, BR-DD-16
- **DD:** DD-16
- **PD:** —
- **T:** T-06, T-08, T-10, T-28
- **TS:** TS-L1, TS-L2, TS-Q1, TS-Q2, TS-C2, TS-S3, TS-T3

### 10. INTERNAL CLARIFICATION MODEL

- **Architecture sections:** PS-14, PS-15
- **REQ:** REQ-BL-06
- **BR:** BR-PD-01, BR-PD-01a, BR-DD-06, BR-DD-07, BR-DD-11, BR-EL-04a, BR-EL-05a, BR-HO-01
- **DD:** DD-06, DD-07, DD-11
- **PD:** PD-01
- **T:** T-07, T-19, T-20, T-21, T-25
- **TS:** TS-V1, TS-V2, TS-V3, TS-V4, TS-W1, TS-W2, TS-W3, TS-P2, TS-P3, TS-I2, TS-I3, TS-E4, TS-E5

### 11. CORRECTIONS

- **Architecture sections:** PS-10
- **REQ:** REQ-OO-01
- **BR:** BR-DD-08, BR-CC-05, BR-CC-11
- **DD:** DD-08
- **PD:** —
- **T:** T-08, T-10, T-14, T-22
- **TS:** TS-X1, TS-X2, TS-X3

### 12. TRANSFER

- **Architecture sections:** PS-12
- **REQ:** REQ-BL-04
- **BR:** BR-TR-01, BR-TR-02, BR-TR-03, BR-TR-04, BR-TR-05, BR-TR-06, BR-TR-07, BR-DD-02, BR-PD-02, BR-PD-03
- **DD:** DD-02, DD-16
- **PD:** PD-02, PD-03
- **T:** T-11, T-15
- **TS:** TS-M1, TS-M2, TS-M3, TS-N1, TS-Z1, TS-Z5

### 13. DISQUALIFICATION

- **Architecture sections:** PS-11
- **REQ:** REQ-BL-01, REQ-BL-02, REQ-EL-01, REQ-EL-03, REQ-EL-05, REQ-EL-07
- **BR:** BR-DQ-01, BR-DQ-02, BR-DQ-03, BR-DQ-04, BR-DQ-05, BR-DQ-06, BR-DQ-07, BR-DQ-08, BR-DQ-09, BR-DQ-10, BR-DD-11, BR-DD-17, BR-PD-02, BR-PD-03
- **DD:** DD-02, DD-08, DD-11, DD-16, DD-17
- **PD:** PD-02, PD-03
- **T:** T-10, T-14
- **TS:** TS-C1, TS-C2, TS-D1, TS-F1, TS-F2, TS-G1, TS-H1, TS-Q2, TS-X3, TS-Y3, TS-Z2, TS-Z3

### 14. BUSY / CALLBACK

- **Architecture sections:** PS-13
- **REQ:** REQ-CS-02, REQ-PV-05, REQ-PV-06, REQ-PV-07
- **BR:** BR-CB-01, BR-CB-02, BR-CB-03, BR-CB-04, BR-DD-04, BR-DD-13, BR-PD-02, BR-PD-03
- **DD:** DD-04, DD-13
- **PD:** PD-02, PD-03
- **T:** T-04, T-13, T-19, T-24, T-27
- **TS:** TS-B1, TS-B2, TS-B3, TS-B4, TS-Z1, TS-Z3, TS-Z4

### 15. NOT INTERESTED

- **Architecture sections:** PS-16
- **REQ:** —
- **BR:** BR-DD-09, BR-DD-15, BR-HO-01, BR-PD-02, BR-PD-03
- **DD:** DD-09, DD-15
- **PD:** PD-02, PD-03
- **T:** T-18, T-19
- **TS:** TS-U1, TS-U2, TS-Z2, TS-Z4, TS-Z5

### 16. UNKNOWN / UNCLASSIFIED ANSWERS

- **Architecture sections:** PS-14, PS-15
- **REQ:** REQ-BL-06
- **BR:** BR-DD-06, BR-DD-07, BR-DD-11, BR-PD-01, BR-PD-03
- **DD:** DD-06, DD-07, DD-11
- **PD:** PD-01, PD-03
- **T:** T-19, T-20, T-21, T-25
- **TS:** TS-V1, TS-V2, TS-V3, TS-V4, TS-W1, TS-W2, TS-P3

### 17. LANGUAGE

- **Architecture sections:** PS-17
- **REQ:** REQ-PV-09, REQ-NC-04
- **BR:** BR-CC-04, BR-DD-05
- **DD:** DD-05
- **PD:** —
- **T:** —
- **TS:** TS-R1, TS-R2

### 18. AGENT GENDER

- **Architecture sections:** PS-18
- **REQ:** REQ-PV-04, REQ-PV-03
- **BR:** BR-CC-09
- **DD:** —
- **PD:** —
- **T:** —
- **TS:** TS-A1, TS-R1

### 19. RAG

- **Architecture sections:** PS-19
- **REQ:** REQ-PV-08, REQ-BL-05, REQ-BL-07
- **BR:** BR-CC-12, BR-HO-04, BR-DD-10, BR-DD-17
- **DD:** DD-10, DD-17
- **PD:** —
- **T:** T-07
- **TS:** TS-O1, TS-Y1, TS-Y2, TS-Y3

### 20. CONVERSATION HISTORY

- **Architecture sections:** PS-20, PS-06
- **REQ:** REQ-PV-10, REQ-PV-11, REQ-OO-01
- **BR:** BR-CC-05, BR-CC-11, BR-DD-14
- **DD:** DD-14
- **PD:** —
- **T:** T-01
- **TS:** TS-B5, TS-L1, TS-L2, TS-S2, TS-X1, TS-W3

### 21. NATURAL CONVERSATION

- **Architecture sections:** PS-21
- **REQ:** REQ-UC-04, REQ-NC-01, REQ-NC-02, REQ-NC-03, REQ-NC-05, REQ-NC-06
- **BR:** BR-CC-01, BR-CC-02, BR-CC-03, BR-HO-05
- **DD:** DD-05
- **PD:** —
- **T:** T-07
- **TS:** TS-O1, TS-O2, TS-P1, TS-P2, TS-Q1, TS-I1, TS-S1

### 22. HANDOFF GATE

- **Architecture sections:** PS-22
- **REQ:** REQ-BL-05, REQ-BL-06, REQ-UC-05, REQ-EL-00
- **BR:** BR-HO-01, BR-HO-03, BR-HO-05, BR-HO-06, BR-EL-00, BR-EL-05a, BR-PD-01a, BR-DD-14
- **DD:** DD-07, DD-11, DD-14
- **PD:** PD-01
- **T:** T-12
- **TS:** TS-A1, TS-S1, TS-S2, TS-S3, TS-G1, TS-G2, TS-H2

### 23. QUALIFIED HANDOFF

- **Architecture sections:** PS-22, PS-24
- **REQ:** REQ-BL-05, REQ-BL-07, REQ-UC-05
- **BR:** BR-HO-02, BR-HO-04, BR-HO-06
- **DD:** DD-10
- **PD:** —
- **T:** T-12, T-16
- **TS:** TS-A1, TS-G2, TS-H2

### 24. TERMINAL STATES

- **Architecture sections:** PS-23, PS-24
- **REQ:** REQ-BL-01, REQ-BL-04, REQ-BL-05, REQ-CS-02
- **BR:** BR-DQ-07, BR-TR-04, BR-HO-02, BR-DD-01, BR-DD-04, BR-DD-08, BR-DD-09, BR-DD-11, BR-DD-12, BR-DD-13, BR-PD-03
- **DD:** DD-01, DD-04, DD-08, DD-09, DD-11, DD-12, DD-13
- **PD:** PD-03
- **T:** T-13, T-14, T-15, T-16, T-17, T-18, T-19, T-25, T-26, T-27
- **TS:** TS-A1, TS-C1, TS-M1, TS-B2, TS-B4, TS-E2, TS-E5, TS-U1, TS-W2, TS-V3, TS-P3, TS-T2, TS-X2, TS-I3

### 25. FINAL RESPONSE POLICY

- **Architecture sections:** PS-21, PS-24
- **REQ:** REQ-UC-04, REQ-PV-03, REQ-PV-04, REQ-PV-09
- **BR:** BR-CC-01, BR-CC-04, BR-CC-09, BR-PD-03
- **DD:** —
- **PD:** PD-03
- **T:** —
- **TS:** TS-A1, TS-R1, TS-Z2

## 3. Invariants

The six invariants of the architecture, and where the prompt states them.

| Invariant | The prompt must never allow | Prompt sections |
|---|---|---|
| INV-1 | RAG context to override assignment eligibility | 3.1 (rule 1), 19 |
| INV-2 | Conversational inference to create new eligibility criteria | 3.1 (rule 2), 3.2, 7, 13, 16 |
| INV-3 | Incomplete data to be treated as qualification | 3.1 (rule 3), 10, 16, 22 |
| INV-4 | A handoff before all seven required points are established | 3.1 (rule 4), 22, 23, 25 |
| INV-5 | "Not qualified" presented as "disqualified" when no documented criterion failed | 3.1 (rule 5), 10, 13, 24 |
| INV-6 | Any offer or eligibility detail disclosed before the customer is verified | 3.1 (rule 6), 4, 5 |

## 4. Assignment requirements and project decisions in the prompt

The prompt does not label its rules by source, because those labels must not reach the customer. The split is recorded here.

| Behaviour in the prompt | Source |
|---|---|
| The seven eligibility points and their eligible values | Assignment (REQ-EL-01 to REQ-EL-07) |
| The four disqualifying answers; immediate disqualification | Assignment (REQ-BL-01) |
| Above 75 Lakhs: explain the limit, ask about the maximum | Assignment (REQ-BL-03) |
| Transfer triggers and the specialist-for-loan-transfer message | Assignment (REQ-BL-04) |
| Handoff only after all seven points; the senior-loan-expert message | Assignment (REQ-BL-05, REQ-BL-06) |
| Verify the customer; offer only once verified; up to 75 Lakhs | Assignment (REQ-CS-01, REQ-CS-03, REQ-CS-04) |
| Busy: acknowledge and ask for a preferred callback time | Assignment (REQ-CS-02) |
| Out-of-order details noted and not asked again | Assignment (REQ-OO-01) |
| The eleven run-time values; language and gender binding | Assignment (REQ-PV-01 to REQ-PV-11) |
| Customer declines the maximum: close without qualification | Project decision DD-01 |
| Transfer outranks disqualification | Project decision DD-02 |
| Nothing disclosed before verification; no extra identity data | Project decisions DD-03, DD-16 |
| Busy at any stage; interaction ends after the callback request | Project decision DD-04 |
| Never switch response language | Project decision DD-05 |
| Unclassified answers: clarify, never infer | Project decision DD-06 |
| Don't know or refusal: explain and ask again | Project decision DD-07 |
| Latest correction wins; ended calls are not reopened | Project decision DD-08 |
| Not interested: acknowledge and end | Project decision DD-09 |
| Retrieved context: use only when relevant, invent nothing | Project decisions DD-10, DD-17 |
| Incomplete outcome, kept apart from disqualification | Project decision DD-11 |
| Wrong person: disclose nothing, ask for the customer, else close | Project decision DD-12 |
| No callback time: close politely | Project decision DD-13 |
| Nothing assumed from an earlier call | Project decision DD-14 |
| No consent gate after the offer | Project decision DD-15 |
| Exactly one clarification; tracking never adds eligibility points | Prompt-policy decision PD-01 |
| Signal ranking: transfer, disqualification, not interested, busy, normal flow | Prompt-policy decision PD-02 |
| Closings: thanks, no internal names, incomplete wording | Prompt-policy decision PD-03 |

## 5. Project defaults that are not approved decisions

> **Nothing in this section is an assignment requirement, and nothing in it is an approved design or prompt-policy decision.** These are behaviours the prompt had to state because a prompt cannot leave them blank. They are **project defaults** in V1. None of them adds, removes or changes an eligibility criterion.

The architecture lists the prompt-policy decisions that are still pending (`PD-04` to `PD-13`). Each default is rated:

- **Neutral** — harmless and platform-neutral; it can stay as it is.
- **Flagged** — it changes what a customer hears or how a call ends, so it could affect customer behaviour or how the assignment is scored. It needs an explicit decision before the prompt is treated as final.

### 5.1 Defaults for pending prompt-policy decisions

| Pending decision | What the prompt does in V1 | Prompt section | Rating |
|---|---|---|---|
| PD-04 AI disclosure | Does not volunteer that it is an AI. If sincerely asked, says truthfully that it is an AI assistant. Never claims to be human. Gives no recording or regulatory statement. | 1 | **Flagged** |
| PD-05 Hindi form and gender values | Speaks natural Hindi and matches self-reference to the gender value. Fixes no script, register or list of allowed gender values. | 17, 18 | **Flagged** (decides how Hindi is produced for speech at integration) |
| PD-06 Output contract | Spoken reply only. No structured record of the outcome, and no recap of details at handoff. | 23, 25 | Neutral |
| PD-07 Transfer trigger scope | Applies the transfer when the customer's words clearly indicate an existing loan on the property or a wish to reduce their current EMI, which is the assignment's own wording. Does not infer a trigger from unrelated talk about affordability or a possible new-loan EMI. Never asks about existing loans. Does not decide the case of a loan that is not on this property. | 12 | Neutral |
| PD-08 Identity details | A clear statement that the person is the customer counts as confirmation. An unclear reply is asked again, with no attempt limit. Before confirmation the agent may give only its name, the company and who it wants to speak to. A person who will not confirm, or wants to end the call first, gets the same closing as a wrong person. | 4 | **Flagged** |
| PD-09 Placeholder syntax and call ending | Uses neutral `[[name]]` placeholders. Says nothing about how the call is disconnected. | 2, 24 | Neutral |
| PD-10 Silence, voicemail, dropped calls | Not addressed in the prompt. | — | **Flagged** (a gap, not a default; real calls will hit it) |
| PD-11 "Pre-approved" wording | May call the offer pre-approved; always says "up to" 75 Lakhs; never says the loan is approved, sanctioned or guaranteed. | 6 | **Flagged** |
| PD-12 Reason in the disqualification message | Gives the assignment's message only. Does not name the criterion that was not met and does not list the criteria. | 13 | **Flagged** |
| PD-13 Other closings | Qualified, declined maximum, callback, no callback time and wrong person all close politely. Thanks are required only where PD-03 requires them. | 23, 24 | Neutral |

### 5.2 Other defaults found in the prompt

These are not tied to a numbered pending decision. They were found by auditing the prompt against the specification.

| Behaviour in the prompt | Why it is a default | Prompt section | Rating |
|---|---|---|---|
| When information volunteered before verification calls for a transfer or a disqualification, the outcome is given in the same reply in which the agent first explains why it is calling. | DD-16 says such information is checked once the customer is verified, but not how the reply is composed. | 4 | **Flagged** |
| The agent never states an exact interest rate, even if a figure appears in the retrieved context. | The assignment gives exact rates to the senior loan expert, and DD-10 forbids inventing or committing to one. Whether a rate found in the retrieved context may be relayed is unspecified (AMB-17). The prompt takes the stricter reading. | 19, 23 | **Flagged** |
| When the retrieved context does not cover a question, the agent says it does not have that detail on this call. | DD-10 says to invent nothing; it does not say what to say instead. | 19 | Neutral |
| The agent does not try to persuade a customer who has declined. | DD-09 says to acknowledge and end; persuasion is not mentioned. | 15 | Neutral |
| A callback time is accepted as the customer states it, without pressing for precision, and the agent confirms it has been noted. | DD-04 and DD-13 do not say how precise a time must be. | 14 | Neutral |
| A tenure that is not a clear length of time in years is treated as unclassified and clarified once. | AMB-11 (months, fractions) is only partly covered by DD-06. | 7, 16 | Neutral |
| The agent does not assume the customer's gender from their name. | Listed as a failure mode in the architecture; not a requirement. | 18 | Neutral |
| The agent does not volunteer retrieved context that the customer has not asked about. | DD-10 says "only when relevant"; the prompt reads that as relevant to a customer question. | 19 | Neutral |
| The amount is spoken as "75 Lakhs" with no currency. | The assignment gives no currency (AMB-23). | 6, 7 | Neutral |

### 5.3 Flagged items needing a decision

1. **AI disclosure and recording notice** (PD-04).
2. **Hindi output form for speech** (PD-05).
3. **Identity edge cases:** unclear replies, attempt limit, a refusal before confirmation (PD-08).
4. **Silence, voicemail and dropped calls** (PD-10).
5. **"Pre-approved" wording** (PD-11).
6. **Whether a disqualified customer is told the reason** (PD-12).
7. **How a pre-verification transfer or disqualification is delivered** (DD-16 gap).
8. **Whether a rate found in retrieved context may be relayed** (AMB-17).

## 6. Deployment notes

- Replace each `[[name]]` placeholder with the voice platform's own variable syntax. The eleven names are those of the assignment.
- Do not paste this document, or any ID from it, into the platform.
- The English examples in the prompt are illustrations of tone. They are not required wording.
