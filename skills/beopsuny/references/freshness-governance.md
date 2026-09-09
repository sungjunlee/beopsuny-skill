# Freshness Governance

법순이의 번들 YAML과 reference 문서의 dated claim은 빠른 triage와 issue spotting을 위한 로컬 지식이다. 현행 법령, 시행령, 고시, 서식, 수수료, 과징금, 신고기한, 인허가 요건, treaty/source count, 단계적 시행일, statutory threshold를 대신하지 않는다.

stale 자산 처리의 일반 원칙(triage_only, 승격 금지, retirement/revalidation)은 이 문서가 단일 소스다. 미러 공포본·시행일 특수 규칙은 `references/source-access.md#freshness-gate`, 체크리스트 특수 처리는 `references/checklist-routing.md#freshness-routing`을 본다. 공통 freshness metadata는 `assets/schemas/freshness_metadata.yaml`, stale debt 목록은 `assets/policies/freshness_debt.yaml`을 단일 레지스트리로 삼고, 재검증 기록은 `assets/schemas/freshness_revalidation.yaml`의 evidence shape를 따른다.

## Runtime Rule

`assets/policies/freshness_debt.yaml`에 등록된 자산과 reference 문서는 모두 `triage_only`로 취급한다.

답변에서 허용되는 사용:

- 사용자 상황을 좁히기 위한 후보 체크리스트
- 어떤 법령·기관·서식을 확인해야 하는지 찾는 research seed
- 대량 표 검토에서 `needs_review` 후보 셀을 만드는 입력

답변에서 금지되는 사용:

- 등록된 stale 자산의 금액, 기한, 인원 기준, 과징금, 구비서류, 서식 번호를 현행 의무처럼 말하기
- live source 확인 없이 `answered`, `[VERIFIED]`, “현재 확인된 의무”로 승격하기
- 오래된 체크리스트 날짜를 숨기고 일반 법률 결론처럼 출력하기
- reference 문서의 연도 기준 수치, treaty/source count, 금액·비율 threshold, 신고기한을 live 확인 없이 현행 사실처럼 말하기

## Verification Before Answering

stale 등록 자산에서 나온 항목이 결론에 들어가려면 먼저 live legal research를 수행한다. 우선순위: (1) law.go.kr 법령·시행령·시행규칙·행정규칙, (2) 소관 기관 공식 고시·예규·가이드라인·민원안내, (3) 법망 API 또는 로컬 legalize-kr/admrule-kr/ordinance-kr/precedent-kr 원문, (4) 공식 원문에 접근할 수 없을 때만 해설/의견을 보조 자료로 사용.

확인 실패 시 결론을 유보하고, 해당 항목을 `[STALE]` 또는 `[INSUFFICIENT]`로 표시하며, 답변의 관련 위치에 재확인 필요 범위를 적는다.

## Maintainer Workflow

아래는 자산을 수정·재검증·삭제하는 유지보수 때만 읽는다. 일반 법률 답변은 위 Runtime Rule과 Verification Before Answering을 적용하며 운영 기록을 만들 필요가 없다.

- stale 목록과 필드·만료 정의는 `assets/policies/freshness_debt.yaml`이 단일 소스다. 새 stale 예외를 테스트 코드에 직접 추가하지 않는다. `next_review` 또는 `last_verified + freshness_days` 만료를 숨기거나 날짜만 연장하지 않는다. overdue 해소 기한이 지나면 실패하며, 미래로 변경한 날짜에는 실제 재검증 근거가 필요하다.
- `skills/beopsuny/assets/` 하위 YAML은 `assets/schemas/freshness_metadata.yaml`의 `maintenance` 대상이다. opt-out은 시간에 따라 틀려지는 법률 사실이 없는 구조·설정·판정 정책만 허용한다: `assets/schemas/*.yaml`, `assets/policies/freshness_debt.yaml`, `assets/policies/knowledge_manifest.yaml`, `assets/policies/review_mode.yaml`, `assets/policies/source_grades.yaml`. 테스트 allowlist는 집행 목록이다.
- 살아 있는 자산을 갱신하거나 registry에서 제거할 때 `assets/schemas/freshness_revalidation.yaml`로 공식 source, 검토한 volatile 항목, 갱신 전후와 `retirement_decision`을 기록한다. 필드 사본은 이 문서에 두지 않는다. 계약 테스트 입력은 `tests/fixtures/freshness_revalidations/`다.
- `keep_registered`는 확인한 범위만, `partial_refresh`는 `remaining_stale_scope`와 registry 유지를 기록한다. 전부 재검증한 자산만 `retire`를 검토하며 `freshness_debt_updated: true`와 제거 diff가 필요하다. 사용자 기억·오래된 뉴스레터·stale 번들 YAML만으로 `retire`하지 않는다. 일부 갱신 뒤에도 residual stale scope가 남으면 `triage_only`다.

## Unrouted Asset Rule (retire-first)

registry는 살아 있는 자산의 신선도 부채를 관리하는 곳이지, 죽은 자산의 보관소가 아니다. 여기의 retire는 **파일 삭제**를 뜻한다 — 아래 Retirement Rule의 "registry 제거"(revalidation record 필요)와 다른 절차다.

- SKILL.md 라우터, reference 문서, checklist routing, 시나리오 어디에서도 로드 경로가 없는(unrouted) 자산은 registry에 등록하지 말고 삭제한다. 복구는 git 이력으로 충분하다. 이미 registry에 있으면 같은 커밋에서 항목도 제거하고, revalidation record 대신 unrouted 근거(참조 그래프 감사 결과)를 커밋 메시지나 이슈에 남긴다.
- 유일한 소비자가 이미 읽는 공식 소스와 같은 내용을 중복 제공할 뿐인 자산도 소비자 대조 근거와 함께 삭제할 수 있다. 이때 소비자 포인터·registry·해당 자산만 위한 fixture와 검사를 함께 제거하고 법률 재검증으로 보고하지 않는다.
- 가치 있는 로드 경로가 남아 있고 stale이면 registry에 등록하고 아래 Retirement Rule을 따른다.
- 정기 감사: 참조 그래프에서 unrouted 자산을 찾아 즉시 삭제하거나 유지 사유를 이슈에 기록한다.

## Retirement Rule

registry 제거의 경계 — 아래가 모두 필요하다.

1. 자산 본문 또는 maintainer note에 확인한 공식 source family를 남긴다.
2. YAML 자산은 `maintenance.next_review`, reference 문서는 registry `next_review`를 실제 다음 검토일로 갱신한다.
3. stale 상태였던 금액, 기한, threshold, 구비서류, 고시·가이드라인 항목을 live source 기준으로 재검토한다.
4. 재검증 기록에 `retirement_decision.decision: "retire"` 또는 `partial_refresh` 근거를 남긴다.
5. `tests/validate_skill_contracts.py`가 registry 제거 후에도 통과해야 한다.

부분 갱신이면 registry에서 제거하지 않고 `risk` 또는 `retire_when`을 좁혀 남긴다.
