#!/usr/bin/env python3
"""CHANGELOG 게이트가 rename의 원래 경로를 보는지 (#370).

`git diff --name-only`는 rename을 목적지만 돌려준다. 보호 경로에서 밖으로
옮기면 계약 표면 판정이 조용히 빠진다. 회귀는 격리된 Git 저장소의 실제
rename 결과를 쓴다.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))

import check_changelog_gate as gate  # noqa: E402


class TempRepo:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.git("init", "-b", "main")
        self.git("config", "user.email", "changelog-gate@example.com")
        self.git("config", "user.name", "Changelog Gate Test")
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "diff.renames", "true")

    def git(self, *args: str) -> str:
        proc = subprocess.run(
            ["git", "-C", str(self.path), *args],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            detail = proc.stderr.strip() or proc.stdout.strip()
            raise AssertionError(f"git {' '.join(args)} failed: {detail}")
        return proc.stdout

    def write(self, relative: str, text: str) -> None:
        path = self.path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def commit_all(self, message: str) -> str:
        self.git("add", "-A")
        self.git("commit", "-m", message)
        return self.git("rev-parse", "HEAD").strip()


class ChangelogRenameGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = TempRepo(Path(self.tmp.name))
        self.addCleanup(self.tmp.cleanup)

    def _paths_from(self, base: str) -> list[str]:
        original = gate.ROOT
        gate.ROOT = self.repo.path
        try:
            return gate.changed_paths(base)
        finally:
            gate.ROOT = original

    def _run_gate(self, base: str, body: str = "") -> tuple[int, str]:
        event = {"pull_request": {"base": {"sha": base}, "body": body}}
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
            json.dump(event, handle)
            event_path = handle.name
        self.addCleanup(lambda: os.unlink(event_path) if os.path.exists(event_path) else None)
        original = gate.ROOT
        gate.ROOT = self.repo.path
        stdout = StringIO()
        try:
            with mock.patch.dict(
                os.environ,
                {"GITHUB_EVENT_NAME": "pull_request", "GITHUB_EVENT_PATH": event_path},
            ):
                with redirect_stdout(stdout):
                    code = gate.main()
        finally:
            gate.ROOT = original
        return code, stdout.getvalue()

    def test_move_out_of_contract_surface_fails_without_changelog_or_exemption(self) -> None:
        self.repo.write("skills/example.md", "contract surface\n")
        base = self.repo.commit_all("add protected file")
        (self.repo.path / "archive").mkdir()
        self.repo.git("mv", "skills/example.md", "archive/example.md")
        self.repo.commit_all("move out of the contract surface")

        # rename 감지가 켜져 있어야 이 테스트가 버그를 실제로 건드린다.
        raw = self.repo.git("diff", "--name-only", f"{base}...HEAD")
        self.assertEqual(["archive/example.md"], [line for line in raw.splitlines() if line.strip()])

        paths = self._paths_from(base)
        self.assertIn("skills/example.md", paths)
        self.assertIn("archive/example.md", paths)
        self.assertTrue(gate.touches_contract_surface(paths))

        code, output = self._run_gate(base)
        self.assertEqual(1, code)
        self.assertIn("FAIL", output)
        self.assertIn("skills/example.md", output)

        code, output = self._run_gate(base, body="no-changelog:")
        self.assertEqual(1, code)
        self.assertIn("FAIL", output)

        code, output = self._run_gate(base, body="- no-changelog: 보관 이동이며 계약 내용은 같다")
        self.assertEqual(0, code)
        self.assertIn("예외 경로", output)

    def test_edit_delete_and_move_inside_the_surface_stay_visible(self) -> None:
        self.repo.write("skills/example.md", "contract surface\n")
        base = self.repo.commit_all("add protected file")
        self.repo.write("skills/example.md", "contract surface\nchanged\n")
        self.repo.commit_all("edit protected file")
        paths = self._paths_from(base)
        self.assertIn("skills/example.md", paths)
        self.assertTrue(gate.touches_contract_surface(paths))
        code, output = self._run_gate(base)
        self.assertEqual(1, code)
        self.assertIn("FAIL", output)

        delete_base = self.repo.git("rev-parse", "HEAD").strip()
        self.repo.git("rm", "skills/example.md")
        self.repo.commit_all("delete protected file")
        paths = self._paths_from(delete_base)
        self.assertIn("skills/example.md", paths)
        code, _output = self._run_gate(delete_base)
        self.assertEqual(1, code)

        self.repo.write("skills/example.md", "back\n")
        inside_base = self.repo.commit_all("restore protected file")
        (self.repo.path / "skills" / "nested").mkdir()
        self.repo.git("mv", "skills/example.md", "skills/nested/example.md")
        self.repo.commit_all("move inside the contract surface")
        paths = self._paths_from(inside_base)
        self.assertTrue(any(path.startswith("skills/") for path in paths))
        self.assertTrue(gate.touches_contract_surface(paths))
        code, _output = self._run_gate(inside_base)
        self.assertEqual(1, code)

    def test_unprotected_edits_and_valid_commit_exemption_pass(self) -> None:
        self.repo.write("archive/note.md", "note\n")
        base = self.repo.commit_all("add unprotected note")
        self.repo.write("archive/note.md", "note changed\n")
        self.repo.commit_all("edit unprotected note")
        paths = self._paths_from(base)
        self.assertEqual(["archive/note.md"], paths)
        self.assertFalse(gate.touches_contract_surface(paths))
        code, output = self._run_gate(base)
        self.assertEqual(0, code)
        self.assertIn("계약 표면 변경 없음", output)

        self.repo.write("skills/example.md", "contract surface\n")
        move_base = self.repo.commit_all("add protected file")
        self.repo.git("mv", "skills/example.md", "archive/example.md")
        self.repo.commit_all("move out\n\nno-changelog: 커밋 메시지의 사유 있는 예외")
        code, output = self._run_gate(move_base)
        self.assertEqual(0, code)
        self.assertIn("예외 경로", output)

        self.repo.write("skills/again.md", "another\n")
        changelog_base = self.repo.commit_all("add another protected file")
        self.repo.git("mv", "skills/again.md", "archive/again.md")
        self.repo.write("CHANGELOG.md", "unreleased note\n")
        self.repo.commit_all("record the move")
        paths = self._paths_from(changelog_base)
        self.assertIn("skills/again.md", paths)
        self.assertIn("CHANGELOG.md", paths)
        code, output = self._run_gate(changelog_base)
        self.assertEqual(0, code)
        self.assertIn("CHANGELOG.md", output)


if __name__ == "__main__":
    unittest.main()
