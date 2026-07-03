---
id: BACK-186
title: '[Report] bulk_tabular_review grid HTML 템플릿 (values/sources, cell state, 정렬)'
status: To Do
labels:
  - enhancement
priority: medium
milestone:
created_date: '2026-07-03'
---
## Description
Part of #184 — PRD S1, #185 이후

## 작업

`bulk_tabular_review` 결과를 HTML grid 리포트로 렌더하는 템플릿.

1. `assets/templates/report_bulk_grid.html` (또는 유사 위치):
   - values table / sources table 토글
   - cell state 4종(`answered`/`not_present`/`unclear`/`needs_review`) 색상 코딩 — needs_review가 시각적으로 가장 눈에 띄어야 함
   - 클라이언트 사이드 정렬 (인라인 JS, 외부 라이브러리 금지)
   - evidence rule 반영: answered 셀은 quote/location 또는 출처 권위 라벨 hover/expand
2. `references/bulk-tabular-review.md`에 리포트 출력 옵션 1-2줄 + template pointer 추가
3. 하단 고정 블록(읽은 범위·자가 검증·면책)은 #ISSUE1 계약 그대로

## AC

- [ ] 템플릿이 self-contained 규격 통과 (외부 요청 0건 — grep으로 http/https src·href 리소스 검사)
- [ ] cell state가 값 없이도 구분 가능 (색상만이 아니라 라벨 병기 — 접근성)
- [ ] O2 unsafe fixture: 출처 권위 라벨 없는 결론 grid 출력이 FAIL로 잡힘
- [ ] 시나리오 추가 또는 기존 bulk 시나리오에 리포트 분기 반영, O1/O2 PASS

