# -*- coding: utf-8 -*-
"""Private: makes v1.0/private_keys/blind_key_t.json (secret salt that fixes the answer order inside every grading/judge unit) and
writes its SHA-256 into v1.0/KEY_HASHES.txt. Run once before the freeze. The key is published after human grading."""
import hashlib
import json
import pathlib
import secrets

V10 = pathlib.Path(__file__).resolve().parents[1]
p = V10 / "private_keys" / "blind_key_t.json"
if not p.exists():
    p.write_text(json.dumps({"salt": secrets.token_hex(32), "purpose": "grading/judge answer order (common_t.unit_seed)"}) + "\n",
                 encoding="utf-8", newline="\n")
lines = ["# SHA-256 of the private v1.0 keys (LF, UTF-8). Published after human grading; committing the hash binds them.",
         f"blind_key_t.json  {hashlib.sha256(p.read_bytes()).hexdigest()}",
         "HUMAN_KEY_T.json  (made after the run, from the scored rows; its hash is committed and stamped before the sheet goes online)"]
(V10 / "KEY_HASHES.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
print("\n".join(lines))
