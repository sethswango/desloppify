"""Shared pytest fixtures for review tests."""

from __future__ import annotations

import pytest

import desloppify.app.commands.runner.codex_batch as codex_batch_mod
import desloppify.engine.plan_state as plan_mod
from desloppify.tests.review.shared_review_fixtures import (
    empty_state,
    mock_lang,
    mock_lang_with_zones,
    sample_issues_data,
    state_with_issues,
)


@pytest.fixture(autouse=True)
def _isolate_plan(monkeypatch):
    """Prevent review tests from touching the real .desloppify/plan.json."""
    monkeypatch.setattr(plan_mod, "has_living_plan", lambda: False)


@pytest.fixture(autouse=True)
def _plain_codex_argv(monkeypatch):
    """Keep the codex argv a plain list whatever codex the host has installed.

    On Windows an npm-installed codex is a ``.cmd`` shim, which the runner
    collapses into ``["cmd", "/c", "<one string>"]``. The fake subprocess
    runners in the review cases read ``-o`` from the argv list, so they need the plain form.
    """
    monkeypatch.setattr(codex_batch_mod, "_resolve_executable", lambda name: [name])


__all__ = [
    "empty_state",
    "mock_lang",
    "mock_lang_with_zones",
    "sample_issues_data",
    "state_with_issues",
]
