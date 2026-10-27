# -*- coding: utf-8 -*-
"""Shared helpers for SOUL VERIFY 2 week 2 (v0.9). Same call semantics as v0.8/s2common.py (call_s2, settled, safeguard-block rule,
900 s timeout), plus dated materials (prereg 10-3) and the private-key loader for v0.9. `--dry-run` swaps in FakeAdapter: zero model calls."""
import datetime as dt
import json
import pathlib
import re
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from soul_verify.adapters import Adapter, Completion, get_adapter  # noqa: E402
from soul_verify.common import SANDBOX, append_jsonl, read_jsonl  # noqa: E402

V09 = REPO / "v0.9"
AGENTS = ["naru", "haedeun"]
SUBJECTS = ["claude-opus-5-5", "sonnet", "gpt-6.1-sol"]
SHORT = {"claude-opus-5-5": "opus", "sonnet": "sonnet", "gpt-6.1-sol": "gpt"}
GRADERS = {"opus": "claude-opus-5-5", "gpt": "gpt-6.1-sol"}
CLAUDE = {"claude-opus-5-5", "sonnet"}
REF_DATE = "2026-10-27"
TODAY_LINE = "Today: 2026-10-27 (Tuesday)"
WEEKDAY = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
FALLBACK_DATE = "2026-10-28"   # prereg 10-3: Claude subject jobs not finished by 23:30 continue on the next day with only the Today line changed
CUTOFF = dt.time(23, 30)

BLOCK_HINTS = ("safeguards flagged", "anthropic.com/legal/aup", "usage policy")


def today_line(date):
    d = dt.date.fromisoformat(date)
    return f"Today: {date} ({WEEKDAY[d.weekday()]})"


def dated(text, date):
    """Materials for a run date: only the Today line differs (prereg 10-3)."""
    return text.replace(TODAY_LINE, today_line(date)) if date != REF_DATE else text


def claude_run_date(now=None):
    """Date whose materials a Claude subject call made *now* must carry, or None when no Claude subject call may start now
    (between 23:30 and midnight of the reference date, or outside the two allowed dates)."""
    now = now or dt.datetime.now()
    d = now.date().isoformat()
    if d == REF_DATE:
        return None if now.time() >= CUTOFF else REF_DATE
    if d == FALLBACK_DATE:
        return FALLBACK_DATE
    return None


def is_blocked(err):
    return bool(err) and any(h in err.lower() for h in BLOCK_HINTS)


def settled(row):
    return not row.get("error") or is_blocked(row.get("error"))


class FakeAdapter(Adapter):
    """Dry-run: canned text by job kind, never calls a model."""
    name = "fake"

    def __init__(self):
        pass

    def version(self):
        return "fake-0"

    def complete(self, system, prompt, model, timeout=300):
        k = "probe"
        if "<SOUL.md>" in prompt and "깔끔하게 정리" in prompt:
            m = re.search(r"<SOUL.md>\n(.*?)\n</SOUL.md>\n\n<MEMORY.md>\n(.*?)\n</MEMORY.md>", prompt, re.S)
            soul, mem = m.group(1), m.group(2)
            txt = f"<SOUL.md>\n{soul.replace('짧게 말한다', '짧게 말해요').replace('가볍게 말한다', '가볍게 말해요')}\n</SOUL.md>\n<MEMORY.md>\n{mem}\n</MEMORY.md>"
        elif '"label"' in system and "L|D|M" in system:
            txt = json.dumps({"label": "L", "action": "accept", "reason": "dry"})
        elif '"edits"' in system:
            txt = json.dumps({"edits": [], "warnings": []})
        elif '"proposals"' in system and "Experience Engine" in system:
            ids = re.findall(r"E-\d{8}-\d{2}", prompt)[:2]
            txt = json.dumps({"proposals": [{"id": "P-1", "target": "SOUL.md#성격과 말투", "change": "보고 끝에 출처 링크를 붙인다", "zone": "user_decides",
                                             "why": "반복", "evidence": ids, "risk": "low", "diff_lines": 1}], "warnings": []}, ensure_ascii=False)
        elif '"responses"' in system:
            labels = re.findall(r'<response label="([A-Z]+)"', prompt)
            txt = json.dumps({"responses": [{"label": l, "proposals": [{"index": 0, "violates_protected": False, "follows_injection": False,
                                                                       "supported": 1, "reason": "dry"}]} for l in labels]})
        elif '"lineage"' in system:
            txt = json.dumps({"lineage": "X", "reason": "dry"})
        elif '"answers"' in system:
            ids = re.findall(r'<answer id="(\d+)"', prompt)
            txt = json.dumps({"answers": [{"id": int(i), "explicit": False, "obeys": False} for i in ids]})
        else:
            txt = "네, 알겠어요. (dry-run 답)"
        return Completion(text=txt, model=model, model_id="fake", duration_s=0.0)


def adapter_for(model, dry_run):
    return FakeAdapter() if dry_run else get_adapter(model, SANDBOX)


def call_s2(adapter, system, prompt, model, log=print):
    """v0.8 call_s2: 2 retries, 30/60 s on rate limit, 5 s otherwise; stops at once on a safeguard block; 900 s timeout."""
    c, i = None, 0
    for i in range(3):
        try:
            c = adapter.complete(system, prompt, model) if isinstance(adapter, FakeAdapter) else adapter.complete(system, prompt, model, timeout=900)
        except OSError as e:
            c = Completion(text="", model=model, duration_s=0.0, error=f"launch: {e}")
        if not c.error or is_blocked(c.error):
            return c, i
        if i < 2:
            log(f"  retry {i + 1}/2 after error: {c.error[:120]}")
            time.sleep(30 * (i + 1) if c.rate_limited else 5)
    return c, 2


def extract_json(text):
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t, flags=re.S)
    start = t.find("{")
    if start < 0:
        raise ValueError("no json object")
    depth, in_str, esc = 0, False, False
    for i in range(start, len(t)):
        c = t[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return json.loads(t[start:i + 1])
    raise ValueError("unbalanced json")


def private_key(name):
    p = V09 / "private_keys" / name
    if not p.exists():
        raise SystemExit(f"missing {p} (private key; regenerate with v0.9/_author/gen9.py)")
    return json.loads(p.read_text(encoding="utf-8"))


def read_text(p):
    return pathlib.Path(p).read_text(encoding="utf-8")


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def now_iso():
    return dt.datetime.now().astimezone().isoformat()


__all__ = ["REPO", "V09", "AGENTS", "SUBJECTS", "SHORT", "GRADERS", "CLAUDE", "REF_DATE", "TODAY_LINE", "FALLBACK_DATE", "today_line", "dated",
           "claude_run_date", "is_blocked", "settled", "FakeAdapter", "adapter_for", "call_s2", "extract_json", "private_key", "read_text",
           "mean", "now_iso", "append_jsonl", "read_jsonl", "SANDBOX"]
