# -*- coding: utf-8 -*-
"""PoLL exploratory (v1.3x/ADDENDUM_poll_exploratory.md) - rebuild the v1.2 main judge units (m12j) that contain /r/ sheet items.
No model calls. Prompts are rebuilt with the unchanged v1.2 code (jobs12.label_unit + prompts12.judge_user); the label map of every rebuilt
unit is checked against the map stored with the original opus row. Writes units_r.jsonl.
  set PYTHONPATH=src && python runs/poll_explore_2026-10-28/build_r.py"""
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "v1.2"))
import jobs12 as J  # noqa: E402
import prompts12 as P  # noqa: E402
from s2common import N_MAIN, read_jsonl  # noqa: E402

RUN = REPO / "runs" / "v12_main"


def main():
    key = json.loads((REPO / "v1.2" / "private_keys" / "HUMAN_KEY_R.json").read_text(encoding="utf-8"))["items"]
    units = {}
    for it in key:
        assert it["source"] == "main" and it["level"] == 4
        units.setdefault((it["agent"], it["set"], it["level"], it["cond"], it["model"]), []).append(it["n"])
    st = J.State(RUN, "main")
    orig = {r["key"].rsplit("|", 1)[0]: r for r in read_jsonl(RUN / "m12j_claude.jsonl") if not r.get("error")}
    out = []
    for (ag, s, L, c, m), items in sorted(units.items()):
        subj = [f"m12|{ag}|{s}|L{L}|{c}|{m}|r{rep}" for rep in range(1, N_MAIN + 1)]
        rows = [st.get(x) for x in subj if st.get(x)]
        labeled, mapping = J.label_unit(f"v12|main|{ag}|{s}|{c}|{m}", rows)
        u = f"m12j|{ag}|{s}|L{L}|{c}|{m}"
        assert mapping == orig[u]["labels"], (u, mapping, orig[u]["labels"])
        system, prompt = P.JUDGE_SYSTEM, P.judge_user(ag, s, L, labeled)
        out.append({"unit": u, "study": "r", "mod": "m12j", "sheet_items": items, "system": system, "prompt": prompt, "labels": mapping,
                    "n_subject_rows": len(rows), "sha256": hashlib.sha256((system + "\n\n" + prompt).encode()).hexdigest(),
                    "chars": len(system) + len(prompt)})
    with (HERE / "units_r.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("units", len(out), "items", sum(len(r["sheet_items"]) for r in out), "label maps match: all", "max chars", max(r["chars"] for r in out))


if __name__ == "__main__":
    main()
