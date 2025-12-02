from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def generate_rsa_keypair(key_size: int = 4096):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    public_key = private_key.public_key()
    return private_key, public_key


def save_keys_to_pem(private_key, public_key):
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    with open("student_private.pem", "wb") as f:
        f.write(private_pem)

    with open("student_public.pem", "wb") as f:
        f.write(public_pem)


if __name__ == "__main__":
    private_key, public_key = generate_rsa_keypair()
    save_keys_to_pem(private_key, public_key)
    print("✅ Keys generated: student_private.pem & student_public.pem")
