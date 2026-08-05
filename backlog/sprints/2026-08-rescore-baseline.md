---
milestone: tests-layer-reaim
status: completed
started: 2026-08-05
due: 2026-08-05
objectives: [O1]
component: "tests"
---

# rescore-baseline

이슈 #294 — 차등 재채점을 산문 규범에서 커밋된 게이트로. 에픽 #277이 실측한 사각지대("코퍼스 앵커는 조임은 막지만 완화는 구조적으로 못 막는다")의 절차적 해법 — 스코어러를 건드리기 전후로 evidence 전량을 재채점해 판정 변화를 대조하는 것 — 을 도구+baseline+CI 게이트로 굽는다.

## Goal

- 스코어러/하네스 판정 로직 변경이 **diff에 드러난다**. 완화든 조임든 baseline 갱신 없이는 그린이 불가능하다 (#282: 게이트 3종 그린 채 완화 30건 통과 사고 방향).
- "판정 변화 0건이면 그 방향이 안전하다"는 증명 구조를 커밋된 도구로 만든다. 어떤 룰이 옳은지는 판단하지 않는다 — "판정이 바뀌었는데 아무도 그걸 선언하지 않았다"만 잡는다.

## Plan

- [x] 재채점 도구 `tests/check_rescore_baseline.py` — evidence의 `source_eval`로 config를 찾아 `score_one_prompt`에 태우고, `{corpus: {prompt_id: [failure message]}}` 결정론 직렬화. 모드: 체크(기본) / `--write-baseline` / `--json`.
- [x] baseline 체크인 `tests/forward_evals/rescore_baseline.json` — 19 corpus, 실패 메시지 38건 (스코어러 안정 타이밍: #293/#296 머지 후).
- [x] 완화/조임 방향 명시 검사 — 메시지 단위 대조, 완화는 조임보다 강한 문구 (#282 사고 방향).
- [x] CI step + unittest(`test_rescore_baseline.py` 7건) + py_compile + README 체크리스트·지도·명령 블록 배선.
- [x] 산문 규범 2곳 포인터 축약 — `forward_eval_harness.py` `active_sentence_hit` docstring, `test_suppression_window_limits.py` 모듈 docstring (single-home: check docstring이 집).
- [x] mutation 실증 2건 + baseline 동반 갱신 그린.

## Mutation evidence

**M1 (완화 방향)** — `mirror_promulgation_currency_gate`의 `currency_scope_markers`에 `"공포일자"` 동의어 추가 (`tests/evaluate_scenario_outputs.py`). v080 o4-08 출력이 "공포일자"를 이미 담고 있어 실패가 사라짐.

- 게이트: `FAIL: 판정 변화 1건 (완화 1건, 조임 0건)` — corpus·prompt·메시지 지목, exit 1. **완화 방향이 조용한 통과로 안 넘어간다.**
- (b) 같은 PR에서 `--write-baseline` → `PASS: 판정 변화 0건` (38→37건). **선언하면 그린.**
- 복원: pristine 사본.

**M2 (조임 방향)** — fwd-02 forbidden에 `"루틴"` needle 추가 (기존 needle 유지, `beopsuny_guardrails.yaml`).

- 게이트: `FAIL: 판정 변화 3건 (완화 0건, 조임 3건)` — v060·v09·v050 corpus fwd-02가 새 실패, exit 1. **조임도 조용히 통과하지 않는다.**
- needle 치환 형태로 바꾸면 같은 diff에 완화 1건이 섞인다(옛 needle 메시지 소실) — 조임만 순수하게 보여주려고 추가 형태로 재작성.
- 복원: pristine 사본.

## Decisions

- **체크 단위는 메시지다** (prompt pass/fail이 아니라) — #282 형태(일부 FAIL 메시지 소실)가 메시지 단위에서 잡힌다. `classify_diffs`가 baseline↔actual을 메시지 집합으로 대조.
- **baseline 파일은 순수 데이터다** (메타데이터·타임스탬프 없음) — `--write-baseline`이 결정론적으로 같은 바이트를 재생성, churn 없음.
- **corpus 키는 evidence 파일 스템** — evidence의 `name` 필드가 아니라 (이름은 바뀔 수 있지만 파일 스템이 체크인 단위).
- **config에 없는 prompt는 마커로 기록** (`<prompt not in current config>`) — 매핑되지 않은 rename이 "채점 불가"로 조용히 사라지지 않게 (PR #261 선례). 현재 19 corpus 전부 resolve.
- **CI step은 PR/push 모두 실행** — 결정론적 정적 게이트라 이벤트 분기 불필요 (#295 changelog gate와 다름).
- **autofix 잡음 대응**: README markdownlint(표 구분선)·harness ruff(import 재정렬)가 매 턴 재발 — 커밋 직전 pristine 복원 + bash 재적용으로 diff를 의도분만 유지 (핸드오프 교훈 재적용).

## What didn't work

- **markdownlint autofix가 README 전역 표 구분선을 패딩** — 편집 도구 호출마다 재발. bash 스크립트로 잡음 훙크만 되돌리는 방식으로 수렴.
- **`완화 1건마다` 문구가 volatile 검사에 걸림** — `\d{1,3}건` 패턴 매치. 한글 수사("완화 한 건마다")로 해소 — README volatile 패턴은 숫자+건 단위 서술 금지.
- **ruff autofix가 `active_sentence_hit` docstring 편집 시 harness 194+/56- 폭주 재발** — pristine + bash 재적용으로 6줄 diff 복원. 편집 도구 사용은 해당 파일에 금지.
