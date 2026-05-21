# 대량 표 검토 워크플로

여러 계약, 체크리스트, 컴플라이언스 항목을 표로 비교해 달라는 요청에 사용한다. 이 워크플로는 결론을 자동 확정하는 도구가 아니라, 검토자가 확인할 evidence grid를 만드는 절차다.

## 적용 범위

사용:

- 여러 계약에서 동일 항목을 비교
- 계약 조항, 인허가, 컴플라이언스 의무를 표로 정리
- "엑셀처럼", "grid", "대량 검토", "계약 20개에서 해지 조항만 비교" 같은 요청

비사용:

- 단일 조문 확인
- 단일 계약의 상세 법률 검토
- 사용자가 표가 아니라 결론 메모를 원하는 경우

## 기본 흐름

```text
입력 범위 확인
  -> schema 초안 작성
  -> 사용자 확인
  -> 3-5개 샘플 검토
  -> schema 조정
  -> 전체 표 작성
  -> evidence/status 점검
  -> 자가 검증 및 읽은 범위 표시
```

## Column Type

| Type | 반환값 | 사용 예 |
| --- | --- | --- |
| `verbatim` | 문서의 정확한 문구 | 조항 원문, 정의 조항 |
| `classify` | 정해진 option 중 하나 | 있음/없음, consent_required/silent |
| `date` | ISO 날짜 | 계약일, 해지 통지 기한 |
| `duration` | 숫자 + 단위 | 계약기간, 통지기간 |
| `currency` | 금액 + 통화 | 책임한도, 수수료 |
| `number` | 숫자 | 직원 수, 처리 건수 |
| `free` | 짧은 설명 | 다른 type으로 표현하기 어려운 요약 |

`free`는 드리프트 위험이 높으므로 최소화한다.

## Cell State

빈칸을 쓰지 않는다. 확인되지 않은 값은 아래 상태 중 하나로 표시한다.

| State | 의미 |
| --- | --- |
| `answered` | 값과 근거가 확인됨 |
| `not_present` | 읽은 범위에서 해당 항목이 없음 |
| `unclear` | 문구는 있으나 분류가 불명확함 |
| `needs_review` | 사람의 법률 판단 또는 추가 원문 확인 필요 |

quote/location을 확보하지 못하면 `answered`가 아니라 `needs_review`다.

## Evidence Rule

각 셀은 가능한 한 아래 값을 가진다.

```yaml
value: ""
state: "needs_review"
source_grade: ""
quote: ""
location: ""
notes: ""
```

계약 문서에서 온 값은 quote와 location을 붙인다. 법령/행정규칙/판례에서 온 값은 Source Grade와 verification status를 붙인다. 후보 체크리스트나 clause mapping만으로는 `answered`가 될 수 없다. `answered`는 quote/location 또는 live Source Grade verification이 있을 때만 허용한다.

## Schema 예시

```yaml
schema:
  name: "SaaS 계약 책임제한 비교"
  columns:
    - id: counterparty
      label: "상대방"
      type: verbatim
      prompt: "계약 상대방은 누구인가?"
    - id: liability_cap
      label: "책임한도"
      type: currency
      prompt: "책임한도 금액 또는 산정 기준은 무엇인가?"
    - id: gross_negligence_carveout
      label: "고의·중과실 carve-out"
      type: classify
      options: [present, absent, unclear]
      prompt: "고의 또는 중과실 책임이 책임제한에서 제외되는가?"
```

## 출력 예시

```markdown
**검토 메모**: 5개 계약 중 샘플 2개로 schema 확인 | 각 셀은 evidence 확인 전 검토 lead

| 문서 | 책임한도 | 상태 | Evidence | 확인 |
| --- | --- | --- | --- | --- |
| A MSA | 12개월 수수료 | answered | §12.2 "fees paid in the twelve months..." | 미확인 |
| B MSA | null | needs_review | quote_unavailable: OCR 불량 | 추가 원문 필요 |
| C NDA | null | not_present | 책임제한 조항 없음(읽은 범위: 전문) | 미확인 |
```

## 대량 입력 안전장치

- 읽은 문서 수, 제외된 문서 수, 읽은 범위를 검토 메모에 표시한다.
- 일부 문서만 읽었으면 전체 결론처럼 말하지 않는다.
- 샘플 검토 후 schema가 맞지 않으면 전체 실행 전에 사용자에게 조정안을 보여준다.
- 표가 10행을 넘거나 status/date/severity 열이 있으면 dashboard나 CSV는 제안할 수 있지만, 자동 생성은 별도 요청이 있을 때만 한다.

## 다른 workflow와의 관계

- 계약 조항의 법적 위험 판단은 `contract_review`가 담당한다.
- 인허가·연간 의무 판단은 `compliance_checklist`가 담당한다.
- 책임제한, 해지권, 개인정보, 인허가, 제재, 법정기한처럼 법률 리스크가 있는 column은 이 문서만으로 결론 내리지 않는다. schema에는 column type과 evidence status를 정의하고, 해당 셀의 법적 판단은 `contract_review` 또는 `compliance_checklist`에서 Source Grade 기준으로 확인한다.
- 이 워크플로는 같은 질문을 여러 문서에 일관되게 적용하는 표면이다.
- `self-verification.md`의 긴 입력 읽은 범위 규칙을 반드시 따른다.
