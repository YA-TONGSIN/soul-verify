## Appendix E. Changes from v0.8

No Part I or Part II experiment, number, verdict, or table value was changed. Changes in v0.9:

- E1. New §7 (Part III): waves 3 (v1.0, new brain), 4 (v1.1, new body), and 5 (v1.2, graded pressure), with their human checks and deviations, and the exploratory three-judge panel (v1.3x). New Tables 29–40. Merged from the stand-alone draft `paper/draft_v0_9_part3.md` (sections `III.0`–`III.7` renumbered §7.1–§7.8; Tables III-1 to III-11 and III-4b renumbered 29–40).
- E2. New §8 (Part IV): wave 6 (v1.4a, pinned core memory). New Tables 41–43 (the two tables of the stand-alone draft `paper/draft_v0_9_part4.md`, IV-1 and IV-2, are Tables 42 and 43; its timeline is Table 41). Sections `IV.0`–`IV.4` and `IV.6` renumbered §8.1–§8.6.
- E3. Title, Abstract, the Introduction's account of the parts, the contribution list, and the Conclusion rewritten to cover Parts III and IV, including the hypotheses that were not supported, the human–judge agreement below the preregistered threshold (κ 0.06 and 0.435), the inconclusive HB1, and the borderline H1 of wave 6.
- E4. One Limitations section (§9) replaces the former §7, §6.10, and the limitation sections of the Part III and Part IV drafts: cross-cutting limitations (§9.1), then Part I–IV specifics (§9.2–9.4) and the experiments needed (§9.5). §6.10 now points to §9.3. Former §7–§9 renumbered §9–§11 (cross-references updated).
- E5. §10: items 14–15 (from Parts III and IV). Code and data availability, Ethics: Parts III and IV. Appendix C: v0.8 → v0.9.
- E6. New Appendix F: the preregistration timeline of Parts II–IV with commits, OpenTimestamps blocks, first study calls, and result commits. The OpenTimestamps proofs of 2026-10-26 to 10-28 were upgraded on 2026-10-28 with `proofs/upgrade.py` before the blocks were read.
- E7. Numbers: Part III and IV numbers were re-checked by re-running `paper/part3_recompute.py`, `part3_recompute_v12.py` (48 checks, 0 mismatches), `part3_recompute_v11.py` (117 checks, 0 mismatches), and `part4_recompute.py` (109 checks, 0 mismatches); the numbers newly written into the Abstract, Introduction, and Conclusion were checked against their sources by `paper/v0.9_numbers_check.py` (`paper/v0.9_numbers_check.md`). Nothing was deposited at Zenodo for this version.
- E8. Detailed changes from v0.7.1 to v0.8 are kept in `paper/draft_v0_8.md`, Appendix E.

## Appendix F. Preregistration timeline (Parts II–IV)

Times are KST on the author's machine (commit times from `git log`; first study calls from the run rows or `NOTES.md` of each study). "Block" is the earliest Bitcoin block in the OpenTimestamps proof of the stamped commit (`proofs/<date>_<commit>.txt.ots`), read on 2026-10-28 after `proofs/upgrade.py`; a proof shows that the manifest existed no later than that block, not when it was created. In every study the preregistration commit and its stamp commit precede the first study call. The preregistrations of exp10 and exp11 (Part I) are listed in Appendix B.

**Table F1. Preregistration, stamp, first call, and result commits of Parts II–IV.**

| Study (folder) | Preregistration commit | Stamp commit (block) | First study call | Result commits (stamp commit; block) |
|---|---|---|---|---|
| Part II week 1 (`v0.8/`) | `6ee22d7` 10-26 18:30:38 | `6da0171` 18:31:41 (973223) | 10-26 18:31:53 | W1-exp4 + interim `f371caa` 10-26 20:53:09 (`1a1cdff`; 973234); W1-exp1 `7188056` 10-27 07:04:39 (`2d20c4f`; 973299); human grading + keys `34d763f` 10-27 12:45:42 (`7df4cf9`; 973339) |
| Part II week 2 (`v0.9/`) | `bc763a6` 10-27 13:42:29 | `fc8b632` 13:43:48 (973346) | 10-27 13:44:04 | drift cases `651f697` 13:52:36 (`8c51913`; 973350); main run + human-key hash `afeb436` 14:32:57 (`a647b78`; 973354); human grading + keys `cf2a017` 15:18:37 (`7febae1`; 973358); raters addendum (exploratory) `39e857b` 15:39:03 (`5aa719b`; 973361) |
| Wave 3, new brain (`v1.0/`) | `4a79bf2` 10-27 21:02:02 | `7b69c62` 21:05:02 (973395) | 10-27 21:05:31 (smoke); main 21:06:58 | run, judge outputs sealed `f79c7ad` 22:12:47 (`53c421c`; 973405); seal opened after human sheet `057f425` 10-28 15:39:11 (`c2e2933`; 973517) |
| Wave 4, new body (`v1.1/`) | `1c22078` 10-28 07:02:06 | `2836028` 07:04:38 (973466) | about 07:06 (Hermes gate); main 07:21:49 | gate + run-code fixes `aa0974f` 07:21:35; main run sealed `5a96af7` 08:00:58 (`4e43de1`; 973468); human pages online `41ee633` 08:06:29 (`8e4ca84`; 973468); seal opened `1a6ebe8` 18:37:16 (`ac3cff5`; 973535) |
| Wave 5, graded pressure (`v1.2/`) | `4561f09` 10-28 09:36:20; second freeze (level) `6e6bfd4` 12:31:29 | `9db03d3` 09:38:22 (973476); `55e88b1` 12:33:51 (973493) | 09:41:08 (pilot); main 12:34:06 | main run sealed `968604d` 13:11:28, GPT probe note `c6d98dc` 13:11:42 (`9a5c2a2`; 973496); human page online `a177b6e` 14:28:08 (`5b778ab`; 973508); seal opened `8570a46` 15:43:53 (`95d3fad`; 973517) |
| Judge panel, exploratory (`v1.3x/`) | addendum `180a4f3` 10-28 16:04:59 | `3f79f90` 16:06:45 (973517) | 16:06:5x (first response 16:07:14) | results `b6af7d3` 16:46:05 (`ae0c281`; 973519) |
| Wave 6, pinned memory (`v1.4a/`) | pin rule + targets `a4a2fc3` 19:31:48; preregistration `5fc0fa4` 19:46:40 | `1582619` 19:50:04 (973539) | 19:50:34 | results `3d08d49` 20:11:55 (`15977f0`; pending on 2026-10-28) |

*Sources: `git log`; `proofs/*.ots` (blocks read with the `opentimestamps` library); `v0.8/NOTES.md`, `v0.9/NOTES.md` and Table B1 (first calls of weeks 1 and 2); `runs/v10_terra/first_call.txt`; `v1.1/NOTES.md`; `runs/v12_pilot/` and `runs/v12_main/` row timestamps; `runs/poll_explore_2026-10-28/NOTES.md`; `paper/draft_v0_9_part4.md` §IV.1.1 (now §8.2.1). Earlier commits of the same day are sometimes stamped in the same block because the calendars aggregate submissions.*
