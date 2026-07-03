---
id: BACK-187
title: '[Report] 계약 검토 리포트 템플릿 — destination 변형(internal/business_summary) 소비'
status: To Do
labels:
  - enhancement
  - area:docs
priority: low
milestone:
created_date: '2026-07-03'
---
## Description
Part of #184 — PRD S2, #185 이후 (뒤 이슈와 병렬 가능)

## 작업

계약 검토 결과를 HTML 리포트로 렌더하는 템플릿.

1. `assets/templates/report_contract_review.html`: 횡단 이슈 → 조항별 위험(why_risky / negotiation_points / alt_wording_hint) → 권고 구조. review_mode.yaml의 counter-draft 금지 패턴이 리포트에도 동일 적용
2. destination 규칙 소비 검증이 본 이슈의 핵심: 기본 `internal_legal_memo`(검토자 메모·자가 검증 포함) vs `business_summary` 요청 시(내부 법리 논증 비노출) 두 변형이 같은 템플릿에서 나옴을 확인
3. `references/contract_review_guide.md`에 리포트 옵션 pointer 추가

## AC

- [ ] internal / business_summary 두 destination 변형 산출 확인 (수동 샘플 2개)
- [ ] business_summary 변형에 검토자 메모·자가 검증 블록·미확인 내부 노트 미포함
- [ ] counter-draft 금지 표현("아래 문구로 교체" 등)이 리포트에서도 차단됨을 fixture로 확인
- [ ] self-contained 규격 통과, O1/O2 PASS

