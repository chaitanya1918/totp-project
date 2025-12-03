#!/usr/bin/env python3
import os
import pyotp
from base64 import b32encode
from datetime import datetime, timezone

SEED_FILE = "/data/seed.txt"

def load_seed():
    """Read stored hex seed from /data/seed.txt"""
    if not os.path.exists(SEED_FILE):
        return None
    with open(SEED_FILE, "r") as f:
        return f.read().strip()

def hex_to_base32(hex_seed: str) -> str:
    """Convert hex seed to Base32 for TOTP"""
    raw_bytes = bytes.fromhex(hex_seed)
    return b32encode(raw_bytes).decode("utf-8")

def generate_totp(hex_seed: str):
    """Generate TOTP from hex seed"""
    try:
        base32_seed = hex_to_base32(hex_seed)
        totp = pyotp.TOTP(base32_seed)
        return totp.now()
    except Exception as e:
        return f"ERROR: {e}"

def main():
    seed = load_seed()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    if seed is None:
        output = f"{timestamp} - ERROR: seed.txt not found"
    else:
        code = generate_totp(seed)
        output = f"{timestamp} - 2FA Code: {code}"

    print(output)

if __name__ == "__main__":
    main()
