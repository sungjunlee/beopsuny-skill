---
id: BACK-109
title: '[Suite] Document virtual workflow map before any physical plugin split'
status: To Do
labels:
  - enhancement
  - area:architecture
priority: medium
milestone: 
created_date: '2026-07-03'
---
## Description
Parent epic: #97

## 문제
`claude-for-legal`식 suite로 가더라도 한국법 라우팅 안정성을 위해 당장은 단일 스킬의 장점을 유지해야 한다.

## 작업
- commercial, privacy, labor, regulatory, litigation, startup, cross-border workflow map 작성.
- 각 workflow의 trigger, required references, output mode, verification requirements 정의.
- 물리적 split trigger를 DESIGN.md와 정렬한다.

## 완료 기준
- 단일 beopsuny 안에서 named workflow처럼 읽히는 map이 있다.
- plugin split 전/후 경계가 명확하다.

