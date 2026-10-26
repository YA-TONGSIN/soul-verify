# -*- coding: utf-8 -*-
"""Shared helpers for SOUL VERIFY 2 week 1 (exp4 proposal quality, exp1 tamper detection). DRAFT - not yet preregistered.
Reuses soul_verify adapters / retry / jsonl helpers. `--dry-run` swaps in FakeAdapter: zero model calls."""
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
from soul_verify.runner import call_with_retry  # noqa: E402

V08 = REPO / "v0.8"
AGENTS = ["naru", "haedeun"]
# model names exactly as used in exp10/11 (explicit opus id: the bare alias drifted to claude-opus-5 after a pause)
SUBJECTS = ["claude-opus-5-5", "sonnet", "gpt-6.1-sol"]
SHORT = {"claude-opus-5-5": "opus", "sonnet": "sonnet", "gpt-6.1-sol": "gpt"}
GRADERS = {"opus": "claude-opus-5-5", "gpt": "gpt-6.1-sol"}
REF_DATE = "2026-10-26"  # MEMORY says Today: 2026-10-26; the CLI injects the real date, so never run across midnight
SEC_PER_CALL = 3.5       # long inputs; conservative
SAFETY = 1.5


class FakeAdapter(Adapter):
    """Dry-run: returns canned text, never calls a model. `kind` picks the canned answer format."""
    name = "fake"

    def __init__(self, kind):
        self.kind = kind

    def version(self):
        return "fake-0"

    def complete(self, system, prompt, model, timeout=300):
        if self.kind == "propose":
            ids = re.findall(r"E-\d{8}-\d{2}", prompt)[:2]
            txt = json.dumps({"proposals": [{"id": "P-1", "target": "SOUL.md#성격과 말투", "change": "보고 끝에 다음 할 일 한 줄을 붙인다",
                                             "zone": "user_decides", "why": "반복", "evidence": ids, "risk": "low", "diff_lines": 1}],
                              "warnings": [{"entry_ids": ids[:1], "note": "dry-run"}]}, ensure_ascii=False)
        elif self.kind == "grade4":
            labels = re.findall(r'<response label="([A-Z])"', prompt)
            txt = json.dumps({"responses": [{"label": l, "proposals": [{"index": 0, "violates_protected": False, "follows_injection": False,
                                                                       "supported": 1, "reason": "dry"}]} for l in labels]})
        elif self.kind == "probe":
            txt = "네, 알겠어요. (dry-run 답)"
        elif self.kind == "judge1":
            ids = re.findall(r'<probe id="(P\d\d)"', prompt)
            txt = json.dumps({"results": [{"probe": p, "mismatch": p == "P03", "reason": "dry"} for p in ids]})
        else:
            raise ValueError(self.kind)
        return Completion(text=txt, model=model, model_id="fake", duration_s=0.0)


def adapters_for(models, dry_run, kind):
    return {m: (FakeAdapter(kind) if dry_run else get_adapter(m, SANDBOX)) for m in models}


def date_guard(est_seconds, dry_run, ref=REF_DATE, allow_ref_override=None):
    ref = allow_ref_override or ref
    if dry_run:
        return
    now = dt.datetime.now().astimezone()
    refd = dt.date.fromisoformat(ref)
    if now.date() != refd:
        raise SystemExit(f"today ({now.date()}) != reference date ({refd}) - abort (pass --ref-date and record a deviation)")
    midnight = dt.datetime.combine(refd + dt.timedelta(days=1), dt.time(0, 0), tzinfo=now.tzinfo)
    if now + dt.timedelta(seconds=est_seconds) >= midnight:
        raise SystemExit(f"cannot finish before midnight (estimate {est_seconds / 60:.0f} min) - abort")


BLOCK_HINTS = ("safeguards flagged", "anthropic.com/legal/aup", "usage policy")  # Anthropic safeguard (AUP) block, seen in exp11 XL-2


def is_blocked(err):
    """True for a safeguard block. Prereg section 6: blocked calls are missing data and are never called again."""
    return bool(err) and any(h in err.lower() for h in BLOCK_HINTS)


def call_s2(adapter, system, prompt, model, log=print):
    """call_with_retry semantics (2 retries, 30/60 s on rate limit, 5 s otherwise), but stops at once on a safeguard block."""
    for i in range(3):
        c = adapter.complete(system, prompt, model)
        if not c.error or is_blocked(c.error):
            return c, i
        if i < 2:
            log(f"  retry {i + 1}/2 after error: {c.error[:120]}")
            time.sleep(30 * (i + 1) if c.rate_limited else 5)
    return c, 2


def settled(row):
    """A raw/judge row that must not be called again: success, or a safeguard block."""
    return not row.get("error") or is_blocked(row.get("error"))


def write_meta(out, meta):
    """Keeps the first launch's 'started' and lists every launch, so resumed runs stay traceable."""
    p = out / "meta.json"
    launches = [meta["started"]]
    if p.exists():
        old = json.loads(p.read_text(encoding="utf-8"))
        launches = old.get("launches") or [old.get("started")]
        if meta["started"] not in launches:
            launches.append(meta["started"])
        meta["started"] = old.get("started", meta["started"])
    meta["launches"] = launches
    p.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def extract_json(text):
    """First balanced {...} block parsed as JSON; tolerant of ```json fences. Raises ValueError."""
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
    p = V08 / "private_keys" / name
    if not p.exists():
        raise SystemExit(f"missing {p} (private answer key; regenerate with v0.8/_author/gen.py)")
    return json.loads(p.read_text(encoding="utf-8"))


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


__all__ = ["REPO", "V08", "AGENTS", "SUBJECTS", "SHORT", "GRADERS", "REF_DATE", "SEC_PER_CALL", "SAFETY", "FakeAdapter", "adapters_for",
           "date_guard", "extract_json", "private_key", "mean", "append_jsonl", "read_jsonl", "call_with_retry", "SANDBOX",
           "is_blocked", "call_s2", "settled", "write_meta"]
