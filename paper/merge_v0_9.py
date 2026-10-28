"""Assemble paper/draft_v0_9.md from draft_v0_8.md (Parts I-II), draft_v0_9_part3.md, draft_v0_9_part4.md
and the new v0.9 text in paper/v0_9_src/ (abstract, introduction tail, Part III/IV heads, limitations,
conclusion, appendices E-F).

Renumbering:
  v0.8 §7-§9           -> §9-§11 (Limitations, Practical observations, Conclusion)
  Part III  III.k(.m)  -> §7.(k+1)(.m)   (III.8 Limitations -> §9.4; III.9 revision note -> Appendix E)
  Part IV   IV.k(.m)   -> §8.(k+1)(.m) for k <= 4, IV.6 -> §8.6 (IV.5 Limitations -> §9.4)
  Tables    v0.8 1-28 unchanged; III-1..III-11 (+III-4b) -> 29-40; IV timeline/IV-1/IV-2 -> 41/42/43
Usage: python paper/merge_v0_9.py      (no model calls; reads and writes files in paper/ only)
"""
import pathlib
import re

P = pathlib.Path(__file__).resolve().parent
SRC = P / "v0_9_src"


def read(p):
    return p.read_text(encoding="utf-8").replace("\r\n", "\n")


def cut(text, start, end=None):
    i = text.index(start)
    j = text.index(end, i) if end else len(text)
    return text[i:j]


def must_replace(text, old, new, count=1):
    assert text.count(old) == count, (old[:80], text.count(old))
    return text.replace(old, new)


v08 = read(P / "draft_v0_8.md")
p3 = read(P / "draft_v0_9_part3.md")
p4 = read(P / "draft_v0_9_part4.md")
frag = {n: read(SRC / f"{n}.md").strip("\n") + "\n" for n in
        ["abstract", "intro_tail", "part3_head", "part4_head", "limitations", "conclusion", "appendix_ef"]}

# ---------------------------------------------------------------- v0.8 pieces
front = cut(v08, "**Wunjong Shin**", "## Abstract")
intro_head = cut(v08, "## 1 Introduction", "**Part II: changes to the documents.**")
body = cut(v08, "\n---\n\n## 2 Related Work", "### 6.10 What Part II does not show")
observations = cut(v08, "## 8 Practical observations", "\n---\n\n## 9 Conclusion")
back = cut(v08, "## Code and data availability", "## Appendix E. Changes from v0.7.1")


def renum_v08(t):
    # §7 -> §9, §8 -> §10, §9 -> §11 (only whole section numbers; §5.7 etc. untouched)
    return re.sub(r"§([789])(?![\d.]\d)", lambda m: "§" + {"7": "9", "8": "10", "9": "11"}[m.group(1)], t)


intro_head = renum_v08(intro_head)
body = renum_v08(body)
observations = renum_v08(observations)
back = renum_v08(back)

# §6.10 -> pointer to the unified limitations
body += ("### 6.10 What Part II does not show\n\n"
         "The limitations of Part II are collected with those of the other parts in §9 (Part II specifics in §9.3).\n")

# Practical observations: new number, intro sentence, items 14-15
observations = must_replace(observations, "## 8 Practical observations", "## 10 Practical observations")
observations = must_replace(
    observations,
    "items 11–13 come from Part II (two further synthetic agents) and are equally unvalidated.",
    "items 11–13 come from Part II (two further synthetic agents) and are equally unvalidated; "
    "items 14–15 come from Parts III and IV and are hypotheses as well.")
observations = must_replace(
    observations,
    "whether this helps in a real deployment is untested.\n",
    "whether this helps in a real deployment is untested.\n"
    "14. *(Hypothesis)* **Check how the MEMORY reaches the model, not only where the SOUL sits** (§7.4.4–7.4.6). "
    "With the model fixed, moving the SOUL from the system prompt into the user message changed nothing measurable, "
    "while replacing the full MEMORY by top-5 retrieval lowered memory accuracy by 0.21, mostly on facts worded far "
    "from the question. A harness change that looks cosmetic can still change what the agent remembers.\n"
    "15. *(Hypothesis)* **Pin the entries that govern behavior, and keep the full memory when possible** (§8). "
    "A pinned block of the latest corrections, decisions, and preferences recovered every pinned fact under "
    "retrieval and none of the unpinned ones; it is a floor, not a replacement. This rests on a borderline, "
    "LLM-graded test on two synthetic agents.\n")

# Back matter
back = must_replace(
    back,
    "the web page for the planned additional raters is in `human-grading-web/`.",
    "the web page for the planned additional raters is in `human-grading-web/`. Parts III and IV: preregistrations, "
    "deviation reports, notes, and analysis code are in `v1.0/`, `v1.1/`, `v1.2/`, `v1.3x/`, and `v1.4a/`; run rows "
    "and analyses in `runs/v10_terra/`, `runs/v10_terra_human/`, `runs/v11_theseus/`, `runs/v11_human/`, "
    "`runs/v12_pilot/`, `runs/v12_main/`, `runs/v12_human/`, `runs/poll_explore_2026-10-28/`, and `runs/v14a_pin/`; "
    "the human pages in `human-grading-web/`. The private-copy block of wave 4 is not included (hashes only, "
    "`v1.1/KEY_HASHES.txt`).")
back = must_replace(
    back,
    "We make no claims about consciousness or moral status of the models.",
    "**Parts III and IV.** Agents, memories, and items are synthetic, apart from the MIT-licensed external SOULs "
    "reused in wave 3. The exploratory private-copy block of wave 4 used a redacted copy of the author's own agent "
    "documents at the author's decision; it was graded by Opus only, so that private answers were not sent to a "
    "second provider, and only aggregates and hashes are published. Hermes reached Opus through a setup token the "
    "author created for this study only. The Korean reference translation on wave 3's human page was produced by an "
    "LLM. The only human grader is the author. We make no claims about consciousness or moral status of the models.")
back = must_replace(
    back,
    "The proof of this version (v0.8) is created after its commit and is pending until a later upgrade.",
    "Proofs of Parts III and IV are in Appendix F (Table F1). The proof of this version (v0.9) is created after its "
    "commit and is pending until a later upgrade.")
back = must_replace(
    back,
    "v0.7.1 → v0.8: Part II (SOUL VERIFY 2, two preregistered weeks) added; Part I unchanged in results (Appendix E).",
    "v0.7.1 → v0.8: Part II (SOUL VERIFY 2, two preregistered weeks) added; Part I unchanged in results. "
    "v0.8 → v0.9: Parts III and IV (four preregistered waves and one exploratory rerun) added; abstract, "
    "contributions, limitations (now one section), and conclusion rewritten; Parts I and II unchanged in results "
    "(Appendix E).")

# ---------------------------------------------------------------- Part III
T3 = {"1": 29, "2": 30, "3": 31, "4": 32, "4b": 33, "5": 34, "6": 35, "7": 36, "8": 37, "9": 38, "10": 39, "11": 40}
p3 = cut(p3, "## III.0 Overview", "\n---\n\n## III.8 Limitations")
p3 = re.sub(r"Table III-(\d+b?)", lambda m: f"Table {T3[m.group(1)]}", p3)
p3 = re.sub(r"^## III\.(\d+) ", lambda m: f"### 7.{int(m.group(1)) + 1} ", p3, flags=re.M)
p3 = re.sub(r"^### III\.(\d+)\.(\d+) ", lambda m: f"#### 7.{int(m.group(1)) + 1}.{m.group(2)} ", p3, flags=re.M)


def ref3(m):
    k, rest = int(m.group(1)), m.group(2) or ""
    if k == 8:
        return "§9.4"
    if k == 9:
        return "Appendix E"
    return f"§7.{k + 1}{rest}"


p3 = re.sub(r"(?<![\w§-])III\.(\d+)((?:\.\d+)*)", ref3, p3)
p3 = must_replace(p3, "their Bitcoin anchoring had not been checked when this draft was written.",
                  "their Bitcoin blocks are listed in Appendix F.")
p3 = must_replace(p3, "(prereg §8)", "(preregistration, section 8)")
p3 = must_replace(p3, "At the time of this draft all three seals are open.",
                  "All three seals have since been opened.")
p3 = must_replace(p3, "The writer of the first version of this draft did not open any sealed file; for the update, "
                      "the writer used the published files after the seals were opened.",
                  "The writer of the first draft of Part III did not open any sealed file; later drafts used the "
                  "files published after the seals were opened.")
assert "III." not in p3.replace("Part III", ""), re.findall(r".{20}III\..{20}", p3)

# ---------------------------------------------------------------- Part IV
p4 = cut(p4, "## IV.0 Overview")
p4 = p4[:p4.index("## IV.5 Limitations")] + p4[p4.index("## IV.6 Interpretation"):]
MAP4 = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: None, 6: 6}
p4 = re.sub(r"^## IV\.(\d+) ", lambda m: f"### 8.{MAP4[int(m.group(1))]} ", p4, flags=re.M)
p4 = re.sub(r"^### IV\.(\d+)\.(\d+) ", lambda m: f"#### 8.{MAP4[int(m.group(1))]}.{m.group(2)} ", p4, flags=re.M)
p4 = must_replace(p4, "#### 8.4.1 Confirmatory (Table IV-1)\n\n",
                  "#### 8.4.1 Confirmatory (Table 42)\n\n**Table 42. Wave 6 confirmatory results (Holm over three).**\n\n")
p4 = must_replace(p4, "#### 8.4.3 Pinned versus unpinned targets (exploratory, Table IV-2)\n\n",
                  "#### 8.4.3 Pinned versus unpinned targets (exploratory, Table 43)\n\n"
                  "**Table 43. Memory accuracy by target and item type (exploratory; number of cells in parentheses).**\n\n")
p4 = must_replace(p4, "#### 8.2.1 Order of events (all 2026-10-28, KST)\n\n",
                  "#### 8.2.1 Order of events (all 2026-10-28, KST)\n\n**Table 41. Wave 6 timeline (2026-10-28, KST).**\n\n")
p4 = re.sub(r"(?<![\w§-])IV\.(\d+)((?:\.\d+)*)",
            lambda m: "§9.4" if m.group(1) == "5" else f"§8.{MAP4[int(m.group(1))]}{m.group(2) or ''}", p4)
assert "IV." not in p4.replace("Part IV", ""), re.findall(r".{20}IV\..{20}", p4)
assert "Table IV" not in p4 and "Table III" not in p3

# ---------------------------------------------------------------- assemble
TITLE = ("# SOUL VERIFY: Behavioral Carry-Over of an Agent's Identity Documents Across Model and Harness Changes, "
         "and Checking Changes to the Documents, in Eight Preregistered Studies\n\n"
         "**Preprint, version 0.9 (2026-10-28).**\n\n")
out = (TITLE + front + "## Abstract\n\n" + frag["abstract"] + "\n---\n\n"
       + intro_head + frag["intro_tail"]
       + body + "\n---\n\n"
       + frag["part3_head"] + "\n" + p3.rstrip("\n") + "\n\n---\n\n"
       + frag["part4_head"] + "\n" + p4.rstrip("\n") + "\n\n---\n\n"
       + frag["limitations"] + "\n---\n\n"
       + observations.rstrip("\n") + "\n\n---\n\n"
       + frag["conclusion"] + "\n---\n\n"
       + back + frag["appendix_ef"])

# demote Part III/IV's '---' separators inside a section are kept; collapse 3+ blank lines
out = re.sub(r"\n{3,}", "\n\n", out)
(P / "draft_v0_9.md").write_text(out, encoding="utf-8")

# ---------------------------------------------------------------- checks
tables = [int(x) for x in re.findall(r"^\*\*Table (\d+)\.", out, flags=re.M)]
assert tables == list(range(1, 44)), tables
sections = re.findall(r"^## (\d+) ", out, flags=re.M)
assert sections == [str(i) for i in range(1, 12)], sections
dangling = sorted(set(re.findall(r"Table (\d+)", out)) - {str(i) for i in range(1, 44)})
assert not dangling, dangling
heads = set(re.findall(r"^#{2,4} (\d+(?:\.\d+)*) ", out, flags=re.M))
refs = set(re.findall(r"§(\d+(?:\.\d+)*)", out))
missing = sorted(r for r in refs if r not in heads)
print("captioned tables 1..%d ok; sections %s; section refs without a heading: %s" % (len(tables), ",".join(sections), missing))
print("wrote", P / "draft_v0_9.md", len(out), "chars")
