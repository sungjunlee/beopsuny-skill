#!/usr/bin/env python3
"""YAML and text-source loading for knowledge manifest ingest."""

from __future__ import annotations

import importlib.util
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


def _load_sibling(module_name: str):
    path = Path(__file__).resolve().parent / f"{module_name}.py"
    existing = sys.modules.get(module_name)
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load sibling {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_validate = _load_sibling("knowledge_manifest_validate")
IngestError = _validate.IngestError

RAW_MAIN_MARKER = "/sungjunlee/beopsuny-knowledge/main/"
# The stable/canary sources in knowledge_manifest.yaml use this HTTPS origin.
AUTHENTICATED_ORIGIN = ("https", "raw.githubusercontent.com", 443)


def _allows_credentials(source: str) -> bool:
    try:
        url = urllib.parse.urlsplit(source)
        port = url.port if url.port is not None else 443
        return (
            url.username is None
            and url.password is None
            and (url.scheme, url.hostname, port) == AUTHENTICATED_ORIGIN
        )
    except ValueError:
        # Malformed authorities must never gain credentials.
        return False


def load_yaml(path: Path) -> Any:
    try:
        import yaml  # type: ignore[import-not-found]
    except Exception as exc:  # noqa: BLE001 - helper should explain missing optional parser.
        raise IngestError(
            "PyYAML is required to read knowledge manifest policy"
        ) from exc
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def read_text_source(source: str, knowledge_root: Path | None = None) -> str:
    if (
        knowledge_root
        and source.startswith("https://raw.githubusercontent.com/")
        and RAW_MAIN_MARKER in source
    ):
        relative = source.split(RAW_MAIN_MARKER, 1)[1]
        return (knowledge_root / relative).read_text(encoding="utf-8")
    if source.startswith("file://"):
        return Path(source.removeprefix("file://")).read_text(encoding="utf-8")
    if re.match(r"https?://", source):
        headers = {"User-Agent": "beopsuny-knowledge-ingest"}
        request = urllib.request.Request(source, headers=headers)
        if _allows_credentials(source):
            token = os.environ.get("BEOPSUNY_KNOWLEDGE_TOKEN") or os.environ.get(
                "GITHUB_TOKEN"
            )
            if token:
                # Even same-origin redirects are anonymous: no later hop may
                # inherit or restore the initial request's credentials.
                request.add_unredirected_header("Authorization", f"Bearer {token}")
        try:
            with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310 - configured manifest URL.
                status = getattr(response, "status", 200)
                if status != 200:
                    raise IngestError(f"HTTP {status} for {source}")
                return response.read().decode("utf-8")
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            raise IngestError(f"failed to fetch {source}: {exc}") from exc
    return Path(source).read_text(encoding="utf-8")
