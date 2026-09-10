"""Model artifact versioning helpers (ties to MODEL_ARTIFACT_PATH)."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path


def make_version_tag(prefix: str = "model") -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    git = os.environ.get("GIT_COMMIT", "nogit")[:8]
    return f"{prefix}-{ts}-{git}"


def artifact_root() -> Path:
    env = os.environ.get("MODEL_ARTIFACT_PATH")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[1] / "artifacts"


def resolve_artifact_path(directory: Path, model_name: str, version: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    safe_version = version.replace("/", "_")
    return directory / f"{model_name}_{safe_version}.joblib"
