# 출력 형식

모든 법률 정보에는 원소스 링크와 출처 권위 라벨을 제공한다. 링크는 패턴이 확실할 때만 만들고 추정 링크를 만들지 않는다.

`[VERIFIED]`, provenance, source family별 확인 조건은 `references/citation-verification-contract.md`를 단일 계약으로 따른다. 출력 예시는 이 계약을 통과한 경우의 표시 형식이다.

## 법령 인용

```markdown
## 민법 제750조 (불법행위의 내용)
**[공식 원문 기반 로컬 미러] [VERIFIED]** — legalize-kr 로컬 미러 확인 (직접 공식 사이트 확인 아님)

> 고의 또는 과실로 인한 위법행위로 타인에게 손해를 가한 자는...

- **시행일**: 원문 확인 결과 기재 (예: YYYY. M. D.)
- **법령 원문**: https://www.law.go.kr/법령/민법/제750조
```

law.go.kr를 직접 열어 확인한 경우에는 다음처럼 표시한다.

```markdown
## 민법 제750조 (불법행위의 내용)
**[공식 원문] [VERIFIED]** — law.go.kr 원문 확인
```

항까지 특정할 때:

```text
https://www.law.go.kr/법령/개인정보보호법/제15조제1항
```

법체계 전체를 안내할 때:

```markdown
- **법률**: https://www.law.go.kr/법령/개인정보보호법
- **시행령**: https://www.law.go.kr/법령/개인정보보호법시행령
- **시행규칙**: https://www.law.go.kr/법령/개인정보보호법시행규칙
```

## 판례 인용

대법원과 하급심 모두 직접 공식 사이트 원문이면 `공식 원문`이다. precedent-kr 로컬 미러 파일만 확인했다면 `공식 원문 기반 로컬 미러`로 표시한다. 하급심 로컬 미러 인용 시 `공식 원문 기반 로컬 미러: 하급심`으로 표시하고 상급심 변경 가능성을 언급한다.

```markdown
## 대법원 {선고일} 선고 {사건번호} 판결
**[공식 원문 기반 로컬 미러] [VERIFIED]** — precedent-kr 로컬 미러 확인 (직접 공식 사이트 확인 아님)

- **사건명**: 손해배상(기)
- **판시사항**: ...
- **법원 원문**: https://glaw.scourt.go.kr/wsjo/intesrch/sjo022.do?query={사건번호}
- **법령정보**: https://www.law.go.kr/판례/({사건번호})
```

```markdown
## 서울고등법원 {사건번호} 판결
**[공식 원문 기반 로컬 미러: 하급심] [VERIFIED]** — precedent-kr 로컬 미러 확인 (직접 공식 사이트 확인 아님)
※ 상급심에 의해 변경 가능 — 대법원 판례와 교차검증 권장
```

glaw.scourt.go.kr를 직접 열어 확인한 경우에는 다음처럼 표시한다.

```markdown
## 대법원 {선고일} 선고 {사건번호} 판결
**[공식 원문] [VERIFIED]** — glaw.scourt.go.kr 원문 확인
```

## 행정규칙 인용

행정규칙은 법망 API 또는 공식 링크로 확인하고, law.go.kr 검색 링크를 제공한다. provenance는 실제 확인 수준을 나눠 쓴다.

```markdown
## {고시명} — {발령기관}
**[공식 원문] [VERIFIED]** — 법망 API 원문 필드 확인 (type=admrul) + law.go.kr 원문 링크 확인

> {본문 인용}

- **원문 검색**: https://www.law.go.kr/행정규칙/{고시명}
```

검색 결과나 메타데이터만 확인했으면 `[VERIFIED]`가 아니다.

```markdown
## {고시명} — {발령기관}
**[공식 실무자료: 미확정] [INSUFFICIENT]** — 법망 API 검색 결과만 확인 (type=admrul), 원문 필드·law.go.kr 본문 미확인

- **원문 검색 후보**: https://www.law.go.kr/행정규칙/{고시명}
- **의존 전 확인**: 원문 본문, 발령기관, 시행일, 개정 여부
```

## 2차 소스 인용

로펌 뉴스레터, 학술 논문, 법률 매체 해설은 `해설/의견`이다. 단독 결론 근거로 쓰지 않는다.

```markdown
## 관련 해설
**[해설/의견] [EDITORIAL]** 김장 법률사무소 뉴스레터 (2024-10)

※ 위는 단일 2차 소스의 의견입니다. 결론은 공식 원문 또는 공식 실무자료를 우선 참조하세요.
```

## 확인 불가

원문 매칭이 안 되면 등급을 추정하지 않고 유보한다.

```markdown
**[INSUFFICIENT]** — 해당 조문의 원문을 확인할 수 없음

확인 필요: law.go.kr에서 직접 조회를 권장합니다.
```

## 계약 검토 출력

계약 검토 상세 포맷은 `references/contract_review_guide.md`를 따른다. 기본 구조:

```markdown
## 계약서 검토 결과

**계약 유형**: [유형] | **상대방**: [국내/해외] | **당사 위치**: [고객/공급자]

### 횡단 이슈
- [ ] 국제거래 세금: [해당/비해당]
- [ ] 하도급법: [해당/비해당]
- [ ] 약관규제법: [해당/비해당]

### 주요 위험 조항

| 조항 | 위험도 | 이슈 | 근거 법령 |
|------|--------|------|----------|
| ... | 상/중/하 | ... | 법령명 제X조 |

### 권고사항
1. ...
```

## Role-based output modes

`profile.yaml.user_role`은 법률 정확성 기준을 낮추지 않는다. 다만 같은 법률 검토라도 사용자가 바로 쓸 산출물의 모양과 법적 효과 gate를 바꾼다. 역할이 불명확하면 `business_user`에 준해 보수적으로 출력한다.

역할과 destination의 구조화된 기준은 `assets/schemas/output_contract.yaml`을 따른다. 이 스키마는 결론의 법률 정확성을 낮추는 예외가 아니라, 검증된 결론이나 유보 결론을 누구에게 어떤 형태로 전달할지 정하는 포장 계약이다.

| 역할 | 기본 산출물 | 반드시 지킬 점 |
| --- | --- | --- |
| `lawyer` | 법률 근거, 쟁점 분석, 반대논거, 검토자 메모 중심 | 결론 강도와 미확인 범위를 명확히 표시하고, 대외 제출·송부 요청이면 destination을 확인 |
| `legal_ops` | 실무 메모, owner/action/escalation, 승인권자 확인 항목 중심 | 법적 효과가 있는 조치에는 담당 변호사 또는 승인권자 확인 gate를 둠 |
| `business_user` | 한 줄 결론, 지금 할 일, 하지 말 것, 확인 필요 정보, 변호사/법무에게 물어볼 질문, 근거 순서 | 서명·송부·제출·확정 답변을 바로 지시하지 않고, 법무 검토 전제와 의사결정 포인트를 분리 |
| `unknown` | `business_user`와 같은 보수적 출력 | 역할 확인 전에는 대외 행동을 확정 지시하지 않음 |

`business_user` 또는 `unknown` 기본 구조:

```markdown
## 한 줄 결론
...

## 지금 할 일
- ...

## 하지 말 것
- ...

## 확인 필요 정보
- ...

## 변호사/법무에게 물어볼 질문
- ...

## 근거
- **[공식 원문] [VERIFIED]** ...
```

비법무 사용자에게는 출처 권위 라벨을 숨기지 않되, 본문에서는 `확인된 1차 근거`, `추가 확인 필요`, `현행성 재확인 필요`처럼 쉬운 라벨을 함께 쓸 수 있다. 이 라벨은 출처 권위 라벨과 verification status를 대체하지 않는다.

### 고위험 상황 gate

`assets/schemas/output_contract.yaml`의 `high_risk_situations`(`징계·해고 통보`, `수사·고소·고발 대응`, `개인정보 유출 신고`, `기관 제출`, `계약 서명`, `고액 과징금 처분 대응`)에 해당하면, role(`lawyer` 포함)과 무관하게 확정 행동을 직접 지시하지 않고 변호사/legal_ops 검토를 요구하며, 기한(불복 기간 등)이 있으면 기한 확인을 최우선으로 안내한다. 각 상황별 세부 gate 문구는 스키마의 `high_risk_situations`를 단일 소스로 따르고 여기서 다시 나열하지 않는다.

## Destination output contracts

사용자가 산출물의 수신자나 사용처를 말하면, 같은 결론이라도 아래 destination 계약을 적용한다.

`assets/schemas/output_contract.yaml`의 `legal_effect_triggers`에 해당하는 요청이면 role mode와 destination contract를 함께 적용한다. `non_overrides`에 있는 Legal Verification Core, 출처 권위 / VERIFIED 계약, Freshness Governance, 변호사/법무 검토 필요 조건은 어떤 output preference로도 덮어쓸 수 없다.

Artifact/URL 배포 요청도 수신자나 사용처가 외부 송부·공유·제출 맥락이면 위 `legal_effect_triggers`를 적용한다. 채널별 배포 gate는 `references/report-deliverable.md#r4-artifact-배포-gate`를 따른다.

`practice_profile.yaml`이 default destination이나 preferred section을 제안할 수는 있다. 그러나 practice profile은 출력 선호일 뿐이므로 `business_user`/`unknown` gate, 외부 송부 전 법무 검토, 출처 권위 라벨과 verification status를 덮어쓰지 못한다. practice profile과 현재 사용자 요청이 충돌하면 현재 사용자 요청과 role/destination gate를 우선한다.

| 목적지 | 출력 방식 | 금지/주의 |
| --- | --- | --- |
| `internal_legal_memo` | 검토자 메모, 출처 권위 라벨, 자가 검증, 미확인 범위를 모두 포함 | 사실관계가 불완전하면 결론 강도를 낮춤 |
| `business_summary` | 의사결정 포인트, 실행 항목, 법무 확인 필요 항목 중심 | 내부 법리 논증 전체를 그대로 노출하지 않음 |
| `executive_report` | 핵심 리스크, 선택지, 비용/일정/책임 owner 중심 | 조문 나열만으로 끝내지 않음 |
| `external_draft` | 외부 공유용 초안임을 표시하고, 보내기 전 법무 검토 필요 문구를 포함 | 내부 검토자 메모와 자가 검증 블록을 그대로 포함하지 않는다 |
| `agency_or_court_submission` | 제출용 문안이 아니라 확인된 사실·근거·누락 항목 정리 중심 | 변호사 또는 담당 법무 검토 없이 제출하라고 쓰지 않음 |

목적지가 불명확한 상태에서 사용자가 "상대방에게 보낼 문구", "기관에 제출할 답변", "고객에게 회신"처럼 법적 효과가 있는 문안을 요청하면, 먼저 초안의 destination과 검토자를 표시한다. 외부 송부용 초안에는 내부 provenance를 숨기라는 뜻이 아니라, `검토자 메모`, `자가 검증`, 내부 사고 과정, 미확인 내부 메모를 그대로 붙여 보내지 않는다는 뜻이다.

## 검토자 메모 Lite / 표준 검토자 메모

`full` 법률 답변에서 출처 범위, 읽은 범위, 최신성 한계가 결론 이해에 중요하면 본문 앞에 표준 검토자 메모를 1-4줄로 표시한다. 단순 조문 확인처럼 명확한 답변에는 생략하거나 한 줄로 축약할 수 있다. `compact` 응답에는 검토자 메모를 강제하지 않는다.

```markdown
**검토자 메모**: Sources 법령 원문 2건 확인 · 법망 API 1건 확인 | Read 질문 범위 한정 | Currency 현재 원문 확인 | Before relying 판례 원문은 별도 확인
```

긴 계약서나 일부 문서만 읽은 경우:

```markdown
**검토자 메모**: Sources 사용자 제공 계약서 일부 · legalize-kr 로컬 미러 확인 (직접 공식 사이트 확인 아님) | Read 본문 1-18쪽과 DPA 별첨만 확인, 부속서 B/C 원문 미확인 | Currency 법령 원문 기준 | Before relying 미제공 부속서가 결론을 바꿀 수 있음
```

출처 provenance는 실제 수행한 확인을 기준으로 적는다. 예: `legalize-kr 로컬 미러 확인 (직접 공식 사이트 확인 아님)`, `precedent-kr 로컬 미러 확인 (직접 공식 사이트 확인 아님)`, `법망 API 확인`, `법망 API 원문 필드 확인`, `law.go.kr 원문 확인`, `glaw.scourt.go.kr 원문 확인`, `사용자 제공`, `web — verify`, `확인 불가`. 출처 권위 라벨은 소스의 성격과 사용 가능성이고, provenance는 이번 응답에서 실제로 무엇을 확인했는지다. `법망 API search 결과만 확인`이나 `WebSearch 스니펫 확인`은 `[VERIFIED]`가 아니라 `[UNVERIFIED]` 또는 `[INSUFFICIENT]`로 낮춘다.

검토자 메모 필드:

| 필드 | 의미 | 생략 가능 여부 |
| --- | --- | --- |
| `Sources` | 이번 응답에서 실제 확인한 provenance와 출처 권위 라벨 범위 | 법률 인용이 없으면 생략 가능 |
| `Read` | 읽은 문서, 페이지, 조항, 제외된 범위 | 단문 조문 확인이면 생략 가능 |
| `Currency` | 최신성 확인 기준일, 현행/미시행/조회 실패 여부 | 시행일·개정 여부가 쟁점이면 필수 |
| `Before relying` | 의존 전 사용자가 확인해야 할 1-2개 항목 | 확정 결론이 아니거나 대외 사용 예정이면 필수 |

검토자 메모에는 새로운 verification status 태그를 만들지 않는다. `[VERIFIED]`, `[UNVERIFIED]`, `[INSUFFICIENT]`, `[CONTRADICTED]`, `[STALE]`, `[EDITORIAL]`과 출처 권위 라벨 체계를 그대로 사용한다.

## 자가 검증 메타데이터

전부 통과:

```markdown
---
🔍 **자가 검증**: Citation 3/3 ✓ | Legal Substance ✓ | Client Alignment ✓ | Counter-draft ✓
```

계약 검토가 아닌 응답:

```markdown
---
🔍 **자가 검증**: Citation 3/3 ✓ | Legal Substance ✓ | Client Alignment ✓ | Counter-draft n/a
```

인용이 없는 절차 안내:

```markdown
---
🔍 **자가 검증**: Citation n/a | Legal Substance ✓ | Client Alignment ✓ | Counter-draft n/a
```

부분 실패:

```markdown
---
🔍 **자가 검증**: Citation 2/3 ⚠ | Legal Substance ✓ | Client Alignment ✓ | Counter-draft ✓
   - 경업금지 판례 원문 확인 불가 → [UNVERIFIED] 표시됨
```

## 링크 생성 규칙

| 대상 | URL 패턴 | 비고 |
|------|----------|------|
| 법령 조문 | `law.go.kr/법령/{법령명}/제{N}조` | 항: `제{N}조제{M}항` |
| 시행령 | `law.go.kr/법령/{법령명}시행령` | 띄어쓰기 없이 |
| 판례 1순위 | `glaw.scourt.go.kr/wsjo/intesrch/sjo022.do?query={사건번호}` | 대법원 원문 |
| 판례 보조 | `law.go.kr/판례/({사건번호})` | 괄호 필수 |
| 행정규칙 | `law.go.kr/행정규칙/{고시명}` | 검색 링크 |
| 의안 | `likms.assembly.go.kr/bill/billDetail.do?billId={의안ID}` | ID 있을 때만 |
