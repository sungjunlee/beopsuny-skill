---
id: BACK-105
title: '[Profile] Define matter workspace with output history, source log, and cross-matter gate'
status: To Do
labels:
  - enhancement
  - area:architecture
  - area:docs
priority: medium
milestone: 
created_date: '2026-07-03'
---
## Description
Parent epic: #95

## 문제
로펌/사내법무급 사용에는 matter별 history, source log, outputs, cross-matter boundary가 필요하다.

## 작업
- matter workspace 최소 구조 정의.
- source-log, review-log, outputs, history 파일의 역할 분리.
- cross-matter context 기본값 off와 예외 절차 명시.

## 완료 기준
- 각 matter가 독립된 source/provenance 기록을 가진다.
- 다른 matter 파일은 명시적 요청 없이 읽지 않는다.

