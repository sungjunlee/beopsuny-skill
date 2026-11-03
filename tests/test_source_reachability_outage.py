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


class BeopmangAxisTest(unittest.TestCase):
    """축 전체 판정 — `declared_outage`가 None을 준 뒤 무엇이 되는가.

    WARN 경로를 새로 내면서 200 + `ok: false`가 그대로 `summarize_beopmang()`까지
    흘러 **OK로 보고되던** 구멍이 생겼다 (PR #269 codex 리뷰). 계약 문서는 오류
    응답을 조회 실패로 규정하므로, 공지 shape이 아니라는 이유로 그린이 되면
    문서와 검사가 다시 갈라진다.
    """

    def axis(self, body: bytes, status: int = 200, today: str = BEFORE) -> dict[str, str]:
        original = health.http_get

        def fake(url, timeout=15, max_bytes=None):
            return status, body, ""

        health.http_get = fake
        try:
            return health.check_beopmang(today=today)
        finally:
            health.http_get = original

    def test_ok_false_without_a_notice_fails_the_axis(self) -> None:
        for label, body in [
            ("일반 오류", b'{"ok": false, "error": "internal_error"}'),
            ("옛 maintenance 형태", b'{"ok": false, "error": "service_maintenance"}'),
            ("사유 없는 오류", b'{"ok": false}'),
        ]:
            with self.subTest(label):
                result = self.axis(body)
                self.assertEqual("FAIL", result["status"], label)
                self.assertIn("조회 실패", result["detail"])

    def test_declared_outage_still_warns_on_the_axis(self) -> None:
        result = self.axis(notice_body().encode(), status=503)
        self.assertEqual("WARN", result["status"])

    def test_healthy_response_is_ok(self) -> None:
        result = self.axis(b'{"data": {"total": 5}}')
        self.assertEqual("OK", result["status"])

    def test_valid_json_over_the_read_cap_is_ok_and_invalid_json_fails(self) -> None:
        """4096에서 자른 정상 JSON은 non-JSON이 아니다 (#369). 잘못된 JSON은 그대로 FAIL."""
        payload = {"data": {"total": 7}, "pad": "x" * 5200}
        raw = json.dumps(payload).encode()
        self.assertGreaterEqual(len(raw), 5078)
        with self.assertRaises(json.JSONDecodeError):
            json.loads(raw[:4096])

        class Resp:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def getcode(self):
                return 200

            def read(self, n=-1):
                return raw if n is None or n < 0 else raw[:n]

        original = health.urllib.request.urlopen
        health.urllib.request.urlopen = lambda req, timeout=15: Resp()
        try:
            result = health.check_beopmang(today=BEFORE)
        finally:
            health.urllib.request.urlopen = original
        self.assertEqual("OK", result["status"])
        self.assertIn("total=7", result["detail"])

        invalid = self.axis(b"<html>502 Bad Gateway</html>")
        self.assertEqual("FAIL", invalid["status"])
        self.assertIn("non-JSON", invalid["detail"])


# 수용 기한은 이 날짜까지다 (`today > BEOPMANG_PAUSE_ACCEPTED_UNTIL`).
DAY_BEFORE = "2027-06-29"
ON_DEADLINE = "2027-06-30"
DAY_AFTER = "2027-07-01"


class ForeignVantageOutageTest(unittest.TestCase):
    """`--dns-links`는 지역별 연결 불확실성만 보류한다 (#369).

    수용 기한 만료는 공지를 읽은 정책 판정이라 CI에서도 FAIL이다. 구분은 detail
    문구가 아니라 명시적 reason으로 한다. 나머지 축은 네트워크 없이 OK stub이다.
    """

    def setUp(self) -> None:
        self.saved = {
            "http_get": health.http_get,
            "check_beopmang": health.check_beopmang,
            "check_legalize_data": health.check_legalize_data,
            "check_korean_law_mcp": health.check_korean_law_mcp,
            "check_mirror": health.check_mirror,
            "check_link": health.check_link,
        }
        health.check_legalize_data = lambda: {
            "status": "OK",
            "axis": "기본 도구/legalize 데이터",
            "detail": "stub",
        }
        health.check_korean_law_mcp = lambda: {
            "status": "OK",
            "axis": "기본 도구/korean-law-mcp",
            "detail": "stub",
        }
        health.check_mirror = lambda family: {
            "status": "NOT_INSTALLED",
            "axis": f"로컬 미러/{family}",
            "detail": "stub",
        }
        health.check_link = lambda label, url, dns_only=False: {
            "status": "OK",
            "axis": f"링크/{label}",
            "detail": "stub",
        }

    def tearDown(self) -> None:
        for name, original in self.saved.items():
            setattr(health, name, original)

    def _run(self, *, dns_links: bool, today: str):
        checks = health.run_checks(dns_links=dns_links, today=today)
        found = next(check for check in checks if check["axis"] == "법망 API")
        line, code = health.summarize(checks)
        return found, line, code

    def test_acceptance_edges_and_ci_keeps_expiry(self) -> None:
        health.http_get = lambda url, timeout=15, max_bytes=None: (
            503,
            notice_body().encode(),
            "HTTP 503",
        )
        for day, status in (
            (DAY_BEFORE, "WARN"),
            (ON_DEADLINE, "WARN"),
            (DAY_AFTER, "FAIL"),
        ):
            with self.subTest(day=day, mode="ci"):
                found, _line, code = self._run(dns_links=True, today=day)
                self.assertEqual(status, found["status"])
                self.assertNotIn("판정 보류", found["detail"])
                self.assertEqual(0 if status == "WARN" else 1, code)
            with self.subTest(day=day, mode="local"):
                found, _line, code = self._run(dns_links=False, today=day)
                self.assertEqual(status, found["status"])
                self.assertEqual(0 if status == "WARN" else 1, code)
        found, _line, _code = self._run(dns_links=True, today=DAY_AFTER)
        self.assertEqual(health.BEOPMANG_REASON_ACCEPTANCE_EXPIRED, found.get("reason"))
        self.assertIn(health.BEOPMANG_PAUSE_ACCEPTED_UNTIL, found["detail"])

    def test_regional_connection_failures_stay_deferred(self) -> None:
        cases = {
            "timeout": (None, b"", "timeout"),
            "connection": (None, b"", "connection error: refused"),
            "http 410": (410, b"gone", "HTTP 410"),
        }
        for label, value in cases.items():
            with self.subTest(label=label, mode="ci"):
                health.http_get = lambda url, timeout=15, max_bytes=None, value=value: value
                found, _line, code = self._run(dns_links=True, today=DAY_AFTER)
                self.assertEqual("WARN", found["status"])
                self.assertIn("판정 보류", found["detail"])
                self.assertEqual(0, code)
            with self.subTest(label=label, mode="local"):
                health.http_get = lambda url, timeout=15, max_bytes=None, value=value: value
                found, _line, code = self._run(dns_links=False, today=DAY_BEFORE)
                self.assertEqual("FAIL", found["status"])
                self.assertNotIn("판정 보류", found["detail"])
                self.assertEqual(1, code)

    def test_deferral_uses_reason_not_detail_text(self) -> None:
        """detail에 기한 문구가 있어도 reason이 만료가 아니면 보류하고, 반대도 같다."""

        def looks_like_expiry(today=None):
            return {
                "status": "FAIL",
                "axis": "법망 API",
                "detail": "수용 기한 2027-06-30 경과처럼 보이는 연결 실패",
                "reason": "timeout",
            }

        def expired_without_those_words(today=None):
            return {
                "status": "FAIL",
                "axis": "법망 API",
                "detail": "policy window elapsed",
                "reason": "acceptance_expired",
            }

        health.check_beopmang = looks_like_expiry
        found, _line, code = self._run(dns_links=True, today=DAY_AFTER)
        self.assertEqual("WARN", found["status"])
        self.assertIn("판정 보류", found["detail"])
        self.assertEqual(0, code)

        health.check_beopmang = expired_without_those_words
        found, _line, code = self._run(dns_links=True, today=DAY_AFTER)
        self.assertEqual("FAIL", found["status"])
        self.assertEqual("policy window elapsed", found["detail"])
        self.assertNotIn("판정 보류", found["detail"])
        self.assertEqual(1, code)


class DefaultToolAxesTest(unittest.TestCase):
    """기본 도구 경로 축: 응답 shape으로 판정하고 네트워크는 쓰지 않는다."""

    def run_axis(self, fn, responses):
        original = health.http_get

        def fake(url, timeout=15, max_bytes=4096):
            for prefix, value in responses.items():
                if url.startswith(prefix):
                    return value
            raise AssertionError(f"unexpected url {url}")

        health.http_get = fake
        try:
            return fn()
        finally:
            health.http_get = original

    def legalize(self, repo=(200, b'{"archived": false, "pushed_at": "2026-10-07T00:00:00Z"}', ""),
                 pypi=(200, b'{"info": {"version": "0.5.1"}}', "")):
        return self.run_axis(health.check_legalize_data, {
            health.GITHUB_API_REPOS: repo,
            health.LEGALIZE_CLI_PYPI_URL: pypi,
        })

    def test_legalize_healthy_is_ok(self) -> None:
        result = self.legalize()
        self.assertEqual("OK", result["status"])
        self.assertIn("0.5.1", result["detail"])

    def test_github_rate_limit_is_deferred_not_failed(self) -> None:
        limited = b'{"message": "API rate limit exceeded for 1.2.3.4."}'
        for code, body in ((403, limited), (429, b"{}")):
            with self.subTest(code):
                result = self.legalize(repo=(code, body, f"HTTP {code}"))
                self.assertEqual("WARN", result["status"])
                self.assertIn("조회 실패 ≠ 데이터 없음", result["detail"])

    def test_other_github_403_fails(self) -> None:
        result = self.legalize(repo=(403, b'{"message": "Repository access blocked"}', "HTTP 403"))
        self.assertEqual("FAIL", result["status"])

    def test_malformed_pypi_payload_fails_without_crashing(self) -> None:
        result = self.legalize(pypi=(200, b'{"info": ["unexpected"]}', ""))
        self.assertEqual("FAIL", result["status"])

    def test_json_axes_read_the_whole_body(self) -> None:
        """잘린 JSON이 non-JSON FAIL로 보이지 않게, JSON 축은 본문 전체를 읽는다."""
        big = json.dumps({"info": {"version": "9.9.9"}, "pad": "x" * 600_000}).encode()

        class Resp:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def getcode(self):
                return 200

            def read(self, n=-1):
                return big if n is None or n < 0 else big[:n]

        original = health.urllib.request.urlopen
        health.urllib.request.urlopen = lambda req, timeout=15: Resp()
        try:
            status, payload, err = health.get_json(health.LEGALIZE_CLI_PYPI_URL)
        finally:
            health.urllib.request.urlopen = original
        self.assertEqual(200, status)
        self.assertEqual("9.9.9", payload["info"]["version"])

    def test_rate_limit_does_not_hide_a_package_failure(self) -> None:
        result = self.legalize(repo=(403, b'{"message": "API rate limit exceeded"}', "HTTP 403"), pypi=(404, b"{}", "HTTP 404"))
        self.assertEqual("FAIL", result["status"])

    def test_archived_repo_or_missing_package_fails(self) -> None:
        self.assertEqual("FAIL", self.legalize(repo=(200, b'{"archived": true}', ""))["status"])
        self.assertEqual("FAIL", self.legalize(repo=(404, b"{}", "HTTP 404"))["status"])
        self.assertEqual("FAIL", self.legalize(pypi=(404, b"{}", "HTTP 404"))["status"])

    def klm(self, health_resp, npm=(200, b'{"version": "4.15.6"}', "")):
        return self.run_axis(health.check_korean_law_mcp, {
            health.KOREAN_LAW_MCP_HEALTH_URL: health_resp,
            health.KOREAN_LAW_MCP_NPM_URL: npm,
        })

    def test_korean_law_mcp_healthy_is_ok(self) -> None:
        result = self.klm((200, b'{"status": "ok"}', ""))
        self.assertEqual("OK", result["status"])
        self.assertIn("4.15.6", result["detail"])

    def test_korean_law_mcp_unhealthy_fails(self) -> None:
        for label, resp in [
            ("down", (None, b"", "timeout")),
            ("5xx", (503, b"{}", "HTTP 503")),
            ("not ok", (200, b'{"status": "degraded"}', "")),
        ]:
            with self.subTest(label):
                self.assertEqual("FAIL", self.klm(resp)["status"])


if __name__ == "__main__":
    unittest.main()
