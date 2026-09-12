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


if __name__ == '__main__':
    unittest.main()
