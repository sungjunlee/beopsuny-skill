# Forward-eval evidence (committed)

`runs/`는 일회성 산출물이라 gitignore한다. 이 `evidence/` 디렉토리는 반대로,
charter 목표(예: O4 Full/Lite 모드 판별 + provenance)를 실증하기 위해 **승격한
스모크 증거만** 골라 커밋하는 곳이다.

- run: `runs/`에 나온 evidence YAML 중 대표 스모크 하나를 이 디렉토리로 복사한다.
- 파일명에 config와 모델, 날짜를 남긴다. 예: `o4-provenance-<model>-YYYYMMDD.yaml`.
- charter/PR에서 이 경로를 인용한다.
