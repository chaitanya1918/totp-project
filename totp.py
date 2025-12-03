import base64
import pyotp


def hex_seed_to_base32(hex_seed: str) -> str:
    """
    Convert 64-char hex seed to base32 string for TOTP.
    """
    hex_seed = hex_seed.strip().lower()

    if len(hex_seed) != 64:
        raise ValueError(f"Expected 64-character hex seed, got {len(hex_seed)}")

    # 1. hex -> bytes
    seed_bytes = bytes.fromhex(hex_seed)

    # 2. bytes -> base32
    b32 = base64.b32encode(seed_bytes).decode("utf-8")

    # Most TOTP libs accept padded base32, so we can keep padding.
    # If needed, we could strip "=" padding: .rstrip("=")
    return b32


def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current 6-digit TOTP code (SHA-1, 30s period).
    """
    b32_seed = hex_seed_to_base32(hex_seed)

    # Algorithm: SHA-1 (default), period: 30s, digits: 6
    totp = pyotp.TOTP(b32_seed, digits=6, interval=30)  # sha1 is default

    code = totp.now()  # current 6-digit code
    return code


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify TOTP code with ±valid_window time steps (default 1 = ±30s).
    """
    b32_seed = hex_seed_to_base32(hex_seed)
    totp = pyotp.TOTP(b32_seed, digits=6, interval=30)

    # valid_window = 1 → current, previous, next time step accepted
    return totp.verify(code, valid_window=valid_window)


def main():
    # Read the decrypted hex seed from seed.txt (Step 5)
    with open("seed.txt", "r", encoding="utf-8") as f:
        hex_seed = f.read().strip()

    print("Hex seed from seed.txt:")
    print(hex_seed)

    # Generate current TOTP code
    code = generate_totp_code(hex_seed)
    print("\n✅ Current TOTP code:")
    print(code)

    # Optional: test verification
    is_valid = verify_totp_code(hex_seed, code, valid_window=1)
    print(f"\nVerification of current code: {is_valid}")


if __name__ == "__main__":
    main()
