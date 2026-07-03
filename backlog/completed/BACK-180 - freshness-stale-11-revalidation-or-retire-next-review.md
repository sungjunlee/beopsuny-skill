---
id: BACK-180
title: '[Freshness] 등록 stale 자산 11개 revalidation-or-retire 일괄 패스 — next_review 전부 기한 초과'
status: To Do
labels:
  - area:refactor
  - area:docs
priority: high
milestone:
created_date: '2026-07-03'
---
## Description
## 문제

`references/freshness-governance.md`의 Registered Stale Assets 표 기준, 등록된 stale 자산 11개의 `next_review`가 **전부 기한 초과** 상태다 (2026-01 ~ 2026-05, 오늘 2026-07 기준):

- 체크리스트 9개 (contract_review, fair_trade, food_business, healthcare, investment_due_diligence, labor_hr, privacy_compliance, serious_accident, startup)
- `assets/data/clause_references.yaml`
- `references/international_guide.md`

이 자산들이 계속 `triage_only`로 묶여 있으면 업종별 체크리스트·조항 참조가 스킬의 실질 가치에 기여하지 못한다. #178에서 확립한 retire-first 원칙(Unrouted Asset Rule)과 기존 Retirement Rule로 판단 규칙은 명확해진 상태 — 실행 사이클을 돌릴 시점.

## 작업

자산별로 Maintainer Workflow(freshness-governance.md) 절차에 따라 판정:

1. **revalidate**: volatile 항목(금액·기한·threshold·서식)을 공식 소스로 재검증 → 자산 본문 + `maintenance.next_review` 갱신 → `freshness_revalidation.yaml` 형식 기록 → registry 제거(retire)
2. **partial_refresh**: 일부만 갱신 가능하면 갱신분/잔여 stale 분리, registry 유지 + `retire_when` 좁힘
3. **retire(파일 삭제)**: 로드 경로 대비 유지 가치가 없다고 판단되면 Unrouted Asset Rule 절차로 삭제 (registry 항목 동시 제거)

우선순위: 사용 빈도 높은 것부터 — contract_review, privacy_compliance, labor_hr → 나머지.

## AC

- [ ] 11개 자산 각각에 revalidate / partial_refresh / retire 판정과 근거 기록
- [ ] 판정 결과가 freshness_debt.yaml, Registered Stale Assets 표, 자산 본문에 일관 반영
- [ ] `next_review` 기한 초과 자산 0개
- [ ] O1/O2 테스트 PASS

