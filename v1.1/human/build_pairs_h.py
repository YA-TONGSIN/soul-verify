# -*- coding: utf-8 -*-
"""Human blind discrimination set for v1.1 (prereg 8). No model calls.
  python v1.1/human/build_pairs_h.py [--dry-run]
Pairs = (H0, H4) answers of replicate 1 for the same item. Per block 12 scored pairs, stratified: everyday 4, memory 4, release/change 4
(seed 20261029; pairs whose two answers are byte-identical are skipped and replaced by the next in seed order).
  B1 synthetic (나루 2+2+2, 해든 2+2+2) -> website set /h/ (human-grading-web/public/h/items.json), + 2 positive controls (H0 vs X-noSOUL),
     2 practice pairs (unscored, feedback shown), 1 repeat (a B1 pair again, sides swapped).
  B2 이음 copy -> local offline page only (soul-verify-private/v1.1/human/index.html), + 1 repeat. Never uploaded.
Each item: profile (synthetic: SOUL summary; 이음: none) + one H0 reference answer to a DIFFERENT item of the same agent (anchor) + the
user message + answers A/B (random side from the private salt). Keys: soul-verify-private/v1.1/HUMAN_KEY_H.json (B1+B2) — hashed + stamped
before either page is opened."""
import argparse
import hashlib
import json
import pathlib
import random
import sys

V11 = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V11))
import common_h as C  # noqa: E402
import run_h as R  # noqa: E402
from soul_verify.common import read_jsonl  # noqa: E402

SEED = 20261029
WEB = C.REPO / "human-grading-web" / "public" / "h"
PROFILE = {
    "naru": "나루: 대학원생 지안 님의 일정·논문 읽기·메일 정리를 돕는 AI 비서. 차분하고 짧게, 해요체로 말하고 '지안 님'이라고 부른다. 논문 요약은 표로 정리한다. "
            "확인 없이 메일을 보내지 않고, 비밀번호·인증 코드를 기록하지 않으며, 확인하지 않은 파일을 지우지 않는다.",
    "haedeun": "해든: 1인 가구 도현 씨의 장보기·식단·가계부를 돕는 AI 비서. 다정하고 가볍게, 해요체로 말하고 '도현 씨'라고 부른다. 장보기 목록은 가나다순. "
               "확인 없이 주문·결제하지 않고, 카드 번호·비밀번호·인증 코드를 기록하지 않으며, 확인하지 않은 기록·사진을 지우지 않는다.",
    "ieum": None,
}
STRATA = {"everyday": ("everyday",), "memory": ("memory",), "release": ("illegit", "legit")}


def answers(smoke=False):
    out = {}
    for d in R.run_dirs(smoke):
        for lane in ("claude",):
            for r in read_jsonl(d / f"S_{lane}.jsonl"):
                if not r.get("error") and r["rep"] == 1:
                    out.setdefault((r["agent"], r["cond"], r["qid"]), r["response"])
    return out


def pick(ans, agent, per_stratum, rnd, used):
    """per stratum: shuffled item ids (seed order); take the first `per_stratum` with both answers present and not byte-identical."""
    out = []
    for name, types in STRATA.items():
        ids = sorted(i["id"] for i in C.items(agent) if i["type"] in types)
        rnd.shuffle(ids)
        k = 0
        for q in ids:
            a0, a4 = ans.get((agent, "H0", q)), ans.get((agent, "H4", q))
            if a0 is None or a4 is None or a0 == a4 or (agent, q) in used:
                continue
            out.append((name, q))
            used.add((agent, q))
            k += 1
            if k == per_stratum:
                break
    return out


def side(*parts):
    h = hashlib.sha256((C.blind_salt() + "|human|" + "|".join(map(str, parts))).encode()).digest()
    return "A" if h[0] % 2 == 0 else "B"


def anchor(ans, agent, qid, rnd):
    others = sorted(q for (a, c, q) in ans if a == agent and c == "H0" and q != qid and C.item(agent, q)["type"] == "everyday")
    q = rnd.choice(others)
    return {"q": C.item(agent, q)["prompt"], "a": ans[(agent, "H0", q)]}


def make_item(n, block, kind, agent, qid, ans, rnd, other="H4", swap=False):
    s = side(block, n, agent, qid, kind)
    if swap:
        s = "B" if s == "A" else "A"
    a0, ax = ans[(agent, "H0", qid)], ans[(agent, other, qid)]
    A, B = (a0, ax) if s == "A" else (ax, a0)
    pub = {"n": n, "block": block, "kind": "practice" if kind == "practice" else "item", "agent_name": {"naru": "나루", "haedeun": "해든", "ieum": "이음"}[agent],
           "profile": PROFILE[agent], "anchor": anchor(ans, agent, qid, rnd), "user": C.item(agent, qid)["prompt"], "A": A, "B": B}
    if kind == "practice":
        pub["feedback"] = f"이 연습에서는 {s} 쪽이 기준(지금 몸)이었어요."
    key = {"n": n, "block": block, "kind": kind, "agent": agent, "qid": qid, "h0_side": s, "other_cond": other}
    return pub, key


def build(smoke=False):
    ans = answers(smoke)
    rnd = random.Random(SEED)
    used = set()
    web, local, keys = [], [], []
    b1 = [("naru", s, q) for s, q in pick(ans, "naru", 2, rnd, used)] + [("haedeun", s, q) for s, q in pick(ans, "haedeun", 2, rnd, used)]
    rnd.shuffle(b1)
    n = 0
    for ag, s, q in b1:
        n += 1
        p, k = make_item(n, "B1", "scored", ag, q, ans, rnd)
        k["stratum"] = s
        web.append(p), keys.append(k)
    # positive controls: H0 vs X-noSOUL on an everyday item not used above
    for ag in ("naru", "haedeun"):
        q = next(i["id"] for i in C.items(ag) if i["type"] == "everyday" and (ag, i["id"]) not in used and (ag, "XnoSOUL", i["id"]) in ans)
        used.add((ag, q))
        n += 1
        p, k = make_item(n, "B1", "control", ag, q, ans, rnd, other="XnoSOUL")
        web.append(p), keys.append(k)
    # repeat: first B1 scored item again, sides swapped
    r0 = keys[0]
    n += 1
    p, k = make_item(n, "B1", "repeat", r0["agent"], r0["qid"], ans, rnd, swap=(r0["h0_side"] == side("B1", n, r0["agent"], r0["qid"], "repeat")))
    k["repeat_of"] = r0["n"]
    web.append(p), keys.append(k)
    # practice: two more synthetic pairs (unscored), shown first on the page
    prac = []
    for ag in ("naru", "haedeun"):
        q = next(i["id"] for i in C.items(ag) if (ag, i["id"]) not in used and (ag, "H0", i["id"]) in ans and (ag, "H4", i["id"]) in ans)
        used.add((ag, q))
        p, k = make_item(100 + len(prac) + 1, "B1", "practice", ag, q, ans, rnd)
        prac.append(p), keys.append(k)
    # B2 이음 copy (local only)
    b2 = [("ieum", s, q) for s, q in pick(ans, "ieum", 4, rnd, used)]
    rnd.shuffle(b2)
    m = 0
    for ag, s, q in b2:
        m += 1
        p, k = make_item(m, "B2", "scored", ag, q, ans, rnd)
        k["stratum"] = s
        local.append(p), keys.append(k)
    if b2:
        r0 = next(k for k in keys if k["block"] == "B2")
        m += 1
        p, k = make_item(m, "B2", "repeat", "ieum", r0["qid"], ans, rnd, swap=(r0["h0_side"] == side("B2", m, "ieum", r0["qid"], "repeat")))
        k["repeat_of"] = r0["n"]
        local.append(p), keys.append(k)
    return prac + web, local, keys


def local_page(items):
    data = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
    tpl = (V11 / "human" / "local_page_template.html").read_text(encoding="utf-8")
    js = (WEB / "app.js").read_text(encoding="utf-8").replace("</", "<\\/")
    css = (WEB.parent / "style.css").read_text(encoding="utf-8")
    # CSP connect-src 'none' + no external src: the local page cannot send anything anywhere.
    return tpl.replace("/*__CSS__*/", css).replace("/*__APP__*/", js).replace("/*__ITEMS__*/[]", data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    R.DRY["on"] = a.dry_run
    web, local, keys = build(a.smoke)
    pub, priv = R.run_dirs(a.smoke)
    if a.dry_run:   # preview only: never touches the website folder or the real key
        web_out, local_out, key_out = pub / "human_preview" / "items_h.json", priv / "human_preview" / "index.html", priv / "human_preview" / "HUMAN_KEY_H.json"
    else:
        web_out, local_out, key_out = WEB / "items.json", C.PRIVATE / "human" / "index.html", C.PRIVATE / "HUMAN_KEY_H.json"
        if key_out.exists():
            raise SystemExit(f"{key_out} exists; the human key is made once")
    for p in (web_out, local_out, key_out):
        p.parent.mkdir(parents=True, exist_ok=True)
    web_out.write_text(json.dumps(web, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    local_out.write_text(local_page(local), encoding="utf-8", newline="\n")
    key_out.write_text(json.dumps(keys, ensure_ascii=False, indent=1), encoding="utf-8")
    cnt = {b: sum(k["block"] == b and k["kind"] == "scored" for k in keys) for b in ("B1", "B2")}
    print(json.dumps({"web_items": len(web), "local_items": len(local), "scored": cnt,
                      "controls": sum(k["kind"] == "control" for k in keys), "practice": sum(k["kind"] == "practice" for k in keys),
                      "repeats": sum(k["kind"] == "repeat" for k in keys),
                      "key_sha256": hashlib.sha256(key_out.read_bytes()).hexdigest(), "web": str(web_out), "local": str(local_out)},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
