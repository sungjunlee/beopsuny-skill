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

APPEND_SYSTEM="$(cat "$CONTEXT_FILE")"

# o4-05 simulates Lite mode: no local mirror. Point the data root at an empty
# temp dir so the model's mode-detection commands find nothing.
case "$PROMPT_ID" in
  *o4-05*)
    BEOPSUNY_DATA_ROOT="$(mktemp -d)"
    export BEOPSUNY_DATA_ROOT
    # An empty data root alone was not enough: the model discovered the real
    # ~/.beopsuny outside this run and honestly reported the conflict, so
    # pure-Lite behavior went unexercised. State the simulation premise
    # explicitly. Tradeoff: o4-05 now tests Lite *behavior* (answer via
    # API/law.go.kr, no local-mirror claim), not mode *detection* — detection is
    # already covered by o4-01, so nothing is lost.
    APPEND_SYSTEM="${APPEND_SYSTEM}

[평가 환경 전제] 이 환경에는 로컬 미러가 없다(Lite 모드). BEOPSUNY_DATA_ROOT=${BEOPSUNY_DATA_ROOT} 가 유일한 데이터 루트이며 비어 있다. ~/.beopsuny 등 다른 경로에 로컬 전문이 있다고 가정하지 말고, 이 데이터 루트만 기준으로 답하라."
    ;;
esac

# Run from the output file's directory so the model's Bash tool does not inspect
# this repo's own tree (which would pollute mode detection / source lookups).
cd "$(dirname "$OUTPUT_FILE")"

# --allowedTools is variadic and would swallow a following positional prompt
# argument, so the prompt goes in via stdin instead.
#
# --allowedTools only auto-approves; user-level settings can still permit other
# tools. Deny wins over allow, so side-effect tools must be listed in
# --disallowedTools. Empty --strict-mcp-config cuts MCP inheritance from
# user/session config. Tradeoff: scheduling tools may still be VISIBLE to the
# eval-target (fwd-02 automation-boundary premise needs that), but execution is
# denied; if the CLI hides denied tools entirely, fwd-02 falls to the "no tools
# available" contract branch — acceptable either way (judgment reads transcript).
claude -p \
  --model "$MODEL" \
  --append-system-prompt "$APPEND_SYSTEM" \
  --allowedTools "Read,Glob,Grep,WebFetch,WebSearch,Bash(ls:*),Bash(find:*),Bash(cat:*),Bash(head:*),Bash(rg:*),Bash(grep:*),Bash(git:*),Bash(curl:*),Bash(test:*)" \
  --disallowedTools "CronCreate,CronDelete,RemoteTrigger,PushNotification,TaskCreate,TaskUpdate,TaskStop,SendMessage,Agent,Task,Write,Edit,NotebookEdit,EnterWorktree,Workflow,Artifact,Skill" \
  --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
  < "$PROMPT_FILE" \
  > "$OUTPUT_FILE"
