"""Write proofs/<date>_<commit7>.txt: commit, tree, sha256 of every committed blob (LF, byte-exact).
Usage: python proofs/manifest.py <commit>   then   python proofs/stamp.py proofs/<file>.txt
"""
import datetime
import hashlib
import subprocess
import sys


def git(*args):
    return subprocess.check_output(["git", *args])


commit = git("rev-parse", sys.argv[1]).decode().strip()
tree = git("rev-parse", commit + "^{tree}").decode().strip()
files = [f for f in git("ls-tree", "-r", "--name-only", commit).decode("utf-8").split("\n") if f]
rows = [f"{hashlib.sha256(git('cat-file', 'blob', f'{commit}:{f}')).hexdigest()}  {f}" for f in files]
now = datetime.datetime.now().astimezone()
lines = ["SOUL VERIFY timestamp manifest", "repo: https://github.com/YA-TONGSIN/soul-verify",
         f"commit: {commit}", f"tree: {tree}", f"created: {now.isoformat()}", "", "sha256  path", *rows]
out = f"proofs/{now:%Y-%m-%d}_{commit[:7]}.txt"
with open(out, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines) + "\n")
print(out, len(rows), "files")
