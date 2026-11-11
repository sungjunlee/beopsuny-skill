#!/usr/bin/env python3
"""Regression tests for the beopsuny-knowledge manifest ingestion helper."""

from __future__ import annotations

import importlib.util
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HELPER_PATH = ROOT / "skills/beopsuny/assets/tools/knowledge_manifest_ingest.py"
POLICY_PATH = ROOT / "skills/beopsuny/assets/policies/knowledge_manifest.yaml"
PREPARE_PATH = ROOT / "tests/forward_evals/model_era/prepare_knowledge.py"


def load_helper():
    spec = importlib.util.spec_from_file_location(
        "knowledge_manifest_ingest", HELPER_PATH
    )
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load {HELPER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_prepare_knowledge():
    spec = importlib.util.spec_from_file_location(
        "prepare_knowledge_wrapper", PREPARE_PATH
    )
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load {PREPARE_PATH}")
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

    def write_fixture(
        self,
        root: Path,
        *,
        content_overrides: dict[str, str] | None = None,
        manifest_overrides: dict[str, object] | None = None,
    ) -> tuple[Path, dict[str, str], dict[str, object]]:
        contents = {
            "taxonomy": "schema_version: 1\nasset_type: taxonomy\nusage_mode: issue_framing_only\n",
            "retrieval_hints": (
                "schema_version: 1\nasset_type: retrieval_hints\n"
                "usage_mode: expansion_after_blind_search\n"
            ),
            "authority_map.core": (
                "schema_version: 1\nasset_type: authority_map_core\n"
                "usage_mode: post_search_audit_only\n"
            ),
            "authority_map.overlay": (
                "schema_version: 1\nasset_type: authority_map_overlay\n"
                "usage_mode: post_search_audit_only\n"
            ),
            "session_schema": "schema_version: 1\n",
        }
        contents.update(content_overrides or {})
        entries = {
            "taxonomy": self.write_asset(
                root, "privacy/assets/taxonomy.yaml", contents["taxonomy"]
            ),
            "retrieval_hints": self.write_asset(
                root, "privacy/assets/retrieval-hints.yaml", contents["retrieval_hints"]
            ),
            "authority_map.core": self.write_asset(
                root,
                "privacy/assets/authority-map.core.yaml",
                contents["authority_map.core"],
            ),
            "authority_map.overlay": self.write_asset(
                root,
                "privacy/assets/authority-map.overlay.yaml",
                contents["authority_map.overlay"],
            ),
            "session_schema": self.write_asset(
                root,
                "_system/schemas/exploration-session.schema.yaml",
                contents["session_schema"],
            ),
        }
        manifest: dict[str, object] = {
            "schema_version": 1,
            "channel": "stable",
            "vertical": "privacy",
            "compatibility": {"supported_schema_versions": [1]},
            "publication": {"publish_ready": True, "url_status": "live"},
            "taxonomy": entries["taxonomy"],
            "retrieval_hints": entries["retrieval_hints"],
            "authority_map": {
                "core": entries["authority_map.core"],
                "overlay": entries["authority_map.overlay"],
            },
            "session_schema": entries["session_schema"],
        }
        manifest.update(manifest_overrides or {})
        manifest_path = root / "_system/manifests/stable.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return manifest_path, contents, manifest

    def run_channel_case(
        self,
        helper,
        root: Path,
        *,
        selected: str,
        returned: str | None,
        allow_canary: bool,
        mode: str,
        strict: bool,
    ) -> tuple[int, dict[str, object], list[str]]:
        manifest_path, _, manifest = self.write_fixture(root)
        if returned is None:
            manifest.pop("channel")
        else:
            manifest["channel"] = returned
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        policy = helper.load_yaml(POLICY_PATH)["knowledge_manifest"]
        endpoints = {row["url"] for row in policy["channels"].values()}
        original_read = helper.read_text_source
        reads: list[str] = []

        def synthetic_read(location, knowledge_root=None):
            reads.append(location)
            if location in endpoints:
                return json.dumps(manifest)
            if location != str(manifest_path) and not location.startswith("file://"):
                raise AssertionError(f"unexpected source read: {location}")
            return original_read(location, knowledge_root=knowledge_root)

        args = ["--policy", str(POLICY_PATH)]
        if selected != "stable":
            args += ["--channel", selected]
        if allow_canary:
            args.append("--allow-canary")
        if mode == "local_file":
            args += ["--manifest-file", str(manifest_path)]
        if strict:
            args.append("--strict")

        output = io.StringIO()
        with (
            patch.object(helper, "read_text_source", side_effect=synthetic_read),
            patch.object(
                helper.urllib.request,
                "urlopen",
                side_effect=AssertionError("network forbidden"),
            ),
            redirect_stdout(output),
        ):
            exit_code = helper.main(args)
        return exit_code, json.loads(output.getvalue()), reads

    def run_schema_case(
        self,
        helper,
        root: Path,
        *,
        manifest_version: int,
        advertised: list[int] | None,
        asset_version: int,
        strict: bool,
    ) -> tuple[int, dict[str, object], list[str]]:
        _, contents, _ = self.write_fixture(root)
        contents = {
            key: text.replace(
                "schema_version: 1", f"schema_version: {asset_version}"
            )
            for key, text in contents.items()
        }
        manifest_path, _, manifest = self.write_fixture(
            root,
            content_overrides=contents,
            manifest_overrides={"schema_version": manifest_version},
        )
        if advertised is None:
            manifest.pop("compatibility")
        else:
            manifest["compatibility"] = {
                "supported_schema_versions": advertised
            }
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        original_read = helper.read_text_source
        reads: list[str] = []

        def tracked_read(location, knowledge_root=None):
            reads.append(location)
            return original_read(location, knowledge_root=knowledge_root)

        args = ["--manifest-file", str(manifest_path)]
        if strict:
            args.append("--strict")
        output = io.StringIO()
        with (
            patch.object(helper, "read_text_source", side_effect=tracked_read),
            patch.object(
                helper.urllib.request,
                "urlopen",
                side_effect=AssertionError("network forbidden"),
            ),
            redirect_stdout(output),
        ):
            exit_code = helper.main(args)
        return exit_code, json.loads(output.getvalue()), reads

    def test_temp_manifest_validates_assets_and_builds_packet(self) -> None:
        helper = load_helper()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path, contents, _ = self.write_fixture(root)

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
            [
                "taxonomy",
                "retrieval_hints",
                "authority_map.core",
                "authority_map.overlay",
                "session_schema",
            ],
        )
        usages = {asset["key"]: asset["usage"] for asset in packet["assets"]}
        self.assertEqual(usages["taxonomy"], "issue_framing_only")
        self.assertEqual(usages["retrieval_hints"], "expansion_after_blind_search")
        self.assertEqual(usages["authority_map.core"], "post_search_audit_only")
        self.assertEqual(usages["authority_map.overlay"], "post_search_audit_only")
        self.assertEqual(packet["delivery"]["max_asset_chars"], 400)
        self.assertEqual(packet["delivery"]["profile"], "nondefault_override")
        self.assertEqual(len(packet["delivery"]["receipt"]), 5)
        self.assertEqual(packet["injection_packet"]["rendered_sections"], contents)

    def test_consumer_schema_support_accepts_v1_with_declared_or_missing_metadata(
        self,
    ) -> None:
        helper = load_helper()
        self.assertEqual(helper.CONSUMER_SUPPORTED_SCHEMA_VERSIONS, {"1"})
        with tempfile.TemporaryDirectory() as tmpdir:
            for advertised in ([1], [], None):
                with self.subTest(advertised=advertised):
                    exit_code, packet, reads = self.run_schema_case(
                        helper,
                        Path(tmpdir),
                        manifest_version=1,
                        advertised=advertised,
                        asset_version=1,
                        strict=True,
                    )

                    self.assertEqual(exit_code, 0)
                    self.assertEqual(packet["status"], "ready")
                    self.assertIsNotNone(packet["injection_packet"])
                    self.assertEqual(
                        sum(location.startswith("file://") for location in reads), 5
                    )

    def test_producer_metadata_cannot_expand_supported_manifest_schemas(self) -> None:
        helper = load_helper()
        cases = (None, [], [999], [1, 999])
        with tempfile.TemporaryDirectory() as tmpdir:
            for advertised in cases:
                for strict, expected_exit in ((False, 0), (True, 1)):
                    with self.subTest(advertised=advertised, strict=strict):
                        exit_code, packet, reads = self.run_schema_case(
                            helper,
                            Path(tmpdir),
                            manifest_version=999,
                            advertised=advertised,
                            asset_version=999,
                            strict=strict,
                        )

                        self.assertEqual(exit_code, expected_exit)
                        self.assertEqual(packet["status"], "skipped")
                        self.assertIn(
                            "unsupported manifest schema_version=999", packet["reason"]
                        )
                        self.assertTrue(packet["continue_live_legal_research"])
                        self.assertIsNone(packet["injection_packet"])
                        self.assertEqual(packet["delivery"]["receipt"], [])
                        self.assertEqual(
                            sum(
                                location.startswith("file://") for location in reads
                            ),
                            0,
                        )

    def test_producer_metadata_cannot_expand_supported_asset_schemas(self) -> None:
        helper = load_helper()
        with tempfile.TemporaryDirectory() as tmpdir:
            exit_code, packet, reads = self.run_schema_case(
                helper,
                Path(tmpdir),
                manifest_version=1,
                advertised=[1, 999],
                asset_version=999,
                strict=True,
            )

        self.assertEqual(exit_code, 1)
        self.assertEqual(packet["status"], "skipped")
        self.assertIn("unsupported asset schema_version='999'", packet["reason"])
        self.assertTrue(packet["continue_live_legal_research"])
        self.assertIsNone(packet["injection_packet"])
        self.assertEqual(
            sum(location.startswith("file://") for location in reads), 1
        )

    def test_producer_metadata_can_narrow_consumer_schema_support(self) -> None:
        helper = load_helper()
        with tempfile.TemporaryDirectory() as tmpdir:
            exit_code, packet, reads = self.run_schema_case(
                helper,
                Path(tmpdir),
                manifest_version=1,
                advertised=[999],
                asset_version=1,
                strict=True,
            )

        self.assertEqual(exit_code, 1)
        self.assertEqual(packet["status"], "skipped")
        self.assertIn("unsupported manifest schema_version=1", packet["reason"])
        self.assertEqual(
            sum(location.startswith("file://") for location in reads), 0
        )

    def test_manifest_channel_matches_for_endpoint_and_local_file(self) -> None:
        helper = load_helper()
        with tempfile.TemporaryDirectory() as tmpdir:
            for selected, allow_canary in (("stable", False), ("canary", True)):
                for mode in ("configured_endpoint", "local_file"):
                    with self.subTest(selected=selected, mode=mode):
                        exit_code, packet, reads = self.run_channel_case(
                            helper,
                            Path(tmpdir),
                            selected=selected,
                            returned=selected,
                            allow_canary=allow_canary,
                            mode=mode,
                            strict=True,
                        )

                        self.assertEqual(exit_code, 0)
                        self.assertEqual(packet["status"], "ready")
                        self.assertEqual(packet["channel"], selected)
                        self.assertEqual(
                            sum(location.startswith("file://") for location in reads),
                            5,
                        )

    def test_invalid_or_mismatched_manifest_channel_skips_before_assets(self) -> None:
        helper = load_helper()
        cases = [
            ("stable", "canary", False, "manifest channel mismatch"),
            ("stable", None, False, "unknown manifest channel"),
            ("stable", "unknown", False, "unknown manifest channel"),
            ("canary", "stable", True, "manifest channel mismatch"),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            for selected, returned, allow_canary, reason in cases:
                for mode in ("configured_endpoint", "local_file"):
                    with self.subTest(
                        selected=selected, returned=returned, mode=mode
                    ):
                        exit_code, packet, reads = self.run_channel_case(
                            helper,
                            Path(tmpdir),
                            selected=selected,
                            returned=returned,
                            allow_canary=allow_canary,
                            mode=mode,
                            strict=True,
                        )

                        self.assertEqual(exit_code, 1)
                        self.assertEqual(packet["status"], "skipped")
                        self.assertNotIn("channel", packet)
                        self.assertIn(reason, packet["reason"])
                        self.assertTrue(packet["continue_live_legal_research"])
                        self.assertIsNone(packet["injection_packet"])
                        self.assertEqual(packet["delivery"]["receipt"], [])
                        self.assertEqual(
                            packet["delivery"]["status"], "failed_before_delivery"
                        )
                        self.assertEqual(
                            sum(location.startswith("file://") for location in reads),
                            0,
                        )

    def test_canary_channel_still_requires_opt_in(self) -> None:
        helper = load_helper()
        with tempfile.TemporaryDirectory() as tmpdir:
            for mode in ("configured_endpoint", "local_file"):
                with self.subTest(mode=mode):
                    exit_code, packet, reads = self.run_channel_case(
                        helper,
                        Path(tmpdir),
                        selected="canary",
                        returned="canary",
                        allow_canary=False,
                        mode=mode,
                        strict=True,
                    )

                    self.assertEqual(exit_code, 1)
                    self.assertEqual(packet["status"], "skipped")
                    self.assertIn("requires --allow-canary", packet["reason"])
                    self.assertEqual(reads, [])

    def test_manifest_channel_mismatch_is_fail_open_unless_strict(self) -> None:
        helper = load_helper()
        with tempfile.TemporaryDirectory() as tmpdir:
            for mode in ("configured_endpoint", "local_file"):
                with self.subTest(mode=mode):
                    exit_code, packet, reads = self.run_channel_case(
                        helper,
                        Path(tmpdir),
                        selected="stable",
                        returned="canary",
                        allow_canary=False,
                        mode=mode,
                        strict=False,
                    )

                    self.assertEqual(exit_code, 0)
                    self.assertEqual(packet["status"], "skipped")
                    self.assertTrue(packet["continue_live_legal_research"])
                    self.assertIsNone(packet["injection_packet"])
                    self.assertEqual(
                        sum(location.startswith("file://") for location in reads), 0
                    )

    def test_exact_boundary_delivers_whole_section_and_one_extra_char_omits_it(
        self,
    ) -> None:
        helper = load_helper()
        taxonomy = (
            "schema_version: 1\nasset_type: taxonomy\nusage_mode: issue_framing_only\n"
            "conditions:\n  - boundary condition\n"
        )
        limit = len(taxonomy)
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path, _, _ = self.write_fixture(
                root, content_overrides={"taxonomy": taxonomy}
            )
            base_args = [
                "--policy",
                str(POLICY_PATH),
                "--manifest-file",
                str(manifest_path),
            ]

            ready = helper.build_packet(
                helper.parse_args([*base_args, "--max-asset-chars", str(limit)])
            )

            longer = taxonomy + "x"
            manifest_path, _, _ = self.write_fixture(
                root, content_overrides={"taxonomy": longer}
            )
            partial = helper.build_packet(
                helper.parse_args([*base_args, "--max-asset-chars", str(limit)])
            )

        self.assertEqual(ready["status"], "ready")
        self.assertEqual(
            ready["injection_packet"]["rendered_sections"]["taxonomy"], taxonomy
        )
        ready_receipt = next(
            item for item in ready["delivery"]["receipt"] if item["key"] == "taxonomy"
        )
        self.assertEqual(ready_receipt["source_chars"], limit)
        self.assertEqual(ready_receipt["delivered_chars"], limit)
        self.assertEqual(
            ready_receipt["source_sha256"], ready_receipt["delivered_sha256"]
        )
        self.assertEqual(ready_receipt["status"], "delivered")

        self.assertEqual(partial["status"], "partial")
        self.assertNotIn("taxonomy", partial["injection_packet"]["rendered_sections"])
        partial_receipt = next(
            item for item in partial["delivery"]["receipt"] if item["key"] == "taxonomy"
        )
        self.assertEqual(partial_receipt["source_chars"], limit + 1)
        self.assertEqual(partial_receipt["delivered_chars"], 0)
        self.assertIsNone(partial_receipt["delivered_sha256"])
        self.assertEqual(partial_receipt["status"], "omitted")
        self.assertEqual(partial_receipt["reason"], "source_exceeds_max_asset_chars")

    def test_long_asset_late_condition_is_never_delivered_as_a_truncated_section(
        self,
    ) -> None:
        helper = load_helper()
        long_taxonomy = (
            "schema_version: 1\nasset_type: taxonomy\nusage_mode: issue_framing_only\n"
            + "padding: "
            + ("x" * 200)
            + "\nconditions:\n  - LATE_CONDITION_MUST_REMAIN_CONNECTED\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path, _, _ = self.write_fixture(
                root, content_overrides={"taxonomy": long_taxonomy}
            )
            base_args = [
                "--policy",
                str(POLICY_PATH),
                "--manifest-file",
                str(manifest_path),
            ]

            partial = helper.build_packet(
                helper.parse_args([*base_args, "--max-asset-chars", "180"])
            )
            complete = helper.build_packet(
                helper.parse_args(
                    [*base_args, "--max-asset-chars", str(len(long_taxonomy))]
                )
            )

        self.assertNotIn("taxonomy", partial["injection_packet"]["rendered_sections"])
        delivered = complete["injection_packet"]["rendered_sections"]["taxonomy"]
        self.assertIn("LATE_CONDITION_MUST_REMAIN_CONNECTED", delivered)
        self.assertEqual(delivered, long_taxonomy)

    def test_zero_budget_skips_delivery_but_keeps_full_validation_receipt_and_live_fallback(
        self,
    ) -> None:
        helper = load_helper()
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path, _, _ = self.write_fixture(Path(tmpdir))
            packet = helper.build_packet(
                helper.parse_args(
                    [
                        "--policy",
                        str(POLICY_PATH),
                        "--manifest-file",
                        str(manifest_path),
                        "--max-asset-chars",
                        "0",
                    ]
                )
            )

        self.assertEqual(packet["status"], "skipped")
        self.assertEqual(
            packet["reason"], "no_complete_asset_section_within_max_asset_chars"
        )
        self.assertTrue(packet["continue_live_legal_research"])
        self.assertIsNone(packet["injection_packet"])
        self.assertEqual(len(packet["assets"]), 5)
        self.assertEqual(len(packet["delivery"]["receipt"]), 5)
        self.assertTrue(
            all(item["status"] == "omitted" for item in packet["delivery"]["receipt"])
        )

    def test_oversized_assets_still_enforce_checksum_usage_and_publication(
        self,
    ) -> None:
        helper = load_helper()
        long_taxonomy = (
            "schema_version: 1\nasset_type: taxonomy\nusage_mode: issue_framing_only\n"
            + ("x" * 200)
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path, _, manifest = self.write_fixture(
                root, content_overrides={"taxonomy": long_taxonomy}
            )
            retrieval = manifest["retrieval_hints"]
            assert isinstance(retrieval, dict)
            retrieval["sha256"] = "0" * 64
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(
                helper.IngestError, "retrieval_hints: sha256 mismatch"
            ):
                helper.build_packet(
                    helper.parse_args(
                        [
                            "--policy",
                            str(POLICY_PATH),
                            "--manifest-file",
                            str(manifest_path),
                            "--max-asset-chars",
                            "10",
                        ]
                    )
                )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = helper.main(
                    [
                        "--policy",
                        str(POLICY_PATH),
                        "--manifest-file",
                        str(manifest_path),
                        "--max-asset-chars",
                        "10",
                        "--strict",
                    ]
                )
            failed_packet = json.loads(stdout.getvalue())

        self.assertEqual(exit_code, 1)
        self.assertEqual(failed_packet["status"], "skipped")
        self.assertTrue(failed_packet["continue_live_legal_research"])
        self.assertEqual(failed_packet["delivery"]["status"], "failed_before_delivery")
        self.assertIn("retrieval_hints: sha256 mismatch", failed_packet["reason"])

        for case, content_overrides, manifest_overrides, expected_error in [
            (
                "schema",
                {
                    "taxonomy": (
                        "schema_version: 2\nasset_type: taxonomy\nusage_mode: issue_framing_only\n"
                    )
                },
                None,
                "taxonomy: unsupported asset schema_version='2'",
            ),
            (
                "usage",
                {
                    "retrieval_hints": (
                        "schema_version: 1\nasset_type: retrieval_hints\nusage_mode: issue_framing_only\n"
                    )
                },
                None,
                "retrieval_hints: usage mismatch",
            ),
            (
                "publication",
                None,
                {"publication": {"publish_ready": False, "url_status": "live"}},
                "manifest publication.publish_ready is not true",
            ),
        ]:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmpdir:
                manifest_path, _, _ = self.write_fixture(
                    Path(tmpdir),
                    content_overrides=content_overrides,
                    manifest_overrides=manifest_overrides,
                )
                with self.assertRaisesRegex(helper.IngestError, expected_error):
                    helper.build_packet(
                        helper.parse_args(
                            [
                                "--policy",
                                str(POLICY_PATH),
                                "--manifest-file",
                                str(manifest_path),
                                "--max-asset-chars",
                                "0",
                            ]
                        )
                    )

    def test_default_limit_remains_1800(self) -> None:
        helper = load_helper()
        self.assertEqual(helper.DEFAULT_MAX_ASSET_CHARS, 1800)
        self.assertEqual(helper.parse_args([]).max_asset_chars, 1800)

    def test_evaluation_default_uses_loader_limit_and_records_missing_section(
        self,
    ) -> None:
        long_taxonomy = (
            "schema_version: 1\nasset_type: taxonomy\nusage_mode: issue_framing_only\n"
            + ("x" * 1801)
            + "\nconditions:\n  - LATE_CONDITION\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_fixture(root, content_overrides={"taxonomy": long_taxonomy})
            output = root / "prepared-default"

            result = subprocess.run(
                [
                    sys.executable,
                    str(PREPARE_PATH),
                    "--knowledge-root",
                    str(root),
                    "--output",
                    str(output),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            metadata = json.loads(
                (root / "prepared-default-metadata.json").read_text(encoding="utf-8")
            )

        self.assertEqual(result.returncode, 1)
        self.assertFalse(output.exists())
        self.assertEqual(metadata["status"], "preparation_failed")
        self.assertEqual(metadata["packet_status"], "partial")
        self.assertEqual(metadata["delivery_profile"], "default")
        self.assertEqual(metadata["max_asset_chars"], 1800)
        self.assertIn("taxonomy", metadata["missing_staged_sections"])
        self.assertEqual(metadata["sections"]["taxonomy"]["status"], "omitted")
        self.assertIsNone(metadata["sections"]["taxonomy"]["output_sha256"])

    def test_explicit_shared_override_matches_runtime_packet_and_is_labeled_nondefault(
        self,
    ) -> None:
        helper = load_helper()
        late_taxonomy = (
            "schema_version: 1\nasset_type: taxonomy\nusage_mode: issue_framing_only\n"
            + ("x" * 2000)
            + "\nconditions:\n  - LATE_CONDITION\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path, contents, _ = self.write_fixture(
                root, content_overrides={"taxonomy": late_taxonomy}
            )
            cap = max(len(content) for content in contents.values())
            runtime_packet = helper.build_packet(
                helper.parse_args(
                    [
                        "--policy",
                        str(POLICY_PATH),
                        "--manifest-file",
                        str(manifest_path),
                        "--knowledge-root",
                        str(root),
                        "--max-asset-chars",
                        str(cap),
                    ]
                )
            )
            output = root / "prepared-override"

            result = subprocess.run(
                [
                    sys.executable,
                    str(PREPARE_PATH),
                    "--knowledge-root",
                    str(root),
                    "--output",
                    str(output),
                    "--max-asset-chars",
                    str(cap),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            metadata = json.loads(
                (root / "prepared-override-metadata.json").read_text(encoding="utf-8")
            )
            staged_files = {
                "taxonomy": "taxonomy.txt",
                "retrieval_hints": "hints.txt",
                "authority_map.core": "audit-core.txt",
                "authority_map.overlay": "audit-overlay.txt",
            }
            staged_contents = {
                key: (output / filename).read_text(encoding="utf-8")
                for key, filename in staged_files.items()
            }

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(runtime_packet["status"], "ready")
        self.assertEqual(metadata["status"], "prepared_not_measured")
        self.assertEqual(metadata["packet_status"], "ready")
        self.assertEqual(metadata["delivery_profile"], "nondefault_override")
        self.assertEqual(metadata["max_asset_chars"], cap)
        for key, content in staged_contents.items():
            self.assertEqual(
                content, runtime_packet["injection_packet"]["rendered_sections"][key]
            )
            section = metadata["sections"][key]
            self.assertEqual(section["status"], "delivered")
            self.assertEqual(section["source_chars"], section["delivered_chars"])
            self.assertEqual(section["source_sha256"], section["delivered_sha256"])
            self.assertEqual(section["delivered_sha256"], section["output_sha256"])
        self.assertIn("LATE_CONDITION", staged_contents["taxonomy"])

    def test_strict_rejects_complete_omission_but_default_stays_fail_open(self):
        helper = load_helper()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, _, _ = self.write_fixture(root)
            args = ["--manifest-file", str(manifest), "--knowledge-root", str(root), "--max-asset-chars", "0"]
            for strict, expected in ((False, 0), (True, 1)):
                output = io.StringIO()
                with redirect_stdout(output):
                    result = helper.main(args + (["--strict"] if strict else []))
                self.assertEqual(result, expected)
                packet = json.loads(output.getvalue())
                self.assertEqual(packet["status"], "skipped")
                self.assertEqual(len(packet["delivery"]["receipt"]), 5)
                self.assertTrue(all(item["status"] == "omitted" for item in packet["delivery"]["receipt"]))

    def test_post_search_audit_only_usage_passes(self) -> None:
        helper = load_helper()
        content = "schema_version: 1\nasset_type: authority_map_core\nusage_mode: post_search_audit_only\n"
        result = helper.validate_asset(
            "authority_map.core",
            {"id": "x", "version": "1", "url": "file:///x", "sha256": helper.sha256_text(content), "publish_ready": True, "url_status": "live"},
            content,
            "post_search_audit_only",
            {"1"},
        )
        self.assertEqual(result["usage"], "post_search_audit_only")

    def test_legacy_audit_only_usage_fails(self) -> None:
        helper = load_helper()
        for asset_type in ("authority_map_core", "authority_map_overlay"):
            content = f"schema_version: 1\nasset_type: {asset_type}\nusage_mode: audit_only\n"
            with self.assertRaises(helper.IngestError):
                helper.validate_asset(
                    "authority_map.core" if asset_type == "authority_map_core" else "authority_map.overlay",
                    {"id": "x", "version": "1", "url": "file:///x", "sha256": helper.sha256_text(content), "publish_ready": True, "url_status": "live"},
                    content,
                    "post_search_audit_only",
                    {"1"},
                )

    def test_private_raw_failure_degrades_to_skipped_packet(self) -> None:
        helper = load_helper()
        url = "https://raw.githubusercontent.com/sungjunlee/beopsuny-knowledge/main/_system/manifests/stable.json"
        for strict, expected in ((False, 0), (True, 1)):
            error = helper.urllib.error.HTTPError(url, 404, "Not Found", {}, None)
            output = io.StringIO()
            with patch.object(helper.urllib.request, "urlopen", side_effect=error), redirect_stdout(output):
                result = helper.main(["--manifest-url", url] + (["--strict"] if strict else []))
            packet = json.loads(output.getvalue())
            self.assertEqual(result, expected)
            self.assertEqual(packet["status"], "skipped")
            self.assertTrue(packet["continue_live_legal_research"])
            self.assertIsNone(packet["injection_packet"])
            self.assertEqual(packet["delivery"]["status"], "failed_before_delivery")

    def test_cli_returns_zero_for_fail_open_skip(self) -> None:
        helper = load_helper()
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "missing.json"
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = helper.main(
                    ["--policy", str(POLICY_PATH), "--manifest-file", str(missing)]
                )
        self.assertEqual(exit_code, 0)
        packet = json.loads(stdout.getvalue())
        self.assertEqual(packet["status"], "skipped")
        self.assertEqual(packet["delivery"]["max_asset_chars"], 1800)
        self.assertEqual(packet["delivery"]["profile"], "default")
        self.assertEqual(packet["delivery"]["status"], "failed_before_delivery")


HELPER_SKIP_REASON = "synthetic helper did not deliver staged sections"


class PrepareKnowledgeRetryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_prepare_knowledge()

    def run_failed_helper(self, knowledge: Path, output: Path) -> int:
        packet = {
            "status": "skipped",
            "reason": HELPER_SKIP_REASON,
            "delivery": {"max_asset_chars": None, "receipt": []},
        }
        completed = subprocess.CompletedProcess(
            args=["knowledge-ingest"],
            returncode=1,
            stdout=json.dumps(packet),
            stderr="",
        )
        stdout = io.StringIO()
        with (
            patch.object(self.module.subprocess, "run", return_value=completed),
            redirect_stdout(stdout),
        ):
            return self.module.main(
                ["--knowledge-root", str(knowledge), "--output", str(output)]
            )

    def test_failed_retry_preserves_matching_output_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            knowledge = root / "knowledge"
            knowledge.mkdir()
            output = root / "staged"
            output.mkdir()
            staged = output / "section.txt"
            staged_bytes = b"SENTINEL_STAGED\n"
            staged.write_bytes(staged_bytes)
            digest = hashlib.sha256(staged_bytes).hexdigest()
            metadata = {
                "status": "prepared_not_measured",
                "sentinel": "SENTINEL_METADATA",
                "files": {"section.txt": digest},
            }
            meta_path = self.module.metadata_path(output)
            meta_bytes = (
                json.dumps(metadata, ensure_ascii=False, indent=2) + "\n"
            ).encode("utf-8")
            meta_path.write_bytes(meta_bytes)
            self.assertEqual(
                json.loads(meta_bytes)["files"]["section.txt"],
                hashlib.sha256(staged.read_bytes()).hexdigest(),
            )
            before_tree = {
                path.relative_to(output).as_posix(): path.read_bytes()
                for path in output.rglob("*")
                if path.is_file()
            }

            code = self.run_failed_helper(knowledge, output)

            after_tree = {
                path.relative_to(output).as_posix(): path.read_bytes()
                for path in output.rglob("*")
                if path.is_file()
            }
            self.assertEqual(code, 1)
            self.assertEqual(after_tree, before_tree)
            self.assertEqual(meta_path.read_bytes(), meta_bytes)
            self.assertEqual(
                json.loads(meta_path.read_text(encoding="utf-8"))["status"],
                "prepared_not_measured",
            )

    def test_failed_retry_preserves_metadata_when_output_is_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            knowledge = root / "knowledge"
            knowledge.mkdir()
            output = root / "staged"
            meta_path = self.module.metadata_path(output)
            meta_bytes = (
                json.dumps(
                    {
                        "status": "prepared_not_measured",
                        "sentinel": "SENTINEL_METADATA_ONLY",
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n"
            ).encode("utf-8")
            meta_path.write_bytes(meta_bytes)
            self.assertFalse(output.exists())

            code = self.run_failed_helper(knowledge, output)

            self.assertEqual(code, 1)
            self.assertEqual(meta_path.read_bytes(), meta_bytes)
            self.assertFalse(output.exists())
            self.assertEqual(
                json.loads(meta_path.read_text(encoding="utf-8"))["status"],
                "prepared_not_measured",
            )

    def test_first_failure_on_new_destination_records_failure_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            knowledge = root / "knowledge"
            knowledge.mkdir()
            output = root / "staged"
            meta_path = self.module.metadata_path(output)
            self.assertFalse(output.exists())
            self.assertFalse(meta_path.exists())

            code = self.run_failed_helper(knowledge, output)

            self.assertEqual(code, 1)
            self.assertFalse(output.exists())
            metadata = json.loads(meta_path.read_text(encoding="utf-8"))
            self.assertEqual(metadata["status"], "preparation_failed")
            self.assertEqual(metadata["packet_status"], "skipped")
            self.assertEqual(metadata["failure_reason"], HELPER_SKIP_REASON)


if __name__ == "__main__":
    unittest.main()
