#!/usr/bin/env python3
"""Static contract checks for the beopsuny skill docs.

These checks do not prove legal correctness. They catch structural drift in the
skill instructions: stale packaging metadata, old contract-review guidance, and
missing fallback boundaries that previously caused inconsistent agent behavior.
"""

from __future__ import annotations

import json
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_yaml(path: str) -> Any:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_json(path: str) -> Any:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)


def skill_frontmatter() -> dict[str, Any]:
    text = read_text("skills/beopsuny/SKILL.md")
    match = re.match(r"---\n(.*?)\n---\n", text, flags=re.S)
    if not match:
        raise AssertionError("skills/beopsuny/SKILL.md frontmatter missing")
    return yaml.safe_load(match.group(1))


def assert_contains(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"{label}: missing {needle!r}")


def assert_not_contains(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"{label}: stale or forbidden text still present: {needle!r}")


def check_version_sync() -> None:
    plugin = load_json(".claude-plugin/plugin.json")
    marketplace = load_json(".claude-plugin/marketplace.json")

    values = {
        ".claude-plugin/plugin.json version": str(plugin["version"]),
        ".claude-plugin/marketplace.json plugins[0].version": str(marketplace["plugins"][0]["version"]),
    }
    if len(set(values.values())) != 1:
        raise AssertionError(f"version drift: {values}")


def check_skill_frontmatter_minimal() -> None:
    frontmatter = skill_frontmatter()
    if frontmatter.get("name") != "beopsuny":
        raise AssertionError(f"unexpected skill name: {frontmatter.get('name')!r}")
    description = str(frontmatter.get("description", ""))
    for required in ["한국 법령", "계약", "컴플라이언스", "기억만으로 답하지 않는다"]:
        if required not in description:
            raise AssertionError(f"SKILL.md description missing {required!r}")
    if "metadata" in frontmatter:
        raise AssertionError("SKILL.md frontmatter metadata should stay in plugin metadata")


def check_contract_review_guide() -> None:
    text = read_text("skills/beopsuny/references/contract_review_guide.md")
    label = "contract_review_guide.md"

    for stale in [
        "법순이 명령어",
        "계약서 자동 분석/위험도 점수",
        "수정안 자동 생성",
        "### 법순이가 하지 않는 것",
    ]:
        assert_not_contains(text, stale, label)

    for required in [
        "Source Grade",
        "verification status",
        "review_mode.yaml",
        "Counter-drafting",
        "확정 문구가 아니라 검토 힌트",
        "자가 검증",
    ]:
        assert_contains(text, required, label)


def check_source_access_fallbacks() -> None:
    text = read_text("skills/beopsuny/references/source-access.md")
    label = "source-access.md"

    for required in [
        "Capability Matrix",
        "로컬 데이터 없음",
        "법망 API 접근 불가",
        "WebSearch 없음",
        "네트워크 없음",
        "[INSUFFICIENT]",
    ]:
        assert_contains(text, required, label)


def check_output_contract_right_sizing() -> None:
    text = read_text("skills/beopsuny/SKILL.md")
    label = "SKILL.md"

    for required in [
        "출력 크기 조절",
        "검토 메모",
        "compact",
        "full",
        "법률 결론",
        "비법률 운영 응답",
    ]:
        assert_contains(text, required, label)


def check_self_verification_guardrails() -> None:
    text = read_text("skills/beopsuny/references/self-verification.md")
    label = "self-verification.md"

    for required in [
        "사용자 전제 검증",
        "Retrieved Content Trust",
        "검토 대상 데이터",
        "긴 입력의 읽은 범위",
        "데이터 무결성 이슈",
    ]:
        assert_contains(text, required, label)


def check_output_reviewer_note_lite() -> None:
    text = read_text("skills/beopsuny/references/output-formats.md")
    label = "output-formats.md"

    for required in [
        "검토 메모 Lite",
        "출처 provenance",
        "legalize-kr 로컬 확인",
        "법망 API 확인",
        "web — verify",
    ]:
        assert_contains(text, required, label)


def check_router_scenario_references() -> None:
    data = load_yaml("tests/scenarios/16_router_regression.yaml")
    refs = data.get("global_rules", {}).get("mandatory_references", {})
    expected = {
        "source_grade": "skills/beopsuny/references/source-grading.md",
        "self_verification": "skills/beopsuny/references/self-verification.md",
        "source_access": "skills/beopsuny/references/source-access.md",
    }
    if refs != expected:
        raise AssertionError(f"router mandatory references drift: {refs!r}")


def check_router_guardrail_scenarios() -> None:
    data = load_yaml("tests/scenarios/16_router_regression.yaml")
    scenario_ids = {scenario.get("id") for scenario in data.get("scenarios", [])}
    expected = {"router-07", "router-08", "router-09"}
    missing = expected - scenario_ids
    if missing:
        raise AssertionError(f"router guardrail scenarios missing: {sorted(missing)!r}")


def check_router_output_eval() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "tests/evaluate_scenario_outputs.py")],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        details = "\n".join(part for part in [result.stdout, result.stderr] if part)
        raise AssertionError(details.strip())


def check_optional_installed_skill_drift() -> None:
    installed = os.environ.get("BEOPSUNY_INSTALLED_SKILL_PATH")
    if not installed:
        return

    installed_path = Path(installed).expanduser()
    repo_skill_dir = ROOT / "skills/beopsuny"
    if installed_path.is_file():
        installed_path = installed_path.parent
    if not installed_path.exists() or not installed_path.is_dir():
        raise AssertionError(f"installed skill path does not exist: {installed_path}")

    repo_fingerprint = directory_fingerprint(repo_skill_dir)
    installed_fingerprint = directory_fingerprint(installed_path)
    if installed_fingerprint != repo_fingerprint:
        raise AssertionError(
            "installed skill content drift: "
            f"repo={repo_fingerprint}, installed={installed_fingerprint}, path={installed_path}"
        )


def directory_fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    for file_path in sorted(p for p in path.rglob("*") if p.is_file()):
        relative = file_path.relative_to(path).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


CHECKS = [
    check_version_sync,
    check_skill_frontmatter_minimal,
    check_contract_review_guide,
    check_source_access_fallbacks,
    check_output_contract_right_sizing,
    check_self_verification_guardrails,
    check_output_reviewer_note_lite,
    check_router_scenario_references,
    check_router_guardrail_scenarios,
    check_router_output_eval,
    check_optional_installed_skill_drift,
]


def main() -> int:
    failures: list[str] = []
    for check in CHECKS:
        try:
            check()
        except Exception as exc:  # noqa: BLE001 - print all contract failures.
            failures.append(f"{check.__name__}: {exc}")

    if failures:
        print("FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
