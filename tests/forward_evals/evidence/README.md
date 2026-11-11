# Forward-eval evidence (committed)

`runs/`는 일회성 산출물이라 gitignore한다. 이 `evidence/` 디렉토리는 반대로,
charter 목표(예: O4 로컬 미러 가용성·degradation 판별 + provenance)를 실증하기 위해 **승격한
스모크 증거만** 골라 커밋하는 곳이다.

1. `runs/`에 나온 evidence YAML 중 대표 스모크 하나를 이 디렉토리로 복사한다.
2. 파일명에 config와 모델, 날짜를 남긴다. 예: `o4-provenance-<model>-YYYYMMDD.yaml`.
3. charter/PR에서 이 경로를 인용한다.
4. 승격된 파일을 포함한 커밋 evidence 전체의 판정 차이를 확인한다.

```bash
PYTHON=${PYTHON:-python3}
PYTHONPATH=.test-deps $PYTHON tests/check_rescore_baseline.py
```

이 명령은 현재 판정에서 파생해 체크인한 비교 기준선
[`rescore_baseline.json`](../rescore_baseline.json)과 재채점 결과를 대조한다. 차이가
있으면 먼저 내용을 검토한 뒤, 갱신 여부와 조건은 계약의 집인
[`tests/check_rescore_baseline.py`의 모듈 docstring](../../check_rescore_baseline.py)과
[루트 README의 품질 계약 변경 체크리스트](../../../README.md#품질-계약-변경-체크리스트)를
따른다. 게이트 실패를 없애기 위해 기준선을 무조건 다시 생성하지 않는다.
