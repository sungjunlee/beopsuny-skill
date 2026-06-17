# Beopsuny Forward Evals

이 폴더는 실제 모델이 법순이 router guardrail을 지키는지 확인하기 위한 수동/반자동 prompt set을 둔다. 법률 정답 채점기가 아니며, core skill 동작을 바꾸지 않는다.

## 실행 방법

### 자동 harness

라이브 모델/API 인증 경로가 안정적으로 고정되어 있지 않으므로 이 harness는 CI 필수 gate가 아니다. 대신 같은 scorer로 sample, manual capture, command 실행을 모두 처리한다. evidence YAML은 기본적으로 `tests/forward_evals/runs/` 아래에 기록되며, run 산출물은 커밋하지 않는다.

Dry/sample 실행:

```bash
PYTHONPATH=.test-deps python3 tests/forward_eval_harness.py --mode sample \
  --evidence tests/forward_evals/runs/sample.yaml
```

수동 capture 템플릿 생성:

```bash
PYTHONPATH=.test-deps python3 tests/forward_eval_harness.py --mode template \
  --evidence tests/forward_evals/runs/manual-capture.yaml \
  --packet-dir tests/forward_evals/runs/manual-packets
```

각 prompt를 `manual-packets/{prompt_id}/context.md`와 `prompt.txt`로 깨끗한 skill context에서 실행한 뒤, `manual-capture.yaml`의 `output`에 붙여 넣고 채점한다.

```bash
PYTHONPATH=.test-deps python3 tests/forward_eval_harness.py --mode score \
  --outputs tests/forward_evals/runs/manual-capture.yaml \
  --evidence tests/forward_evals/runs/manual-scored.yaml \
  --model "manual-capture"
```

명령 기반 실행도 가능하다. `{context_file}`, `{prompt_file}`, `{output_file}`, `{prompt_id}`, `{model}` placeholder는 prompt별 임시 파일로 치환된다. 명령이 stdout을 내거나 `{output_file}`에 응답을 쓰면 scorer가 같은 evidence 포맷으로 기록한다.

```bash
PYTHONPATH=.test-deps python3 tests/forward_eval_harness.py --mode command \
  --model "local-model-label" \
  --command 'your-runner --context {context_file} --prompt {prompt_file} > {output_file}' \
  --evidence tests/forward_evals/runs/command-scored.yaml
```

실패 리포트는 `prompt_id`, `guardrail_category`, `guardrail`, `evidence`를 함께 남긴다.

### 원본 수동 절차

1. 새 대화 또는 깨끗한 eval harness에 `skills/beopsuny/SKILL.md`를 system/skill context로 로드한다.
2. `beopsuny_guardrails.yaml`의 각 `prompt`를 그대로 실행한다.
3. 출력마다 `expected_guardrails`가 드러나는지 확인하고, `forbidden_failures`가 있으면 실패로 기록한다.
4. 실패는 `guardrail_category`, `source_router_scenario`, 출력 전문, 사용 모델/날짜와 함께 이슈로 남긴다.

기존 빠른 CI gate는 계속 아래 명령이다.

```bash
PYTHON=${PYTHON:-python3}
$PYTHON -m pip install --no-input --disable-pip-version-check --target .test-deps -r requirements-dev.txt
PYTHONPATH=.test-deps $PYTHON tests/validate_skill_contracts.py
PYTHONPATH=.test-deps $PYTHON tests/evaluate_scenario_outputs.py
```
