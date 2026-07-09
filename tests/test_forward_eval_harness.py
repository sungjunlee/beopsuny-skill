#!/usr/bin/env python3
"""Regression tests for the forward-eval harness."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
HARNESS_PATH = ROOT / "tests/forward_eval_harness.py"
CONFIG_PATH = ROOT / "tests/forward_evals/beopsuny_guardrails.yaml"
O4_CONFIG_PATH = ROOT / "tests/forward_evals/beopsuny_o4_provenance.yaml"


def load_harness():
    spec = importlib.util.spec_from_file_location("forward_eval_harness", HARNESS_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load {HARNESS_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ForwardEvalHarnessTests(unittest.TestCase):
    def test_sample_outputs_score_and_write_deterministic_evidence(self) -> None:
        harness = load_harness()
        config = harness.load_forward_eval(CONFIG_PATH)

        outputs = harness.sample_outputs(config)
        run = harness.score_forward_outputs(
            config,
            outputs,
            mode="sample",
            model="sample-beopsuny-forward-eval",
            run_at=harness.SAMPLE_RUN_AT,
        )

        self.assertEqual(run["summary"]["total"], 10)
        self.assertEqual(run["summary"]["failed"], 0)
        self.assertEqual([item["prompt_id"] for item in run["results"]], [item["id"] for item in config["prompts"]])

        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_path = Path(tmpdir) / "sample.yaml"
            harness.write_evidence(run, evidence_path)
            loaded = yaml.safe_load(evidence_path.read_text(encoding="utf-8"))

        self.assertEqual(loaded["run_at"], "1970-01-01T00:00:00Z")
        self.assertEqual(loaded["summary"], {"total": 10, "passed": 10, "failed": 0})
        for result in loaded["results"]:
            self.assertTrue(result["prompt_id"].startswith("fwd-"))
            self.assertTrue(result["guardrail_category"])
            self.assertTrue(result["output"])
            self.assertTrue(result["passed_guardrails"])
            self.assertEqual(result["failed_guardrails"], [])

    def test_failure_report_includes_prompt_category_and_output_evidence(self) -> None:
        harness = load_harness()
        config = harness.load_forward_eval(CONFIG_PATH)
        outputs = harness.sample_outputs(config)
        outputs["fwd-08-profile-write-boundary"] = "확인 없이 profile.yaml에 저장했습니다."

        run = harness.score_forward_outputs(
            config,
            outputs,
            mode="sample",
            model="sample-beopsuny-forward-eval",
            run_at=harness.SAMPLE_RUN_AT,
        )

        result = next(item for item in run["results"] if item["prompt_id"] == "fwd-08-profile-write-boundary")
        self.assertEqual(result["guardrail_category"], "profile_write_confirmation")
        self.assertGreaterEqual(len(result["failed_guardrails"]), 1)
        failure_text = yaml.safe_dump(result, allow_unicode=True)
        self.assertIn("fwd-08-profile-write-boundary", failure_text)
        self.assertIn("profile_write_confirmation", failure_text)
        self.assertIn("profile.yaml에 저장했습니다", failure_text)


class O4ProvenanceForwardEvalTests(unittest.TestCase):
    def test_o4_sample_outputs_all_pass(self) -> None:
        harness = load_harness()
        config = harness.load_forward_eval(O4_CONFIG_PATH)

        outputs = harness.sample_outputs(config)
        run = harness.score_forward_outputs(
            config,
            outputs,
            mode="sample",
            model="sample-beopsuny-forward-eval",
            run_at=harness.SAMPLE_RUN_AT,
            source_eval="tests/forward_evals/beopsuny_o4_provenance.yaml",
        )

        self.assertEqual(run["summary"]["total"], 8)
        self.assertEqual(run["summary"]["failed"], 0)
        self.assertEqual(run["source_eval"], "tests/forward_evals/beopsuny_o4_provenance.yaml")
        prompt_ids = [item["prompt_id"] for item in run["results"]]
        self.assertEqual(prompt_ids, [item["id"] for item in config["prompts"]])
        for prompt_id in prompt_ids:
            self.assertTrue(prompt_id.startswith("o4-"))
        for result in run["results"]:
            self.assertTrue(result["passed_guardrails"])
            self.assertEqual(result["failed_guardrails"], [])

    def test_o4_fabricated_trap_output_is_caught(self) -> None:
        harness = load_harness()
        config = harness.load_forward_eval(O4_CONFIG_PATH)
        outputs = harness.sample_outputs(config)
        # o4-06 forbids fabricating a non-existent article's content. A made-up
        # answer must be flagged, not silently pass.
        outputs["o4-06-nonexistent-article-trap"] = (
            "개인정보 보호법 제39조의99는 다음과 같이 규정합니다: 정보주체는 "
            "특별한 손해배상을 청구할 수 있습니다."
        )

        run = harness.score_forward_outputs(
            config,
            outputs,
            mode="sample",
            model="sample-beopsuny-forward-eval",
            run_at=harness.SAMPLE_RUN_AT,
        )

        self.assertGreaterEqual(run["summary"]["failed"], 1)
        result = next(
            item for item in run["results"] if item["prompt_id"] == "o4-06-nonexistent-article-trap"
        )
        self.assertEqual(result["guardrail_category"], "hallucination_source_trap")
        self.assertGreaterEqual(len(result["failed_guardrails"]), 1)
        failure_text = yaml.safe_dump(result, allow_unicode=True)
        self.assertIn("forbidden_failure", failure_text)


if __name__ == "__main__":
    unittest.main()
