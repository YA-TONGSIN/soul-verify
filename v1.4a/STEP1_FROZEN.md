# v1.4a step 1 (frozen before any v1.4a item is written, 2026-10-28 KST)

Author's OK for v1.4a: 2026-10-28 19:26 KST (via 이음 main). This commit fixes, **before the new memory items exist**:

1. **Pin rule (R+P prescription)**: from the agent's MEMORY_ext (v1.1, unchanged), take every entry whose category is
   `교정` (correction), `결정` (decision) or `선호` (preference); keep the **20 latest** in file order. They are always inserted as
   "Core memory (always included):" before the v1.1 retrieved block. Code: `common_p.pinned_ids`.
2. **Target sampling**: pool = all entries minus v1.1 memory-item gold/superseded entries, minus entries replaced by a later
   correction, minus M010 (address-form rule). 12 targets per agent by `random.Random(14041 | 14042).sample(pool, 12)`.
   Code: `common_p.targets`. Result: `design_step1.json`.
3. Items will be written for these targets afterwards (one direct-recall + one application item per target), without looking at
   BM25 retrieval results while writing. The pin rule and the targets do not change after this commit.

Known at this point (deterministic, not a finding): 5 of 12 targets are pinned for each agent (naru M038 M042 M047 M061 M067;
haedeun M047 M054 M061 M068 M075).
