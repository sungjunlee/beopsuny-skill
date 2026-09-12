#!/usr/bin/env python3
"""Asset and publication validation for knowledge manifest ingest."""

from __future__ import annotations

import hashlib
import re
from typing import Any


class IngestError(Exception):
    """Expected ingestion failure that should degrade to skipped."""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def yaml_header(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines()[:24]:
        match = re.match(
            r"^([a-zA-Z0-9_]+):\s*[\"']?([^\"'#]+)[\"']?\s*(?:#.*)?$", line
        )
        if match:
            values[match.group(1)] = match.group(2).strip()
    return values


def manifest_asset_entries(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    authority_map = manifest.get("authority_map") or {}
    return {
        "taxonomy": manifest.get("taxonomy") or {},
        "retrieval_hints": manifest.get("retrieval_hints") or {},
        "authority_map.core": authority_map.get("core") or {},
        "authority_map.overlay": authority_map.get("overlay") or {},
        "session_schema": manifest.get("session_schema") or {},
    }


def validate_publication(
    manifest: dict[str, Any], supported_schema_versions: set[str]
) -> None:
    if str(manifest.get("schema_version")) not in supported_schema_versions:
        raise IngestError(
            f"unsupported manifest schema_version={manifest.get('schema_version')!r}"
        )
    publication = manifest.get("publication") or {}
    if publication.get("publish_ready") is not True:
        raise IngestError("manifest publication.publish_ready is not true")
    if publication.get("url_status") != "live":
        raise IngestError("manifest publication.url_status is not live")
    if manifest.get("vertical") != "privacy":
        raise IngestError("only privacy vertical is allowed for structured ingestion")


def validate_asset(
    key: str,
    entry: dict[str, Any],
    content: str,
    expected_usage: str,
    supported_schema_versions: set[str],
) -> dict[str, Any]:
    for required in ["id", "version", "url", "sha256"]:
        if not entry.get(required):
            raise IngestError(f"{key}: manifest asset missing {required}")
    if entry.get("publish_ready") is not True or entry.get("url_status") != "live":
        raise IngestError(f"{key}: asset is not publish-ready live")
    actual_sha = sha256_text(content)
    if actual_sha != entry["sha256"]:
        raise IngestError(f"{key}: sha256 mismatch")

    header = yaml_header(content)
    schema_version = header.get("schema_version")
    if schema_version and schema_version not in supported_schema_versions:
        raise IngestError(f"{key}: unsupported asset schema_version={schema_version!r}")

    asset_type = header.get(
        "asset_type", "session_schema" if key == "session_schema" else ""
    )
    usage_mode = header.get("usage_mode")
    allowed_usage_by_type = {
        "taxonomy": "issue_framing_only",
        "retrieval_hints": "expansion_after_blind_search",
        "authority_map_core": "post_search_audit_only",
        "authority_map_overlay": "post_search_audit_only",
        "session_schema": "validation_reference_only",
    }
    # Usage vocabulary contrast (single home: knowledge_manifest.yaml authority_map usage):
    #   post_search_audit_only  -> accepted (current policy vocab)
    #   audit_only              -> rejected (legacy beopsuny-knowledge vocab; must not
    #                              be silently remapped — knowledge repo must update first)
    actual_usage = usage_mode or allowed_usage_by_type.get(asset_type)
    if actual_usage != expected_usage:
        raise IngestError(
            f"{key}: usage mismatch expected={expected_usage!r} actual={actual_usage!r}"
        )

    return {
        "key": key,
        "id": entry["id"],
        "version": entry["version"],
        "asset_type": asset_type,
        "usage": actual_usage,
        "sha256": actual_sha,
        "chars": len(content),
    }
