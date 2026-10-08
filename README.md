# SalesAgents AI Voice Agent

Repository for the SalesAgents AI Voice Agent assignment: designing, testing and
evaluating an AI voice agent, and packaging the result for submission.

## Project status

**Specification and test fixtures.** The repository contains the project
infrastructure, the requirements and design specification in `docs/`, and
synthetic machine-readable test fixtures in `evaluation/`. No voice-agent
functionality, system prompt or voice-platform integration has been implemented
yet.

## Technology direction

- **Python 3.12** for tooling, tests and evaluation scripts
- **pytest** for automated tests
- **PyYAML** for reading structured configuration and test data
- **GitHub Actions** for continuous integration

Further dependencies will be added only when the work that needs them begins.

## Repository structure

```
salesagents-ai-voice-agent/
├── prompts/              # Prompt files for the agent
├── tests/                # Automated pytest tests
├── evaluation/           # Evaluation material and results
├── docs/                 # Project documentation
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

`prompts/`, `submission/` and `scripts/` are currently empty placeholders (kept
in Git with a `.gitkeep` file). See [`docs/`](docs) for the specification and
[`evaluation/README.md`](evaluation/README.md) for the fixture format.

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
pytest
```

The current test suite verifies the project foundation (required folders and
files exist, the CI workflow is valid YAML, secrets are git-ignored) and the
evaluation fixtures (they are valid, synthetic, and match the specification in
`docs/`). It does not test a voice agent. Tests are deterministic and need no
network access or credentials. Tests for later work will be added alongside
that work.

## CI/CD strategy

`.github/workflows/ci.yml` runs on every push to `main` and on every pull
request targeting `main`. It:

1. Checks out the repository
2. Sets up Python 3.12
3. Installs `requirements.txt`
4. Validates Python files with `compileall`
5. Runs `pytest`

There is no deployment step at this stage.

## Security

Never commit API keys, tokens, platform credentials or any other secrets.

- `.env`, `.env.*` and `secrets/` are excluded by `.gitignore`.
- When environment variables are needed, their names (without real values) will
  be documented in a committed `.env.example`; real values stay in a local
  `.env` file or in GitHub Actions secrets.
- If a secret is ever committed, treat it as compromised and rotate it
  immediately.
