# Freshness Governance

법순이의 번들 YAML과 reference 문서의 dated claim은 빠른 triage와 issue spotting을 위한 로컬 지식이다. 현행 법령, 시행령, 고시, 서식, 수수료, 과징금, 신고기한, 인허가 요건, treaty/source count, 단계적 시행일, statutory threshold를 대신하지 않는다.

이 문서는 `references/source-access.md#freshness-gate`와 `references/checklist-routing.md#freshness-routing`의 운영 계약을 보강한다. 자산별 공통 freshness metadata는 `assets/schemas/freshness_metadata.yaml`, 구조화된 stale debt 목록은 `assets/policies/freshness_debt.yaml`을 단일 레지스트리로 삼고, 재검증 기록은 `assets/schemas/freshness_revalidation.yaml`의 evidence shape를 따른다.

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

stale 등록 자산에서 나온 항목이 결론에 들어가려면 먼저 live legal research를 수행한다.

우선순위:

1. law.go.kr 법령·시행령·시행규칙·행정규칙
2. 소관 기관 공식 고시, 예규, 가이드라인, 민원안내
3. 법망 API 또는 로컬 legalize-kr/admrule-kr/ordinance-kr/precedent-kr 원문
4. 공식 원문에 접근할 수 없을 때만 해설/의견 해설을 보조 자료로 사용

확인 실패 시:

- 결론을 유보한다.
- 해당 항목을 `[STALE]` 또는 `[INSUFFICIENT]`로 표시한다.
- 검토자 메모의 `Currency` 또는 `Before relying`에 재확인 필요 범위를 적는다.

## Debt Register Contract

`assets/policies/freshness_debt.yaml`의 각 항목은 아래 필드를 갖는다. `assets/policies/checklists/*.yaml`뿐 아니라 `references/*.md`도 dated volatile claim이 있으면 등록 대상이다.

| 필드 | 의미 |
| --- | --- |
| `path` | stale로 등록된 repo-relative asset path |
| `status` | 현재는 `stale_registered`만 사용 |
| `next_review` | 해당 자산의 `maintenance.next_review`와 일치해야 함 |
| `risk` | outdated일 때 잘못 답할 수 있는 법률 리스크 |
| `allowed_use` | stale 상태에서 허용되는 사용 범위 |
| `verification_required` | 결론 전 확인해야 할 공식 소스 계열 |
| `retire_when` | registry에서 제거할 수 있는 조건 |

새 stale 예외는 테스트 코드에 직접 추가하지 않는다. 먼저 이 registry에 등록하고, `risk`, `allowed_use`, `verification_required`, `retire_when`을 적어야 한다.

각 YAML 자산의 `maintenance`는 `assets/schemas/freshness_metadata.yaml`의 `next_review`, `last_verified`, `source_url`, `freshness_days`, `must_reverify` 필드를 유지한다. `next_review`가 지나거나 `last_verified + freshness_days`가 지난 자산은 현재 날짜 기준 CI에서 보이며, registry에 등록되지 않았으면 실패한다.
`skills/beopsuny/assets/` 하위 YAML은 기본적으로 `maintenance` 대상이다. 예외는 시간이 지나면 틀려지는 사실(조문 번호, 금액, 기한, 요율, 기관 실무, 시행일, 법률 효과)이 없는 순수 구조·설정·판정 정책 자산만 허용한다. 현재 opt-out 범위는 `assets/schemas/*.yaml`, registry 자신인 `assets/policies/freshness_debt.yaml`, 설정 자산인 `assets/policies/knowledge_manifest.yaml`, 법령 사실을 담지 않는 순수 판정 정책인 `assets/policies/review_mode.yaml`과 `assets/policies/source_grades.yaml`이며, 테스트 allowlist는 이 기준을 집행하기 위한 목록일 뿐 단일 소스는 이 문서다.
`partial_refresh`로 일부 값을 갱신한 자산은 `next_review`가 미래여도 residual stale scope가 남아 있으면 registry에 유지한다. 이 경우에도 runtime 사용 범위는 계속 `triage_only`다.

## Revalidation Record

stale 자산을 갱신하거나 registry에서 제거하려면 재검증 기록을 남긴다. 형식은 `assets/schemas/freshness_revalidation.yaml`을 따른다.
첫 smoke record와 fixture는 `tests/fixtures/freshness_revalidations/`에 둔다. 이 fixture는 법률 결론 샘플이 아니라 keep/partial/retire 운영 루프가 깨지지 않도록 하는 계약 테스트 입력이다.

필수로 남길 정보:

- `asset_path` — 갱신한 repo-relative asset path
- `checked_at`, `checked_by`, `tracked_issue`
- `source_families_checked` — law.go.kr, 소관 부처, gov.kr, 기관 고시, 법원 등 확인한 source family
- `official_sources` — title, URL, 출처 권위 라벨, verification status, retrieved_at
- `volatile_items_checked` — deadline, fee, threshold, filing_requirement, form, authority, penalty, document처럼 stale 위험이 큰 항목별 결과
- `asset_update` — 본문 수정 여부와 `maintenance.next_review` 변경 전후
- `retirement_decision` — `keep_registered`, `retire`, `partial_refresh`
- `self_check` — official source 사용, volatile item 검토, next_review 갱신, freshness debt 반영 여부

공식 source 없이 사용자 기억, 오래된 뉴스레터, stale 번들 YAML만으로 `retire` 결정을 내리지 않는다. 일부 항목만 확인했으면 `partial_refresh`로 남기고 `remaining_stale_scope`를 적는다.

## Maintainer Workflow

stale 자산을 만질 때는 아래 순서로 판단한다.

1. `freshness_debt.yaml`에서 대상 asset과 `verification_required`를 확인한다.
2. `assets/schemas/freshness_revalidation.yaml` 형식으로 `source_families_checked`, `official_sources`, `volatile_items_checked`를 먼저 채운다.
3. 공식 source family를 열었지만 개별 금액·기한·threshold를 갱신하지 못했으면 `retirement_decision.decision: "keep_registered"`로 둔다. 이때 `remaining_stale_scope`에 아직 stale인 항목군을 적고, `maintenance.next_review`를 앞당겼다고 표시하지 않는다.
4. 일부 항목만 원문 확인 후 갱신했으면 `partial_refresh`로 둔다. 갱신한 항목과 남은 stale 범위를 분리하고, registry는 유지한다.
5. 모든 volatile 항목을 공식 source로 재검증했고 자산 본문과 `maintenance.next_review`를 갱신했을 때만 `retire`를 검토한다. `retire` 결정은 `freshness_debt_updated: true`와 함께 registry 제거 diff가 있어야 한다.
6. 어떤 결정이든 stale 자산만 보고 현행 의무, 금액, 기한, 과징금, 서식, 인원 기준을 답했다고 쓰면 실패다. `no_current_obligation_from_stale_only: true`를 유지한다.

## Registered Stale Assets

현재 등록된 stale 자산은 issue #101/#102 registry를 기반으로 issue #180에서 부분 갱신했다.

| 자산 | next_review | stale 상태 사용 |
| --- | --- | --- |
| `skills/beopsuny/assets/data/clause_references.yaml` | 2026-10 | 계약 조항 issue-spotting triage only |
| `skills/beopsuny/assets/data/legal_terms.yaml` | 2025-12-07 | 법률용어·번역 issue-spotting triage only |
| `skills/beopsuny/assets/policies/mandatory_provisions.yaml` | 2026-06-24 | 강행규정 후보 issue-spotting triage only |
| `skills/beopsuny/assets/policies/checklists/fair_trade.yaml` | 2026-10 | 공정거래 research question triage only |
| `skills/beopsuny/assets/policies/checklists/food_business.yaml` | 2026-10 | 식품 사업 triage only |
| `skills/beopsuny/assets/policies/checklists/healthcare.yaml` | 2026-10 | 의료·헬스케어 triage only |
| `skills/beopsuny/assets/policies/checklists/labor_hr.yaml` | 2026-10 | 노동·인사 triage only |
| `skills/beopsuny/assets/policies/checklists/privacy_compliance.yaml` | 2026-10 | 개인정보 issue triage only |
| `skills/beopsuny/assets/policies/checklists/serious_accident.yaml` | 2026-10 | 중대재해 issue triage only |
| `skills/beopsuny/assets/policies/checklists/startup.yaml` | 2026-10 | 설립 절차 triage only |
| `skills/beopsuny/references/international_guide.md` | 2026-10-31 | 해외진출 reference triage only |

## Unrouted Asset Rule (retire-first)

registry는 살아 있는 자산의 신선도 부채를 관리하는 곳이지, 죽은 자산의 보관소가 아니다. 여기의 retire는 **파일 삭제**를 뜻한다 — 아래 Retirement Rule의 "registry 제거"(revalidation record 필요)와 다른 절차다.

- 어떤 자산이 SKILL.md 라우터, reference 문서, checklist routing, 시나리오 어디에서도 로드 경로가 없으면(unrouted), registry에 등록하지 말고 삭제한다. 복구는 git 이력으로 충분하다.
- 삭제하는 자산이 이미 registry에 등록돼 있으면 해당 registry 항목도 같은 커밋에서 제거한다. 이 경우 revalidation record 대신 unrouted 근거(참조 그래프 감사 결과)를 커밋 메시지나 이슈에 남기면 된다.
- 로드 경로가 있는데 stale이면 registry에 등록하고 아래 Retirement Rule을 따른다.
- 정기 감사: 시나리오·라우터 기준 참조 그래프에서 unrouted 자산을 찾고, 발견 즉시 삭제하거나 유지 사유를 이슈에 기록한다.

## Retirement Rule

registry에서 제거하려면 아래가 모두 필요하다.

1. 자산 본문 또는 maintainer note에 확인한 공식 source family를 남긴다.
2. YAML 자산은 `maintenance.next_review`, reference 문서는 registry `next_review`를 실제 다음 검토일로 갱신한다.
3. stale 상태였던 금액, 기한, threshold, 구비서류, 고시·가이드라인 항목을 live source 기준으로 재검토한다.
4. `assets/schemas/freshness_revalidation.yaml` 형식의 재검증 기록에 `retirement_decision.decision: "retire"` 또는 `partial_refresh` 근거를 남긴다.
5. `tests/validate_skill_contracts.py`가 registry 제거 후에도 통과해야 한다.

부분 갱신이면 registry에서 제거하지 않는다. 대신 `risk` 또는 `retire_when`을 좁혀 남긴다.
