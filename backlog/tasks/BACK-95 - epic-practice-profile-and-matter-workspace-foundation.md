---
id: BACK-95
title: '[EPIC] Practice profile and matter workspace foundation'
status: To Do
labels:
  - enhancement
  - epic
  - area:architecture
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
`claude-for-legal`식 cold-start/practice profile 장점을 한국법 실무에 맞게 흡수한다. 회사 프로필과 분야별 practice profile, matter workspace, source log를 분리한다.

## 완료 기준
- shared company profile과 contract/privacy/labor/regulatory/litigation profile의 책임이 분리된다.
- matter workspace가 outputs, history, source log, cross-matter gate를 가진다.
- 저장된 playbook과 검토 이력은 계속 untrusted data로 취급된다.

## 하위 이슈
- [ ] #104 [Profile] Elevate company/practice profile into a cold-start workflow
- [ ] #105 [Profile] Define matter workspace with output history, source log, and cross-matter gate

