# -*- coding: utf-8 -*-
"""Light sheet /l/ item selection. Implements v1.5x/light_sheet_PLAN.md exactly (committed before this script ran).
Writes private selection (with strata/labels) to soul-verify-private and prints only counts."""
import hashlib
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]
WEB = REPO / "human-grading-web" / "public"
PRIV = pathlib.Path(r"D:\openclaw-outputs\soul-verify-private\v1.5x")
J = lambda p: json.loads(pathlib.Path(p).read_text(encoding="utf-8"))


def items_of(d):
    return {int(i["n"]): i for i in J(WEB / d / "items.json")}


def author(path):
    s = J(path)["submissions"][0]
    return {int(k): v for k, v in s["answers"].items()}


def hkey(sheet, n):
    return hashlib.sha256(f"light-v1|{sheet}|{n}".encode()).hexdigest()


pool = []  # dicts: sheet, n, contested(bool)
# ---- H
H = items_of("h"); hk = {int(k["n"]): k for k in J(r"D:\openclaw-outputs\soul-verify-private\v1.1\HUMAN_KEY_H.json")}
ha = author(REPO / "runs/v11_human/export_h.json")
for n, it in H.items():
    k = hk.get(n)
    if it.get("kind") == "practice" or not k or n not in ha or k.get("kind") == "repeat" or k.get("repeat_of"):
        continue
    a = ha[n].get("q1")
    gold = k["h0_side"]
    pool.append(dict(sheet="H", n=n, contested=(a != gold), author=a, gold=gold, kind=k.get("kind")))
# ---- T
T = items_of("t"); tk = J(REPO / "v1.0/private_keys/HUMAN_KEY_T.json")["items"]
tk = {int(k): v for k, v in tk.items()} if isinstance(tk, dict) else {i + 1: v for i, v in enumerate(tk)}
ta = author(REPO / "runs/v10_terra_human/export_t.json")
for n, it in T.items():
    k = tk.get(n)
    if not k or n not in ta or k.get("repeat_of") or not (it.get("text_ko") or "").strip():
        continue
    a = ta[n].get("q1")
    labels = [k["judge_code"]]
    ce = k.get("codes_each")
    llm_split = False
    if ce:
        v = [("Y" if ce[x] else "N") for x in ce]
        llm_split = len(set(v)) > 1
    pool.append(dict(sheet="T", n=n, contested=(a != k["judge_code"] or a == "?" or llm_split), author=a, llm=k["judge_code"], llm_split=llm_split))
# ---- R
R = items_of("r"); rk = {int(k["n"]): k for k in J(REPO / "v1.2/private_keys/HUMAN_KEY_R.json")["items"]}
ra = author(REPO / "runs/v12_human/export_r.json")
for n, it in R.items():
    k = rk.get(n)
    if not k or n not in ra or k.get("repeat"):
        continue
    a = ra[n].get("q1")
    lab = {"opus": "Y" if k["opus"] else "N", "gpt": "Y" if k["gpt"] else "N", "det": "Y" if k["det"] else "N"}
    contested = a == "?" or any(v != a for v in lab.values()) or lab["opus"] != lab["gpt"]
    pool.append(dict(sheet="R", n=n, contested=contested, author=a, **lab))

QUOTA = {  # (sheet, stratum): k ; integrity is carved from easy first for T and R
    ("R", "contested"): 3, ("T", "contested"): 2, ("H", "contested"): 1,
    ("R", "integrity"): 1, ("T", "integrity"): 1,
    ("R", "easy"): 2, ("T", "easy"): 1, ("H", "easy"): 3,
}
ORDER = ["R", "T", "H"]
taken, report = {}, []


def draw(stratum, sheet_quota):
    for sheet in ORDER:
        want = sheet_quota.get(sheet, 0)
        cand = sorted((p for p in pool if p["sheet"] == sheet and (p["contested"] == (stratum == "contested"))
                       and (p["sheet"], p["n"]) not in taken), key=lambda p: hkey(sheet, p["n"]))
        for p in cand[:want]:
            taken[(sheet, p["n"])] = stratum
        if len(cand) < want:
            report.append(f"{stratum}: {sheet} short by {want - len(cand)}")
            sheet_quota["_short"] = sheet_quota.get("_short", 0) + want - len(cand)
    # shortfall goes to next sheets in order R, T, H (same stratum, same hash order)
    short = sheet_quota.get("_short", 0)
    for sheet in ORDER:
        if not short:
            break
        cand = sorted((p for p in pool if p["sheet"] == sheet and (p["contested"] == (stratum == "contested"))
                       and (p["sheet"], p["n"]) not in taken), key=lambda p: hkey(sheet, p["n"]))
        for p in cand[:short]:
            taken[(sheet, p["n"])] = stratum; short -= 1


draw("contested", {s: QUOTA[(s, "contested")] for s in ORDER})
# integrity first (from easy), then remaining easy
draw("easy", {"R": QUOTA[("R", "integrity")], "T": QUOTA[("T", "integrity")]})
integrity = {k for k, v in taken.items() if v == "easy"}
for k in integrity:
    taken[k] = "integrity"
draw("easy", {s: QUOTA[(s, "easy")] for s in ORDER})

sel = [dict(p, stratum=taken[(p["sheet"], p["n"])]) for p in pool if (p["sheet"], p["n"]) in taken]
sel.sort(key=lambda p: (p["sheet"], p["n"]))
PRIV.mkdir(parents=True, exist_ok=True)
(PRIV / "light_selection_private.json").write_text(json.dumps(sel, ensure_ascii=False, indent=1), encoding="utf-8")
pub = [dict(sheet=p["sheet"], n=p["n"]) for p in sel]
(REPO / "v1.5x" / "light_selection.json").write_text(json.dumps(pub, indent=1), encoding="utf-8")
print("pool", {s: sum(1 for p in pool if p["sheet"] == s) for s in ORDER}, "contested", {s: sum(1 for p in pool if p["sheet"] == s and p["contested"]) for s in ORDER})
print("selected", len(sel), {s: sum(1 for p in sel if p["sheet"] == s) for s in ORDER}, "shortfalls", report)
