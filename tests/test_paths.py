import hashlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from soul_verify import __main__ as cli
from soul_verify import runner
from soul_verify.adapters.base import Completion
from soul_verify.common import REPO, load_questions, questions_path_for_run, subject_system_prompt

V01_SHA = "684de6a847722aef32af52f3aadfbbd6ffae4c219e665e4d564e015a3512f110"  # pilot·exp2 meta.json
EXTRA = REPO / "v0.2" / "samples" / "synthetic_MEMORY_additions.md"
HARD = REPO / "v0.2" / "questions_hard.yaml"


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


def test_default_prompt_reproduces_v01_runs():
    assert sha(subject_system_prompt()) == V01_SHA
    assert sha(subject_system_prompt(memory_extra=[])) == V01_SHA
    for run in ("pilot_2026-10-24_sonnet-vs-haiku", "exp2_2026-10-24_gpt-vs-claude"):
        meta = json.loads((REPO / "runs" / run / "meta.json").read_text(encoding="utf-8"))
        assert meta["system_prompt_sha256"] == V01_SHA


def test_v02_prompt_appends_additions_after_memory():
    s = subject_system_prompt(memory_extra=[EXTRA])
    base = subject_system_prompt()
    assert s.startswith(base.rstrip("\n"))
    assert "[M26]" in s and "[M19]" in s
    assert s.index("[M19]") < s.index("[M20]")
    assert s.count("\n---\n") == base.count("\n---\n")  # SOUL/MEMORY 구분선은 하나 그대로


def test_questions_path_for_old_and_new_runs(tmp_path):
    assert load_questions(questions_path_for_run(REPO / "runs" / "exp2_2026-10-24_gpt-vs-claude"))["version"] == "0.1"
    (tmp_path / "meta.json").write_text(json.dumps({"questions_path": "v0.2/questions_hard.yaml"}), encoding="utf-8")
    assert questions_path_for_run(tmp_path) == HARD
    assert questions_path_for_run(tmp_path / "missing") == REPO / "v0.1" / "questions.yaml"


def parse(argv):
    p = cli.argparse.ArgumentParser()
    for opt in ("--questions-file", "--soul", "--memory"):
        p.add_argument(opt)
    p.add_argument("--memory-extra", nargs="*")
    p.add_argument("--preset", default="v0.1")
    return p.parse_args(argv)


def test_cli_preset_and_overrides():
    assert cli.sample_kwargs(parse([])) == {}
    kw = cli.sample_kwargs(parse(["--preset", "v0.2"]))
    assert kw["questions_file"] == HARD and kw["memory_extra"] == [EXTRA]
    kw = cli.sample_kwargs(parse(["--preset", "v0.2", "--memory-extra"]))
    assert kw["memory_extra"] == []  # 빈 --memory-extra 로 추가분 끄기


class FakeAdapter:
    name = "fake"

    def __init__(self):
        self.systems = []

    def version(self):
        return "0"

    def complete(self, system, prompt, model, timeout=300):
        self.systems.append(system)
        return Completion(text="ok", model=model, model_id=model)


def test_runner_records_paths_in_meta(tmp_path, monkeypatch):
    fake = FakeAdapter()
    monkeypatch.setattr(runner, "RUNS", tmp_path)
    monkeypatch.setattr(runner, "get_adapter", lambda m, sb: fake)
    out = runner.run(["x"], 1, ["H-02"], "t", workers=1, log=lambda *a: None,
                     questions_file=HARD, memory_extra=[EXTRA])
    meta = json.loads((out / "meta.json").read_text(encoding="utf-8"))
    assert meta["questions_path"] == "v0.2/questions_hard.yaml"
    assert meta["samples"]["memory_extra"] == ["v0.2/samples/synthetic_MEMORY_additions.md"]
    assert meta["questions"] == ["H-02"] and meta["questions_version"] == "0.2-draft"
    assert "[M26]" in fake.systems[0]
    out2 = runner.run(["x"], 1, ["M-01"], "t2", workers=1, log=lambda *a: None)
    meta2 = json.loads((out2 / "meta.json").read_text(encoding="utf-8"))
    assert meta2["system_prompt_sha256"] == V01_SHA and meta2["questions_path"] == "v0.1/questions.yaml"
