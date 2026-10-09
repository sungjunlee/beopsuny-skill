#!/usr/bin/env bash
# Live runner for forward_eval_harness.py command mode.
#
# The harness sets these per prompt and re-invokes this script once per prompt:
#   BEOPSUNY_EVAL_CONTEXT_FILE  clean skill context (SKILL.md + source_references)
#   BEOPSUNY_EVAL_PROMPT_FILE   the user prompt
#   BEOPSUNY_EVAL_OUTPUT_FILE   where to write the model answer
#   BEOPSUNY_EVAL_PROMPT_ID     e.g. o4-05-no-mirror-degradation-path
#   BEOPSUNY_EVAL_MODEL         model label (default below)
#
# Optional, for evaluating the default tool path (legalize tools + korean-law-mcp):
#   BEOPSUNY_EVAL_MCP_CONFIG          MCP config JSON or file path (default: no MCP servers)
#   BEOPSUNY_EVAL_EXTRA_ALLOWED_TOOLS comma-separated extra --allowedTools, e.g. Bash(legalize:*),Bash(uvx:*)
#   BEOPSUNY_EVAL_EMPTY_DATA_ROOT=1   simulate a data root with no local mirror (as o4-05 does)
#   BEOPSUNY_EVAL_TRACE=1             keep tool calls in ${OUTPUT_FILE%.*}.trace.jsonl
# Secrets (e.g. LAW_OC inside the MCP config) stay in the caller's environment; never commit them.
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

# o4-05 simulates a data root with no local mirror at all (the degradation
# path). Point the data root at an empty temp dir so the model's availability
# probes find nothing. The glob stays `*o4-05*` so the #240 id rename
# (o4-05-lite-mode-identification -> o4-05-no-mirror-degradation-path) and any
# future o4-05-* rename keep matching.
if [[ "$PROMPT_ID" == *o4-05* || "${BEOPSUNY_EVAL_EMPTY_DATA_ROOT:-}" == "1" ]]; then
    BEOPSUNY_DATA_ROOT="$(mktemp -d)"
    export BEOPSUNY_DATA_ROOT
    trap 'rm -rf -- "$BEOPSUNY_DATA_ROOT"' EXIT
    # An empty data root alone was not enough: the model discovered the real
    # ~/.beopsuny outside this run and honestly reported the conflict, so the
    # pure no-mirror behavior went unexercised. State the simulation premise
    # explicitly. Tradeoff: o4-05 now tests degradation *behavior* (answer via
    # API/law.go.kr, no local-mirror claim), not availability *detection* —
    # detection is already covered by o4-01, so nothing is lost.
    APPEND_SYSTEM="${APPEND_SYSTEM}

[평가 환경 전제] 이 환경에는 로컬 미러가 없다(기본 도구 또는 law.go.kr 경로). BEOPSUNY_DATA_ROOT=${BEOPSUNY_DATA_ROOT} 가 유일한 데이터 루트이며 비어 있다. ~/.beopsuny 등 다른 경로에 로컬 전문이 있다고 가정하지 말고, 이 데이터 루트만 기준으로 답하라."
fi

MCP_CONFIG='{"mcpServers":{}}'
if [[ -n "${BEOPSUNY_EVAL_MCP_CONFIG:-}" ]]; then
  MCP_CONFIG="$BEOPSUNY_EVAL_MCP_CONFIG"
fi
ALLOWED_TOOLS="Read,Glob,Grep,WebFetch,WebSearch,Bash(ls:*),Bash(find:*),Bash(cat:*),Bash(head:*),Bash(rg:*),Bash(grep:*),Bash(git:*),Bash(curl:*),Bash(test:*)"
if [[ -n "${BEOPSUNY_EVAL_EXTRA_ALLOWED_TOOLS:-}" ]]; then
  ALLOWED_TOOLS="${ALLOWED_TOOLS},${BEOPSUNY_EVAL_EXTRA_ALLOWED_TOOLS}"
fi

# Run from the output file's directory so the model's Bash tool does not inspect
# this repo's own tree (which would pollute mode detection / source lookups).
cd "${BEOPSUNY_EVAL_WORKSPACE:-$(dirname "$OUTPUT_FILE")}"

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
CLAUDE_ARGS=(
  -p
  --model "$MODEL"
  --append-system-prompt "$APPEND_SYSTEM"
  --allowedTools "$ALLOWED_TOOLS"
  --disallowedTools "CronCreate,CronDelete,RemoteTrigger,PushNotification,TaskCreate,TaskUpdate,TaskStop,SendMessage,Agent,Task,Write,Edit,NotebookEdit,EnterWorktree,Workflow,Artifact,Skill"
  --strict-mcp-config --mcp-config "$MCP_CONFIG"
)

if [[ "${BEOPSUNY_EVAL_TRACE:-}" == "1" ]]; then
  # Tool-call inputs are evidence for remote-lookup boundaries (what was sent to a
  # remote tool); the answer file still holds only the final text.
  TRACE_FILE="${OUTPUT_FILE%.*}.trace.jsonl"
  claude "${CLAUDE_ARGS[@]}" --output-format stream-json --verbose < "$PROMPT_FILE" > "$TRACE_FILE"
  python3 - "$TRACE_FILE" "$OUTPUT_FILE" <<'PY'
import json, sys
result = ""
with open(sys.argv[1], encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "result":
            result = event.get("result") or ""
with open(sys.argv[2], "w", encoding="utf-8") as fh:
    fh.write(result)
PY
else
  claude "${CLAUDE_ARGS[@]}" < "$PROMPT_FILE" > "$OUTPUT_FILE"
fi
