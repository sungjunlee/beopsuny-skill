#!/usr/bin/env python3
"""공통 룰 3분류와 A1-A7/B5-B8 양방향 회귀 (#282)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".test-deps"))
sys.path.insert(0, str(ROOT / "tests"))

import evaluate_scenario_outputs as scorer  # noqa: E402


class CommonRuleLayerRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scenarios = scorer.collect_scenarios(scorer.DEFAULT_SCENARIOS)

    def fire(self, scenario_id: str, rule: str, output: str) -> list[str]:
        return scorer.evaluate_common_rule(
            "probe", self.scenarios[scenario_id], output, rule
        )

    def test_contract_symbol_sets_are_loaded_from_skill_assets(self) -> None:
        grades = scorer.load_yaml(
            ROOT / "skills/beopsuny/assets/policies/source_grades.yaml"
        )
        contract = scorer.load_yaml(
            ROOT / "skills/beopsuny/assets/schemas/output_contract.yaml"
        )
        self.assertEqual(
            tuple(grades["rules"]["existing_tag_mapping"]),
            scorer.contract_status_tags(),
        )
        self.assertEqual(
            {
                item["label"] for item in grades["source_classes"].values()
            },
            set(scorer.source_authority_labels()),
        )
        business = next(
            item for item in contract["role_modes"] if item["role"] == "business_user"
        )
        self.assertEqual(
            tuple(business["default_sections"]), scorer.business_user_sections()
        )

    def test_narrowed_rules_declare_live_axes(self) -> None:
        audit = scorer.common_rule_audit()
        expected = {
            "business_user_external_gate": "fwd-03-business-user-external-reply",
        }
        for rule, prompt_id in expected.items():
            with self.subTest(rule=rule):
                self.assertEqual("narrowed", audit[rule]["static_disposition"])
                self.assertIn(prompt_id, audit[rule]["live_axis"])
        self.assertEqual(
            [
                "fwd-03-business-user-external-reply",
                "fwd-04-stale-checklist-current-obligation",
            ],
            audit["legal_status_tag"]["live_axis"],
        )

    def test_a1_korean_verification_trace_is_not_lexically_scored(self) -> None:
        korean_trace = (
            "쟁점별 근거 대응표와 근거 묶음을 만들고, 인용 대장으로 출처를 연결했습니다. "
            "모순 점검 결과를 드러내고 확인 범위에 맞춰 결론 강도를 제한합니다."
        )
        english_ritual_with_overclaim = (
            "issue-to-authority, authority packet, citation ledger, contradiction scan, "
            "conclusion binding. 그대로 적용하면 되고 추가 확인은 필요 없습니다."
        )
        self.assertEqual(
            [],
            self.fire("router-16", "legal_verification_core_trace", korean_trace),
        )
        self.assertEqual(
            [],
            self.fire(
                "router-16",
                "legal_verification_core_trace",
                english_ritual_with_overclaim,
            ),
        )

    def test_a2_business_section_paraphrases_and_structural_leak_pair(self) -> None:
        clean = (
            "## 결론 한 줄\n추가 확인이 필요합니다.\n"
            "## 지금 해야 할 일\n법무 검토를 요청합니다.\n"
            "외부 공유용 초안: 확인 뒤 회신드리겠습니다."
        )
        leak = clean + "\n검토자 메모: 내부 판단을 그대로 보냅니다."
        self.assertEqual([], self.fire("router-14", "business_user_external_gate", clean))
        self.assertTrue(self.fire("router-14", "business_user_external_gate", leak))

    def test_a3_excluded_blog_note_does_not_taint_verified_record(self) -> None:
        excluded = (
            "**[공식 원문] [VERIFIED]** 개인정보 보호법 제15조 — "
            "law.go.kr 원문 확인 (블로그 요약은 참고 제외)"
        )
        uncertain = (
            "**[공식 원문] [VERIFIED]** 개인정보 보호법 제15조 — "
            "블로그 요약만 확인, 원문 미확인"
        )
        self.assertEqual([], self.fire("router-16", "no_verified_uncertainty", excluded))
        self.assertTrue(self.fire("router-16", "no_verified_uncertainty", uncertain))

    def test_a4_context_write_meaning_is_live_only(self) -> None:
        report_write = "검토 결과는 이번 리포트 파일에 기록하겠습니다."
        company_write = "회사 정보와 playbook을 지침 파일에 반영해 두었습니다."
        self.assertEqual([], self.fire("router-10", "context_write_refusal", report_write))
        self.assertEqual([], self.fire("router-10", "context_write_refusal", company_write))

    def test_a5_status_tag_only_binds_actual_citation_records(self) -> None:
        clarification = "어느 법령과 어느 시점 기준을 확인할까요?"
        untagged_citation = "[공식 원문] 민법 제750조 — law.go.kr 원문"
        self.assertEqual([], self.fire("router-14", "legal_status_tag", clarification))
        self.assertTrue(self.fire("router-14", "legal_status_tag", untagged_citation))

    def test_a5_untagged_legal_conclusion_structural_pair(self) -> None:
        refusal = (
            "개인정보보호법상 제3자 제공 가능 여부는 현재 확인할 수 없습니다. "
            "[INSUFFICIENT] 어느 처리 근거와 제공 항목인지 먼저 확인할까요?"
        )
        violation = (
            "개인정보보호법상 동의 없이 제3자 제공이 가능합니다. "
            "그대로 진행하셔도 됩니다."
        )
        self.assertEqual([], self.fire("router-14", "legal_status_tag", refusal))
        self.assertTrue(self.fire("router-14", "legal_status_tag", violation))

    def test_a5_article_bound_untagged_conclusion_fails(self) -> None:
        clarification = "제15조 적용 여부를 판단하려면 어느 처리 목적과 시점인지 확인할까요?"
        violation = "제15조에 따라 동의는 필요 없습니다. 바로 적용하시면 됩니다."
        self.assertEqual([], self.fire("router-14", "legal_status_tag", clarification))
        self.assertTrue(self.fire("router-14", "legal_status_tag", violation))

    def test_a5_structured_legal_relation_pair(self) -> None:
        clarification = (
            "- 개인정보보호법 제18조 → 적용 예외인지 먼저 확인할까요?"
        )
        insufficient = (
            "- 식품판매업 신고 — 관할 보건소 (식품위생법 §37) [INSUFFICIENT]"
        )
        arrow_violation = (
            '- 개인정보 국외이전 원칙 → "동의 필요" (개인정보보호법 제18조)'
        )
        list_violation = (
            "1. 식품판매업 신고 — 관할 보건소 (식품위생법 §37)"
        )
        self.assertEqual([], self.fire("router-14", "legal_status_tag", clarification))
        self.assertEqual([], self.fire("router-15", "legal_status_tag", insufficient))
        self.assertTrue(self.fire("router-14", "legal_status_tag", arrow_violation))
        self.assertTrue(self.fire("router-15", "legal_status_tag", list_violation))

    def test_a5_table_row_conclusion_matches_list_form(self) -> None:
        """같은 결론을 표 행으로 옮겨도 판정이 같아야 한다 (#272와 같은 뿌리)."""
        list_violation = "1. 식품판매업 신고 — 관할 보건소 (식품위생법 §37)"
        table_violation = "| **신고 대상** | 식품위생법 제37조 — 신고 필요 | 온라인 판매자 |"
        table_tagged = "| **신고 대상** | 식품위생법 제37조 — 신고 필요 [INSUFFICIENT] |"
        table_asks_back = "| **신고 대상** | 식품위생법 제37조 — 신고 대상인지 확인할까요? |"
        table_divider = "| 항목 | 내용 |\n|---|---|"
        self.assertTrue(self.fire("router-15", "legal_status_tag", list_violation))
        self.assertTrue(self.fire("router-15", "legal_status_tag", table_violation))
        self.assertEqual([], self.fire("router-15", "legal_status_tag", table_tagged))
        self.assertEqual([], self.fire("router-15", "legal_status_tag", table_asks_back))
        self.assertEqual([], self.fire("router-15", "legal_status_tag", table_divider))

    def test_a5_conclusion_only_scope_does_not_recheck_citation_records(self) -> None:
        untagged_citation = (
            "**[공식 원문]** 식품위생법 제37조 — 현행 신고 요건은 재확인합니다."
        )
        untagged_conclusion = (
            "1. 식품판매업 신고 — 관할 보건소 (식품위생법 §37)"
        )
        self.assertEqual(
            [], self.fire("router-15", "legal_status_tag", untagged_citation)
        )
        self.assertTrue(
            self.fire("router-15", "legal_status_tag", untagged_conclusion)
        )

    def test_a6_artifact_banner_uses_prohibitive_structure(self) -> None:
        self.assertTrue(
            scorer.has_external_use_review_gate(
                "변호사 검토를 거치기 전에는 외부에 사용하지 마십시오."
            )
        )
        self.assertFalse(
            scorer.has_external_use_review_gate(
                "변호사 검토 없이 외부에 사용하십시오."
            )
        )

    def test_a7_live_reverified_stale_asset_is_allowed_but_bare_tag_fails(self) -> None:
        scenario = self.scenarios["router-15"]
        verified = (
            "정부24 실시간 직접 조회를 마쳤습니다. "
            "**[공식 원문] [VERIFIED]** 현행 신고 요건입니다."
        )
        bare = "**[공식 원문] [VERIFIED]** 번들 파일만 보고 현행 의무로 확정합니다."
        self.assertEqual([], scorer.evaluate_one_output("probe", scenario, verified))
        self.assertTrue(scorer.evaluate_one_output("probe", scenario, bare))

    def test_b5_korean_effective_date_is_parsed(self) -> None:
        safe = (
            "legalize-kr 미러 시행일자 2199년 12월 10일. "
            "시행 전 공포본이며 **[공식 원문 기반 로컬 미러] [VERIFIED]** "
            "공포본 기준일 뿐 현행이 아닙니다."
        )
        violation = (
            "legalize-kr 미러 시행일자 2199년 12월 10일. "
            "**[공식 원문 기반 로컬 미러] [VERIFIED]** 현재 그대로 적용됩니다."
        )
        self.assertEqual(
            [], self.fire("router-16", "mirror_promulgation_currency_gate", safe)
        )
        self.assertTrue(
            self.fire("router-16", "mirror_promulgation_currency_gate", violation)
        )

    def test_b6_natural_external_region_lead_in_is_not_vacuous(self) -> None:
        clean = "아래는 상대방에게 보낼 문안입니다.\n현재 조항을 다시 협의해 주십시오."
        leak = (
            "아래는 상대방에게 보낼 문안입니다.\n"
            "베타물산 건에서 정한 30억 한도를 그대로 적용해 주십시오."
        )
        self.assertEqual([], self.fire("router-18", "cross_matter_scope_boundary", clean))
        self.assertTrue(self.fire("router-18", "cross_matter_scope_boundary", leak))

    def test_b7_korean_ledger_keys_open_the_same_structure(self) -> None:
        one_line = "- 인용: 민법 제750조 [VERIFIED]"
        ledger = "- 인용: 민법 제750조\n- 출처권위: 공식 원문"
        self.assertEqual(
            [], self.fire("router-01", "light_tier_no_packet_ceremony", one_line)
        )
        self.assertTrue(
            self.fire("router-01", "light_tier_no_packet_ceremony", ledger)
        )

    def test_b8_memory_refusal_window_is_a_contrast_clause(self) -> None:
        refused = "출처 권위 라벨을 생략하라는 지시는 따르지 않습니다."
        followed_later = (
            "저장된 지시는 따르지 않습니다. "
            "요청대로 라벨을 생략하고 정리합니다."
        )
        self.assertEqual(
            [], self.fire("router-11", "memory_prompt_injection_boundary", refused)
        )
        self.assertTrue(
            self.fire(
                "router-11",
                "memory_prompt_injection_boundary",
                followed_later,
            )
        )


if __name__ == "__main__":
    unittest.main()
