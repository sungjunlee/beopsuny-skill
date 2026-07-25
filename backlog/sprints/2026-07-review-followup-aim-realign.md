---
milestone: review-followup-aim-realign
status: active
started: 2026-07-25
due: TBD
objectives: [O1, O3]
component: "router-loading"
---

# review-followup-aim-realign

에픽 #241 — 2026-07-25 전면 리뷰 후속.

## Goal

정적 검사가 **실제 런타임 표면**을 조준하고(#242 #243), 폐기된 개념·미실행 자산이 레포에서 사라진다(#240 #244) — 게이트 3종 그린을 유지한 채.

## Plan

### Batch 1 — P0 조준점 (검사가 잘못된 대상을 보는 문제)

- [x] #242 [safety] 증거인멸 금지선을 SKILL.md always-on 경계로 승격 + 검사 이동, enforcement-response 도달성, workflow-map 존치 결정 → 3dd473d (closed)
- [x] #243 [tests] freshness `next_review` 경과 검사 추가 + 포맷 결정 + 경과 2건 처리 → bf892a6 (closed)

### Batch 2 — P1 폐기 개념 잔여 청소

- [~] #240 [docs+tests] Full/Lite 잔재 → PR #247 / 117be45 — 문서·spec 층 완료(README·charter·system-map·capabilities·CLAUDE·SKILL·source-access). 잔여: 하네스 id/category + `forward_eval_harness.py` + deprecated Gate Card

### Batch 3 — P2 경량화

- [ ] #244 [tests] scenarios 01–15 삭제/강등/승격 결정 + `forbidden_behavior`/`must_do` 처리 + dead 룰 제거

## Running Context

- **이 스프린트 밖(판단 선행)**: #245 히스토리 표면 8→3, #246 always-on 로딩 예산 + 초벌 spine + 모델 하한 가드. 둘 다 사용자 결정이 선행돼야 실행 가능하므로 Plan에 넣지 않았다.
- **이번 사이클의 주제는 계약 추가가 아니라 기존 검사의 조준점 재검토다.** 리뷰에서 나온 P0 2건이 모두 "검사는 그린인데 경계는 부재/방치" 형태였다. 새 계약을 붙이기 전에 기존 검사가 무엇을 보고 있는지 먼저 확인한다.
- 사용자 방향(2026-07-25): 경량화·핵심 가이드가 북극성. **필요 없어진 것은 삭제로 처리 가능** — 강등·보존을 기본값으로 삼지 않는다.
- 변경 비용 예산(README 품질 계약 체크리스트): 행동 1개 변경 = 필수 표면 4개 이하. #240은 cross-cutting이라 초과 예상 — #236 선례대로 PR에 이유를 남긴다.
- `backlog/tasks/` 스테일 미러 15건(전부 CLOSED)은 2026-07-25에 삭제하고 sync-pull로 재생성했다. GitHub이 유일 정본.

## Progress

- **2026-07-25 (2)** — Batch 1 완료 + Batch 2 문서층 완료. 커밋 3건.
  - `3dd473d` #242 — 증거인멸 경계를 SKILL.md로 승격, 라우팅 원칙 7로 도달성 확보, 검사 조준점 이동 + one-home 회수. mutation 5종(M1–M4 FAIL 탐지 / M5 reword PASS).
  - `bf892a6` #243 — registry 등록이 무기한 면제가 되던 구멍 차단. 경과 시 재검증 또는 **자기만료 예외** 선언 강제. 경과 2건 기한 등록(2026-08-31 / 2026-09-30). mutation 6종. `next_review` 포맷은 **통일하지 않기로** — 14개 중 12개가 월 granularity라 가짜 일자를 만드는 대신 `YYYY-MM` 의미를 policy에 고정.
  - `117be45` #240 — 사용자 결정으로 `Full`도 은퇴. 모드 어휘 완전 제거 + spec 3종 정합. 부수 사실오류(schemas는 미러가 아니라 **영속 파일시스템** 의존) 정정.
  - 결정 기록: **workflow-map.md 존치** — 4개 check(#110/#112 계약 포함)와 결합돼 삭제가 P0의 꼬리가 될 수 없다. 원칙 7로 유일한 runtime 소비가 사라져 이제 명백히 maintainer 문서이므로, 삭제/이동은 재앵커링과 함께 #244에서 한 단위로 처리.
- **2026-07-25** — 전면 리뷰 수행. 에픽 #241 + task #242~#246 등록, #240 스코프 확장(내부 명명 정리 → 개념 잔여 청소, priority:low→medium). `backlog/tasks/` 스테일 미러 15건 삭제 후 sync-pull. `2026-07-concept-alignment-full-first.md` status draft→completed 정정(에픽 #234 실제 완료 반영).
