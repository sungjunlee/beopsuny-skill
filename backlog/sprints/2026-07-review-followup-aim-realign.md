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

- [x] #240 [docs+tests] Full/Lite 잔재 — 문서·spec 층(117be45) + 코드·하네스 층(Batch 4) 전량 완료 → PR #247 (open)

### Batch 2c — PR #247 리뷰 대응 (P0 계열)

- [x] codex P2 3건 — 만료 정의 단일화(C1) + 재검증 근거 강제(C2) + README schemas 범위 정정(C3) → 35b9914

### Batch 3 — P2 경량화

- [x] #244 [tests] scenarios 01–15 삭제(123,228 bytes) + `must_do`/`forbidden_behavior` 은퇴 + dead 룰 재조준 → fe77507

### Batch 4 — P1 잔여 (Batch 3의 어휘 기준 확정 후)

- [x] #240 [tests] o4 id/`guardrail_category` rename(히스토리 무손상 alias) + 스코어링 토큰 이동 + Gate Card rename + dogfood 문서 삭제 → 4219470, a786b20

### Batch 5 — 방향 (사용자 결정 반영)

- [x] #246 [direction] gate 부착 tier(784 → 339줄) + `초벌` spine 승격 + spec/charter 정합 → 5c0b5ee
- [ ] #248 [tests] workflow-map.md 은퇴 판단 + 4-check 재앵커링 — #244에서 분리. 순수 제거가 아니라 재앵커링이라 난이도가 다르다
- [ ] #249 [research] 모델 하한 런타임 가드 실현 가능성 — #246에서 분리. 스킬이 자기 모델을 신뢰성 있게 식별할 수 없다

## Running Context

- **#245는 이 스프린트 밖**: CHANGELOG 비대화 해소가 핵심인데 이 에픽이 계속 CHANGELOG를 쓰고 있어 동시 진행하면 churn이다. epic 마감 후.
- **이번 사이클의 주제는 계약 추가가 아니라 기존 검사의 조준점 재검토다.** 리뷰에서 나온 P0 2건이 모두 "검사는 그린인데 경계는 부재/방치" 형태였다. 새 계약을 붙이기 전에 기존 검사가 무엇을 보고 있는지 먼저 확인한다.
- 사용자 방향(2026-07-25): 경량화·핵심 가이드가 북극성. **필요 없어진 것은 삭제로 처리 가능** — 강등·보존을 기본값으로 삼지 않는다.
- 변경 비용 예산(README 품질 계약 체크리스트): 행동 1개 변경 = 필수 표면 4개 이하. #240은 cross-cutting이라 초과 예상 — #236 선례대로 PR에 이유를 남긴다.
- `backlog/tasks/` 스테일 미러 15건(전부 CLOSED)은 2026-07-25에 삭제하고 sync-pull로 재생성했다. GitHub이 유일 정본.

## Progress

- **2026-07-25 (6)** — #248 workflow-map 은퇴. **결정: 이동이 아니라 삭제.**
  - 근거: (a) 런타임 소비자 0 — `SKILL.md`·gate 표·의도 표·다른 reference 어디에도 로딩 포인터가 없고 forward-eval `source_references`에도 없다. (b) `spec/`·`docs/` 이동은 **두 번째 집을 만든다** — 의도→reference 매핑은 이미 `SKILL.md` 의도 표가, workflow별 verification 요구는 gate 표·`source-grading.md`가 소유하므로 map은 수동 동기화가 필요한 사본이었다. (c) 유지 비용은 CI check 4개 + 전문 1줄 prose-lock.
  - 4-check 처리: `check_workflow_map_structure` **함수 삭제**(SKILL 의도 집합 동등성은 `check_enforcement_response_workflow`에 이미 중복 존재 → 실질 승계, 라벨 비승격 guard는 `assert_not_router_intent()`로 이전) / `check_litigation_element_fact_template` **블록 제거 + #110 재앵커링**(`research-workflow.md` 분쟁 판단 구조 토큰 + 의도 표 구조) / `check_enforcement_response_workflow` **블록만 제거**(#242가 이미 `SKILL.md` 도달성 assert) / `check_cross_border_overlay_roadmap` **전문 1줄 assert 제거 + #112 재앵커링**(`SKILL.md` 라우팅 원칙 4 토큰 + 부정형 shape + 의도 표 구조).
  - 재퇴적 방지: `check_retired_meta_surfaces_stay_retired`를 `RETIRED_SURFACES` 표로 일반화(TODOS.md + workflow-map.md).
  - mutation 8종(W1~W6 FAIL 탐지 / W7·W8 의미보존 reword PASS). SKILL.md 268줄 무변경.
- **2026-07-25 (5)** — PR #247 squash 머지(`fbe0b06`) 후 #246 착수. 커밋 1건 + 후속.
  - `5c0b5ee` #246 — gate 부착이 라우팅이 아니라 **답변이 실제로 만드는 것**을 따르도록. 단순 조문 확인 784 → 339줄.
  - **원인은 gate 표가 아니라 표 밖 서술이었다.** 각 gate의 `적용 범위`는 이미 좁혀져 있었는데 표 위 문장("단순 조문·링크 확인도 … gate를 적용")과 `## 응답 품질 게이트` 절이 **두 곳에서 표를 덮어쓰고** 있었다. 라우팅 원칙 1은 workflow reference만 관장한다고 명시돼 gate에 닿지 않았다.
  - `초벌`은 결정이 아니라 결함이었다 — charter Decision 2026-07-24의 기본 산출물이 `SKILL.md`에 **0건**. #242와 같은 형태로 spine 승격.
  - spec 정합 필수: `capabilities.md` router-loading Expected Behavior가 옛 semantics를 규정하고 있어 안 고치면 **truth 문서가 시스템을 틀리게 기술**한다(#240의 `system-map.md`와 같은 형태). Hard Constraint를 "부착 조건 명시 가능, 경계 완화 불가"로 조이고 charter Decisions 2026-07-25 행 추가.
  - mutation 7종(G1~G5·G7 FAIL / G6 의미보존 PASS).
- **2026-07-25 (4)** — Batch 4(#240 잔여) 완료. 커밋 3건.
  - `4219470` #240 위임분 — o4 id/category rename + 스코어링 토큰 이동 + Gate Card rename. **히스토리 무손상**: evidence corpus 5건이 옛 id로 기록돼 있어 재작성 대신 `RENAMED_PROMPT_IDS` 정규화를 넣고 5건 전량 재채점 8/8 확인.
  - `a786b20` — **위임 검증 중 신규 결함 발견**. 다른 변형으로 mutation을 재현하다(X4: config에서만 옛 카테고리로 되돌리기) `PASS 8/8`이 나오는 것을 봤다. 스코어링이 `CATEGORY_*.get(category, [])`라 미등록 카테고리는 룰 0개 = 무조건 통과였다. 등록 여부를 하드 실패로 전환 + 회귀 테스트 3종. **이번 에픽의 "검사 조준점" 패턴이 하네스 층에서 재발한 사례.**
  - `docs/desktop-chat-dogfood.md` 삭제 — deprecated인데 PASS 기준이 폐기 어휘("Lite 모드라고 밝히고")라 정상 스킬이 FAIL 판정을 받는 상태였고, 참조처 0건이라 고쳐 유지할 근거가 없었다.
  - mutation 독립 재현 4종(X2 정반대 행동 미크레딧 / X3 alias 무력화 시 히스토리 재채점 붕괴 / X4 미등록 카테고리 / X4b 오타). 최초 X3 변형은 `{} or {...}`가 파이썬에서 no-op이라 잘못 통과했고, 항등함수 치환으로 다시 확인했다.
  - **#246 사용자 결정**: 로딩 예산은 light tier gate 부분집합, 모델 하한은 별도 이슈로 실현 가능성부터.
- **2026-07-25 (3)** — PR #247 리뷰 대응 + Batch 3 완료. 커밋 3건.
  - `35b9914` codex P2 3건 — **#243이 막은 구멍이 축 하나에만 적용돼 있었다**. 만료 축은 둘(`next_review`, `last_verified + freshness_days`)인데 registry 검사는 앞 축만 봤고, 등록 자산은 다른 검사에서 면제되므로 뒤 축이 무검사였다. 실측상 잠복이 아니라 2026-10-01에 4건이 동시에 빠지는 31일 사각지대. `asset_expiry_reasons()`로 정의를 단일화해 **갈라질 수 있는 구조 자체를 제거**. 함께 `revalidation_record_required`가 문서로만 존재하던 것(날짜만 밀면 근거 없이 부채 소멸)을 계약으로 고정. mutation 6종.
  - `fe77507` #244 — scenarios 01–15 삭제(123,228 bytes) + `must_do`/`forbidden_behavior` 109줄 은퇴 + dead 룰 재조준(unsafe fixture 18→19).
  - #248 신설 — workflow-map 은퇴는 재앵커링 작업이라 #244(순수 제거)와 난이도가 달라 분리.
  - **위임 검증 방식**: #240 subagent가 `tests/forward_eval_harness.py`를 동시 편집 중이라 unittest 8건이 빨간 상태였다. worktree에 HEAD + 내 변경만 격리해 4게이트 그린(28 OK, fwd 11/11)을 확인하고 인과를 분리했다 — 병렬 작업 중에는 `git stash`/`git checkout`을 쓰지 않는다.
- **2026-07-25 (2)** — Batch 1 완료 + Batch 2 문서층 완료. 커밋 3건.
  - `3dd473d` #242 — 증거인멸 경계를 SKILL.md로 승격, 라우팅 원칙 7로 도달성 확보, 검사 조준점 이동 + one-home 회수. mutation 5종(M1–M4 FAIL 탐지 / M5 reword PASS).
  - `bf892a6` #243 — registry 등록이 무기한 면제가 되던 구멍 차단. 경과 시 재검증 또는 **자기만료 예외** 선언 강제. 경과 2건 기한 등록(2026-08-31 / 2026-09-30). mutation 6종. `next_review` 포맷은 **통일하지 않기로** — 14개 중 12개가 월 granularity라 가짜 일자를 만드는 대신 `YYYY-MM` 의미를 policy에 고정.
  - `117be45` #240 — 사용자 결정으로 `Full`도 은퇴. 모드 어휘 완전 제거 + spec 3종 정합. 부수 사실오류(schemas는 미러가 아니라 **영속 파일시스템** 의존) 정정.
  - 결정 기록: **workflow-map.md 존치** — 4개 check(#110/#112 계약 포함)와 결합돼 삭제가 P0의 꼬리가 될 수 없다. 원칙 7로 유일한 runtime 소비가 사라져 이제 명백히 maintainer 문서이므로, 삭제/이동은 재앵커링과 함께 #244에서 한 단위로 처리.
- **2026-07-25** — 전면 리뷰 수행. 에픽 #241 + task #242~#246 등록, #240 스코프 확장(내부 명명 정리 → 개념 잔여 청소, priority:low→medium). `backlog/tasks/` 스테일 미러 15건 삭제 후 sync-pull. `2026-07-concept-alignment-full-first.md` status draft→completed 정정(에픽 #234 실제 완료 반영).
