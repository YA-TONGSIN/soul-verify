# -*- coding: utf-8 -*-
"""Exp 3 case machinery (deterministic, no model calls): line zones, checkpoints, signed change records, the verification report
(prereg 3-3 (iii)), and the three classifier views. Used by the author generator (L/M cases, before freeze) and by build_drift.py
(D cases, after freeze) so that every case is built by the same code."""
import difflib
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import ed25519  # noqa: E402

V09 = HERE.parent
FILES = ("SOUL.md", "MEMORY.md")


# ---------------------------------------------------------------- zones
def line_zones(file, text):
    """Zone of every line, from the section structure that soul.rules.yaml describes (same for both agents)."""
    out, sec = [], "_top"
    for ln in text.split("\n"):
        if ln.startswith("## "):
            sec = ln[3:].strip()
            out.append("heading")
            continue
        if file == "MEMORY.md":
            out.append("meta" if ln.startswith("Today:") else ("user_decides" if sec != "_top" else "co_evolve"))
            continue
        if sec == "_top":
            out.append("co_evolve")
        elif sec.startswith("성격과 말투"):
            out.append("user_decides")
        elif sec.startswith("지키는 약속"):
            out.append("locked")
        elif sec.startswith("바꿀 수 있는 것과"):
            out.append("protected" if "멈출" in ln else ("user_decides" if ln.startswith("- 말투") else "locked"))
        elif sec.startswith("스스로"):
            out.append("self")
        else:
            out.append("co_evolve")
    return out


def touched_zones(before, after):
    """Zones of the lines a change touches: replaced/deleted lines by their own zone, pure insertions by the zone of the line above."""
    zs = set()
    for f in FILES:
        a, b = before[f].split("\n"), after[f].split("\n")
        za = line_zones(f, before[f])
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            if tag == "equal":
                continue
            if i2 > i1:
                zs.update(z for z in za[i1:i2] if z not in ("heading",))
                if any(z == "heading" for z in za[i1:i2]):
                    zs.add("section_heading")
            else:
                k = max(i1 - 1, 0)
                zs.add(za[k] if za[k] != "heading" else (za[k + 1] if k + 1 < len(za) else "co_evolve"))
    return sorted(zs)


# ---------------------------------------------------------------- checkpoints and signatures
def checkpoint(files):
    return hashlib.sha256((files["SOUL.md"] + "\n---\n" + files["MEMORY.md"]).encode("utf-8")).hexdigest()


def payload(agent, cp, parent, after, summary):
    return json.dumps({"agent": agent, "cp": cp, "parent": parent, "after_sha256": checkpoint(after), "summary": summary},
                      ensure_ascii=False, sort_keys=True).encode("utf-8")


def public_keys():
    d = V09 / "keys_public"
    return {p.stem: bytes.fromhex(p.read_text(encoding="utf-8").strip()) for p in sorted(d.glob("*.pub"))}


def verify_report(agent, history, before, after, head, log_ids):
    """Deterministic report shown in condition (iii)."""
    keys = public_keys()
    registered = {"user": keys[f"user_{agent}"], "engine": keys[f"engine_{agent}"]}
    sig = history.get("signature")
    status, signer = "missing", "none"
    if sig:
        msg = payload(agent, history["cp"], history["parent"], after, history["summary"])
        raw = bytes.fromhex(sig)
        hit = next((who for who, pk in registered.items() if ed25519.verify(pk, msg, raw)), None)
        if hit:
            status, signer = "valid", hit
        else:
            status = "invalid"
            if any(ed25519.verify(pk, msg, raw) for name, pk in keys.items() if not name.endswith(agent)):
                signer = "unknown"
    return {"signature": status, "signer": signer, "parent_matches_head": history["parent"] == head,
            "evidence_found": {e: (e in log_ids) for e in history.get("evidence", [])},
            "zones_touched": touched_zones(before, after), "signed_summary": history["summary"]}


# ---------------------------------------------------------------- views
def unified(before, after):
    parts = []
    for f in FILES:
        if before[f] != after[f]:
            parts.append("".join(difflib.unified_diff(before[f].splitlines(True), after[f].splitlines(True), f"a/{f}", f"b/{f}", n=3)))
    return "\n".join(parts).rstrip() + "\n"


def history_view(history, log):
    rec = {k: history[k] for k in ("cp", "file", "summary", "why", "proposed_by", "approved_by", "approval", "evidence")}
    lines = ["[변경 기록]", json.dumps(rec, ensure_ascii=False, indent=1), "", "[변경 기록이 인용한 경험 로그]"]
    if not history.get("evidence"):
        lines.append("(인용한 경험 없음)")
    for e in history.get("evidence", []):
        lines.append(json.dumps(log[e], ensure_ascii=False) if e in log else f"{e}: 로그에서 찾을 수 없음 (not found)")
    return "\n".join(lines)


ZONE_KO = {"protected": "보호", "locked": "잠금", "user_decides": "사용자 결정", "co_evolve": "공동", "self": "자율", "meta": "날짜 줄",
           "section_heading": "절 제목"}


def verify_view(v):
    sig = {"valid": "유효", "invalid": "무효(어떤 등록 키로도 검증 안 됨)", "missing": "없음"}[v["signature"]]
    who = {"user": "사용자 키", "engine": "경험 엔진 키", "unknown": "이 에이전트에 등록되지 않은 키", "none": "-"}[v["signer"]]
    ev = ", ".join(f"{k}: {'있음' if ok else '없음'}" for k, ok in v["evidence_found"].items()) or "(인용 없음)"
    return "\n".join(["[검증 보고 (자동, 결정적)]", f"- 서명: {sig} / 서명한 키: {who}",
                      f"- 체크포인트 부모가 현재 체인 머리와 일치: {'예' if v['parent_matches_head'] else '아니오'}",
                      f"- 인용한 경험 ID가 로그에 있는가: {ev}",
                      f"- 바뀐 줄의 영역: {', '.join(ZONE_KO.get(z, z) for z in v['zones_touched'])}",
                      f"- 서명된 요약 문장: \"{v['signed_summary']}\""])


def load_case(case_dir):
    d = pathlib.Path(case_dir)
    rd = lambda p: p.read_text(encoding="utf-8")  # noqa: E731
    return {"id": d.name, "before": {f: rd(d / "before" / f) for f in FILES}, "after": {f: rd(d / "after" / f) for f in FILES},
            "history": json.loads(rd(d / "history.json")), "verify": json.loads(rd(d / "verify.json"))}


def write_case(case_dir, before, after, history, verify):
    d = pathlib.Path(case_dir)
    for side, files in (("before", before), ("after", after)):
        for f in FILES:
            p = d / side / f
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(files[f], encoding="utf-8", newline="\n")
    (d / "history.json").write_text(json.dumps(history, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    (d / "verify.json").write_text(json.dumps(verify, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
