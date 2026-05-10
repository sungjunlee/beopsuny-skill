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

```text
질문 접수
  -> checklist 후보 선택
  -> triage 질문 최소화
  -> branch/threshold/if_yes 조건 적용
  -> 관련 item만 추출
  -> item.laws 원문 확인
  -> 회사 맥락으로 적용 범위 조정
  -> related_checklists 안내
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
- 이미 이행된 항목과 미확인 항목을 구분한다.

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

관련 체크리스트를 안내하더라도 결론은 확인된 법령과 Source Grade 기준으로 낸다.
