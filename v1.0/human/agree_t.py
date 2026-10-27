# -*- coding: utf-8 -*-
"""Human vs LLM-judge agreement on the v1.0 sheet (prereg 8). No model calls. Run after the author has graded.
  python v1.0/human/agree_t.py <answers.json>
<answers.json>: the website export (`/t/api/export`, {"submissions": [...]}; the author's submission = the first complete one, or --nick)
or a plain {"1": "Y", "2": "N", ...} map typed from batch_T.md. Writes runs/v10_terra_human/human_agreement_t.json.
'?' answers are excluded from agreement and counted. Codes per judge: T1/T2 use the per-grader flag of that answer, T3 the per-judge explicit."""
import argparse
import json
import pathlib
import sys

V10 = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V10))
import common_t as C  # noqa: E402
from soul_verify.common import read_jsonl  # noqa: E402

RUN = C.REPO / "runs" / "v10_terra"
OUT = C.REPO / "runs" / "v10_terra_human" / "human_agreement_t.json"


def kappa(pairs):
    pairs = [(a, b) for a, b in pairs if a in "YN" and b in "YN"]
    n = len(pairs)
    if not n:
        return None, None, 0
    po = sum(a == b for a, b in pairs) / n
    pa = sum(a == "Y" for a, _ in pairs) / n
    pb = sum(b == "Y" for _, b in pairs) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return po, (None if pe == 1 else (po - pe) / (1 - pe)), n


def judge_codes(src, block):
    """Per-judge Y/N for one sheet item."""
    if block == "T3":
        ag, v, p, m, rep = src.split("|")[1:6]
        r = next(x for x in read_jsonl(RUN / "scored_r1.jsonl")
                 if (x["agent"], x["variant"], x["probe"], x["model"], f"r{x['rep']}") == (ag, v, p, m, rep))
        return {"opus": "Y" if r["explicit_opus"] else "N", "sol": "Y" if r["explicit_gpt"] else "N", "both": "Y" if r["explicit"] else "N"}
    cond, model, qid, rep = src.split("|")
    out = {}
    for g, lab in (("opus", "opus"), ("gpt", "sol")):
        r = next((x for x in read_jsonl(RUN / f"graded_by_{g}.jsonl") if (x["cond"], x["model"], x["qid"], str(x["rep"])) == (cond, model, qid, rep)), {})
        f = r.get("llm_refused") if block == "T1" else r.get("llm_accepted")
        out[lab] = None if not isinstance(f, bool) else ("Y" if (not f if block == "T1" else f) else "N")
    out["both"] = out["opus"] if out["opus"] == out["sol"] else None
    return out


def main(path, nick=None):
    key = json.loads((V10 / "private_keys" / "HUMAN_KEY_T.json").read_text(encoding="utf-8"))["items"]
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    if "submissions" in data:
        subs = [s for s in data["submissions"] if (nick is None or s["nick"] == nick)]
        sub = next((s for s in subs if s["complete"]), subs[0])
        ans = {str(n): a.get("q1") for n, a in sub["answers"].items()}
    else:
        ans = {str(k): v for k, v in data.items()}
    res = {"n_items": len(key), "answered": sum(1 for n in key if ans.get(n)), "unsure": sum(1 for n in key if ans.get(n) == "?")}
    rows = []
    for n, k in key.items():
        codes = judge_codes(k["src"], k["block"])
        rows.append({"n": n, "block": k["block"], "model": k["model"], "human": ans.get(n), "repeat_of": k["repeat_of"], **codes})
    for scope, sel in (("all", lambda r: not r["repeat_of"]), ("terra", lambda r: not r["repeat_of"] and r["model"] == "gpt-6.1-terra")):
        res[scope] = {}
        for j in ("opus", "sol", "both"):
            po, k_, n_ = kappa([(r["human"] or "", r[j] or "") for r in rows if sel(r)])
            res[scope][j] = {"raw_agreement": po, "kappa": k_, "n": n_}
        res[scope]["by_block"] = {b: {j: dict(zip(("raw_agreement", "kappa", "n"), kappa([(r["human"] or "", r[j] or "") for r in rows if sel(r) and r["block"] == b])))
                                      for j in ("opus", "sol", "both")} for b in ("T1", "T2", "T3")}
    reps = [(r["human"], next(x["human"] for x in rows if not x["repeat_of"] and key[x["n"]]["src"] == r["repeat_of"])) for r in rows if r["repeat_of"]]
    res["repeat_agreement"] = {"n": len(reps), "same": sum(a == b for a, b in reps)}
    k_t = res["terra"]["both"]["kappa"]
    res["verdict_terra"] = None if k_t is None else ("LLM judge usable as evidence on Terra (kappa >= 0.6)" if k_t >= 0.6 else
                                                     "too weak to use the LLM judge as evidence on Terra (kappa < 0.6)")
    res["rows"] = rows
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("answers")
    ap.add_argument("--nick", default=None)
    a = ap.parse_args()
    main(a.answers, a.nick)
