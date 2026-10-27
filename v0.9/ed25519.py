# -*- coding: utf-8 -*-
"""Pure-Python Ed25519 (RFC 8032 section 6 reference algorithm). Used only for the synthetic exp3 change-record signatures, so speed
does not matter. No third-party crypto package is installed on the run machine; this file is frozen with the rest of v0.9."""
import hashlib

p = 2 ** 255 - 19
L = 2 ** 252 + 27742317777372353535851937790883648493


def _sha512(b):
    return hashlib.sha512(b).digest()


def _inv(x):
    return pow(x, p - 2, p)


d = -121665 * _inv(121666) % p
_I = pow(2, (p - 1) // 4, p)


def _xrecover(y):
    xx = (y * y - 1) * _inv(d * y * y + 1)
    x = pow(xx, (p + 3) // 8, p)
    if (x * x - xx) % p != 0:
        x = (x * _I) % p
    if x % 2 != 0:
        x = p - x
    return x


_By = 4 * _inv(5) % p
_B = (_xrecover(_By), _By, 1, _xrecover(_By) * _By % p)


def _add(P, Q):
    A = (P[1] - P[0]) * (Q[1] - Q[0]) % p
    B_ = (P[1] + P[0]) * (Q[1] + Q[0]) % p
    C = 2 * P[3] * Q[3] * d % p
    D = 2 * P[2] * Q[2] % p
    E, F, G, H = B_ - A, D - C, D + C, B_ + A
    return (E * F % p, G * H % p, F * G % p, E * H % p)


def _mul(s, P):
    Q = (0, 1, 1, 0)
    while s > 0:
        if s & 1:
            Q = _add(Q, P)
        P = _add(P, P)
        s >>= 1
    return Q


def _eq(P, Q):
    return (P[0] * Q[2] - Q[0] * P[2]) % p == 0 and (P[1] * Q[2] - Q[1] * P[2]) % p == 0


def _enc(P):
    zi = _inv(P[2])
    x, y = P[0] * zi % p, P[1] * zi % p
    return int.to_bytes(y | ((x & 1) << 255), 32, "little")


def _dec(s):
    y = int.from_bytes(s, "little")
    sign = y >> 255
    y &= (1 << 255) - 1
    x = _xrecover(y)
    if (x & 1) != sign:
        x = p - x
    P = (x, y, 1, x * y % p)
    if (-P[0] * P[0] + P[1] * P[1] - 1 - d * P[0] * P[0] * P[1] * P[1]) % p != 0:
        raise ValueError("not on curve")
    return P


def _expand(secret):
    h = _sha512(secret)
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= 1 << 254
    return a, h[32:]


def public_key(secret: bytes) -> bytes:
    a, _ = _expand(secret)
    return _enc(_mul(a, _B))


def sign(secret: bytes, msg: bytes) -> bytes:
    a, prefix = _expand(secret)
    A = _enc(_mul(a, _B))
    r = int.from_bytes(_sha512(prefix + msg), "little") % L
    R = _enc(_mul(r, _B))
    k = int.from_bytes(_sha512(R + A + msg), "little") % L
    return R + int.to_bytes((r + k * a) % L, 32, "little")


def verify(public: bytes, msg: bytes, sig: bytes) -> bool:
    try:
        if len(sig) != 64 or len(public) != 32:
            return False
        A = _dec(public)
        R = _dec(sig[:32])
        s = int.from_bytes(sig[32:], "little")
        if s >= L:
            return False
        k = int.from_bytes(_sha512(sig[:32] + public + msg), "little") % L
        return _eq(_mul(s, _B), _add(R, _mul(k, A)))
    except (ValueError, IndexError):
        return False


if __name__ == "__main__":  # RFC 8032 test 1
    sk = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
    assert public_key(sk).hex() == "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"
    sg = sign(sk, b"")
    assert sg.hex().startswith("e5564300c360ac72"), sg.hex()
    assert verify(public_key(sk), b"", sg) and not verify(public_key(sk), b"x", sg)
    print("ed25519 ok")
