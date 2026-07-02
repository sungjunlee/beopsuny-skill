---
id: BACK-104
title: '[Profile] Elevate company/practice profile into a cold-start workflow'
status: To Do
labels:
  - enhancement
  - area:architecture
  - area:docs
priority: medium
milestone: 
created_date: '2026-07-02'
---
## Description
Parent epic: #95

## 문제
현재 memory/profile 구조는 좋지만, `claude-for-legal`식으로 모든 workflow가 practice profile에 의해 일관되게 calibration되는 수준은 아니다.

## 작업
- shared company profile과 분야별 practice profile 구조를 설계한다.
- quick/full cold-start interview를 확장한다.
- seed document에서 stated position과 signed practice 차이를 추출하는 절차를 명시한다.

## 완료 기준
- contract/privacy/labor/regulatory/litigation profile이 같은 company profile을 공유한다.
- profile은 사용자 확인 전 저장되지 않는다.

