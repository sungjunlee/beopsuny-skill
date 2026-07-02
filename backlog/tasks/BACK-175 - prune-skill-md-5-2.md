---
id: BACK-175
title: '[Prune] SKILL.md 품질 게이트 5겹 → 2겹 통합 (품질 계약 매핑 삭제 + 응답 품질 게이트 축약)'
status: To Do
labels:
  - area:architecture
  - area:refactor
priority: high
milestone: 
created_date: '2026-07-02'
---
## Description
Part of #174

## 문제

같은 의미("인용은 검증 후 출력")가 항상 로드되는 SKILL.md 안에서만 4곳에 중복:

| 위치 | 내용 |
| --- | --- |
| SKILL.md:59-65 | always-on gate 표 (Citation verification / Self verification / Output contract) |
| SKILL.md:77-88 | 품질 계약 매핑 — 트리거가 "해당 실패모드가 보이면"이라 라우팅 시점에 체크 불가능한 두 번째 라우터. always-on gate 표와 대상도 거의 겹침 |
| SKILL.md:94-98 | 기본 조사 계약 원칙 1·5 |
| SKILL.md:269-287 | 응답 품질 게이트 — `references/self-verification.md`의 4개 차원 + 실패 처리 표를 거의 그대로 재수록한 duplication |

Single source of truth 위반. 에이전트가 어느 gate가 우선인지 매번 조정해야 하고, 326줄 항상-로드 문서의 상당 부분을 반복이 차지.

## 작업

1. **품질 계약 매핑 섹션 삭제**. 유일한 추가 정보인 "계약 충돌 시 우선순위" 문단(SKILL.md:88)만 always-on gate 표 밑으로 이동
2. **응답 품질 게이트 섹션을 2줄로 축약**: "출력 직전 `references/self-verification.md`의 4개 차원(Citation / Legal Substance / Client Alignment / Counter-drafting)을 통과한다" + 실패 시 다운그레이드 pointer
3. 기본 조사 계약 원칙 1·5는 유지하되 citation-verification-contract.md pointer로 정리

## AC

- [ ] SKILL.md에서 "인용 검증" 의미의 authoritative 위치가 always-on gate 표 하나
- [ ] 응답 품질 게이트의 4개 차원 상세·실패 처리 표가 self-verification.md에만 존재
- [ ] SKILL.md ~70줄 절감 (326 → ~255)
- [ ] tests/scenarios 통과 (동작 동등성)

