# SalesAgents AI Voice Agent

Repository for the SalesAgents AI Voice Agent assignment: designing, testing and
evaluating an AI voice agent, and packaging the result for submission.

## Project status

**System Prompt V1 written; not yet deployed.** The repository contains:

- the requirements, business rules, state model and design decisions in `docs/`;
- synthetic machine-readable test scenarios in `evaluation/`;
- the first system prompt, [`prompts/system_prompt_v1.md`](prompts/system_prompt_v1.md),
  with its mapping back to the specification in
  [`docs/system-prompt-traceability.md`](docs/system-prompt-traceability.md).

The prompt is platform-neutral and has not been run on a voice platform. There
is no voice-platform integration, no agent code, no call recordings and no
automated evaluation of the prompt's conversational quality yet. Some prompt
behaviours rest on project defaults that still need a decision; they are listed
in section 5 of the traceability document.

## Technology direction

- **Python 3.12** for tooling, tests and evaluation scripts
- **pytest** for automated tests
- **PyYAML** for reading structured configuration and test data
- **GitHub Actions** for continuous integration

Further dependencies will be added only when the work that needs them begins.

## Repository structure

```
salesagents-ai-voice-agent/
├── prompts/              # System prompt (system_prompt_v1.md)
├── tests/                # Automated pytest tests
├── evaluation/           # Synthetic test scenarios and their validator
├── docs/                 # Requirements, rules, state model, decisions, traceability
├── submission/           # Final assignment deliverables
├── scripts/              # Helper scripts
├── .github/
│   └── workflows/
│       └── ci.yml        # CI pipeline
├── .python-version       # Python version used by the project
├── README.md
├── requirements.txt
└── .gitignore
```

`submission/` and `scripts/` are currently empty placeholders (kept in Git with
a `.gitkeep` file). See [`docs/`](docs) for the specification and
[`evaluation/README.md`](evaluation/README.md) for the fixture format.

Where to start reading:

| Document | What it holds |
|---|---|
| [`docs/assignment-requirements.md`](docs/assignment-requirements.md) | What the assignment requires, and what it leaves unspecified |
| [`docs/business-rules.md`](docs/business-rules.md) | Eligibility, disqualification, transfer, callback and handoff rules |
| [`docs/conversation-state-model.md`](docs/conversation-state-model.md) | Call states and transitions |
| [`docs/design-decisions.md`](docs/design-decisions.md) | Project decisions for points the assignment leaves open |
| [`docs/system-prompt-architecture.md`](docs/system-prompt-architecture.md) | Prompt structure, precedence and prompt-policy decisions |
| [`docs/system-prompt-traceability.md`](docs/system-prompt-traceability.md) | Each prompt section mapped to its sources; unapproved defaults |
| [`docs/test-scenarios.md`](docs/test-scenarios.md) | The test scenarios in prose |

## Getting started

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Development workflow

```
feature branch → development → pull request → CI → review → merge to main
```

1. Create a feature branch from `main` (for example `feature/short-description`).
2. Develop and commit on the feature branch; run the checks locally.
3. Open a pull request targeting `main`.
4. CI runs automatically on the pull request.
5. Review the changes.
6. Merge to `main` once CI passes and the review is approved.

Changes should reach `main` through pull requests rather than direct pushes.

## Testing strategy

Tests live in `tests/` and run with pytest:

```bash
python -m compileall -q -x '(\.venv|\.git)/' .
python -m pytest -q
python -m evaluation.fixture_loader
```

The test suite verifies three things:

- **Project foundation:** required folders and files exist, the CI workflow is
  valid YAML, secrets are git-ignored.
- **Evaluation fixtures:** they are valid, synthetic, and match the
  specification in `docs/`.
- **System prompt structure:** all runtime variables, the seven eligibility
  points, the four disqualifying answers, the transfer triggers, the handoff
  gate and the signal precedence are present; no internal IDs, placeholder text
  or secrets are in the prompt; the traceability document covers every section.

These are structural checks. They do not run the prompt against a model and do
not judge how well it converses. Tests are deterministic and need no network
access or credentials.

## CI/CD strategy

`.github/workflows/ci.yml` runs on every push to `main` and on every pull
request targeting `main`. It:

1. Checks out the repository
2. Sets up Python 3.12
3. Installs `requirements.txt`
4. Validates Python files with `compileall`
5. Runs the tests with `python -m pytest -q`

There is no deployment step at this stage.

## Security

Never commit API keys, tokens, platform credentials or any other secrets.

- `.env`, `.env.*` and `secrets/` are excluded by `.gitignore`.
- When environment variables are needed, their names (without real values) will
  be documented in a committed `.env.example`; real values stay in a local
  `.env` file or in GitHub Actions secrets.
- If a secret is ever committed, treat it as compromised and rotate it
  immediately.
