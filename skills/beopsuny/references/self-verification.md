# 자가 검증 근거 자료

> SKILL.md `자가 검증 (응답 전)` 섹션이 왜 필요한지에 대한 외부 근거 모음.
> SKILL.md 본문에서 인라인 인용된 연구·보고서를 이쪽으로 분리해 본문 rot 를 방지한다.

## 법률 AI 할루시네이션 연구

- **Stanford 2025** — 상업 법률 AI 도구(LexisNexis+, Westlaw AI-Assisted Research, Practical Law 등) 도 **1/6 ~ 1/3 쿼리** 에서 할루시네이션(존재하지 않는 판례·조문·오인용) 이 발생한다고 보고. 법률 분야에서 부정확한 인용은 실제 피해(잘못된 결론, 서면 제출, 의뢰인 손해)로 이어진다.
  - SKILL.md 의 Dim 1 (Citation 검증) 이 존재 여부·조항 번호·취지 일치·판례 사건번호 형식을 **4 개 체크**로 규정한 근거.
  - 링크는 연구 공개 시점에 확인해 갱신한다. 본 문서는 claim 의 출처 트래킹용.

## 자가 검증 = 응답 직전 단계

- 별도 서브에이전트 호출 없이 SKILL.md 내부 프롬프트로 처리한다는 설계 선택의 근거:
  - 법률 분야는 "빠른 응답 + 깊은 검증" 트레이드오프가 있지만, 자가 검증 비용이 latency 대비 피해 회피 가치가 압도적으로 크다.
  - Source Grading 의 `downgrade_triggers` (`assets/policies/source_grades.yaml`) 와 연동되어 **tag 체계 외 새 타입을 도입하지 않는** 최소 침습 설계.

## 보강 권장

- 향후 연구 인용이 추가되면 본 문서 하단에 append-only 로 쌓아 SKILL.md 가 rot 되지 않도록 한다.
- 연구 링크가 사라진 경우 "archive.org snapshot" 링크를 병기한다.
