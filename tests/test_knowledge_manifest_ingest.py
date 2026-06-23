#!/usr/bin/env python3
"""Regression tests for the beopsuny-knowledge manifest ingestion helper."""

from __future__ import annotations

import importlib.util
import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HELPER_PATH = ROOT / "skills/beopsuny/assets/tools/knowledge_manifest_ingest.py"
POLICY_PATH = ROOT / "skills/beopsuny/assets/policies/knowledge_manifest.yaml"
KNOWLEDGE_ROOT = Path("/Users/sjlee/workspace/active/legal-stack/beopsuny-knowledge")


def load_helper():
    spec = importlib.util.spec_from_file_location("knowledge_manifest_ingest", HELPER_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load {HELPER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class KnowledgeManifestIngestTests(unittest.TestCase):
    def write_asset(self, root: Path, relative: str, content: str) -> dict[str, object]:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return {
            "id": relative.replace("/", "."),
            "version": "test",
            "url": f"file://{path}",
            "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "publish_ready": True,
            "url_status": "live",
        }

    def test_temp_manifest_validates_assets_and_builds_packet(self) -> None:
        helper = load_helper()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            taxonomy = self.write_asset(
                root,
                "privacy/assets/taxonomy.yaml",
                "schema_version: 1\nasset_type: taxonomy\nusage_mode: issue_framing_only\n",
            )
            retrieval = self.write_asset(
                root,
                "privacy/assets/retrieval-hints.yaml",
                "schema_version: 1\nasset_type: retrieval_hints\nusage_mode: expansion_after_blind_search\n",
            )
            authority_core = self.write_asset(
                root,
                "privacy/assets/authority-map.core.yaml",
                "schema_version: 1\nasset_type: authority_map_core\nusage_mode: post_search_audit_only\n",
            )
            authority_overlay = self.write_asset(
                root,
                "privacy/assets/authority-map.overlay.yaml",
                "schema_version: 1\nasset_type: authority_map_overlay\nusage_mode: post_search_audit_only\n",
            )
            session_schema = self.write_asset(
                root,
                "_system/schemas/exploration-session.schema.yaml",
                "schema_version: 1\n",
            )
            manifest_path = root / "_system/manifests/stable.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "channel": "stable",
                        "vertical": "privacy",
                        "compatibility": {"supported_schema_versions": [1]},
                        "publication": {"publish_ready": True, "url_status": "live"},
                        "taxonomy": taxonomy,
                        "retrieval_hints": retrieval,
                        "authority_map": {
                            "core": authority_core,
                            "overlay": authority_overlay,
                        },
                        "session_schema": session_schema,
                    }
                ),
                encoding="utf-8",
            )

            packet = helper.build_packet(
                helper.parse_args(
                    [
                        "--policy",
                        str(POLICY_PATH),
                        "--manifest-file",
                        str(manifest_path),
                        "--max-asset-chars",
                        "400",
                    ]
                )
            )

        self.assertEqual(packet["status"], "ready")
        self.assertEqual(packet["channel"], "stable")
        self.assertEqual(packet["vertical"], "privacy")
        self.assertTrue(packet["injection_packet"]["not_legal_authority"])
        self.assertTrue(packet["injection_packet"]["continue_live_legal_research"])
        self.assertEqual(
            [asset["key"] for asset in packet["assets"]],
            ["taxonomy", "retrieval_hints", "authority_map.core", "authority_map.overlay", "session_schema"],
        )
        usages = {asset["key"]: asset["usage"] for asset in packet["assets"]}
        self.assertEqual(usages["taxonomy"], "issue_framing_only")
        self.assertEqual(usages["retrieval_hints"], "expansion_after_blind_search")
        self.assertEqual(usages["authority_map.core"], "post_search_audit_only")
        self.assertEqual(usages["authority_map.overlay"], "post_search_audit_only")

    @unittest.skipUnless(KNOWLEDGE_ROOT.exists(), "local beopsuny-knowledge checkout not available")
    def test_local_stable_manifest_validates_assets_and_builds_packet(self) -> None:
        helper = load_helper()
        manifest = KNOWLEDGE_ROOT / "_system/manifests/stable.json"

        packet = helper.build_packet(
            helper.parse_args(
                [
                    "--policy",
                    str(POLICY_PATH),
                    "--manifest-file",
                    str(manifest),
                    "--knowledge-root",
                    str(KNOWLEDGE_ROOT),
                    "--max-asset-chars",
                    "400",
                ]
            )
        )

        self.assertEqual(packet["status"], "ready")
        self.assertEqual(packet["vertical"], "privacy")
        self.assertEqual(len(packet["assets"]), 5)

    def test_private_raw_failure_degrades_to_skipped_packet(self) -> None:
        helper = load_helper()
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "missing.json"
            args = helper.parse_args(
                [
                    "--policy",
                    str(POLICY_PATH),
                    "--manifest-file",
                    str(manifest_path),
                ]
            )
            try:
                helper.build_packet(args)
            except Exception as exc:  # noqa: BLE001 - helper converts this at CLI boundary.
                packet = helper.skipped_packet(str(exc))
            else:
                self.fail("missing manifest should not build a ready packet")

        self.assertEqual(packet["status"], "skipped")
        self.assertTrue(packet["continue_live_legal_research"])
        self.assertIsNone(packet["injection_packet"])

    def test_cli_returns_zero_for_fail_open_skip(self) -> None:
        helper = load_helper()
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "missing.json"
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = helper.main(["--policy", str(POLICY_PATH), "--manifest-file", str(missing)])
        self.assertEqual(exit_code, 0)
        packet = json.loads(stdout.getvalue())
        self.assertEqual(packet["status"], "skipped")


if __name__ == "__main__":
    unittest.main()
