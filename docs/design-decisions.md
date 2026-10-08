# Design Decisions

Design decisions for the Home Credit Loan Against Property (LAP) qualification call.

> **These are project design decisions. They are not requirements from the assignment PDF.**
> The assignment is silent on each point below. A decision records the behaviour this project has chosen so the agent can be built and tested. If the assignment owner later states a different behaviour, the assignment wins and the decision is replaced.

- Source requirements (`REQ-*`) and the ambiguities they leave (`AMB-*`) are in [assignment-requirements.md](assignment-requirements.md).
- Source-derived business rules (`BR-EL`, `BR-DQ`, `BR-TR`, `BR-CB`, `BR-HO`, `BR-CC`) and the design-decision rules (`BR-DD-*`) are in [business-rules.md](business-rules.md).
- Transitions (`T-nn`) are in [conversation-state-model.md](conversation-state-model.md); design-decision transitions are T-17 to T-28, kept in their own section there.
- Scenarios (`TS-*`) are in [test-scenarios.md](test-scenarios.md).

## Principles

1. **No new eligibility criteria.** No decision adds, removes or changes an eligibility criterion. The only disqualifying answers remain the ones the assignment names: Agricultural property, Original Documents unavailable, Cash income, and Tenure outside 3 to 15 years.
2. **Source first.** Where the assignment says something, the decision repeats it as "what the assignment says" and adds only what is missing.
3. **Not qualifying is not disqualifying.** Several decisions end or block a call without qualification. None of them uses a criterion failure as the reason.

## Summary

| ID | Topic | Decision in one line | Resolves |
|---|---|---|---|
| DD-01 | Customer declines the 75 Lakh maximum | Respect the decision and end the call without qualification. | AMB-08 (partly) |
| DD-02 | Transfer trigger and disqualification together | Route to the specialist for loan transfer; do not continue fresh-loan qualification. | AMB-12 (partly) |
| DD-03 | Identity verification | No offer or eligibility details until the intended customer is confirmed; no extra identity data. | AMB-01, AMB-02 (partly) |
| DD-04 | Busy / callback | Acknowledge, ask for a preferred callback time, and do not continue qualification in that interaction. | AMB-03 (partly) |
| DD-05 | Language mismatch | Always respond in `language_to_speak`; mixed-language customer speech may be understood. | AMB-16 |
| DD-06 | Unclassified answers | Ask a clarification question; never infer eligibility or create a category. | AMB-06, AMB-09, AMB-07 (partly), AMB-11 (partly), AMB-22 (partly) |
| DD-07 | Don't know / refusal | Explain why it is needed, ask again; if still not established, do not qualify or hand off. | AMB-15 (partly), AMB-10 (partly), AMB-08 (partly) |
| DD-08 | Correction of an earlier answer | Latest explicit correction wins while the call is active; closed flows are not reopened. | AMB-14 |
| DD-09 | Not interested | Acknowledge and end politely; no qualification, no handoff. | AMB-04 |
| DD-10 | RAG / product information | Use retrieved context only when relevant; invent nothing; never invent or commit to an exact interest rate. | AMB-17 (partly) |
| DD-11 | Stuck calls | If a required fact cannot be established after reasonable clarification, close politely without qualifying and without calling the customer ineligible. | AMB-15 |
| DD-12 | Wrong person | Disclose nothing about the offer or eligibility; ask for the intended customer where appropriate, otherwise close. | AMB-02 |
| DD-13 | Callback with no time | If a busy customer cannot give a callback time, close politely without qualification. | AMB-03 (partly) |
| DD-14 | Callback information carryover | Rely only on information actually available through `conversation_history` or supplied customer/context data. | AMB-03 (partly) |
| DD-15 | Consent | No separate mandatory "consent to proceed" question; a clear refusal uses the not-interested path. | AMB-05 |
| DD-16 | Pre-verification offer-related information | Disclose nothing before verification, even in response to volunteered information; preserve it only if useful and available. | AMB-13, AMB-12 (partly) |
| DD-17 | Conflicting RAG context | The assignment's eligibility and business rules take precedence over `additional_context_from_rag`. | AMB-17 |

---

## DD-01 — Customer declines the 75 Lakh maximum

- **Status:** Design decision. Not from the assignment PDF.
- **Decision:** If the customer does not want to proceed with the maximum allowed amount after being told their requested amount exceeds 75 Lakhs, the agent respects the decision and ends the call without qualification.
- **What the assignment says:** If a customer requests more than 75 Lakhs, explain the limit and ask if they would like to proceed with the maximum allowed amount (REQ-BL-03). It does not say what happens if they say no.
- **Why it is needed:** Without it, the loan-amount confirmation step has no exit for a "no". The customer cannot be handed off, because the Loan Amount criterion is not met (REQ-EL-04, REQ-BL-05).
- **Ambiguity resolved:** AMB-08, the declined-maximum part.
- **Affected business rules:** BR-EL-04a, BR-DQ-09, BR-HO-01; adds BR-DD-01.
- **Affected state transitions:** T-08, T-09; adds T-17 and T-19.
- **Affected test scenarios:** TS-E1, TS-E2.
- **Left open:** the closing wording. Whether a minimum loan amount exists is still unspecified, and none is applied.

## DD-02 — Transfer trigger and disqualification in the same utterance

- **Status:** Design decision. Not from the assignment PDF.
- **Decision:** If the customer explicitly indicates an existing loan on the property, or that they want to reduce their current EMI, the agent routes to the specialist-for-loan-transfer flow and does not continue fresh-loan eligibility qualification. This applies even when the same utterance also contains a disqualifying answer.
- **What the assignment says:** Both rules are stated separately: immediate disqualification "at any point" (REQ-BL-01), and the transfer switch when the customer mentions an existing loan on the property or wanting to reduce their current EMI (REQ-BL-04). No priority between them is given.
- **Why it is needed:** One utterance can satisfy both rules, and they give the customer different messages. The agent needs exactly one. The eligibility criteria describe the standard "Fresh Loan" flow, and a transfer customer has left that flow.
- **Ambiguity resolved:** AMB-12, the priority part.
- **Affected business rules:** BR-TR-02 to BR-TR-05, BR-TR-07, BR-DQ-05, rule precedence; adds BR-DD-02.
- **Affected state transitions:** T-10, T-11, T-15. T-11 takes priority over T-10 when both conditions hold in the same utterance.
- **Affected test scenarios:** TS-M1, TS-M2, TS-M3, TS-N1. TS-Q2 is the contrast case (disqualifying answer, no transfer trigger).
- **Left open:** loans or EMIs unrelated to this property; whether the agent should ever ask about existing loans. The decision covers explicit mentions only. A trigger given before identity verification is decided in DD-16.

## DD-03 — Identity verification

- **Status:** Design decision. Not from the assignment PDF.
- **Decision:** The agent does not disclose the LAP offer or eligibility details until the intended customer is confirmed. It does not ask for identity-verification data that the assignment does not provide for.
- **What the assignment says:** Verify that you are speaking with the correct customer; present the offer "once verified" (REQ-CS-01, REQ-CS-03). `customer_name` is the only identifying variable (REQ-PV-02). The method of verification is not described.
- **Why it is needed:** "Verified" needs a working meaning, and the agent must know what it may say to someone who is not, or not yet, confirmed as the customer.
- **Ambiguity resolved:** AMB-01; AMB-02 in part (what must not be said to a wrong person).
- **Affected business rules:** BR-CC-07, BR-CC-08; adds BR-DD-03.
- **Affected state transitions:** T-02, T-03; adds T-23.
- **Affected test scenarios:** TS-A1, TS-B1, TS-T1; global fail condition GF-4.
- **Left open:** nothing. What the agent does next when the person is not the customer is decided in DD-12.

## DD-04 — Busy / callback

- **Status:** Design decision for everything beyond "acknowledge and ask for a preferred callback time", which is the source requirement.
- **Decision:** When the customer says they are busy, the agent acknowledges it and asks for a preferred callback time. Once the callback request is accepted, the agent does not continue the qualification flow in that same interaction.
- **What the assignment says:** "If the customer is busy, acknowledge this and ask for a preferred callback time" (REQ-CS-02), stated under the Greeting and Identification stage.
- **Explicitly a design decision:** **ending the current interaction.** The PDF requires only that the agent ask for a preferred callback time. It does not say the call ends, and it does not say the qualification flow stops. Both are decided here.
- **Also a design decision:** applying this when the customer says they are busy *after* the greeting stage. DD-04 as worded is not limited to the greeting, so it is applied at any stage. The assignment places the busy case under Greeting and Identification only.
- **Why it is needed:** The busy path otherwise has no end, and a customer who becomes busy mid-call has no defined handling.
- **Ambiguity resolved:** AMB-03 in part.
- **Affected business rules:** BR-CB-01 to BR-CB-04; adds BR-DD-04.
- **Affected state transitions:** T-04, T-13 (now a design-decision transition); adds T-24.
- **Affected test scenarios:** TS-B1, TS-B2, TS-B3.
- **Left open:** who makes the callback. A customer who gives no callback time is decided in DD-13, and carryover of captured answers in DD-14.

## DD-05 — Language mismatch

- **Status:** Design decision. Not from the assignment PDF.
- **Decision:** The agent speaks using `language_to_speak`. It does not change its configured language merely because the customer responds in a different one. Where technically possible, the agent may understand natural mixed-language customer speech, but its response language remains `language_to_speak`.
- **What the assignment says:** `language_to_speak` is "the language you must use (English or Hindi)" (REQ-PV-09). Nothing is said about a customer who uses the other language.
- **Why it is needed:** Customers mix Hindi and English naturally, and the assignment requires natural conversation (REQ-NC-01). The agent needs a fixed rule for its own output.
- **Ambiguity resolved:** AMB-16.
- **Affected business rules:** BR-CC-04; adds BR-DD-05.
- **Affected state transitions:** none. Language does not change call flow; captured answers follow the usual transitions.
- **Affected test scenarios:** TS-R1, TS-R2; global fail condition GF-6.
- **Left open:** understanding the other language is "may", not "must". If the agent cannot understand an answer, the point stays unanswered and is asked again in `language_to_speak`.

## DD-06 — Unclassified answers

- **Status:** Design decision. Not from the assignment PDF.
- **Decision:** The agent does not infer eligibility from an answer that does not clearly map to the assignment's accepted categories. It asks a clarification question. It does not create new eligibility categories.
- **What the assignment says:** It names the categories: Residential, Commercial, Industrial, Agricultural; Sole, Joint; Original Documents available; Salaried, Self-Employed; Bank, Cash; Tenure in years. It does not say how to treat an answer that fits none of them clearly.
- **Why it is needed:** Real answers often fall between categories ("an empty plot", "I'm retired", "my father's house"). Guessing could qualify or disqualify a customer on a basis the assignment never gave.
- **Ambiguity resolved:** AMB-06, AMB-09; AMB-07, AMB-11 and AMB-22 in part.
- **Affected business rules:** BR-EL-01, BR-EL-02, BR-EL-03, BR-EL-05, BR-EL-07, BR-HO-01; adds BR-DD-06.
- **Affected state transitions:** T-06, guard on T-12; adds T-20.
- **Affected test scenarios:** TS-V1, TS-V2.
- **Left open:** an answer that still maps to no category after clarification. It is neither eligible nor a disqualification; the point stays unanswered and DD-07 applies. If it can never be established, DD-11 closes the call.

## DD-07 — Don't know / refusal

- **Status:** Design decision. Not from the assignment PDF.
- **Decision:** If the customer does not provide a required value, the agent explains that the information is needed for preliminary qualification and asks again naturally. If the required fact still cannot be established, the agent does not qualify or hand off the customer. No disqualification criterion is invented for this case.
- **What the assignment says:** The final handoff can happen only once all eligibility questions are asked and answered (REQ-BL-06). It does not say what to do when a customer cannot or will not answer.
- **Why it is needed:** The handoff gate blocks an incomplete call, but nothing tells the agent how to try to complete it, or that an unanswered point is not a failed criterion.
- **Ambiguity resolved:** AMB-15 in part; the "don't know" parts of AMB-10 (Market Value) and AMB-08 (Loan Amount).
- **Affected business rules:** BR-EL-00, BR-EL-06, BR-EL-06a, BR-HO-01, BR-HO-03, BR-HO-05; adds BR-DD-07.
- **Affected state transitions:** T-07, guard on T-12; adds T-21.
- **Affected test scenarios:** TS-W1, TS-W2.
- **Left open:** nothing. The number of re-asks is fixed at one by prompt-policy decision PD-01 ([system-prompt-architecture.md](system-prompt-architecture.md)). How the call closes when the fact can never be established is decided in DD-11.

## DD-08 — Correction of an earlier answer

- **Status:** Design decision. Not from the assignment PDF.
- **Decision:** The customer's latest explicit correction replaces the earlier answer while the conversation is still active. If the call has already entered a terminal state such as disqualification, transfer completion or call termination, the flow is not reopened.
- **What the assignment says:** Details given out of order must be noted and not asked again (REQ-OO-01). Nothing is said about a customer changing an answer.
- **Why it is needed:** Customers correct themselves. The agent needs to know which value counts, and whether a correction can undo a call that has already been closed.
- **Ambiguity resolved:** AMB-14.
- **Affected business rules:** BR-CC-05, BR-CC-11, BR-DQ-05, BR-DQ-07, BR-TR-04; adds BR-DD-08.
- **Affected state transitions:** T-08, T-10, T-14, T-15; adds T-22. A corrected value is checked against its criterion like any captured value, so a correction can itself trigger T-10 or T-08.
- **Affected test scenarios:** TS-X1, TS-X2, TS-X3.
- **Left open:** nothing identified. A correction made in the same utterance as the original answer, before the agent has responded, is simply the customer's answer.

## DD-09 — Not interested

- **Status:** Design decision. Not from the assignment PDF.
- **Decision:** If the customer clearly declines the offer, the agent acknowledges their decision and ends the interaction politely. It does not continue qualification or hand off.
- **What the assignment says:** Nothing. The customer declining the offer is not covered.
- **Why it is needed:** It is one of the most common outcomes of an outbound offer call, and without it the agent has no exit.
- **Ambiguity resolved:** AMB-04.
- **Affected business rules:** BR-HO-01; adds BR-DD-09.
- **Affected state transitions:** adds T-18 and T-19.
- **Affected test scenarios:** TS-U1.
- **Left open:** a request not to be called again, and the closing wording.

## DD-10 — RAG / product information

- **Status:** Design decision, except the last point, which restates the assignment.
- **Decision:** `additional_context_from_rag` may provide product knowledge. The agent uses it only when relevant and does not invent information outside the retrieved context. It does not invent or commit to an exact interest rate.
- **What the assignment says:** `additional_context_from_rag` is "specific product knowledge retrieved" (REQ-PV-08). A senior loan expert will call back "to provide exact interest rates" (REQ-BL-05). **Exact interest rates remaining the responsibility of the senior loan expert is consistent with the assignment**; the rest of this decision is not in it.
- **Why it is needed:** Customers ask product questions mid-call (rates, fees, usage). The agent needs a boundary on what it may say.
- **Ambiguity resolved:** AMB-17 in part.
- **Affected business rules:** BR-HO-04, BR-CC-12; adds BR-DD-10.
- **Affected state transitions:** none added. A product question is a diversion (T-07); the pending point is still asked.
- **Affected test scenarios:** TS-O1, TS-Y1, TS-Y2; global fail condition GF-5.
- **Left open:** nothing. Retrieved context that conflicts with the rules in this specification is decided in DD-17.

## DD-11 — Stuck calls

- **Status:** Design decision. Not from the assignment PDF.
- **Decision:** If a required fact cannot be established after reasonable clarification, the agent closes the interaction politely. It does not qualify the customer. It does not call the customer ineligible unless an explicit disqualifying criterion was actually provided. The outcome is kept separate from `DISQUALIFIED`.
- **What the assignment says:** The final handoff can happen only once all eligibility questions are asked and answered (REQ-BL-06). Disqualification follows an answer that does not meet the eligibility criteria (REQ-BL-01). Neither covers a point that is never answered.
- **Why it is needed:** DD-06 and DD-07 keep a point unanswered and block the handoff, but leave the call with no way to end. Ending it as a disqualification would treat "not answered" as a failed criterion, which the assignment never states.
- **Ambiguity resolved:** AMB-15 (the closing part); the residual cases of AMB-06, AMB-09, AMB-10 and AMB-22 after clarification.
- **Affected business rules:** BR-HO-01, BR-HO-05, BR-DQ-05, BR-DD-06, BR-DD-07; adds BR-DD-11.
- **Affected state transitions:** guard on T-12, T-20, T-21, T-19; adds T-25.
- **Affected test scenarios:** TS-W2, TS-V3.
- **Left open:** nothing. "Reasonable clarification" is fixed at exactly one clarification by prompt-policy decision PD-01 ([system-prompt-architecture.md](system-prompt-architecture.md)).

## DD-12 — Wrong person

- **Status:** Design decision. Not from the assignment PDF.
- **Decision:** If the person answering is not the intended customer, the agent does not disclose the LAP offer and does not disclose eligibility information. It asks to speak with the intended customer where appropriate; otherwise it closes the interaction. No additional identity-verification requirements are introduced.
- **What the assignment says:** Verify that you are speaking with the correct customer (REQ-CS-01). It does not say what to do when you are not.
- **Why it is needed:** DD-03 fixed what must not be said to an unconfirmed person, but not what the agent does next.
- **Ambiguity resolved:** AMB-02.
- **Affected business rules:** BR-CC-07, BR-DD-03; adds BR-DD-12.
- **Affected state transitions:** T-03, T-23, T-19; adds T-26. If the intended customer comes to the phone and is confirmed, the source transition T-03 applies as usual.
- **Affected test scenarios:** TS-T1, TS-T2.
- **Left open:** what "where appropriate" covers in practice (for example, a third party offering to take a message).

## DD-13 — Callback with no time

- **Status:** Design decision for the no-time case. Asking for a preferred callback time is the source requirement.
- **Decision:** If the customer says they are busy, the agent asks for a preferred callback time. If the customer cannot provide a time, the agent closes politely without qualification.
- **What the assignment says:** "If the customer is busy, acknowledge this and ask for a preferred callback time" (REQ-CS-02). **That is all the assignment requires.** What follows when no time is given is decided here, not by the assignment.
- **Why it is needed:** A busy customer often cannot name a time. Without this the busy path has no exit in that case.
- **Ambiguity resolved:** AMB-03 (the no-time part).
- **Affected business rules:** BR-CB-01, BR-CB-02, BR-DD-04; adds BR-DD-13.
- **Affected state transitions:** T-04, T-13, T-24, T-19; adds T-27.
- **Affected test scenarios:** TS-B4.
- **Left open:** who makes the callback, and how a callback time is recorded.

## DD-14 — Callback information carryover

- **Status:** Design decision. Not from the assignment PDF.
- **Decision:** The agent does not assume information from a previous interaction unless it is actually available through the supplied `conversation_history` or customer/context data. A new callback interaction relies only on information available to the agent.
- **What the assignment says:** `conversation_history` is "the log of the current chat" (REQ-PV-10). Details already given must not be asked again (REQ-OO-01). Nothing is said about a later, separate interaction.
- **Why it is needed:** After a busy/callback close, a later call could wrongly treat earlier answers as known. An answer the agent cannot see must not count toward the handoff gate.
- **Ambiguity resolved:** AMB-03 (the carryover part).
- **Affected business rules:** BR-CC-05, BR-CC-11, BR-HO-01; adds BR-DD-14.
- **Affected state transitions:** T-01 (the starting field statuses of an interaction). No transition is added.
- **Affected test scenarios:** TS-B5.
- **Left open:** nothing identified.

## DD-15 — Consent

- **Status:** Design decision. Not from the assignment PDF.
- **Decision:** The agent does not introduce a separate mandatory "consent to proceed" question, because the PDF does not require one. If the customer clearly declines participation, or says they do not want the offer or the process, the not-interested path (DD-09) is used.
- **What the assignment says:** Present the offer once verified (REQ-CS-03), then gather the 7 data points (REQ-EL-00). No consent step is described between them.
- **Why it is needed:** To settle whether a consent gate sits between the offer and the checklist. Adding one would be an extra step the assignment does not ask for.
- **Ambiguity resolved:** AMB-05.
- **Affected business rules:** BR-DD-09; adds BR-DD-15.
- **Affected state transitions:** T-05 (unchanged: no consent condition), T-18.
- **Affected test scenarios:** TS-A1, TS-U1, TS-U2.
- **Left open:** nothing identified. A natural lead-in before the first question is not a consent gate.

## DD-16 — Pre-verification offer-related information

- **Status:** Design decision. Not from the assignment PDF.
- **Decision:** The agent does not disclose offer or eligibility details before the intended customer is verified. If a customer volunteers an offer-related answer before verification, the agent does not disclose protected offer information in response. The information is preserved only if doing so is useful for the later verified interaction and is technically available within the conversation state.
- **What the assignment says:** The offer is presented "once verified" (REQ-CS-03). Disqualification applies "at any point in the conversation" (REQ-BL-01), and out-of-order details must be noted (REQ-OO-01). It does not say how these combine before verification.
- **Why it is needed:** A disqualification or transfer message given before verification would itself reveal the offer to an unverified person. The agent needs to know that verification comes first.
- **Effect on the source rules:** No disqualification or transfer rule is waived. The response is deferred: before verification the agent gives neither message, and once the customer is verified any preserved information is treated like any other out-of-order detail and checked then.
- **Ambiguity resolved:** AMB-13; AMB-12 (the pre-verification part).
- **Affected business rules:** BR-CC-05, BR-CC-07, BR-DQ-05, BR-DQ-06, BR-TR-04, BR-DD-03; adds BR-DD-16.
- **Affected state transitions:** T-03, T-10, T-11; adds T-28. T-10 and T-11 remain unavailable from `GREETING` and `IDENTITY_VERIFICATION`.
- **Affected test scenarios:** TS-T3.
- **Left open:** nothing identified. Preservation is conditional, so a detail that was not preserved is simply asked in its turn.

## DD-17 — Conflicting RAG context

- **Status:** Design decision. Not from the assignment PDF.
- **Decision:** Explicit assignment eligibility and business rules take precedence over `additional_context_from_rag`. Retrieved context may provide supporting product information, but:
  - it must not override the assignment's eligibility criteria;
  - it must not create new eligibility criteria;
  - it must not justify inventing facts;
  - it may be used for relevant product knowledge where permitted by the design decisions (DD-10);
  - exact interest rates must not be invented or committed to by the AI agent.
- **What the assignment says:** `additional_context_from_rag` is "specific product knowledge retrieved" (REQ-PV-08). The eligibility criteria and business logic are stated in the assignment itself (§2C, §3). No order of precedence is given.
- **Why it is needed:** Retrieved text is not controlled by this specification and could contradict it. The agent needs a fixed rule for which one wins.
- **Ambiguity resolved:** AMB-17 (the conflict part).
- **Affected business rules:** BR-EL-00 to BR-EL-07, BR-DQ-01 to BR-DQ-04, BR-HO-04, BR-CC-12, BR-DD-10; adds BR-DD-17.
- **Affected state transitions:** none added. The source transitions (for example T-10) fire on the assignment's criteria regardless of retrieved context.
- **Affected test scenarios:** TS-Y1, TS-Y2, TS-Y3.
- **Left open:** nothing identified.

---

## Decision chain

Design decision → ambiguity → business rules → transitions → test scenarios.

| Decision | Ambiguity | Design rule | Source rules touched | Transitions | Test scenarios |
|---|---|---|---|---|---|
| DD-01 | AMB-08 | BR-DD-01 | BR-EL-04a, BR-DQ-09, BR-HO-01 | T-08, T-09, T-17, T-19 | TS-E1, TS-E2 |
| DD-02 | AMB-12 | BR-DD-02 | BR-TR-02, BR-TR-03, BR-TR-04, BR-TR-05, BR-TR-07, BR-DQ-05 | T-10, T-11, T-15 | TS-M1, TS-M2, TS-M3, TS-N1 |
| DD-03 | AMB-01, AMB-02 | BR-DD-03 | BR-CC-07, BR-CC-08 | T-02, T-03, T-23 | TS-A1, TS-B1, TS-T1 |
| DD-04 | AMB-03 | BR-DD-04 | BR-CB-01, BR-CB-02, BR-CB-03, BR-CB-04 | T-04, T-13, T-24 | TS-B1, TS-B2, TS-B3 |
| DD-05 | AMB-16 | BR-DD-05 | BR-CC-04 | — | TS-R1, TS-R2 |
| DD-06 | AMB-06, AMB-07, AMB-09, AMB-11, AMB-22 | BR-DD-06 | BR-EL-01, BR-EL-02, BR-EL-03, BR-EL-05, BR-EL-07, BR-HO-01 | T-06, T-12, T-20 | TS-V1, TS-V2 |
| DD-07 | AMB-08, AMB-10, AMB-15 | BR-DD-07 | BR-EL-00, BR-EL-06, BR-EL-06a, BR-HO-01, BR-HO-03, BR-HO-05 | T-07, T-12, T-21 | TS-W1, TS-W2 |
| DD-08 | AMB-14 | BR-DD-08 | BR-CC-05, BR-CC-11, BR-DQ-05, BR-DQ-07, BR-TR-04 | T-08, T-10, T-14, T-15, T-22 | TS-X1, TS-X2, TS-X3 |
| DD-09 | AMB-04 | BR-DD-09 | BR-HO-01 | T-18, T-19 | TS-U1 |
| DD-10 | AMB-17 | BR-DD-10 | BR-HO-04, BR-CC-12 | T-07 | TS-O1, TS-Y1, TS-Y2 |
| DD-11 | AMB-15 | BR-DD-11 | BR-HO-01, BR-HO-05, BR-DQ-05 | T-12, T-19, T-20, T-21, T-25 | TS-W2, TS-V3 |
| DD-12 | AMB-02 | BR-DD-12 | BR-CC-07 | T-03, T-19, T-23, T-26 | TS-T1, TS-T2 |
| DD-13 | AMB-03 | BR-DD-13 | BR-CB-01, BR-CB-02 | T-04, T-13, T-19, T-24, T-27 | TS-B4 |
| DD-14 | AMB-03 | BR-DD-14 | BR-CC-05, BR-CC-11, BR-HO-01 | T-01 | TS-B5 |
| DD-15 | AMB-05 | BR-DD-15 | — | T-05, T-18 | TS-A1, TS-U1, TS-U2 |
| DD-16 | AMB-12, AMB-13 | BR-DD-16 | BR-CC-05, BR-CC-07, BR-DQ-05, BR-DQ-06, BR-TR-04 | T-03, T-10, T-11, T-28 | TS-T3 |
| DD-17 | AMB-17 | BR-DD-17 | BR-EL-00, BR-DQ-01, BR-DQ-02, BR-DQ-03, BR-DQ-04, BR-HO-04, BR-CC-12 | T-10 | TS-Y1, TS-Y2, TS-Y3 |

## Still open

No remaining point changes who qualifies, who is disqualified or where the call goes. What is left is wording, mechanics and operations, none of which the assignment specifies.

| Point | Ambiguity | Nature |
|---|---|---|
| Who makes the callback, and how a callback time is recorded | AMB-03 | Operational |
| Loans or EMIs unrelated to this property; whether the agent ever asks about existing loans | AMB-12 | Scope of the transfer trigger. The specification applies the assignment's wording: an explicit mention of an existing loan on the property, or of wanting to reduce the current EMI. |
| Handoff mechanics: timing of "shortly", recap, how captured data is passed on | AMB-18 | Operational / platform |
| Closing wording and the mechanism for ending the call | AMB-19 | Prompt wording / platform |
| AI disclosure, recording notice, regulatory statements | AMB-20 | Compliance |
| Variable formats and allowed values | AMB-21 | Platform |
| Currency of the amount | AMB-23 | Wording. The specification writes the amount as the assignment does. |
| Silence, voicemail, dropped call | AMB-24 | Platform |
| Strictness of "sequentially" when nothing is volunteered | AMB-25 | The specification uses order 1 to 7 as the default. |
| What counts as "where appropriate" (DD-12) | — | Prompt wording |

**Not open, by principle:** no minimum loan amount and no Market Value threshold is applied, because the assignment states neither (AMB-08, AMB-10).
