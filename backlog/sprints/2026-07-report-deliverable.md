---
milestone: report-deliverable
status: completed
started: 2026-07-03
due: TBD
objectives: [O1, O2, O3]
component: ""
---

# report-deliverable

에픽 #184 — 리포트 산출물 레이어(self-contained HTML). PRD: `docs/prd/2026-07-report-deliverable.md`.

## Goal

사용자가 bulk 검토·계약 검토 결과를 self-contained HTML 리포트(로컬 파일 기본, Artifact는 gate 통과 시)로 받을 수 있고, 리포트는 기존 destination 계약을 소비하는 얇은 렌더 레이어로 남으며 O1/O2 게이트가 계속 PASS한다.

## Plan

Batch 1 — 계약 기반 (의존성 뿌리):
- [x] #185 report-deliverable 계약 신설 + SKILL.md 시각화 섹션 능력 기반 개정 (M, ~2h) → PR #189 (merged)

Batch 2 — 첫 템플릿 (S1, D5 우선순위):
- [x] #186 bulk_tabular_review grid HTML 템플릿 — values/sources, cell state, 정렬 (M, ~2h, depends #185) → PR #190 (merged)

Batch 3 — 병렬 가능 (둘 다 #185 계약만 의존):
- [x] #187 계약 검토 리포트 템플릿 — destination 변형(internal/business_summary) 소비 (S, ~1.5h, depends #185) → PR #191 (merged)
- [x] #188 Artifact 배포 gate — 공유 가정 구성 강제 + unsafe fixture (S, ~1.5h, depends #185) → PR #192 (merged)

Batch 4 — 마감:
- [x] 에픽 #184 체크리스트/가드레일 최종 검증 (SKILL.md 순증 ≤ 5줄, 새 의도 0개) + CHANGELOG + 에픽 close → 완료 보고 코멘트 후 close

## Running Context

- **에픽 가드레일** (#184 본문): 새 의도 0개, SKILL.md 순증 ≤ 5줄, non_overrides 유지, Mermaid 계속 보류. 상세는 reference/템플릿(`assets/templates/`)으로 내린다.
- **component 빈 값 사유**: 리포트 레이어는 `source-citation` capability의 out-of-scope("답변 레이아웃은 output-role-destination 소관")에 해당하나 해당 capability가 아직 `spec/capabilities.md`에 없다. 스프린트 중 필요해지면 spec-grill로 신설 검토.
- **테스트↔문서 강결합** (_context.md 참조): 문서 문구 수정 전 `tests/validate_skill_contracts.py`의 check 함수 grep 필수. 게이트: `PYTHONPATH=.test-deps python3 tests/validate_skill_contracts.py`(O1) + `tests/evaluate_scenario_outputs.py`(O2, 기대 "PASS 10 outputs, 9 unsafe fixtures" — fixture 추가 시 수치 갱신).
- **PRD 채택 결정**: D1 접근 A(파일 우선), D2 `${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/reports/{YYYY-MM-DD}-{slug}.html`, D3 기본 destination internal_legal_memo, D4 Artifact gate 중간 수위, D5 S1(bulk grid) 우선.
- **self-contained 제약**: 인라인 CSS만, 외부 리소스 0 (Artifact CSP 대비). 고정 footer 블록(provenance/한계 고지) 필수.
- **O2 기대 수치 변동**: #186부터 unsafe fixture 10개 ("PASS 10 outputs, 10 unsafe fixtures"). #188에서 또 늘어날 예정 — 이후 이슈의 게이트 확인 시 최신 수치 기준.
- **템플릿 위치 확정**: `skills/beopsuny/assets/templates/report_bulk_grid.html` (#186). #187 템플릿도 같은 디렉토리에.

## Progress

- 2026-07-03: 스프린트 생성. 에픽 #184의 서브이슈 #185-188을 4개 배치로 편성 (185 → 186 → 187∥188 → 마감). 구현은 relay로 위임 예정.
- 2026-07-03 18:07: 스프린트 완료. #188 → PR #192 round 1 LGTM → merge. 가드레일 최종 검증: SKILL.md 303줄(순증 0), 새 의도 0, O1 PASS, O2 PASS 10 outputs/12 unsafe fixtures. 에픽 #184 완료 보고 후 close. 전 과정 relay 위임(dispatch codex + review codex), 총 PR 4개(#189-192), 리뷰 라운드 합계 7회.
- 2026-07-03 17:53: #187 relay dispatch(codex) → PR #191 → round 1 changes_requested(PR 본문 샘플 evidence 누락) → 오케스트레이터가 샘플 독립 재검증+PR 본문 보강(same-head recovery) → round 2 LGTM → 봇 P2(템플릿 주석의 counter-draft 리터럴이 생성 리포트에 잔류) 수정 + static check를 부재 검증으로 반전 → round 3 LGTM → squash merge. O2 unsafe fixture 11개.
- 2026-07-03 17:31: #186 relay dispatch(codex) → PR #190 → 리뷰 round 1 LGTM, 봇 지적 0건 → squash merge. 템플릿 665줄, O2 unsafe fixture 10개로 증가.
- 2026-07-03 17:17: #185 relay dispatch(codex) → PR #189 → 리뷰 round 1 LGTM → 봇 리뷰 4건(이스케이프 계약 추가, 로컬 파일 채널 능력 gate, data URI 문구 정합, 시각화 섹션 EOF 정규식) 오케스트레이터가 수정 → round 2 LGTM → squash merge. references/report-deliverable.md 계약 확립.
