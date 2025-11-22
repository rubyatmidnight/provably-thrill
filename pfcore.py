import hmac
import hashlib
from typing import Optional

# Secure random byte gen

def hmacSha512(serverSeed: bytes, message: bytes) -> bytes:
    return hmac.new(serverSeed, message, hashlib.sha512).digest()

def generateRandomBytes(serverSeed: bytes, clientSeed: str, nonce: int, cursor: int, size: int=64) -> bytes:
    msg = f"{clientSeed}:{nonce}:{cursor}".encode()
    raw = hmacSha512(serverSeed, msg)
    # If you want more than 64 bytes, you need to chain (not in the scope of instant games)
    return raw[:size]

# Floating-point double in [0,1)
def generateDouble(randomBytes: bytes) -> float:
    assert len(randomBytes) >= 7, "Need at least 7 bytes"
    bits = int.from_bytes(randomBytes[:7], 'big')
    mantissa = bits & ((1 << 52) - 1)  # Lower 52 bits
    return mantissa / float(1 << 52)

# Uniform int with rejection sampling
def nextPositiveInt32(randomBytes: bytes, maxExclusive: Optional[int]=None) -> int:
    """randomBytes must be at least 4 bytes, prefer 64 (HMAC output)"""
    maxExclusive = maxExclusive if maxExclusive and maxExclusive>0 else 2**32
    limit = (2**32) - (2**32 % maxExclusive)
    # Try every 4-byte block in the randomBytes sequence
    for i in range(0, len(randomBytes)-3, 4):
        val = int.from_bytes(randomBytes[i:i+4], 'big')
        if val < limit:
            return val % maxExclusive
    # If all blocks fail, re-run with new cursor
    raise ValueError("Rejection sampling failed; try next cursor value")

if __name__ == "__main__":
    # Demo with full debug output for each nonce
    import sys
    import binascii
    serverSeed = "ndJNeOljzuskm1U8EQousyueTevLOaauQXnqt1MpiytcSAz9qB6nB17Dinc1fFMP"
    clientSeed = "KhtYMe4JORllqDUJ"

    print("PF Demo - Full Debug Output:\n")
    for nonce in range(11):
        cursor = 0
        raw_bytes = generateRandomBytes(serverSeed.encode(), clientSeed, nonce, cursor, 64)
        digest_hex = binascii.hexlify(raw_bytes).decode()
        double_bytes = raw_bytes[:7]
        double_bytes_hex = binascii.hexlify(double_bytes).decode()
        bits = int.from_bytes(double_bytes, 'big')
        mantissa = bits & ((1 << 52) - 1)
        uniform = mantissa / float(1 << 52)
        scaled = uniform * 100
        print(f"Nonce={nonce}")
        print(f"  HMAC Digest (hex):    {digest_hex}")
        print(f"  Double Bytes (hex):   {double_bytes_hex}")
        print(f"  Bits:                 {bits}")
        print(f"  Mantissa (52 bits):   {mantissa}")
        print(f"  Uniform [0,1):        {uniform}")
        print(f"  Scaled [0,100):       {scaled:.8f}")
        print()