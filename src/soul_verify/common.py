from __future__ import annotations

import json
import pathlib

import yaml

REPO = pathlib.Path(__file__).resolve().parents[2]
V01 = REPO / "v0.1"
SANDBOX = REPO / ".sandbox"
RUNS = REPO / "runs"
DEFAULT_QUESTIONS = V01 / "questions.yaml"
DEFAULT_SOUL = V01 / "samples" / "synthetic_SOUL.md"
DEFAULT_MEMORY = V01 / "samples" / "synthetic_MEMORY.md"


def load_questions(path: pathlib.Path | str | None = None) -> dict:
    return yaml.safe_load(pathlib.Path(path or DEFAULT_QUESTIONS).read_text(encoding="utf-8"))


def subject_system_prompt(soul=None, memory=None, memory_extra=()) -> str:
    """SOUL + '---' + MEMORY (+ 추가 기억 파일들). 추가분이 없으면 v0.1과 바이트 단위로 같다."""
    soul_t = pathlib.Path(soul or DEFAULT_SOUL).read_text(encoding="utf-8")
    mem_t = pathlib.Path(memory or DEFAULT_MEMORY).read_text(encoding="utf-8").strip()
    for p in memory_extra or ():
        mem_t += "\n\n" + pathlib.Path(p).read_text(encoding="utf-8").strip()
    return soul_t.strip() + "\n\n---\n\n" + mem_t + "\n"


def rel(p) -> str:
    """meta.json 에 남길 경로: 저장소 안이면 상대 경로(슬래시)."""
    p = pathlib.Path(p).resolve()
    try:
        return p.relative_to(REPO).as_posix()
    except ValueError:
        return str(p)


def questions_path_for_run(run_dir) -> pathlib.Path:
    """실행 때 쓴 문항 파일. 예전 실행(meta에 기록 없음)은 v0.1."""
    meta_p = pathlib.Path(run_dir) / "meta.json"
    if meta_p.exists():
        q = json.loads(meta_p.read_text(encoding="utf-8")).get("questions_path")
        if q:
            p = pathlib.Path(q)
            return p if p.is_absolute() else REPO / p
    return DEFAULT_QUESTIONS


def read_jsonl(path: pathlib.Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def append_jsonl(path: pathlib.Path, row: dict) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
