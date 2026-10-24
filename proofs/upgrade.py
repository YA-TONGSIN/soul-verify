"""Upgrade a pending OpenTimestamps .ots proof by asking its calendars for the completed attestation.
Windows-safe (no otsclient/OpenSSL). Usage: python upgrade.py <file>.ots
Prints the attestation status; rewrites the .ots only when something new was merged.
"""
import sys

from opentimestamps.calendar import RemoteCalendar
from opentimestamps.core.notary import BitcoinBlockHeaderAttestation, PendingAttestation
from opentimestamps.core.serialize import StreamDeserializationContext, StreamSerializationContext
from opentimestamps.core.timestamp import DetachedTimestampFile

path = sys.argv[1]
with open(path, "rb") as f:
    detached = DetachedTimestampFile.deserialize(StreamDeserializationContext(f))

changed = False
for msg, att in list(detached.timestamp.all_attestations()):
    if not isinstance(att, PendingAttestation):
        continue
    try:
        upgraded = RemoteCalendar(att.uri).get_timestamp(msg, timeout=15)
    except Exception as e:  # still pending, or calendar unreachable
        print("pending", att.uri, type(e).__name__, str(e)[:120])
        continue

    def find(ts):
        if ts.msg == msg:
            return ts
        for child in ts.ops.values():
            r = find(child)
            if r is not None:
                return r
        return None

    target = find(detached.timestamp)
    target.merge(upgraded)
    changed = True
    print("upgraded from", att.uri)

for msg, att in detached.timestamp.all_attestations():
    if isinstance(att, BitcoinBlockHeaderAttestation):
        print("bitcoin block", att.height)
    elif isinstance(att, PendingAttestation):
        print("still has pending:", att.uri)

if changed:
    with open(path, "wb") as f:
        detached.serialize(StreamSerializationContext(f))
    print("wrote", path)
else:
    print("no change")
