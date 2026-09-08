#!/usr/bin/env python3
"""Validate pinned privacy assets with runtime ingestion; prepare staged inputs only."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INGEST_HELPER = ROOT / "skills/beopsuny/assets/tools/knowledge_manifest_ingest.py"
STAGED_SECTIONS = {
    "taxonomy": "taxonomy.txt",
    "retrieval_hints": "hints.txt",
    "authority_map.core": "audit-core.txt",
    "authority_map.overlay": "audit-overlay.txt",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata_path(output: Path) -> Path:
    return output.parent / f"{output.name}-metadata.json"


def write_metadata(output: Path, metadata: dict[str, Any]) -> None:
    target = metadata_path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--knowledge-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--max-asset-chars",
        type=int,
        default=None,
        help="Explicit shared runtime/evaluation override; omission uses the loader default.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    knowledge = args.knowledge_root.resolve()
    output = args.output.resolve()
    command = [
        sys.executable,
        str(INGEST_HELPER),
        "--manifest-file",
        str(knowledge / "_system/manifests/stable.json"),
        "--knowledge-root",
        str(knowledge),
        "--strict",
    ]
    if args.max_asset_chars is not None:
        command.extend(["--max-asset-chars", str(args.max_asset_chars)])

    result = subprocess.run(command, capture_output=True, text=True, check=False)
    try:
        packet = json.loads(result.stdout)
    except json.JSONDecodeError:
        packet = {
            "status": "skipped",
            "reason": "ingestion helper did not return a JSON packet",
            "delivery": {"max_asset_chars": args.max_asset_chars, "receipt": []},
        }

    receipt_by_key = {
        item["key"]: item
        for item in (packet.get("delivery") or {}).get("receipt", [])
        if isinstance(item, dict) and item.get("key")
    }
    rendered_sections = (packet.get("injection_packet") or {}).get(
        "rendered_sections"
    ) or {}
    section_metadata: dict[str, dict[str, Any]] = {}
    for key, receipt in receipt_by_key.items():
        section_metadata[key] = {
            **receipt,
            "output_file": STAGED_SECTIONS.get(key),
            "output_sha256": None,
        }

    missing_sections = [key for key in STAGED_SECTIONS if key not in rendered_sections]
    delivery_profile = (packet.get("delivery") or {}).get("profile")
    if delivery_profile is None:
        delivery_profile = (
            "default" if args.max_asset_chars is None else "nondefault_override"
        )
    metadata: dict[str, Any] = {
        "status": "preparation_failed",
        "packet_status": packet.get("status"),
        "delivery_profile": delivery_profile,
        "max_asset_chars": (packet.get("delivery") or {}).get("max_asset_chars"),
        "missing_staged_sections": missing_sections,
        "sections": section_metadata,
        "assets": packet.get("assets", []),
        "snapshot": None,
        "files": {},
        "note": (
            "The loader delivery receipt is authoritative for actual section receipt. "
            "A nondefault override must be applied to both operational reproduction and evaluation "
            "and cannot be generalized as default operation."
        ),
    }
    capture_path = knowledge / "capture.json"
    if capture_path.exists():
        metadata["snapshot"] = json.loads(capture_path.read_text(encoding="utf-8"))

    if result.returncode or packet.get("status") == "skipped" or missing_sections:
        metadata["failure_reason"] = (
            packet.get("reason") or "required complete staged section was not delivered"
        )
        write_metadata(output, metadata)
        print(
            json.dumps(
                {
                    "status": "preparation_failed",
                    "packet_status": packet.get("status"),
                    "metadata": str(metadata_path(output)),
                },
                ensure_ascii=False,
            )
        )
        return 1

    output.mkdir(parents=True, exist_ok=False)
    for key, filename in STAGED_SECTIONS.items():
        target = output / filename
        target.write_text(rendered_sections[key], encoding="utf-8")
        section_metadata[key]["output_sha256"] = sha256_file(target)
    for name in ["privacy-saas", "privacy-tags"]:
        target = output / f"{name}.txt"
        target.write_text(
            (HERE / "inputs" / f"{name}.txt").read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    metadata["status"] = "prepared_not_measured"
    metadata["files"] = {path.name: sha256_file(path) for path in output.iterdir()}
    write_metadata(output, metadata)
    print(
        json.dumps(
            {
                "status": "prepared_not_measured",
                "packet_status": packet.get("status"),
                "delivery_profile": delivery_profile,
                "output": str(output),
                "metadata": str(metadata_path(output)),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
