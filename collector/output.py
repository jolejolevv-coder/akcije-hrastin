"""Write JSON files so that a failed run never leaves a half written file behind."""

import json
import os
from pathlib import Path

MAX_DEALS_FILE_BYTES = 2 * 1024 * 1024
# The catalogue of all regular prices. The website loads it only when the reader searches.
MAX_PRICES_FILE_BYTES = 12 * 1024 * 1024
TEMP_SUFFIX = ".tmp"


class OutputError(Exception):
    """The output could not be written or breaks the size limit."""


def write_json(path: Path, document: dict, max_bytes: int | None = None) -> int:
    """Write the document atomically and return its size in bytes."""
    payload = json.dumps(document, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if max_bytes is not None and len(payload) > max_bytes:
        raise OutputError(f"{path.name} would be {len(payload)} bytes, limit is {max_bytes}")
    temp_path = path.with_name(path.name + TEMP_SUFFIX)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path.write_bytes(payload)
        os.replace(temp_path, path)
    except OSError as error:
        raise OutputError(f"Cannot write {path}: {error!r}") from error
    return len(payload)
