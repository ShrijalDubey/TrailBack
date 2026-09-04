import bcrypt
import secrets

_KEY_PREFIX_TAG = "tb"


def generate_api_key() -> tuple[str, str, str]:
    secret = secrets.token_urlsafe(32)
    prefix = f"{_KEY_PREFIX_TAG}_{secrets.token_hex(4)}"
    raw_key = f"{prefix}.{secret}"
    key_bytes = raw_key.encode("utf-8")
    salt = bcrypt.gensalt()
    key_hash = bcrypt.hashpw(key_bytes, salt).decode("utf-8")
    return raw_key, prefix, key_hash


def verify_api_key(raw_key: str, key_hash: str) -> bool:
    try:
        return bcrypt.checkpw(raw_key.encode("utf-8"), key_hash.encode("utf-8"))
    except Exception:
        return False


def extract_prefix(raw_key: str) -> str | None:
    if "." not in raw_key:
        return None
    prefix, _, _ = raw_key.partition(".")
    return prefix or None