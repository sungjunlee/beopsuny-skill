---
id: BACK-96
title: '[EPIC] Output modes and legal-effect gates for lawyer, legal ops, business users, and external drafts'
status: To Do
labels:
  - enhancement
  - epic
  - area:architecture
  - area:patterns
  - area:docs
priority: medium
milestone: 
created_date: '2026-07-02'
---
## Description
## 배경
최근 법순이 스킬 리뷰에서 도출된 개선 항목입니다. 목표는 현재 장점인 한국법 원문주의, Source Grade, 자가 검증, 단일 라우터 구조를 보존하면서 `claude-for-legal` 수준의 practice-area suite로 점진 진화하는 것입니다.

## 원칙
- 한국법 질문은 기억만으로 답하지 않는다.
- 기능 확장보다 citation/freshness/profile/output 계약을 먼저 강화한다.
- 물리적 multi-plugin 전환은 DOCX/connector/scheduled workflow가 실제로 필요해질 때 판단한다.

## 목표
전문가용, 법무운영용, 비전문가용, 대외송부용 출력의 목적과 gate를 분리한다.

## 완료 기준
- `lawyer`, `legal_ops`, `business_user`, `unknown` 역할별 기본 출력 순서가 다르다.
- 상대방 송부/기관 제출/계약 체결 전 gate가 일관되게 적용된다.
- README와 예시 문구가 “정확한 법률 정보 제공”보다 “확인 가능한 1차 소스 중심 조사 보조”에 맞게 조정된다.

## 하위 이슈
- [ ] #106 [Output] Add business_user mode focused on decisions, next actions, and legal-effect gates
- [ ] #107 [Output] Split internal memo, business summary, and external draft output contracts
- [ ] #108 [Docs] Recalibrate README and examples to investigation-assist posture

