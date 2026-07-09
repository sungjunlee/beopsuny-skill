# Beopsuny Forward Evals

이 폴더는 실제 모델이 법순이 router guardrail을 지키는지 확인하기 위한 수동/반자동 prompt set을 둔다. 법률 정답 채점기가 아니며, core skill 동작을 바꾸지 않는다.

## Prompt set

| 파일 | 목적 | prompt 수 |
| --- | --- | --- |
| `beopsuny_guardrails.yaml` | 고위험 router guardrail (자동화 약속, role/destination, stale asset 등) | 10 |
| `beopsuny_o4_provenance.yaml` | charter O4: Full/Lite 모드 판별 + 4가지 provenance 상태(로컬 미러 / 직접 공식소스 / API fallback / insufficient) | 8 |

`--config`로 어느 세트든 같은 harness/scorer에 넣는다. 세트마다 `guardrail_category`가 있고, scorer의 `CATEGORY_COMMON_RULES`/`CATEGORY_REQUIRED_ANY`가 카테고리별 가드레일을 건다.

## runs/ vs evidence/

- `runs/`: harness가 기본으로 evidence YAML을 쓰는 곳. 일회성이라 gitignore한다(커밋하지 않는다).
- `evidence/`: charter 목표를 실증하기 위해 `runs/`에서 골라 **승격한 스모크 증거만** 커밋한다. charter/PR에서 이 경로를 인용한다.

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

### O4 세트 라이브 실행 (`run_claude_live.sh`)

O4 provenance 세트는 라이브 러너 `run_claude_live.sh`와 함께 command 모드로 돌린다. 러너는 harness가 넘기는 `BEOPSUNY_EVAL_*` 환경변수를 읽어 `claude -p`를 호출하고, `o4-05`일 때는 `BEOPSUNY_DATA_ROOT`를 빈 임시 디렉토리로 설정해 Lite 환경을 시뮬레이션한다. output 파일 디렉토리로 cd해서 이 repo 트리가 모드 판별을 오염시키지 않게 한다.

```bash
PYTHONPATH=.test-deps python3 tests/forward_eval_harness.py --mode command \
  --config tests/forward_evals/beopsuny_o4_provenance.yaml \
  --model claude-sonnet-5 \
  --command 'tests/forward_evals/run_claude_live.sh' \
  --evidence tests/forward_evals/runs/o4-live.yaml
```

승격할 스모크는 `runs/o4-live.yaml`을 `evidence/o4-provenance-<model>-YYYYMMDD.yaml`로 복사해 커밋한다.

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
