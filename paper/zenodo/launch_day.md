# Launch-day checklist — SOUL VERIFY (prepared 2026-10-26; NOTHING below has been run)

Timeline (user decision 10-26): arXiv submit Tue 10-27 evening KST → expected announcement Wed 10-28 ~09:00 KST. Zenodo publication date in `metadata.md` = 2026-10-28. Each public step is the author's decision; the assistant prepares, the author says go.

Repos: `D:\openclaw-outputs\soul-verify` (YA-TONGSIN/soul-verify), `D:\openclaw-outputs\soul-registry` (YA-TONGSIN/soul-registry). Both PRIVATE until step 5.

## 0. Day before (Tue)
- [ ] Zenodo account exists (GitHub login or email; see report). Log in once; confirm email.
- [ ] `git -C D:\openclaw-outputs\soul-verify status` clean; PDF `paper\zenodo\SOUL_VERIFY_v0.7.1_en.pdf` is the final one.
- [ ] If the DOI should be inside the PDF: Zenodo → New upload → "Reserve DOI" (see `metadata.md`) and note it as `10.5281/zenodo.NNNNNNN` (concept DOI shown after first Publish; the reserved one is the version DOI — see step 3 note).

## 1. Zenodo: upload and publish
- [ ] zenodo.org → Upload → New upload; fill fields in the order of `metadata.md`; attach PDF(s).
- [ ] Click **Preview**, read every field and open the PDF in the preview. Publish is irreversible for the files.
- [ ] **Publish.** Zenodo shows the version DOI and the concept DOI ("Cite all versions").
- [ ] Record both: `VERSION_DOI=10.5281/zenodo.______`, `CONCEPT_DOI=10.5281/zenodo.______`.

## 2. Insert the DOI (new commit + OpenTimestamps stamp)
Use the **concept DOI** for citations. Edit these three places:
- `README.md` — replace the line "arXiv 번호는 제출 후 추가합니다" area with: `DOI: https://doi.org/<CONCEPT_DOI>` (plus arXiv ID if announced).
- `CITATION.cff` — under `preferred-citation:` add `doi: "<CONCEPT_DOI>"`, change `notes:` to mention Zenodo/arXiv, bump `version: "0.7.1"` and `date-released: "2026-10-28"`; also top-level `identifiers:` can hold the DOI:
  ```yaml
  identifiers:
    - type: doi
      value: "10.5281/zenodo.NNNNNNN"
  ```
- Paper first page: a comment line in `paper/draft_v0_7_1.md` header (e.g., `<!-- DOI: 10.5281/zenodo.NNNNNNN -->`) and, only if the author wants the DOI printed, in the PDF header. Printing it needs a PDF rebuild → that PDF can no longer be the one already published on Zenodo; then publish a **new version** on Zenodo (and re-check). Simplest: keep the Zenodo PDF as is, comment only.
Commands:
```powershell
cd D:\openclaw-outputs\soul-verify
git add README.md CITATION.cff paper\draft_v0_7_1.md
git commit -m "add Zenodo DOI (concept 10.5281/zenodo.NNNNNNN)"
python proofs\manifest.py HEAD          # prints the new proofs\<date>_<sha>.txt
python proofs\stamp.py proofs\<date>_<sha>.txt
git add proofs; git commit -m "proofs: manifest + OpenTimestamps stamp for DOI commit"
git push
```
Same `CITATION.cff` + README edit in `D:\openclaw-outputs\soul-registry` (commit, push; it has no proofs\ script).

## 3. Make both repos public
Pre-checks first (once public, history is public):
```powershell
cd D:\openclaw-outputs\soul-verify;   git status --short; git log --oneline | Select -First 3
cd D:\openclaw-outputs\soul-registry; git status --short
```
- [ ] No real SOUL/MEMORY content, keys, `.env`, tokens in either repo (grep: `git grep -nIE "PRIVATE_KEY|password|secret"`). `soul-chain-ieum` is separate and stays private.
- [ ] Untracked review logs (`paper/reviews/_bundle_v0.6.md`, `_gpt_stdout_v0.6.log`) are NOT committed — keep untracked.
Then:
```powershell
gh repo edit YA-TONGSIN/soul-verify   --visibility public --accept-visibility-change-consequences
gh repo edit YA-TONGSIN/soul-registry --visibility public --accept-visibility-change-consequences
gh repo view YA-TONGSIN/soul-verify --json visibility,url
gh repo view YA-TONGSIN/soul-registry --json visibility,url
```
- [ ] Open both URLs logged out (private window) — Zenodo "Related works" links and the paper's availability statement must work.
- [ ] Optional: GitHub release `v0.7.1` (`gh release create v0.7.1 --title "v0.7.1" --notes "Paper v0.7.1; DOI 10.5281/zenodo.NNNNNNN"`), then stamp that commit.

## 4. ieum-ledger: remove noindex and redeploy
Files in `D:\openclaw-outputs\ieum-ledger-build`: `index.html` and `donate.html` have `<meta name="robots" content="noindex, nofollow">`; `_headers` has `X-Robots-Tag: noindex, nofollow`; `robots.txt` has `Disallow: /`.
```powershell
cd D:\openclaw-outputs\ieum-ledger-build
# 1) delete the meta line in index.html and donate.html
# 2) _headers: remove the X-Robots-Tag line (keep other headers)
# 3) robots.txt -> "User-agent: *`nAllow: /"
Select-String -Path *.html,_headers,robots.txt -Pattern "noindex|Disallow"   # expect no output
npx wrangler pages deploy . --project-name ieum-ledger        # confirm project name/flags with the previous deploy; same method as before
```
- [ ] Verify: `curl.exe -sI https://ieum-ledger.pages.dev/ | findstr /i x-robots` → empty; open the page once; the donation address/contract unchanged.
(Deploy command is the standard Cloudflare Pages one; if the earlier deploys used different flags (e.g. `--branch main`), reuse those.)

## 5. soul-chain-ieum: public bundle of fingerprints/proofs only
Real SOUL.md content stays private. Publish only hashes and proofs:
```powershell
$src="D:\openclaw-outputs\soul-chain-ieum"; $dst="D:\openclaw-outputs\soul-registry\docs\ieum-chain-proofs"
New-Item -ItemType Directory -Force $dst | Out-Null
Copy-Item "$src\proofs\*.txt","$src\proofs\*.ots" $dst
Get-Content $dst\*.txt | Select-String "soul_sha256|commit|reason"   # inspect: the 'reason' lines must not leak private content
```
- [ ] Read every `.txt` before committing (reasons may mention private matters). Remove or redact any that do; the `.ots` hashes still match only the original file, so excluded files simply stay unverifiable.
- [ ] Add a short `README.md` in that folder: what a fingerprint is, how to check (opentimestamps.org with txt + ots).
- [ ] `cd D:\openclaw-outputs\soul-registry; git add docs\ieum-chain-proofs; git commit -m "publish ieum SOUL chain fingerprints and OpenTimestamps proofs"; git push`
- [ ] If the `.ots` are still "pending": `python D:\openclaw-outputs\soul-verify\proofs\upgrade.py <file>.ots` first (after block confirmation), then copy.

## 6. GitHub–Zenodo integration (optional, only for future releases)
- [ ] zenodo.org → Account → GitHub → flip the switch for `YA-TONGSIN/soul-verify` (needs the repo to be public and GitHub login linked).
- [ ] Effect: each GitHub *release* creates a new Zenodo version automatically. Do NOT create a release before deciding this, or an unintended record appears. It would not edit the manually published v0.7.1 record.
- [ ] Skip if the manual record is enough.

## 7. Fill in links in the outreach drafts (`paper\outreach\`)
Drafts currently say "Zenodo DOI 자리" and "arXiv: 추후". Replace:
- `Zenodo DOI 자리` → `https://doi.org/<CONCEPT_DOI>`
- `arXiv: 추후` → `https://arxiv.org/abs/<ID>` once announced (else keep "coming").
- GitHub link placeholders → the two repo URLs.
Posting each (LessWrong, r/ArtificialSentience, Eleos email, Korean SNS) = author's separate decision.

## 8. After arXiv announcement
- [ ] Add arXiv ID to README, CITATION.cff, `arxiv/metadata.md`; Zenodo record → Edit → Related works: add "Is identical to" arXiv:ID (metadata edits are allowed after publish, files are not).
- [ ] Tag a release if wanted, then stamp the commit (`proofs\manifest.py` + `stamp.py`).
- [ ] Append the day's events to `soul-chain-project.md` memory.
