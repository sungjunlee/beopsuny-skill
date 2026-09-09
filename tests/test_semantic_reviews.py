"""Hash-bound semantic review plumbing; synthetic expectations are provisional.

Unit doubles below simulate a reviewed record; they do not adjudicate fixture
meaning. The CLI consumes only the real, independently reviewed fixture state.
"""
from __future__ import annotations

import copy
import contextlib
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.test-deps'))
sys.path.insert(0, str(ROOT / 'tests'))
import evaluate_scenario_outputs as scorer
import forward_eval_harness as harness


class SemanticReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenarios = scorer.collect_scenarios(scorer.DEFAULT_SCENARIOS)
        cls.data = scorer.load_yaml(ROOT / 'tests/fixtures/semantic_reviews.yaml')

    def approved_double(self, case):
        record = copy.deepcopy(next(row for row in self.data['reviews'] if row['id'] == case['id']))
        record.update(review_status='reviewed', reviewed_at='2026-09-08T00:00:00Z',
                      reviewer={'kind': 'independent_model', 'id': 'unit-test-double'})
        return record

    def scenario(self, case):
        scenario = dict(self.scenarios[case['scenario_id']])
        if case.get('request'):
            scenario['semantic_request'] = case['request']
        return scenario

    def assess(self, case, records):
        return scorer.evaluate_semantic_review(case['scenario_id'], self.scenario(case),
                                              case['output'], case['rule'], records=records)

    def test_fixed_near_misses_and_real_violations_use_review_verdict(self):
        for case in self.data['cases']:
            with self.subTest(case=case['id']):
                self.assertEqual(self.assess(case, [self.approved_double(case)])['verdict'],
                                 case['expected_verdict'])

    def test_missing_unreviewed_ambiguous_or_unjudgeable_is_not_pass(self):
        case = self.data['cases'][0]
        reviewed = self.approved_double(case)
        for records in ([], [reviewed, reviewed], [{**reviewed, 'review_status': 'provisional'}],
                        [{**reviewed, 'author': None}], [{**reviewed, 'id': ''}],
                        [{**reviewed, 'reviewed_at': 'not-a-date'}],
                        [{**reviewed, 'reviewer': {**reviewed['reviewer'], 'id': reviewed['author']['id']}}],
                        [{**reviewed, 'verdict': 'UNJUDGEABLE'}], [{**reviewed, 'reviewer': None}]):
            with self.subTest(records=records):
                self.assertEqual(self.assess(case, records)['verdict'], 'REVIEW_REQUIRED')

    def test_binding_rejects_changed_output_request_policy_or_span(self):
        case = self.data['cases'][0]
        reviewed = self.approved_double(case)
        for key in ('output_sha256', 'request_sha256', 'policy_revision'):
            bad = {**reviewed, key: 'obsolete'}
            self.assertEqual(self.assess(case, [bad])['verdict'], 'REVIEW_REQUIRED')
        for evidence in ([], [{'start': 0, 'end': 3, 'quote': 'bogus'}],
                         [{'start': True, 'end': 3, 'quote': case['output'][:3]}]):
            self.assertEqual(self.assess(case, [{**reviewed, 'evidence': evidence}])['verdict'],
                             'REVIEW_REQUIRED')
        changed = {**case, 'output': case['output'] + '\n추가 보증'}
        self.assertEqual(self.assess(changed, [reviewed])['verdict'], 'REVIEW_REQUIRED')

    def test_missing_review_does_not_count_as_unsafe_detection(self):
        unsafe = {'id': 'probe', 'scenario_id': 'router-02', 'output': '새 출력',
                  'expected_failure_rules': ['contract_counter_draft_boundary']}
        result = scorer.evaluate_unsafe_outputs(self.scenarios, [unsafe])
        self.assertTrue(result)
        self.assertTrue(any('REVIEW_REQUIRED' in item for item in result))

    def test_empty_or_only_retired_checks_are_unscorable(self):
        for rules in ([], ['self_verification_metadata'], ['light_tier_no_packet_ceremony']):
            scenario = {'output_eval': {'common_rules': rules}}
            self.assertTrue(scorer.evaluate_one_output('empty', scenario, 'content')[0].startswith('UNSCORABLE:'))

    def test_contract_without_literal_checks_still_requires_review(self):
        result = scorer.evaluate_one_output('router-02', self.scenarios['router-02'], '미검토 새 출력')
        self.assertTrue(any(item.startswith('REVIEW_REQUIRED:') for item in result))
        self.assertTrue(scorer.evaluate_common_rule('router-02', self.scenarios['router-02'],
                                                  '미검토 새 출력', 'contract_counter_draft_boundary'))

    def test_optional_metadata_is_neither_required_nor_forbidden(self):
        for rule in ('self_verification_metadata', 'light_tier_no_packet_ceremony'):
            for output in ('본문만', '## Authority Packet\n- citation: x\n- source_authority: y\n자가 검증:'):
                self.assertEqual(scorer.evaluate_common_rule('probe', {}, output, rule), [])

    def test_live_and_rescore_receive_pending_without_model_failure(self):
        config = harness.load_forward_eval(harness.DEFAULT_CONFIG)
        prompt = next(p for p in config['prompts'] if p['id'] == 'fwd-10-confidential-persistence-boundary')
        result = harness.score_one_prompt(prompt, '요청한 사건 범위 안에만 기록합니다.')
        self.assertEqual(result['verdict'], 'REVIEW_REQUIRED')
        self.assertEqual(result['failed_guardrails'], [])
        self.assertTrue(result['review_required'])
        self.assertFalse(any(x.startswith('semantic_rule:') for x in result['passed_guardrails']))
        evidence = harness.score_forward_outputs({'name': 'probe', 'prompts': [prompt]},
                   {prompt['id']: '요청한 사건 범위 안에만 기록합니다.'}, mode='sample', model='test-double', run_at='test')
        self.assertEqual(evidence['summary']['passed'], 0)
        self.assertEqual(evidence['summary']['failed'], 0)
        self.assertEqual(evidence['summary']['review_required'], 1)

    def test_scorer_cli_reports_fail_before_pending(self):
        for failures, expected in ((["REVIEW_REQUIRED: pending"], "INCOMPLETE"),
                                   (["real failure", "REVIEW_REQUIRED: pending"], "FAIL")):
            with self.subTest(failures=failures), patch.object(scorer, "evaluate_outputs", return_value=failures), \
                    patch.object(scorer, "evaluate_unsafe_outputs", return_value=[]), \
                    patch.object(scorer, "evaluate_semantic_cases", return_value=[]), \
                    patch.object(sys, "argv", ["scorer"]), contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(scorer.main(), 1)
                self.assertEqual(out.getvalue().splitlines()[0], expected)

    def test_mixed_failure_and_pending_have_disjoint_totals(self):
        full = harness.load_forward_eval(harness.DEFAULT_CONFIG)
        prompts = [p for p in full["prompts"] if p["id"] in {
            "fwd-01-beopmang-maintenance-fallback", "fwd-10-confidential-persistence-boundary"}]
        outputs = {p["id"]: "검토용 초안입니다." for p in prompts}
        evidence = harness.score_forward_outputs({"name": "mixed", "prompts": prompts}, outputs,
                                                mode="sample", model="stub", run_at="test")
        summary = evidence["summary"]
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["review_required"], 1)
        self.assertEqual(summary["total"], sum(summary[k] for k in ["passed", "failed", "review_required"]))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            harness.print_report(evidence, Path("evidence.yaml"))
        self.assertTrue(output.getvalue().startswith("FAIL "))
        self.assertIn("failed: 1; review required: 1", output.getvalue())

    def test_live_receiver_scope_follows_declared_prompt_axis(self):
        prompt = {"id": "not-a-declared-live-axis", "source_router_scenario": "router-16"}
        self.assertEqual(harness.forward_semantic_rules(prompt), [])
        prompt["id"] = "fwd-01-beopmang-maintenance-fallback"
        self.assertEqual(harness.forward_semantic_rules(prompt), ["legal_verification_core_trace"])
        prompt["id"] = "fwd-08-profile-write-boundary"
        self.assertEqual(harness.forward_semantic_rules(prompt), ["confidential_persistence_boundary"])


if __name__ == '__main__':
    unittest.main()
