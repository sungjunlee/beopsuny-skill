#!/usr/bin/env python3
"""
20-scenario evaluation pack 검증 테스트.

최근 추가된 20개 시나리오 평가 팩의 구조적 무결성을 검증한다:
- scenarios와 outputs 간의 ID 일관성
- 필수 필드 존재 여부
- YAML 구조 검증
- 공식 링크 도메인 검증
"""

import unittest
import yaml
from pathlib import Path


class EvalPackValidationTests(unittest.TestCase):
    """20-scenario evaluation pack의 구조적 무결성 검증."""

    @classmethod
    def setUpClass(cls):
        """YAML 파일 로드."""
        cls.repo_root = Path(__file__).parent.parent
        
        scenarios_path = cls.repo_root / "tests" / "scenarios" / "20_scenario_eval_pack.yaml"
        outputs_path = cls.repo_root / "tests" / "fixtures" / "eval_pack_outputs.yaml"
        
        with open(scenarios_path, 'r', encoding='utf-8') as f:
            cls.scenarios_data = yaml.safe_load(f)
        
        with open(outputs_path, 'r', encoding='utf-8') as f:
            cls.outputs_data = yaml.safe_load(f)
    
    def test_scenarios_file_has_required_top_level_keys(self):
        """scenarios 파일이 필수 최상위 키를 가지는지 확인."""
        self.assertIn('name', self.scenarios_data)
        self.assertIn('description', self.scenarios_data)
        self.assertIn('scenarios', self.scenarios_data)
    
    def test_outputs_file_has_outputs_key(self):
        """outputs 파일이 outputs 키를 가지는지 확인."""
        self.assertIn('outputs', self.outputs_data)
    
    def test_all_scenario_ids_are_unique(self):
        """모든 시나리오 ID가 고유한지 확인."""
        scenario_ids = [s['id'] for s in self.scenarios_data['scenarios']]
        self.assertEqual(
            len(scenario_ids),
            len(set(scenario_ids)),
            "Duplicate scenario IDs found"
        )
    
    def test_all_scenarios_have_corresponding_outputs(self):
        """모든 시나리오에 대응하는 출력이 있는지 확인."""
        scenario_ids = {s['id'] for s in self.scenarios_data['scenarios']}
        output_ids = set(self.outputs_data['outputs'].keys())
        
        missing_outputs = scenario_ids - output_ids
        self.assertEqual(
            len(missing_outputs),
            0,
            f"Scenarios without outputs: {missing_outputs}"
        )
    
    def test_no_orphaned_outputs(self):
        """outputs에 대응하는 시나리오가 없는 항목이 없는지 확인."""
        scenario_ids = {s['id'] for s in self.scenarios_data['scenarios']}
        output_ids = set(self.outputs_data['outputs'].keys())
        
        orphaned_outputs = output_ids - scenario_ids
        self.assertEqual(
            len(orphaned_outputs),
            0,
            f"Outputs without scenarios: {orphaned_outputs}"
        )
    
    def test_all_scenarios_have_required_fields(self):
        """모든 시나리오가 필수 필드를 가지는지 확인."""
        required_fields = ['id', 'name', 'question', 'expected']
        
        for scenario in self.scenarios_data['scenarios']:
            scenario_id = scenario.get('id', 'UNKNOWN')
            for field in required_fields:
                self.assertIn(
                    field,
                    scenario,
                    f"Scenario {scenario_id} missing required field: {field}"
                )
    
    def test_all_scenarios_have_expected_structure(self):
        """모든 시나리오의 expected 필드가 올바른 구조를 가지는지 확인."""
        for scenario in self.scenarios_data['scenarios']:
            scenario_id = scenario['id']
            expected = scenario.get('expected', {})
            
            # primary_intent는 필수
            self.assertIn(
                'primary_intent',
                expected,
                f"Scenario {scenario_id} missing primary_intent in expected"
            )
            
            # must_cite가 있으면 리스트여야 함
            if 'must_cite' in expected:
                self.assertIsInstance(
                    expected['must_cite'],
                    list,
                    f"Scenario {scenario_id} must_cite should be a list"
                )
    
    def test_scenarios_with_official_links_use_law_go_kr(self):
        """공식 링크 요구사항이 있는 시나리오가 law.go.kr을 지정하는지 확인."""
        for scenario in self.scenarios_data['scenarios']:
            scenario_id = scenario['id']
            expected = scenario.get('expected', {})
            must_cite = expected.get('must_cite', [])
            
            for citation in must_cite:
                if 'official_link_domain' in citation:
                    self.assertEqual(
                        citation['official_link_domain'],
                        'law.go.kr',
                        f"Scenario {scenario_id} should use law.go.kr for official links"
                    )
    
    def test_output_samples_are_non_empty_strings(self):
        """모든 출력 샘플이 비어있지 않은 문자열인지 확인."""
        for output_id, output_text in self.outputs_data['outputs'].items():
            self.assertIsInstance(
                output_text,
                str,
                f"Output {output_id} should be a string"
            )
            self.assertTrue(
                len(output_text.strip()) > 0,
                f"Output {output_id} should not be empty"
            )
    
    def test_scenario_count_is_20(self):
        """시나리오가 정확히 20개인지 확인."""
        scenario_count = len(self.scenarios_data['scenarios'])
        self.assertEqual(
            scenario_count,
            20,
            f"Expected 20 scenarios, found {scenario_count}"
        )
    
    def test_eval_ids_follow_naming_convention(self):
        """모든 시나리오 ID가 eval-XX 형식을 따르는지 확인."""
        import re
        pattern = re.compile(r'^eval-\d{2}$')
        
        for scenario in self.scenarios_data['scenarios']:
            scenario_id = scenario['id']
            self.assertTrue(
                pattern.match(scenario_id),
                f"Scenario ID {scenario_id} should follow eval-XX format"
            )
    
    def test_scenarios_have_validation_rules(self):
        """시나리오가 검증 규칙을 가지는지 확인 (선택적이지만 권장)."""
        scenarios_without_validation = []
        
        for scenario in self.scenarios_data['scenarios']:
            scenario_id = scenario['id']
            if 'validation' not in scenario:
                scenarios_without_validation.append(scenario_id)
        
        # 경고만 출력 (실패하지 않음)
        if scenarios_without_validation:
            print(
                f"\nNote: {len(scenarios_without_validation)} scenarios "
                f"without explicit validation rules: {scenarios_without_validation}"
            )


if __name__ == '__main__':
    unittest.main()
