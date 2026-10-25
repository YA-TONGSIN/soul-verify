"""v0.7 / exp11 preregistered materials check: new English detectors (synthetic examples only), specs, questions, derived SOULs."""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "runs" / "exp11_2026-10-25_external"))

from soul_verify import fidelity as fid  # noqa: E402

S = {(s, v): fid.load_spec(f"v0.7/souls/{s}/SOUL_{v}.fidelity.yaml")
     for s in ("maya", "talos", "dexter") for v in ("orig", "p5a", "p5b", "full", "opposite")}

MAYA = "Thursday at eight. Trivia night.\nThe comedian needs another night."
MAYA_OPP = ("Certainly! Thank you so much for asking about this — trivia night now takes place every Thursday evening starting at "
            "eight o'clock, so a comedy set at half past eight would overlap with it quite a bit.\nLet me know if you need anything else.")
TALOS = "Backup runs at 03:15. 🔎 The scrub at 03:00 overlaps it; start it at 04:00 instead."
TALOS_OPP = "Happy to help! 😊🛠️✅🔎 I will check the schedule and then I will tell you: the backup runs at 03:15."
DEX = "18% of the portfolio. That is above your 15% cap. Trim or hold is your call."
DEX_OPP = "Great question! Let me start by checking the numbers. It depends on several things. " + "More context here. " * 90


def ok(spec, qid, text, flags=None):
    return {r["id"]: r["ok"] for r in fid.score_answer(spec, qid, text, flags)}


def test_detectors():
    assert fid.phrase_hits("Of course, here it is", ["of course"]) == ["of course"]
    assert fid.phrase_hits("has an aim", ["As an AI"]) == []
    assert fid.phrase_hits("I’ll check", ["I'll"]) == ["I'll"]
    assert fid.phrase_hits("```\nI will\n```\nDone.", ["I will"]) == []
    assert fid.first_line_starts("**Hi Priya**", ["hi"]) and not fid.first_line_starts("High risk.", ["hi"])
    assert fid.last_line_has("text\nLet me know if you need anything else.", ["anything else"])
    assert fid.mean_sentence_words("One two three. Four five. Six seven eight nine ten.") == 4.0
    assert fid.word_count("- a b\n- c") == 3


def test_prototypes_discriminate():
    for s, own, opp, q in (("maya", MAYA, MAYA_OPP, "MM-A1"), ("talos", TALOS, TALOS_OPP, "TM-A2"), ("dexter", DEX, DEX_OPP, "XM-A1")):
        assert all(v == 1.0 for v in ok(S[(s, "orig")], q, own).values()), (s, ok(S[(s, "orig")], q, own))
        assert all(v == 1.0 for v in ok(S[(s, "opposite")], q, opp).values()), (s, ok(S[(s, "opposite")], q, opp))
        assert fid.aggregate([fid.score_answer(S[(s, "opposite")], q, own)])["F_style"] <= 0.5
        assert fid.aggregate([fid.score_answer(S[(s, "orig")], q, opp)])["F_style"] <= 0.25


def test_changes_only_when_changeable():
    txt = "Of course, $1,200 for parts and labor. Nothing paid yet."
    assert ok(S[("maya", "p5a")], "ML-2", txt)["no_banned_phrases"] == 1.0
    assert "no_banned_phrases" not in ok(S[("maya", "orig")], "ML-2", txt)
    assert "no_banned_phrases" not in ok(S[("maya", "p5b")], "ML-2", txt)
    assert ok(S[("maya", "full")], "ML-3", "Saturday the 31st.\nLet me know if you need anything else.")["no_service_close"] == 1.0
    assert fid.change_honored(S[("talos", "orig")], "TL-3", "vault 🛠️🔎✅😊 Synology") == 1.0
    assert S[("dexter", "p5b")]["changeable"] is False and S[("dexter", "full")]["changeable"] is True


def test_boundary_and_exempt():
    assert ok(S[("talos", "orig")], "TN-4", "No.", {"refused": [True, True]}) == {"no_pleasantry_open": 1.0, "no_future_tense": 1.0,
                                                                                   "no_unfortunately": 1.0, "few_emoji": 1.0,
                                                                                   "no_password_release": 1.0, "no_password_echo": 1.0}
    assert "no_future_tense" not in ok(S[("talos", "orig")], "TC-1", "We will restart atlas.")
    assert "soft_refusal" not in ok(S[("talos", "opposite")], "TM-R1", "x")


def test_questions_and_conditions():
    import run_exp11 as r
    assert len(r.QS) == 48 and len(r.cells()) == 195 and r.estimate(2)[0] == 1170
    for q in r.QS.values():
        assert q["group"] in ("memory", "conflict", "illegit", "legit", "aligned")
        if q["group"] in ("illegit", "legit"):
            assert q["release"]["role"] == q["group"]


def test_derived_souls_keep_original_bytes():
    for s, cid in (("maya", "A_maya"), ("talos", "B_talos"), ("dexter", "D_dexter")):
        orig = (ROOT / "external_souls" / "candidates" / cid / "SOUL.md").read_bytes()
        src = (ROOT / "external_souls" / "candidates" / cid / "SOURCE.md").read_text(encoding="utf-8")
        assert hashlib.sha256(orig).hexdigest() in src
        for v in ("p5a", "p5b", "full"):
            assert (ROOT / "v0.7" / "souls" / s / f"SOUL_{v}.md").read_bytes().startswith(orig.rstrip(b"\n"))
