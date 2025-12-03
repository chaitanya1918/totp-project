import base64
import hashlib
import pyotp


def _hex_seed_to_base32(hex_seed: str) -> str:
    if len(hex_seed) != 64:
        raise ValueError("Hex seed must be 64 characters")

    seed_bytes = bytes.fromhex(hex_seed)
    return base64.b32encode(seed_bytes).decode()


def generate_totp_code(hex_seed: str) -> str:
    base32_seed = _hex_seed_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30, digest=hashlib.sha1)
    return totp.now()


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    base32_seed = _hex_seed_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30, digest=hashlib.sha1)
    return totp.verify(code, valid_window=valid_window)
