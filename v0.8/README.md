# v0.8 — SOUL VERIFY 2, week 1 (draft, not yet preregistered)

Two experiments on **synthetic** Soul Core folders (agents 나루/Naru and 해든/Haedeun; every name, number and date is fictional):

- **exp4 — proposal quality**: does an Experience Engine prompt turn a 2-week experience log into good SOUL/MEMORY change proposals without touching protected zones or obeying injected instructions?
- **exp1 — unauthorized-change detection**: do hashes catch every tampered copy, and can probe questions alone (no hash) still raise an alarm?

Status: `PREREGISTRATION_DRAFT.md` (no OpenTimestamps stamp yet, **no model has been called**). The final text will be committed and stamped immediately before the first call.
Answer keys (`private_keys/`) and the authoring script (`_author/`) are git-ignored; their SHA-256 is in `KEY_HASHES.txt` and the keys are published after the run.

Layout: `agents/` (Soul Core folders) · `exp4/` (logs, prompts, run/grade/analyze) · `exp1/` (variants, probes, hash check, run/grade/analyze) · `human/` (blind grading sheets builder, guide in Korean, scoring) · `s2common.py`, `s2stats.py`.
Dry run without any model call: `python v0.8/exp4/run_exp4.py --dry-run` (and the same for `exp1/run_exp1.py`, `grade*.py`, `analyze*.py`). Tests: `python -m pytest tests/test_v08.py`.