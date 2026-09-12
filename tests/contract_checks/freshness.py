"""Freshness/revalidation contract checks.

Extracted from tests/validate_skill_contracts.py (#335). The entrypoint still
registers these functions in CHECK_GROUPS and runs them via main().
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_yaml(path: str) -> Any:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def assert_contains(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"{label}: missing {needle!r}")


def first_mapping(value: Any, label: str, field: str) -> dict[str, Any]:
    if not isinstance(value, list) or not value or not isinstance(value[0], dict):
        raise AssertionError(f"{label}: {field} must be a non-empty list of mappings")
    return value[0]


_SOURCE_GRADES = load_yaml("skills/beopsuny/assets/policies/source_grades.yaml")
SOURCE_AUTHORITIES = {
    str(item["label"])
    for item in _SOURCE_GRADES["source_classes"].values()
    if isinstance(item, dict) and isinstance(item.get("label"), str)
}
VERIFICATION_STATUSES = set(_SOURCE_GRADES["rules"]["existing_tag_mapping"])


def freshness_debt_registry() -> dict[str, Any]:
    data = load_yaml("skills/beopsuny/assets/policies/freshness_debt.yaml")
    if not isinstance(data, dict):
        raise AssertionError("freshness_debt.yaml: expected mapping")
    return data


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
    for required in ["title", "url", "source_authority", "verification_status", "retrieved_at", "notes"]:
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

REVALIDATION_REQUIRED_FIELDS = [
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
]

REVALIDATION_OFFICIAL_SOURCE_FAMILIES = {
    "agency_notice",
    "beopmang",
    "competent_ministry",
    "court",
    "gov.kr",
    "law.go.kr",
    "local_legalize_kr",
}

REVALIDATION_DECISIONS = {"keep_registered", "retire", "partial_refresh"}
REVALIDATION_ITEM_RESULTS = {"unchanged", "updated", "removed", "insufficient", "contradicted"}

def check_freshness_revalidation_records() -> None:
    registry_paths = {
        str(item.get("path"))
        for item in freshness_debt_registry().get("assets", [])
        if isinstance(item, dict)
    }
    fixtures_dir = ROOT / "tests/fixtures/freshness_revalidations"
    label = "tests/fixtures/freshness_revalidations"
    fixture_paths = sorted(fixtures_dir.glob("*.yaml")) if fixtures_dir.exists() else []
    if not fixture_paths:
        raise AssertionError(f"{label}: add at least one freshness revalidation record fixture")

    for path in fixture_paths:
        relative = path.relative_to(ROOT).as_posix()
        record = load_yaml(relative)
        if not isinstance(record, dict):
            raise AssertionError(f"{relative}: expected mapping")
        for required in REVALIDATION_REQUIRED_FIELDS:
            if required not in record:
                raise AssertionError(f"{relative}: missing {required!r}")

        asset_path = str(record["asset_path"])
        if not (ROOT / asset_path).exists():
            raise AssertionError(f"{relative}: asset_path does not exist: {asset_path}")
        if not re.search(r"/issues/\d+", str(record["tracked_issue"])):
            raise AssertionError(f"{relative}: tracked_issue must reference a GitHub issue URL")

        source_families = record["source_families_checked"]
        if not isinstance(source_families, list) or not source_families:
            raise AssertionError(f"{relative}: source_families_checked must be a non-empty list")
        if not any(str(source) in REVALIDATION_OFFICIAL_SOURCE_FAMILIES for source in source_families):
            raise AssertionError(f"{relative}: source_families_checked must include an official source family")
        forbidden_sources = {"memory", "old_bundled_yaml", "secondary_commentary_only"}
        if any(str(source) in forbidden_sources for source in source_families):
            raise AssertionError(f"{relative}: source_families_checked cannot rely on stale-only evidence")

        official_titles: dict[str, str] = {}
        official_sources = record["official_sources"]
        if not isinstance(official_sources, list) or not official_sources:
            raise AssertionError(f"{relative}: official_sources must be a non-empty list")
        for index, source in enumerate(official_sources):
            if not isinstance(source, dict):
                raise AssertionError(f"{relative}: official_sources[{index}] must be a mapping")
            for required in ["title", "url", "source_authority", "verification_status", "retrieved_at", "notes"]:
                if not source.get(required):
                    raise AssertionError(f"{relative}: official_sources[{index}] missing {required!r}")
            if source["source_authority"] not in SOURCE_AUTHORITIES:
                raise AssertionError(f"{relative}: official_sources[{index}].source_authority invalid")
            if source["verification_status"] not in VERIFICATION_STATUSES:
                raise AssertionError(f"{relative}: official_sources[{index}].verification_status invalid")
            if not str(source["url"]).startswith("https://"):
                raise AssertionError(f"{relative}: official_sources[{index}].url must be https")
            official_titles[str(source["title"])] = str(source["verification_status"])

        volatile_items = record["volatile_items_checked"]
        if not isinstance(volatile_items, list) or not volatile_items:
            raise AssertionError(f"{relative}: volatile_items_checked must be a non-empty list")
        for index, item in enumerate(volatile_items):
            if not isinstance(item, dict):
                raise AssertionError(f"{relative}: volatile_items_checked[{index}] must be a mapping")
            for required in ["item", "previous_value", "refreshed_value", "source_ref", "result"]:
                if required not in item:
                    raise AssertionError(f"{relative}: volatile_items_checked[{index}] missing {required!r}")
            if item["result"] not in REVALIDATION_ITEM_RESULTS:
                raise AssertionError(f"{relative}: volatile_items_checked[{index}].result invalid")
            if str(item["source_ref"]) not in official_titles:
                raise AssertionError(f"{relative}: volatile_items_checked[{index}].source_ref must match official source title")

        asset_update = record["asset_update"]
        if not isinstance(asset_update, dict):
            raise AssertionError(f"{relative}: asset_update must be a mapping")
        for required in ["updated", "maintenance_next_review_before", "maintenance_next_review_after", "summary"]:
            if required not in asset_update:
                raise AssertionError(f"{relative}: asset_update missing {required!r}")
        if not isinstance(asset_update["updated"], bool):
            raise AssertionError(f"{relative}: asset_update.updated must be boolean")

        decision = record["retirement_decision"]
        if not isinstance(decision, dict) or decision.get("decision") not in REVALIDATION_DECISIONS:
            raise AssertionError(f"{relative}: retirement_decision.decision invalid")
        decision_value = str(decision["decision"])
        if decision_value == "retire":
            if asset_path in registry_paths:
                raise AssertionError(f"{relative}: retire decisions must remove asset_path from freshness_debt")
            for source_title, status in official_titles.items():
                if status != "[VERIFIED]":
                    raise AssertionError(f"{relative}: retire source {source_title!r} must be [VERIFIED]")
            for index, item in enumerate(volatile_items):
                if item["result"] in {"insufficient", "contradicted"}:
                    raise AssertionError(f"{relative}: retire item {index} must be verified as unchanged, updated, or removed")
        elif asset_path not in registry_paths:
            raise AssertionError(f"{relative}: non-retire decisions must keep asset_path in freshness_debt")
        elif not decision.get("remaining_stale_scope"):
            raise AssertionError(f"{relative}: non-retire decisions must record remaining_stale_scope")

        self_check = record["self_check"]
        if not isinstance(self_check, dict):
            raise AssertionError(f"{relative}: self_check must be a mapping")
        if self_check.get("official_source_used") is not True:
            raise AssertionError(f"{relative}: self_check.official_source_used must be true")
        if self_check.get("volatile_items_reviewed") is not True:
            raise AssertionError(f"{relative}: self_check.volatile_items_reviewed must be true")
        if self_check.get("no_current_obligation_from_stale_only") is not True:
            raise AssertionError(f"{relative}: stale-only conclusions must remain forbidden")
        if decision_value == "retire":
            if self_check.get("freshness_debt_updated") is not True:
                raise AssertionError(f"{relative}: retire decisions must update freshness_debt")
            if self_check.get("next_review_advanced") is not True:
                raise AssertionError(f"{relative}: retire decisions must advance next_review")


def check_freshness_metadata_schema() -> None:
    data = load_yaml("skills/beopsuny/assets/schemas/freshness_metadata.yaml")
    text = read_text("skills/beopsuny/assets/schemas/freshness_metadata.yaml")
    label = "freshness_metadata.yaml"

    for required in [
        "Freshness metadata schema",
        "next_review",
        "last_verified",
        "source_url",
        "freshness_days",
        "must_reverify",
        "stale_registered",
        "freshness_debt.yaml",
        "triage_only",
        "[STALE]",
    ]:
        assert_contains(text, required, label)
    for required in ["review_cycle", "next_review", "last_verified", "source_url", "freshness_days", "must_reverify"]:
        if required not in data:
            raise AssertionError(f"{label}: missing {required!r}")

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


def asset_expiry_reasons(next_review: Any, maintenance: Any, today: date) -> list[str]:
    """만료 판정의 단일 정의. 만료 축은 둘(`next_review`, `last_verified + freshness_days`)이고,
    등록 자산 검사와 미등록 자산 검사가 서로 다른 축만 보면 registry 등록이 나머지 축의
    면제 통로가 된다 — #243이 막은 구멍이 축 하나에만 적용돼 있던 문제(PR #247 리뷰).
    두 검사 모두 이 함수를 통해서만 만료를 판정한다."""
    reasons: list[str] = []
    due = parse_review_due(next_review)
    if due and due <= today:
        reasons.append(f"next_review {next_review} 경과")
    if isinstance(maintenance, dict):
        last_verified = maintenance.get("last_verified")
        freshness_days = maintenance.get("freshness_days")
        if last_verified is not None and isinstance(freshness_days, int):
            window_due = date.fromisoformat(str(last_verified)) + timedelta(days=freshness_days)
            if window_due <= today:
                reasons.append(f"last_verified {last_verified} + freshness_days {freshness_days}일 경과")
    return reasons


def check_asset_freshness_metadata_tracked() -> None:
    freshness_metadata_allowlist = {
        "skills/beopsuny/assets/policies/freshness_debt.yaml",
        "skills/beopsuny/assets/policies/knowledge_manifest.yaml",
        "skills/beopsuny/assets/policies/review_mode.yaml",
        "skills/beopsuny/assets/policies/source_grades.yaml",
        "skills/beopsuny/assets/schemas/freshness_metadata.yaml",
        "skills/beopsuny/assets/schemas/freshness_revalidation.yaml",
        "skills/beopsuny/assets/schemas/legal_verification_packet.yaml",
        "skills/beopsuny/assets/schemas/output_contract.yaml",
    }
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
    missing_metadata: list[str] = []
    stale_untracked: list[str] = []
    today = date.today()

    for path in asset_paths:
        relative = path.relative_to(ROOT).as_posix()
        data = load_yaml(relative)
        if not isinstance(data, dict):
            if relative not in freshness_metadata_allowlist:
                missing_metadata.append(relative)
            continue
        maintenance = data.get("maintenance")
        if not isinstance(maintenance, dict):
            if relative not in freshness_metadata_allowlist:
                missing_metadata.append(relative)
            continue
        for required in [
            "review_cycle",
            "next_review",
            "last_verified",
            "source_url",
            "freshness_days",
            "must_reverify",
        ]:
            if required not in maintenance:
                raise AssertionError(f"{relative}: maintenance missing {required!r}")
        if not str(maintenance["source_url"]).startswith("https://"):
            raise AssertionError(f"{relative}: maintenance.source_url must be an official https source")
        if not isinstance(maintenance["must_reverify"], bool) or maintenance["must_reverify"] is not True:
            raise AssertionError(f"{relative}: maintenance.must_reverify must be true")
        if not isinstance(maintenance["freshness_days"], int) or maintenance["freshness_days"] <= 0:
            raise AssertionError(f"{relative}: maintenance.freshness_days must be a positive integer")

        expired = bool(asset_expiry_reasons(maintenance.get("next_review"), maintenance, today))
        if expired and relative not in registered_assets:
            stale_untracked.append(f"{relative}: next_review={maintenance.get('next_review')}")

    if missing_metadata:
        raise AssertionError(
            "YAML assets under skills/beopsuny/assets must carry maintenance metadata "
            "unless explicitly allowlisted by the volatile-fact criterion documented in "
            f"freshness-governance.md: {missing_metadata}"
        )

    if stale_untracked:
        raise AssertionError(
            "stale asset metadata must be refreshed or explicitly tracked in "
            f"freshness_debt.yaml: {stale_untracked}"
        )


def revalidated_asset_paths() -> set[str]:
    """재검증 기록이 존재하는 asset_path 집합. 기록의 스키마 검증은
    check_freshness_revalidation_records가 담당하고, 여기서는 존재 여부만 본다."""
    fixtures_dir = ROOT / "tests/fixtures/freshness_revalidations"
    paths: set[str] = set()
    for path in sorted(fixtures_dir.glob("*.yaml")) if fixtures_dir.exists() else []:
        record = load_yaml(path.relative_to(ROOT).as_posix())
        if isinstance(record, dict) and record.get("asset_path"):
            paths.add(str(record["asset_path"]))
    return paths


def check_freshness_debt_registry() -> None:
    data = freshness_debt_registry()
    label = "freshness_debt.yaml"
    today = date.today()
    revalidated = revalidated_asset_paths()

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
        maintenance: Any = None
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
        if not due:
            raise AssertionError(f"{label}: registered asset has invalid next_review: {path}")

        expiry_reasons = asset_expiry_reasons(item["next_review"], maintenance, today)

        # #243: registry 등록이 무기한 면제 통로가 되지 않게 한다. 등록 이전에는
        # next_review 경과를 아무도 검사하지 않아 부채가 조용히 누적됐다
        # (legal_terms.yaml이 231일 경과한 채 그린). 경과분은 날짜가 박힌
        # 자기만료 예외로만 통과하며, resolve_by가 지나면 스스로 FAIL한다.
        if expiry_reasons:
            resolve_by = item.get("overdue_resolve_by")
            if not resolve_by:
                raise AssertionError(
                    f"{label}: {path} 만료({', '.join(expiry_reasons)}) — 재검증 후 "
                    "next_review를 전진시키거나(revalidation record 필요) "
                    "overdue_resolve_by/overdue_reason/overdue_tracked_issue를 등록하라"
                )
            for required in ["overdue_reason", "overdue_tracked_issue"]:
                if not item.get(required):
                    raise AssertionError(f"{label}: {path} overdue entry missing {required!r}")
            resolve_due = parse_review_due(resolve_by)
            if not resolve_due:
                raise AssertionError(f"{label}: {path} invalid overdue_resolve_by: {resolve_by!r}")
            if resolve_due <= today:
                raise AssertionError(
                    f"{label}: {path} overdue_resolve_by {resolve_by} 도과 — "
                    "예외를 연장하지 말고 재검증 또는 은퇴로 해소하라"
                )
        elif path not in revalidated:
            # 경과 상태를 벗어난 등록 자산은 근거를 제시해야 한다. 이 분기가 없으면
            # overdue 항목의 next_review를 미래로 밀기만 해도 CI가 통과해,
            # policy.revalidation_record_required가 문서로만 존재하게 된다.
            raise AssertionError(
                f"{label}: {path} 미경과 등록 자산에 revalidation record가 없다 — "
                "tests/fixtures/freshness_revalidations/에 asset_path가 일치하는 기록을 남기거나, "
                "경과 상태면 overdue 3필드를 선언하라"
            )

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
    for token in ["Runtime Rule", "Verification Before Answering", "Maintainer Workflow",
                  "triage_only", "assets/policies/freshness_debt.yaml",
                  "assets/schemas/freshness_revalidation.yaml", "remaining_stale_scope",
                  "partial_refresh", "live legal research", "[INSUFFICIENT]"]:
        assert_contains(text, token, "freshness-governance.md")
    # Registry contents and record fields have one machine-readable home; their
    # completeness, expiration and deletion are checked by registry/record checks.

