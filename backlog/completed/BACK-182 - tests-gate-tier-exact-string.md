---
id: BACK-182
title: '[Tests] gate 표·tier 표의 exact-string 검사를 구조 검사로 전환'
status: To Do
labels:
  - enhancement
  - area:refactor
priority: medium
milestone:
created_date: '2026-07-03'
---
## Description
## 문제

`tests/validate_skill_contracts.py`가 SKILL.md·references의 정확한 한국어 문장 수십 개에 `assert_contains`로 결합돼 있다. 프루닝 스프린트(#174)에서 문서 한 줄 수정마다 테스트 문자열 짝 수정이 필요했고, PR #179 리뷰도 이를 altitude 문제로 지적했다:

- 무해한 리워딩(동의어, 표 헤더 문구)에 CI가 깨짐 — 문서 개선 비용을 올림
- 반대로 exact-string은 구조를 검증하지 않음 — 헤더 문구만 맞으면 행이 빠진 표도 통과

## 작업

전면 전환이 아니라 **구조가 있는 두 표**부터 파싱 기반 검사로 전환:

1. SKILL.md 의도 라우터 gate 표: markdown 표 파싱 → 행 수(5), 각 행의 gate 이름, `필수 reference` 셀의 파일 경로 존재 검증 (ALWAYS_ON_LEGAL_GATES와 대조)
2. research-workflow.md 2단 트리거 표: 행 2개(light/full), light 행에 ledger 필드 열거 존재, full 행에 6단계 core 언급 검증
3. 위 표를 커버하던 exact-string assert는 구조 검사로 대체하고, 규범 문장(계약 충돌 우선순위 등) assert만 유지
4. 표 파서는 기존 파일 내 유틸로 (새 의존성 금지)

## AC

- [ ] gate 표·tier 표의 문구 리워딩(의미 불변)이 CI를 깨지 않음
- [ ] 행 누락·ref 경로 오타는 CI가 잡음 (mutation 확인: 행 하나 지우고 FAIL 확인)
- [ ] 대체된 exact-string assert 수와 잔존 사유 기록
- [ ] O1/O2 PASS

