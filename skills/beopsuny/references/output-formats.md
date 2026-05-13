# 출력 형식

모든 법률 정보에는 원소스 링크와 Source Grade 태그를 제공한다. 링크는 패턴이 확실할 때만 만들고 추정 링크를 만들지 않는다.

## 법령 인용

```markdown
## 민법 제750조 (불법행위의 내용)
**[Grade A] [VERIFIED]** — legalize-kr 로컬

> 고의 또는 과실로 인한 위법행위로 타인에게 손해를 가한 자는...

- **시행일**: 2025. 1. 31.
- **법령 원문**: https://www.law.go.kr/법령/민법/제750조
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

대법원은 Grade A, 하급심은 Grade B다. 하급심 인용 시 상급심 변경 가능성을 언급한다.

```markdown
## 대법원 2023. 1. 12. 선고 2022다12345 판결
**[Grade A] [VERIFIED]** — precedent-kr 로컬

- **사건명**: 손해배상(기)
- **판시사항**: ...
- **법원 원문**: https://glaw.scourt.go.kr/wsjo/intesrch/sjo022.do?query=2022다12345
- **법령정보**: https://www.law.go.kr/판례/(2022다12345)
```

```markdown
## 서울고등법원 2022나56789 판결
**[Grade B] [VERIFIED]** — precedent-kr 로컬
※ 상급심에 의해 변경 가능 — Grade A 판례와 교차검증 권장
```

## 행정규칙 인용

행정규칙은 법망 API 또는 공식 링크로 확인하고, law.go.kr 검색 링크를 제공한다.

```markdown
## {고시명} — {발령기관}
**[Grade A] [VERIFIED]** — 법망 API (type=admrul)

> {본문 인용}

- **원문 검색**: https://www.law.go.kr/행정규칙/{고시명}
```

## 2차 소스 인용

로펌 뉴스레터, 학술 논문, 법률 매체 해설은 Grade C다. 단독 결론 근거로 쓰지 않는다.

```markdown
## 관련 해설
**[Grade C]** 김장 법률사무소 뉴스레터 (2024-10)
[EDITORIAL: Single-source, Grade C]

※ 위는 단일 2차 소스의 의견입니다. 결론은 Grade A/B 법령·판례를 우선 참조하세요.
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

## 검토 메모 Lite

`full` 법률 답변에서 출처 범위, 읽은 범위, 최신성 한계가 결론 이해에 중요하면 본문 앞이나 자가 검증 직전에 1-3줄로 표시한다. 단순 조문 확인처럼 명확한 답변에는 생략할 수 있다.

```markdown
**검토 메모**: 법령 원문 2건 확인 | 법망 API 1건 확인 | 판례 원문 미확인
```

긴 계약서나 일부 문서만 읽은 경우:

```markdown
**검토 메모**: 본문 1-18쪽과 DPA 별첨만 확인 | 부속서 B/C 원문 미확인 | 개인정보 조항은 부분 검토
```

출처 provenance는 실제 수행한 확인을 기준으로 적는다. 예: `legalize-kr 로컬 확인`, `법망 API 확인`, `law.go.kr 확인`, `사용자 제공`, `web — verify`, `확인 불가`. Source Grade는 소스의 신뢰도이고, provenance는 이번 응답에서 실제로 무엇을 확인했는지다.

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
