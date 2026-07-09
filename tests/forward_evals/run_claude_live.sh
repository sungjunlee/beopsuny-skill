#!/usr/bin/env bash
# Live runner for forward_eval_harness.py command mode.
#
# The harness sets these per prompt and re-invokes this script once per prompt:
#   BEOPSUNY_EVAL_CONTEXT_FILE  clean skill context (SKILL.md + source_references)
#   BEOPSUNY_EVAL_PROMPT_FILE   the user prompt
#   BEOPSUNY_EVAL_OUTPUT_FILE   where to write the model answer
#   BEOPSUNY_EVAL_PROMPT_ID     e.g. o4-05-lite-mode-identification
#   BEOPSUNY_EVAL_MODEL         model label (default below)
#
# Usage (from repo root):
#   PYTHONPATH=.test-deps python3 tests/forward_eval_harness.py --mode command \
#     --config tests/forward_evals/beopsuny_o4_provenance.yaml \
#     --model claude-sonnet-5 \
#     --command 'tests/forward_evals/run_claude_live.sh' \
#     --evidence tests/forward_evals/runs/o4-live.yaml
set -euo pipefail

MODEL="${BEOPSUNY_EVAL_MODEL:-claude-sonnet-5}"
CONTEXT_FILE="${BEOPSUNY_EVAL_CONTEXT_FILE:?BEOPSUNY_EVAL_CONTEXT_FILE is required}"
PROMPT_FILE="${BEOPSUNY_EVAL_PROMPT_FILE:?BEOPSUNY_EVAL_PROMPT_FILE is required}"
OUTPUT_FILE="${BEOPSUNY_EVAL_OUTPUT_FILE:?BEOPSUNY_EVAL_OUTPUT_FILE is required}"
PROMPT_ID="${BEOPSUNY_EVAL_PROMPT_ID:-unknown}"

# o4-05 simulates Lite mode: no local mirror. Point the data root at an empty
# temp dir so the model's mode-detection commands find nothing.
case "$PROMPT_ID" in
  *o4-05*)
    BEOPSUNY_DATA_ROOT="$(mktemp -d)"
    export BEOPSUNY_DATA_ROOT
    ;;
esac

# Run from the output file's directory so the model's Bash tool does not inspect
# this repo's own tree (which would pollute mode detection / source lookups).
cd "$(dirname "$OUTPUT_FILE")"

# --allowedTools is variadic and would swallow a following positional prompt
# argument, so the prompt goes in via stdin instead.
claude -p \
  --model "$MODEL" \
  --append-system-prompt "$(cat "$CONTEXT_FILE")" \
  --allowedTools "Read,Glob,Grep,WebFetch,WebSearch,Bash(ls:*),Bash(find:*),Bash(cat:*),Bash(head:*),Bash(rg:*),Bash(grep:*),Bash(git:*),Bash(curl:*),Bash(test:*)" \
  < "$PROMPT_FILE" \
  > "$OUTPUT_FILE"
