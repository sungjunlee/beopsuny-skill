---
id: BACK-195
title: '[Report] 리포트 인용에 law.go.kr 공식 링크 슬롯 부재 — 핵심 원칙 2가 리포트 레이어에서 끊김'
status: To Do
labels:
  - bug
  - enhancement
  - area:patterns
  - area:refactor
  - area:docs
priority: medium
milestone:
created_date: '2026-07-04'
---
## Description
## 발견 (2026-07-04 리포트 실사용 smoke test)

sonnet subagent가 스킬 계약을 그대로 따라 NDA 검토 리포트(internal_legal_memo)를 생성한 결과, **인용 10건 전부에 law.go.kr/glaw.scourt.go.kr 링크가 0개**였다. 원인은 실행 오류가 아니라 계약·템플릿 차원의 구멍:

- `references/output-formats.md`의 citation 형식은 **법령 원문** 링크(https://www.law.go.kr/법령/...)를 포함하지만,
- `references/report-deliverable.md`(R1-R5)와 `assets/templates/report_contract_review.html`에는 공식 링크 요구/슬롯이 없다 (템플릿에 law.go.kr 문자열 0회).
- 핵심 원칙 2(공식 링크 필수)가 채팅 출력에는 적용되는데 HTML 리포트에서 끊긴다. 리포트는 self-contained(외부 리소스 금지)지만 `<a href>` 하이퍼링크는 리소스가 아니라 콘텐츠 — R2와 충돌하지 않는다.

## 작업

1. report-deliverable.md R2에 인용 링크 규칙 추가: citation 줄의 조문·판례는 law.go.kr/glaw.scourt.go.kr 링크를 `<a href>`로 포함 (외부 리소스 fetch 아님을 명시)
2. 템플릿 2종(contract_review, bulk_grid)의 citation 영역에 링크 슬롯/예시 추가
3. O1 drift check 갱신

## AC
- [ ] 계약 문서에 리포트 인용 링크 규칙 존재, R2 self-contained 규정과의 관계 명시
- [ ] 템플릿에 링크 슬롯 반영
- [ ] O1/O2 PASS
