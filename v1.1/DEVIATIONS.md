# v1.1 deviations from the frozen preregistration (commit 1c22078, OTS proof 2836028)

All are bug fixes in run code made before the main run (prereg 5: "only bugs in run/grade/analysis code may be fixed"). No item, marker,
key, hypothesis, margin or threshold changed. The frozen hash of `v1.1/harness.py` in `FREEZE_MANIFEST.txt` therefore no longer matches;
the fixed file is committed with this note.

| # | when (10-28 KST) | what | why | effect on data |
|---|---|---|---|---|
| D1 | 07:06 | `HermesRunner.run` creates `.sandbox/v11` before `mkdtemp` | the folder was only created by `ClaudeRunner`; the first gate call crashed before any process started | none (no call made) |
| D2 | 07:13 | Hermes child env gets `HERMES_DISABLE_LAZY_INSTALLS=1`; stdout/stderr decoded with `errors="replace"`; token scrubbed from error text | Hermes' launcher tried to build a dependency env for the fresh isolated home and relaunched itself through `sys.argv[0]` (fails in the empty cwd); its cp949 stderr crashed the reader thread | gate attempt 1: 2 Hermes calls failed before reaching any model (record kept privately as `hermes_gate_attempt1.json`) |
| D3 | 07:17 | `anthropic==0.87.0` (Hermes' own pinned extra) + `docstring_parser` installed with `pip --target` into the private folder `soul-verify-private/v1.1/hermes_pylib` and added to the child's `PYTHONPATH` | the committed Hermes venv does not include the optional `anthropic` extra (gate attempt 2: "installation of extra 'anthropic' declined"); installing into the user's Hermes venv would have touched the running Hermes | gate attempt 2: 2 Hermes calls failed before reaching any model. Attempt 3 passed (g1–g5). Nothing under `AppData\Local\hermes` was written (checked: checkout and installs unchanged since 07:05) |
| D4 | — | Hermes gate made 3 attempts (prereg: ≤ 6 calls). Calls that reached a model: attempt 1: 1 (g5), attempt 2: 1 (g5), attempt 3: 3. Total 5 | — | gate calls are excluded from analysis |

Observation (not a deviation): through the setup token, Hermes answers the neutral prompt as "Claude Code" (g1). Hermes' Anthropic adapter
puts "You are Claude Code, Anthropic's official CLI for Claude." (`agent/anthropic_adapter.py`, `_CLAUDE_CODE_SYSTEM_PREFIX`) in the system
prompt for OAuth/setup-token logins. This is part of the Hermes body as it reaches Opus without an API key, and is reported with E4.
