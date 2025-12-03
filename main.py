from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import base64
import time

from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

from totp_utils import generate_totp_code, verify_totp_code

app = FastAPI()

# Paths
PRIVATE_KEY_PATH = "student_private_key.pem"   # adjust if your key file name is different
SEED_FILE_PATH = "/data/seed.txt"             # as required by assignment


# ---------- Helpers ----------

def load_private_key():
    with open(PRIVATE_KEY_PATH, "rb") as f:
        key_data = f.read()
    private_key = load_pem_private_key(key_data, password=None)
    return private_key


def decrypt_seed(encrypted_seed_b64: str) -> str:
    """
    Decrypt base64-encoded seed using RSA/OAEP-SHA256 and return 64-char hex string.
    """
    private_key = load_private_key()

    # Base64 decode
    encrypted_bytes = base64.b64decode(encrypted_seed_b64)

    # RSA OAEP SHA-256 decrypt
    decrypted_bytes = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    hex_seed = decrypted_bytes.decode("ascii").strip()

    # Validate: 64 hex chars
    if len(hex_seed) != 64:
        raise ValueError("Decrypted seed is not 64 characters")
    int(hex_seed, 16)  # will raise if not valid hex

    return hex_seed


def read_seed_from_file() -> str:
    if not os.path.exists(SEED_FILE_PATH):
        raise FileNotFoundError("Seed not decrypted yet")

    with open(SEED_FILE_PATH, "r") as f:
        hex_seed = f.read().strip()

    if not hex_seed or len(hex_seed) != 64:
        raise ValueError("Invalid seed in file")

    return hex_seed


# ---------- Request models ----------

class DecryptSeedRequest(BaseModel):
    encrypted_seed: str


class Verify2FARequest(BaseModel):
    code: str | None = None


# ---------- Endpoint 1: POST /decrypt-seed ----------

@app.post("/decrypt-seed")
def decrypt_seed_endpoint(body: DecryptSeedRequest):
    try:
        hex_seed = decrypt_seed(body.encrypted_seed)

        # Ensure /data exists
        os.makedirs(os.path.dirname(SEED_FILE_PATH), exist_ok=True)

        # Save hex seed to /data/seed.txt
        with open(SEED_FILE_PATH, "w") as f:
            f.write(hex_seed)

        return {"status": "ok"}

    except Exception:
        # You could log the exception here if you want
        return JSONResponse(
            status_code=500,
            content={"error": "Decryption failed"},
        )


# ---------- Endpoint 2: GET /generate-2fa ----------

@app.get("/generate-2fa")
def generate_2fa():
    try:
        hex_seed = read_seed_from_file()
    except FileNotFoundError:
        return JSONResponse(
            status_code=500,
            content={"error": "Seed not decrypted yet"},
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Invalid seed"},
        )

    # Generate TOTP code
    code = generate_totp_code(hex_seed)

    # Remaining seconds in current 30s window
    period = 30
    now = int(time.time())
    elapsed = now % period
    valid_for = period - elapsed  # 1–30

    return {
        "code": code,
        "valid_for": valid_for,
    }


# ---------- Endpoint 3: POST /verify-2fa ----------

@app.post("/verify-2fa")
def verify_2fa(body: Verify2FARequest):
    # Validate code provided
    if not body.code:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing code"},
        )

    # Read seed
    try:
        hex_seed = read_seed_from_file()
    except FileNotFoundError:
        return JSONResponse(
            status_code=500,
            content={"error": "Seed not decrypted yet"},
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Invalid seed"},
        )

    # Verify TOTP (±1 period)
    is_valid = verify_totp_code(hex_seed, body.code, valid_window=1)

    return {
        "valid": bool(is_valid),
    }

