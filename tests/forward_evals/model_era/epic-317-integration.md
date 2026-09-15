# 에픽 #317 통합 기록 — 검토용 완성 초벌과 유연한 출력 계약 정렬

2026-09-15. 에픽 #317의 완료 조건(하위 이슈 AC·증거 대조와 채택·유보·기각 및 미측정 범위 기록)에 따라 오케스트레이터 통합 판정을 기록한다. 이 기록 자체는 구현 완료나 법률 정답 인증이 아니며, runtime 증거·재현 조건은 같은 디렉터리의 `integration-report.md`, `followup-plan.md`, `evidence/`를 따른다. 2026-09-12 사용자 정정(변호사 업무 지원 목적, 가족 일반 사용·피벗 트랙 #341 철회)을 반영했다.

## 채택

- #318 — 근거 중심 초벌과 사용자 권한의 제품 계약 정렬: `spec/charter.md` 목표 계약, draft-first 산출물, 회사 맥락 저장 경계, role/destination gate. 정적 계약 검사(O1)와 시나리오 게이트(O2)로 고정돼 있다.
- #323 (정적 계약 범위) — 수정 조항 요청에 대한 검토용 완성 초안·수정 제안 계약: 합성 fixture `router-19`(`complete_clause_draft`)와 `contract_counter_draft_boundary`의 hash-bound 의미 수신처(PASS 1건 / FAIL 3건 대조, 미검토 출력은 REVIEW_REQUIRED)로 출력 모양과 실패 형태를 고정했다. hint-only·무조건 full·고정 형식·중복 면책 제약의 제거/축소와 그 회귀 가드를 포함한다.
- #317 M1 — 완성 초안(결론·초벌)에 Output contract gate를 붙이는 라우터 배선: SKILL.md 계약 검토 포인터, router-19 `always_apply_gates`와 `output-formats.md` 로딩, `check_counter_draft_output_contract_wiring`. 법적 조항 실체를 새로 만들지 않는다.
- #272 — 출처 권위 라벨 교정 3형식(표·산문·각주)의 유한 검증: `router-16` 의미 fixture가 형식과 무관한 근거 대응 존재/누락 대조를 고정한다.
- 구조 정리(자가검증·review mode·출처 상태표 중복 제거) — 정본 단일화 범위만 채택하며, 라이브 출력 회귀의 해결 근거로는 채택하지 않았다.

## 유보·기각

- 유보(OPEN) — #323 AC5 실제 모델 사실 경계 회귀: 미제공 별첨의 부존재 단정, 미확인 회사 사실 승격, 법정 요건과 계약상 수단의 혼동이 고정 계약 라이브 실행(Opus5 high, 입력 구성 보완 포함)에서 반복 관측됐다. 후보 runtime 수정(B1/B2, binding, selfverify, review-mode, Fable 후보)은 모두 독립/root FAIL로 기각·되돌림했고, 릴리즈 게이트는 미충족이다.
- 기각 — 지식 추가가 모델 출력 문제를 자동 해결한다는 가정: knowledge #79로 장기 지식 축적·컴파일 과제와 연결하되, 이 에픽의 출력 회귀 해결 근거로 쓰지 않는다.
- 기각(철회) — 가족 일반 사용·피벗 트랙 #341: 2026-09-12 사용자 정정으로 철회됐으며 #323의 변경됐던 AC5는 원문으로 복원했다.
- 유보 — 자동 judge 점수는 사람 검토 보조로만 조건부 사용하며 자동 법률 합격 게이트로 채택하지 않는다. #325 privacy hints-first는 후보 NO_GO(작은 비교 완료 판단)로 runtime 순서를 바꾸지 않았다.

## 미측정 범위

- 후보 되돌림 후 현행 runtime의 라이브 모델 재실행 — 고정 계약 실패 대조군은 보존됐으나 현행본의 새 출력 판정은 미측정이다.
- 반복·holdout 확대 — 사전등록대로 실행하지 않았다. 개발 사례 재실행은 holdout을 대체하지 않는다.
- 비용·편집 부담 감소 효과 — Astra profile은 INCONCLUSIVE, #325 타이밍 인과효과도 INCONCLUSIVE다.
- 전문가(사람) 법률 검토 — 모델 판정·정적 검사·의미 fixture는 expert gold가 아니며 provisional이다.
- fwd-11 원본의 직접 변형 독립 리뷰 — timeout으로 미판정 기록이 남아 있으며 유한 검증 범위와 별개다.

## 상태

- #323 AC5 미완료이므로 에픽 #317은 OPEN으로 남는다. milestone 8과 릴리즈(v0.9.0)는 미완료이며 버전은 0.8.0(draft)을 유지한다.
- 이 기록은 새 merge/release/배포·개인 설치본·private 지식 자산·최신성 기한을 변경하지 않는다.
- 정적 게이트(unit/O1/O2/rescore) PASS 기록은 증거 commit(`344ad48`, `747a2ad`) 기준이며 실제 출력의 의미 판정과 별개다. 이 기록과 함께 추가된 정적 검사의 재검증은 통합 PR 게이트가 담당한다.
