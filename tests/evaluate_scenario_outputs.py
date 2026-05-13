#!/usr/bin/env python3
"""Evaluate sample skill outputs against scenario-level string checks.

This is a lightweight harness, not a legal-correctness judge. It lets scenario
fixtures pin concrete output guardrails such as required reviewer-note text,
source-status tags, and forbidden unsafe phrases.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENARIOS = [ROOT / "tests/scenarios/16_router_regression.yaml"]
DEFAULT_OUTPUTS = ROOT / "tests/fixtures/router_guardrail_outputs.yaml"


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
