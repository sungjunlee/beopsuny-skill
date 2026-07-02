---
id: BACK-107
title: '[Output] Split internal memo, business summary, and external draft output contracts'
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
내부 법무 검토용 메타와 대외 송부용 문안은 섞이면 안 된다.

## 작업
- 내부 법무 메모, 현업 공유 요약, 임원 보고, 상대방 송부용, 기관 제출용 출력 계약을 분리한다.
- 대외 송부/기관 제출 전 검토 gate를 명시한다.
- 자가 검증 블록과 내부 provenance가 외부 문안에 그대로 들어가지 않게 한다.

## 완료 기준
- destination별 출력 스키마가 있다.
- 외부 문안은 내부 검증 메타를 그대로 보내지 않는다.

