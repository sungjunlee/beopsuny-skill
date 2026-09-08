#!/usr/bin/env python3
"""Prepare isolated model inputs with the existing harness; never score or run a model."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tests'))
import forward_eval_harness as harness

HERE = Path(__file__).resolve().parent


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--arm', choices=['A', 'B'], required=True)
    parser.add_argument('--tasks', nargs='+', default=['m8-simple-statute-fixed', 'm8-future-effective-fixed'])
    parser.add_argument('--include-holdout', action='store_true')
    args = parser.parse_args()
    runtime = args.runtime_root.resolve()
    os.environ['BEOPSUNY_EVAL_RUNTIME_ROOT'] = str(runtime)
    config = harness.load_yaml(HERE.parent / 'model_era.yaml')
    sources = json.loads((HERE / 'sources/manifest.json').read_text())
    source_map = {source['id']: source for source in sources}
    for source in sources:
        for item in [source, source['excerpt']]:
            if digest(HERE / 'sources' / item['file']) != item['sha256']:
                raise ValueError(f'source checksum mismatch: {item["file"]}')
    tasks = {task['id']: task for task in config['tasks']}
    references = ['skills/beopsuny/references/source-access.md',
                  'skills/beopsuny/references/citation-verification-contract.md']
    prompts, records = [], []
    loaded_references = set(references)
    for task_id in args.tasks:
        task = tasks[task_id]
        if task['split'] == 'holdout' and not args.include_holdout:
            raise ValueError('holdout is sealed; pass --include-holdout only after preregistered expansion decision')
        text = (HERE / task['input_file']).read_text()
        if task['source_mode'] == 'fixed':
            text += '\n[자료 조건] 제공된 고정 원문 발췌만 읽을 수 있는 환경이다. 인터넷·개인 설치본·다른 파일에 접근할 수 없다. 원문에 없는 하위 규정이나 사건의 존재·부존재는 이 자료만으로 확인되지 않는다. 출처는 공식 원문 기반 미러이며 직접 공식 사이트를 열었다는 뜻은 아니다.\n'
            for source_id in task['fixed_sources']:
                source = source_map[source_id]
                text += f'\n## 자료 {source_id}\n공식 URL: {source["official_url"]}\n미러 revision: {source["mirror_commit"]}\n원문 SHA256: {source["sha256"]}\n취득시각: {source["captured_at"]}\n'
                text += (HERE / 'sources' / source['excerpt']['file']).read_text()
        else:
            text += '\n[자료 조건] 실제로 접근한 공식 소스와 자료의 적용 시점을 확인해 답하라. 접근 실패는 그대로 구분하라. 개인 설치 skill 및 다른 평가 사례·채점 파일은 이용하지 않는다.\n'
        task_references = list(references)
        if any(kind in task_id for kind in ('complex-contract', 'external-draft')):
            task_references += [
                'skills/beopsuny/references/contract_review_guide.md',
                'skills/beopsuny/assets/policies/review_mode.yaml',
                'skills/beopsuny/references/self-verification.md',
                'skills/beopsuny/references/output-formats.md',
                'skills/beopsuny/assets/schemas/output_contract.yaml',
            ]
        loaded_references.update(task_references)
        prompt = {'id': task_id, 'source_references': task_references, 'prompt': text}
        prompts.append(prompt)
        records.append({'task_id': task_id, 'arm': args.arm, 'split': task['split'],
                        'source_mode': task['source_mode'], 'source_ids': task['fixed_sources'],
                        'task_runtime_inputs': {p: digest(runtime / p) for p in ['skills/beopsuny/SKILL.md', *task_references]},
                        'execution_status': 'not_measured', 'legal_adjudication': 'unadjudicated',
                        'assessment': None, 'model_id': None, 'effort': None, 'elapsed_seconds': None,
                        'tokens': None, 'cost': None, 'unavailable_reason': 'not executed',
                        'tools': 'none required; executor must enforce no tools' if task['source_mode'] == 'fixed' else 'record actual matched read/search tools before run',
                        'access_log': [], 'scorer_false_positives': None})
    packet_dir = args.output.resolve() / 'model-inputs' / args.arm
    if packet_dir.exists():
        raise ValueError(f'refusing to overwrite prepared packets: {packet_dir}')
    harness.write_prompt_packets({'prompts': prompts}, packet_dir)
    for record in records:
        location = packet_dir / record['task_id']
        record['context_sha256'] = digest(location / 'context.md')
        record['prompt_sha256'] = digest(location / 'prompt.txt')
    manifest = {'baseline_commit': config['baseline_commit'], 'arm': args.arm,
                'runtime_root': str(runtime), 'harness_sha256': digest(ROOT / 'tests/forward_eval_harness.py'),
                'runtime_inputs': {p: digest(runtime / p) for p in ['skills/beopsuny/SKILL.md', *sorted(loaded_references)]},
                'source_manifest_sha256': digest(HERE / 'sources/manifest.json'),
                'configuration_sha256': digest(HERE.parent / 'model_era.yaml'),
                'evaluation_date': config['evaluation_date'], 'records': records}
    evaluator_dir = args.output.resolve() / 'evaluator-only'
    evaluator_dir.mkdir(parents=True, exist_ok=True)
    (evaluator_dir / f'{args.arm}-metadata.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'packet_dir': str(packet_dir), 'tasks': len(records), 'execution_status': 'not_measured'}))


if __name__ == '__main__':
    main()
