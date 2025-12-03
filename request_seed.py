import json
import urllib.request

API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

# ✅ CHANGE THESE VALUES ONLY:
STUDENT_ID = "23MH1A4420"
GITHUB_REPO_URL = "https://github.com/chaitanya1918/totp-project"


def request_seed(student_id: str, github_repo_url: str, api_url: str):
    # 1. Read student public key from PEM file
    with open("student_public.pem", "r") as f:
        public_key_pem = f.read()

    # 2. Prepare JSON payload (THIS MUST USE VARIABLES)
    payload = {
        "student_id": "23MH1A4420",
        "github_repo_url":  "https://github.com/chaitanya1918/totp-project",
        "public_key": public_key_pem,
    }

    data = json.dumps(payload).encode("utf-8")

    # 3. Send POST request
    req = urllib.request.Request(
        api_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=10) as resp:
        resp_body = resp.read().decode("utf-8")
        resp_json = json.loads(resp_body)

    # 4. Handle response
    if resp_json.get("status") != "success":
        raise RuntimeError(f"API error: {resp_json}")

    encrypted_seed = resp_json["encrypted_seed"]
    print("Encrypted seed received:")
    print(encrypted_seed)

    # 5. Save to file (DO NOT COMMIT THIS FILE)
    with open("encrypted_seed.txt", "w") as f:
        f.write(encrypted_seed)

    print("Saved encrypted_seed.txt")


if __name__ == "__main__":
    request_seed("23MH1A4420", "https://github.com/chaitanya1918/totp-project", API_URL)


