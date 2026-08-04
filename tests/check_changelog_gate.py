"""PR changelog gate (#295).

계약 표면(CONTRACT_SURFACE_PATHS)을 건드린 pull request가 CHANGELOG.md 없이
CI 그린을 받는 경로를 닫는다. 그 상수가 대상 경로 집합의 단일 소스다 —
워크플로 YAML이나 다른 곳에 이 목록을 리터럴로 다시 적지 않는다 (#278이
구조 검사로 대체한 두 곳 리터럴 패턴).

- pull_request 이벤트에서만 판정한다. main push는 squash 후 비교 대상이
  애매해 판정하지 않는다 — 워크플로 step의 if가 1차 방어, 여기의
  GITHUB_EVENT_NAME 확인이 2차 방어다.
- diff는 merge-base 대비다: ``git diff <base.sha>...HEAD`` (three-dot).
- 예외는 PR 본문 또는 범위 내 커밋 메시지의 ``no-changelog:`` 마커 +
  사유뿐이다. 마커가 있어도 사유가 비어 있으면 예외로 인정하지 않는다 —
  사유 없는 예외 게이트는 우회 수단으로 퇴화한다.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 단일 소스: 계약 표면 경로 집합. tests/는 이 레포의 검증 계층이라 포함한다.
CONTRACT_SURFACE_PATHS = (
    "skills/",
    "tests/",
    "spec/",
    "README.md",
)

CHANGELOG_PATH = "CHANGELOG.md"
NO_CHANGELOG_MARKER = "no-changelog:"

# 줄 앞의 마커 + 비어 있지 않은 사유. 불릿(- / *)과 인용(>) 프리픽스는 허용한다.
MARKER_RE = re.compile(r"^\s*(?:[-*>]\s*)*no-changelog:\s*(?P<reason>\S.*?)\s*$")


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def changed_paths(base_sha: str) -> list[str]:
    """merge-base 대비 HEAD diff의 변경 파일 목록."""
    proc = _git("diff", "--name-only", f"{base_sha}...HEAD")
    if proc.returncode != 0:
        raise SystemExit(
            f"git diff {base_sha}...HEAD 실패: {proc.stderr.strip() or proc.stdout.strip()}"
        )
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def touches_contract_surface(paths: list[str]) -> bool:
    for path in paths:
        if path == CHANGELOG_PATH:
            continue
        if any(path == surface or path.startswith(surface) for surface in CONTRACT_SURFACE_PATHS):
            return True
    return False


def commit_messages(base_sha: str) -> list[str]:
    proc = _git("log", "--format=%B", f"{base_sha}..HEAD")
    if proc.returncode != 0:
        raise SystemExit(
            f"git log {base_sha}..HEAD 실패: {proc.stderr.strip() or proc.stdout.strip()}"
        )
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def exempted(sources: list[str]) -> bool:
    """no-changelog: 마커 + 사유가 있으면 True. 사유 없는 마커는 예외가 아니다."""
    for source in sources:
        for line in source.splitlines():
            if MARKER_RE.match(line):
                return True
    return False


def main() -> int:
    if os.environ.get("GITHUB_EVENT_NAME") != "pull_request":
        print("SKIP: pull_request 이벤트가 아니다 (main push 등) — 비교 대상이 애매해 판정하지 않는다")
        return 0

    event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    if not event_path or not os.path.isfile(event_path):
        print("SKIP: GITHUB_EVENT_PATH가 없다 — GitHub Actions 컨텍스트가 아니다")
        return 0
    with open(event_path, encoding="utf-8") as handle:
        event = json.load(handle)
    pull_request = event.get("pull_request") or {}
    base_sha = (pull_request.get("base") or {}).get("sha")
    if not base_sha:
        print("SKIP: pull_request.base.sha가 없다")
        return 0

    paths = changed_paths(base_sha)
    if not touches_contract_surface(paths):
        print("PASS: 계약 표면 변경 없음")
        return 0
    if CHANGELOG_PATH in paths:
        print("PASS: CHANGELOG.md가 함께 바뀌었다")
        return 0

    sources = [pull_request.get("body") or ""]
    sources.extend(commit_messages(base_sha))
    if exempted(sources):
        print("PASS: no-changelog: 마커 + 사유 (예외 경로)")
        return 0

    print(
        "FAIL: 계약 표면이 바뀌었는데 CHANGELOG.md가 없다 — "
        "README 품질 계약 변경 체크리스트 7단계를 지키거나, 예외라면 "
        "PR 본문/커밋 메시지에 'no-changelog: <사유>'를 남긴다."
    )
    print(f"변경 파일: {paths}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
