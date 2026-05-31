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
from datetime import date
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


def freshness_debt_registry() -> dict[str, Any]:
    data = load_yaml("skills/beopsuny/assets/policies/freshness_debt.yaml")
    if not isinstance(data, dict):
        raise AssertionError("freshness_debt.yaml: expected mapping")
    return data


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


QUALITY_CONTRACT_REFERENCES = {
    "README.md": [
        ("skills/beopsuny/references/research-workflow.md", "legal-verification-core"),
        ("skills/beopsuny/assets/schemas/legal_verification_packet.yaml", None),
        ("skills/beopsuny/references/self-verification.md", None),
        ("skills/beopsuny/references/source-grading.md", None),
        ("skills/beopsuny/assets/policies/source_grades.yaml", None),
        ("skills/beopsuny/references/freshness-governance.md", None),
        ("skills/beopsuny/assets/policies/freshness_debt.yaml", None),
        ("skills/beopsuny/assets/schemas/freshness_revalidation.yaml", None),
        ("skills/beopsuny/references/source-access.md", "freshness-gate"),
        ("skills/beopsuny/references/output-formats.md", None),
        ("skills/beopsuny/assets/schemas/output_contract.yaml", None),
        ("skills/beopsuny/references/self-verification.md", "role--destination-gate"),
        ("skills/beopsuny/references/memory-structure.md", None),
        ("skills/beopsuny/assets/schemas/company_profile.yaml", None),
        ("skills/beopsuny/assets/schemas/practice_profile.yaml", None),
        ("skills/beopsuny/references/bulk-tabular-review.md", None),
        ("tests/validate_skill_contracts.py", None),
        ("tests/scenarios/16_router_regression.yaml", None),
        ("tests/evaluate_scenario_outputs.py", None),
        (".github/workflows/contract-tests.yml", None),
    ],
}


def markdown_heading_slugs(text: str) -> set[str]:
    slugs: set[str] = set()
    counts: dict[str, int] = {}

    for line in text.splitlines():
        match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        heading = re.sub(r"`([^`]*)`", r"\1", match.group(1)).strip().lower()
        heading = re.sub(r"<[^>]+>", "", heading)
        heading = re.sub(r"[^\w\s가-힣-]", "", heading)
        slug = re.sub(r"\s", "-", heading)
        duplicate_count = counts.get(slug, 0)
        counts[slug] = duplicate_count + 1
        if duplicate_count:
            slug = f"{slug}-{duplicate_count}"
        slugs.add(slug)

    return slugs


def yaml_file_count(path: str) -> int:
    return sum(1 for item in (ROOT / path).glob("*.yaml") if item.is_file())


def defined_check_functions() -> set[str]:
    text = read_text("tests/validate_skill_contracts.py")
    return set(re.findall(r"^def (check_[a-zA-Z0-9_]+)\(", text, flags=re.M))


def evaluator_rule_names() -> set[str]:
    text = read_text("tests/evaluate_scenario_outputs.py")
    return set(re.findall(r'if rule == "([^"]+)"', text))


def router_scenario_ids() -> set[str]:
    data = load_yaml("tests/scenarios/16_router_regression.yaml")
    return {
        str(scenario.get("id"))
        for scenario in data.get("scenarios", [])
        if isinstance(scenario, dict) and scenario.get("id")
    }


def router_scenarios() -> dict[str, dict[str, Any]]:
    data = load_yaml("tests/scenarios/16_router_regression.yaml")
    scenarios: dict[str, dict[str, Any]] = {}
    for scenario in data.get("scenarios", []):
        if not isinstance(scenario, dict):
            raise AssertionError(f"router scenario must be a mapping: {scenario!r}")
        scenario_id = str(scenario.get("id", ""))
        if not scenario_id:
            raise AssertionError("router scenario missing id")
        if scenario_id in scenarios:
            raise AssertionError(f"duplicate router scenario id: {scenario_id}")
        scenarios[scenario_id] = scenario
    return scenarios


def router_output_eval_ids() -> set[str]:
    return {
        scenario_id
        for scenario_id, scenario in router_scenarios().items()
        if scenario.get("output_eval")
    }


def forward_eval_prompts() -> dict[str, Any]:
    data = load_yaml("tests/forward_evals/beopsuny_guardrails.yaml")
    if not isinstance(data, dict):
        raise AssertionError("beopsuny_guardrails.yaml: expected mapping")
    return data


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


def check_skill_router_schema_references_precise() -> None:
    text = read_text("skills/beopsuny/SKILL.md")
    label = "SKILL.md"

    assert_not_contains(text, "`assets/schemas/*.yaml`", label)
    for required in [
        "`memory_profile`",
        "assets/schemas/company_profile.yaml",
        "assets/schemas/practice_profile.yaml",
        "assets/schemas/past_reviews.yaml",
        "assets/schemas/watched_laws.yaml",
        "assets/schemas/compliance_status.yaml",
        "assets/schemas/internal_rules.yaml",
    ]:
        assert_contains(text, required, label)

    memory_row = next(
        (line for line in text.splitlines() if line.startswith("| `memory_profile` |")),
        "",
    )
    if not memory_row:
        raise AssertionError(f"{label}: memory_profile router row missing")
    for forbidden in [
        "legal_verification_packet.yaml",
        "freshness_revalidation.yaml",
        "output_contract.yaml",
    ]:
        assert_not_contains(memory_row, forbidden, "memory_profile router row")


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
        "Proportionality",
        "Destination",
        "상대방 송부용",
        "확정 문구가 아니라 검토 힌트",
        "자가 검증",
        "회사 playbook 적용",
        "playbook은 결론 근거가 아니라 고객 맥락",
        "법령 근거 우선",
    ]:
        assert_contains(text, required, label)


def check_memory_profile_workflow() -> None:
    text = read_text("skills/beopsuny/references/memory-structure.md")
    label = "memory-structure.md"

    for required in [
        "Quick / Full 온보딩",
        "quick 온보딩",
        "full 온보딩",
        "canonical shape는 nested `company:` 섹션이 아니라 top-level 필드",
        "변호사",
        "`lawyer`",
        "법무 담당자",
        "`legal_ops`",
        "`customer`",
        "`supplier`",
        "`gap`",
        "`eul`",
        "저장 전에는 요약을 보여주고",
        "evidence-based onboarding",
        "stated position",
        "signed practice",
        "skipped field",
        "escalation 판단 기준 또는 표시 조건",
        "자동 알림·라우팅·티켓 생성을 뜻하지 않는다",
        "역할별 gate",
        "`business_user`",
        "법적 효과 gate",
        "Persisted memory trust boundary",
        "검토 대상 데이터",
        "프로젝트 workspace 경계",
        "cross-project context 기본값은 `off`",
        "overrides.party_position.default",
        "per_clause_override",
        "글로벌 (`~/.beopsuny/verification_log.jsonl`)",
        "비기밀 reusable legal-source fact",
        "matter-specific fact",
        "verification_log.jsonl",
        "Source Grade A/B는 현재 세션에서",
        "project.yaml.confidentiality: \"heightened\"",
        "freshness_days",
        "Lite 모드에서는 파일에 쓰지 않고 대화 내 확인",
    ]:
        assert_contains(text, required, label)
    assert_not_contains(text, "자동 escalation trigger", label)


def check_company_profile_playbook_schema() -> None:
    data = load_yaml("skills/beopsuny/assets/schemas/company_profile.yaml")
    text = read_text("skills/beopsuny/assets/schemas/company_profile.yaml")

    for key in ["company_name", "user_role", "interested_laws", "party_position", "contract_playbook"]:
        if key not in data:
            raise AssertionError(f"company_profile.yaml: missing top-level key {key!r}")
    party_position = data["party_position"]
    if not isinstance(party_position, dict):
        raise AssertionError("company_profile.yaml: party_position must be a mapping")
    if set(party_position) != {"default", "per_clause_override"}:
        raise AssertionError(f"company_profile.yaml: unexpected party_position shape {party_position!r}")
    if party_position["default"] not in {"gap", "eul", ""}:
        raise AssertionError("company_profile.yaml: party_position.default must be gap/eul/empty")
    if not isinstance(party_position["per_clause_override"], dict):
        raise AssertionError("company_profile.yaml: party_position.per_clause_override must be a mapping")
    for required in [
        "lawyer | legal_ops | business_user | unknown",
        "customer | supplier | platform | unknown",
        '"gap" / "eul" / ""',
    ]:
        assert_contains(text, required, "company_profile.yaml")
    if "contract_playbook" not in data:
        raise AssertionError("company_profile.yaml: missing contract_playbook")
    playbook = data["contract_playbook"]
    for key in [
        "default_role",
        "risk_posture",
        "standard_positions",
        "acceptable_fallbacks",
        "never_accept",
        "escalation_triggers",
        "seed_documents",
    ]:
        if key not in playbook:
            raise AssertionError(f"company_profile.yaml: contract_playbook missing {key!r}")
    if "user_role" not in data:
        raise AssertionError("company_profile.yaml: missing user_role")


def check_practice_profile_overlay_schema() -> None:
    data = load_yaml("skills/beopsuny/assets/schemas/practice_profile.yaml")
    text = read_text("skills/beopsuny/assets/schemas/practice_profile.yaml")
    label = "practice_profile.yaml"

    for key in [
        "practice",
        "version",
        "jurisdiction_scope",
        "allowed_scope",
        "merge_order",
        "cannot_override",
        "conflict_handling",
        "metadata",
    ]:
        if key not in data:
            raise AssertionError(f"{label}: missing top-level key {key!r}")

    jurisdiction_scope = data["jurisdiction_scope"]
    if not isinstance(jurisdiction_scope, dict):
        raise AssertionError(f"{label}: jurisdiction_scope must be a mapping")
    if jurisdiction_scope.get("primary") != "KR":
        raise AssertionError(f"{label}: primary jurisdiction must default to KR")
    if not isinstance(jurisdiction_scope.get("secondary"), list):
        raise AssertionError(f"{label}: jurisdiction_scope.secondary must be a list")

    allowed_scope = data["allowed_scope"]
    if not isinstance(allowed_scope, dict):
        raise AssertionError(f"{label}: allowed_scope must be a mapping")
    for key in [
        "output_preferences",
        "issue_sequence",
        "escalation_thresholds",
        "repeated_questions",
        "external_counsel_handoff",
    ]:
        if key not in allowed_scope:
            raise AssertionError(f"{label}: allowed_scope missing {key!r}")

    merge_order = data["merge_order"]
    if not isinstance(merge_order, list):
        raise AssertionError(f"{label}: merge_order must be a list")
    for required in [
        "SKILL.md",
        "current user request",
        "source grade and live verification",
        "project.yaml overrides",
        "profile.yaml shared company facts",
        "practice profile output preferences",
    ]:
        if required not in merge_order:
            raise AssertionError(f"{label}: merge_order missing {required!r}")

    cannot_override = data["cannot_override"]
    if not isinstance(cannot_override, list):
        raise AssertionError(f"{label}: cannot_override must be a list")
    for required in [
        "SKILL.md instructions",
        "Source Grade / VERIFIED contract",
        "Legal Verification Core",
        "Freshness Governance",
        "Role / destination output gate",
        "current Korean law, precedent, regulation, or official source",
    ]:
        if required not in cannot_override:
            raise AssertionError(f"{label}: cannot_override missing {required!r}")

    for required in [
        "업무별 practice profile template",
        "회사 사실의 기준이 아니다",
        "한국법 결론과 분리",
        "자동 알림·라우팅 아님",
        "apply_role_destination_gate",
        "apply_freshness_governance",
        "continue_without_practice_profile",
    ]:
        assert_contains(text, required, label)


def check_legal_verification_packet_schema() -> None:
    data = load_yaml("skills/beopsuny/assets/schemas/legal_verification_packet.yaml")
    text = read_text("skills/beopsuny/assets/schemas/legal_verification_packet.yaml")
    label = "legal_verification_packet.yaml"

    for key in [
        "matter",
        "issue_to_authority_map",
        "authority_packets",
        "citation_ledger",
        "contradiction_scan",
        "conclusion_binding",
        "self_verification",
    ]:
        if key not in data:
            raise AssertionError(f"{label}: missing top-level key {key!r}")

    matter = data["matter"]
    if not isinstance(matter, dict):
        raise AssertionError(f"{label}: matter must be a mapping")
    jurisdiction = matter.get("jurisdiction")
    if not isinstance(jurisdiction, dict):
        raise AssertionError(f"{label}: matter.jurisdiction must be a mapping")
    if jurisdiction.get("primary") != "KR":
        raise AssertionError(f"{label}: primary jurisdiction must default to KR")
    if not isinstance(jurisdiction.get("secondary"), list):
        raise AssertionError(f"{label}: jurisdiction.secondary must be a list")
    for required in ["question", "user_role", "destination"]:
        if required not in matter:
            raise AssertionError(f"{label}: matter missing {required!r}")

    issue = first_mapping(data["issue_to_authority_map"], label, "issue_to_authority_map")
    for required in [
        "issue_id",
        "conclusion_candidate",
        "required_authority",
        "legal_effect",
        "must_not_conclude_without",
    ]:
        if required not in issue:
            raise AssertionError(f"{label}: issue_to_authority_map entry missing {required!r}")
    if not isinstance(issue["required_authority"], list):
        raise AssertionError(f"{label}: required_authority must be a list")

    packet = first_mapping(data["authority_packets"], label, "authority_packets")
    if "issue_id" not in packet or "authorities" not in packet:
        raise AssertionError(f"{label}: authority packet must contain issue_id and authorities")
    authority = first_mapping(packet["authorities"], label, "authority_packets.authorities")
    for required in [
        "authority_id",
        "type",
        "citation",
        "pinpoint",
        "source_grade",
        "verification_status",
        "provenance",
        "currency",
        "retrieved_at",
        "supports",
        "limitations",
    ]:
        if required not in authority:
            raise AssertionError(f"{label}: authority entry missing {required!r}")

    ledger = first_mapping(data["citation_ledger"], label, "citation_ledger")
    for required in [
        "citation_id",
        "authority_id",
        "citation",
        "pinpoint",
        "source_grade",
        "verification_status",
        "provenance",
        "currency",
        "supports",
        "output_allowed",
    ]:
        if required not in ledger:
            raise AssertionError(f"{label}: citation ledger entry missing {required!r}")
    if ledger["output_allowed"] is not False:
        raise AssertionError(f"{label}: output_allowed must default to false")

    scan = data["contradiction_scan"]
    if not isinstance(scan, dict):
        raise AssertionError(f"{label}: contradiction_scan must be a mapping")
    if "checked" not in scan or "conflicts" not in scan:
        raise AssertionError(f"{label}: contradiction_scan missing checked/conflicts")

    binding = first_mapping(data["conclusion_binding"], label, "conclusion_binding")
    for required in ["issue_id", "conclusion_strength", "binding_reason", "required_next_check"]:
        if required not in binding:
            raise AssertionError(f"{label}: conclusion_binding entry missing {required!r}")

    self_check = data["self_verification"]
    if not isinstance(self_check, dict):
        raise AssertionError(f"{label}: self_verification must be a mapping")
    for required in [
        "source_grade_applied",
        "ledger_covers_output_citations",
        "freshness_gate_checked",
        "role_destination_gate_checked",
        "no_unledgered_citation_in_output",
        "unresolved_limits",
    ]:
        if required not in self_check:
            raise AssertionError(f"{label}: self_verification missing {required!r}")

    for required in [
        "Legal Verification Core packet template",
        "not a required user-facing output",
        "한국법 결론과 분리",
        "[VERIFIED]",
        "[INSUFFICIENT]",
        "[CONTRADICTED]",
        "[STALE]",
        "[EDITORIAL]",
        "external_send",
        "role_destination_gate_checked",
    ]:
        assert_contains(text, required, label)


def check_freshness_revalidation_schema() -> None:
    data = load_yaml("skills/beopsuny/assets/schemas/freshness_revalidation.yaml")
    text = read_text("skills/beopsuny/assets/schemas/freshness_revalidation.yaml")
    label = "freshness_revalidation.yaml"

    for key in [
        "asset_path",
        "checked_at",
        "checked_by",
        "tracked_issue",
        "source_families_checked",
        "official_sources",
        "volatile_items_checked",
        "asset_update",
        "retirement_decision",
        "self_check",
    ]:
        if key not in data:
            raise AssertionError(f"{label}: missing top-level key {key!r}")

    if not isinstance(data["source_families_checked"], list) or not data["source_families_checked"]:
        raise AssertionError(f"{label}: source_families_checked must be a non-empty list")

    official_source = first_mapping(data["official_sources"], label, "official_sources")
    for required in ["title", "url", "source_grade", "verification_status", "retrieved_at", "notes"]:
        if required not in official_source:
            raise AssertionError(f"{label}: official_sources entry missing {required!r}")

    volatile_item = first_mapping(data["volatile_items_checked"], label, "volatile_items_checked")
    for required in ["item", "previous_value", "refreshed_value", "source_ref", "result"]:
        if required not in volatile_item:
            raise AssertionError(f"{label}: volatile_items_checked entry missing {required!r}")

    asset_update = data["asset_update"]
    if not isinstance(asset_update, dict):
        raise AssertionError(f"{label}: asset_update must be a mapping")
    for required in [
        "updated",
        "maintenance_next_review_before",
        "maintenance_next_review_after",
        "summary",
    ]:
        if required not in asset_update:
            raise AssertionError(f"{label}: asset_update missing {required!r}")

    decision = data["retirement_decision"]
    if not isinstance(decision, dict):
        raise AssertionError(f"{label}: retirement_decision must be a mapping")
    for required in ["decision", "reason", "remaining_stale_scope"]:
        if required not in decision:
            raise AssertionError(f"{label}: retirement_decision missing {required!r}")

    self_check = data["self_check"]
    if not isinstance(self_check, dict):
        raise AssertionError(f"{label}: self_check must be a mapping")
    for required in [
        "official_source_used",
        "volatile_items_reviewed",
        "next_review_advanced",
        "freshness_debt_updated",
        "no_current_obligation_from_stale_only",
    ]:
        if required not in self_check:
            raise AssertionError(f"{label}: self_check missing {required!r}")
    if self_check["no_current_obligation_from_stale_only"] is not True:
        raise AssertionError(f"{label}: no_current_obligation_from_stale_only must default to true")

    for required in [
        "Freshness revalidation event template",
        "required before retiring an entry from freshness_debt.yaml",
        "law.go.kr",
        "competent_ministry",
        "deadline",
        "filing_requirement",
        "retire",
        "partial_refresh",
        "keep_registered",
    ]:
        assert_contains(text, required, label)


def check_output_contract_schema() -> None:
    data = load_yaml("skills/beopsuny/assets/schemas/output_contract.yaml")
    text = read_text("skills/beopsuny/assets/schemas/output_contract.yaml")
    label = "output_contract.yaml"

    for key in ["role_modes", "destinations", "legal_effect_triggers", "non_overrides"]:
        if key not in data:
            raise AssertionError(f"{label}: missing top-level key {key!r}")

    role_modes = data["role_modes"]
    if not isinstance(role_modes, list):
        raise AssertionError(f"{label}: role_modes must be a list")
    roles = {item.get("role") for item in role_modes if isinstance(item, dict)}
    expected_roles = {"lawyer", "legal_ops", "business_user", "unknown"}
    if roles != expected_roles:
        raise AssertionError(f"{label}: unexpected role set {roles!r}")
    for role in role_modes:
        if not isinstance(role, dict):
            raise AssertionError(f"{label}: role entry must be a mapping: {role!r}")
        for required in [
            "role",
            "default_destination",
            "default_sections",
            "legal_effect_gate",
            "must_include",
            "must_not",
        ]:
            if required not in role:
                raise AssertionError(f"{label}: role entry missing {required!r}: {role!r}")
        if not isinstance(role["default_sections"], list) or not role["default_sections"]:
            raise AssertionError(f"{label}: role {role['role']} must define default_sections")

    destinations = data["destinations"]
    if not isinstance(destinations, list):
        raise AssertionError(f"{label}: destinations must be a list")
    destination_map = {
        item.get("destination"): item
        for item in destinations
        if isinstance(item, dict)
    }
    expected_destinations = {
        "internal_legal_memo",
        "business_summary",
        "executive_report",
        "external_draft",
        "agency_or_court_submission",
    }
    if set(destination_map) != expected_destinations:
        raise AssertionError(f"{label}: unexpected destination set {set(destination_map)!r}")
    for destination, item in destination_map.items():
        for required in [
            "destination",
            "may_include_internal_blocks",
            "required_gate",
            "must_include",
            "must_strip",
        ]:
            if required not in item:
                raise AssertionError(f"{label}: destination {destination} missing {required!r}")

    external_draft = destination_map["external_draft"]
    if external_draft.get("may_include_internal_blocks") is not False:
        raise AssertionError(f"{label}: external_draft must not include internal blocks")
    for required in ["검토자 메모", "자가 검증", "internal scratchpad"]:
        if required not in external_draft.get("must_strip", []):
            raise AssertionError(f"{label}: external_draft must strip {required!r}")

    agency_submission = destination_map["agency_or_court_submission"]
    if agency_submission.get("may_include_internal_blocks") is not False:
        raise AssertionError(f"{label}: agency_or_court_submission must not include internal blocks")
    if "review before submission" not in agency_submission.get("must_include", []):
        raise AssertionError(f"{label}: agency_or_court_submission must require review before submission")

    triggers = data["legal_effect_triggers"]
    if not isinstance(triggers, list):
        raise AssertionError(f"{label}: legal_effect_triggers must be a list")
    for required in [
        "signing",
        "external_send",
        "agency_or_court_submission",
        "contract_acceptance",
        "litigation_position",
        "customer_or_regulator_reply",
    ]:
        if required not in triggers:
            raise AssertionError(f"{label}: legal_effect_triggers missing {required!r}")

    non_overrides = data["non_overrides"]
    if not isinstance(non_overrides, list):
        raise AssertionError(f"{label}: non_overrides must be a list")
    for required in [
        "Legal Verification Core",
        "Source Grade / VERIFIED contract",
        "Freshness Governance",
        "Role / Destination Gate",
        "lawyer/legal_ops review requirement",
        "current user request",
    ]:
        if required not in non_overrides:
            raise AssertionError(f"{label}: non_overrides missing {required!r}")

    for required in [
        "Role and destination output contract template",
        "does not reduce legal verification duties",
        "send as-is",
        "file as-is",
        "sign as-is",
        "보내기 전 법무 검토 필요",
    ]:
        assert_contains(text, required, label)


def first_mapping(value: Any, label: str, field: str) -> dict[str, Any]:
    if not isinstance(value, list) or not value or not isinstance(value[0], dict):
        raise AssertionError(f"{label}: {field} must be a non-empty list of mappings")
    return value[0]


def check_bulk_tabular_review_reference() -> None:
    text = read_text("skills/beopsuny/references/bulk-tabular-review.md")
    label = "bulk-tabular-review.md"

    for required in [
        "대량 표 검토 워크플로",
        "schema 초안 작성",
        "Column Type",
        "`verbatim`",
        "`classify`",
        "`needs_review`",
        "quote/location을 확보하지 못하면",
        'state: "needs_review"',
        'source_grade: ""',
        "`answered`는 quote/location 또는 live Source Grade verification이 있을 때만 허용",
        "Evidence Rule",
        "Output Grid",
        "values table",
        "sources table",
        "Verified column",
        "Normalization Spot-check",
        "quote mismatch",
        "읽은 문서 수",
        "법률 리스크가 있는 column",
        "`contract_review` 또는 `compliance_checklist`",
        "Freshness Rule",
        "stale 후보 데이터를 그대로 `answered`로 승격하지 않는다",
        "`references/source-access.md#freshness-gate`",
        "references/freshness-governance.md",
        "stale_candidate: live source verification required before answering",
        "live source로 재확인한 경우에만 `answered`",
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
        "Freshness Gate",
        "법령 ID, 인허가 요건, 공식 서식, 법정 기한",
        "live source로 재확인",
        "[STALE]",
        "references/freshness-governance.md",
        "assets/policies/freshness_debt.yaml",
        "assets/schemas/freshness_revalidation.yaml",
        "retirement decision",
    ]:
        assert_contains(text, required, label)


def check_checklist_routing_freshness() -> None:
    text = read_text("skills/beopsuny/references/checklist-routing.md")
    label = "checklist-routing.md"

    for required in [
        "체크리스트 YAML은 triage 후보이지 현행 결론 근거가 아니다",
        "`type: checklist`",
        "`type: research_guide`",
        "Freshness Routing",
        "`maintenance.next_review`",
        "`references/source-access.md#freshness-gate`",
        "references/freshness-governance.md",
        "assets/policies/freshness_debt.yaml",
        "live legal research로 재확인",
        "[STALE]",
        "[INSUFFICIENT]",
        "검토자 메모",
        "Currency",
    ]:
        assert_contains(text, required, label)


LIVE_CHECK_CUES = (
    "현행",
    "공식",
    "확인",
    "재확인",
    "검토",
    "후보",
    "live",
    "원문",
    "고시",
    "소관",
    "관할",
    "법령",
    "안내",
)

VOLATILE_TEXT_KEYS = {
    "deadline",
    "punishment",
    "fee",
    "authority",
    "required_documents",
}

VOLATILE_NOTE_KEYWORDS = (
    "처리기간",
    "신고기한",
    "유효기간",
    "보관",
    "교육",
    "과태료",
    "벌금",
    "징역",
    "처벌",
    "영업정지",
    "제재",
    "수수료",
    "서식",
    "구비서류",
)

VOLATILE_LITERAL_RE = re.compile(r"\d|매년|반기|주기|과태료|벌금|징역|처벌|영업정지|제재|수수료|서식|구비서류")


def has_live_check_cue(text: str) -> bool:
    return any(cue in text for cue in LIVE_CHECK_CUES)


def walk_yaml_values(value: Any, path: tuple[str, ...] = ()) -> Any:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = (*path, str(key))
            yield child_path, key, child
            yield from walk_yaml_values(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_yaml_values(child, (*path, str(index)))


def check_volatile_policy_literals_require_live_check() -> None:
    checklist_dir = ROOT / "skills/beopsuny/assets/policies/checklists"
    for path in sorted(checklist_dir.glob("*.yaml")):
        relative = path.relative_to(ROOT).as_posix()
        data = load_yaml(relative)
        if not isinstance(data, dict) or data.get("type") != "checklist":
            continue

        for value_path, key, value in walk_yaml_values(data):
            if not isinstance(value, str):
                continue

            compact_path = ".".join(value_path)
            if key in VOLATILE_TEXT_KEYS and VOLATILE_LITERAL_RE.search(value) and not has_live_check_cue(value):
                raise AssertionError(f"{relative}:{compact_path}: volatile literal must require live check: {value!r}")

            if key not in {"notes", "check_points"} and not any(
                segment in {"notes", "check_points"} for segment in value_path
            ):
                continue
            for line in value.splitlines():
                stripped = line.strip().lstrip("- ").strip('"')
                if not stripped:
                    continue
                if not any(keyword in stripped for keyword in VOLATILE_NOTE_KEYWORDS):
                    continue
                if VOLATILE_LITERAL_RE.search(stripped) and not has_live_check_cue(stripped):
                    raise AssertionError(
                        f"{relative}:{compact_path}: volatile note/checkpoint must require live check: {stripped!r}"
                    )


def check_mandatory_provision_notes_are_candidates() -> None:
    data = load_yaml("skills/beopsuny/assets/policies/mandatory_provisions.yaml")
    if not isinstance(data, dict):
        raise AssertionError("mandatory_provisions.yaml: expected mapping")
    provisions = data.get("provisions")
    if not isinstance(provisions, list):
        raise AssertionError("mandatory_provisions.yaml: provisions must be a list")

    final_terms = ("무효", "위반", "필수", "금지", "불가", "의무")
    for index, provision in enumerate(provisions):
        if not isinstance(provision, dict):
            raise AssertionError(f"mandatory_provisions.yaml: provisions[{index}] must be a mapping")
        note = provision.get("note")
        if not isinstance(note, str):
            raise AssertionError(f"mandatory_provisions.yaml: provisions[{index}].note must be a string")
        if any(term in note for term in final_terms) and not has_live_check_cue(note):
            raise AssertionError(
                "mandatory_provisions.yaml: "
                f"provisions[{index}].note has conclusion-style wording without verification cue: {note!r}"
            )


def check_policy_checklist_runtime_contracts() -> None:
    checklist_dir = ROOT / "skills/beopsuny/assets/policies/checklists"
    for path in sorted(checklist_dir.glob("*.yaml")):
        relative = path.relative_to(ROOT).as_posix()
        data = load_yaml(relative)
        if not isinstance(data, dict):
            raise AssertionError(f"{relative}: expected mapping")

        asset_type = data.get("type")
        if asset_type not in {"checklist", "research_guide"}:
            raise AssertionError(f"{relative}: unsupported type {asset_type!r}")

        contract = data.get("runtime_contract")
        if not isinstance(contract, dict):
            raise AssertionError(f"{relative}: missing runtime_contract")
        if contract.get("triage_only") is not True:
            raise AssertionError(f"{relative}: runtime_contract.triage_only must be true")
        if contract.get("live_check_required") is not True:
            raise AssertionError(f"{relative}: runtime_contract.live_check_required must be true")
        if not contract.get("verify_with"):
            raise AssertionError(f"{relative}: runtime_contract.verify_with must name official source families")

        expected_output = "candidate_checklist" if asset_type == "checklist" else "investigation_plan"
        if contract.get("output_behavior") != expected_output:
            raise AssertionError(
                f"{relative}: output_behavior must be {expected_output!r} for type {asset_type!r}"
            )

        if asset_type == "checklist":
            volatile_fields = set(contract.get("volatile_fields") or [])
            for required in ["deadline", "penalty", "threshold", "fee", "form", "authority"]:
                if required not in volatile_fields:
                    raise AssertionError(f"{relative}: volatile_fields missing {required!r}")

        serialized = path.read_text(encoding="utf-8")
        if re.search(r"^\s*law_id\s*:", serialized, flags=re.M):
            raise AssertionError(f"{relative}: checklist policies must not include direct law_id shortcuts")
        if "related_permits" in serialized or re.search(r"\bpermit-\d+\b", serialized):
            raise AssertionError(f"{relative}: stale permit id references must use live-check wording")


def check_mandatory_provisions_candidate_index() -> None:
    text = read_text("skills/beopsuny/assets/policies/mandatory_provisions.yaml")
    label = "mandatory_provisions.yaml"

    for required in [
        "강행규정 후보 인덱스",
        "issue spotting",
        "결론 근거가 아니다",
        "current primary source",
    ]:
        assert_contains(text, required, label)
    assert_not_contains(text, "강행규정 단일 소스", label)


def check_source_grading_verified_contract() -> None:
    text = read_text("skills/beopsuny/references/source-grading.md")
    label = "source-grading.md"

    for required in [
        "VERIFIED 계약",
        "이번 응답에서 해당 법률 사실을 실제 원문 또는 공식 응답으로 대조",
        "Grade와 verification status는 분리",
        "대상 특정",
        "원문 대조",
        "최신성 표시",
        "provenance 표시",
        "법망 API나 WebSearch의 요약·스니펫만 본 경우",
        "`assets/data/*.yaml` 또는 체크리스트 후보만 본 경우",
        "법령 ID, 인허가 요건, 서식, 법정 기한",
        "contradiction scan",
        "conclusion binding",
        "단정 결론으로 쓰지 않는다",
    ]:
        assert_contains(text, required, label)


def check_research_workflow_verification_core() -> None:
    text = read_text("skills/beopsuny/references/research-workflow.md")
    skill_text = read_text("skills/beopsuny/SKILL.md")
    label = "research-workflow.md"

    for required in [
        "Legal Verification Core",
        "assets/schemas/legal_verification_packet.yaml",
        "Verification packet contract",
        "issue-to-authority map",
        "authority packet",
        "citation ledger",
        "contradiction scan",
        "conclusion binding",
        "self-verification",
        "결론 후보",
        "필요한 authority",
        "packet 안의 source가 모두 후보·스니펫·stale 자산이면 결론을 확정하지 않는다",
        "`citation`",
        "`pinpoint`",
        "`source_grade`",
        "`verification_status`",
        "`provenance`",
        "`currency`",
        "`supports`",
        "ledger에 없는 인용은 출력하지 않는다",
        "source가 서로 다르면 숨기지 않는다",
        "[CONTRADICTED]",
        "최종 결론의 강도는 가장 약한 필수 authority에 맞춘다",
        "stale 자산만 있음",
        "triage 후보로만 제시",
        "`matter`",
        "`issue_to_authority_map`",
        "`authority_packets`",
        "`citation_ledger`",
        "`contradiction_scan`",
        "`conclusion_binding`",
        "`self_verification`",
        "`output_allowed: true`가 아닌 ledger 항목",
    ]:
        assert_contains(text, required, label)

    for required in [
        "references/research-workflow.md#legal-verification-core",
        "issue-to-authority map",
        "authority packet",
        "citation ledger",
        "contradiction scan",
        "conclusion binding",
    ]:
        assert_contains(skill_text, required, "SKILL.md")


def parse_review_due(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    if value is None:
        return None
    text = str(value)
    if re.fullmatch(r"\d{4}-\d{2}", text):
        year, month = (int(part) for part in text.split("-"))
        if month == 12:
            return date(year + 1, 1, 1)
        return date(year, month + 1, 1)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        year, month, day = (int(part) for part in text.split("-"))
        return date(year, month, day)
    raise AssertionError(f"unsupported next_review date format: {text!r}")


def check_asset_freshness_metadata_tracked() -> None:
    registry = freshness_debt_registry()
    registered_assets = {
        str(item.get("path"))
        for item in registry.get("assets", [])
        if isinstance(item, dict)
    }
    asset_paths = sorted(
        path
        for path in (ROOT / "skills/beopsuny/assets").rglob("*.yaml")
        if path.is_file()
    )
    stale_untracked: list[str] = []
    today = date.today()

    for path in asset_paths:
        relative = path.relative_to(ROOT).as_posix()
        data = load_yaml(relative)
        if not isinstance(data, dict):
            continue
        maintenance = data.get("maintenance")
        if not isinstance(maintenance, dict):
            continue
        for required in ["review_cycle", "next_review"]:
            if required not in maintenance:
                raise AssertionError(f"{relative}: maintenance missing {required!r}")
        due = parse_review_due(maintenance.get("next_review"))
        if due and due <= today and relative not in registered_assets:
            stale_untracked.append(f"{relative}: next_review={maintenance.get('next_review')}")

    if stale_untracked:
        raise AssertionError(
            "stale asset metadata must be refreshed or explicitly tracked in "
            f"freshness_debt.yaml: {stale_untracked}"
        )


def check_freshness_debt_registry() -> None:
    data = freshness_debt_registry()
    label = "freshness_debt.yaml"

    for required in ["tracked_issue", "policy", "assets"]:
        if required not in data:
            raise AssertionError(f"{label}: missing {required!r}")
    if "issues/101" not in str(data["tracked_issue"]):
        raise AssertionError(f"{label}: tracked_issue must reference issue #101")

    policy = data["policy"]
    if not isinstance(policy, dict):
        raise AssertionError(f"{label}: policy must be a mapping")
    for required in [
        "allowed_runtime_use",
        "required_before_legal_conclusion",
        "forbidden_runtime_use",
        "retirement_rule",
        "revalidation_record_required",
    ]:
        assert_contains(str(policy), required, label)
    if policy.get("allowed_runtime_use") != "triage_only":
        raise AssertionError(f"{label}: allowed_runtime_use must be triage_only")

    assets = data["assets"]
    if not isinstance(assets, list) or not assets:
        raise AssertionError(f"{label}: assets must be a non-empty list")

    today = date.today()
    seen: set[str] = set()
    for item in assets:
        if not isinstance(item, dict):
            raise AssertionError(f"{label}: asset entry must be a mapping: {item!r}")
        for required in [
            "path",
            "status",
            "next_review",
            "risk",
            "allowed_use",
            "verification_required",
            "retire_when",
        ]:
            if not item.get(required):
                raise AssertionError(f"{label}: asset entry missing {required!r}: {item!r}")

        path = str(item["path"])
        if path in seen:
            raise AssertionError(f"{label}: duplicate asset path {path!r}")
        seen.add(path)
        if item["status"] != "stale_registered":
            raise AssertionError(f"{label}: unsupported status for {path}: {item['status']!r}")
        if "triage" not in str(item["allowed_use"]):
            raise AssertionError(f"{label}: {path} allowed_use must keep stale asset triage-only")

        registered_path = ROOT / path
        if not registered_path.exists():
            raise AssertionError(f"{label}: registered asset does not exist: {path}")
        if registered_path.suffix == ".yaml":
            asset_data = load_yaml(path)
            maintenance = asset_data.get("maintenance") if isinstance(asset_data, dict) else None
            if not isinstance(maintenance, dict):
                raise AssertionError(f"{label}: registered asset has no maintenance metadata: {path}")
            if str(maintenance.get("next_review")) != str(item["next_review"]):
                raise AssertionError(
                    f"{label}: {path} next_review drift: registry={item['next_review']!r}, "
                    f"asset={maintenance.get('next_review')!r}"
                )
        elif not path.startswith("skills/beopsuny/references/") or registered_path.suffix != ".md":
            raise AssertionError(f"{label}: non-YAML entries must be reference markdown files: {path}")
        due = parse_review_due(item["next_review"])
        if not due or due > today:
            raise AssertionError(f"{label}: registered asset is not currently stale: {path}")


VOLATILE_REFERENCE_PATTERNS = [
    re.compile(pattern)
    for pattern in [
        r"\d{4}년 기준",
        r"\d{4}년 \d{1,2}월 법 개정",
        r"\d{4}년 개정",
        r"\d+개국",
        r"\d+개 분야",
        r"\d+개 기술",
        r"\d{1,3}(?:,\d{3})*억원",
        r"\d+일 내",
        r"전 세계 매출 \d+%",
        r"\d+(?:\.\d+)?억 유로",
    ]
]


def volatile_reference_hits(path: Path) -> list[str]:
    hits: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if "[STALE]" in line or "뉴스레터" in line:
            continue
        for pattern in VOLATILE_REFERENCE_PATTERNS:
            if pattern.search(line):
                relative = path.relative_to(ROOT).as_posix()
                hits.append(f"{relative}:{line_number}: {line.strip()}")
                break
    return hits


def check_reference_freshness_debt_scan() -> None:
    registry = freshness_debt_registry()
    registered_paths = {
        str(item.get("path"))
        for item in registry.get("assets", [])
        if isinstance(item, dict)
    }
    untracked: list[str] = []

    for path in sorted((ROOT / "skills/beopsuny/references").glob("*.md")):
        relative = path.relative_to(ROOT).as_posix()
        hits = volatile_reference_hits(path)
        if hits and relative not in registered_paths:
            untracked.extend(hits)

    if untracked:
        raise AssertionError(
            "dated volatile reference claims must be removed, reframed as live-check hints, "
            f"or tracked in freshness_debt.yaml: {untracked}"
        )


def check_freshness_governance_reference() -> None:
    text = read_text("skills/beopsuny/references/freshness-governance.md")
    label = "freshness-governance.md"
    registry = freshness_debt_registry()

    for required in [
        "Freshness Governance",
        "assets/policies/freshness_debt.yaml",
        "assets/schemas/freshness_revalidation.yaml",
        "triage_only",
        "Runtime Rule",
        "Verification Before Answering",
        "Debt Register Contract",
        "Revalidation Record",
        "Registered Stale Assets",
        "reference 문서",
        "treaty/source count",
        "Retirement Rule",
        "live legal research",
        "`source_families_checked`",
        "`volatile_items_checked`",
        "`retirement_decision`",
        "`keep_registered`, `retire`, `partial_refresh`",
        "공식 source 없이 사용자 기억, 오래된 뉴스레터, stale 번들 YAML만으로 `retire` 결정을 내리지 않는다",
        "`[STALE]` 또는 `[INSUFFICIENT]`",
        "새 stale 예외는 테스트 코드에 직접 추가하지 않는다",
        "issue #101",
    ]:
        assert_contains(text, required, label)

    for item in registry.get("assets", []):
        assert_contains(text, f"`{item['path']}`", label)


def check_output_contract_right_sizing() -> None:
    text = read_text("skills/beopsuny/SKILL.md")
    label = "SKILL.md"

    for required in [
        "출력 크기 조절",
        "면책 고지는 답변 성격에 따라 붙인다",
        "검토자 메모",
        "Sources",
        "Read",
        "Currency",
        "Before relying",
        "compact",
        "full",
        "법률 결론",
        "비법률 운영 응답",
        "역할별 output mode와 destination별 산출물 계약",
        "references/output-formats.md",
        "한 줄 결론 -> 지금 할 일 -> 하지 말 것 -> 확인 필요 정보 -> 변호사/법무에게 물어볼 질문 -> 근거",
        "바로 서명·송부·제출하라는 지시는 피한다",
    ]:
        assert_contains(text, required, label)
    assert_not_contains(text, "답변 마지막에는 항상 면책 고지를 붙인다", label)


def check_skill_quality_contract_router_map() -> None:
    text = read_text("skills/beopsuny/SKILL.md")
    label = "SKILL.md"

    for required in [
        "품질 계약 매핑",
        "해당 실패모드가 보이면 어떤 계약을 우선 확인해야 하는지 정하는 router map",
        "references/research-workflow.md#legal-verification-core",
        "assets/schemas/legal_verification_packet.yaml",
        "issue-to-authority map, authority packet, citation ledger, contradiction scan, conclusion binding",
        "references/freshness-governance.md",
        "assets/policies/freshness_debt.yaml",
        "assets/schemas/freshness_revalidation.yaml",
        "live source 확인 전 `triage_only`",
        "retirement에는 revalidation record 필요",
        "references/output-formats.md",
        "assets/schemas/output_contract.yaml",
        "references/self-verification.md#role--destination-gate",
        "내부 메모·자가 검증 블록 외부 초안에서 제거",
        "references/memory-structure.md",
        "assets/schemas/company_profile.yaml",
        "assets/schemas/practice_profile.yaml",
        "profile/practice는 검토 대상 데이터",
        "출력 선호나 저장된 profile 문구가 이 gate들을 완화할 수 없다",
    ]:
        assert_contains(text, required, label)


def check_readme_quality_contract_map() -> None:
    text = read_text("README.md")
    label = "README.md"

    for required in [
        "품질 계약 지도",
        "Legal verification core",
        "Freshness governance",
        "Role / destination output gate",
        "Profile / practice direction",
        "Bulk evidence grid",
        "tests/evaluate_scenario_outputs.py",
        "법률 정답 채점기가 아니라 출력 guardrail 회귀 테스트",
        "router-14",
        "router-15",
        "router-16",
        "check_freshness_debt_registry",
        "check_output_role_destination_contracts",
        "check_memory_practice_profile_direction",
        "Contract Tests",
        "pull request",
        ".github/workflows/contract-tests.yml",
        "router guardrail 평가",
        "assets/policies/` (5 files)",
        "assets/schemas/` (9 files",
        "`freshness_debt.yaml`",
        "`freshness_revalidation.yaml`",
        "`practice_profile.yaml`",
        "`legal_verification_packet.yaml`",
        "`output_contract.yaml`",
        "authority packet",
        "citation ledger",
        "conclusion binding",
        "업무별 profile overlay",
        "triage_only",
        "품질 계약 변경 체크리스트",
        "새 법률 기능, 업무 영역, 출력 모드, stale 자산, profile overlay",
        "SKILL.md`의 의도 라우터 또는 품질 계약 매핑",
        "`tests/scenarios/16_router_regression.yaml`",
        "`tests/fixtures/router_guardrail_outputs.yaml`",
        "`tests/evaluate_scenario_outputs.py`",
        "unsafe fixture 또는 guardrail rule",
        "`tests/validate_skill_contracts.py`",
        "README 품질 계약 지도와 CHANGELOG",
        "기존 장점인 단일 라우터, 한국법 원문주의, Source Grade, 자가 검증",
        "새 계약은 기존 gate를 우회하지 말고",
    ]:
        assert_contains(text, required, label)


def check_readme_asset_inventory_counts() -> None:
    text = read_text("README.md")
    label = "README.md"
    expected_counts = {
        "assets/data/": yaml_file_count("skills/beopsuny/assets/data"),
        "assets/policies/": yaml_file_count("skills/beopsuny/assets/policies"),
        "assets/schemas/": yaml_file_count("skills/beopsuny/assets/schemas"),
    }

    for section, expected_count in expected_counts.items():
        pattern = rf"{re.escape(section)}` \({expected_count} files(?:,|\))"
        if not re.search(pattern, text):
            raise AssertionError(f"{label}: {section} inventory count must be {expected_count} files")

    for schema_name in [
        "company_profile.yaml",
        "practice_profile.yaml",
        "legal_verification_packet.yaml",
        "freshness_revalidation.yaml",
        "output_contract.yaml",
        "internal_rules.yaml",
        "past_reviews.yaml",
        "watched_laws.yaml",
        "compliance_status.yaml",
    ]:
        assert_contains(text, f"`{schema_name}`", label)

    for policy_name in [
        "mandatory_provisions.yaml",
        "clause_taxonomy.yaml",
        "review_mode.yaml",
        "source_grades.yaml",
        "freshness_debt.yaml",
    ]:
        assert_contains(text, f"`{policy_name}`", label)


def check_law_change_automation_promise_drift() -> None:
    sensitive_docs = {
        "CLAUDE.md": read_text("CLAUDE.md"),
        "watched_laws.yaml": read_text("skills/beopsuny/assets/schemas/watched_laws.yaml"),
    }
    forbidden_phrases = [
        "법 개정 시 자동 알림",
        "자동 추가",
        "자동으로 추가",
        "자동으로 알려",
        "크론",
        "cron",
        "notification",
        "push",
        "푸시",
        "스케줄",
        "정기적으로 알려",
        "주기적으로 체크",
        "자동 모니터링",
    ]

    for label, text in sensitive_docs.items():
        for phrase in forbidden_phrases:
            assert_not_contains(text, phrase, label)

    watched_laws = sensitive_docs["watched_laws.yaml"]
    for required in [
        "조회 후보",
        "사용자가 저장을 확인한 경우에만 추가",
    ]:
        assert_contains(watched_laws, required, "watched_laws.yaml")

    law_change = read_text("skills/beopsuny/references/law-change-detection.md")
    for required in [
        "법령 변경 감지는 pull 방식이다",
        "사용자가 명시적으로 automation을 요청하지 않으면",
        "이 스킬의 기본 변경 감지와 섞지 않는다",
    ]:
        assert_contains(law_change, required, "law-change-detection.md")


def check_readme_quality_verification_refs_resolve() -> None:
    text = read_text("README.md")
    label = "README.md"
    checks = defined_check_functions()
    rules = evaluator_rule_names()
    scenario_ids = router_scenario_ids()
    table_match = re.search(
        r"\| 품질 계약 \| 기준 문서 \| 회귀 검증 \|\n"
        r"\| --- \| --- \| --- \|\n"
        r"(?P<body>(?:\| .+\n)+)",
        text,
    )
    if not table_match:
        raise AssertionError(f"{label}: quality contract table missing")

    refs: set[str] = set()
    for row in table_match.group("body").splitlines():
        columns = [column.strip() for column in row.strip().strip("|").split("|")]
        if len(columns) != 3:
            raise AssertionError(f"{label}: malformed quality contract row: {row!r}")
        verification_cell = columns[2]
        refs.update(re.findall(r"`([^`]+)`", verification_cell))

    for ref in refs:
        if ref.startswith("tests/"):
            if not (ROOT / ref).exists():
                raise AssertionError(f"{label}: referenced verification file missing: {ref}")
            continue
        if ref.startswith("check_"):
            if ref not in checks:
                raise AssertionError(f"{label}: referenced check function missing: {ref}")
            continue
        if re.fullmatch(r"router-\d+", ref):
            if ref not in scenario_ids:
                raise AssertionError(f"{label}: referenced router scenario missing: {ref}")
            continue
        if ref not in rules:
            raise AssertionError(f"{label}: referenced evaluator rule missing: {ref}")


def check_quality_contract_reference_targets() -> None:
    for source_path, targets in QUALITY_CONTRACT_REFERENCES.items():
        source_text = read_text(source_path)
        for target_path, anchor in targets:
            literal_reference = f"{target_path}#{anchor}" if anchor else target_path
            assert_contains(source_text, literal_reference, source_path)

            resolved = ROOT / target_path
            if not resolved.exists():
                raise AssertionError(f"{source_path}: referenced target does not exist: {target_path}")
            if not anchor:
                continue
            if resolved.suffix.lower() != ".md":
                raise AssertionError(f"{source_path}: anchor target is not markdown: {target_path}#{anchor}")
            slugs = markdown_heading_slugs(resolved.read_text(encoding="utf-8"))
            if anchor not in slugs:
                raise AssertionError(
                    f"{source_path}: anchor #{anchor} not found in {target_path}; "
                    f"available={sorted(slugs)!r}"
                )


def check_changelog_quality_contract_notes() -> None:
    text = read_text("CHANGELOG.md")
    label = "CHANGELOG.md"

    for required in [
        "Legal Verification Core",
        "issue-to-authority map",
        "authority packet",
        "citation ledger",
        "legal_verification_packet.yaml",
        "Freshness Governance",
        "freshness_debt.yaml",
        "freshness_revalidation.yaml",
        "retirement decision",
        "practice_profile.yaml",
        "allowed scope",
        "cannot_override",
        "역할별 output mode",
        "destination output contract",
        "output_contract.yaml",
        "legal_effect_triggers",
        "non_overrides",
        "품질 계약 매핑",
        "memory_profile",
        "assets/schemas/*.yaml",
        "memory 관련 schema만 명시",
        "practice profile direction",
        "router guardrail",
        "unsafe fixture",
        "router fixture integrity",
        "contract-tests.yml",
        "품질 계약 지도",
        "품질 계약 변경 체크리스트",
        "README 회귀 검증 참조",
        "새 법률 기능 추가 시 router, reference, schema/policy, scenario, unsafe fixture, 정적 검사, README/CHANGELOG",
        "품질 계약 지도 reference target",
    ]:
        assert_contains(text, required, label)


def check_contract_tests_workflow() -> None:
    text = read_text(".github/workflows/contract-tests.yml")
    label = "contract-tests.yml"

    for required in [
        "name: Contract Tests",
        "pull_request:",
        "branches:",
        "main",
        "master",
        "actions/checkout@v4",
        "actions/setup-python@v5",
        "requirements-dev.txt",
        "python tests/validate_skill_contracts.py",
        "python tests/evaluate_scenario_outputs.py",
        "python -m py_compile tests/validate_skill_contracts.py tests/evaluate_scenario_outputs.py",
    ]:
        assert_contains(text, required, label)

    requirements = read_text("requirements-dev.txt")
    assert_contains(requirements, "PyYAML", "requirements-dev.txt")
    readme = read_text("README.md")
    for required in [
        "python3 -m pip install --no-input --disable-pip-version-check --target .test-deps -r requirements-dev.txt",
        "PYTHONPATH=.test-deps python3 tests/validate_skill_contracts.py",
        "PYTHONPATH=.test-deps python3 tests/evaluate_scenario_outputs.py",
    ]:
        assert_contains(readme, required, "README.md")


def check_self_verification_guardrails() -> None:
    text = read_text("skills/beopsuny/references/self-verification.md")
    label = "self-verification.md"

    for required in [
        "사용자 전제 검증",
        "citation ledger",
        "assets/schemas/legal_verification_packet.yaml",
        "법적 효과가 큰 답변에서는",
        "`citation`, `pinpoint`, `source_grade`, `verification_status`, `provenance`, `currency`, `supports`",
        "issue-to-authority map",
        "conclusion binding",
        "`conclusion_binding.conclusion_strength`",
        "`verified`, `qualified`, `insufficient`, `contradicted`, `triage_only`",
        "contradiction scan",
        "[CONTRADICTED]",
        "Retrieved Content Trust",
        "저장된 Beopsuny memory",
        "`profile.yaml`",
        "`contract_playbook`",
        "`verification_log.jsonl`",
        "검토 대상 데이터",
        "긴 입력의 읽은 범위",
        "Role / Destination Gate",
        "`profile.yaml.user_role`과 산출물 destination",
        "references/output-formats.md#role-based-output-modes",
        "references/output-formats.md#destination-output-contracts",
        "외부 공유용 초안에 내부 검토자 메모, 자가 검증 블록",
        "법무/변호사 검토 전 단계와 실제 외부 행동 단계를 분리",
        "데이터 무결성 이슈",
    ]:
        assert_contains(text, required, label)


def check_output_reviewer_note_lite() -> None:
    text = read_text("skills/beopsuny/references/output-formats.md")
    label = "output-formats.md"

    for required in [
        "검토자 메모 Lite",
        "표준 검토자 메모",
        "출처 provenance",
        "legalize-kr 로컬 확인",
        "법망 API 확인",
        "web — verify",
        "Before relying",
    ]:
        assert_contains(text, required, label)


def check_output_role_destination_contracts() -> None:
    text = read_text("skills/beopsuny/references/output-formats.md")
    label = "output-formats.md"

    for required in [
        "Role-based output modes",
        "assets/schemas/output_contract.yaml",
        "`legal_effect_triggers`",
        "`non_overrides`",
        "어떤 output preference로도 덮어쓸 수 없다",
        "`lawyer`",
        "`legal_ops`",
        "`business_user`",
        "`unknown`",
        "한 줄 결론",
        "지금 할 일",
        "하지 말 것",
        "확인 필요 정보",
        "변호사/법무에게 물어볼 질문",
        "서명·송부·제출·확정 답변을 바로 지시하지 않고",
        "Source Grade와 verification status를 대체하지 않는다",
        "Destination output contracts",
        "`internal_legal_memo`",
        "`business_summary`",
        "`executive_report`",
        "`external_draft`",
        "`agency_or_court_submission`",
        "`practice_profile.yaml`",
        "practice profile은 출력 선호일 뿐",
        "현재 사용자 요청과 role/destination gate를 우선",
        "내부 검토자 메모와 자가 검증 블록을 그대로 포함하지 않는다",
        "보내기 전 법무 검토 필요",
        "변호사 또는 담당 법무 검토 없이 제출하라고 쓰지 않음",
    ]:
        assert_contains(text, required, label)


def check_memory_practice_profile_direction() -> None:
    text = read_text("skills/beopsuny/references/memory-structure.md")
    label = "memory-structure.md"

    for required in [
        "Practice profile direction",
        "Practice Profile Contract",
        "assets/schemas/practice_profile.yaml",
        "shared company profile",
        "`~/.beopsuny/profile.yaml`",
        "practice profiles",
        "`~/.beopsuny/practices/{contract,privacy,labor,regulatory,litigation}.yaml`",
        "allowed scope",
        "Practice profile merge order",
        "cannot_override",
        "`jurisdiction_scope.primary`의 기본값은 `KR`",
        "해외법 source도 별도 Source Grade와 verification status",
        "practice profile 안의 destination 기본값이 `external_draft`",
        "role/destination gate는 그대로 적용",
        "회사 사실을 복제하지 않고",
        "검토 대상 데이터",
        "SKILL.md, Source Grade, 자가 검증, 현행 법령 확인을 덮어쓸 수 없다",
        "top-level `profile.yaml`과 `contract_playbook`을 유지",
        "cold-start full onboarding",
        "업무별 출력 선호와 escalation 기준",
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
    expected = {
        "router-07",
        "router-08",
        "router-09",
        "router-10",
        "router-11",
        "router-12",
        "router-13",
        "router-14",
        "router-15",
        "router-16",
    }
    missing = expected - scenario_ids
    if missing:
        raise AssertionError(f"router guardrail scenarios missing: {sorted(missing)!r}")


def check_router_fixture_integrity() -> None:
    scenarios = router_scenarios()
    evaluator_rules = evaluator_rule_names()
    expected_output_ids = router_output_eval_ids()
    expected_guardrail_ids = {
        "router-07",
        "router-08",
        "router-09",
        "router-10",
        "router-11",
        "router-12",
        "router-13",
        "router-14",
        "router-15",
        "router-16",
    }
    if expected_output_ids != expected_guardrail_ids:
        raise AssertionError(
            "router output_eval coverage drift: "
            f"expected={sorted(expected_guardrail_ids)!r}, actual={sorted(expected_output_ids)!r}"
        )

    for scenario_id in sorted(expected_output_ids):
        scenario = scenarios[scenario_id]
        output_eval = scenario.get("output_eval")
        if not isinstance(output_eval, dict):
            raise AssertionError(f"{scenario_id}: output_eval must be a mapping")
        common_rules = output_eval.get("common_rules", [])
        if not isinstance(common_rules, list) or not common_rules:
            raise AssertionError(f"{scenario_id}: output_eval.common_rules must be a non-empty list")
        missing_rules = sorted(str(rule) for rule in common_rules if str(rule) not in evaluator_rules)
        if missing_rules:
            raise AssertionError(f"{scenario_id}: evaluator missing common rules {missing_rules!r}")

    fixture = load_yaml("tests/fixtures/router_guardrail_outputs.yaml")
    if not isinstance(fixture, dict):
        raise AssertionError("router_guardrail_outputs.yaml: expected mapping")
    description = str(fixture.get("description", ""))
    assert_contains(description, "router-07 through router-16", "router_guardrail_outputs.yaml description")

    outputs = fixture.get("outputs")
    if not isinstance(outputs, dict):
        raise AssertionError("router_guardrail_outputs.yaml: outputs must be a mapping")
    output_ids = {str(key) for key in outputs}
    if output_ids != expected_output_ids:
        raise AssertionError(
            "router_guardrail_outputs.yaml: output ids must exactly match output_eval scenarios: "
            f"expected={sorted(expected_output_ids)!r}, actual={sorted(output_ids)!r}"
        )
    empty_outputs = sorted(scenario_id for scenario_id, output in outputs.items() if not str(output).strip())
    if empty_outputs:
        raise AssertionError(f"router_guardrail_outputs.yaml: empty sample outputs {empty_outputs!r}")

    unsafe_outputs = fixture.get("unsafe_outputs")
    if not isinstance(unsafe_outputs, list) or not unsafe_outputs:
        raise AssertionError("router_guardrail_outputs.yaml: unsafe_outputs must be a non-empty list")

    seen_unsafe_ids: set[str] = set()
    for item in unsafe_outputs:
        if not isinstance(item, dict):
            raise AssertionError(f"router_guardrail_outputs.yaml: unsafe output must be a mapping: {item!r}")
        item_id = str(item.get("id", ""))
        if not item_id:
            raise AssertionError("router_guardrail_outputs.yaml: unsafe output missing id")
        if item_id in seen_unsafe_ids:
            raise AssertionError(f"router_guardrail_outputs.yaml: duplicate unsafe output id {item_id!r}")
        seen_unsafe_ids.add(item_id)

        scenario_id = str(item.get("scenario_id", ""))
        if scenario_id not in expected_output_ids:
            raise AssertionError(
                f"router_guardrail_outputs.yaml: unsafe output {item_id} references "
                f"non-guardrail scenario {scenario_id!r}"
            )
        if not str(item.get("output", "")).strip():
            raise AssertionError(f"router_guardrail_outputs.yaml: unsafe output {item_id} has empty output")

        expected_failure_rules = item.get("expected_failure_rules")
        if not isinstance(expected_failure_rules, list) or not expected_failure_rules:
            raise AssertionError(
                f"router_guardrail_outputs.yaml: unsafe output {item_id} "
                "must define expected_failure_rules"
            )
        scenario_rules = {
            str(rule)
            for rule in scenarios[scenario_id].get("output_eval", {}).get("common_rules", [])
        }
        for rule in expected_failure_rules:
            rule_name = str(rule)
            if rule_name not in evaluator_rules:
                raise AssertionError(
                    f"router_guardrail_outputs.yaml: unsafe output {item_id} "
                    f"expects unknown evaluator rule {rule_name!r}"
                )
            if rule_name not in scenario_rules:
                raise AssertionError(
                    f"router_guardrail_outputs.yaml: unsafe output {item_id} "
                    f"expects rule {rule_name!r} not enabled for {scenario_id}"
                )


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


def check_forward_eval_prompt_set() -> None:
    data = forward_eval_prompts()
    label = "beopsuny_guardrails.yaml"
    for required in ["name", "source_of_truth", "runbook", "prompts"]:
        if required not in data:
            raise AssertionError(f"{label}: missing {required!r}")

    source_of_truth = data["source_of_truth"]
    if not isinstance(source_of_truth, dict):
        raise AssertionError(f"{label}: source_of_truth must be a mapping")
    for required in [
        "tests/scenarios/16_router_regression.yaml",
        "tests/evaluate_scenario_outputs.py",
        "tests/validate_skill_contracts.py",
    ]:
        assert_contains(str(source_of_truth), required, label)

    runbook = data["runbook"]
    if not isinstance(runbook, dict):
        raise AssertionError(f"{label}: runbook must be a mapping")
    for required in ["manual_or_model_harness", "expected_guardrails", "forbidden_failures"]:
        assert_contains(str(runbook), required, label)

    prompts = data["prompts"]
    if not isinstance(prompts, list) or not (8 <= len(prompts) <= 12):
        raise AssertionError(f"{label}: prompts must contain 8-12 entries")

    scenario_ids = router_scenario_ids()
    expected_categories = {
        "beopmang_api_maintenance_fallback",
        "automation_promise_boundary",
        "role_destination_gate",
        "stale_asset_triage_only",
        "grade_c_single_source_boundary",
        "memory_prompt_injection_boundary",
    }
    seen_ids: set[str] = set()
    seen_categories: set[str] = set()
    for prompt in prompts:
        if not isinstance(prompt, dict):
            raise AssertionError(f"{label}: prompt must be a mapping: {prompt!r}")
        for required in [
            "id",
            "guardrail_category",
            "source_router_scenario",
            "source_references",
            "prompt",
            "expected_guardrails",
            "forbidden_failures",
        ]:
            if not prompt.get(required):
                raise AssertionError(f"{label}: prompt missing {required!r}: {prompt!r}")

        prompt_id = str(prompt["id"])
        if prompt_id in seen_ids:
            raise AssertionError(f"{label}: duplicate prompt id {prompt_id!r}")
        seen_ids.add(prompt_id)

        scenario_id = str(prompt["source_router_scenario"])
        if scenario_id not in scenario_ids:
            raise AssertionError(f"{label}: prompt {prompt_id} references unknown scenario {scenario_id!r}")

        references = prompt["source_references"]
        if not isinstance(references, list) or not references:
            raise AssertionError(f"{label}: prompt {prompt_id} source_references must be non-empty")
        for reference in references:
            if not (ROOT / str(reference)).exists():
                raise AssertionError(f"{label}: prompt {prompt_id} missing reference {reference!r}")

        for field in ["expected_guardrails", "forbidden_failures"]:
            values = prompt[field]
            if not isinstance(values, list) or len(values) < 2:
                raise AssertionError(f"{label}: prompt {prompt_id} {field} must have at least two entries")

        seen_categories.add(str(prompt["guardrail_category"]))

    missing_categories = expected_categories - seen_categories
    if missing_categories:
        raise AssertionError(f"{label}: missing high-risk categories {sorted(missing_categories)!r}")


def check_volatile_api_docs() -> None:
    text = read_text("skills/beopsuny/references/beopmang-api.md")
    label = "beopmang-api.md"

    for required in [
        "운영 정보",
        "운영 정보는 변동될 수 있으므로",
        "문서에 고정하지 않는다",
        "help?action=schema",
        "`q`",
        "`law_id`",
        "`article`",
        "`service_maintenance`",
        "조회 실패",
        "개정 없음",
    ]:
        assert_contains(text, required, label)
    for stale in [
        "분당 100회",
        "❌ 503",
        "법령 5,573",
    ]:
        assert_not_contains(text, stale, label)

    docs = {
        "skills/beopsuny/references/beopmang-api.md": read_text(
            "skills/beopsuny/references/beopmang-api.md"
        ),
        "skills/beopsuny/references/source-access.md": read_text(
            "skills/beopsuny/references/source-access.md"
        ),
        "skills/beopsuny/references/law-change-detection.md": read_text(
            "skills/beopsuny/references/law-change-detection.md"
        ),
        "docs/desktop-chat-guide.md": read_text("docs/desktop-chat-guide.md"),
    }
    stale_patterns = [
        "action=search&query=",
        "action=get&id=",
        "action=history&id=",
        "action=diff&id=",
        "case?action=get&id=",
    ]
    failure_terms = ["service_maintenance", "timeout", "5xx", "빈 응답", "조회 실패"]
    for doc_label, doc_text in docs.items():
        for pattern in stale_patterns:
            assert_not_contains(doc_text, pattern, doc_label)
        for required in failure_terms:
            assert_contains(doc_text, required, doc_label)


def check_international_index_routing() -> None:
    skill_text = read_text("skills/beopsuny/SKILL.md")
    guide_text = read_text("skills/beopsuny/references/international_guide.md")

    assert_contains(skill_text, "references/international_guide.md", "SKILL.md")
    assert_contains(guide_text, "별도 router intent가 아니라", "international_guide.md")
    assert_contains(guide_text, "한국법상 확인할 후보 쟁점", "international_guide.md")


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
    check_skill_router_schema_references_precise,
    check_contract_review_guide,
    check_memory_profile_workflow,
    check_company_profile_playbook_schema,
    check_practice_profile_overlay_schema,
    check_legal_verification_packet_schema,
    check_freshness_revalidation_schema,
    check_bulk_tabular_review_reference,
    check_source_access_fallbacks,
    check_checklist_routing_freshness,
    check_policy_checklist_runtime_contracts,
    check_volatile_policy_literals_require_live_check,
    check_mandatory_provisions_candidate_index,
    check_mandatory_provision_notes_are_candidates,
    check_source_grading_verified_contract,
    check_research_workflow_verification_core,
    check_asset_freshness_metadata_tracked,
    check_freshness_debt_registry,
    check_reference_freshness_debt_scan,
    check_freshness_governance_reference,
    check_output_contract_right_sizing,
    check_skill_quality_contract_router_map,
    check_readme_quality_contract_map,
    check_readme_asset_inventory_counts,
    check_law_change_automation_promise_drift,
    check_readme_quality_verification_refs_resolve,
    check_quality_contract_reference_targets,
    check_changelog_quality_contract_notes,
    check_contract_tests_workflow,
    check_self_verification_guardrails,
    check_output_reviewer_note_lite,
    check_output_contract_schema,
    check_output_role_destination_contracts,
    check_memory_practice_profile_direction,
    check_router_scenario_references,
    check_router_guardrail_scenarios,
    check_router_fixture_integrity,
    check_router_output_eval,
    check_forward_eval_prompt_set,
    check_volatile_api_docs,
    check_international_index_routing,
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
