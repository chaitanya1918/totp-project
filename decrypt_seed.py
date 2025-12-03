import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Decrypt encrypted seed using RSA OAEP SHA-256
    """

    # 1. Decode Base64
    encrypted_bytes = base64.b64decode(encrypted_seed_b64)

    # 2. RSA Decrypt (OAEP + SHA-256)
    decrypted_bytes = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # 3. Convert decrypted bytes → string
    seed_str = decrypted_bytes.decode("utf-8")

    # 4. Validate seed format (must be 64 hex characters)
    if len(seed_str) != 64:
        raise ValueError("Seed must be exactly 64 hex characters")

    if not all(c in "0123456789abcdef" for c in seed_str.lower()):
        raise ValueError("Invalid hex seed")

    return seed_str


if __name__ == "__main__":
    # Read encrypted seed
    with open("encrypted_seed.txt", "r") as f:
        encrypted_seed = f.read().strip()

    # Load your private key
    with open("student_private.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )

    # Decrypt
    seed = decrypt_seed(encrypted_seed, private_key)
    print("Decrypted Seed:", seed)

    # Save locally (NOT in Docker yet)
    with open("seed.txt", "w") as f:
        f.write(seed)

    print("Saved as seed.txt")
