#!/usr/bin/env bash
# Foreground parallel driver for a full live forward-eval run.
#
# Env (defaults):
#   CONFIG  tests/forward_evals/beopsuny_guardrails.yaml
#   MODEL   claude-sonnet-5
#   PAR     4
#   RUN_DIR tests/forward_evals/runs/live-$(basename "$CONFIG" .yaml)
#   RUNNER  tests/forward_evals/run_claude_live.sh  (override with a mock for dry tests)
#
# Known traps:
#   (a) `claude -p --allowedTools` is variadic and swallows a positional prompt —
#       prompts go via stdin (handled in run_claude_live.sh).
#   (b) Some orchestration environments kill long background tasks — run this
#       driver in FOREGROUND; incremental skip makes interrupted runs resumable.
#   (c) macOS xargs -I has replacement-length limits — hence a plain bash loop.
#   (d) Side-effect blocking lives in run_claude_live.sh (--disallowedTools +
#       --strict-mcp-config, #223).
#
# Usage (from anywhere; resolves repo root from this script):
#   CONFIG=tests/forward_evals/beopsuny_o4_provenance.yaml MODEL=claude-sonnet-5 \
#     tests/forward_evals/run_live_parallel.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$ROOT"

CONFIG="${CONFIG:-tests/forward_evals/beopsuny_guardrails.yaml}"
MODEL="${MODEL:-claude-sonnet-5}"
PAR="${PAR:-4}"
RUN_DIR="${RUN_DIR:-tests/forward_evals/runs/live-$(basename "$CONFIG" .yaml)}"
RUNNER="${RUNNER:-tests/forward_evals/run_claude_live.sh}"

[[ "$CONFIG" = /* ]] || CONFIG="$ROOT/$CONFIG"
[[ "$RUN_DIR" = /* ]] || RUN_DIR="$ROOT/$RUN_DIR"
[[ "$RUNNER" = /* ]] || RUNNER="$ROOT/$RUNNER"

mkdir -p "$RUN_DIR/outputs"

# 1. Template + packets (skip if packets already exist so re-runs reuse them).
# Harness template mode writes via --evidence (not --outputs).
if [[ ! -d "$RUN_DIR/packets" ]]; then
  echo "template: generating packets + capture-template.yaml under $RUN_DIR"
  PYTHONPATH=.test-deps python3 tests/forward_eval_harness.py \
    --config "$CONFIG" \
    --mode template \
    --packet-dir "$RUN_DIR/packets" \
    --evidence "$RUN_DIR/capture-template.yaml"
else
  echo "template: reusing existing packets at $RUN_DIR/packets"
fi

# 2. Parallel execution with incremental resume (non-empty outputs skipped).
running=0
for prompt_dir in "$RUN_DIR/packets"/*/; do
  [[ -d "$prompt_dir" ]] || continue
  id="$(basename "$prompt_dir")"
  out_file="$RUN_DIR/outputs/${id}.txt"
  if [[ -s "$out_file" ]]; then
    echo "skip: $id (non-empty $out_file)"
    continue
  fi
  echo "start: $id"
  (
    BEOPSUNY_EVAL_CONTEXT_FILE="${prompt_dir}context.md" \
    BEOPSUNY_EVAL_PROMPT_FILE="${prompt_dir}prompt.txt" \
    BEOPSUNY_EVAL_OUTPUT_FILE="$out_file" \
    BEOPSUNY_EVAL_PROMPT_ID="$id" \
    BEOPSUNY_EVAL_MODEL="$MODEL" \
      "$RUNNER"
  ) &
  running=$((running + 1))
  if (( running >= PAR )); then
    wait
    running=0
  fi
done
wait

# 3. Assemble capture.yaml from template + per-prompt outputs.
export RUN_DIR MODEL
PYTHONPATH=.test-deps python3 <<'PY'
import os
from pathlib import Path

import yaml

run_dir = Path(os.environ["RUN_DIR"])
model = os.environ["MODEL"]
template_path = run_dir / "capture-template.yaml"
capture = yaml.safe_load(template_path.read_text(encoding="utf-8"))
for prompt in capture.get("prompts", []):
    prompt_id = str(prompt["prompt_id"])
    out_path = run_dir / "outputs" / f"{prompt_id}.txt"
    if out_path.is_file():
        prompt["output"] = out_path.read_text(encoding="utf-8")
    else:
        prompt["output"] = ""
    prompt["model"] = model
capture["model"] = model
out = run_dir / "capture.yaml"
out.write_text(yaml.safe_dump(capture, allow_unicode=True, sort_keys=False), encoding="utf-8")
print(f"capture: {out}")
PY

# 4. Score. Always exit 0 after printing — live runs are judged by reading evidence.
scorer_status=0
PYTHONPATH=.test-deps python3 tests/forward_eval_harness.py \
  --config "$CONFIG" \
  --mode score \
  --outputs "$RUN_DIR/capture.yaml" \
  --model "$MODEL" \
  --evidence "$RUN_DIR/evidence.yaml" \
  --no-fail-on-regression || scorer_status=$?

echo "SCORER: status=${scorer_status} evidence=${RUN_DIR}/evidence.yaml"
exit 0
