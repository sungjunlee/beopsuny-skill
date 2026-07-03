---
id: BACK-184
title: '[EPIC] 리포트 산출물 레이어 — self-contained HTML 리포트 (PRD 2026-07)'
status: To Do
labels:
  - enhancement
  - epic
  - area:architecture
priority: high
milestone:
created_date: '2026-07-03'
---
## Description
## 배경

PRD: [`docs/prd/2026-07-report-deliverable.md`](https://github.com/sungjunlee/beopsuny-skill/blob/main/docs/prd/2026-07-report-deliverable.md) (승인 2026-07-03)

검토 결과를 **self-contained HTML 리포트 파일**로 생성하는 렌더 레이어. 핵심 설계:

- **얇은 렌더 계약**: 내용 규칙은 기존 destination 계약(output-formats.md의 5개)을 그대로 소비 — 에픽 #96과 직교, 내용 계약 재정의 없음
- **능력 기반 전달**: 로컬 파일(기본, Claude Code/Codex) → Claude Code Artifact(요청 시, 공유 가정 gate) → Chat 탭 Artifacts(Lite)
- **1규격 3환경**: 인라인 CSS·외부 리소스 금지 HTML 1파일로 로컬/Artifact CSP/Chat 탭 모두 커버
- **비목표**: Mermaid/다이어그램(별도 보류 유지), 자동 발송/공유, 리포트가 대화 답변 대체

채택된 결정: 접근 A(파일 우선), 저장 `~/.beopsuny/reports/`, 기본 destination `internal_legal_memo`, Artifact gate 중간 수위, S1(bulk grid) 우선.

## 서브이슈 (실행 순서)

- [ ] #185 [Report] report-deliverable 계약 + SKILL.md 시각화 섹션 능력 기반 개정
- [ ] #186 [Report] bulk_tabular_review grid HTML 템플릿 (S1)
- [ ] #187 [Report] 계약 검토 리포트 템플릿 (S2)
- [ ] #188 [Report] Artifact 배포 gate (S3)

순서 근거: 1이 계약 기반(나머지의 전제) → 2가 체감 최대 소비자 → 3은 destination 규칙 소비 검증 → 4는 공유 gate라 계약·템플릿 안정 후.

## 가드레일 (전 이슈 공통)

- 프루닝 기준선 유지: 새 의도 0개, SKILL.md 순증 ≤ 5줄, 상세는 reference/template로
- non_overrides: 출처 권위 라벨·verification status·면책 고지는 리포트에서 생략 불가
- 텍스트 응답이 원본, 리포트는 파생물
- README 품질 계약 변경 체크리스트 준수 (각 이슈에 테스트 AC 내장)

