#!/usr/bin/env python3
"""Fetch and validate beopsuny-knowledge manifest assets.

This helper is intentionally fail-open for legal research: network, auth,
schema, checksum, or usage-mode failures return a skipped packet unless
``--strict`` is set. The caller must continue live legal research either way.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_POLICY = ROOT / "skills/beopsuny/assets/policies/knowledge_manifest.yaml"
DEFAULT_MAX_ASSET_CHARS = 1800
RAW_MAIN_MARKER = "/sungjunlee/beopsuny-knowledge/main/"


class IngestError(Exception):
    """Expected ingestion failure that should degrade to skipped."""


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
        token = os.environ.get("BEOPSUNY_KNOWLEDGE_TOKEN") or os.environ.get(
            "GITHUB_TOKEN"
        )
        if token:
            headers["Authorization"] = f"Bearer {token}"
        request = urllib.request.Request(source, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310 - configured manifest URL.
                status = getattr(response, "status", 200)
                if status != 200:
                    raise IngestError(f"HTTP {status} for {source}")
                return response.read().decode("utf-8")
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            raise IngestError(f"failed to fetch {source}: {exc}") from exc
    return Path(source).read_text(encoding="utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def delivery_profile(max_asset_chars: int | None) -> str:
    if max_asset_chars is None:
        return "unknown"
    if max_asset_chars == DEFAULT_MAX_ASSET_CHARS:
        return "default"
    return "nondefault_override"


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


def build_packet(args: argparse.Namespace) -> dict[str, Any]:
    policy = load_yaml(Path(args.policy))
    manifest_policy = policy.get("knowledge_manifest") or {}
    channel = args.channel or manifest_policy.get("default_channel", "stable")
    channels = manifest_policy.get("channels") or {}
    channel_policy = channels.get(channel)
    if not isinstance(channel_policy, dict):
        raise IngestError(f"unknown manifest channel {channel!r}")
    if channel == "canary" and not args.allow_canary:
        raise IngestError("canary channel requires --allow-canary")

    manifest_source = (
        args.manifest_file or args.manifest_url or channel_policy.get("url")
    )
    if not manifest_source:
        raise IngestError("manifest source missing")
    knowledge_root = (
        Path(args.knowledge_root).resolve() if args.knowledge_root else None
    )
    manifest = json.loads(
        read_text_source(str(manifest_source), knowledge_root=knowledge_root)
    )
    supported = set(
        str(item)
        for item in (manifest.get("compatibility") or {}).get(
            "supported_schema_versions", []
        )
    )
    if not supported:
        supported = {"1"}
    validate_publication(manifest, supported)

    expected_assets = manifest_policy.get("required_asset_keys") or {}
    entries = manifest_asset_entries(manifest)
    max_chars = int(args.max_asset_chars)
    if max_chars < 0:
        raise IngestError("max_asset_chars must be non-negative")
    assets: list[dict[str, Any]] = []
    rendered_sections: dict[str, str] = {}
    delivery_receipt: list[dict[str, Any]] = []
    for key, expected in expected_assets.items():
        entry = entries.get(key)
        if not isinstance(entry, dict) or not entry:
            raise IngestError(f"manifest missing required asset {key!r}")
        expected_usage = str((expected or {}).get("usage", ""))
        content = read_text_source(str(entry["url"]), knowledge_root=knowledge_root)
        asset = validate_asset(key, entry, content, expected_usage, supported)
        assets.append(asset)
        if len(content) <= max_chars:
            rendered_sections[key] = content
            delivery_receipt.append(
                {
                    "key": key,
                    "source_chars": len(content),
                    "source_sha256": asset["sha256"],
                    "delivered_chars": len(content),
                    "delivered_sha256": asset["sha256"],
                    "status": "delivered",
                    "reason": "within_max_asset_chars",
                }
            )
        else:
            delivery_receipt.append(
                {
                    "key": key,
                    "source_chars": len(content),
                    "source_sha256": asset["sha256"],
                    "delivered_chars": 0,
                    "delivered_sha256": None,
                    "status": "omitted",
                    "reason": "source_exceeds_max_asset_chars",
                }
            )

    delivered_count = len(rendered_sections)
    if delivered_count == len(expected_assets):
        status = "ready"
    elif delivered_count:
        status = "partial"
    else:
        status = "skipped"

    packet: dict[str, Any] = {
        "status": status,
        "channel": channel,
        "vertical": "privacy",
        "manifest_schema_version": str(manifest.get("schema_version")),
        "assets": assets,
        "delivery": {
            "max_asset_chars": max_chars,
            "profile": delivery_profile(max_chars),
            "receipt": delivery_receipt,
        },
        "continue_live_legal_research": True,
    }
    if rendered_sections:
        packet["injection_packet"] = {
            "use": "post_blind_recall_and_audit_only",
            "not_legal_authority": True,
            "continue_live_legal_research": True,
            "rendered_sections": rendered_sections,
        }
    else:
        packet["reason"] = "no_complete_asset_section_within_max_asset_chars"
        packet["injection_packet"] = None
    return packet


def skipped_packet(reason: str, max_asset_chars: int | None = None) -> dict[str, Any]:
    return {
        "status": "skipped",
        "reason": reason,
        "continue_live_legal_research": True,
        "delivery": {
            "max_asset_chars": max_asset_chars,
            "profile": delivery_profile(max_asset_chars),
            "receipt": [],
            "status": "failed_before_delivery",
            "reason": reason,
        },
        "injection_packet": None,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    parser.add_argument("--channel", default=None)
    parser.add_argument("--manifest-url", default=None)
    parser.add_argument("--manifest-file", default=None)
    parser.add_argument("--knowledge-root", default=None)
    parser.add_argument("--allow-canary", action="store_true")
    parser.add_argument("--max-asset-chars", type=int, default=DEFAULT_MAX_ASSET_CHARS)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        packet = build_packet(args)
        exit_code = 0
    except Exception as exc:  # noqa: BLE001 - fail-open boundary is the contract.
        packet = skipped_packet(str(exc), max_asset_chars=args.max_asset_chars)
        exit_code = 1 if args.strict else 0
    print(json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
