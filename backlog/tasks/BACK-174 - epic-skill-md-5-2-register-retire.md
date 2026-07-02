---
id: BACK-174
title: '[EPIC] SKILL.md 프루닝 사이클 — 게이트 5겹을 2겹으로, register를 retire로'
status: To Do
labels:
  - epic
  - area:architecture
  - area:refactor
priority: high
milestone: 
created_date: '2026-07-02'
---
## Description
## 배경

`/writing-great-skills` 기준 + anthropics/claude-for-legal 비교군으로 스킬 크리틱을 수행한 결과 (2026-07-02):

- **아키텍처(단일 스킬 + 의도 라우터 + progressive disclosure)는 목표에 부합** — claude-for-legal(151개 스킬, 3.5만 줄)을 따라갈 이유 없음
- **문제는 품질 통제 장치의 퇴적**: 지금까지 layer를 *더하는* 방식으로 신뢰를 쌓아왔고("Harden trust contract release gates" 등), 다음 단계는 *빼면서* 같은 신뢰를 유지하는 프루닝 사이클

## 핵심 진단

| 심각도 | 진단 |
| --- | --- |
| HIGH | 품질 게이트가 SKILL.md 안에서만 4곳, 전체 5겹 중복 (always-on gate 표 / 품질 계약 매핑 / 기본 조사 계약 / 응답 품질 게이트 / self-verification.md) |
| HIGH | 품질 계약 매핑 섹션은 라우팅 시점에 체크 불가능한 두 번째 라우터 — collapse 후보 |
| MED | Legal Verification Core 6단계 파이프라인의 "축약형 적용" 조건이 checkable하지 않음 |
| MED | "과잉 라우팅 금지" 같은 의미가 5곳에 산재 |
| LOW | assets ~9,100줄 YAML의 신선도 부채 — freshness debt를 register가 아니라 retire로 |

## 서브이슈 (실행 순서)

- [ ] #175 SKILL.md 품질 게이트 5겹 → 2겹 통합
- [ ] #176 과잉 라우팅 금지 규칙 5곳 → 1곳 통합
- [ ] #177 Legal Verification Core에 체크 가능한 2단 트리거 도입
- [ ] #178 시나리오 기반 asset 감사 + retire 사이클

순서 근거: 1번이 SKILL.md 구조를 정리하는 기반 작업(의존성 없음, 되돌리기 쉬움) → 2번은 1번 이후 통합 위치가 명확해짐 → 3번은 행동 변화 폭이 가장 커서 기준선 확보 후 test scenarios로 전후 비교 → 4번은 계측 데이터가 필요해 마지막.

## 목표 지표

- SKILL.md 326줄 → ~180줄 (역할·경계 / 의도 라우터+always-on gate / Full-Lite / 상태 태그 / 출력 순서만 유지)
- 품질 레이어 2겹: 라우팅은 의도 라우터 하나, 검증은 citation-verification-contract 하나
- tests/scenarios 통과 유지 (프루닝 전후 동작 동등성)

