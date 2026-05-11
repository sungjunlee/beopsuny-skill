# 계약서 검토 보조 가이드

계약 검토는 계약 문구를 최종 확정하는 기능이 아니라, 조항별 한국법 이슈와 확인해야 할 근거를 좁히는 workflow다. 모든 결론은 현재 법령·판례·행정규칙 확인과 Source Grade, verification status를 거쳐야 한다.

## 범위

지원:

- 한국어·영문 계약 조항의 한국법 이슈 식별
- 계약 유형, 당사자 위치, 거래 구조에 따른 위험 조항 분류
- 강행규정 충돌 가능성, 누락 조항, 협상 포인트 제시
- 영문 법률용어의 한국법상 뉘앙스 설명

경계:

- 위험도는 `상/중/하` 실무 우선순위이지 자동 점수나 확정 평가가 아니다.
- Counter-drafting은 확정 문구가 아니라 검토 힌트와 협상 방향만 제공한다.
- "아래 문구로 교체", "최종 수정안", "이 문구를 사용" 같은 단정 표현은 금지한다.
- 법령 원문을 확인하지 않은 조항 매핑은 `[UNVERIFIED]` 또는 `[INSUFFICIENT]`로 둔다.

## 입력 파악

먼저 아래 정보를 확인한다. 결론을 좌우하는 값이 없으면 질문하고, 좌우하지 않으면 가정을 표시한다.

| 축 | 확인할 내용 |
| --- | --- |
| 계약 유형 | SaaS/라이선스, 용역, 공급, 고용, 투자, NDA 등 |
| 당사자 위치 | 우리 쪽이 고객인지, 공급자인지, 플랫폼인지 |
| 상대방 | 국내/해외, 대기업/중소기업, 소비자 상대 여부 |
| 개인정보 | 처리위탁, 제3자 제공, 국외이전, subprocessor 여부 |
| 거래 특성 | 하도급, 전자용역, 외국환, 수출입·전략물자, 표준계약서 적용 가능성 |

## Review Mode

`assets/policies/review_mode.yaml`을 단일 소스로 사용한다.

| 모드 | 트리거 | 동작 |
| --- | --- | --- |
| `strict` | "엄격하게", "꼼꼼히", "전수 검토" | 낮은 위험도와 누락 조항까지 표시, 횡단 이슈 전수 확인 |
| `moderate` | 기본값 | 중간 이상 위험과 주요 누락 조항 표시, 트리거된 횡단 이슈 확인 |
| `loose` | "간단히", "핵심만", "요약" | 높은 위험과 명백한 누락 위주, 횡단 이슈는 필요한 경우만 |

출력 필드(`why_risky`, `negotiation_points`, `alt_wording_hint`)와 금지 문구는 `review_mode.yaml`을 따른다. 이 파일이 SKILL.md보다 우선한다.

## 검토 흐름

```text
계약 유형과 당사자 위치 파악
  -> review_mode 결정
  -> 횡단 이슈 확인
  -> 조항 분류와 관련 법령 후보 매핑
  -> 법령/하위법령/행정규칙/판례 원문 확인
  -> Source Grade + verification status 부여
  -> 자가 검증 후 출력
```

## 횡단 이슈

조항별 검토 전에 계약 전체에 걸치는 이슈를 먼저 본다.

| 이슈 | 트리거 | 확인 근거 |
| --- | --- | --- |
| 국제거래 세금 | 해외법인 상대방, SaaS/라이선스/용역 대가 지급 | 법인세법, 부가가치세법, 조세조약 |
| 하도급 | 원사업자-수급사업자 구조, 용역·제조 위탁 | 하도급법, 공정위 고시·표준계약서 |
| 약관규제 | 다수 고객에게 반복 사용하는 표준 조건 | 약관규제법 |
| 개인정보 | 고객·임직원·이용자 데이터 처리 | 개인정보보호법, 시행령, 개인정보위 자료 |
| 외국환·수출입 | 대외지급, 전략물자, 이중용도 품목 | 외국환거래법, 대외무역법, 관계 고시 |

## 조항별 매핑

`assets/data/clause_references.yaml`을 후보 매핑으로 사용하되, 그 자체를 결론 근거로 쓰지 않는다. 각 후보 법령은 현재 원문 또는 공식 API로 다시 확인한다.

| 조항군 | 대표 조항 | 주의할 한국법 이슈 |
| --- | --- | --- |
| Boilerplate | Governing Law, Dispute Resolution, Assignment | 국제사법 강행규정, 중재합의 서면성, 채권양도 통지 |
| Risk Allocation | Indemnification, Limitation of Liability, Liquidated Damages | 약관규제법 제7조/제8조, 민법 손해배상·손해배상액 예정 |
| IP & Data | Work for Hire, IP Assignment, Data Processing | 저작권법 제9조·제14조, 개인정보보호법 제26조·제28조의8 |
| Employment | Non-Compete, Non-Solicitation, Invention Assignment | 직업선택의 자유, 민법 제103조, 발명진흥법 보상 |
| Commercial Terms | Payment, Termination, Exclusivity, MFN | 이자·지급기일, 해지권, 공정거래법·하도급법 |

## 출력 형식

```markdown
## 계약서 검토 결과

**계약 유형**: [유형] | **당사자 위치**: [고객/공급자/미확인] | **review_mode**: [strict/moderate/loose]

### 횡단 이슈

| 이슈 | 상태 | 확인 필요 사항 |
| --- | --- | --- |
| ... | 해당/비해당/미확인 | ... |

### 주요 위험 조항

| 조항 | 위험도 | 이슈 | 근거 |
| --- | --- | --- | --- |
| Limitation of Liability | 상 | 고의·중과실 면책까지 포함되면 무효 가능성 | **[Grade A] [VERIFIED]** 약관규제법 제7조 |

### 협상 포인트

- [조항명] 상대방 책임 제한 범위, 고의·중과실 carve-out, 개인정보 사고 책임 범위를 확인.

---
🔍 **자가 검증**: Citation n/m | Legal Substance ✓/⚠ | Client Alignment ✓/⚠ | Counter-draft ✓/⚠/n/a
```

## Source Grade와 Verification

- 법령·판례·행정규칙 근거는 `**[Grade X] [VERIFIED/UNVERIFIED/INSUFFICIENT]**` 형식으로 표시한다.
- `clause_references.yaml`, 체크리스트, 과거 검토 이력은 후보·맥락 자료다. 결론 근거가 되려면 live legal research로 확인해야 한다.
- Grade C 해설은 보조 의견이다. 단독 결론은 `[EDITORIAL: Single-source, Grade C]`로 유보한다.
- 확인 실패는 "문제 없음"이 아니라 `[INSUFFICIENT]`다.

## Counter-drafting

허용:

- 조항의 위험 이유(`why_risky`)
- 협상 포인트(`negotiation_points`)
- 확정 문구가 아니라 검토 힌트인 대안 방향(`alt_wording_hint`)

금지:

- 최종 수정안처럼 확정된 문구 제시
- 사용자에게 그대로 삽입하라고 지시
- 강행규정 충돌 가능성을 확인하지 않은 대체 문언

계약 힌트를 하나라도 출력하면 `Counter-drafting Quality` 자가 검증을 수행한다. 실패하면 단정 문구를 힌트형으로 바꾸거나 해당 필드를 생략한다.

## 영문 계약 용어

영문 용어는 `assets/data/legal_terms.yaml`을 우선 참고한다. 한국법에 같은 제도가 없거나 효과가 다르면 직역 대신 차이를 설명한다.

| 영문 | 주의점 |
| --- | --- |
| Consideration | 한국 민법상 계약 성립 요건과 다르므로 "약인"으로만 기계 번역하지 않는다 |
| Warranty / Representation | 보증과 진술의 효과 차이를 조항 맥락에서 설명한다 |
| Work for Hire | 저작권법 제9조 요건과 외주 개발 관행 차이를 확인한다 |
| Moral Rights | 저작인격권은 일신전속성이 있어 양도 문구 효력이 제한된다 |

## 면책 고지

계약 검토 답변도 SKILL.md의 공통 면책 고지를 따른다. 이 reference 안에서 별도 문구를 새로 만들지 않는다.
