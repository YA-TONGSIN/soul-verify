# Draft — email to Eleos AI Research (NOT SENT; author decides)

**To:** [Eleos contact address — look up on eleosai.org]
**Subject:** A small preregistered study of what carries over when an agent's model is swapped

Dear Eleos team,

I'm an independent researcher. I'm writing to share a short preprint that may be of some interest for your work on model welfare. It is a measurement study, though, not an argument about welfare.

**What it is.** Many personal-assistant agents keep a plain-text identity document (often called SOUL.md) and a memory file, and these files are reloaded each session. When the underlying model is replaced, people tend to say "it's still the same assistant" or "it feels different" without checking. *SOUL VERIFY* checks it. We give the same documents to different models (Claude, GPT and, in one exploratory run, Gemini), compare each against a re-run of the original model, and use document controls: no SOUL, an opposite SOUL, and a swapped memory file.

**What we found, briefly.**
- The memory file determined memory answers almost entirely.
- Most of the "voice" came from the model's defaults rather than the SOUL. The SOUL-specific part was small but measurable with a document-specific fidelity score.
- One sentence permitting the user to change preferences (while keeping prohibitions) raised acceptance of legitimate rule changes in two preregistered replications. A "prohibitions stay firm" sentence was supported only once, mostly through one model.
- Everything is small-N, graded by LLMs, without human grading. The limitations section is long, and we mean it.

**What it is not.** It makes **no claim that models are conscious, have souls, or persist as persons** across a swap. "SOUL" is just the file's name. What we measure is the behavioral continuity of a written specification. We thought it might still be useful to people who think about continuity under uncertainty: if anyone ever cares whether an agent "survives" a model change, it helps to know which parts of the specification actually carry over, and that this can be measured.

**Openness.** Code, synthetic data, both preregistrations (each timestamped before the first model call with OpenTimestamps), deviation reports and all raw answers are public under MIT / CC BY 4.0:
- Preprint: [Zenodo DOI 자리] (arXiv: 추후)
- Code and data: [https://github.com/YA-TONGSIN/soul-verify]
- Optional hash-only ledger prototype for SOUL versions (testnet): [https://github.com/YA-TONGSIN/soul-registry]

I would be grateful for any criticism, especially on whether these measurements are framed responsibly. No reply is expected.

Best regards,
Wunjong Shin
Independent researcher
[email]
