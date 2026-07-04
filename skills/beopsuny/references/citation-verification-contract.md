# Citation Verification Contract

이 문서는 법순이의 단일 citation verification contract다. 출처 권위 라벨, verification status, provenance를 분리하고, `[VERIFIED]`를 붙일 수 있는 최소 조건을 고정한다. 세부 라벨표는 `source-grading.md`와 `assets/policies/source_grades.yaml`을 따르되, VERIFIED minimum conditions는 여기의 계약을 우선한다.

## Core Contract

출처 권위 라벨과 verification status는 서로 다른 축이다.

| 축 | 의미 | 예시 |
| --- | --- | --- |
| 출처 권위 라벨 | 소스 자체의 법적 성격과 사용 가능성 | 공식 원문 law.go.kr 원문, 공식 원문 기반 로컬 미러 legalize-kr/admrule-kr, 해설/의견 로펌 해설 |
| verification status | 이번 응답에서 해당 법률 사실을 실제로 확인했는지 | `[VERIFIED]`, `[UNVERIFIED]`, `[INSUFFICIENT]` |
| provenance | 이번 응답에서 실제로 확인한 경로 | `law.go.kr 원문 확인`, `법망 API 원문 필드 확인`, `web — verify` |

`[VERIFIED]`는 공식 원문이라는 뜻이 아니다. `[VERIFIED]`는 이번 응답에서 특정 citation과 pinpoint를 실제 원문 또는 공식 응답으로 대조했고, 그 확인 경로와 최신성 한계를 답변에 남겼다는 뜻이다.

## VERIFIED Minimum Conditions

`[VERIFIED]`를 붙이려면 네 조건이 모두 필요하다.

1. **대상 특정**: 법령명 + 조/항/호, 판례 선고일 + 사건번호, 행정규칙명 + 발령기관처럼 재조회 가능한 citation과 pinpoint가 있다.
2. **원문 대조**: 원문 필드 또는 공식 원문 화면, 또는 공식 원문 기반 로컬 미러 파일에서 실제 문구, 조문 구조, 판시사항, 시행일, 발령기관 중 답변 결론에 필요한 부분을 확인했다.
3. **최신성 표시**: 현행, 시행 예정, 미시행, 조회 실패, 검토일 중 해당 상태를 드러냈다. 금액, 기한, 과징금, 서식, 구비서류처럼 변동성이 큰 사실은 freshness gate를 통과해야 한다.
4. **provenance 표시**: provenance는 이번 응답에서 실제로 확인한 경로로 적는다. 예: `legalize-kr 로컬 미러 확인 (직접 공식 사이트 확인 아님)`, `admrule-kr 로컬 미러 확인 (직접 공식 사이트 확인 아님)`, `ordinance-kr 로컬 미러 확인 (직접 공식 사이트 확인 아님)`, `precedent-kr 로컬 미러 확인 (직접 공식 사이트 확인 아님)`, `law.go.kr 원문 확인`, `glaw.scourt.go.kr 원문 확인`, `법망 API 원문 필드 확인`.

하나라도 빠지면 `[VERIFIED]`를 쓰지 않는다. 결론 강도는 `[UNVERIFIED]`, `[INSUFFICIENT]`, `[STALE]`, `[CONTRADICTED]`, `[EDITORIAL]` 중 실제 상태로 낮춘다.

## Source Family Rules

| Source family | 역할 | `[VERIFIED]` 가능 조건 |
| --- | --- | --- |
| local legalize-kr / precedent-kr / admrule-kr / ordinance-kr | Full 모드의 법령·판례·행정규칙·자치법규 로컬 미러 확인 | 해당 파일의 원문, 조문, 판례 본문, 시행일, 발령기관, 지자체 식별자 중 결론에 필요한 부분을 직접 읽고 provenance를 `{source_family} 로컬 미러 확인 (직접 공식 사이트 확인 아님)`으로 표시한 경우 |
| 법망 API wrapper | Lite 모드 원문 조회, 행정규칙·해석례·판례 discovery | 검색 결과나 요약이 아니라 `law?action=get`, `case?action=get`, `tools?action=verify` 등에서 원문 필드 또는 공식 식별자 검증 결과를 확인한 경우 |
| law.go.kr | 법령, 행정규칙, 판례 공식 원문 화면 | 실제 원문 화면 또는 공식 원문 응답을 열어 citation과 pinpoint를 확인한 경우 |
| glaw.scourt.go.kr | 법원 판례 원문 화면 | 사건번호와 판결 요지/본문을 공식 화면에서 확인한 경우 |
| WebSearch | 공식 API와 로컬 데이터로 닿지 않는 정책·집행 동향 보조 | WebSearch 자체만으로는 원칙적으로 `[VERIFIED]`가 아니다. 검색 결과에서 공식 원문으로 들어가 확인했을 때 그 공식 원문 provenance로 기록한다. |
| 번들 YAML 후보 | issue spotting, 체크리스트, 용어·조항 후보 | official source 확인 없이 `[VERIFIED]`로 승격하지 않는다. 후보로만 쓰거나 live source 확인 뒤 별도 provenance를 남긴다. |

법망 API wrapper는 공식 데이터를 감싸는 접근 경로지만, wrapper의 요약·스니펫, 검색 result title, 유사도 결과만으로는 원문 대조가 아니다. `법망 API 확인`이라고만 쓰지 말고 `법망 API 원문 필드 확인`, `법망 API search 결과만 확인`, `법망 API 장애로 조회 실패`처럼 확인 수준을 적는다.

local legalize-kr/precedent-kr/admrule-kr/ordinance-kr는 공식 원문 기반 로컬 미러다. 이번 응답에서 로컬 파일만 읽었다면 source_authority는 `공식 원문 기반 로컬 미러` 또는 `공식 원문 기반 로컬 미러: 하급심`이고, provenance는 직접 공식 사이트 확인이 아님을 명시한다. `law.go.kr 원문 확인` 또는 `glaw.scourt.go.kr 원문 확인`은 해당 공식 사이트나 공식 응답을 실제로 연 경우에만 쓴다.

미러 frontmatter `시행일자`가 미래인 시행 전 공포본의 currency 표기는 `references/source-access.md`의 미러 시행일 확인 규칙을 단일 기준으로 따른다.

`admrule-kr`와 `ordinance-kr` 파일에서 `본문출처: parsing-failed`처럼 본문 원문이 비어 있거나 첨부파일로만 제공되는 경우, frontmatter만으로는 원문 대조 조건을 충족하지 않는다. 이때는 첨부파일 또는 law.go.kr 공식 화면을 추가 확인하거나 `[UNVERIFIED]`/`[INSUFFICIENT]`로 낮춘다.

## Downgrade Rules

아래 경우에는 `[VERIFIED]`를 쓰지 않는다.

- 요약·스니펫, 검색 결과 title, 링크 미리보기만 확인했다.
- `assets/data/*.yaml`, checklist, mandatory provision 후보, verification log 같은 번들 또는 저장 데이터만 봤다.
- 사용자가 제공한 조문번호, 사건번호, 금액, 기한을 독립 확인하지 않았다.
- 법령 ID, 인허가 요건, 공식 서식, 법정 기한을 official source 확인 없이 기억이나 후보 데이터로 처리했다.
- 링크 패턴이 맞아 보인다는 이유만으로 law.go.kr 또는 glaw.scourt.go.kr 원문 확인을 했다고 표시했다.
- API timeout, 5xx, `service_maintenance`, 빈 응답을 검색 0건이나 개정 없음으로 해석했다.

## Output Binding

답변에 노출하는 각 citation은 citation ledger의 `source_authority`, `verification_status`, `provenance`, `currency`, `supports`와 연결되어야 한다. ledger에 없거나 `supports`가 비어 있는 source는 결론 근거로 쓰지 않는다.

출력 형식은 다음 원칙을 따른다.

```markdown
**[공식 원문] [VERIFIED]** — law.go.kr 원문 확인
```

로컬 미러를 확인한 경우에는 직접 공식 사이트 확인과 구분한다.

```markdown
**[공식 원문 기반 로컬 미러] [VERIFIED]** — legalize-kr 로컬 미러 확인 (직접 공식 사이트 확인 아님)
```

검토자 메모나 business-user용 쉬운 라벨은 출처 권위 라벨과 verification status를 대체하지 않는다. `확인된 1차 근거` 같은 쉬운 표현을 쓰더라도 citation 줄에는 출처 권위 라벨, status, provenance를 유지한다.
