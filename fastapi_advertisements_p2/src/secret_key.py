import secrets
import base64

secret_key = secrets.token_hex(32)
print(secret_key)