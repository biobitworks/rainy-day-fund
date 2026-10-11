"""Local runtime configuration with no secret-value telemetry.

Loads a user-owned .env into process environment. Never print values or put them
in an exception. Running this function neither contacts providers nor writes data.
"""
from __future__ import annotations
import os
import re
import stat
from pathlib import Path

_ALLOWED = ("ELEVENLABS_API_KEY", "ELEVENLABS_AGENT_ID",
            "ELEVENLABS_WEBHOOK_SECRET", "MONGODB_URI", "ATLAS_MONGODB_URI",
            "MONGODB_DB", "OLLARMA_BRIDGE_URL")


def load_env(root: Path | None = None) -> dict[str, str]:
    base = root if root is not None else Path(__file__).resolve().parents[2]
    path = base / ".env"
    if not path.exists():
        return {k: ("SET" if os.getenv(k) else "EMPTY") for k in _ALLOWED}
    if os.name == "posix" and (stat.S_IMODE(path.stat().st_mode) & 0o077):
        raise PermissionError("Refusing a shared-readable .env; require chmod 600")
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text or text.startswith("#") or "=" not in text:
            continue
        name, value = text.split("=", 1)
        name = name.removeprefix("export ").strip()
        if name not in _ALLOWED or not re.fullmatch(r"[A-Z][A-Z0-9_]*", name):
            continue
        value = value.strip()
        if value[:1] in ("'", '"') and value[-1:] == value[:1]:
            value = value[1:-1]
        # Existing operator env takes precedence over local file.
        if value:
            os.environ.setdefault(name, value)
    return {k: ("SET" if os.getenv(k) else "EMPTY") for k in _ALLOWED}


def database_uri() -> str | None:
    return os.getenv("ATLAS_MONGODB_URI") or os.getenv("MONGODB_URI")
