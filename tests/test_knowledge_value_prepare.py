"""Guard the experiment's shared product behavior and evaluator exclusion."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import importlib.util

module_path = Path(__file__).parent / "forward_evals/knowledge_value/prepare.py"
spec = importlib.util.spec_from_file_location("knowledge_value_prepare", module_path)
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)


class PreparationTests(unittest.TestCase):
    def test_a_keeps_generic_right_sizing_and_product_references(self):
        original = (prepare.ROOT / 'skills/beopsuny/SKILL.md').read_text()
        variant = prepare.build_arm_a_skill(original)
        self.assertIn('1. Right-sizing', variant)
        self.assertIn('짧은 조문·시행일·링크 확인은 `legal_research`만 수행', variant)
        self.assertIn('과잉 라우팅·과잉 gate 적용 판단의 단일 기준', variant)
        self.assertNotIn('privacy_knowledge_layer', variant)
        self.assertNotIn('knowledge-injection.md', variant)
        for reference in ('privacy_compliance.yaml', 'clause_references.yaml'):
            self.assertEqual(original.count(reference), variant.count(reference))

    def test_candidate_excludes_later_hypothesis(self):
        with tempfile.TemporaryDirectory() as directory:
            memo = Path(directory) / 'memo.md'
            memo.write_text('# Research\n\n## Evaluation Candidate\nConditional knowledge.\n\n## Evaluation hypothesis\nNever inject this.\n')
            self.assertEqual('Conditional knowledge.\n', prepare.extract_evaluation_candidate(memo))
            memo.write_text('## Evaluation Candidate\n### Rubric\nLeak.\n')
            with self.assertRaisesRegex(ValueError, 'evaluator-only'):
                prepare.extract_evaluation_candidate(memo)

    def test_candidate_discovery_supports_current_and_frozen_layouts(self):
        for layout in (prepare.CANDIDATE_MEMO_DIRECTORY, prepare.LEGACY_CANDIDATE_MEMO_DIRECTORY):
            with self.subTest(layout=layout), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                memos = root / layout
                memos.mkdir(parents=True)
                for name in ("a.md", "b.md"):
                    (memos / name).write_text("## Evaluation Candidate\nConditional knowledge.\n")
                found = prepare.discover_evaluation_candidate_memos(root)
                self.assertEqual([memos / "a.md", memos / "b.md"], found)
                (memos / "c.md").write_text("## Evaluation Candidate\nUnexpected candidate.\n")
                with self.assertRaisesRegex(ValueError, "exactly two"):
                    prepare.discover_evaluation_candidate_memos(root)

    def test_source_bundle_rejects_changed_content(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory)
            source = bundle / 'official.md'
            source.write_text('Frozen source.')
            (bundle / 'manifest.json').write_text(json.dumps({'access_mode':'fixed','sources':[{'id':'official','file':'official.md','sha256':hashlib.sha256(source.read_bytes()).hexdigest()}]}))
            prepare.load_source_bundle(bundle)
            source.write_text('Changed source.')
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                prepare.load_source_bundle(bundle)


if __name__ == '__main__':
    unittest.main()
