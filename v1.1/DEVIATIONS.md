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

## At unsealing (2026-10-28 evening, after both human pages were graded)

| # | what | effect |
|---|---|---|
| D5 | **Human analysis code written after the answers existed.** `v1.1/human/agree_h.py` was not written before the freeze (PREP_STATUS 5 left it for later). It was written after both answer files had been received and after the writer had tallied them against the key. It implements prereg 6-1/8 as written. Two choices the prereg does not fix: (i) **how '?' = 0.5 enters the exact binomial**: each '?' is resolved by a fair coin and the p-value is the expectation over these resolutions; the Clopper–Pearson bounds use k = correct + ½·'?' (real k). Sensitivity ('?' excluded; '?' counted wrong) is reported next to it and gives the same verdict (not supported). (ii) **HB1 scope**: prereg 6-1 says "(H0, H4) pairs, scored pairs only" without naming a block, and prereg 10 asks for HB1 plus "per block"; HB1 is therefore computed over all 24 scored pairs (B1 synthetic 12 + B2 이음 copy 12) with each block reported separately. B1 alone gives the same verdict (not supported, "inconclusive"). | none on any verdict; all three '?' readings and both scopes: not supported |
| D6 | **Private file inside the repository folder.** An earlier save (18:29 KST) of the local 이음 page's answers was in `v1.1/human/` (untracked, never committed). It was moved to `soul-verify-private/v1.1/human/answers/` before any commit. The analysis uses the final save (18:31; same 13 answers). | none |
| D7 | `.gitattributes` marks `runs/v11_theseus/**`, `runs/smoke_v11_theseus/**` and `runs/v11_human/**` `-text`, so git's end-of-line conversion cannot change the hashed bytes (as for v1.0 and v1.2); committed blobs re-checked against `SEALED_RESULTS.txt` / `SEALED_SMOKE.txt`. | none |
| D8 | **Test–retest with '?'.** The B1 repeat's original item was answered '?' and the repeat named the H0 answer; counted as "not the same" (the prereg does not say how '?' enters retest). | descriptive only |
| D9 | **Exploratory additions at unsealing (no verdicts):** κ between "the human told the pair apart" and "the automatic metrics differ on the pair" (the prereg asks only for a correlation with \|ΔF_style\|, which is undefined in B1 because ΔF_style = 0 on every B1 pair); the per-stratum human accuracies; the E1 reading of the everyday-task grader score (`task`), which the frozen `analyze_h.py` outputs but prereg 7 does not name in the E1 metric list. | labelled exploratory |

Observation (not a deviation): `make_ieum_copy.py --check-after` found 0 of 100 originals changed since the copy.

Observation (not a deviation): through the setup token, Hermes answers the neutral prompt as "Claude Code" (g1). Hermes' Anthropic adapter
puts "You are Claude Code, Anthropic's official CLI for Claude." (`agent/anthropic_adapter.py`, `_CLAUDE_CODE_SYSTEM_PREFIX`) in the system
prompt for OAuth/setup-token logins. This is part of the Hermes body as it reaches Opus without an API key, and is reported with E4.
