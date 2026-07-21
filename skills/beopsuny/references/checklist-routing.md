# 컴플라이언스 체크리스트 라우팅

체크리스트는 사용자의 상황을 빠르게 좁힌 뒤 관련 항목만 뽑기 위한 진입점이다. 체크리스트 자체가 결론 근거는 아니며, 각 항목의 법령은 live legal research로 확인한다.

## Checklist Inventory

`assets/policies/checklists/`에서 필요한 파일만 읽는다.

| 영역 | 파일 | 트리거 예시 |
|------|------|-------------|
| 계약서 | `contract_review.yaml` | 계약서 검토, 위험 조항 |
| 노동/인사 | `labor_hr.yaml` | 해고 절차, 수습기간, 근로시간 |
| 개인정보 | `privacy_compliance.yaml` | 개인정보 동의, 처리위탁, 국외이전 |
| 공정거래 | `fair_trade.yaml` | 하도급, 담합, 대리점 |
| 중대재해 | `serious_accident.yaml` | 중대재해법, 안전보건 |
| 투자/M&A | `investment_due_diligence.yaml` | 투자 실사, M&A |
| 법인설립 | `startup.yaml` | 법인 설립, 사업자등록 |
| 식품 | `food_business.yaml` | 식품 인허가, HACCP |
| 의료 | `healthcare.yaml` | 의료기기, 원격의료 |
| 부동산 | `realestate.yaml` | 임대차, 건설 인허가 |
| 모빌리티 | `mobility.yaml` | 운송 면허, 플랫폼 운송 |

## Flow

기본형 (경계 충족 시 조정 가능):

```text
질문 접수 -> checklist 후보 선택 -> triage 질문 최소화
  -> branch/threshold/if_yes 조건으로 관련 item만 추출
  -> item.laws 원문 확인, 인허가·서식·기한은 공식 기관 사이트에서 실시간 확인
  -> 회사 맥락으로 적용 범위 조정 + related_checklists 안내
```

## Triage Rules

- `branches`: 사용자 답변에 맞는 분기만 진행한다.
- `if_yes` / `if_no`: 해당 조건에 맞는 경로만 진행한다.
- `thresholds`: 직원 수, 매출, 업종, 처리 건수 등 수치 기준을 적용한다.
- 모르는 값이 결론을 좌우하면 질문한다.
- 모르는 값이 결론을 좌우하지 않으면 가정을 표시하고 진행한다.

## Filtering Rules

- 전체 체크리스트를 그대로 나열하지 않는다.
- 사용자 상황에 관련된 items만 출력한다.
- 각 item의 법령·시행령·고시 근거를 확인한다.
- 체크리스트 YAML은 triage 후보이지 현행 결론 근거가 아니다.
- `type: checklist` 파일은 후보 체크리스트를 만들고, `type: research_guide` 파일은 조사 계획과 확인 질문을 만든다.
- 두 타입 모두 `runtime_contract.triage_only: true`이며, `runtime_contract.live_check_required: true`이면 결론 전 공식 소스 확인이 필수다.
- 인허가 요건, 수수료, 처리기간, 구비서류, 공식 서식 URL은 번들 데이터에 의존하지 않고 관할 기관·정부24·law.go.kr 등 공식 소스로 확인한다.
- 이미 이행된 항목과 미확인 항목을 구분한다.
- 여러 사업장, 여러 제품, 여러 계약을 표로 비교해야 하면 `references/bulk-tabular-review.md`로 schema를 먼저 확정하고, 각 셀의 법령 근거는 이 체크리스트 workflow로 확인한다.

## Asset Type Contracts

`type: checklist`:

- 사용자 상황에 맞는 후보 의무·점검 항목만 추린다.
- `deadline`, `penalty`, `threshold`, `fee`, `form`, `authority`, `required_documents` 같은 `volatile_fields`는 현재값으로 출력하기 전에 live source로 확인한다.
- 확인하지 못한 항목은 `needs_review`, `[STALE]`, `[INSUFFICIENT]` 중 실제 상태로 둔다.

`type: research_guide`:

- 완료 체크리스트가 아니라 조사 질문, 확인할 권위자료, 쟁점 맵을 만든다.
- 공정거래, M&A, 계약 검토처럼 맥락 의존성이 큰 영역은 조사 계획을 먼저 제시하고 결론은 출처 권위 라벨 확인 후 낸다.
- 검색 명령·키워드는 research seed일 뿐 결론 근거가 아니다.

## Freshness Routing

체크리스트 특수 처리 요지: 파일의 `maintenance.next_review`가 지났거나 금액·기한·인원 기준·과징금·서식·구비서류처럼 변동성 높은 값이 있으면 `references/source-access.md#freshness-gate`를 적용한다 — stale 체크리스트는 상황을 좁히는 후보로만 쓰고, 결론에 들어가는 법령명·조문·시행일·threshold·금액·기한·구비서류는 live legal research로 재확인하며, 실패 시 `[STALE]` 또는 `[INSUFFICIENT]`로 표시하고 stale 상태를 검토자 메모의 `Currency`에 짧게 남긴다. 일반 원칙(triage_only, 승격 금지)과 등록 자산 목록은 `references/freshness-governance.md`와 `assets/policies/freshness_debt.yaml`이 단일 소스다.

## Company Context

가능하면 `~/.beopsuny/profile.yaml`의 아래 필드를 반영한다.

- `employee_count`
- `industry`
- `handles_personal_data`
- `has_subcontract`
- `party_position.default`
- `interested_laws`

Lite 모드에서 파일 접근이 없으면 필요한 맥락만 사용자에게 묻는다.

## Related Checklists

복합 이슈면 관련 체크리스트를 안내한다.

예:

- SaaS 계약 + 개인정보 처리 -> `contract_review.yaml` + `privacy_compliance.yaml`
- 대기업이 중소기업에게 용역 위탁 -> `contract_review.yaml` + `fair_trade.yaml`
- 식품 온라인 판매 -> `food_business.yaml` + `privacy_compliance.yaml` 가능성

관련 체크리스트를 안내하더라도 결론은 확인된 법령과 출처 권위 라벨 기준으로 낸다.
