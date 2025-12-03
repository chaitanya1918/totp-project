from totp_utils import generate_totp_code, verify_totp_code

example_hex_seed = "0" * 64  # Replace later with real decrypted seed

code = generate_totp_code(example_hex_seed)
print("Generated TOTP:", code)

is_valid = verify_totp_code(example_hex_seed, code)
print("Code Valid:", is_valid)
print('test script working')
