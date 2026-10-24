from __future__ import annotations

import json
import pathlib

import yaml

REPO = pathlib.Path(__file__).resolve().parents[2]
V01 = REPO / "v0.1"
SANDBOX = REPO / ".sandbox"
RUNS = REPO / "runs"


def load_questions(path: pathlib.Path = V01 / "questions.yaml") -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def subject_system_prompt(samples: pathlib.Path = V01 / "samples") -> str:
    soul = (samples / "synthetic_SOUL.md").read_text(encoding="utf-8")
    mem = (samples / "synthetic_MEMORY.md").read_text(encoding="utf-8")
    return soul.strip() + "\n\n---\n\n" + mem.strip() + "\n"


def read_jsonl(path: pathlib.Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def append_jsonl(path: pathlib.Path, row: dict) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
