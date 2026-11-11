#!/usr/bin/env python3
"""Focused freshness date and revalidation binding regressions (#366)."""

from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = str(REPO_ROOT / "tests")
if TESTS_DIR not in sys.path:
    sys.path.insert(0, TESTS_DIR)

from contract_checks import freshness  # noqa: E402


_MISSING = object()
ASSET_PATH = "skills/beopsuny/assets/policies/checklists/example.yaml"
REGISTRY_PATH = "skills/beopsuny/assets/policies/freshness_debt.yaml"


class FreshnessContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.original_root = freshness.ROOT
        freshness.ROOT = self.root
        self.today = date.today()

    def tearDown(self) -> None:
        freshness.ROOT = self.original_root
        self.temp_dir.cleanup()

    def write_yaml(self, relative: str, data: Any) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

    def maintenance(
        self,
        *,
        next_review: Any = _MISSING,
        last_verified: Any = _MISSING,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "review_cycle": "annual",
            "source_url": "https://www.law.go.kr/",
            "freshness_days": 365,
            "must_reverify": True,
        }
        if next_review is not _MISSING:
            result["next_review"] = next_review
        if last_verified is not _MISSING:
            result["last_verified"] = last_verified
        return result

    def write_asset(self, maintenance: dict[str, Any]) -> None:
        self.write_yaml(ASSET_PATH, {"name": "synthetic", "maintenance": maintenance})

    def write_registry(self, next_review: str, *, registered: bool = True) -> None:
        assets: list[dict[str, Any]] = []
        if registered:
            assets.append(
                {
                    "path": ASSET_PATH,
                    "status": "stale_registered",
                    "next_review": next_review,
                    "risk": "synthetic volatile values",
                    "allowed_use": "triage only",
                    "verification_required": "check official source",
                    "retire_when": "reverified",
                }
            )
        self.write_yaml(
            REGISTRY_PATH,
            {
                "tracked_issue": "https://github.com/sungjunlee/beopsuny-skill/issues/101",
                "policy": {
                    "allowed_runtime_use": "triage_only",
                    "required_before_legal_conclusion": "live official-source check",
                    "forbidden_runtime_use": "no stale conclusion",
                    "retirement_rule": "reverify first",
                    "revalidation_record_required": "record the review",
                },
                "assets": assets,
            },
        )

    def write_record(
        self,
        filename: str,
        *,
        checked_at: str,
        next_review_before: str,
        next_review_after: str,
    ) -> None:
        self.write_yaml(
            f"tests/fixtures/freshness_revalidations/{filename}",
            {
                "asset_path": ASSET_PATH,
                "checked_at": checked_at,
                "checked_by": "synthetic regression",
                "tracked_issue": "https://github.com/sungjunlee/beopsuny-skill/issues/366",
                "source_families_checked": ["law.go.kr"],
                "official_sources": [
                    {
                        "title": "Official source",
                        "url": "https://www.law.go.kr/",
                        "source_authority": "공식 원문",
                        "verification_status": "[VERIFIED]",
                        "retrieved_at": checked_at,
                        "notes": "Synthetic local contract input.",
                    }
                ],
                "volatile_items_checked": [
                    {
                        "item": "deadline",
                        "previous_value": "old",
                        "refreshed_value": "checked",
                        "source_ref": "Official source",
                        "result": "unchanged",
                    }
                ],
                "asset_update": {
                    "updated": True,
                    "maintenance_next_review_before": next_review_before,
                    "maintenance_next_review_after": next_review_after,
                    "summary": "Synthetic review.",
                },
                "retirement_decision": {
                    "decision": "partial_refresh",
                    "reason": "Residual scope remains.",
                    "remaining_stale_scope": "remaining notice details",
                },
                "self_check": {
                    "official_source_used": True,
                    "volatile_items_reviewed": True,
                    "next_review_advanced": True,
                    "freshness_debt_updated": True,
                    "no_current_obligation_from_stale_only": True,
                },
            },
        )

    def assert_metadata_rejected(self, maintenance: dict[str, Any], field: str) -> None:
        fallback_review = (self.today + timedelta(days=365)).isoformat()
        self.write_asset(maintenance)
        self.write_registry(fallback_review, registered=False)
        with self.assertRaises(AssertionError) as caught:
            freshness.check_asset_freshness_metadata_tracked()
        self.assertIn(field, str(caught.exception))

    def test_missing_and_null_maintenance_dates_are_rejected(self) -> None:
        valid_review = (self.today + timedelta(days=365)).isoformat()
        valid_verified = self.today.isoformat()
        cases = [
            ("missing next_review", self.maintenance(last_verified=valid_verified), "next_review"),
            (
                "null next_review",
                self.maintenance(next_review=None, last_verified=valid_verified),
                "next_review",
            ),
            ("missing last_verified", self.maintenance(next_review=valid_review), "last_verified"),
            (
                "null last_verified",
                self.maintenance(next_review=valid_review, last_verified=None),
                "last_verified",
            ),
        ]
        for label, maintenance, field in cases:
            with self.subTest(label):
                self.assert_metadata_rejected(maintenance, field)

    def test_invalid_dates_and_future_last_verified_are_rejected(self) -> None:
        valid_review = (self.today + timedelta(days=365)).isoformat()
        cases = [
            (
                "invalid review month",
                self.maintenance(next_review="2099-13", last_verified=self.today.isoformat()),
                "next_review",
            ),
            (
                "invalid review month 00",
                self.maintenance(next_review="2027-00", last_verified=self.today.isoformat()),
                "next_review",
            ),
            (
                "invalid verification day",
                self.maintenance(next_review=valid_review, last_verified="2026-02-30"),
                "last_verified",
            ),
            (
                "future verification",
                self.maintenance(
                    next_review=valid_review,
                    last_verified=(self.today + timedelta(days=1)).isoformat(),
                ),
                "last_verified",
            ),
        ]
        for label, maintenance, field in cases:
            with self.subTest(label):
                self.assert_metadata_rejected(maintenance, field)

    def test_historical_record_cannot_support_advanced_current_dates(self) -> None:
        old_checked = (self.today - timedelta(days=365)).isoformat()
        old_review = (self.today + timedelta(days=30)).isoformat()
        current_review = (self.today + timedelta(days=730)).isoformat()
        self.write_asset(
            self.maintenance(
                next_review=current_review,
                last_verified=self.today.isoformat(),
            )
        )
        self.write_registry(current_review)
        self.write_record(
            "historical.yaml",
            checked_at=old_checked,
            next_review_before=(self.today - timedelta(days=30)).isoformat(),
            next_review_after=old_review,
        )

        # The metadata is well-formed and not stale; the missing evidence is the
        # old record's inability to support the newly advanced current dates.
        freshness.check_asset_freshness_metadata_tracked()
        with self.assertRaisesRegex(AssertionError, "no revalidation record supports"):
            freshness.check_freshness_revalidation_records()
        with self.assertRaisesRegex(AssertionError, "revalidation record"):
            freshness.check_freshness_debt_registry()

    def test_one_current_record_is_enough_among_history(self) -> None:
        current_review = f"{self.today.year + 1:04d}-{self.today.month:02d}"
        self.write_asset(
            self.maintenance(
                next_review=current_review,
                last_verified=self.today.isoformat(),
            )
        )
        self.write_registry(current_review)
        self.write_record(
            "historical.yaml",
            checked_at=(self.today - timedelta(days=365)).isoformat(),
            next_review_before=(self.today - timedelta(days=730)).isoformat(),
            next_review_after=(self.today - timedelta(days=30)).isoformat(),
        )
        self.write_record(
            "current.yaml",
            checked_at=self.today.isoformat(),
            next_review_before=(self.today - timedelta(days=30)).isoformat(),
            next_review_after=current_review,
        )

        freshness.check_freshness_revalidation_records()
        freshness.check_freshness_debt_registry()
        self.assertEqual(
            freshness.parse_review_due("2027-12-31"),
            date(2027, 12, 31),
        )

    def test_record_after_retained_last_verified_is_applicable(self) -> None:
        current_review = (self.today + timedelta(days=365)).isoformat()
        self.write_asset(
            self.maintenance(
                next_review=current_review,
                last_verified=(self.today - timedelta(days=2)).isoformat(),
            )
        )
        self.write_registry(current_review)
        self.write_record(
            "current.yaml",
            checked_at=self.today.isoformat(),
            next_review_before=(self.today - timedelta(days=30)).isoformat(),
            next_review_after=current_review,
        )

        freshness.check_freshness_revalidation_records()
        freshness.check_freshness_debt_registry()

    def test_iso_timestamp_checked_at_is_accepted(self) -> None:
        current_review = (self.today + timedelta(days=365)).isoformat()
        self.write_asset(
            self.maintenance(
                next_review=current_review,
                last_verified=self.today.isoformat(),
            )
        )
        self.write_registry(current_review)
        self.write_record(
            "timestamp.yaml",
            checked_at=f"{self.today.isoformat()}T12:00:00Z",
            next_review_before=(self.today - timedelta(days=30)).isoformat(),
            next_review_after=current_review,
        )
        # retrieved_at in the dumped record also uses checked_at; that field is
        # not date-validated by these checks. The record itself must load as a
        # timestamp string or datetime and still apply.
        freshness.check_freshness_revalidation_records()
        freshness.check_freshness_debt_registry()

        parsed = freshness.parse_checked_at(
            "2026-07-03T12:00:00Z", date(2026, 7, 3), "checked_at"
        )
        self.assertEqual(parsed, date(2026, 7, 3))
        parsed_dt = freshness.parse_checked_at(
            datetime(2026, 7, 3, 12, 0, tzinfo=timezone.utc),
            date(2026, 7, 3),
            "checked_at",
        )
        self.assertEqual(parsed_dt, date(2026, 7, 3))



if __name__ == "__main__":
    unittest.main()
