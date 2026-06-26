import base64
from config import ENCODE_KEY


def _xor(data: bytes) -> bytes:
    key = (ENCODE_KEY * ((len(data) // len(ENCODE_KEY)) + 1)).encode()[:len(data)]
    return bytes(a ^ b for a, b in zip(data, key))


def encode_guest(name_uz: str, name_ru: str) -> str:
    text = f"{name_uz}|{name_ru}"
    return base64.urlsafe_b64encode(_xor(text.encode("utf-8"))).decode().rstrip("=")


def decode_guest(token: str) -> tuple[str, str] | None:
    try:
        padded = token + "=" * ((-len(token)) % 4)
        parts = _xor(base64.urlsafe_b64decode(padded)).decode("utf-8").split("|", 1)
        return parts[0], parts[1]
    except Exception:
        return None
