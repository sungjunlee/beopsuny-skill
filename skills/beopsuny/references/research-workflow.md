# 법률 조사 워크플로우

법률 질문을 받으면 질문 난이도에 맞게 필요한 단계만 수행한다. 짧은 조문 확인에 모든 단계를 적용하지 않는다.

## Default Flow

```text
1. 질문 intent와 관할 확인
2. 현재 적용 법령과 시행일 확인
3. 하위법령/행정규칙 필요성 판단
4. 판례/해석례/정책 동향 필요성 판단
5. 출처 권위 라벨과 verification status 부여
6. 실무 적용 범위와 caveat 정리
```

## Legal Verification Core

모든 법률 결론은 답변 직전에 verification core를 통과한다. 적용 강도는 아래 2단 트리거로 정한다. 트리거는 라우팅 시점에 질문 형태로 판정하고, 애매하면 `full`로 올린다.

| Tier | 트리거 | 적용 |
| --- | --- | --- |
| `light` | 결론 후보가 1개이고 조문·시행일·공식 링크의 원문 확인으로 종결되는 질문 | 별도 map·packet·ledger 문서를 만들지 않는다. 출력 citation 줄이 한 줄 ledger 항목으로서 `citation`(pinpoint 포함), `source_authority`, `verification_status`, `provenance`, `currency`를 직접 담는다. contradiction scan은 확인한 원문이 사용자 전제와 다를 때만 수행한다. |
| `full` | 결론 후보 2개 이상, 또는 금액·기한·과징금·서식·구비서류, 또는 계약 검토 결론, 또는 외부 송부·기관 제출·소송/분쟁 포지션 | 아래 6단계 core 전체를 적용한다. |

light에서도 인용 없는 결론 금지, 상태 태그 downgrade, 출처 권위 라벨 규칙은 동일하게 적용된다.

`assets/schemas/legal_verification_packet.yaml`은 이 과정을 재사용 가능한 evidence shape로 고정한 템플릿이다. 기본은 내부 scratchpad이며, 사용자가 별도 검토 기록이나 handoff artifact를 요청한 경우에만 산출물로 저장하거나 노출한다.
`[VERIFIED]`, provenance, source family별 확인 조건은 `references/citation-verification-contract.md`를 단일 계약으로 따른다.

```text
issue-to-authority map 작성
  -> authority packet 구성
  -> citation ledger 작성
  -> contradiction scan
  -> conclusion binding
  -> self-verification
```

### 1. Issue-to-authority map

사용자 질문을 결론 후보 단위로 나눈다. 각 결론 후보에는 필요한 authority type을 붙인다.

| 결론 후보 | 필요한 authority |
| --- | --- |
| 조문 자체 | 법률 원문 + 시행일 |
| 예외·단서 적용 | 법률 원문 + 시행령/시행규칙 |
| 과징금·수수료·서식·처리기간 | 법률 원문 + 행정규칙/고시/기관 안내 |
| 유효/무효/위법 판단 | 법률 원문 + 관련 판례 또는 해석례 |
| 정책·집행 동향 | 현행 법령 결론과 분리된 공식 보도자료/가이드/처분례 |

질문 안에 여러 결론 후보가 있으면 하나의 큰 답을 만들기 전에 후보별로 authority가 충분한지 본다. authority가 부족한 결론 후보는 결론에서 분리하고 `[INSUFFICIENT]` 또는 추가 확인 항목으로 둔다.

### 2. Authority packet

각 결론 후보마다 실제로 확인한 source를 packet으로 묶는다.

```yaml
issue: "개인정보 국외이전 동의 필요 여부"
authorities:
  - type: "statute"
    citation: "개인정보 보호법 제28조의8"
    source_authority: "공식 원문"
    verification_status: "[VERIFIED]"
    provenance: "law.go.kr 원문 확인"
    currency: "현행 원문 기준"
  - type: "guidance"
    citation: "개인정보보호위원회 가이드라인"
    source_authority: "공식 실무자료"
    verification_status: "[UNVERIFIED]"
    provenance: "web — verify"
    currency: "원문 미확인"
```

packet 안의 source가 모두 후보·스니펫·stale 자산이면 결론을 확정하지 않는다.

### 3. Citation ledger

답변에 실제로 노출할 모든 법령·판례·행정규칙 인용은 내부 citation ledger에 한 번씩 들어가야 한다. ledger는 출력 필수 형식은 아니지만, 검토자 메모와 자가 검증의 근거가 된다.

필수 필드:

| 필드 | 의미 |
| --- | --- |
| `citation` | 법령명+조/항/호, 판례 선고일+사건번호, 행정규칙명+발령기관 |
| `pinpoint` | 인용한 조/항/호, 판시사항, 조문 위치 |
| `source_authority` | 공식 원문 / 공식 원문: 하급심 / 공식 원문 기반 로컬 미러 / 공식 원문 기반 로컬 미러: 하급심 / 공식 실무자료 / 공식 실무자료: 미확정 / 해설/의견 / 참고 제외 |
| `verification_status` | `[VERIFIED]`, `[UNVERIFIED]`, `[INSUFFICIENT]`, `[CONTRADICTED]`, `[STALE]`, `[EDITORIAL]` |
| `provenance` | 이번 응답에서 실제 확인한 경로 |
| `currency` | 현행/시행 예정/미시행/조회 실패/검토일 |
| `supports` | 답변의 어느 결론을 뒷받침하는지 |

ledger에 없는 인용은 출력하지 않는다. ledger에 있지만 `supports`가 없는 source는 배경 자료로만 표시하고 결론 근거로 쓰지 않는다.

### 4. Contradiction scan

같은 결론 후보에 대해 source가 서로 다르면 숨기지 않는다.

- 상위 규범과 하위 규범이 충돌해 보이면 상위 규범을 우선하고 하위 규범의 적용 범위를 확인한다.
- 현행 법령과 과거 뉴스레터·체크리스트가 다르면 과거 자료를 `[STALE]` 또는 `[EDITORIAL]`로 낮춘다.
- 대법원 판례와 하급심 판례가 다르면 대법원을 우선하고 하급심은 변경 가능성을 표시한다.
- 공식 기관 안내와 법령 원문 해석이 다르면 `[CONTRADICTED]`를 표시하고 결론 강도를 낮춘다.

모순이 해소되지 않으면 단정 결론을 내지 않고, 어떤 source가 어떤 방향인지 나눠서 보여준다.

### 5. Conclusion binding

최종 결론의 강도는 가장 약한 필수 authority에 맞춘다.

| 상태 | 결론 표현 |
| --- | --- |
| 모든 필수 authority가 `공식 원문`, `공식 원문: 하급심`, `공식 원문 기반 로컬 미러`, `공식 원문 기반 로컬 미러: 하급심`, `공식 실무자료` 중 해당 source 성격에 맞는 라벨이고 `[VERIFIED]` | “확인한 범위에서는 …” |
| 필수 authority가 `공식 실무자료: 미확정`, 계류·예정·초안, search-only 결과, 또는 원문 필드 미확인 자료 | `[UNVERIFIED]` 또는 `[INSUFFICIENT]` + 현재법 결론 유보 |
| 일부 authority가 `[UNVERIFIED]` | “가능성이 있으나 원문/공식 확인 전 단정 불가” |
| 필수 authority가 `[INSUFFICIENT]` | 결론 유보 + 확인할 source 제시 |
| source 간 충돌 | `[CONTRADICTED]` 표시 + 결론 강도 낮춤 |
| stale 자산만 있음 | triage 후보로만 제시 |

### 6. Verification packet contract

`full` tier 중에서도 복합 결론, 외부 송부, 기관 제출, 소송·분쟁 포지션, 과징금·신고기한·서식처럼 법적 효과가 큰 답변에서는 내부적으로 `legal_verification_packet.yaml`의 최소 shape를 채운다고 가정한다. `light` tier에서는 packet을 만들지 않는다. 어느 tier든 출력 인용은 citation ledger 계약을 통과해야 한다 — `light`의 ledger는 출력 citation 줄 그 자체다.

필수 블록:

- `matter` — 질문, 관할, 사용자 역할, destination
- `issue_to_authority_map` — 결론 후보, 필요한 authority, 법적 효과, 빠지면 결론 금지할 source
- `authority_packets` — 실제 확인 source와 출처 권위 라벨, verification status, provenance, currency
- `citation_ledger` — 답변에 노출할 인용의 허용 여부와 결론 연결
- `contradiction_scan` — stale/current, 상하위 규범, 판례 분기, 공식 안내와 원문 해석 차이
- `conclusion_binding` — 결론 강도와 다음 확인 필요 항목
- `self_verification` — 출처 권위 라벨, freshness, role/destination, unledgered citation 여부

이 packet은 법률 조언을 자동 확정하는 양식이 아니다. source가 약하거나 모순되면 결론을 강하게 만드는 것이 아니라 `qualified`, `insufficient`, `contradicted`, `triage_only`로 낮추는 구조다. `output_allowed: true`가 아닌 ledger 항목은 사용자 답변의 인용으로 노출하지 않는다.

## Investigation Matrix

| Phase | 무엇을 | Full 모드 | Lite 모드 | 기본 |
|-------|--------|-----------|-----------|------|
| 법령 | 법률 원문, 조/항/호 | legalize-kr | 법망 API 또는 law.go.kr | 필수 |
| 하위법령 | 시행령, 시행규칙 | 같은 법령 디렉토리 | 법망 API/law.go.kr | 조건부 필수 |
| 행정규칙 | 고시, 훈령, 예규 | admrule-kr -> 법망 API/law.go.kr | 법망 API/law.go.kr | 실무 기준이면 필수 |
| 자치법규 | 조례, 규칙, 지자체 고시 | ordinance-kr -> korean-law-mcp/law.go.kr | 법망 API/korean-law-mcp/law.go.kr | 지역이 특정되면 확인 |
| 개정 확인 | 공포일, 시행일, 최근 변경 | git log/show | 법망 history/diff | 시행일 질문이면 필수 |
| 해석례 | 법제처 해석 | 법망 API/korean-law-mcp | 법망 API/korean-law-mcp | 쟁점형 질문 |
| 정책 동향 | 부처 보도자료, 가이드 | WebSearch | WebSearch | 집행 동향 질문 |
| 제재 동향 | 과징금, 처분 사례 | WebSearch | WebSearch | 리스크·금액 질문 |
| 판례 | 관련 판결 | 법망 검색 -> precedent-kr 직접 읽기 | 법망 case search/get | 분쟁·해석 쟁점 |
| 개정안 | 계류 의안 | WebSearch/의안 링크 | WebSearch/의안 링크 | 미래 변경 질문 |

## Right-Sizing

- 조문·시행일·링크 확인: 법령 원문과 시행일만 확인한다.
- 과징금·절차·서식 질문: 행정규칙과 고시를 반드시 확인한다.
- 해고, 개인정보, 공정거래처럼 예외·단서가 많은 질문: 하위법령, 행정규칙, 판례 또는 해석례를 확인한다.
- "법적으로 괜찮아?"처럼 결론형 질문: 전제 조건을 먼저 좁히고, 불명확하면 질문하거나 가정 표시를 한다.
- 정책 동향·제재 동향은 공식 실무자료와 해설/의견 자료가 섞이므로 1차 법령 결론과 분리해 표시한다.

## 행정규칙 확인 기준

행정규칙은 실무 답변 품질을 좌우한다. 아래 질문에서는 생략하지 않는다.

- 과징금, 과태료, 제재 기준
- 인허가 신청 절차
- 신고/보고 서식
- 안전보건, 개인정보, 공정거래 세부 고시
- 정부 가이드라인이나 감독 기준이 실제 적용을 좌우하는 질문

Full 모드에서 `admrule-kr`가 있으면 행정규칙 원문 후보를 먼저 읽는다. 다만 `본문출처: parsing-failed`이거나 첨부파일이 결론에 필요한 경우에는 law.go.kr 원문 또는 첨부 파일을 추가 확인한다.

## 자치법규 확인 기준

자치법규는 지역 전제가 핵심이다. 아래 경우에 확인한다.

- 특정 지자체 조례·규칙·고시가 적용되는지 묻는 경우
- 인허가, 시설 설치, 보조금, 공공시설 이용처럼 지자체 규율이 실제 의무를 좌우하는 경우
- 국가 법령은 원칙만 두고 조례에 위임한 경우

Full 모드에서 `ordinance-kr`가 있고 지역이 특정되면 자치법규 원문 후보를 먼저 읽는다. 다만 전역 검색은 비용이 크므로 지자체·지역을 먼저 좁힌다. 지역이 없으면 결론을 만들지 말고 확인 질문 또는 범위 가정을 표시한다.

## 판례 확인 기준

판례는 아래 경우 확인한다.

- 조문 해석이 갈리는 경우
- 손해배상, 해고, 비밀유지, 경업금지, 저작권 귀속처럼 분쟁형 질문
- 사용자 질문이 "유효한가", "무효인가", "위법인가", "소송 가면"처럼 법원 판단을 묻는 경우

직접 `glaw.scourt.go.kr` 또는 `law.go.kr` 판례 원문을 열어 확인한 대법원 판례는 `공식 원문`, 하급심은 `공식 원문: 하급심`으로 표시한다. `precedent-kr` 로컬 미러만 읽은 경우 대법원 판례는 `공식 원문 기반 로컬 미러`, 하급심은 `공식 원문 기반 로컬 미러: 하급심`으로 표시하고 provenance에 `precedent-kr 로컬 미러 확인 (직접 공식 사이트 확인 아님)`을 남긴다. 하급심만 있으면 상급심 변경 가능성을 caveat로 붙인다.

## 개정안과 미시행 법령

- 의안은 시행 미확정이므로 공식 실무자료로 다룬다.
- 시행 예정 법령은 현재 적용법과 예정 시행법을 분리한다.
- "곧 바뀐다"는 표현은 시행일과 적용 대상을 확인한 뒤 사용한다.

## No Result Handling

검색 결과 없음은 결론이 아니다.

- 없는 법령을 만들지 않는다.
- 유사 법령이나 검색어를 제안한다.
- 원문 확인 불가 시 `[INSUFFICIENT]`로 표시한다.
- 법령명 매칭 실패, API timeout, git 실패는 "조회 실패"로 표시한다.
