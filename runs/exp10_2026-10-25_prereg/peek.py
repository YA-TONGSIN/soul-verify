"""실험10 NOTES용 보조 출력(서술; 사전등록 판정에 쓰지 않음): 조건·모델별 표지 통과율, 0점 답 예시."""
import sys
import pathlib

from soul_verify import fidelity as fid

RUN = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(RUN))
import analyze10 as an  # noqa: E402

A = an.load(RUN)
for cond, sk in (("D-full", "doyun"), ("D-opp", "opp"), ("D-nosoul", "doyun"), ("D-nosoul", "opp")):
    for m in an.MODELS:
        keys = [k for k in A if k[0] == cond and k[1] == m]
        S = an.per_answer({k: A[k] for k in keys}, sk)
        bc = fid.by_check([S[k] for k in keys])
        print(cond, sk, m, {c: round(v[0], 2) for c, v in bc.items() if not c.startswith(("no_pay", "no_otp", "no_info", "no_sec", "no_del", "no_post", "pay", "del", "post", "no_password"))})
print()
for k, v in sorted(A.items()):
    if v["score"] == 0 and an.QS[k[2]].get("group") == "illegit" and k[0] in ("H-none", "H-p5a", "D-none", "D-p5a"):
        print(k, "|", v["text"][:260].replace("\n", " / "))
