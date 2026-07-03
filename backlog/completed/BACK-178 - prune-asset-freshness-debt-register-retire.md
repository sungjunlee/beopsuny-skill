---
id: BACK-178
title: '[Prune] 시나리오 기반 asset 감사 — freshness debt를 register가 아니라 retire로'
status: To Do
labels:
  - enhancement
  - area:refactor
  - area:docs
priority: low
milestone:
created_date: '2026-07-02'
---
## Description
Part of #174 — 계측 데이터가 필요하므로 마지막 순서

## 문제

assets가 ~9,100줄 YAML (업종별 체크리스트 10개, 강행규정, 조항 분류, 스키마 등). 법률 도메인 특성상 빠르게 낡고, 이를 관리하기 위해 freshness-governance + freshness_debt.yaml이라는 메타 인프라가 또 필요해진 구조 — 복잡성이 복잡성을 낳음.

현재 freshness debt는 **register**(등록) 중심이고 append-only 성향이라, 프루닝 규율 없이는 자라기만 함 (writing-great-skills의 sediment). references/self-verification.md 설계 메모의 append-only 연구 인용 방침도 동일 패턴.

## 작업

1. **계측**: tests/scenarios 실행 시 실제로 로드되는 reference/YAML을 기록하는 간단한 방법 마련 (수동 로그로도 충분)
2. **감사**: 시나리오 전체에서 한 번도 로드되지 않는 asset 목록 도출
3. **retire**: 미사용 asset은 freshness debt register에 등록만 하지 말고 삭제 (git으로 되돌리기 쉬움). 사용되지만 stale한 asset은 revalidation 또는 retire 판단
4. freshness-governance.md에 "register가 아니라 retire가 기본" 원칙 명문화

## AC

- [ ] 시나리오 기준 asset 로드 현황표 존재
- [ ] 미사용 asset이 retire되거나, 유지 사유가 이슈/문서에 기록됨
- [ ] freshness-governance.md에 retire-first 원칙 반영
- [ ] tests/scenarios 통과

