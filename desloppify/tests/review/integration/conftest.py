"""Shared fixtures for review integration tests."""

from __future__ import annotations

import pytest

import desloppify.app.commands.runner.codex_batch as codex_batch_mod
import desloppify.engine.plan_state as plan_mod


@pytest.fixture(autouse=True)
def _isolate_plan(monkeypatch):
    """Prevent review integration tests from touching the real .desloppify/plan.json.

    ``do_import`` triggers ``_sync_plan_after_review_change`` which
    calls ``has_living_plan()`` / ``load_plan()`` / ``save_plan()`` on
    the real plan file.  Mocking ``has_living_plan`` to return False
    short-circuits that path so tests don't leak into production state.
    """
    monkeypatch.setattr(plan_mod, "has_living_plan", lambda: False)


@pytest.fixture(autouse=True)
def _plain_codex_argv(monkeypatch):
    """Keep the codex argv a plain list whatever codex the host has installed.

    On Windows an npm-installed codex is a ``.cmd`` shim, which the runner
    collapses into ``["cmd", "/c", "<one string>"]``. The fake subprocess
    runners in the review cases read ``-o`` from the argv list, so they need the plain form.
    """
    monkeypatch.setattr(codex_batch_mod, "_resolve_executable", lambda name: [name])
