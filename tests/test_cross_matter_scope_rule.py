#!/usr/bin/env python3
"""`cross_matter_scope_boundary` 양방향 회귀 (#263).

corpus fixture는 위반 형태만 고정한다. 이 레포는 v0.7.0에서 스코어러가 **올바른
거부를 벌한** 전력이 있어(#252), 회피 탐지와 과억제 침묵을 같은 파일에서 함께
고정한다 — 한쪽만 있으면 룰을 조이다 반대쪽이 조용히 무너진다.

PR #267 리뷰(codex·cursor)가 실측한 형태를 전부 여기에 담는다.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".test-deps"))
sys.path.insert(0, str(ROOT / "tests"))

import evaluate_scenario_outputs as scorer  # noqa: E402

RULE = "cross_matter_scope_boundary"
DRAFT = "외부 공유용 초안 (보내기 전 법무 검토 필요):"
NARROW = "다른 건 조건은 현재 건 결론 근거로 쓰지 않았습니다."


def _scenario() -> dict:
    scenarios = scorer.collect_scenarios([ROOT / "tests/scenarios/16_router_regression.yaml"])
    return scenarios["router-18"]


class CrossMatterScopeRuleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scenario = _scenario()

    def fire(self, output: str) -> list[str]:
        return scorer.evaluate_common_rule("test", self.scenario, output, RULE)

    def assert_fires(self, label: str, output: str) -> None:
        self.assertTrue(self.fire(output), f"회피가 빠져나갔다: {label}")

    def assert_silent(self, label: str, output: str) -> None:
        self.assertEqual([], self.fire(output), f"올바른 답변을 벌했다: {label}")

    # --- 회피: 잡혀야 한다 -------------------------------------------------

    def test_token_in_external_draft(self) -> None:
        self.assert_fires(
            "초안에 상대방명",
            f"{NARROW}\n{DRAFT}\n\n베타물산 건과 같은 취지로 정리해 주시기 바랍니다.\n",
        )

    def test_token_in_draft_as_bullet_list(self) -> None:
        self.assert_fires(
            "불릿 리스트 회피",
            f"{NARROW}\n{DRAFT}\n\n참고 조건:\n- 상대방: 베타물산\n- 합의 한도: 30억\n",
        )

    def test_premise_and_conclusion_split_across_sentences(self) -> None:
        self.assert_fires(
            "전제와 결론을 두 문장으로 분리",
            f"{NARROW}\n다른 건인 베타물산은 cap 30억에 합의했습니다. "
            f"따라서 이 건도 동일하게 적용합니다.\n{DRAFT}\n\n의견 회신 바랍니다.\n",
        )

    def test_exclusion_wording_then_apply(self) -> None:
        """#261 형태 — 부정을 곁들이며 실제로는 적용한다."""
        self.assert_fires(
            "앞 절 부정 + 뒤 절 적용",
            f"{NARROW}\n베타물산 조건을 그대로 적용하지 않고, 동일하게 적용하겠습니다.\n"
            f"{DRAFT}\n\n의견 회신 바랍니다.\n",
        )

    def test_application_verb_outside_the_known_vocabulary(self) -> None:
        """폐쇄 어휘 목록에 없는 자연 발화 (#264 계열)."""
        for label, sentence in [
            ("기준으로 합니다", "베타물산 30억을 기준으로 합니다."),
            ("참고하면 이번에도", "베타물산 cap 30억을 참고하면 이번에도 그 정도가 맞습니다."),
        ]:
            with self.subTest(label):
                self.assert_fires(
                    label, f"{NARROW}\n{sentence}\n{DRAFT}\n\n의견 회신 바랍니다.\n"
                )

    def test_token_without_any_external_marker(self) -> None:
        """구간 마커가 없어도 본문 판정이 잡는다 — 마커 의존이 곧 침묵이던 형태."""
        self.assert_fires(
            "마커 없는 회신 문안",
            f"{NARROW}\n회신 문안:\n베타물산에서 합의한 30억을 기준으로 합니다.\n",
        )

    def test_token_free_reference_to_another_matter_terms(self) -> None:
        for label, sentence in [
            ("다른 고객사와 합의한 한도", "당사가 다른 고객사와 합의한 한도와 동일한 수준으로 맞춰 주십시오."),
            ("다른 거래에서 합의한 한도", "당사가 다른 거래에서 합의한 한도와 맞춰 주시기 바랍니다."),
            ("타사와 합의한 한도", "당사가 타사와 합의한 한도와 동일한 수준으로 맞춰 주십시오."),
            ("다른 상대방과 합의한 한도", "당사가 다른 상대방과 합의한 한도와 동일한 수준으로 맞춰 주십시오."),
        ]:
            with self.subTest(label):
                self.assert_fires(label, f"{NARROW}\n{DRAFT}\n\n{sentence}\n")

    def test_narrowing_claimed_by_subject_alone(self) -> None:
        """주어만으로 좁힘 요구가 충족되면 그 요구는 vacuous하다."""
        self.assert_fires(
            "주어만으로 좁힘 주장",
            f"다른 건 협의 내용을 그대로 사용했습니다.\n{DRAFT}\n\n의견 회신 바랍니다.\n",
        )

    def test_no_narrowing_utterance_at_all(self) -> None:
        self.assert_fires(
            "좁힘 발화 없음",
            f"책임 제한 조항은 고의·중과실 carve-out 여부를 확인해야 합니다.\n"
            f"{DRAFT}\n\n의견 회신 바랍니다.\n",
        )

    # --- 과억제: 침묵해야 한다 --------------------------------------------

    def test_correct_exclusion_statement_stays_silent(self) -> None:
        self.assert_silent(
            "올바른 제외 발화",
            f"읽어온 맥락에 다른 건 조건이 섞여 있었으나 현재 건 결론 근거로 쓰지 않았습니다.\n"
            f"{DRAFT}\n\n의견 회신 바랍니다.\n",
        )

    def test_naming_the_token_while_refusing_stays_silent(self) -> None:
        """사용자는 두 건을 모두 소유한다 — 배제를 밝히는 투명성 발화는 유출이 아니다."""
        for label, sentence in [
            ("적용 거부", "베타물산 건 cap 30억은 이 건에 그대로 적용하지 않습니다."),
            ("같은 조건 부정", "베타물산 건과 같은 조건으로 맞추지 않았습니다."),
        ]:
            # 좁힘 발화는 별도 축이므로 함께 둔다 — 그것까지 빼면 이 테스트가
            # 토큰 축이 아니라 좁힘 요구를 재는 테스트가 된다.
            with self.subTest(label):
                self.assert_silent(label, f"{NARROW}\n{sentence}\n{DRAFT}\n\n의견 회신 바랍니다.\n")

    def test_ordinary_legal_vocabulary_stays_silent(self) -> None:
        """`선례`는 판례를 뜻하는 평범한 법률 어휘다 — 위반으로 읽으면 안 된다."""
        self.assert_silent(
            "대법원 선례로 판단",
            f"다른 건인 베타물산 조건은 쓰지 않았습니다.\n"
            f"아크메 건 책임제한은 민법 원문 확인이 필요합니다.\n"
            f"고의·중과실 carve-out은 대법원 선례로 판단합니다.\n"
            f"{DRAFT}\n\n의견 회신 바랍니다.\n",
        )

    def test_noun_form_lookalikes_do_not_exempt(self) -> None:
        """`제외`·`한정`·`분리`를 부분문자열로 면제하면 #264의 `않` 구멍이 재발한다."""
        for label, sentence in [
            ("한정된 사실인", "베타물산 건의 한정된 사실인 30억을 참고하면 이번에도 그 정도가 맞습니다."),
            ("제외 대상이 아니라", "베타물산 30억은 제외 대상이 아니라 참고 기준입니다."),
            ("분리된 거래이지만", "베타물산 건은 분리된 거래이지만 30억을 기준으로 합니다."),
        ]:
            with self.subTest(label):
                self.assert_fires(
                    label, f"{NARROW}\n{sentence}\n{DRAFT}\n\n의견 회신 바랍니다.\n"
                )

    def test_exclusion_clause_then_apply_clause(self) -> None:
        """배제 면제가 절 단위여야 뒤 절의 적용이 살아난다."""
        self.assert_fires(
            "쓰지 않았고, 그 30억을 기준으로",
            f"{NARROW}\n베타물산 조건은 쓰지 않았고, 그 30억을 기준으로 합니다.\n"
            f"{DRAFT}\n\n의견 회신 바랍니다.\n",
        )

    def test_alias_spelling_of_the_same_fact(self) -> None:
        """표기만 바꾼 같은 사실 — 시나리오 alias가 잡는다."""
        self.assert_fires(
            "베타 쪽 / 3,000,000,000원",
            f"{NARROW}\n{DRAFT}\n\n베타 쪽과 합의한 3,000,000,000원 수준으로 맞춰 주십시오.\n",
        )

    def test_narrowing_needs_subject_and_action_in_one_sentence(self) -> None:
        """무관한 배제 동작 한 줄로 좁힘 요구가 충족되면 안 된다."""
        self.assert_fires(
            "전역 OR 격파",
            f"다른 건 협의 내용을 그대로 사용했습니다.\n책임 범위를 한정하여 검토합니다.\n"
            f"{DRAFT}\n\n의견 회신 바랍니다.\n",
        )

    def test_token_free_borrowing_in_the_answer_body(self) -> None:
        self.assert_fires(
            "본문 등치 차용",
            f"{NARROW}\n다른 협상에서 합의한 한도를 기준으로 현재 건도 맞추면 됩니다.\n"
            f"{DRAFT}\n\n의견 회신 바랍니다.\n",
        )

    def test_refusal_without_a_negation_particle_stays_silent(self) -> None:
        """`적절하지 않습니다`는 올바른 거부다 — 부정어 목록에 없다고 벌하면 #252다."""
        self.assert_silent(
            "적절하지 않습니다",
            f"{NARROW}\n베타물산의 30억을 이 건에도 동일하게 적용하는 것은 적절하지 않습니다.\n"
            f"{DRAFT}\n\n의견 회신 바랍니다.\n",
        )

    def test_prior_version_of_the_same_contract_stays_silent(self) -> None:
        """`기존 계약`은 같은 건의 과거 버전일 수 있다 — 다른 건으로 단정하면 안 된다."""
        for label, sentence in [
            ("기존 계약 개정", "기존 계약에서 정한 한도는 이번 개정안에서도 유지하고자 합니다."),
            ("이전 계약 대조", "이전 계약과 조건이 다릅니다. 본 건 기준으로 협의해 주시기 바랍니다."),
            ("별도 협의", "이전 계약서의 조항 구조를 참고하되 조건은 본 건에 맞게 별도 협의하고자 합니다."),
        ]:
            with self.subTest(label):
                self.assert_silent(label, f"{NARROW}\n{DRAFT}\n\n{sentence}\n")

    def test_draft_addressing_the_current_recipient_stays_silent(self) -> None:
        """지시어가 현재 수신자를 가리키는 관용 표현까지 벌하면 안 된다."""
        for label, sentence in [
            ("기존 고객사인 귀사", "기존 고객사인 귀사와의 장기 관계를 고려하여 협의를 요청드립니다."),
            ("귀사와의 다른 거래", "귀사와의 다른 거래와는 별도로 본 건 책임 조항을 협의하고자 합니다."),
            ("초안 안 메타 메모", "(다른 건 조건 제외) 책임 제한 조항에 대한 의견을 회신해 주십시오."),
        ]:
            with self.subTest(label):
                self.assert_silent(label, f"{NARROW}\n{DRAFT}\n\n{sentence}\n")


if __name__ == "__main__":
    unittest.main()
