import os
from typing import Optional


def get_secret(key: str, default: str = "") -> str:
    return os.getenv(key, default)


def require_secret(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise ValueError(f"Required secret {key} not configured")
    return val
