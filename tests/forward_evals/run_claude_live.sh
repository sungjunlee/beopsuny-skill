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
# Optional, for evaluating the default tool path (legalize tools + korean-law-mcp).
# Unset means the historical behavior (no MCP servers, base tool list, no trace).
#   BEOPSUNY_EVAL_MCP_CONFIG          absolute path to an MCP config file. Inline JSON and
#                                     relative paths are rejected (values are never echoed);
#                                     reference secrets as ${LAW_OC} inside the file and export
#                                     them in the caller environment. Setting this forces trace
#                                     mode, auto-allows mcp__<server> tools, and the run fails
#                                     unless every server connects and no tool-path call is denied.
#   BEOPSUNY_EVAL_EXTRA_ALLOWED_TOOLS comma-separated extra --allowedTools, e.g. Bash(legalize:*),Bash(uvx:*)
#   BEOPSUNY_EVAL_EMPTY_DATA_ROOT=1   simulate a data root with no local mirror (as o4-05 does)
#   BEOPSUNY_EVAL_CLAUDE_BIN          replace the claude executable (runner tests use a fake)
#   BEOPSUNY_EVAL_TRACE=1             keep tool calls (stream-json) under BEOPSUNY_EVAL_TRACE_DIR
#   BEOPSUNY_EVAL_TRACE_DIR           absolute path; default tests/forward_evals/runs/traces
#                                     (gitignored). OC= values and $LAW_OC are masked in the
#                                     trace and the answer. Keep traces out of evidence/ unless
#                                     reviewed. Tool-path runs are slow: raise BEOPSUNY_EVAL_TIMEOUT.
#
# Usage (from repo root):
#   PYTHONPATH=.test-deps python3 tests/forward_eval_harness.py --mode command \
#     --config tests/forward_evals/beopsuny_o4_provenance.yaml \
#     --model claude-sonnet-5 \
#     --command 'tests/forward_evals/run_claude_live.sh' \
#     --evidence tests/forward_evals/runs/o4-live.yaml
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL="${BEOPSUNY_EVAL_MODEL:-claude-sonnet-5}"
CONTEXT_FILE="${BEOPSUNY_EVAL_CONTEXT_FILE:?BEOPSUNY_EVAL_CONTEXT_FILE is required}"
PROMPT_FILE="${BEOPSUNY_EVAL_PROMPT_FILE:?BEOPSUNY_EVAL_PROMPT_FILE is required}"
OUTPUT_FILE="${BEOPSUNY_EVAL_OUTPUT_FILE:?BEOPSUNY_EVAL_OUTPUT_FILE is required}"
PROMPT_ID="${BEOPSUNY_EVAL_PROMPT_ID:-unknown}"

APPEND_SYSTEM="$(cat "$CONTEXT_FILE")"

# Remove only what this script created (never a caller-provided data root).
CREATED_ROOT=""
cleanup() {
  [[ -n "$CREATED_ROOT" ]] && rm -rf -- "$CREATED_ROOT"
  return 0
}
trap cleanup EXIT

# o4-05 simulates a data root with no local mirror at all (the degradation
# path). Point the data root at an empty temp dir so the model's availability
# probes find nothing. The glob stays `*o4-05*` so the #240 id rename
# (o4-05-lite-mode-identification -> o4-05-no-mirror-degradation-path) and any
# future o4-05-* rename keep matching.
if [[ "$PROMPT_ID" == *o4-05* || "${BEOPSUNY_EVAL_EMPTY_DATA_ROOT:-}" == "1" ]]; then
    BEOPSUNY_DATA_ROOT="$(mktemp -d)"
    CREATED_ROOT="$BEOPSUNY_DATA_ROOT"
    export BEOPSUNY_DATA_ROOT
    # An empty data root alone was not enough: the model discovered the real
    # ~/.beopsuny outside this run and honestly reported the conflict, so the
    # pure no-mirror behavior went unexercised. State the simulation premise
    # explicitly. Tradeoff: o4-05 now tests degradation *behavior* (answer via
    # API/law.go.kr, no local-mirror claim), not availability *detection* —
    # detection is already covered by o4-01, so nothing is lost.
    # The historical premise stays byte-identical for the default path so past
    # o4-05 evidence remains comparable; the opt-in tool path names its own route.
    NO_MIRROR_ROUTE="법망 API·law.go.kr degradation 경로"
    if [[ "${BEOPSUNY_EVAL_EMPTY_DATA_ROOT:-}" == "1" ]]; then
      NO_MIRROR_ROUTE="기본 도구 또는 law.go.kr 경로"
    fi
    APPEND_SYSTEM="${APPEND_SYSTEM}

[평가 환경 전제] 이 환경에는 로컬 미러가 없다(${NO_MIRROR_ROUTE}). BEOPSUNY_DATA_ROOT=${BEOPSUNY_DATA_ROOT} 가 유일한 데이터 루트이며 비어 있다. ~/.beopsuny 등 다른 경로에 로컬 전문이 있다고 가정하지 말고, 이 데이터 루트만 기준으로 답하라."
fi

MCP_CONFIG='{"mcpServers":{}}'
TRACE="${BEOPSUNY_EVAL_TRACE:-}"
REQUIRE_MCP=0
if [[ -n "${BEOPSUNY_EVAL_MCP_CONFIG:-}" ]]; then
  # Never echo the value: it may carry a key.
  if [[ "$BEOPSUNY_EVAL_MCP_CONFIG" != /* || ! -f "$BEOPSUNY_EVAL_MCP_CONFIG" ]]; then
    echo "run_claude_live: BEOPSUNY_EVAL_MCP_CONFIG must be an absolute path to an existing file (value not shown)" >&2
    exit 2
  fi
  MCP_CONFIG="$BEOPSUNY_EVAL_MCP_CONFIG"
  TRACE=1
  REQUIRE_MCP=1
fi
ALLOWED_TOOLS="Read,Glob,Grep,WebFetch,WebSearch,Bash(ls:*),Bash(find:*),Bash(cat:*),Bash(head:*),Bash(rg:*),Bash(grep:*),Bash(git:*),Bash(curl:*),Bash(test:*)"
TOOL_PATH=$REQUIRE_MCP
if [[ -n "${BEOPSUNY_EVAL_EXTRA_ALLOWED_TOOLS:-}" ]]; then
  ALLOWED_TOOLS="${ALLOWED_TOOLS},${BEOPSUNY_EVAL_EXTRA_ALLOWED_TOOLS}"
  TRACE=1
  TOOL_PATH=1
fi
if [[ "${BEOPSUNY_EVAL_EMPTY_DATA_ROOT:-}" == "1" ]]; then
  TRACE=1
fi
if [[ "$REQUIRE_MCP" == "1" && -z "${LAW_OC:-}" ]]; then
  echo "[eval-runner] warning: LAW_OC is not exported; only OC=... patterns can be masked" >&2
fi
if [[ "$REQUIRE_MCP" == "1" ]]; then
  # Headless runs deny tools that are not pre-approved, so a connected server
  # would still be unusable without its mcp__<server> entry.
  MCP_TOOLS="$(python3 -c 'import json,sys; print(",".join("mcp__"+n for n in json.load(open(sys.argv[1])).get("mcpServers",{})))' "$MCP_CONFIG")"
  if [[ -n "$MCP_TOOLS" ]]; then
    ALLOWED_TOOLS="${ALLOWED_TOOLS},${MCP_TOOLS}"
  fi
fi
if [[ "$TRACE" == "1" ]]; then
  TRACE_DIR="${BEOPSUNY_EVAL_TRACE_DIR:-$SCRIPT_DIR/runs/traces}"
  if [[ "$TRACE_DIR" != /* ]]; then
    echo "run_claude_live: BEOPSUNY_EVAL_TRACE_DIR must be an absolute path" >&2
    exit 2
  fi
  mkdir -p "$TRACE_DIR"
  TRACE_FILE="$TRACE_DIR/${PROMPT_ID}.trace.jsonl"
  # Run conditions without secrets, printed before the call so failed runs carry them too.
  echo "[eval-runner] mcp_config=$([[ $REQUIRE_MCP == 1 ]] && echo set || echo none) extra_tools=${BEOPSUNY_EVAL_EXTRA_ALLOWED_TOOLS:--} empty_data_root=${BEOPSUNY_EVAL_EMPTY_DATA_ROOT:-0} trace=${PROMPT_ID}.trace.jsonl" >&2
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
# BEOPSUNY_EVAL_CLAUDE_BIN replaces the claude executable (tests use a fake; never
# rely on PATH order, which differs between shells and Windows process lookup).
read -r -a CLAUDE_CMD <<< "${BEOPSUNY_EVAL_CLAUDE_BIN:-claude}"
CLAUDE_ARGS=(
  -p
  --model "$MODEL"
  --append-system-prompt "$APPEND_SYSTEM"
  --allowedTools "$ALLOWED_TOOLS"
  --disallowedTools "CronCreate,CronDelete,RemoteTrigger,PushNotification,TaskCreate,TaskUpdate,TaskStop,SendMessage,Agent,Task,Write,Edit,NotebookEdit,EnterWorktree,Workflow,Artifact,Skill"
  --strict-mcp-config --mcp-config "$MCP_CONFIG"
)

if [[ "$TRACE" != "1" ]]; then
  "${CLAUDE_CMD[@]}" "${CLAUDE_ARGS[@]}" < "$PROMPT_FILE" > "$OUTPUT_FILE"
  exit 0
fi

# Trace mode: tool-call inputs are evidence for remote-lookup boundaries (what was
# sent to a remote tool). The answer file holds only the final text. The stream is
# masked line by line before it touches disk, so a killed run never leaves an
# unmasked trace. An inner timeout (shorter than the harness timeout) ends claude
# first so the normal failure path runs. A run whose MCP servers did not all
# connect, whose tool-path calls were denied, or whose result is an error exits
# non-zero and is recorded as an execution error, never as a scored answer.
INNER_TIMEOUT=$(( ${BEOPSUNY_EVAL_TIMEOUT:-300} - 30 ))
(( INNER_TIMEOUT < 30 )) && INNER_TIMEOUT=30
RUN_TRACED='
import json, os, re, subprocess, sys, threading

trace_path, output_path, prompt_path, require_mcp, tool_path, inner = sys.argv[1:7]
cmd = sys.argv[7:]
secret = os.environ.get("LAW_OC", "")
PATTERNS = [
    (re.compile(r"(\bOC=)[^&\"\s\\]+", re.I), r"\1REDACTED"),
    (re.compile(r"(OC%3D)[^&\"\s\\%]+", re.I), r"\1REDACTED"),
    # also the escaped form inside a JSON string value (\"oc\": \"...\")
    (re.compile(r"(\\?\"(?:oc|law_oc)\\?\"\s*:\s*\\?\")[^\\\"]+", re.I), r"\1REDACTED"),
]


def mask(text):
    for pattern, repl in PATTERNS:
        text = pattern.sub(repl, text)
    return text.replace(secret, "REDACTED") if secret else text


servers, result_event = [], None
with open(prompt_path, "rb") as stdin, open(trace_path, "w", encoding="utf-8") as trace:
    proc = subprocess.Popen(cmd, stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    timed_out = []
    timer = threading.Timer(int(inner), lambda: (timed_out.append(1), proc.kill()))
    timer.start()
    err_chunks = []
    reader = threading.Thread(target=lambda: err_chunks.append(proc.stderr.read()))
    reader.start()
    for line in proc.stdout:
        trace.write(mask(line))
        trace.flush()
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "system" and event.get("subtype") == "init":
            servers = event.get("mcp_servers") or []
        elif event.get("type") == "result":
            result_event = event
    rc = proc.wait()
    timer.cancel()
    reader.join()
sys.stderr.write(mask("".join(err_chunks)))

status = ",".join(str(x.get("name")) + ":" + str(x.get("status")) for x in servers) or "none"
print(f"[eval-runner] mcp={status}", file=sys.stderr)
if timed_out:
    print(f"[eval-runner] inner timeout {inner}s; masked trace kept", file=sys.stderr)
    sys.exit(124)
if rc != 0:
    print(f"[eval-runner] claude exited {rc}; masked trace kept", file=sys.stderr)
    sys.exit(rc)
if require_mcp == "1" and (not servers or any(s.get("status") != "connected" for s in servers)):
    print("[eval-runner] MCP server not connected; refusing to score a tool-less run", file=sys.stderr)
    sys.exit(1)
if result_event is None or result_event.get("is_error") or result_event.get("subtype", "success") != "success":
    print("[eval-runner] no successful result event", file=sys.stderr)
    sys.exit(1)

TOOL_TOKEN = re.compile(r"(?:^|[\s;&|/(])(?:legalize|uvx)(?:\s|$)")


def tool_path_denial(denial):
    name = str(denial.get("tool_name", ""))
    command = str((denial.get("tool_input") or {}).get("command", ""))
    return name.startswith("mcp__") or (name == "Bash" and bool(TOOL_TOKEN.search(command)))


denied = [d for d in result_event.get("permission_denials") or [] if tool_path_denial(d)]
if tool_path == "1" and denied:
    print("[eval-runner] tool-path calls denied: " + ",".join(sorted({str(x.get("tool_name")) for x in denied})), file=sys.stderr)
    sys.exit(1)
answer = result_event.get("result") or ""
masked = mask(answer)
if masked != answer:
    print("[eval-runner] masked a secret in the answer", file=sys.stderr)
with open(output_path, "w", encoding="utf-8") as fh:
    fh.write(masked)
'
python3 -c "$RUN_TRACED" "$TRACE_FILE" "$OUTPUT_FILE" "$PROMPT_FILE" "$REQUIRE_MCP" "$TOOL_PATH" "$INNER_TIMEOUT" \
  "${CLAUDE_CMD[@]}" "${CLAUDE_ARGS[@]}" --output-format stream-json --verbose
