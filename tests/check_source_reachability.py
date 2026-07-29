#!/usr/bin/env python3
"""소스 도달성 헬스체크 (로컬 미러 / 법망 API / law.go.kr 링크).

세 축을 점검한다:
1. 로컬 미러 동기화 — legalize-kr, precedent-kr, admrule-kr, ordinance-kr
   (upstream HEAD 해시 비교; 커밋 날짜는 정보용 — precedent-kr은 판례
   선고일을 커밋 날짜로 쓰는 합성 히스토리라 날짜 기반 판정이 무의미하다)
2. 법망 API 가용성 — search endpoint 응답
3. law.go.kr 링크 rot — 법령·판례 대표 링크 HTTP 상태

릴리즈 전 또는 필요 시 수동 실행. 네트워크 의존이므로 O1/O2 정적 게이트에
포함하지 않는다. 실패는 "조회 실패"이며 "개정 없음"이 아니다.

`--dns-links`: CI 등 국외 vantage용. 한국 정부 사이트는 국외에서 HTTP가
timeout/거부될 수 있어(실측: GitHub 러너에서 law.go.kr timeout, 법망 410)
링크 축은 DNS 해석만 판정하고(glaw류 도메인 사망은 DNS로 전 세계에서 감지됨)
법망 축 실패는 WARN으로 낮춘다. 사용자 vantage(국내) 판정은 로컬 실행이 기준.

CI vs 로컬 커버리지 — 이 도크스트링이 이 계약의 집이다 (#286). 다른 표면은
포인터만 둔다 (`README.md` 릴리즈 체크리스트 2번 ·
`.github/workflows/source-reachability.yml` cron·이슈 메커닉).
- CI (`--dns-links`, 미러 clone 안 함): ① 미러 축은 항상 `NOT_INSTALLED`
  (FAIL 아님, 조용히 넘어감). ② 법망 축은 서비스가 공지한 중단 동안 자기만료
  WARN (아래 `BEOPMANG_PAUSE_ACCEPTED_UNTIL`). ③ 링크 축은 DNS 해석만. 그러므로
  CI의 그린은 "3축 정상"이 아니라 "law.go.kr 도메인 1개 생존"이다 — 수용 기한
  `2027-06-30`까지 이 상태가 유지된다. 이 워크플로의 원래 목적은 glaw류 도메인
  사망 감지이고, CI는 그 목적을 유지한다.
- 로컬 릴리즈 체크 (`README.md` `### 릴리즈 체크리스트` 2번, 미러 설치된 국내
  vantage): 위 3축이 전부 실제로 돈다. 릴리즈 전 3축 확인은 이 경로가 기준이다.
- 미러 축을 CI에서 돌릴지: **돌리지 않는다** — clone 비용·weekly cron 시간
  예산이 크고, CI의 역할은 도메인 사망 감지(DNS로 충분)이지 미러 freshness가
  아니다. 미러 staleness는 로컬 릴리즈 체크가 담당한다. 번복하려면 clone 비용과
  cron 예산을 함께 다시 판단한다.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any


SOURCE_FAMILIES = ("legalize-kr", "precedent-kr", "admrule-kr", "ordinance-kr")
GIT_TIMEOUT = 60
HTTP_TIMEOUT = 15
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
BEOPMANG_SEARCH_URL = (
    "https://api.beopmang.org/law?action=search&q="
    + urllib.parse.quote("개인정보보호법")
)
LINK_CHECKS = (
    (
        "law.go.kr 법령",
        "https://www.law.go.kr/"
        + urllib.parse.quote("법령/개인정보보호법", safe="/"),
    ),
    (
        "law.go.kr 판례",
        "https://www.law.go.kr/LSW/precInfoP.do?precSeq=233797",
    ),
)

STATUS_WIDTH = 15

# 서비스가 스스로 공지한 중단은 원인불명 실패와 다르다 — 대체 경로로 내려가면
# 되는 알려진 조건이고, 릴리즈마다 손으로 넘겨야 하는 빨간불이면 게이트를 아무도
# 읽지 않게 된다. 그래서 WARN으로 낮추되 freshness_debt의 `overdue_resolve_by`와
# 같은 자기만료를 준다: 아래 날짜가 지나면 서비스가 여전히 공지 중이어도 FAIL로
# 돌아간다. 무기한 WARN은 조용한 영속화다. 날짜를 연장하지 말고 그때 다시 판단한다.
#
# 수용 기한(2027-06-30)이 복구 예상(estimated_recovery 2027-Q1)보다 약 2분기
# 뒤인 것은 의도다 (#286) — 복구가 예상보다 늦어지는 날 한 번에 WARN→FAIL로
# 뒤집히면 그 지연이 즉시 빨간불이 되어 게이트를 아무도 읽지 않는다. 버퍼가
# 있어야 "재판단 시점"이 의미 있다. 기한을 미루는 것이 아니라, 지난 뒤에
# 다시 판단하게 두는 것 — 바로 위 자기만료 문장의 연장선이다.
BEOPMANG_PAUSE_ACCEPTED_UNTIL = "2027-06-30"
BEOPMANG_PAUSE_TRACKED_ISSUE = "https://github.com/sungjunlee/beopsuny-skill/issues/268"


def data_root() -> Path:
    root = os.environ.get("BEOPSUNY_DATA_ROOT", str(Path.home() / ".beopsuny"))
    return Path(root).expanduser() / "data"


def run_git(repo: Path, *args: str) -> tuple[int, str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            timeout=GIT_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return 1, f"timeout after {GIT_TIMEOUT}s"
    out = (result.stdout or result.stderr or "").strip()
    return result.returncode, out


def check_mirror(family: str) -> dict[str, Any]:
    axis = f"로컬 미러/{family}"
    path = data_root() / family
    if not path.is_dir():
        return {
            "status": "NOT_INSTALLED",
            "axis": axis,
            "detail": "degradation 경로 사용 (실패 아님)",
        }

    code, head = run_git(path, "rev-parse", "HEAD")
    if code != 0 or not head:
        return {
            "status": "FAIL",
            "axis": axis,
            "detail": f"git rev-parse 실패: {head or 'empty'}",
        }

    # staleness 판정은 upstream HEAD 해시 비교로 한다. 커밋 날짜는 정보용 —
    # precedent-kr은 판례 선고일을 커밋 날짜로 쓰는 합성 히스토리라(최신
    # HEAD가 1999년) 날짜 기반 판정이 무의미하다. upstream이 히스토리를
    # 재생성(diverge)해도 해시 불일치로 동일하게 잡힌다.
    _, iso = run_git(path, "log", "-1", "--format=%cI")
    code, remote = run_git(path, "ls-remote", "origin", "HEAD")
    if code != 0 or not remote:
        return {
            "status": "FAIL",
            "axis": axis,
            "detail": f"ls-remote 실패 (원격 도달 불가): {remote or 'empty'}",
        }

    remote_head = remote.split()[0]
    if remote_head == head:
        return {
            "status": "OK",
            "axis": axis,
            "detail": f"upstream 일치 (HEAD {head[:11]}, last_commit={iso})",
        }
    return {
        "status": "WARN",
        "axis": axis,
        "detail": (
            f"upstream 불일치 — 재동기화 필요: 로컬 변경 없음 확인 후 "
            f"`git fetch origin && git reset --hard origin/main` "
            f"(force-push 재생성 대응, source-access.md 최신화 절차 참조; "
            f"local {head[:11]}, upstream {remote_head[:11]}, last_commit={iso})"
        ),
    }


def http_get(url: str, timeout: int = HTTP_TIMEOUT) -> tuple[int | None, bytes, str]:
    """Return (status_or_None, body_or_empty, error_reason)."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            # 링크 rot 검사용으로 본문 일부만 읽는다.
            return resp.getcode(), resp.read(4096), ""
    except urllib.error.HTTPError as exc:
        body = exc.read() if exc.fp is not None else b""
        return exc.code, body, f"HTTP {exc.code}"
    except urllib.error.URLError as exc:
        return None, b"", f"connection error: {exc.reason}"
    except TimeoutError:
        return None, b"", "timeout"
    except Exception as exc:  # noqa: BLE001 — 헬스체크는 모든 네트워크 예외를 FAIL로
        return None, b"", f"{type(exc).__name__}: {exc}"


def declared_outage(text: str, today: str) -> dict[str, str] | None:
    """서비스가 스스로 공지한 중단이면 판정을 돌려주고, 아니면 None.

    `error` 값이 아니라 **응답 shape**으로 알아본다 — 벤더는 코드 이름을 바꾸고
    (`service_maintenance` → `service_paused`, #268), 코드를 열거하는 판정은 그때마다
    조용히 빗나간다. 사람이 읽을 공지(`service_notice`)를 담은 `ok: false` 응답이
    "서비스가 자기 입으로 밝힌 중단"의 구조다.
    """
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict) or payload.get("ok") is not False:
        return None
    notice = payload.get("service_notice")
    if not isinstance(notice, dict):
        return None

    recovery = notice.get("estimated_recovery") or payload.get("estimated_recovery") or "미공지"
    detail = f"서비스 공지 중단 (복구 예상 {recovery}, 조회 실패 ≠ 개정 없음)"
    if today > BEOPMANG_PAUSE_ACCEPTED_UNTIL:
        return {
            "status": "FAIL",
            "detail": (
                f"{detail} — 수용 기한 {BEOPMANG_PAUSE_ACCEPTED_UNTIL} 경과. "
                f"경로 유지 여부를 다시 판단한다: {BEOPMANG_PAUSE_TRACKED_ISSUE}"
            ),
        }
    return {"status": "WARN", "detail": f"{detail}, {BEOPMANG_PAUSE_ACCEPTED_UNTIL}까지 수용"}


def check_beopmang(today: str | None = None) -> dict[str, Any]:
    # 조회 실패는 개정 없음이 아니다 — 이 헬스체크는 스킬 계약의 실패 의미론을 따른다.
    axis = "법망 API"
    today = today or date.today().isoformat()
    status, body, err = http_get(BEOPMANG_SEARCH_URL)
    text = body.decode("utf-8", errors="replace")

    if err == "timeout" or "timeout" in err.lower():
        return {"status": "FAIL", "axis": axis, "detail": "timeout (조회 실패)"}
    if status is None:
        return {"status": "FAIL", "axis": axis, "detail": f"{err} (조회 실패)"}
    outage = declared_outage(text, today)
    if outage:
        return {"status": outage["status"], "axis": axis, "detail": outage["detail"]}
    if status >= 500:
        return {
            "status": "FAIL",
            "axis": axis,
            "detail": f"HTTP {status} (조회 실패)",
        }
    if status != 200:
        return {"status": "FAIL", "axis": axis, "detail": f"HTTP {status}"}

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {"status": "FAIL", "axis": axis, "detail": "non-JSON body (조회 실패)"}

    # 200 + `ok: false`는 공지 없이 실패한 응답이다. 계약 문서가 규정한 실패 구조
    # 그대로이므로, 공지 shape이 아니라는 이유로 그린이 되면 안 된다 — WARN은
    # 서비스가 스스로 밝힌 중단에만 준다 (PR #269 codex 리뷰).
    if isinstance(payload, dict) and payload.get("ok") is False:
        reason = payload.get("error") or "사유 미상"
        return {"status": "FAIL", "axis": axis, "detail": f"ok: false ({reason}) — 조회 실패"}

    summary = summarize_beopmang(payload)
    return {"status": "OK", "axis": axis, "detail": summary}


def summarize_beopmang(payload: Any) -> str:
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, dict) and "total" in data:
            return f"200 + JSON, total={data['total']}"
        results = payload.get("results")
        if isinstance(results, list):
            return f"200 + JSON, results={len(results)}"
        if isinstance(data, dict) and isinstance(data.get("results"), list):
            return f"200 + JSON, results={len(data['results'])}"
    return "200 + JSON"


def check_link(label: str, url: str, dns_only: bool = False) -> dict[str, Any]:
    axis = f"링크/{label}"
    if dns_only:
        host = urllib.parse.urlsplit(url).hostname or ""
        try:
            socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
        except OSError as exc:
            return {
                "status": "FAIL",
                "axis": axis,
                "detail": f"DNS 미해석 — 도메인 사망 의심: {exc} ({host})",
            }
        return {"status": "OK", "axis": axis, "detail": f"DNS resolved ({host})"}
    status, _body, err = http_get(url)
    if status == 200:
        return {"status": "OK", "axis": axis, "detail": f"HTTP 200 ({url})"}
    if status is None:
        return {"status": "FAIL", "axis": axis, "detail": f"{err} ({url})"}
    return {"status": "FAIL", "axis": axis, "detail": f"HTTP {status} ({url})"}


def format_line(check: dict[str, Any]) -> str:
    tag = f"[{check['status']}]"
    return f"{tag:<{STATUS_WIDTH + 2}} {check['axis']:<28} {check['detail']}"


def summarize(checks: list[dict[str, Any]]) -> tuple[str, int]:
    counts = {"OK": 0, "WARN": 0, "FAIL": 0, "NOT_INSTALLED": 0}
    for check in checks:
        counts[check["status"]] = counts.get(check["status"], 0) + 1
    if counts["FAIL"]:
        result = "FAIL"
        exit_code = 1
    elif counts["WARN"]:
        result = "WARN"
        exit_code = 0
    else:
        result = "OK"
        exit_code = 0
    line = (
        f"RESULT: {result} "
        f"(ok={counts['OK']} warn={counts['WARN']} "
        f"fail={counts['FAIL']} not_installed={counts['NOT_INSTALLED']})"
    )
    return line, exit_code


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="소스 도달성 헬스체크 (미러 / 법망 / 링크)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="리포트 끝에 machine-readable JSON 출력",
    )
    parser.add_argument(
        "--dns-links",
        action="store_true",
        help="국외 vantage(CI)용: 링크 축은 DNS 해석만 판정, 법망 축 실패는 WARN",
    )
    return parser.parse_args(argv)


def run_checks(dns_links: bool = False) -> list[dict[str, Any]]:
    checks = [check_mirror(family) for family in SOURCE_FAMILIES]
    beopmang = check_beopmang()
    if dns_links and beopmang["status"] == "FAIL":
        # 국외 vantage에서는 법망의 HTTP 판정이 신뢰 불가(geo 차이) — 보류.
        beopmang = {
            "status": "WARN",
            "axis": beopmang["axis"],
            "detail": f"{beopmang['detail']} — 국외 vantage, 판정 보류",
        }
    checks.append(beopmang)
    checks.extend(check_link(label, url, dns_only=dns_links) for label, url in LINK_CHECKS)
    return checks


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    checks = run_checks(dns_links=args.dns_links)
    for check in checks:
        print(format_line(check))
    summary_line, exit_code = summarize(checks)
    print(summary_line)
    if args.json:
        print(
            json.dumps(
                {
                    "result": summary_line.split()[1],
                    "checks": checks,
                    "summary": summary_line,
                },
                ensure_ascii=False,
            )
        )
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
