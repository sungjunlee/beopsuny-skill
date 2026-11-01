#!/usr/bin/env python3
"""차등 재채점 게이트의 회귀 테스트 (#294).

게이트 로직(diff 분류·방향 메시지·결정론 직렬화)과, **커밋된 baseline이 현재
스코어러 판정과 일치하는지**를 검증한다 — 후자의 테스트가 곧 게이트다. 계약의
집은 `tests/check_rescore_baseline.py` docstring이고 여기는 포인터다.
"""

from __future__ import annotations

import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

import yaml

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

    def test_empty_capture_is_unscorable_without_model_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.yaml"
            path.write_text(json.dumps({
                "source_eval": "tests/forward_evals/beopsuny_guardrails.yaml",
                "outputs": {"fwd-03-business-user-external-reply": ""}}))
            with patch.object(self.check, "EVIDENCE_DIR", Path(directory)):
                result = self.check.rescore_all()
            prompt_id = "fwd-03-business-user-external-reply"
            self.assertEqual(result["failures"]["empty"][prompt_id],
                             ["UNSCORABLE: captured execution did not complete"])
            self.assertEqual(result["inventory"]["empty"], [prompt_id])

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
        relaxed, tightened, inventory = self.check.classify_diffs(actual, baseline)
        # c1/p1 실패가 사라졌다 → 완화. c2/p2에 새 실패 → 조임. c3는 변화 없음.
        # 구형 실패 맵은 inventory를 선언하지 않는다.
        self.assertEqual(relaxed, {"c1": {"p1": ["msg-a"]}})
        self.assertEqual(tightened, {"c2": {"p2": ["msg-y"]}})
        self.assertIsNone(inventory)

    def test_message_level_diff_catches_partial_relaxation(self) -> None:
        """같은 prompt의 일부 실패만 사라져도 완화로 잡힌다 — 전부 통과해야만
        잡히는 판정 단위로는 #282 형태(일부 FAIL 메시지 소실)가 놓친다."""
        baseline = {"c1": {"p1": ["msg-a", "msg-b"]}}
        actual = {"c1": {"p1": ["msg-b"]}}
        relaxed, tightened, inventory = self.check.classify_diffs(actual, baseline)
        self.assertEqual(relaxed, {"c1": {"p1": ["msg-a"]}})
        self.assertEqual(tightened, {})
        self.assertIsNone(inventory)

    def test_build_report_fails_with_direction_and_stronger_relaxation_wording(
        self,
    ) -> None:
        baseline = {"c1": {"p1": ["old-failure"]}, "c2": {"p2": ["kept"]}}
        actual = {"c1": {}, "c2": {"p2": ["kept", "new-failure"]}}
        report, exit_code = self.check.build_report(actual, baseline)
        self.assertEqual(exit_code, 1)
        self.assertIn("제거 1건", report)
        self.assertIn("추가 1건", report)
        self.assertIn("[완화]", report)
        self.assertIn("[조임]", report)
        # 완화는 조임보다 강한 문구 — 이 레포의 사고 방향 (#282).
        relaxation_block = report.split("[완화]")[1].split("[조임]")[0]
        self.assertIn("느슨해졌다", relaxation_block)
        self.assertIn("근거를 남긴다", relaxation_block)

    def test_pending_report_is_not_model_failure_or_tightening(self) -> None:
        report, exit_code = self.check.build_report({"c": {"p": ["REVIEW_REQUIRED: missing review"]}}, {"c": {}})
        self.assertEqual(exit_code, 1)
        self.assertIn("[미검토/채점불가]", report)
        self.assertNotIn("[조임]", report)
        self.assertIn("모델 실패가 아니다", report)

    def test_removed_pending_is_not_relaxation(self) -> None:
        for pending in ("REVIEW_REQUIRED: missing", "UNSCORABLE: setup missing"):
            report, code = self.check.build_report({"c": {}}, {"c": {"p": [pending]}})
            self.assertEqual(code, 1)
            self.assertIn("[검토/채점 상태 변경]", report)
            self.assertNotIn("[완화]", report)
            report, code = self.check.build_report({"c": {}}, {"c": {"p": [pending, "real failure"]}})
            self.assertIn("baseline 실패 1건", report)
            self.assertIn("[완화]", report)

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


# #303: 하네스가 커밋된 evidence를 다시 채점하던 검사. 차등 재채점 스캔이
# 유일한 집이다. 이 목록에서 빼면서 하네스 (b) 테스트도 없으면 커버리지가
# 사라지므로, 아래 mutation이 그 상태를 FAIL로 만든다.
ABSORBED_CORPUS_STEMS = (
    "guardrails-live-sonnet5-20260709",
    "fwd02-recheck-live-sonnet5-20260710",
    "guardrails-live-sonnet5-20260710-v050",
    "o4-live-driver-sonnet5-20260710",
    "guardrails-live-sonnet5-20260720-v051",
    "o4-live-sonnet5-20260720-v051",
    "guardrails-live-sonnet5-20260725-v070",
)

HARNESS_TEST_PATH = ROOT / "tests/test_forward_eval_harness.py"

class AbsorbedHarnessCorpusTests(unittest.TestCase):
    """#303: (b) 채점 재현을 baseline 스캔으로 이관한 뒤의 mutation.

    (b) 테스트를 지우고 이 스템들이 스캔·baseline에도 없으면 커버리지가
    조용히 사라진다 — 그 상태가 여기서 FAIL이어야 한다.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.check = load_check()
        cls.actual = cls.check.rescore_all()
        try:
            cls.baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise AssertionError(
                f"baseline 파일을 읽지 못했다 — --write-baseline으로 생성해야 한다: {exc}"
            ) from exc

    def test_absorbed_corpora_remain_in_the_baseline_scan(self) -> None:
        """하네스 (b)를 지운 뒤 evidence glob이 이 스템을 빠뜨리면 FAIL."""
        evidence_stems = {
            path.stem
            for path in (ROOT / "tests/forward_evals/evidence").glob("*.yaml")
        }
        missing_files = sorted(set(ABSORBED_CORPUS_STEMS) - evidence_stems)
        missing_scan = sorted(set(ABSORBED_CORPUS_STEMS) - set(self.actual["failures"]))
        missing_inventory = sorted(set(ABSORBED_CORPUS_STEMS) - set(self.actual["inventory"]))
        missing_baseline = sorted(set(ABSORBED_CORPUS_STEMS) - set(self.baseline["failures"]))
        missing_baseline_inventory = sorted(
            set(ABSORBED_CORPUS_STEMS) - set(self.baseline["inventory"])
        )
        self.assertEqual([], missing_files)
        self.assertEqual([], missing_scan)
        self.assertEqual([], missing_inventory)
        self.assertEqual([], missing_baseline)
        self.assertEqual([], missing_baseline_inventory)
        self.assertEqual(2, self.baseline.get("schema"))

    def test_harness_tests_do_not_rescore_absorbed_evidence(self) -> None:
        """한 개념 한 집 — 흡수된 corpus 스템이 하네스 테스트로 되돌아오면 FAIL."""
        text = HARNESS_TEST_PATH.read_text(encoding="utf-8")
        returned = [stem for stem in ABSORBED_CORPUS_STEMS if stem in text]
        self.assertEqual([], returned)

    def test_absorbed_corpus_anchor_judgments(self) -> None:
        """정적 실위반과 현재 의미 검토 대기를 구별한다.

        전체 메시지와 corpus별 판정은 baseline 일치 검사가 잠근다.
        과거 키워드 PASS/FAIL을 현재 의미 판정으로 재사용하지 않는다.
        """
        failures = self.actual["failures"]
        july09 = failures["guardrails-live-sonnet5-20260709"]
        self.assertTrue(any("forbidden failure phrase" in message
                            for message in july09["fwd-02-law-change-automation-request"]))
        self.assertNotIn("fwd-02-law-change-automation-request",
                         failures["fwd02-recheck-live-sonnet5-20260710"])
        for stem in ("guardrails-live-sonnet5-20260710-v050",
                     "guardrails-live-sonnet5-20260720-v051"):
            messages = failures[stem]["fwd-08-profile-write-boundary"]
            self.assertTrue(messages)
            self.assertTrue(all(message.startswith("REVIEW_REQUIRED:") for message in messages))
        messages = failures["guardrails-live-sonnet5-20260725-v070"]["fwd-11-shape-deviating-verification"]
        self.assertTrue(messages)
        self.assertTrue(all(message.startswith("REVIEW_REQUIRED:") for message in messages))

    def test_passed_inputs_are_inventoried_without_empty_messages(self) -> None:
        """통과 corpus는 실패 맵이 비어도 원래 id를 보존한다. 빈 배열로 채우지 않는다."""
        stem = "fwd02-recheck-live-sonnet5-20260710"
        self.assertEqual(self.actual["failures"][stem], {})
        self.assertEqual(
            self.actual["inventory"][stem],
            ["fwd-02-law-change-automation-request"],
        )
        for corpus, prompts in self.actual["failures"].items():
            self.assertTrue(set(prompts) <= set(self.actual["inventory"][corpus]))
            for messages in prompts.values():
                self.assertTrue(messages)


PASS_ID = "fwd-03-business-user-external-reply"
FAIL_ID = "fwd-02-law-change-automation-request"
PASS_ALT_ID = "fwd-04-stale-checklist-current-obligation"
SOURCE_EVAL = "tests/forward_evals/beopsuny_guardrails.yaml"


class RescoreInventoryTests(unittest.TestCase):
    """#373: 통과 입력 누락과 빈 outputs는 내용 판정과 따로 실패한다."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.check = load_check()
        cls.harness = cls.check.load_harness()
        config = cls.harness.load_forward_eval(
            ROOT / "tests/forward_evals/beopsuny_guardrails.yaml"
        )
        cls.prompts = {str(prompt["id"]): prompt for prompt in config["prompts"]}
        cls.samples = cls.harness.SAMPLE_OUTPUTS

    def write_capture(
        self,
        directory: Path,
        outputs: dict[str, str],
        rows: list[dict[str, Any]] | None = None,
    ) -> None:
        for old in directory.glob("*.yaml"):
            old.unlink()
        payload: dict[str, Any] = {"source_eval": SOURCE_EVAL, "outputs": outputs}
        if rows is not None:
            payload["prompts"] = rows
        (directory / "case.yaml").write_text(
            yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    def rescore(self, directory: Path) -> dict[str, Any]:
        with patch.object(self.check, "EVIDENCE_DIR", directory):
            return self.check.rescore_all()

    def test_omitted_passing_id_is_not_a_content_match(self) -> None:
        fail_output = "루틴이 생성되었습니다"
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.write_capture(
                directory,
                {PASS_ID: self.samples[PASS_ID], FAIL_ID: fail_output},
            )
            before = self.rescore(directory)
            self.assertNotIn(PASS_ID, before["failures"]["case"])
            self.assertIn(FAIL_ID, before["failures"]["case"])
            self.assertEqual(before["inventory"]["case"], sorted([PASS_ID, FAIL_ID]))
            self.write_capture(directory, {FAIL_ID: fail_output})
            after = self.rescore(directory)
            self.assertEqual(before["failures"]["case"][FAIL_ID], after["failures"]["case"][FAIL_ID])
            self.assertNotIn(PASS_ID, after["inventory"]["case"])
            self.assertNotEqual(
                self.check.serialize_failures(before),
                self.check.serialize_failures(after),
            )
            report, code = self.check.build_report(after, before)
            self.assertEqual(code, 1)
            self.assertIn("[입력 누락]", report)
            self.assertIn(PASS_ID, report)
            self.assertNotIn("[완화]", report)
            self.assertNotIn("[조임]", report)
            relaxed, tightened, inventory = self.check.classify_diffs(after, before)
            self.assertEqual(relaxed, {})
            self.assertEqual(tightened, {})
            self.assertEqual(inventory["missing"], {"case": [PASS_ID]})

    def test_empty_outputs_do_not_match_an_all_pass_capture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.write_capture(
                directory,
                {PASS_ID: self.samples[PASS_ID], PASS_ALT_ID: self.samples[PASS_ALT_ID]},
            )
            before = self.rescore(directory)
            self.assertEqual(before["failures"]["case"], {})
            self.assertEqual(before["inventory"]["case"], sorted([PASS_ID, PASS_ALT_ID]))
            self.write_capture(directory, {})
            after = self.rescore(directory)
            self.assertEqual(after["failures"]["case"], {})
            self.assertEqual(after["inventory"]["case"], [])
            report, code = self.check.build_report(after, before)
            self.assertEqual(code, 1)
            self.assertNotIn("PASS:", report)
            self.assertIn("[입력 누락]", report)
            self.assertIn(PASS_ID, report)
            self.assertIn(PASS_ALT_ID, report)
            self.assertNotIn("[완화]", report)

    def test_timeout_record_without_output_is_unscorable_not_relaxation(self) -> None:
        fail_output = "루틴이 생성되었습니다"
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.write_capture(
                directory,
                {PASS_ID: self.samples[PASS_ID], FAIL_ID: fail_output},
            )
            before = self.rescore(directory)
            self.write_capture(
                directory,
                {FAIL_ID: fail_output},
                rows=[
                    {"prompt_id": PASS_ID, "execution": {"execution_status": "timeout"}},
                    {"prompt_id": FAIL_ID, "execution": {"execution_status": "completed"}},
                ],
            )
            after = self.rescore(directory)
            self.assertEqual(
                after["failures"]["case"][PASS_ID],
                ["UNSCORABLE: captured output missing"],
            )
            self.assertIn(PASS_ID, after["inventory"]["case"])
            report, code = self.check.build_report(after, before)
            self.assertEqual(code, 1)
            self.assertIn("[미검토/채점불가]", report)
            self.assertIn("모델 실패가 아니다", report)
            self.assertNotIn("[완화]", report)
            self.assertNotIn("[조임]", report)
            self.assertNotIn("[입력 누락]", report)

    def test_empty_string_stays_unscorable_and_is_not_model_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.write_capture(directory, {PASS_ID: self.samples[PASS_ID]})
            before = self.rescore(directory)
            self.write_capture(directory, {PASS_ID: ""})
            after = self.rescore(directory)
            self.assertEqual(
                after["failures"]["case"][PASS_ID],
                ["UNSCORABLE: captured execution did not complete"],
            )
            self.assertEqual(after["inventory"]["case"], [PASS_ID])
            report, code = self.check.build_report(after, before)
            self.assertEqual(code, 1)
            self.assertIn("[미검토/채점불가]", report)
            self.assertIn("모델 실패가 아니다", report)
            self.assertNotIn("[완화]", report)
            self.assertNotIn("[조임]", report)

    def test_added_id_is_not_tightening_and_partial_capture_stays_partial(self) -> None:
        baseline = {
            "schema": 2,
            "failures": {"case": {FAIL_ID: ["real failure"]}},
            "inventory": {"case": [FAIL_ID]},
        }
        actual = {
            "schema": 2,
            "failures": {"case": {FAIL_ID: ["real failure"]}},
            "inventory": {"case": sorted([FAIL_ID, PASS_ID])},
        }
        relaxed, tightened, inventory = self.check.classify_diffs(actual, baseline)
        self.assertEqual(relaxed, {})
        self.assertEqual(tightened, {})
        self.assertEqual(inventory["added"], {"case": [PASS_ID]})
        report, code = self.check.build_report(actual, baseline)
        self.assertEqual(code, 1)
        self.assertIn("[입력 추가]", report)
        self.assertIn(PASS_ID, report)
        self.assertNotIn("[조임]", report)
        self.assertNotIn("[완화]", report)
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.write_capture(directory, {PASS_ID: self.samples[PASS_ID]})
            scored = self.rescore(directory)
        self.assertEqual(scored["inventory"]["case"], [PASS_ID])
        self.assertGreater(len(self.prompts), 1)
        self.assertFalse(set(self.prompts) <= set(scored["inventory"]["case"]))

    def test_legacy_baseline_without_inventory_is_not_a_pass(self) -> None:
        actual = {
            "schema": 2,
            "failures": {"case": {FAIL_ID: ["real failure"]}},
            "inventory": {"case": [FAIL_ID]},
        }
        legacy = {"case": {FAIL_ID: ["real failure"]}}
        report, code = self.check.build_report(actual, legacy)
        self.assertEqual(code, 1)
        self.assertIn("입력 inventory가 없다", report)
        self.assertNotIn("[완화]", report)
        self.assertNotIn("[입력 누락]", report)
        self.assertNotIn("PASS:", report)

    def test_cli_report_detects_omission_and_empty_outputs(self) -> None:
        fail_output = "루틴이 생성되었습니다"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = root / "evidence"
            evidence.mkdir()
            baseline = root / "baseline.json"
            self.write_capture(
                evidence,
                {PASS_ID: self.samples[PASS_ID], FAIL_ID: fail_output},
            )
            with patch.object(self.check, "EVIDENCE_DIR", evidence), patch.object(
                self.check, "BASELINE_PATH", baseline
            ):
                write_buf = io.StringIO()
                with redirect_stdout(write_buf):
                    self.assertEqual(self.check.main(["--write-baseline"]), 0)
                self.write_capture(evidence, {FAIL_ID: fail_output})
                omit_buf = io.StringIO()
                with redirect_stdout(omit_buf):
                    omit_code = self.check.main([])
                self.write_capture(
                    evidence,
                    {PASS_ID: self.samples[PASS_ID], PASS_ALT_ID: self.samples[PASS_ALT_ID]},
                )
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(self.check.main(["--write-baseline"]), 0)
                self.write_capture(evidence, {})
                empty_buf = io.StringIO()
                with redirect_stdout(empty_buf):
                    empty_code = self.check.main([])
        self.assertEqual(omit_code, 1)
        omit_report = omit_buf.getvalue()
        self.assertIn("[입력 누락]", omit_report)
        self.assertIn(PASS_ID, omit_report)
        self.assertNotIn("[완화]", omit_report)
        self.assertEqual(empty_code, 1)
        empty_report = empty_buf.getvalue()
        self.assertIn("[입력 누락]", empty_report)
        self.assertNotIn("PASS:", empty_report)
        self.assertNotIn("[완화]", empty_report)


if __name__ == "__main__":
    unittest.main()
