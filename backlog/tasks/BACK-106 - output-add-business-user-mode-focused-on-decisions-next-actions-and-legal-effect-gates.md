---
id: BACK-106
title: '[Output] Add business_user mode focused on decisions, next actions, and legal-effect gates'
status: To Do
labels:
  - enhancement
  - area:architecture
  - area:patterns
  - area:docs
priority: medium
milestone: 
created_date: '2026-07-02'
---
## Description
Parent epic: #96

## 문제
일반인/창업자/현업 사용자는 Source Grade 메타보다 “지금 무엇을 하면 안 되는지”가 먼저 필요하다.

## 작업
- `business_user` 기본 출력 순서 정의: 한 줄 결론 -> 지금 할 일 -> 하지 말 것 -> 준비 자료 -> 변호사에게 물어볼 질문 -> 근거.
- 고위험 상황 gate 강화: 해고, 형사, 개인정보 유출, 기관 제출, 계약 서명, 고액 과징금.
- 테스트에 비전문가 UX 기대값 추가.

## 완료 기준
- 비전문가에게 확정 행동을 바로 지시하지 않는다.
- 근거는 유지하되 행동 지침이 먼저 보인다.

