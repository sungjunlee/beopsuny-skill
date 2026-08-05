#!/usr/bin/env python3
"""차등 재채점 게이트의 회귀 테스트 (#294).

게이트 로직(diff 분류·방향 메시지·결정론 직렬화)과, **커밋된 baseline이 현재
스코어러 판정과 일치하는지**를 검증한다 — 후자의 테스트가 곧 게이트다. 계약의
집은 `tests/check_rescore_baseline.py` docstring이고 여기는 포인터다.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHECK_PATH = ROOT / "tests/check_rescore_baseline.py"
BASELINE_PATH = ROOT / "tests/forward_evals/rescore_baseline.json"


def load_check() -> Any:
    spec = importlib.util.spec_from_file_location("check_rescore_baseline", CHECK_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load {CHECK_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RescoreBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.check = load_check()
        # 전량 스캔은 한 번만 — 아래 여러 테스트가 같은 스냅샷을 쓴다.
        cls.actual = cls.check.rescore_all()

    def test_rescore_is_deterministic_and_matches_committed_baseline(self) -> None:
        """게이트 본체: 스캔 결과가 체크인된 baseline과 정확히 일치해야 한다.

        스코어러/하네스 판정 로직을 건드린 PR은 `--write-baseline`으로 이 파일을
        함께 갱신해야 여기가 그린이다 — 완화든 조임든 조용한 통과가 불가능하다.
        """
        serialized = self.check.serialize_failures(self.actual)
        try:
            baseline_text = BASELINE_PATH.read_text(encoding="utf-8")
        except OSError as exc:
            # 게이트 테스트 — baseline이 없으면 실패가 맞다. "채점 불가"를
            # 조용한 통과로 바꾸지 않는다.
            self.fail(
                f"baseline 파일을 읽지 못했다 — --write-baseline으로 생성해야 한다: {exc}"
            )
        self.assertEqual(serialized, baseline_text)

    def test_serialization_is_byte_stable(self) -> None:
        self.assertEqual(
            self.check.serialize_failures(self.actual),
            self.check.serialize_failures(self.actual),
        )
        # JSON 파싱 라운드트립도 동일한 바이트여야 한다 (write→read→write churn 없음).
        try:
            parsed = json.loads(self.check.serialize_failures(self.actual))
        except json.JSONDecodeError as exc:
            self.fail(f"직렬화 결과가 JSON이 아니다: {exc}")
        self.assertEqual(
            self.check.serialize_failures(parsed),
            self.check.serialize_failures(self.actual),
        )

    def test_classify_diffs_detects_relaxation_and_tightening(self) -> None:
        baseline = {
            "c1": {"p1": ["msg-a"]},
            "c2": {"p2": ["msg-x"]},
            "c3": {},
        }
        actual = {
            "c1": {},
            "c2": {"p2": ["msg-x", "msg-y"]},
            "c3": {},
        }
        relaxed, tightened = self.check.classify_diffs(actual, baseline)
        # c1/p1 실패가 사라졌다 → 완화. c2/p2에 새 실패 → 조임. c3는 변화 없음.
        self.assertEqual(relaxed, {"c1": {"p1": ["msg-a"]}})
        self.assertEqual(tightened, {"c2": {"p2": ["msg-y"]}})

    def test_message_level_diff_catches_partial_relaxation(self) -> None:
        """같은 prompt의 일부 실패만 사라져도 완화로 잡힌다 — 전부 통과해야만
        잡히는 판정 단위로는 #282 형태(일부 FAIL 메시지 소실)가 놓친다."""
        baseline = {"c1": {"p1": ["msg-a", "msg-b"]}}
        actual = {"c1": {"p1": ["msg-b"]}}
        relaxed, tightened = self.check.classify_diffs(actual, baseline)
        self.assertEqual(relaxed, {"c1": {"p1": ["msg-a"]}})
        self.assertEqual(tightened, {})

    def test_build_report_fails_with_direction_and_stronger_relaxation_wording(
        self,
    ) -> None:
        baseline = {"c1": {"p1": ["old-failure"]}, "c2": {"p2": ["kept"]}}
        actual = {"c1": {}, "c2": {"p2": ["kept", "new-failure"]}}
        report, exit_code = self.check.build_report(actual, baseline)
        self.assertEqual(exit_code, 1)
        self.assertIn("완화 1건", report)
        self.assertIn("조임 1건", report)
        self.assertIn("[완화]", report)
        self.assertIn("[조임]", report)
        # 완화는 조임보다 강한 문구 — 이 레포의 사고 방향 (#282).
        relaxation_block = report.split("[완화]")[1].split("[조임]")[0]
        self.assertIn("느슨해졌다", relaxation_block)
        self.assertIn("근거를 남긴다", relaxation_block)

    def test_build_report_passes_when_identical(self) -> None:
        report, exit_code = self.check.build_report(self.actual, self.actual)
        self.assertEqual(exit_code, 0)
        self.assertIn("PASS", report)

    def test_write_baseline_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            # write_baseline은 모듈 상수 경로에 쓴다 — 테스트에서는 tmp 경로로
            # 직렬화 함수를 검증한다.
            data = {"c1": {"p1": ["m"]}, "c2": {}}
            serialized = self.check.serialize_failures(data)
            path = Path(tmpdir) / "baseline.json"
            path.write_text(serialized, encoding="utf-8")
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                self.fail(f"roundtrip 재읽기 실패: {exc}")
            self.assertEqual(
                self.check.serialize_failures(loaded),
                serialized,
            )


if __name__ == "__main__":
    unittest.main()
