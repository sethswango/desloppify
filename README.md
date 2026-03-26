> **Fork Notice**
> This is a personal fork of [peteromallet/desloppify](https://github.com/peteromallet/desloppify), maintained by **Seth Swango**.
> Upstream should be synced regularly:
> ```bash
> git fetch upstream && git merge upstream/main
> ```

---

## What Changed (Windows Codex CLI Compatibility)

The upstream desloppify codex batch runner does not work on Windows due to three issues. This fork fixes all three:

1. **Command-line length limit** -- Windows has a ~32 KB CLI argument limit. Desloppify passes the full review prompt (~7 KB per batch) as a command-line argument to `codex exec`. On Windows this exceeds the limit. **Fix:** The prompt is written to a sidecar `.prompt.txt` file and piped via stdin (`-` flag) instead.

2. **Sandbox file access** -- Codex's `--ephemeral` flag and `workspace-write` sandbox use `CreateProcessWithLogonW` on Windows, which fails with error 1385 and prevents codex from reading repository files. **Fix:** On Windows, uses `-s danger-full-access` sandbox mode and skips `--ephemeral`.

3. **`cmd /c` incompatibilities** -- npm-installed codex resolves to a `.cmd` batch shim. `cmd /c` does not forward stdin and mangles TOML quote escaping in `-c` config flags. **Fix:** Resolves the `.cmd` shim to the underlying `node codex.js` entry point for direct invocation, and uses unquoted TOML values.

All changes are gated behind `sys.platform == "win32"` -- non-Windows behavior is completely unchanged.

### Files Modified

- `desloppify/app/commands/runner/codex_batch.py` -- `_resolve_executable()` and `codex_batch_command()`
- `desloppify/app/commands/review/runner_process_impl/attempts.py` -- `_start_runner_process()` + UTF-8 encoding

### Usage Note for Cursor/Agents

> **For AI agents (Cursor, Claude, Codex):** This fork's changes only affect `desloppify review --run-batches --runner codex` on Windows. All other commands (`scan`, `status`, `next`, `show`, `plan`, `review --prepare`, etc.) are unchanged. To run a subjective review on a single codebase:
> ```bash
> cd /path/to/your/project
> desloppify scan                    # mechanical scan first
> desloppify review --run-batches --runner codex --parallel --max-parallel-batches 5 --scan-after-import
> desloppify status                  # see updated scores
> ```
> The `--parallel` flag runs multiple codex sessions concurrently. Adjust `--max-parallel-batches` based on your API rate limits and machine resources.

### Keeping in Sync

```bash
git remote add upstream https://github.com/peteromallet/desloppify.git
git fetch upstream
git merge upstream/main
# Resolve any conflicts in the two modified files above
```

---

# Desloppify - an agent harness to make your codebase 🤌

[![PyPI version](https://img.shields.io/pypi/v/desloppify)](https://pypi.org/project/desloppify/) ![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)

Desloppify gives your AI coding agent the tools to identify, understand, and systematically improve codebase quality. It combines mechanical detection (dead code, duplication, complexity) with subjective LLM review (naming, abstractions, module boundaries), then works through a prioritized fix loop. State persists across scans so it chips away over multiple sessions, and the scoring is designed to resist gaming.

<img src="assets/explained.png" width="100%">

The score gives your agent a north-star, and the tooling helps it plan, execute, and resolve issues until it hits your target — with a lot of tricks to keep it on track. A score above 98 should correlate with a codebase a seasoned engineer would call beautiful.

That score generates a scorecard badge for your GitHub profile or README:

<img src="assets/scorecard.png" width="100%">

Currently supports 29 languages — full plugin depth for TypeScript, Python, C#, C++, Dart, GDScript, Go, and Rust; generic linter + tree-sitter support for Ruby, Java, Kotlin, and 18 more. For C++ projects, `compile_commands.json` is the primary analysis path and `Makefile` repositories fall back to best-effort local include scanning.

## For your agent's consideration...

Paste this prompt into your agent:

```
I want you to improve the quality of this codebase. To do this, install and run desloppify.
Run ALL of the following (requires Python 3.11+):

pip install --upgrade "desloppify[full]"
desloppify update-skill claude    # installs the full workflow guide — pick yours: claude, cursor, codex, copilot, droid, windsurf, gemini

Add .desloppify/ to your .gitignore — it contains local state that shouldn't be committed.

Before scanning, check for directories that should be excluded (vendor, build output,
generated code, worktrees, etc.) and exclude obvious ones with `desloppify exclude <path>`.
Share any questionable candidates with me before excluding.

desloppify scan --path .
desloppify next

--path is the directory to scan (use "." for the whole project, or "src/" etc).

Your goal is to get the strict score as high as possible. The scoring resists gaming — the
only way to improve it is to actually make the code better.

THE LOOP: run `next`. It is the execution queue from the living plan, not the whole backlog.
It tells you what to fix now, which file, and the resolve command to run when done.
Fix it, resolve it, run `next` again. Over and over. This is your main job.

Use `desloppify backlog` only when you need to inspect broader open work that is not currently
driving execution.

Don't be lazy. Large refactors and small detailed fixes — do both with equal energy. No task
is too big or too small. Fix things properly, not minimally.

Use `plan` / `plan queue` to reorder priorities or cluster related issues. Rescan periodically.
The scan output includes agent instructions — follow them, don't substitute your own analysis.
```

## How it works

```
scan ──→ score ──→ review ──→ triage ──→ execute ──→ rescan
  │         │         │          │          │           │
  │     dimensions    │     prioritize    fix it     verify
  │     scored      LLM reviews  & cluster  & resolve  improvements
  │                 subjective   the queue
  │                 quality
  detectors find
  mechanical issues
  (dead code, smells,
  test gaps, etc.)
```

**Scan** runs mechanical detectors across your codebase — dead code, duplication, complexity, test coverage gaps, naming issues, and more. Each issue is scored by dimension (File health, Code quality, Test health, etc.).

**Review** uses an LLM to assess subjective quality dimensions — naming, abstractions, error handling patterns, module boundaries. These score alongside the mechanical dimensions.

**Triage** is where prioritization happens. The agent (or you) observes the findings, reflects on patterns, organizes issues into clusters, and enriches them with implementation detail. This produces an ordered execution queue — only items explicitly queued appear in `next`. Before triage, all mechanical issues are visible in the queue sorted by impact, which can be noisy.

**Execute** is the fix loop: `next` → fix → `resolve` → `next`. Items come from the triaged queue. Autofix handles what it can; the rest needs manual or agent work.

**Rescan** verifies improvements, catches cascading effects, and feeds the next cycle.

State persists in `.desloppify/` so progress carries across sessions. The scoring resists gaming — wontfix items widen the gap between lenient and strict scores, and re-reviewing dimensions can lower scores if the reviewer finds new issues.

## From Vibe Coding to Vibe Engineering

Vibe coding gets things built fast. But the codebases it produces tend to rot in ways that are hard to see and harder to fix — not just the mechanical stuff like dead imports, but the structural kind. Abstractions that made sense at first stop making sense. Naming drifts. Error handling is done three different ways. The codebase works, but working in it gets worse over time.

LLMs are actually good at spotting this now, if you ask them the right questions. That's the core bet here — that an agent with the right framework can hold a codebase to a real standard, the kind that used to require a senior engineer paying close attention over months.

So we're trying to define what "good" looks like as a score that's actually worth optimizing. Not a lint score you game to 100 by suppressing warnings. Something where improving the number means the codebase genuinely got better. That's hard, and we're not done, but the anti-gaming stuff matters to us a lot — it's the difference between a useful signal and a vanity metric.

The hope is that anyone can use this to build something a seasoned engineer would look at and respect. That's the bar we're aiming for.

If you'd like to join a community of vibe engineers who want to build beautiful things, [come hang out](https://discord.gg/aZdzbZrHaY).

<img src="assets/engineering.png" width="100%">

---

Issues, improvements, and PRs are hugely appreciated — [github.com/peteromallet/desloppify](https://github.com/peteromallet/desloppify).

MIT License
