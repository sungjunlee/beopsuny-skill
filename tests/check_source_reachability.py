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
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
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
            "detail": "Lite 경로 사용 (실패 아님)",
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
            f"upstream 불일치 — 재동기화 필요 "
            f"(local {head[:11]}, upstream {remote_head[:11]}, last_commit={iso})"
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


def check_beopmang() -> dict[str, Any]:
    # 조회 실패는 개정 없음이 아니다 — 이 헬스체크는 스킬 계약의 실패 의미론을 따른다.
    axis = "법망 API"
    status, body, err = http_get(BEOPMANG_SEARCH_URL)
    text = body.decode("utf-8", errors="replace")

    if err == "timeout" or "timeout" in err.lower():
        return {"status": "FAIL", "axis": axis, "detail": "timeout (조회 실패)"}
    if status is None:
        return {"status": "FAIL", "axis": axis, "detail": f"{err} (조회 실패)"}
    if "service_maintenance" in text:
        return {
            "status": "FAIL",
            "axis": axis,
            "detail": "service_maintenance (조회 실패 ≠ 개정 없음)",
        }
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


def check_link(label: str, url: str) -> dict[str, Any]:
    axis = f"링크/{label}"
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
    return parser.parse_args(argv)


def run_checks() -> list[dict[str, Any]]:
    checks = [check_mirror(family) for family in SOURCE_FAMILIES]
    checks.append(check_beopmang())
    checks.extend(check_link(label, url) for label, url in LINK_CHECKS)
    return checks


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    checks = run_checks()
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
