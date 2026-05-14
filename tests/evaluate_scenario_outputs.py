#!/usr/bin/env python3
"""Evaluate sample skill outputs against scenario-level string checks.

This is a lightweight harness, not a legal-correctness judge. It lets scenario
fixtures pin concrete output guardrails such as required reviewer-note text,
source-status tags, and forbidden unsafe phrases.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENARIOS = [ROOT / "tests/scenarios/16_router_regression.yaml"]
DEFAULT_OUTPUTS = ROOT / "tests/fixtures/router_guardrail_outputs.yaml"
STATUS_TAGS = {
    "[VERIFIED]",
    "[UNVERIFIED]",
    "[INSUFFICIENT]",
    "[CONTRADICTED]",
    "[STALE]",
    "[EDITORIAL]",
}
UNCERTAINTY_PATTERNS = [
    "확인 불가",
    "원문 미확인",
    "추정",
    "블로그",
    "사용자 전제",
]
PUSH_BOUNDARY_PATTERNS = [
    "알림을 설정",
    "크론",
    "스케줄",
    "notification",
    "자동으로 알려드림",
    "푸시",
    "정기적으로 알려드릴게요",
    "주기적으로 체크해드리겠습니다",
    "자동 모니터링",
    "지속적으로 추적해드리겠습니다",
]


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def collect_scenarios(paths: list[Path]) -> dict[str, dict[str, Any]]:
    scenarios: dict[str, dict[str, Any]] = {}
    for path in paths:
        data = load_yaml(path)
        for scenario in data.get("scenarios", []):
            scenario_id = scenario.get("id")
            if not scenario_id:
                raise AssertionError(f"{path}: scenario missing id")
            if scenario_id in scenarios:
                raise AssertionError(f"duplicate scenario id: {scenario_id}")
            scenarios[scenario_id] = scenario
    return scenarios


def load_outputs(path: Path) -> dict[str, str]:
    data = load_yaml(path)
    outputs = data.get("outputs", {})
    if not isinstance(outputs, dict):
        raise AssertionError(f"{path}: outputs must be a mapping")
    return {str(key): str(value) for key, value in outputs.items()}


def load_list_from_source(source: str) -> list[str]:
    path_text, _, key_path = source.partition("#")
    source_path = ROOT / path_text
    if not source_path.exists():
        source_path = ROOT / "skills/beopsuny" / path_text
    data = load_yaml(source_path)
    current: Any = data
    for key in key_path.split("."):
        if not key:
            continue
        if not isinstance(current, dict) or key not in current:
            raise AssertionError(f"{source}: missing key {key!r}")
        current = current[key]
    if not isinstance(current, list) or not all(isinstance(item, str) for item in current):
        raise AssertionError(f"{source}: expected a list of strings")
    return current


def output_common_rules(scenario: dict[str, Any]) -> list[str]:
    output_eval = scenario.get("output_eval") or {}
    rules = list(output_eval.get("common_rules", []))
    expected = scenario.get("expected") or {}

    if expected.get("primary_intent") == "contract_review":
        rules.append("contract_counter_draft_boundary")
    if expected.get("primary_intent") == "law_change_detection":
        rules.append("law_change_push_boundary")

    return sorted(set(str(rule) for rule in rules))


def evaluate_common_rule(scenario_id: str, scenario: dict[str, Any], output: str, rule: str) -> list[str]:
    failures: list[str] = []

    if rule == "legal_status_tag":
        if not any(tag in output for tag in STATUS_TAGS):
            failures.append(f"{scenario_id}: common rule {rule} missing status tag")
        return failures

    if rule == "no_verified_uncertainty":
        for line in output.splitlines():
            if "[VERIFIED]" in line and any(pattern in line for pattern in UNCERTAINTY_PATTERNS):
                failures.append(f"{scenario_id}: common rule {rule} has [VERIFIED] with uncertainty text")
        return failures

    if rule == "contract_counter_draft_boundary":
        expected = scenario.get("expected") or {}
        source = expected.get("forbidden_phrases_source")
        patterns = list(expected.get("forbidden_phrases", []))
        if source:
            patterns.extend(load_list_from_source(str(source)))
        for pattern in sorted(set(str(item) for item in patterns)):
            if pattern in output:
                failures.append(f"{scenario_id}: common rule {rule} contains forbidden pattern {pattern!r}")
        return failures

    if rule == "law_change_push_boundary":
        for pattern in PUSH_BOUNDARY_PATTERNS:
            if pattern in output:
                failures.append(f"{scenario_id}: common rule {rule} contains push-boundary pattern {pattern!r}")
        return failures

    if rule == "self_verification_metadata":
        if not re.search(r"자가 검증\s*:", output):
            failures.append(f"{scenario_id}: common rule {rule} missing self-verification metadata")
        return failures

    failures.append(f"{scenario_id}: unknown common rule {rule!r}")
    return failures


def evaluate_outputs(scenarios: dict[str, dict[str, Any]], outputs: dict[str, str]) -> list[str]:
    failures: list[str] = []
    expected_output_ids = {
        scenario_id for scenario_id, scenario in scenarios.items() if scenario.get("output_eval")
    }
    missing_outputs = expected_output_ids - set(outputs)
    for scenario_id in sorted(missing_outputs):
        failures.append(f"{scenario_id}: output_eval scenario has no sample output")

    for scenario_id, output in outputs.items():
        scenario = scenarios.get(scenario_id)
        if scenario is None:
            failures.append(f"{scenario_id}: no matching scenario")
            continue

        output_eval = scenario.get("output_eval")
        if not output_eval:
            failures.append(f"{scenario_id}: scenario has no output_eval block")
            continue

        for needle in output_eval.get("required_substrings", []):
            if needle not in output:
                failures.append(f"{scenario_id}: missing required substring {needle!r}")

        for needle in output_eval.get("forbidden_substrings", []):
            if needle in output:
                failures.append(f"{scenario_id}: contains forbidden substring {needle!r}")

        for rule in output_common_rules(scenario):
            failures.extend(evaluate_common_rule(scenario_id, scenario, output, rule))

    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenarios",
        nargs="+",
        type=Path,
        default=DEFAULT_SCENARIOS,
        help="Scenario YAML files with output_eval blocks.",
    )
    parser.add_argument(
        "--outputs",
        type=Path,
        default=DEFAULT_OUTPUTS,
        help="YAML file mapping scenario ids to sample outputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scenario_paths = [path if path.is_absolute() else ROOT / path for path in args.scenarios]
    output_path = args.outputs if args.outputs.is_absolute() else ROOT / args.outputs

    scenarios = collect_scenarios(scenario_paths)
    outputs = load_outputs(output_path)
    failures = evaluate_outputs(scenarios, outputs)

    if failures:
        print("FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"PASS {len(outputs)} outputs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
