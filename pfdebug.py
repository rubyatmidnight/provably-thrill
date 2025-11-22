from pfverify import verifyDiceEvent
import binascii
from pfcore import hmacSha512
import hmac, hashlib

server_seed_str = "ndJNeOljzuskm1U8EQousyueTevLOaauQXnqt1MpiytcSAz9qB6nB17Dinc1fFMP"
client_seed = "KhtYMe4JORllqDUJ"
cursor = 1

def super_debug(server_seed_bytes, label):
    print(f"\n==== {label} ====")
    print(f"repr: {repr(server_seed_bytes)}")
    print(f"len: {len(server_seed_bytes)}")
    print(f"bytes: {list(server_seed_bytes)}")
    for nonce in range(1, 6):
        msg_str = f"{client_seed}:{nonce}:{cursor}"
        msg_bytes = msg_str.encode('utf-8')
        hmacval = hmac.new(server_seed_bytes, msg_bytes, hashlib.sha512).digest()
        print(f"\nNonce {nonce}")
        print(f"  Message str: {msg_str}")
        print(f"  Message repr: {repr(msg_bytes)}")
        print(f"  Message len: {len(msg_bytes)}")
        print(f"  Message bytes: {list(msg_bytes)}")
        print(f"  HMAC SHA512 hex: {binascii.hexlify(hmacval).decode()}")
        print(f"  HMAC SHA512 bytes: {list(hmacval)}")
        result = verifyDiceEvent(server_seed_bytes, client_seed, nonce, cursor)
        print(f"  Dice result: {result}")

super_debug(server_seed_str.encode(), "Server seed RAW string")