# Beopsuny Forward Evals

이 폴더는 실제 모델이 법순이 router guardrail을 지키는지 확인하기 위한 수동/반자동 prompt set을 둔다. 법률 정답 채점기가 아니며, core skill 동작을 바꾸지 않는다.

## 실행 방법

1. 새 대화 또는 깨끗한 eval harness에 `skills/beopsuny/SKILL.md`를 system/skill context로 로드한다.
2. `beopsuny_guardrails.yaml`의 각 `prompt`를 그대로 실행한다.
3. 출력마다 `expected_guardrails`가 드러나는지 확인하고, `forbidden_failures`가 있으면 실패로 기록한다.
4. 실패는 `guardrail_category`, `source_router_scenario`, 출력 전문, 사용 모델/날짜와 함께 이슈로 남긴다.

기존 빠른 CI gate는 계속 아래 명령이다.

```bash
python3 -m pip install --no-input --disable-pip-version-check --target .test-deps -r requirements-dev.txt
PYTHONPATH=.test-deps python3 tests/validate_skill_contracts.py
PYTHONPATH=.test-deps python3 tests/evaluate_scenario_outputs.py
```
