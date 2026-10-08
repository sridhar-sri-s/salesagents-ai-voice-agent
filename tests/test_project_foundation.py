"""Checks that the repository foundation is in place.

These tests cover project infrastructure only, not voice-agent behaviour.
"""

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_DIRECTORIES = [
    "prompts",
    "tests",
    "evaluation",
    "docs",
    "submission",
    "scripts",
    ".github/workflows",
]

REQUIRED_FILES = [
    "README.md",
    "requirements.txt",
    ".gitignore",
    ".github/workflows/ci.yml",
]


@pytest.mark.parametrize("directory", REQUIRED_DIRECTORIES)
def test_required_directory_exists(directory):
    assert (REPO_ROOT / directory).is_dir()


@pytest.mark.parametrize("filename", REQUIRED_FILES)
def test_required_file_exists(filename):
    assert (REPO_ROOT / filename).is_file()


def test_ci_workflow_is_valid_yaml():
    workflow = yaml.safe_load((REPO_ROOT / ".github/workflows/ci.yml").read_text())
    assert isinstance(workflow, dict)
    assert "jobs" in workflow


def test_gitignore_excludes_secrets_and_virtualenv():
    ignored = (REPO_ROOT / ".gitignore").read_text().splitlines()
    for pattern in (".env", ".env.*", "secrets/", ".venv/"):
        assert pattern in ignored
