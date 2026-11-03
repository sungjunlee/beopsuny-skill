"""Exercise packet preparation only; these checks do not grade model answers."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'tests/forward_evals/model_era'
sys.path.insert(0, str(ROOT / '.test-deps'))
import yaml


class ModelEraPrepareTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.fixture = self.root / 'tests/forward_evals/model_era'
        self.fixture.mkdir(parents=True)
        self.script = self.fixture / 'prepare_packets.py'
        shutil.copy2(HERE / 'prepare_packets.py', self.script)
        # Only the CLI's input/config location is isolated; use the real harness.
        (self.root / 'tests/forward_eval_harness.py').symlink_to(
            ROOT / 'tests/forward_eval_harness.py')
        for name in ('inputs', 'sources'):
            (self.fixture / name).symlink_to(HERE / name, target_is_directory=True)
        config = yaml.safe_load((HERE.parent / 'model_era.yaml').read_text())
        task = next(t for t in config['tasks'] if t['id'] == 'm8-missing-annex-fixed')
        # An opaque ID ensures reference selection follows task_type, not its name.
        self.task_id = task['id'] = 'sealed-case-42'
        self.canary = 'EVALUATOR_ONLY_DO_NOT_SEND_7d9fc2'
        task['source_reference_policy'] = self.canary
        config['tasks'] = [task]
        (self.fixture.parent / 'model_era.yaml').write_text(yaml.safe_dump(config))
        (self.fixture / 'rubric.json').write_text(json.dumps({'private_rubric': self.canary}))
        self.output = self.root / 'output'

    def run_cli(self, *options):
        env = os.environ.copy()
        env['PYTHONPATH'] = os.pathsep.join(
            filter(None, [str(ROOT / '.test-deps'), env.get('PYTHONPATH', '')]))
        return subprocess.run(
            [sys.executable, str(self.script), '--runtime-root', str(ROOT),
             '--output', str(self.output), '--arm', 'B', '--tasks', self.task_id,
             *options], cwd=self.root, env=env, capture_output=True, text=True,
            timeout=30,
        )

    def test_sealed_holdout_rejected_without_writing_packets(self):
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('holdout is sealed', result.stderr)
        self.assertFalse(self.output.exists())

    def test_unlocked_holdout_has_complete_hashed_context_without_evaluator_data(self):
        result = self.run_cli('--include-holdout')
        self.assertEqual(result.returncode, 0, result.stderr)
        packet = self.output / 'model-inputs/B' / self.task_id
        self.assertEqual({p.name for p in packet.iterdir()}, {'context.md', 'prompt.txt'})
        metadata = json.loads((self.output / 'evaluator-only/B-metadata.json').read_text())
        record, = metadata['records']
        context = (packet / 'context.md').read_text()
        required = {
            'skills/beopsuny/references/research-workflow.md',
            'skills/beopsuny/references/source-grading.md',
            'skills/beopsuny/references/contract_review_guide.md',
            'skills/beopsuny/assets/policies/review_mode.yaml',
            'skills/beopsuny/references/self-verification.md',
            'skills/beopsuny/references/output-formats.md',
            'skills/beopsuny/assets/schemas/output_contract.yaml',
        }
        self.assertTrue(required <= record['task_runtime_inputs'].keys())
        for path, checksum in record['task_runtime_inputs'].items():
            with self.subTest(path=path):
                source = ROOT / path
                self.assertIn(source.read_text().rstrip(), context)
                self.assertEqual(checksum, hashlib.sha256(source.read_bytes()).hexdigest())
                self.assertEqual(checksum, metadata['runtime_inputs'][path])
        for filename, key in [('context.md', 'context_sha256'), ('prompt.txt', 'prompt_sha256')]:
            content = (packet / filename).read_bytes()
            self.assertEqual(record[key], hashlib.sha256(content).hexdigest())
            self.assertNotIn(self.canary.encode(), content)
            self.assertNotIn(b'"task_runtime_inputs"', content)
            self.assertNotIn(b'"legal_adjudication"', content)
        self.assertEqual(record['execution_status'], 'not_measured')
        self.assertIsNone(record['assessment'])


# prepare_packets digests these and the harness copies them into context.md.
# Stubs keep the packet oracle off historical eval inputs and captured sources.
_RUNTIME_FILES = (
    'skills/beopsuny/SKILL.md',
    'skills/beopsuny/references/source-access.md',
    'skills/beopsuny/references/citation-verification-contract.md',
    'skills/beopsuny/references/research-workflow.md',
    'skills/beopsuny/references/source-grading.md',
)


class SyntheticFixedPacketTests(unittest.TestCase):
    """Fixed-packet delivery, checksum, and overwrite boundaries.

    Fixtures are generated here. They are not the historical model-era inputs.
    """

    QUESTION = 'SYNTHETIC-QUESTION-7f3a9c'
    EXCERPT_MARKER = 'SYNTHETIC-EXCERPT-c91e4b'
    TASK_ID = 'synthetic-fixed-1'

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.fixture = self.root / 'tests/forward_evals/model_era'
        self.fixture.mkdir(parents=True)
        self.script = self.fixture / 'prepare_packets.py'
        shutil.copy2(HERE / 'prepare_packets.py', self.script)
        (self.root / 'tests/forward_eval_harness.py').symlink_to(
            ROOT / 'tests/forward_eval_harness.py')
        self.runtime = self.root / 'runtime'
        for relative in _RUNTIME_FILES:
            path = self.runtime / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f'synthetic runtime {relative}\n', encoding='utf-8')
        self.question_path = self.fixture / 'inputs/question.txt'
        self.source_path = self.fixture / 'sources/source.md'
        self.excerpt_path = self.fixture / 'sources/excerpt.md'
        self.question_path.parent.mkdir(parents=True)
        self.source_path.parent.mkdir(parents=True)
        self.question_path.write_text(self.QUESTION + '\n', encoding='utf-8')
        self.source_path.write_text('synthetic full source body\n', encoding='utf-8')
        self.excerpt_path.write_text(self.EXCERPT_MARKER + '\n', encoding='utf-8')
        self.manifest_path = self.fixture / 'sources/manifest.json'
        self._write_manifest()
        config = {
            'name': 'synthetic-model-era',
            'baseline_commit': '0' * 40,
            'evaluation_date': '2026-01-01',
            'tasks': [{
                'id': self.TASK_ID,
                'task_type': 'simple-statute',
                'split': 'smoke',
                'source_mode': 'fixed',
                'input_file': 'inputs/question.txt',
                'fixed_sources': ['synthetic-source'],
            }],
        }
        (self.fixture.parent / 'model_era.yaml').write_text(
            yaml.safe_dump(config, allow_unicode=True, sort_keys=False), encoding='utf-8')
        self.output = self.root / 'output'
        self.packet = self.output / 'model-inputs' / 'A' / self.TASK_ID

    def _sha256(self, path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _write_manifest(self):
        manifest = [{
            'id': 'synthetic-source',
            'file': 'source.md',
            'sha256': self._sha256(self.source_path),
            'captured_at': '2026-01-01T00:00:00+00:00',
            'mirror_commit': 'synthetic-mirror',
            'official_url': 'https://example.invalid/statute',
            'excerpt': {
                'file': 'excerpt.md',
                'sha256': self._sha256(self.excerpt_path),
            },
        }]
        self.manifest_path.write_text(json.dumps(manifest), encoding='utf-8')

    def _recorded_hash(self, filename):
        manifest = json.loads(self.manifest_path.read_text(encoding='utf-8'))
        source = manifest[0]
        if filename == source['file']:
            return source['sha256']
        return source['excerpt']['sha256']

    def run_cli(self, *options, question=None):
        if question is not None:
            self.question_path.write_text(question + '\n', encoding='utf-8')
        env = os.environ.copy()
        env['PYTHONPATH'] = os.pathsep.join(
            filter(None, [str(ROOT / '.test-deps'), env.get('PYTHONPATH', '')]))
        return subprocess.run(
            [sys.executable, str(self.script), '--runtime-root', str(self.runtime),
             '--output', str(self.output), '--arm', 'A', '--tasks', self.TASK_ID,
             *options], cwd=self.root, env=env, capture_output=True, text=True,
            timeout=30,
        )

    def _assert_rejected_without_output(self, result, message):
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(message, result.stderr)
        self.assertFalse(self.output.exists())

    def _tamper_keeping_recorded_hash(self, path):
        recorded = self._recorded_hash(path.name)
        self.assertEqual(recorded, self._sha256(path))
        path.write_bytes(path.read_bytes() + b'\nTAMPER\n')
        self.assertNotEqual(self._sha256(path), recorded)
        self.assertEqual(self._recorded_hash(path.name), recorded)
        self.assertNotIn(self._sha256(path), self.manifest_path.read_text(encoding='utf-8'))

    def _output_files(self):
        return {
            path.relative_to(self.output).as_posix(): path.read_bytes()
            for path in self.output.rglob('*')
            if path.is_file()
        }

    def test_prompt_contains_question_and_fixed_excerpt(self):
        self.assertNotIn(self.EXCERPT_MARKER, self.question_path.read_text(encoding='utf-8'))
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({p.name for p in self.packet.iterdir()}, {'context.md', 'prompt.txt'})
        prompt = (self.packet / 'prompt.txt').read_text(encoding='utf-8')
        self.assertIn(self.QUESTION, prompt)
        self.assertIn(self.EXCERPT_MARKER, prompt)

    def test_changed_source_bytes_with_original_hash_write_nothing(self):
        self._tamper_keeping_recorded_hash(self.source_path)
        result = self.run_cli()
        self._assert_rejected_without_output(result, 'source checksum mismatch: source.md')

    def test_changed_excerpt_bytes_with_original_hash_write_nothing(self):
        self._tamper_keeping_recorded_hash(self.excerpt_path)
        result = self.run_cli()
        self._assert_rejected_without_output(result, 'source checksum mismatch: excerpt.md')

    def test_reprepare_same_destination_keeps_existing_bytes(self):
        first = self.run_cli()
        self.assertEqual(first.returncode, 0, first.stderr)
        before = self._output_files()
        prompt_key = f'model-inputs/A/{self.TASK_ID}/prompt.txt'
        self.assertIn(self.QUESTION.encode(), before[prompt_key])
        revised = 'REVISED-QUESTION-b2e8'
        self.assertNotIn(revised.encode(), before[prompt_key])
        second = self.run_cli(question=revised)
        self.assertNotEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertIn('refusing to overwrite prepared packets', second.stderr)
        self.assertEqual(self._output_files(), before)
        self.assertNotIn(revised, (self.packet / 'prompt.txt').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
