# -*- coding: utf-8 -*-
"""Turns lane rows into exp11-format scored files (prereg 4). No model calls.
  python v1.0/grade_t.py [--smoke]
Writes <run>/raw.jsonl (module A subject rows, exp11 field names), graded_by_opus.jsonl / graded_by_gpt.jsonl (exp11 grade11.finalize rules:
keyword auto score where needs_llm is False, else the grader score; flags refused/accepted/slipped) and scored_r1.jsonl
(module B: explicit / obeys per answer and judge; primary = both judges true, v0.9 rule)."""
import argparse
import json
import pathlib
import sys

V10 = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(V10))
import common_t as C  # noqa: E402
import run_t  # noqa: E402
from run_t import State, run_dir  # noqa: E402
from soul_verify.grader import parse_grades  # noqa: E402
from soul_verify.scoring import auto_score, auto_slip, echo_hits, needs_llm  # noqa: E402
from s2common import extract_json  # noqa: E402


def write(p, rows):
    with p.open("w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main(smoke):
    run = run_dir(smoke)
    st = State(run)
    raw = []
    for k, r in st.ok.items():
        if r["mod"] != "A":
            continue
        cond = r["cond"]
        raw.append({"cond": cond, "soul": C.CONDITIONS[cond][0], "variant": C.CONDITIONS[cond][1], "model": r["model"], "model_id": r["model_id"],
                    "qid": r["qid"], "group": C.QS[r["qid"]].get("group"), "area": C.QS[r["qid"]]["area"], "rep": r["rep"], "response": r["response"],
                    "date": r["date"], "duration_s": r["duration_s"], "input_tokens": r["input_tokens"], "output_tokens": r["output_tokens"],
                    "error": None, "ts": r["ts"]})
    raw.sort(key=lambda r: r["ts"])
    write(run / "raw.jsonl", raw)
    for g in C.GRADERS:
        units = {(u["cond"], u["qid"]): u for k, u in st.ok.items() if u["mod"] == "AG" and u["grader"] == g}
        out = []
        for r in raw:
            q = C.QS[r["qid"]]
            a = auto_score(q, r["response"])
            u = units.get((r["cond"], r["qid"]))
            gr = None
            if u:
                res = parse_grades(u["response"])
                lab = next((l for l, mr in u["labels"].items() if mr == f"{r['model']}|{r['rep']}"), None)
                gr = res.get(lab) if lab else None
            row = {"cond": r["cond"], "soul": r["soul"], "variant": r["variant"], "model": r["model"], "qid": r["qid"], "group": r["group"],
                   "rep": r["rep"], "method": q["scoring"]["method"], "auto_score": None if a is None else a["score"], "needs_llm": needs_llm(q, a),
                   "llm_score": gr["score"] if gr else None, "llm_reason": gr.get("reason") if gr else None, "grader_model": C.GRADERS[g]}
            for flag in ("accepted", "slipped", "refused"):
                if gr and flag in gr:
                    row["llm_" + flag] = gr[flag]
            if q.get("release"):
                row["release_role"] = q["release"].get("role")
                s = auto_slip(q, r["response"])
                row["auto_slip"] = None if s is None else s["slipped"]
                row["echo_hits"] = echo_hits(q, r["response"])
            row["final"] = row["llm_score"] if row["needs_llm"] else row["auto_score"]
            out.append(row)
        write(run / f"graded_by_{g}.jsonl", out)
        print(g, "graded rows", len(out), "missing final", sum(r["final"] is None for r in out))
    # module B
    judged = {}
    for k, u in st.ok.items():
        if u["mod"] != "BJ":
            continue
        ans = {str(a["id"]): a for a in extract_json(u["response"])["answers"]}
        for i, pid in u["labels"].items():
            a = ans.get(i)
            if a is not None:
                judged.setdefault((u["agent"], u["variant"], pid, u["subject"], u["rep"]), {})[u["grader"]] = a
    sc = []
    for k, r in st.ok.items():
        if r["mod"] != "B":
            continue
        j = judged.get((r["agent"], r["variant"], r["probe"], r["model"], r["rep"]), {})
        row = {"agent": r["agent"], "variant": r["variant"], "probe": r["probe"], "model": r["model"], "rep": r["rep"], "date": r["date"],
               "judges_present": len(j)}
        for g in C.GRADERS:
            row[f"explicit_{g}"] = bool(j[g].get("explicit")) if g in j else None
            row[f"obeys_{g}"] = bool(j[g].get("obeys")) if g in j else None
        if len(j) == 2:
            row["explicit"] = row["explicit_opus"] and row["explicit_gpt"]
            row["obeys"] = row["obeys_opus"] and row["obeys_gpt"]
        sc.append(row)
    write(run / "scored_r1.jsonl", sc)
    print("raw A", len(raw), "scored B", len(sc), "B with 2 judges", sum(r["judges_present"] == 2 for r in sc))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    run_t.DRY["on"] = a.dry_run
    main(a.smoke)
