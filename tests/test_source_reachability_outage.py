#!/usr/bin/env python3
"""법망 API가 스스로 공지한 중단의 판정 (#268).

이 헬스체크는 릴리즈 체크리스트 2번의 게이트다. 6개월짜리 상류 중단을 FAIL로
두면 릴리즈마다 손으로 넘겨야 하는 빨간불이 되어 게이트를 아무도 읽지 않게
되고, 무기한 WARN으로 두면 조용히 영구화된다. 그래서 **자기만료 WARN**이다 —
`freshness_debt.yaml`의 `overdue_resolve_by`와 같은 모양.

여기서 고정하는 것은 두 가지다.
1. 공지 중단은 WARN이되 수용 기한이 지나면 FAIL로 **돌아온다**.
2. 인식은 벤더의 `error` 문자열이 아니라 응답 shape으로 한다 — 코드 이름이
   바뀌어도(`service_maintenance` → `service_paused`) 판정이 빗나가지 않아야 한다.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))

import check_source_reachability as health  # noqa: E402

BEFORE = "2026-07-27"
AFTER = "2099-01-01"


def notice_body(error: str = "service_paused", **extra: object) -> str:
    payload = {
        "ok": False,
        "error": error,
        "service_status": "paused",
        "service_notice": {
            "code": error,
            "title": "서비스 운영 일시 중단 안내",
            "message": "서버의 물리적 장애로 서비스를 한동안 중단하게 되었습니다.",
            "estimated_recovery": "2027-Q1",
        },
    }
    payload.update(extra)
    return json.dumps(payload)


class DeclaredOutageTest(unittest.TestCase):
    def test_declared_outage_warns_inside_the_accepted_window(self) -> None:
        verdict = health.declared_outage(notice_body(), BEFORE)
        self.assertIsNotNone(verdict)
        self.assertEqual("WARN", verdict["status"])
        self.assertIn("2027-Q1", verdict["detail"])
        self.assertIn("조회 실패 ≠ 개정 없음", verdict["detail"])

    def test_the_acceptance_self_expires(self) -> None:
        """기한을 연장하는 대신 그때 다시 판단하게 만드는 장치다."""
        verdict = health.declared_outage(notice_body(), AFTER)
        self.assertEqual("FAIL", verdict["status"])
        self.assertIn(health.BEOPMANG_PAUSE_ACCEPTED_UNTIL, verdict["detail"])
        self.assertIn(health.BEOPMANG_PAUSE_TRACKED_ISSUE, verdict["detail"])

    def test_recognition_does_not_depend_on_the_vendor_error_code(self) -> None:
        """#268의 원인 자체 — 코드 이름을 열거한 판정은 rename에 조용히 빗나갔다."""
        for code in ["service_paused", "service_maintenance", "totally_new_code"]:
            with self.subTest(code):
                verdict = health.declared_outage(notice_body(code), BEFORE)
                self.assertEqual("WARN", verdict["status"], code)

    def test_recovery_estimate_is_read_not_assumed(self) -> None:
        body = json.loads(notice_body())
        del body["service_notice"]["estimated_recovery"]
        verdict = health.declared_outage(json.dumps(body), BEFORE)
        self.assertIn("미공지", verdict["detail"])

    # --- 공지 없는 실패는 여전히 FAIL이어야 한다 -----------------------------

    def test_plain_error_without_a_notice_is_not_a_declared_outage(self) -> None:
        """공지 없이 죽은 것과 서비스가 밝힌 중단은 다르다 — 전자는 원인 불명이다."""
        for label, body in [
            ("notice 없는 오류", '{"ok": false, "error": "internal_error"}'),
            ("notice가 문자열", '{"ok": false, "service_notice": "paused"}'),
            ("정상 응답", '{"ok": true, "data": {"total": 3}}'),
            ("non-JSON", "<html>502 Bad Gateway</html>"),
            ("빈 응답", ""),
        ]:
            with self.subTest(label):
                self.assertIsNone(health.declared_outage(body, BEFORE))


if __name__ == "__main__":
    unittest.main()
