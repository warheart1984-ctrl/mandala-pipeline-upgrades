"""Deterministic hashing helpers for NCE artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_dumps(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_hex(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def digest_obj(obj: Any) -> str:
    return sha256_hex(canonical_dumps(obj))


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
