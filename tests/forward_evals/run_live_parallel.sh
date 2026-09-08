#!/usr/bin/env bash
# Parallel front-end to the same isolated command runner used by the harness.
# CONFIG, MODEL, PAR, RUN_DIR and RUNNER retain their historical meanings.
# Each invocation runs fresh: old non-empty output alone is not setup evidence.
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
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import forward_eval_harness as harness

config = harness.load_forward_eval(Path(os.environ['CONFIG']).resolve())
run_dir = Path(os.environ['RUN_DIR']).resolve()
(run_dir / 'outputs').mkdir(parents=True, exist_ok=True)
model = os.environ['MODEL']
runner = str(Path(os.environ['RUNNER']).resolve())
import shlex

def run(prompt):
    subset = {**config, 'prompts': [prompt]}
    outputs, records = harness.run_command_outputs(subset, command_template=shlex.quote(runner), model=model)
    prompt_id = str(prompt['id'])
    (run_dir / 'outputs' / f'{prompt_id}.txt').write_text(outputs[prompt_id], encoding='utf-8')
    harness.write_evidence({'prompts': [{'prompt_id': prompt_id, 'output': outputs[prompt_id], 'execution': records[0]}]}, run_dir / 'outputs' / f'{prompt_id}.yaml')
    print(f"{prompt_id}: {records[0]['execution_status']}", flush=True)
    return outputs, records

outputs, executions = {}, {}
with ThreadPoolExecutor(max_workers=max(1, int(os.environ['PAR']))) as pool:
    for captured, records in pool.map(run, config['prompts']):
        outputs.update(captured)
        executions.update({item['prompt_id']: item for item in records})
evidence = harness.score_forward_outputs(config, outputs, executions=executions,
    mode='command', model=model, run_at=harness.utc_now(), source_eval=os.environ['CONFIG'])
harness.write_evidence({'model': model, 'prompts': [
    {'prompt_id': key, 'output': value, 'execution': executions[key]}
    for key, value in outputs.items()]}, run_dir / 'capture.yaml')
harness.write_evidence(evidence, run_dir / 'evidence.yaml')
harness.print_report(evidence, run_dir / 'evidence.yaml')
raise SystemExit(1 if evidence['summary']['failed'] or evidence['summary']['unscorable'] or evidence['summary']['review_required'] else 0)
PY
