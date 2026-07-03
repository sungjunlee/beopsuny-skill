---
id: BACK-185
title: '[Report] report-deliverable 계약 신설 + SKILL.md 시각화 섹션 능력 기반 개정'
status: To Do
labels:
  - enhancement
  - area:architecture
  - area:refactor
priority: medium
milestone:
created_date: '2026-07-03'
---
## Description
Part of #184 — PRD §R1/R2/R3/R5

## 작업

1. `references/report-deliverable.md` 신설:
   - 렌더 레이어 원칙: 리포트는 하나의 destination 계약을 선택해 내용 규칙을 따름 (기본 `internal_legal_memo`)
   - 파일 규격: self-contained HTML 1파일 (인라인 CSS, 외부 리소스 금지), 저장 `${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/reports/{YYYY-MM-DD}-{slug}.html`
   - 하단 고정 블록: 생성일, 읽은 범위, 최신성 한계, 면책 고지 (+내부용이면 자가 검증 블록)
   - 전달 채널 표 (능력 기반): 로컬 파일 / Claude Code Artifact / Chat 탭 Artifacts
2. SKILL.md 시각화 섹션 개정: "Lite 모드나" → 능력 기반 조건 + report-deliverable.md pointer. 새 의도 추가 없음 — 트리거는 사용자 발화("리포트로", "HTML로", "문서로 정리")
3. `docs/desktop-chat-guide.md` 시각화 가이드에 환경 주석 (Mermaid는 Chat 탭 전용임을 명시)

## AC

- [ ] report-deliverable.md에 R1/R2/R3 계약 존재, destination 계약과 non_overrides 참조 연결
- [ ] SKILL.md 시각화 섹션이 능력 기반 문구 + pointer로 개정, 순증 ≤ 5줄
- [ ] O1 static check 추가: 계약 필수 요소(기본 destination, 하단 블록, 외부 리소스 금지) drift 검사
- [ ] O1/O2 PASS, CHANGELOG 갱신

주의: `tests/validate_skill_contracts.py`가 SKILL.md 시각화 섹션 문구를 참조하는지 grep 후 수정 (프루닝 스프린트 교훈).

