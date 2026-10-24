"""Create an OpenTimestamps .ots proof for a file (Windows-safe: avoids otsclient's bitcoin/OpenSSL import).

Usage: python stamp.py <file>      -> writes <file>.ots
Later: `ots upgrade <file>.ots` / `ots verify` on any machine with a working client, or opentimestamps.org.
"""
import hashlib
import sys

from opentimestamps.calendar import RemoteCalendar
from opentimestamps.core.op import OpSHA256
from opentimestamps.core.serialize import StreamSerializationContext
from opentimestamps.core.timestamp import DetachedTimestampFile, Timestamp

CALENDARS = [
    "https://alice.btc.calendar.opentimestamps.org",
    "https://bob.btc.calendar.opentimestamps.org",
    "https://finney.calendar.eternitywall.com",
]

path = sys.argv[1]
with open(path, "rb") as f:
    digest = hashlib.sha256(f.read()).digest()

detached = DetachedTimestampFile(OpSHA256(), Timestamp(digest))
ok = 0
for url in CALENDARS:
    try:
        detached.timestamp.merge(RemoteCalendar(url).submit(digest, timeout=15))
        ok += 1
        print("ok  ", url)
    except Exception as e:  # one calendar down is fine
        print("fail", url, type(e).__name__, e)

if ok == 0:
    sys.exit("no calendar accepted the digest")

with open(path + ".ots", "wb") as f:
    detached.serialize(StreamSerializationContext(f))
print("sha256", digest.hex())
print("wrote", path + ".ots", f"({ok} calendars)")
