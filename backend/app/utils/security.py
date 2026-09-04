import secrets

from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_KEY_PREFIX_TAG = "tb"

def generate_api_key() -> tuple[str, str, str]:
    secret = secrets.token_urlsafe(32)
    prefix = f"{_KEY_PREFIX_TAG}_{secrets.token_hex(4)}"
    raw_key = f"{prefix}.{secret}"
    key_hash = _pwd_context.hash(raw_key)
    return raw_key, prefix, key_hash


def verify_api_key(raw_key: str, key_hash: str) -> bool:
    return _pwd_context.verify(raw_key, key_hash)


def extract_prefix(raw_key: str) -> str | None:
    if "." not in raw_key:
        return None
    prefix, _, _ = raw_key.partition(".")
    return prefix or None