#!/usr/bin/env python3
"""Validate pinned privacy assets with existing ingestion; prepare staged inputs only."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--knowledge-root', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
knowledge = args.knowledge_root.resolve()
result = subprocess.run([sys.executable, str(ROOT / 'skills/beopsuny/assets/tools/knowledge_manifest_ingest.py'),
    '--manifest-file', str(knowledge / '_system/manifests/stable.json'), '--knowledge-root', str(knowledge),
    '--max-asset-chars', '1000000', '--strict'], capture_output=True, text=True)
packet = json.loads(result.stdout)
if result.returncode or packet.get('status') != 'ready':
    raise SystemExit('preparation_failed: manifest validation did not return ready; no performance inference')
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=False)
sections = packet['injection_packet']['rendered_sections']
for key, filename in [('taxonomy', 'taxonomy.txt'), ('retrieval_hints', 'hints.txt'),
                      ('authority_map.core', 'audit-core.txt'), ('authority_map.overlay', 'audit-overlay.txt')]:
    (output / filename).write_text(sections[key])
for name in ['privacy-saas', 'privacy-tags']:
    (output / f'{name}.txt').write_text((HERE / 'inputs' / f'{name}.txt').read_text())
metadata = {'status': 'prepared_not_measured', 'assets': packet['assets'],
            'snapshot': json.loads((knowledge / 'capture.json').read_text()),
            'files': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir()},
            'note': 'Respect staged timing in rubric; source files contain original usage labels. Explicit experimental timing is required for hints-first, with no production policy change. Legal sources and runtime packets remain separate.'}
(output.parent / (output.name + '-metadata.json')).write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': 'prepared_not_measured', 'output': str(output)}))
