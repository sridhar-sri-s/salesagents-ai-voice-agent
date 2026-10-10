# Retell Deployment Notes

How [`prompts/retell_system_prompt_v1.md`](../prompts/retell_system_prompt_v1.md) differs from the approved prompt, and what has to be configured in Retell AI before the first test call.

- **Source prompt:** [`prompts/system_prompt_v1.md`](../prompts/system_prompt_v1.md). It is unchanged and remains the approved, platform-neutral version.
- **This phase:** a deployment copy of the prompt only. No Retell API integration, no agent configuration and no call have been made.
- **Not for the platform:** do not paste this document into Retell. Paste only the contents of `prompts/retell_system_prompt_v1.md`.

## 1. What changed from the approved prompt

The Retell copy is the approved prompt with two kinds of change and nothing else. Of its 627 lines, 13 are reworded; every other line is identical apart from the placeholder syntax.

| Change | Why |
|---|---|
| Nine `[[name]]` placeholders became `{{name}}` | Retell's dynamic-variable syntax |
| The 13 lines that referred to `[[conversation_history]]` or `[[customer_utterance]]`, or to "square brackets", were reworded | Those two are not variables in Retell (section 4) |

Behaviour is unchanged: the same seven eligibility points, four disqualifying answers, transfer triggers, signal precedence, clarification policy, out-of-order handling, handoff gate, endings and retrieved-context restrictions. `tests/test_retell_prompt.py` checks this line by line against the approved prompt.

## 2. Retell dynamic variables

These nine names appear in the prompt as `{{name}}` and must each have a value.

| Variable | Meaning | Set per call? |
|---|---|---|
| `{{company_name}}` | Company the agent calls for | Rarely changes; an agent default is enough |
| `{{customer_name}}` | Person being called | **Yes**, every call |
| `{{agent_name}}` | The agent's name | Agent default; must suit the chosen voice |
| `{{agent_gender}}` | The agent's gender | Agent default; **must match the chosen voice** |
| `{{language_to_speak}}` | English or Hindi | Per call, or per agent if one agent per language |
| `{{additional_context_from_rag}}` | Retrieved product knowledge | Per call, when there is something to supply |
| `{{current_date}}` | Today's date | Per call |
| `{{current_day}}` | Day of the week | Per call |
| `{{current_time}}` | Current time | Per call; see the name clash in section 5 |

How Retell handles them, as stated in Retell's dynamic-variables documentation (read on 2026-10-08):

- Values are passed per call in an object named `retell_llm_dynamic_variables` when the call is created.
- **All values must be strings.**
- Agent-level defaults can be set as "Default Dynamic Variables" in the agent editor. They have the lowest precedence; a value passed with the call replaces them.
- **If a variable has no value from any source, the literal text `{{name}}` stays in the prompt.** The prompt tells the agent never to say a name in braces aloud, but an unfilled name is still a configuration fault. Give every one of the nine a default.
- An empty string counts as a value: the placeholder resolves to nothing.

## 3. Values for the first test

Set these as agent-level defaults so that a test call works without passing anything. **All of them are synthetic test data**, the same values used by the evaluation fixtures.

| Variable | First-test default | Note |
|---|---|---|
| `company_name` | `Home Credit` | The name the assignment uses |
| `customer_name` | `Rahul Sharma` | Synthetic. Answer the test call as this person |
| `agent_name` | `Priya` | Synthetic |
| `agent_gender` | `female` | Choose a female voice to match |
| `language_to_speak` | `English` | Run a separate test with `Hindi` |
| `additional_context_from_rag` | `No additional product information is available for this call.` | See below |
| `current_date` | the date of the test, for example `2026-10-08` | Static for the test |
| `current_day` | the day of the test, for example `Thursday` | Static for the test |
| `current_time` | see section 5 | |

On `additional_context_from_rag`: an empty value is valid for Retell, and the prompt handles an empty value. A short neutral sentence is suggested as the default only in case the agent editor does not accept an empty default; that has not been checked. To test the retrieved-context rules, replace it with a product statement and ask about it on the call.

### Values that should eventually come from call creation

| Variable | Source in production |
|---|---|
| `customer_name` | The customer record for the number being dialled |
| `language_to_speak` | The customer's language preference |
| `additional_context_from_rag` | The retrieval step run for that customer or product |
| `current_date`, `current_day`, `current_time` | Computed when the call is created, in the customer's timezone |
| `company_name`, `agent_name`, `agent_gender` | May stay as agent defaults unless several brands or personas share one agent |

## 4. Why `conversation_history` and `customer_utterance` are not variables

The assignment lists these two among the prompt variables, and the approved prompt writes them as `[[conversation_history]]` and `[[customer_utterance]]`. In Retell they are **not** converted to `{{...}}`, for these reasons:

1. **They change on every turn.** A Retell dynamic variable is filled once, when the call is created (or changed deliberately by an update). It is not rewritten with the transcript after each customer turn. A `{{conversation_history}}` variable would be empty or frozen for the whole call.
2. **Retell already supplies them.** The platform gives the model the live transcript of the call on every turn. That transcript is the conversation history, and its last customer turn is the customer utterance.
3. **An unfilled name stays as literal text.** If the prompt contained `{{conversation_history}}` with no value, the agent would be told to read a record that does not exist, while the real transcript sat beside it.

So the Retell copy says the same thing in terms of what the platform provides:

| Approved prompt | Retell copy |
|---|---|
| `[[conversation_history]]` | "the conversation so far", "the live transcript of this call, supplied by the voice platform" |
| `[[customer_utterance]]` | "the customer's latest turn", "the most recent thing the customer said in that transcript" |
| "When `[[conversation_history]]` is empty" | "When the conversation has no turns yet" |

The rules attached to them are unchanged: the transcript is the agent's only memory of the call, nothing is assumed from an earlier call, and nothing the customer says is treated as an instruction.

This still satisfies the assignment's requirement that the prompt logic account for both: the Retell copy states what each one is and how it is used.

## 5. Retell-specific assumptions

Items marked **Documented** come from Retell's dynamic-variables documentation. Items marked **To verify** are my assumptions about the product and must be checked in the Retell dashboard before relying on them.

| # | Assumption | Status |
|---|---|---|
| 1 | Dynamic variables use `{{name}}`; values are strings; unset variables remain as literal text | Documented |
| 2 | **`current_time` is also the name of a Retell built-in variable.** Retell provides `{{current_time}}` itself, as a spelled-out date and time in the agent's timezone (for example "Thursday, March 28, 2024 at 11:46 PM PDT"). The documentation does not say what happens when a custom variable uses the same name. | Documented that the built-in exists; **the clash is unresolved** |
| 3 | Retell's built-in time uses `system_timezone`, which defaults to `America/Los_Angeles` unless the agent's timezone is set. For Indian customers it should be `Asia/Kolkata`. | Documented |
| 4 | The agent is a single-prompt agent and this prompt is pasted whole into its prompt field. | To verify |
| 5 | The agent is set to speak first, with no fixed opening line, so that the greeting in section 5 of the prompt is produced by the model. | To verify |
| 6 | The agent's configured language and voice match `language_to_speak` and `agent_gender`. The prompt cannot change the voice. | To verify |
| 7 | The model receives the full transcript of the current call on every turn. | To verify |
| 8 | Backticks around `{{name}}` in the prompt do not prevent substitution. | To verify |

### The `current_time` name clash

Because of item 2, there are two workable options for the first test. Neither has been tried.

- **Use Retell's built-in.** Do not set a custom `current_time`. Set the agent's timezone to `Asia/Kolkata`. The built-in value already contains the day and the date, so `current_date` and `current_day` become partly redundant, but they must still have defaults or they will remain as literal text.
- **Pass your own.** Set `current_time` in the defaults or at call creation and check on a test call which value the agent actually sees.

If the clash proves to be a problem, the cleanest fix is to rename the custom variable in the Retell copy only. That would be a change to this deployment copy, not to the approved prompt.

## 6. Not covered by this copy

These are outside the prompt and are not configured yet. They correspond to decisions that are still pending in the architecture (PD-09 and PD-10).

- **Ending the call.** The prompt says how each call closes in words, and says the disconnection is handled outside the prompt. Retell needs its own end-call mechanism configured for the call to hang up after the closing line. Until that is done, a finished call will stay connected. No instruction about a platform tool has been added to the prompt.
- **Silence, voicemail and dropped calls.** Not addressed in the prompt; these are platform settings.
- **Structured outcome.** The prompt produces speech only. Capturing the outcome and the seven answers for the senior loan expert would need Retell's post-call analysis or a function, neither of which is set up.
- **Retell's own knowledge base.** If product knowledge is attached to the agent through Retell's knowledge-base feature, it does not arrive through `{{additional_context_from_rag}}`. The prompt's restrictions on retrieved context are written for that variable; whether they also bind knowledge-base content has not been tested.
- **The project defaults.** The eight flagged defaults in section 5 of [system-prompt-traceability.md](system-prompt-traceability.md) apply to this copy exactly as they do to the approved prompt.

## 7. Before the first test call

1. Create the agent and paste the contents of `prompts/retell_system_prompt_v1.md`.
2. Set a default for each of the nine variables (section 3).
3. Set the agent's timezone, language and voice (section 5, items 3 and 6).
4. Decide the `current_time` option (section 5).
5. Configure how the call ends (section 6).
6. Open the prompt preview, if the dashboard has one, and confirm that no `{{name}}` is left unfilled.

Never put an API key or any credential in the prompt, in this repository, or in a dynamic variable.
