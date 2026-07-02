---
id: BACK-97
title: '[EPIC] Korean legal workflow suite roadmap before physical multi-plugin split'
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
단일 `beopsuny` 스킬의 장점을 유지하면서, 내부적으로 commercial/privacy/labor/regulatory/litigation/startup/cross-border workflow pack을 named workflow처럼 정리한다.

## 완료 기준
- 물리적 plugin split 전에 virtual workflow map이 문서화된다.
- 각 workflow의 진입 조건, 읽을 reference, output mode, Source Grade 요구가 명확하다.
- 한국회사에서 자주 참조하는 해외법 overlay는 한국법 workflow의 보조축으로 시작한다.

## 하위 이슈
- [ ] #109 [Suite] Document virtual workflow map before any physical plugin split
- [ ] #110 [Suite] Add court-style element/fact analysis template for disputes and case law
- [ ] #111 [Suite] Add enforcement/criminal response workflow for investigation and regulatory incident scenarios
- [ ] #112 [Suite] Define Korea-company cross-border legal overlay roadmap

