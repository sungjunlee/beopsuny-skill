---
id: BACK-47
title: '[v0.4.0] 갈래 1 — DOCX 처리형 조사 + 설계'
status: To Do
labels: []
priority: medium
milestone: v0.4.0 — DOCX / Candidate topics
created_date: '2026-07-02'
---
## Description
## 배경
v0.3.0 에서 갈래 2 (housekeeping) + 갈래 3 (정책 확장 ①~④) 를 consolidate. 갈래 1 (DOCX 처리형) 은 v0.3.0 scope 외로 이월.

## 스코프 (TBD)
실제 계약서 .docx 파일을 다루는 기능:
- [ ] .docx 파싱 방법 조사 (Claude native / python-docx / 기타)
- [ ] 트랙 변경 (track changes) 표시 방식 조사
- [ ] redlining 출력 포맷 설계
- [ ] 법순이 철학과의 정합 — "수정안 자동 생성 금지" 원칙 하에서 redlining 은 hint 수준 유지 가능한지
- [ ] scenario 설계 (실제 .docx 파일 테스트)

## 의존성
- SKILL.md ≤ 800 경계 — 신규 섹션은 references/ 분리 검토 필요
- Push 설계 금지 원칙 유지
- 새 태그 도입 금지 — 기존 6개 태그 + Grade A/B/C/D 만

## Non-goals
- 본 이슈는 **조사 + 설계 단계** — 실구현은 하위 이슈로 분리
- 계약 자동 수정안 생성은 여전히 금지 (법순이 핵심 원칙)

## 참고
- v0.3.0 릴리즈: https://github.com/sungjunlee/beopsuny-skill/releases/tag/v0.3.0
- CEO/Eng review (주제 결정 후)
