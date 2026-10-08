# Test Scenarios

Test matrix for the Home Credit Loan Against Property (LAP) qualification call.

- States, fields and transitions (`T-nn`) are defined in [conversation-state-model.md](conversation-state-model.md); rules (`BR-*`) in [business-rules.md](business-rules.md); requirements (`REQ-*`) and ambiguities (`AMB-*`) in [assignment-requirements.md](assignment-requirements.md).
- These are specification-level scenarios for later manual and automated testing. Nothing here is executable yet.
- Scenarios whose expected behaviour comes from a project design decision carry a **Basis** line naming the `DD-*` decision ([design-decisions.md](design-decisions.md)) or the `PD-*` prompt-policy decision ([system-prompt-architecture.md](system-prompt-architecture.md)). Their expected behaviour is a project choice, not something the assignment PDF states. Scenarios without a Basis line rest on the assignment alone.
- Customer utterances are written the way real customers speak, as the assignment requires (REQ-NC-06). Expected behaviour describes *what* the agent must do, not exact wording.

## Conventions

**Test fixture values** (illustrative test data only, not requirements):

| Variable | Value |
|---|---|
| `company_name` | Home Credit |
| `customer_name` | Rahul Sharma |
| `agent_name` | Priya |
| `agent_gender` | female |
| `language_to_speak` | English, unless the scenario says otherwise |

**Field shorthand:** `P1` property type, `P2` ownership status, `P3` document availability, `P4` loan amount, `P5a` occupation, `P5b` income mode, `P6` market value, `P7` tenure. "P1–P3 answered" means those fields are `ANSWERED` with eligible values and all others are `UNANSWERED`.

**Global fail conditions.** Any scenario fails if the agent does any of the following, in addition to the scenario's own conditions:

| ID | Global fail condition | Rule |
|---|---|---|
| GF-1 | Asks for a detail that is already `ANSWERED`. | BR-CC-05 |
| GF-2 | Gives the senior-loan-expert handoff message while any of the seven points is `UNANSWERED`. | BR-HO-01 |
| GF-3 | Continues asking eligibility questions after a disqualifying answer or a transfer trigger. | BR-DQ-08, BR-TR-05 |
| GF-4 | Presents the offer before the customer is verified. | BR-CC-07 |
| GF-5 | Invents or commits to an exact interest rate. (Relaying rate information from `additional_context_from_rag` is not judged: AMB-17.) | BR-HO-04 |
| GF-6 | Speaks a language other than `language_to_speak`, or contradicts `agent_gender` or `agent_name`. | BR-CC-04, BR-CC-09 |
| GF-7 | Applies an eligibility rule the assignment does not contain (e.g. a market-value threshold). | BR-EL-06a |
| GF-8 | Ends a disqualified, transfer, not-interested or incomplete call without thanking the customer, or exposes internal rule names or implementation details. *(Prompt-policy decision PD-03, not from the assignment.)* | BR-PD-03 |
| GF-9 | Makes more than one clarification or re-ask for the same tracked item (an internal clarification-tracking sub-value, or the branch-specific proceed-with-maximum confirmation), or closes as incomplete without having made one. *(Prompt-policy decision PD-01, not from the assignment.)* | BR-PD-01 |

## Scenario index

| ID | Category | Scenario | Expected outcome |
|---|---|---|---|
| TS-A1 | A. Happy path | All seven points eligible, answered in order | `QUALIFIED` |
| TS-A2 | A. Happy path | Industrial property is accepted | continues |
| TS-B1 | B. Busy | Customer busy at greeting | `CALLBACK` |
| TS-B2 | B. Busy | Busy customer gives a callback time | `CALLBACK` (ending per DD-04) |
| TS-C1 | C. Agricultural | Agricultural property, asked in order | `DISQUALIFIED` |
| TS-C2 | C. Agricultural | Agricultural property volunteered early | `DISQUALIFIED` |
| TS-D1 | D. Documents | Original documents not available | `DISQUALIFIED` |
| TS-E1 | E. Loan amount | Above 75 Lakhs, accepts the maximum | continues |
| TS-E2 | E. Loan amount | Above 75 Lakhs, declines the maximum | ends without qualification (DD-01) |
| TS-E3 | E. Loan amount | Exactly 75 Lakhs | continues |
| TS-F1 | F. Cash income | Self-employed, cash income | `DISQUALIFIED` |
| TS-F2 | F. Cash income | Salaried, paid in cash | `DISQUALIFIED` |
| TS-G1 | G. Tenure low | Tenure below 3 years | `DISQUALIFIED` |
| TS-G2 | G. Tenure low | Tenure exactly 3 years | continues / `QUALIFIED` |
| TS-H1 | H. Tenure high | Tenure above 15 years | `DISQUALIFIED` |
| TS-H2 | H. Tenure high | Tenure exactly 15 years | continues / `QUALIFIED` |
| TS-I1 | I. Salaried + bank | Salaried, salary credited to bank | continues |
| TS-I2 | I. Salaried + bank | Occupation given, income mode not stated | income mode asked |
| TS-J1 | J. Self-employed + bank | Self-employed, income via bank | continues |
| TS-K1 | K. Joint ownership | Jointly owned property | continues |
| TS-L1 | L. Out of order | One later answer given early | continues, no re-ask |
| TS-L2 | L. Out of order | Later answers given during the offer | continues, no re-ask |
| TS-M1 | M. Existing loan | Existing loan on the property | `TRANSFER` |
| TS-M2 | M. Existing loan | Existing loan mentioned in passing, mid-checklist | `TRANSFER` |
| TS-N1 | N. Lower EMI | Customer wants to reduce current EMI | `TRANSFER` |
| TS-O1 | O. Interruption | Customer interrupts with a question | continues, pending point re-asked |
| TS-O2 | O. Interruption | Customer interrupts with the answer | continues |
| TS-P1 | P. Fillers | Answer wrapped in fillers | continues |
| TS-P2 | P. Fillers | Filler only, no answer | pending point re-asked |
| TS-Q1 | Q. Multiple answers | Several eligible answers in one sentence | continues, no re-ask |
| TS-Q2 | Q. Multiple answers | Several answers, one disqualifying | `DISQUALIFIED` |
| TS-R1 | R. Language | Hindi call, customer mixes English | continues, agent stays in Hindi |
| TS-R2 | R. Language | English call, customer replies in Hindi | agent stays in English (DD-05) |
| TS-S1 | S. Early handoff | Customer asks for the expert before all points | handoff blocked |
| TS-S2 | S. Early handoff | Point skipped by a diversion | handoff blocked, point revisited |
| TS-S3 | S. Early handoff | Six of seven answered | handoff blocked |
| TS-B3 | DD-04 | Customer becomes busy mid-checklist | callback time asked |
| TS-M3 | DD-02 | Transfer trigger and disqualifying answer together | `TRANSFER` |
| TS-T1 | DD-03, DD-12 | Someone other than the customer answers | no offer disclosed; intended customer asked for |
| TS-U1 | DD-09 | Customer is not interested | `NOT_INTERESTED` |
| TS-V1 | DD-06 | Property type that fits no category | clarification asked |
| TS-V2 | DD-06 | Occupation that fits no category | clarification asked |
| TS-W1 | DD-07 | Customer does not know the Market Value | explained and asked again |
| TS-W2 | DD-07, DD-11, PD-01 | Customer still refuses a required value | `INCOMPLETE`, closed politely |
| TS-X1 | DD-08 | Customer corrects an earlier answer | value replaced, continues |
| TS-X2 | DD-08 | Correction after disqualification | flow not reopened |
| TS-X3 | DD-08 | Correction to a non-qualifying value | `DISQUALIFIED` |
| TS-Y1 | DD-10 | Product question answered from retrieved context | continues, pending point re-asked |
| TS-Y2 | DD-10 | Product question with nothing retrieved | nothing invented |
| TS-B4 | DD-13 | Busy customer cannot give a callback time | `NO_CALLBACK_TIME` |
| TS-B5 | DD-14 | Callback interaction with no earlier answers available | nothing assumed |
| TS-T2 | DD-12 | Intended customer cannot come to the call | `WRONG_PERSON` |
| TS-T3 | DD-16 | Offer-related information volunteered before verification | no disclosure, verification continues |
| TS-U2 | DD-15 | Neutral reply after the offer | checklist starts, no consent gate |
| TS-V3 | DD-06, DD-11, PD-01 | Answer still fits no category after clarification | `INCOMPLETE`, closed politely |
| TS-Y3 | DD-17 | Retrieved context conflicts with an eligibility criterion | `DISQUALIFIED` per the assignment |
| TS-V4 | PD-01 | Clarification resolves the answer | continues |
| TS-W3 | PD-01 | Customer question does not use up the clarification | pending point re-asked |
| TS-P3 | PD-01 | Second reply with no usable answer | `INCOMPLETE`, closed politely |
| TS-I3 | PD-01 | Income mode still not established after its re-ask | `INCOMPLETE`; point 5 not complete |
| TS-E4 | PD-01 | Unclear reply to the maximum-amount question | confirmation re-asked once |
| TS-E5 | PD-01 | Still no answer to the maximum-amount question | `INCOMPLETE`, closed politely |
| TS-Z1 | PD-02 | Transfer trigger and busy together | `TRANSFER` |
| TS-Z2 | PD-02 | Disqualifying answer and not interested together | `DISQUALIFIED` |
| TS-Z3 | PD-02 | Disqualifying answer and busy together | `DISQUALIFIED` |
| TS-Z4 | PD-02 | Not interested and busy together | `NOT_INTERESTED` |
| TS-Z5 | PD-02 | Transfer trigger and not interested together | `TRANSFER` |

---

## A. Happy-path customer

### TS-A1 — All seven points eligible, answered in order

- **Starting state:** `GREETING`. All fields `UNANSWERED`. `identity_verified` and `offer_presented` not set.
- **Customer utterances (one per turn):**

  | Turn | Agent step | Customer says |
  |---|---|---|
  | 1 | Greeting / identification | "Yes, this is Rahul speaking." |
  | 2 | Offer | "Okay, sounds interesting, tell me more." |
  | 3 | P1 | "It's a two-bedroom flat, we live in it." |
  | 4 | P2 | "It's in my name only." |
  | 5 | P3 | "Yes, I've got the original papers at home." |
  | 6 | P4 | "I'm thinking around forty lakhs." |
  | 7 | P5 | "I work at an IT company, salary comes into my bank account every month." |
  | 8 | P6 | "Must be about one crore twenty lakhs now." |
  | 9 | P7 | "I'd like to repay over ten years." |

- **Expected agent behaviour:** Introduces itself as `agent_name` from `company_name` and verifies the customer. Presents the offer only after verification, mentioning loyalty and up to 75 Lakhs. Asks points 1–7 in order, one at a time, each exactly once. After turn 9, tells the customer that a senior loan expert will call back shortly to provide exact interest rates, then ends the call.
- **Expected state change:** `GREETING` → `IDENTITY_VERIFICATION` → `OFFER_PRESENTATION` → `ELIGIBILITY_COLLECTION` → `QUALIFIED_HANDOFF` → `CALL_TERMINATION`. Fields: P1 Residential, P2 Sole, P3 available, P4 40 Lakhs, P5a Salaried, P5b Bank, P6 1.2 Crore, P7 10. `call_outcome = QUALIFIED`.
- **Pass:** All seven fields captured with the values above; offer follows verification; handoff message is given only after turn 9 and mentions the senior loan expert and exact interest rates.
- **Fail:** Any point re-asked, skipped or captured wrongly; handoff message before turn 9; any global fail condition.

### TS-A2 — Industrial property is accepted

- **Starting state:** `ELIGIBILITY_COLLECTION`; offer presented; all fields `UNANSWERED`; agent has asked P1.
- **Customer utterance:** "It's a small factory unit in the industrial area."
- **Expected agent behaviour:** Accepts Industrial as an eligible property type and continues with P2.
- **Expected state change:** P1 = Industrial, `ANSWERED`. Stays in `ELIGIBILITY_COLLECTION`.
- **Pass:** Next question is P2; no disqualification.
- **Fail:** Agent disqualifies, or asks the property type again.

---

## B. Busy customer

### TS-B1 — Customer busy at greeting

- **Starting state:** `GREETING` / `IDENTITY_VERIFICATION`. All fields `UNANSWERED`.
- **Customer utterance:** "Yeah, this is Rahul, but I'm in the middle of a meeting right now."
- **Expected agent behaviour:** Acknowledges that the customer is busy and asks for a preferred callback time. Does not present the offer or ask any eligibility question.
- **Expected state change:** → `CALLBACK_BUSY`. No eligibility field changes. `offer_presented` stays unset.
- **Pass:** Agent acknowledges busyness **and** asks for a preferred callback time in the same turn; no offer details; no eligibility question.
- **Fail:** Agent starts the offer or the checklist, or does not ask for a callback time.

### TS-B2 — Busy customer gives a callback time

- **Basis:** Asking for the callback time is from the assignment. Stopping the qualification flow and ending the interaction is design decision DD-04.
- **Starting state:** `CALLBACK_BUSY`; the agent has asked for a preferred callback time.
- **Customer utterance:** "Call me tomorrow evening, after six."
- **Expected agent behaviour:** Takes note of the stated time. Does not present the offer or ask any eligibility question. Ends the interaction.
- **Expected state change:** `callback_time` captured. → `CALL_TERMINATION` (T-13), `call_outcome = CALLBACK`.
- **Pass:** After the callback time is accepted, no offer and no eligibility question; the callback time is not asked for again; the interaction ends.
- **Fail:** Agent continues into the offer or eligibility questions, or ignores the stated time.

---

## C. Agricultural property

### TS-C1 — Agricultural property, asked in order

- **Starting state:** `ELIGIBILITY_COLLECTION`; offer presented; all fields `UNANSWERED`; agent has asked P1.
- **Customer utterance:** "It's farmland actually, about three acres in my village."
- **Expected agent behaviour:** Politely informs the customer that they do not meet the criteria for this specific offer at this time, and ends the call. Asks nothing further.
- **Expected state change:** P1 = Agricultural. → `DISQUALIFICATION` → `CALL_TERMINATION`. `call_outcome = DISQUALIFIED`.
- **Pass:** Disqualification message is given in the agent's next turn; tone is polite; no further eligibility question; call ends.
- **Fail:** Agent asks P2 or any later point; gives a handoff or transfer message; is curt or blames the customer.

### TS-C2 — Agricultural property volunteered early

- **Starting state:** `OFFER_PRESENTATION`; customer verified; agent is presenting the offer; all fields `UNANSWERED`.
- **Customer utterance:** "Oh nice. I do have some agricultural land I could use for this."
- **Expected agent behaviour:** Treats the volunteered property type as the answer to P1 and disqualifies immediately, as in TS-C1.
- **Expected state change:** P1 = Agricultural (captured out of order). → `DISQUALIFICATION` → `CALL_TERMINATION`. `call_outcome = DISQUALIFIED`.
- **Pass:** Disqualification message without first asking P1 or any other point.
- **Fail:** Agent asks "what type of property is it?" (re-ask) or proceeds through the checklist.

---

## D. Missing original documents

### TS-D1 — Original documents not available

- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P2 answered; agent has asked P3.
- **Customer utterance:** "No, I don't have the originals. They got lost years ago when we shifted houses."
- **Expected agent behaviour:** Politely informs the customer that they do not meet the criteria for this specific offer at this time, and ends the call.
- **Expected state change:** P3 = unavailable. → `DISQUALIFICATION` → `CALL_TERMINATION`. `call_outcome = DISQUALIFIED`.
- **Pass:** Disqualification message in the next turn; P4–P7 never asked.
- **Fail:** Agent continues to P4, or offers to proceed without original documents.

---

## E. Loan amount above 75 Lakhs

### TS-E1 — Above 75 Lakhs, accepts the maximum

- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P3 answered; agent has asked P4.
- **Customer utterances:** (1) "I need about one crore for my business expansion." then, after the agent's reply, (2) "Hmm, okay, seventy-five is fine then, let's go with that."
- **Expected agent behaviour:** After (1): explains that the maximum is 75 Lakhs and asks whether the customer would like to proceed with the maximum allowed amount. Does not disqualify. After (2): continues with the next unanswered point (P5).
- **Expected state change:** After (1): → `LOAN_AMOUNT_LIMIT_CONFIRMATION`; `loan_amount_requested` = 1 Crore; P4 not yet answered. After (2): P4 = 75 Lakhs, `ANSWERED`; → `ELIGIBILITY_COLLECTION`.
- **Pass:** Limit explained **and** the proceed-with-maximum question asked after (1); P4 recorded as 75 Lakhs after (2); next question is P5.
- **Fail:** Agent disqualifies after (1); records 1 Crore as the loan amount; skips the confirmation; re-asks the loan amount after (2).

### TS-E2 — Above 75 Lakhs, declines the maximum

- **Basis:** Design decision DD-01. The assignment does not say what happens when the customer declines the maximum (AMB-08).
- **Starting state:** `LOAN_AMOUNT_LIMIT_CONFIRMATION`; agent has explained the limit and asked whether to proceed with the maximum.
- **Customer utterance:** "No, seventy-five won't work for me. I need the full one crore or nothing."
- **Expected agent behaviour:** Respects the decision and ends the call without qualification. Does not agree to or promise more than 75 Lakhs, does not give the senior-loan-expert handoff message, and asks no further eligibility question.
- **Expected state change:** P4 does not become an eligible `ANSWERED` value. → `NO_QUALIFICATION_CLOSE` (T-17) → `CALL_TERMINATION` (T-19). `call_outcome = DECLINED_MAXIMUM`.
- **Pass:** Call ends politely with no handoff message and no further eligibility question.
- **Fail:** Agent agrees to more than 75 Lakhs; hands off as qualified; or continues to P5.

### TS-E3 — Exactly 75 Lakhs

- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P3 answered; agent has asked P4.
- **Customer utterance:** "The full seventy-five lakhs, if that's possible."
- **Expected agent behaviour:** Accepts the amount and continues with P5. Does not go through the limit explanation as if the customer had exceeded it.
- **Expected state change:** P4 = 75 Lakhs, `ANSWERED`. Stays in `ELIGIBILITY_COLLECTION`.
- **Pass:** Next question is P5; no disqualification.
- **Fail:** Agent treats 75 Lakhs as over the limit or disqualifies.

---

## F. Cash income

### TS-F1 — Self-employed, cash income

- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P4 answered; agent has asked P5.
- **Customer utterance:** "I run a small grocery shop. Mostly it's all cash, customers pay me in cash."
- **Expected agent behaviour:** Politely informs the customer that they do not meet the criteria for this specific offer at this time, and ends the call.
- **Expected state change:** P5a = Self-Employed, P5b = Cash. → `DISQUALIFICATION` → `CALL_TERMINATION`. `call_outcome = DISQUALIFIED`.
- **Pass:** Disqualification message in the next turn; P6 and P7 never asked.
- **Fail:** Agent continues to P6, or treats self-employment itself as the reason.

### TS-F2 — Salaried, paid in cash

- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P4 answered; agent has asked P5.
- **Customer utterance:** "I have a job, I work at a garment factory, but they pay us in cash at the end of the month."
- **Expected agent behaviour:** Same as TS-F1. Being salaried does not offset cash income.
- **Expected state change:** P5a = Salaried, P5b = Cash. → `DISQUALIFICATION` → `CALL_TERMINATION`. `call_outcome = DISQUALIFIED`.
- **Pass:** Disqualification message in the next turn.
- **Fail:** Agent treats "salaried" as sufficient and continues.

---

## G. Invalid tenure below 3 years

### TS-G1 — Tenure below 3 years

- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P6 answered; agent has asked P7.
- **Customer utterance:** "I want to clear it quickly, in two years."
- **Expected agent behaviour:** Politely informs the customer that they do not meet the criteria for this specific offer at this time, and ends the call.
- **Expected state change:** P7 = 2. → `DISQUALIFICATION` → `CALL_TERMINATION`. `call_outcome = DISQUALIFIED`.
- **Pass:** Disqualification message; no handoff message even though all seven points are now answered.
- **Fail:** Agent hands off as qualified, or silently changes the tenure to 3 years.

### TS-G2 — Tenure exactly 3 years

- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P6 answered with eligible values; agent has asked P7.
- **Customer utterance:** "Three years should be enough for me."
- **Expected agent behaviour:** Accepts the tenure. As all seven points are answered and eligible, gives the senior-loan-expert handoff message.
- **Expected state change:** P7 = 3. → `QUALIFIED_HANDOFF` → `CALL_TERMINATION`. `call_outcome = QUALIFIED`.
- **Pass:** Handoff message given; no disqualification. (Reads the 3-year boundary as inclusive; see AMB-11.)
- **Fail:** Agent disqualifies a 3-year tenure.

---

## H. Invalid tenure above 15 years

### TS-H1 — Tenure above 15 years

- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P6 answered; agent has asked P7.
- **Customer utterance:** "I'd want a long one, something like twenty years."
- **Expected agent behaviour:** Politely informs the customer that they do not meet the criteria for this specific offer at this time, and ends the call.
- **Expected state change:** P7 = 20. → `DISQUALIFICATION` → `CALL_TERMINATION`. `call_outcome = DISQUALIFIED`.
- **Pass:** Disqualification message; no handoff.
- **Fail:** Agent hands off, or silently caps the tenure at 15.

### TS-H2 — Tenure exactly 15 years

- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P6 answered with eligible values; agent has asked P7.
- **Customer utterance:** "Let's keep it at fifteen years."
- **Expected agent behaviour:** Accepts the tenure and gives the senior-loan-expert handoff message.
- **Expected state change:** P7 = 15. → `QUALIFIED_HANDOFF` → `CALL_TERMINATION`. `call_outcome = QUALIFIED`.
- **Pass:** Handoff message given; no disqualification. (Reads the 15-year boundary as inclusive; see AMB-11.)
- **Fail:** Agent disqualifies a 15-year tenure.

---

## I. Salaried + bank income

### TS-I1 — Salaried, salary credited to bank

- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P4 answered; agent has asked P5.
- **Customer utterance:** "I'm a government school teacher, my salary gets credited directly to my account."
- **Expected agent behaviour:** Captures both components from the one sentence and continues with P6. Does not separately ask how the income is received.
- **Expected state change:** P5a = Salaried, P5b = Bank; point 5 `ANSWERED`. Stays in `ELIGIBILITY_COLLECTION`.
- **Pass:** Next question is P6.
- **Fail:** Agent re-asks occupation or income mode, or disqualifies.

### TS-I2 — Occupation given, income mode not stated

- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P4 answered; agent has asked P5.
- **Customer utterance:** "I've been working at a private bank for about eight years now."
- **Expected agent behaviour:** Captures the occupation (Salaried). Does not assume how the income is received; asks only whether the income is received in the bank or in cash. Does not move to P6 yet.
- **Expected state change:** P5a = Salaried, `ANSWERED`; P5b remains `UNANSWERED`; point 5 is not complete. Stays in `ELIGIBILITY_COLLECTION`.
- **Pass:** Agent asks for the income mode only; P6 is not asked until the income mode is answered.
- **Fail:** Agent assumes Bank because the customer has a job (or works at a bank) and moves to P6; or re-asks the occupation.

---

## J. Self-employed + bank income

### TS-J1 — Self-employed, income via bank

- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P4 answered; agent has asked P5.
- **Customer utterance:** "I have my own textile trading business, and all the payments come through the bank."
- **Expected agent behaviour:** Captures both components and continues with P6.
- **Expected state change:** P5a = Self-Employed, P5b = Bank; point 5 `ANSWERED`. Stays in `ELIGIBILITY_COLLECTION`.
- **Pass:** Next question is P6.
- **Fail:** Agent treats self-employment as ineligible, or re-asks either component.

---

## K. Joint ownership

### TS-K1 — Jointly owned property

- **Starting state:** `ELIGIBILITY_COLLECTION`; P1 answered; agent has asked P2.
- **Customer utterance:** "It's jointly owned, in my name and my wife's name."
- **Expected agent behaviour:** Accepts joint ownership as eligible and continues with P3.
- **Expected state change:** P2 = Joint, `ANSWERED`. Stays in `ELIGIBILITY_COLLECTION`.
- **Pass:** Next question is P3; no disqualification and no added condition.
- **Fail:** Agent disqualifies, or introduces a requirement about the co-owner that the assignment does not contain.

---

## L. Out-of-order answers

### TS-L1 — One later answer given early

- **Starting state:** `ELIGIBILITY_COLLECTION`; all fields `UNANSWERED`; agent has asked P1.
- **Customer utterance:** "It's a shop in the main market. I'm looking for about thirty lakhs against it."
- **Expected agent behaviour:** Captures P1 (Commercial) and P4 (30 Lakhs). Asks P2 next, then P3, then goes straight to P5 without asking the loan amount.
- **Expected state change:** P1 = Commercial, P4 = 30 Lakhs, both `ANSWERED`. Stays in `ELIGIBILITY_COLLECTION`; next pending field is P2.
- **Pass:** P4 is never asked during the rest of the call; question order is P2 → P3 → P5 → P6 → P7.
- **Fail:** Agent asks "how much are you looking to borrow?" later; or jumps to P5 and skips P2/P3.

### TS-L2 — Later answers given during the offer

- **Starting state:** `OFFER_PRESENTATION`; customer verified; all fields `UNANSWERED`.
- **Customer utterance:** "Good timing. I'm salaried, my pay comes into my bank account, and I'd want to repay in about seven years."
- **Expected agent behaviour:** Captures P5a, P5b and P7 before any question was asked. Begins the checklist at P1 and asks only P1, P2, P3, P4 and P6.
- **Expected state change:** P5a = Salaried, P5b = Bank, P7 = 7, all `ANSWERED`. → `ELIGIBILITY_COLLECTION`; next pending field is P1.
- **Pass:** Exactly five questions are asked in the rest of the call (P1, P2, P3, P4, P6); handoff follows the answer to P6.
- **Fail:** Agent re-asks occupation, income mode or tenure; or hands off before P6 is answered.

---

## M. Existing property loan

### TS-M1 — Existing loan on the property

- **Starting state:** `ELIGIBILITY_COLLECTION`; all fields `UNANSWERED`; agent has asked P1.
- **Customer utterance:** "It's a residential flat, but I already have a home loan running on it with another bank."
- **Expected agent behaviour:** Informs the customer that a specialist for loan transfer will contact them shortly, and ends the call. Asks nothing further.
- **Expected state change:** `transfer_reason` = existing loan on the property. → `LOAN_TRANSFER` → `CALL_TERMINATION`. `call_outcome = TRANSFER`.
- **Pass:** "Specialist for loan transfer" message in the next turn; no further eligibility question; no disqualification wording; no senior-loan-expert message.
- **Fail:** Agent continues to P2; tells the customer they do not meet the criteria; or gives the qualified-handoff message.

### TS-M2 — Existing loan mentioned in passing, mid-checklist

- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P5 answered; agent has asked P6.
- **Customer utterance:** "Value is around ninety lakhs I think. There's still some loan left on this house, by the way."
- **Expected agent behaviour:** Recognises the mention even though it was not asked about. Gives the "specialist for loan transfer" message and ends the call. Does not ask P7.
- **Expected state change:** `transfer_reason` = existing loan on the property. → `LOAN_TRANSFER` → `CALL_TERMINATION`. `call_outcome = TRANSFER`.
- **Pass:** Transfer message in the next turn; P7 never asked.
- **Fail:** Agent ignores the remark and asks P7, or completes a qualified handoff.

---

## N. Customer wants lower EMI

### TS-N1 — Customer wants to reduce current EMI

- **Starting state:** `OFFER_PRESENTATION`; customer verified; agent has presented the offer.
- **Customer utterance:** "Honestly, what I really want is to bring down the EMI I'm paying right now. It's too high."
- **Expected agent behaviour:** Informs the customer that a specialist for loan transfer will contact them shortly, and ends the call. Does not start the eligibility checklist.
- **Expected state change:** `transfer_reason` = wants to reduce current EMI. → `LOAN_TRANSFER` → `CALL_TERMINATION`. `call_outcome = TRANSFER`.
- **Pass:** Transfer message in the next turn; no eligibility question asked.
- **Fail:** Agent starts or continues the checklist, or treats the remark as a disqualification.

---

## O. Customer interrupts the agent

### TS-O1 — Customer interrupts with a question

- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P2 answered; agent is in the middle of asking P3. `additional_context_from_rag` contains no interest-rate information.
- **Customer utterance:** (cutting in) "Wait, wait — before that, what interest rate are you giving on this?"
- **Expected agent behaviour:** Stops and addresses the question. Does not invent an exact rate; explains that the senior loan expert will provide exact interest rates. Then returns to P3 and asks it.
- **Expected state change:** No field changes. P3 remains `UNANSWERED`. Stays in `ELIGIBILITY_COLLECTION` (T-07).
- **Pass:** Question acknowledged; no exact rate invented; P3 is asked again before any later point and before any handoff.
- **Fail:** Agent ignores the question and talks over it; invents an exact rate; moves on to P4 leaving P3 unanswered; or treats the interruption as a handoff request.

### TS-O2 — Customer interrupts with the answer

- **Starting state:** `ELIGIBILITY_COLLECTION`; P1 answered; agent has begun asking P2 and has not finished the sentence.
- **Customer utterance:** (cutting in) "Sole owner, it's only in my name."
- **Expected agent behaviour:** Accepts the answer without repeating or finishing the interrupted question. Continues with P3.
- **Expected state change:** P2 = Sole, `ANSWERED`. Stays in `ELIGIBILITY_COLLECTION`.
- **Pass:** Next question is P3.
- **Fail:** Agent repeats the ownership question.

---

## P. Customer uses conversational fillers

### TS-P1 — Answer wrapped in fillers

- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P5 answered; agent has asked P6.
- **Customer utterance:** "Umm... let me think... you know, like, property rates have gone up, so... I'd say, uh, around eighty, eighty-five lakhs maybe?"
- **Expected agent behaviour:** Extracts the estimate from the hesitant reply and continues with P7. Does not disqualify on market value.
- **Expected state change:** P6 `ANSWERED` with the customer's estimate (about 80–85 Lakhs). Stays in `ELIGIBILITY_COLLECTION`.
- **Pass:** Next question is P7; the estimate is captured as given.
- **Fail:** Agent re-asks P6 as if nothing was said; applies a market-value threshold; or compares it against the loan amount to reject the customer.

### TS-P2 — Filler only, no answer

- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P2 answered; agent has asked P3.
- **Customer utterance:** "Hmm... documents... uh, okay, so... yeah..."
- **Expected agent behaviour:** Does not treat "yeah" in a trailing filler as confirmation that documents are available. Gently asks P3 again.
- **Expected state change:** No field changes. P3 remains `UNANSWERED`. Stays in `ELIGIBILITY_COLLECTION` (T-07).
- **Pass:** P3 is asked again and stays unanswered until a real answer is given.
- **Fail:** Agent records documents as available and moves to P4, or disqualifies.

---

## Q. Customer gives multiple answers in one sentence

### TS-Q1 — Several eligible answers in one sentence

- **Starting state:** `ELIGIBILITY_COLLECTION`; all fields `UNANSWERED`; agent has asked P1.
- **Customer utterance:** "It's my own house, only in my name, I have all the original papers with me, and I need around fifty lakhs for my daughter's wedding."
- **Expected agent behaviour:** Captures P1, P2, P3 and P4 from the one sentence. Next question is P5.
- **Expected state change:** P1 = Residential, P2 = Sole, P3 = available, P4 = 50 Lakhs, all `ANSWERED`. Stays in `ELIGIBILITY_COLLECTION`; next pending field is P5.
- **Pass:** P2, P3 and P4 are never asked; exactly P5, P6 and P7 are asked in the rest of the call.
- **Fail:** Any of P2–P4 is asked; or a captured value is wrong.

### TS-Q2 — Several answers, one disqualifying

- **Starting state:** `ELIGIBILITY_COLLECTION`; all fields `UNANSWERED`; agent has asked P1.
- **Customer utterance:** "It's a commercial shop, jointly with my brother. We run the business from there, and all our income is in cash."
- **Expected agent behaviour:** Recognises the cash income even though P5 has not been asked. Politely informs the customer that they do not meet the criteria for this specific offer at this time, and ends the call.
- **Expected state change:** P1 = Commercial, P2 = Joint, P5a = Self-Employed, P5b = Cash. → `DISQUALIFICATION` → `CALL_TERMINATION`. `call_outcome = DISQUALIFIED`.
- **Pass:** Disqualification message in the next turn; P3 never asked.
- **Fail:** Agent asks P3 and continues until it reaches P5 in order.

---

## R. Customer switches between English and Hindi

### TS-R1 — Hindi call, customer mixes English

- **Starting state:** `language_to_speak` = Hindi. `ELIGIBILITY_COLLECTION`; all fields `UNANSWERED`; agent has asked P1 in Hindi.
- **Customer utterance:** "Residential flat hai, mere naam pe hai, aur original documents sab ready hain."
- **Expected agent behaviour:** Continues in Hindi. Captures P1, P2 and P3. Asks P4 next, in Hindi. Self-references follow `agent_gender`.
- **Expected state change:** P1 = Residential, P2 = Sole, P3 = available, all `ANSWERED`. Stays in `ELIGIBILITY_COLLECTION`; next pending field is P4.
- **Pass:** Agent's reply is in Hindi; P2 and P3 are not asked; the same rules apply as in English.
- **Fail:** Agent switches its own language to English; re-asks a captured point; or uses grammatical gender inconsistent with `agent_gender`.

### TS-R2 — English call, customer replies in Hindi

- **Basis:** Design decision DD-05. The assignment says `language_to_speak` is the language the agent must use, but not what to do when the customer uses the other one (AMB-16).
- **Starting state:** `language_to_speak` = English. `ELIGIBILITY_COLLECTION`; P1–P4 answered; agent has asked P5 in English.
- **Customer utterance:** "Main job karta hoon, salary har mahine bank account mein aati hai."
- **Expected agent behaviour:** Replies in English. If it understands the answer, captures both components and asks P6. If it cannot understand the answer, P5 stays unanswered and is asked again in English.
- **Expected state change:** Agent language unchanged. Either P5a = Salaried and P5b = Bank with next pending field P6, or P5 remains `UNANSWERED`.
- **Pass:** Agent's reply is in English; and either P5 is captured and not re-asked, or P5 is asked again in English.
- **Fail:** Agent replies in Hindi; disqualifies; or moves to P6 without having captured P5.

---

## S. Attempted final handoff before all seven points are answered

### TS-S1 — Customer asks for the expert before all points

- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P3 answered; agent has asked P4.
- **Customer utterance:** "Look, I'm definitely interested. Can you just have your senior person call me and I'll give him the rest?"
- **Expected agent behaviour:** Does not give the handoff message. Politely explains that a few details are still needed, and asks P4.
- **Expected state change:** No field changes. Stays in `ELIGIBILITY_COLLECTION` (T-07). `call_outcome` not set.
- **Pass:** No handoff message; P4 is asked again; the remaining points P4–P7 are all asked before any handoff.
- **Fail:** Agent agrees and gives the senior-loan-expert message, or ends the call as qualified.

### TS-S2 — Point skipped by a diversion

- **Starting state:** `ELIGIBILITY_COLLECTION`. Earlier in the call the agent asked P2; the customer replied with a question about processing time, and the conversation moved on. Now P1 and P3–P6 are answered, **P2 is `UNANSWERED`**, and the agent has asked P7.
- **Note:** This starting state is the case the assignment names in §5 ("skipped earlier due to a diversion"). It tests the handoff gate as a backstop, however the point came to be skipped.
- **Customer utterance:** "Ten years. So that's everything, right? When will I get the call?"
- **Expected agent behaviour:** Captures P7. Does not hand off. Goes back and asks the skipped ownership question (P2). Gives the handoff message only after P2 is answered.
- **Expected state change:** P7 = 10, `ANSWERED`. Stays in `ELIGIBILITY_COLLECTION`; next pending field is P2.
- **Pass:** The agent's next question is P2; the handoff message appears only after P2 is answered.
- **Fail:** Agent gives the handoff message with P2 unanswered; or assumes an ownership value.

### TS-S3 — Six of seven answered

- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P5 and P7 answered (P7 was volunteered early); **P6 is `UNANSWERED`**; agent has just captured P5.
- **Customer utterance:** "Yes, salaried, and it all goes to my bank. I think that covers it."
- **Expected agent behaviour:** Does not hand off. Asks P6 (market value), the only unanswered point. Does not ask P7 again. Gives the handoff message only after P6 is answered.
- **Expected state change:** P5 `ANSWERED`. Stays in `ELIGIBILITY_COLLECTION`; next pending field is P6.
- **Pass:** P6 is asked; P7 is not re-asked; handoff follows the P6 answer.
- **Fail:** Agent hands off without the market value because it has no eligibility threshold; or re-asks P7.

---

## Design-decision scenarios

> Every scenario in this section rests on a **project design decision**, named in its Basis line. The expected behaviour is not stated by the assignment PDF.

### TS-B3 — Customer becomes busy mid-checklist

- **Basis:** Design decision DD-04. The assignment describes the busy case only under Greeting and Identification (AMB-03).
- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P3 answered; agent has asked P4.
- **Customer utterance:** "Sorry, someone's at the door, I really have to go. Can we do this later?"
- **Expected agent behaviour:** Acknowledges that the customer is busy and asks for a preferred callback time. Asks no further eligibility question.
- **Expected state change:** → `CALLBACK_BUSY` (T-24). No eligibility field changes.
- **Pass:** Acknowledgement and a request for a preferred callback time; P4 is not pressed.
- **Fail:** Agent keeps asking eligibility questions, or gives a handoff, disqualification or transfer message.

### TS-M3 — Transfer trigger and disqualifying answer together

- **Basis:** Design decision DD-02. The assignment gives no priority between the two rules (AMB-12).
- **Starting state:** `ELIGIBILITY_COLLECTION`; all fields `UNANSWERED`; agent has asked P1.
- **Customer utterance:** "It's agricultural land, and there's already a loan running on it."
- **Expected agent behaviour:** Informs the customer that a specialist for loan transfer will contact them shortly, and ends the call. Does not give the disqualification message.
- **Expected state change:** `transfer_reason` = existing loan on the property. → `LOAN_TRANSFER` (T-11) → `CALL_TERMINATION`. `call_outcome = TRANSFER`.
- **Pass:** "Specialist for loan transfer" message in the next turn; no disqualification wording; no further eligibility question.
- **Fail:** Agent tells the customer they do not meet the criteria; gives both messages; or continues the checklist.

### TS-T1 — Someone other than the customer answers

- **Basis:** Design decisions DD-03 and DD-12. The assignment does not describe how to verify the customer or what to do with a wrong person (AMB-01, AMB-02).
- **Starting state:** `IDENTITY_VERIFICATION`; the agent has asked whether it is speaking with `customer_name`.
- **Customer utterance:** "No, this is his brother. What's this regarding?"
- **Expected agent behaviour:** Does not disclose the LAP offer, the amount or any eligibility detail. Does not start the eligibility checklist. Does not ask for identity data the assignment does not provide for. Asks to speak with the intended customer.
- **Expected state change:** `identity_verified` stays unset. Stays in `IDENTITY_VERIFICATION` (T-23). `offer_presented` stays unset.
- **Pass:** No mention of the loan offer, the 75 Lakhs amount or eligibility; no eligibility question; the agent asks for the intended customer.
- **Fail:** Agent describes the offer to the brother; asks an eligibility question; or demands extra identity details.

### TS-U1 — Customer is not interested

- **Basis:** Design decision DD-09. The assignment does not cover a customer declining the offer (AMB-04).
- **Starting state:** `OFFER_PRESENTATION`; customer verified; agent has presented the offer.
- **Customer utterance:** "No thanks, I'm not looking for any loan right now. Not interested."
- **Expected agent behaviour:** Acknowledges the decision and ends the interaction politely. Asks no eligibility question and gives no handoff message.
- **Expected state change:** → `NO_QUALIFICATION_CLOSE` (T-18) → `CALL_TERMINATION` (T-19). `call_outcome = NOT_INTERESTED`. No eligibility field changes.
- **Pass:** Polite acknowledgement and close; no eligibility question; no handoff, disqualification or transfer message.
- **Fail:** Agent starts the checklist anyway; hands off; or tells the customer they do not meet the criteria.

### TS-V1 — Property type that fits no category

- **Basis:** Design decision DD-06. The assignment does not classify this answer (AMB-06).
- **Starting state:** `ELIGIBILITY_COLLECTION`; all fields `UNANSWERED`; agent has asked P1.
- **Customer utterance:** "It's just an empty plot, nothing's been built on it yet."
- **Expected agent behaviour:** Does not decide the property type by inference and does not disqualify. Asks a clarification question that lets the customer place the property in one of the assignment's categories.
- **Expected state change:** P1 remains `UNANSWERED`. Stays in `ELIGIBILITY_COLLECTION` (T-20).
- **Pass:** A clarification question about the property type; P2 is not asked yet; no disqualification.
- **Fail:** Agent records the plot as Residential or as Agricultural on its own judgement; treats "plot" as a new category; or moves on to P2.

### TS-V2 — Occupation that fits no category

- **Basis:** Design decision DD-06. The assignment names only Salaried and Self-Employed (AMB-09).
- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P4 answered; agent has asked P5.
- **Customer utterance:** "I'm retired now, I get my pension every month."
- **Expected agent behaviour:** Does not record the customer as Salaried or Self-Employed by inference, does not create a "retired" category, and does not disqualify. Asks a clarification question.
- **Expected state change:** P5a remains `UNANSWERED`; P5b remains `UNANSWERED` (how the pension is received was not stated). Stays in `ELIGIBILITY_COLLECTION` (T-20).
- **Pass:** A clarification question; P6 is not asked; no disqualification and no handoff.
- **Fail:** Agent treats the customer as eligible or as not eligible on the strength of "retired"; or assumes the pension is paid into a bank.

### TS-W1 — Customer does not know the Market Value

- **Basis:** Design decision DD-07. The assignment does not cover a customer who cannot give a value (AMB-10, AMB-15).
- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P5 answered; agent has asked P6.
- **Customer utterance:** "Honestly, I have no idea what it's worth these days."
- **Expected agent behaviour:** Explains that the information is needed for preliminary qualification and asks again naturally. Does not supply a value itself and does not disqualify.
- **Expected state change:** P6 remains `UNANSWERED`. Stays in `ELIGIBILITY_COLLECTION` (T-21).
- **Pass:** The need is explained and P6 is asked again; P7 is not asked yet; no handoff.
- **Fail:** Agent skips to P7; invents or suggests a figure and records it; hands off without P6; or disqualifies.

### TS-W2 — Customer still refuses a required value

- **Basis:** Design decisions DD-07 and DD-11, and prompt-policy decision PD-01 (AMB-15).
- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P4 answered. The agent asked P5, the customer declined, and the agent has already explained why it is needed and asked again.
- **Customer utterance:** "I've told you, I'm not going to discuss my income on a phone call."
- **Expected agent behaviour:** Closes the interaction politely. Does not qualify the customer and does not give the senior-loan-expert handoff message. Does not record an assumed occupation or income mode. Does not tell the customer they are ineligible or that they do not meet the criteria, because no disqualifying answer was given.
- **Expected state change:** P5 remains `UNANSWERED`. → `NO_QUALIFICATION_CLOSE` (T-25) → `CALL_TERMINATION` (T-19). `call_outcome = INCOMPLETE`, not `DISQUALIFIED`.
- **Pass:** Polite close; no handoff message; no assumed value; no disqualification message.
- **Fail:** Agent hands off; assumes Bank income to complete the checklist; says the customer does not meet the criteria; or keeps pressing after the customer has clearly refused.

### TS-X1 — Customer corrects an earlier answer

- **Basis:** Design decision DD-08. The assignment does not cover corrections (AMB-14).
- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P5 answered, with P4 = 40 Lakhs; agent has asked P6.
- **Customer utterance:** "Around ninety lakhs. Oh, and actually make the loan fifty lakhs, not forty."
- **Expected agent behaviour:** Captures P6. Replaces the Loan Amount with 50 Lakhs. Continues with P7 without re-asking any answered point.
- **Expected state change:** P6 `ANSWERED` (about 90 Lakhs). P4 = 50 Lakhs (T-22). Stays in `ELIGIBILITY_COLLECTION`; next pending field is P7.
- **Pass:** P4 holds 50 Lakhs for the rest of the call; next question is P7.
- **Fail:** Agent keeps 40 Lakhs; re-asks the Loan Amount or another answered point; or ignores the correction.

### TS-X2 — Correction after disqualification

- **Basis:** Design decision DD-08 (AMB-14).
- **Starting state:** `DISQUALIFICATION`. The customer said the property was farmland, and the agent has already told them they do not meet the criteria for this specific offer at this time.
- **Customer utterance:** "No, no, wait. I meant it's a residential house, not farmland."
- **Expected agent behaviour:** Does not reopen the eligibility flow. Ends the call politely.
- **Expected state change:** No return to `ELIGIBILITY_COLLECTION`. → `CALL_TERMINATION` (T-14). `call_outcome = DISQUALIFIED`.
- **Pass:** No eligibility question is asked after the disqualification message; call ends.
- **Fail:** Agent resumes the checklist or gives a handoff message.

### TS-X3 — Correction to a non-qualifying value

- **Basis:** Design decision DD-08 for accepting the correction. The disqualification itself is from the assignment (cash income).
- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P5 answered, with P5b = Bank; agent has asked P6.
- **Customer utterance:** "Wait, I should correct something. My income actually comes in cash, not into the bank."
- **Expected agent behaviour:** Accepts the correction, which makes the income mode Cash. Politely informs the customer that they do not meet the criteria for this specific offer at this time, and ends the call.
- **Expected state change:** P5b = Cash (T-22). → `DISQUALIFICATION` (T-10) → `CALL_TERMINATION`. `call_outcome = DISQUALIFIED`.
- **Pass:** Disqualification message in the next turn; P6 and P7 not pursued.
- **Fail:** Agent keeps the earlier Bank answer and continues, or hands off.

### TS-Y1 — Product question answered from retrieved context

- **Basis:** Design decision DD-10. The assignment does not say how `additional_context_from_rag` is to be used (AMB-17).
- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P2 answered; agent has asked P3. `additional_context_from_rag` contains this illustrative fixture text, which is test data and not a product fact: "The loan amount can be used for business expansion, education or medical expenses."
- **Customer utterance:** "Before that, tell me, can I use this money for my daughter's college fees?"
- **Expected agent behaviour:** Answers using the retrieved context and adds nothing that is not in it. Then returns to P3.
- **Expected state change:** No field changes. P3 remains `UNANSWERED`. Stays in `ELIGIBILITY_COLLECTION` (T-07).
- **Pass:** The answer is consistent with the fixture text and contains no added product claims; P3 is asked again before any later point.
- **Fail:** Agent adds details not in the retrieved context (limits, fees, rates); or does not return to P3.

### TS-Y2 — Product question with nothing retrieved

- **Basis:** Design decision DD-10 (AMB-17).
- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P2 answered; agent has asked P3. `additional_context_from_rag` is empty.
- **Customer utterance:** "And what's the processing fee on this?"
- **Expected agent behaviour:** Does not invent a fee or any other product detail, and does not invent or commit to an interest rate. Then returns to P3.
- **Expected state change:** No field changes. P3 remains `UNANSWERED`. Stays in `ELIGIBILITY_COLLECTION` (T-07).
- **Pass:** No figure or product claim is given; P3 is asked again before any later point.
- **Fail:** Agent states a fee, a rate or any product detail it was not given.

### TS-B4 — Busy customer cannot give a callback time

- **Basis:** Design decision DD-13. Asking for the callback time is from the assignment; what follows when none is given is not (AMB-03).
- **Starting state:** `CALLBACK_BUSY`; the agent has asked for a preferred callback time.
- **Customer utterance:** "I really can't say right now, my schedule's all over the place this week."
- **Expected agent behaviour:** Closes politely without qualification. Does not present the offer or ask any eligibility question.
- **Expected state change:** `callback_time` not captured. → `NO_QUALIFICATION_CLOSE` (T-27) → `CALL_TERMINATION` (T-19). `call_outcome = NO_CALLBACK_TIME`.
- **Pass:** Polite close; no offer; no eligibility question; no handoff or disqualification message.
- **Fail:** Agent continues into the offer or the checklist; invents a callback time; or tells the customer they do not qualify.

### TS-B5 — Callback interaction with no earlier answers available

- **Basis:** Design decision DD-14. The assignment describes `conversation_history` as the log of the current chat and says nothing about a later interaction (AMB-03).
- **Starting state:** A new interaction with the same customer after an earlier busy/callback close. `conversation_history` is empty and no captured answers are supplied in customer/context data. `GREETING`; all fields `UNANSWERED`.
- **Customer utterance:** "Yes, this is Rahul. You people called me yesterday about something."
- **Expected agent behaviour:** Treats nothing from the earlier call as known. Verifies the customer and presents the offer as in any call, then asks the eligibility points from the first unanswered one.
- **Expected state change:** `identity_verified` set after confirmation. All seven fields remain `UNANSWERED` until answered in this interaction.
- **Pass:** No eligibility value is assumed or stated from the earlier call; the checklist starts at P1.
- **Fail:** Agent claims to already have the customer's answers; skips points on the basis of the earlier call; or hands off without all seven points answered in information available to it.

### TS-T2 — Intended customer cannot come to the call

- **Basis:** Design decision DD-12 (AMB-02).
- **Starting state:** `IDENTITY_VERIFICATION`; the person has said they are not `customer_name`, and the agent has asked to speak with the intended customer.
- **Customer utterance:** "He's travelling, he won't be back for a few days."
- **Expected agent behaviour:** Closes the interaction politely. Discloses nothing about the LAP offer or eligibility. Asks no eligibility question.
- **Expected state change:** `identity_verified` stays unset. → `NO_QUALIFICATION_CLOSE` (T-26) → `CALL_TERMINATION` (T-19). `call_outcome = WRONG_PERSON`.
- **Pass:** Polite close with no offer or eligibility information.
- **Fail:** Agent explains the offer so the message can be passed on; asks the third party eligibility questions; or demands extra identity details.

### TS-T3 — Offer-related information volunteered before verification

- **Basis:** Design decision DD-16. The assignment does not say how "at any point" disqualification combines with presenting the offer only once verified (AMB-13).
- **Starting state:** `IDENTITY_VERIFICATION`; the agent has asked whether it is speaking with `customer_name`; not yet confirmed.
- **Customer utterance:** "Is this about a loan? Because all I've got is some agricultural land, just so you know."
- **Expected agent behaviour:** Does not confirm or describe the offer and gives no eligibility information. Does not give the disqualification message. Continues to verify the customer.
- **Expected state change:** `identity_verified` stays unset. Stays in `IDENTITY_VERIFICATION` (T-28). The volunteered property type may be preserved if technically available; if so, it is checked once the customer is verified.
- **Pass:** No offer or eligibility details and no disqualification message before verification; the agent returns to confirming the customer.
- **Fail:** Agent says the customer does not meet the criteria; describes the offer; or states which property types are eligible before verification.

### TS-U2 — Neutral reply after the offer

- **Basis:** Design decision DD-15. The assignment describes no consent step between the offer and the checklist (AMB-05).
- **Starting state:** `OFFER_PRESENTATION`; customer verified; agent has presented the offer.
- **Customer utterance:** "Hmm, okay."
- **Expected agent behaviour:** Moves into the eligibility checklist and asks P1. Does not make an explicit "do you consent to proceed" answer a condition for continuing.
- **Expected state change:** `offer_presented` set. → `ELIGIBILITY_COLLECTION` (T-05). All fields `UNANSWERED`; next pending field is P1.
- **Pass:** P1 is asked without a separate mandatory consent step.
- **Fail:** Agent refuses to continue until the customer gives explicit consent; or treats the neutral reply as declining the offer.

### TS-V3 — Answer still fits no category after clarification

- **Basis:** Design decisions DD-06 and DD-11, and prompt-policy decision PD-01 (AMB-09, AMB-15).
- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P4 answered. The agent asked P5, the customer said they are retired on a pension, and the agent has already asked a clarification question.
- **Customer utterance:** "No, I don't have a job and I don't run any business. I'm just retired, that's all there is to it."
- **Expected agent behaviour:** Does not record Salaried or Self-Employed, and does not create a new category. Closes the interaction politely without qualifying the customer. Does not tell the customer they are ineligible, because the assignment does not name this as a disqualifying answer.
- **Expected state change:** P5a remains `UNANSWERED`. → `NO_QUALIFICATION_CLOSE` (T-25) → `CALL_TERMINATION` (T-19). `call_outcome = INCOMPLETE`, not `DISQUALIFIED`.
- **Pass:** Polite close; no handoff message; no disqualification message; no inferred occupation.
- **Fail:** Agent hands off; says the customer does not meet the criteria; or classifies "retired" as eligible or as not eligible.

### TS-Y3 — Retrieved context conflicts with an eligibility criterion

- **Basis:** Design decision DD-17 for the precedence. The disqualification itself is from the assignment (Agricultural property).
- **Starting state:** `ELIGIBILITY_COLLECTION`; offer presented; all fields `UNANSWERED`; agent has asked P1. `additional_context_from_rag` contains this illustrative fixture text, which is test data and deliberately contradicts the assignment: "Agricultural land is accepted as security for this loan."
- **Customer utterance:** "It's farmland, about two acres."
- **Expected agent behaviour:** Applies the assignment's criterion, not the retrieved text. Politely informs the customer that they do not meet the criteria for this specific offer at this time, and ends the call.
- **Expected state change:** P1 = Agricultural. → `DISQUALIFICATION` (T-10) → `CALL_TERMINATION`. `call_outcome = DISQUALIFIED`.
- **Pass:** Disqualification message in the next turn; P2 is not asked.
- **Fail:** Agent treats the property as eligible because of the retrieved text, or continues the checklist.

## Prompt-policy scenarios

> Every scenario in this section rests on a **prompt-policy decision** (PD-01 or PD-02), named in its Basis line. These are project decisions; the expected behaviour is not stated by the assignment PDF. Closings follow PD-03 (see GF-8).

### TS-V4 — Clarification resolves the answer

- **Basis:** Prompt-policy decision PD-01, with design decision DD-06.
- **Starting state:** `ELIGIBILITY_COLLECTION`; all fields `UNANSWERED`. The agent asked P1, the customer said the property is an empty plot, and the agent has made its one clarification for P1.
- **Customer utterance:** "It's in a residential layout, so it's residential."
- **Expected agent behaviour:** Captures the property type from the customer's own classification and continues with P2.
- **Expected state change:** P1 = Residential, `ANSWERED`. Stays in `ELIGIBILITY_COLLECTION` (T-06); next pending field is P2.
- **Pass:** Next question is P2; the call is not closed.
- **Fail:** Agent closes as incomplete; asks for the property type a third time; or disqualifies.

### TS-W3 — Customer question does not use up the clarification

- **Basis:** Prompt-policy decision PD-01, with design decision DD-07.
- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P5 answered. The agent asked P6, the customer said they did not know, and the agent has explained why it is needed and asked again (the one re-ask for P6).
- **Customer utterance:** "Hold on, which company did you say you were calling from?"
- **Expected agent behaviour:** Answers the question, then asks P6 again. Does not treat the question as a second failed attempt.
- **Expected state change:** No field changes. P6 remains `UNANSWERED`. Stays in `ELIGIBILITY_COLLECTION` (T-07). The clarification count for P6 is unchanged.
- **Pass:** The question is answered and P6 is asked again; the call is not closed.
- **Fail:** Agent closes as incomplete; ignores the question; or moves on to P7.

### TS-P3 — Second reply with no usable answer

- **Basis:** Prompt-policy decision PD-01, with design decision DD-11.
- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P2 answered. The agent asked P3, the customer replied only with fillers, and the agent has asked again (the one re-ask for P3).
- **Customer utterance:** "Hmm... I mean... I don't know, we'll see..."
- **Expected agent behaviour:** Does not ask a third time. Explains that the required information could not be established, does not call the customer ineligible, thanks the customer and ends the interaction.
- **Expected state change:** P3 remains `UNANSWERED`. → `NO_QUALIFICATION_CLOSE` (T-25) → `CALL_TERMINATION` (T-19). `call_outcome = INCOMPLETE`, not `DISQUALIFIED`.
- **Pass:** Incomplete closing with thanks; no third request for P3; no disqualification or handoff message.
- **Fail:** Agent asks for P3 again; records documents as available or unavailable; says the customer does not meet the criteria; or hands off.

### TS-I3 — Income mode still not established after its re-ask

- **Basis:** Prompt-policy decision PD-01.
- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P4 answered. The agent asked P5; the customer gave the occupation only (Salaried), so the agent asked for the income mode (the one re-ask for that sub-value).
- **Customer utterance:** "Oh, it varies, I can't really say."
- **Expected agent behaviour:** Does not ask for the income mode again. Does not treat point 5 as answered because the occupation is known. Explains that the required information could not be established, does not call the customer ineligible, thanks the customer and ends the interaction.
- **Expected state change:** P5a stays `ANSWERED` (Salaried); P5b remains `UNANSWERED`; eligibility point 5 is not complete. → `NO_QUALIFICATION_CLOSE` (T-25) → `CALL_TERMINATION` (T-19). `call_outcome = INCOMPLETE`, not `DISQUALIFIED`.
- **Pass:** Incomplete closing with thanks; no handoff; no disqualification message.
- **Fail:** Agent counts point 5 as complete and moves to P6; assumes Bank or Cash; says the customer does not meet the criteria; or asks for the income mode a third time.

### TS-E4 — Unclear reply to the maximum-amount question

- **Basis:** Prompt-policy decision PD-01.
- **Starting state:** `LOAN_AMOUNT_LIMIT_CONFIRMATION`; P1–P3 answered. The customer asked for one crore; the agent has explained the limit and asked whether to proceed with the maximum.
- **Customer utterance:** "Hmm, seventy-five... I don't know, let me think about that."
- **Expected agent behaviour:** Asks once more whether the customer would like to proceed with the maximum allowed amount. Does not record a loan amount, does not close the call and does not move on to P5.
- **Expected state change:** Stays in `LOAN_AMOUNT_LIMIT_CONFIRMATION` (T-07). P4 remains `UNANSWERED`. The one re-ask for the confirmation is now used. The response is a branch-specific confirmation, not an eighth eligibility point: there are still exactly seven points, with P4 open.
- **Pass:** The confirmation question is asked again, once; P4 is not recorded.
- **Fail:** Agent records 75 Lakhs without agreement; treats the reply as a refusal and closes; asks P5; or disqualifies.

### TS-E5 — Still no answer to the maximum-amount question

- **Basis:** Prompt-policy decision PD-01.
- **Starting state:** `LOAN_AMOUNT_LIMIT_CONFIRMATION`; P1–P3 answered. The customer's first reply to the maximum-amount question was unclear, and the agent has asked it again (the one re-ask for the confirmation).
- **Customer utterance:** "I really can't decide that right now."
- **Expected agent behaviour:** Does not ask a third time. Explains that the required information could not be established, does not call the customer ineligible, thanks the customer and ends the interaction.
- **Expected state change:** P4 remains `UNANSWERED`. → `NO_QUALIFICATION_CLOSE` (T-25) → `CALL_TERMINATION` (T-19). `call_outcome = INCOMPLETE`, not `DECLINED_MAXIMUM` and not `DISQUALIFIED`.
- **Pass:** Incomplete closing with thanks; no amount recorded; no handoff or disqualification message.
- **Fail:** Agent records 75 Lakhs; agrees to more than 75 Lakhs; says the customer does not meet the criteria; or asks again.

### TS-Z1 — Transfer trigger and busy together

- **Basis:** Prompt-policy decision PD-02.
- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P2 answered; agent has asked P3.
- **Customer utterance:** "I'm about to step into a meeting, but quickly, there's already a loan on this property."
- **Expected agent behaviour:** Acts on the transfer trigger only. Informs the customer that a specialist for loan transfer will contact them shortly, thanks them and ends the interaction. Does not ask for a callback time.
- **Expected state change:** `transfer_reason` = existing loan on the property. → `LOAN_TRANSFER` (T-11) → `CALL_TERMINATION` (T-15). `call_outcome = TRANSFER`.
- **Pass:** "Specialist for loan transfer" message with thanks; no callback question; no further eligibility question.
- **Fail:** Agent asks for a callback time; continues the checklist; or gives two outcomes.

### TS-Z2 — Disqualifying answer and not interested together

- **Basis:** Prompt-policy decision PD-02.
- **Starting state:** `ELIGIBILITY_COLLECTION`; offer presented; all fields `UNANSWERED`; agent has asked P1.
- **Customer utterance:** "It's agricultural land, and honestly I'm not interested anyway."
- **Expected agent behaviour:** Acts on the disqualifying answer only. Politely informs the customer that they do not meet the criteria for this specific offer at this time, thanks them and ends the interaction.
- **Expected state change:** P1 = Agricultural. → `DISQUALIFICATION` (T-10) → `CALL_TERMINATION` (T-14). `call_outcome = DISQUALIFIED`, not `NOT_INTERESTED`.
- **Pass:** Disqualification message with thanks; one outcome only.
- **Fail:** Agent closes as not interested; continues the checklist; or gives two closings.

### TS-Z3 — Disqualifying answer and busy together

- **Basis:** Prompt-policy decision PD-02.
- **Starting state:** `ELIGIBILITY_COLLECTION`; P1–P4 answered; agent has asked P5.
- **Customer utterance:** "I'm driving right now, but my income is all cash, if that matters."
- **Expected agent behaviour:** Acts on the disqualifying answer only. Politely informs the customer that they do not meet the criteria for this specific offer at this time, thanks them and ends the interaction. Does not ask for a callback time.
- **Expected state change:** P5b = Cash. → `DISQUALIFICATION` (T-10) → `CALL_TERMINATION` (T-14). `call_outcome = DISQUALIFIED`.
- **Pass:** Disqualification message with thanks; no callback question.
- **Fail:** Agent asks for a callback time; asks for the occupation or any later point.

### TS-Z4 — Not interested and busy together

- **Basis:** Prompt-policy decision PD-02.
- **Starting state:** `OFFER_PRESENTATION`; customer verified; agent has presented the offer.
- **Customer utterance:** "I'm busy right now, and anyway I don't want any loan."
- **Expected agent behaviour:** Acts on the refusal only. Acknowledges the decision, thanks the customer and ends the interaction. Does not ask for a callback time.
- **Expected state change:** → `NO_QUALIFICATION_CLOSE` (T-18) → `CALL_TERMINATION` (T-19). `call_outcome = NOT_INTERESTED`, not `CALLBACK`.
- **Pass:** Acknowledgement with thanks; no callback question; no eligibility question.
- **Fail:** Agent asks when to call back; starts the checklist.

### TS-Z5 — Transfer trigger and not interested together

- **Basis:** Prompt-policy decision PD-02.
- **Starting state:** `OFFER_PRESENTATION`; customer verified; agent has presented the offer.
- **Customer utterance:** "I'm not interested in a new loan, I'm already paying one off on this house."
- **Expected agent behaviour:** Acts on the transfer trigger only. Informs the customer that a specialist for loan transfer will contact them shortly, thanks them and ends the interaction.
- **Expected state change:** `transfer_reason` = existing loan on the property. → `LOAN_TRANSFER` (T-11) → `CALL_TERMINATION` (T-15). `call_outcome = TRANSFER`, not `NOT_INTERESTED`.
- **Pass:** "Specialist for loan transfer" message with thanks; one outcome only.
- **Fail:** Agent closes as not interested; starts the checklist; or gives two closings.

---

## Scenarios that cannot be written yet

These situations have no expected behaviour in the assignment and no design decision, so no pass/fail condition can be stated. None of them affects who qualifies.

| Situation | Ambiguity |
|---|---|
| Customer mentions a loan or EMI that is not on this property | AMB-12 |
| Silence, voicemail, dropped call | AMB-24 |
