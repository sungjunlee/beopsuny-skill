#!/usr/bin/env bash
# Parallel front-end to the same isolated command runner used by the harness.
# CONFIG, MODEL, PAR, RUN_DIR and RUNNER retain their historical meanings.
# Each invocation owns RUN_DIR exclusively. A second overlapping invocation
# exits without writing. Outputs, capture, and evidence stay in a private
# slot until every file exists; only then does `current` publish them together.
# A failed invocation does not leave the previous success as this run's result.
# BEOPSUNY_EVAL_RUNTIME_ROOT selects a preserved runtime for paired comparison.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$ROOT"
export CONFIG="${CONFIG:-tests/forward_evals/beopsuny_guardrails.yaml}"
export MODEL="${MODEL:-claude-sonnet-5}"
export PAR="${PAR:-4}"
export RUN_DIR="${RUN_DIR:-tests/forward_evals/runs/live-$(basename "$CONFIG" .yaml)}"
export RUNNER="${RUNNER:-tests/forward_evals/run_claude_live.sh}"
PYTHONPATH="tests:.test-deps${PYTHONPATH:+:$PYTHONPATH}" python3 <<'PY'
import fcntl
import json
import os
import shutil
import shlex
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import forward_eval_harness as harness

config = harness.load_forward_eval(Path(os.environ['CONFIG']).resolve())
run_dir = Path(os.environ['RUN_DIR']).resolve()
run_dir.mkdir(parents=True, exist_ok=True)
lock_handle = open(run_dir / '.run.lock', 'a+')
try:
    fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    sys.stderr.write(f"RUN_DIR busy: {run_dir}\n")
    raise SystemExit(1)

model = os.environ['MODEL']
runner = str(Path(os.environ['RUNNER']).resolve())
run_id = uuid.uuid4().hex

def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)

def ensure_public_link(name: str) -> None:
    link = run_dir / name
    relative = str(Path('current') / name)
    if link.is_symlink():
        if os.readlink(link) == relative:
            return
        link.unlink()
    elif link.exists():
        quarantine = run_dir / '.quarantine' / run_id
        quarantine.mkdir(parents=True, exist_ok=True)
        link.rename(quarantine / name)
    link.symlink_to(relative)

for public_name in ('outputs', 'capture.yaml', 'evidence.yaml', 'publish.json'):
    ensure_public_link(public_name)
remove_path(run_dir / 'current')
slots = run_dir / 'slots'
slot = slots / run_id
out_dir = slot / 'outputs'
out_dir.mkdir(parents=True)

def run(prompt):
    subset = {**config, 'prompts': [prompt]}
    captured, records = harness.run_command_outputs(
        subset, command_template=shlex.quote(runner), model=model
    )
    prompt_id = str(prompt['id'])
    (out_dir / f'{prompt_id}.txt').write_text(captured[prompt_id], encoding='utf-8')
    harness.write_evidence(
        {'prompts': [{'prompt_id': prompt_id, 'output': captured[prompt_id], 'execution': records[0]}]},
        out_dir / f'{prompt_id}.yaml',
    )
    print(f"{prompt_id}: {records[0]['execution_status']}", flush=True)
    return captured, records

published = False
try:
    outputs, executions = {}, {}
    with ThreadPoolExecutor(max_workers=max(1, int(os.environ['PAR']))) as pool:
        for captured, records in pool.map(run, config['prompts']):
            outputs.update(captured)
            executions.update({item['prompt_id']: item for item in records})
    evidence = harness.score_forward_outputs(
        config, outputs, executions=executions, mode='command', model=model,
        run_at=harness.utc_now(), source_eval=os.environ['CONFIG'],
    )
    evidence['run_id'] = run_id
    capture = {
        'model': model,
        'run_id': run_id,
        'prompts': [
            {'prompt_id': key, 'output': value, 'execution': executions[key]}
            for key, value in outputs.items()
        ],
    }
    harness.write_evidence(capture, slot / 'capture.yaml')
    harness.write_evidence(evidence, slot / 'evidence.yaml')
    (slot / 'publish.json').write_text(
        json.dumps(
            {
                'model': model,
                'prompt_ids': sorted(outputs),
                'run_id': run_id,
                'status': 'complete',
            },
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )
    tmp_link = run_dir / f'.current-{run_id}'
    remove_path(tmp_link)
    tmp_link.symlink_to(Path('slots') / run_id)
    os.replace(tmp_link, run_dir / 'current')
    published = True
except Exception as exc:
    if not published:
        remove_path(slot)
    sys.stderr.write(f"publish aborted: {type(exc).__name__}: {exc}\n")
    raise SystemExit(1)
for child in list(slots.iterdir()):
    if child != slot:
        remove_path(child)
harness.print_report(evidence, run_dir / 'evidence.yaml')
raise SystemExit(
    1
    if evidence['summary']['failed']
    or evidence['summary']['unscorable']
    or evidence['summary']['review_required']
    else 0
)
PY
