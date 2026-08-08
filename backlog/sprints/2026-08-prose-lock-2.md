# 2026-08 — validator prose-lock 잔존분 2차 이행 (#306)

## 목표

283 1차 슬라이스(#283 PR 본문 분류표)에서 남긴 (c) 문서 산문 핀 37건을 전수 소각한다.

## 이행 대상 (37건 → 15개 check 함수)

| check | (c) 건수 | 이행 방식 |
| --- | --- | --- |
| `check_research_workflow_verification_core` | 6 | 문단 앵커 + 순서 토큰 / 결론 binding 표 구조 |
| `check_report_deliverable_contract` | 9 | R2/R4 표 구조 (행 라벨 + 셀 토큰) |
| `check_source_authority_verified_contract` | 3 | 문단 앵커 + 순서 토큰 (source-grading + output-formats) |
| `check_output_contract_right_sizing` | 2 | 문단 앵커 + 순서 토큰 (SKILL.md) |
| `check_self_verification_guardrails` | 3 | 목록 앵커 + 순서 토큰 (self-verification.md) |
| `check_skill_gate_attachment_and_draft_first` | 3 | 문단 앵커 + 순서 토큰 (SKILL.md) |
| `check_skill_quality_contract_router_map` | 2 | 문단 앵커 + 순서 토큰 (SKILL.md) |
| `check_litigation_element_fact_template` | 3 | 표 셀 / 목록 앵커 + 순서 토큰 |
| `check_bulk_tabular_review_reference` | 3 | 문단 앵커 + 순서 토큰 (bulk-tabular-review.md) |
| `check_law_change_automation_promise_drift` | 3 | 문단 앵커 + 순서 토큰 (law-change-detection.md) |
| `check_current_law_verified_binding_excludes_unconfirmed_practice_material` | 1 | 목록 앵커 + 순서 토큰 (SKILL.md) |
| `check_static_privacy_preknowledge_boundaries` | 3 | 문단 앵커 + 순서 토큰 (SKILL.md) |
| `check_output_role_destination_contracts` | 2 | 문단 앵커 + 순서 토큰 (output-formats.md) |
| `check_international_index_routing` | 2 | 도입 문단 앵커 + 토큰 (international_guide.md) |
| `check_readme_investigation_assist_posture` | 1 | 도입 문단 앵커 + 순서 토큰 (README.md) |
| **합계** | **46** | #283 이행 9건 제외, #306에서 37건 |

## 이행 원칙 (#283과 동일)

- 문장 전체 대신 핵심 토큰 2~3개 동시 존재 / `assert_ordered_tokens` 순서 / 표 구조 검사
- 문단 스코프를 앵커로 좁혀 전역 토큰 #262 함정을 피한다
- 각 이행마다 mutation 증명: "이 검사가 막으려던 drift"를 문서에 주입해 FAIL 확인 + 의미 보존 다듬기 PASS 확인
- 출력 리터럴(출처 라벨·provenance 문구)은 (a)로 유지 — 건드리지 않는다

## 발견한 기존 결함 (이행 중 수정)

- **`| 항목 | 계약 |` 헤더 중복** — report-deliverable.md에서 적용 범위 표(L7)와 R4 표(L79)가 같은 헤더를 써서 `parse_markdown_table`이 앞 표를 잡았다. R4 섹션으로 스코프를 좁혀 해결.
- **한글 음절 합성 함정 (2건)** — "올린다"(올리+ㄴ)에서 어간 "올리"가 substring이 아님(리 U+B9AC vs 린 U+B9B0). "애매하면 `full`로 올린다"는 방향 토큰 "`full`로"로, "아니라→아닌" 다듬기는 "router intent가 아"로 해결. 같은 함정은 "낮춘다/낮춥니다", "생성한다/생성합니다", "보고한다/보고합니다"에서도 발생해 어근 토큰 또는 OR 정규식으로 완화.

## Mutation 증명 요약

| check | mutation 수 | 결과 |
| --- | --- | --- |
| research_workflow_verification_core | 15 | 15/15 의도대로 |
| report_deliverable_contract | 9 | 9/9 |
| source_authority_verified_contract | 6 | 6/6 |
| output_contract_right_sizing | 5 | 5/5 |
| self_verification_guardrails | 6 | 6/6 |
| skill_gate_attachment_and_draft_first | 8 | 8/8 |
| skill_quality_contract_router_map | 4 | 4/4 |
| litigation_element_fact_template | 6 | 6/6 |
| bulk_tabular_review_reference | 6 | 6/6 |
| law_change_automation_promise_drift | 8 | 8/8 |
| current_law_verified_binding | 2 | 2/2 |
| static_privacy_preknowledge_boundaries | 4 | 4/4 |
| output_role_destination_contracts | 4 | 4/4 |
| international_index_routing | 4 | 4/4 |
| readme_investigation_assist_posture | 2 | 2/2 |

대표 mutation (PR 본문에도 기재):

- 완화 방향 반전: "gate를 완화하지 않는다" → "완화할 수 있다" FAIL
- 조임 방향 반전: "애매하면 `full`로 올린다" → "애매하면 `light`로" FAIL
- 의미 보존 다듬기: "출력하지 않는다" → "출력하지 않습니다" PASS

## 게이트

- validate_skill_contracts.py: PASS
- evaluate_scenario_outputs.py: PASS 11 outputs, 14 unsafe fixtures
- check_rescore_baseline.py: PASS — 판정 변화 0건 (스코어러/하네스 미접촉이라 baseline 무변화가 기대)
- unittest: 113 OK
- `git diff --check`: clean

## 산출물

- `tests/validate_skill_contracts.py` — 15개 check 함수 (c) 핀 → 토큰/구조
- `CHANGELOG.md` — #306 항목 (Fixed)
- 문서 파일 변경 없음 (검사만 바뀜 — 문서가 이미 새 토큰을 충족)
