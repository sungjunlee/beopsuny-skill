# 자가 검증

출력 직전 수행하는 내부 검증 절차다. 별도 서브에이전트 호출 없이 같은 응답 생성 흐름 안에서 확인한다.

## 목적

법률 분야에서 잘못된 조문, 판례, 시행일, 과징금 기준은 실제 피해로 이어질 수 있다. 자가 검증은 답변 직전 citation, 법리, 사용자 맥락, 계약 counter-drafting 경계를 다시 확인해 Source Grade 태그와 결론 강도를 맞추는 품질 게이트다.

## Dim 1: Citation 검증

필수. 응답에 등장한 모든 법령, 판례, 행정규칙 인용을 확인한다.

- 인용한 조문이 실제 존재하는가
- 조/항/호 번호가 정확한가
- 인용 내용 또는 paraphrase가 조문 취지를 왜곡하지 않는가
- 판례 사건번호가 실존 형식이고 가능한 경우 원문 확인이 끝났는가

`[VERIFIED]`는 위 조건을 통과한 경우에만 붙인다. 일부라도 확인할 수 없으면 `[UNVERIFIED]` 또는 `[INSUFFICIENT]`로 낮춘다.

## Dim 2: Legal Substance

필수. 결론의 법적 논리와 적용 범위를 확인한다.

- 결론이 사용자 전제와 논리적으로 연결되는가
- 법률 위계가 지켜졌는가: 헌법 -> 법률 -> 시행령 -> 시행규칙 -> 행정규칙
- 단서, 예외, 적용 제외, 경과규정을 빠뜨리지 않았는가
- 시행일과 공포일을 구분했는가
- 실무 기준, 과징금, 신청 절차, 서식 질문에서 행정규칙을 확인했는가

논리가 불충분하면 결론을 유보하고 추가 확인 필요를 표시한다.

## Dim 3: Client Alignment

필수. 실제 질문과 회사 맥락에 맞는지 확인한다.

- 사용자가 묻지 않은 workflow로 과잉 라우팅하지 않았는가
- 법률 원론만 나열하지 않고 실무적 시사점을 제공했는가
- `~/.beopsuny/profile.yaml`의 업종, 규모, 갑/을 위치, 개인정보 처리 여부가 관련되면 반영했는가
- 맥락이 결론을 좌우하는데 빠져 있다면 질문하거나 가정을 표시했는가

## Dim 4: Counter-drafting Quality

조건부. 계약 검토에서 `why_risky`, `negotiation_points`, `alt_wording_hint` 중 하나라도 출력한 경우에만 적용한다.

- `alt_wording_hint`가 한국 강행규정상 유효 가능한 방향인가
- `negotiation_points`가 `profile.yaml.party_position` 또는 사용자 관점과 일치하는가
- 출력이 "자동 생성 금지선"을 넘지 않았는가

금지 패턴은 `assets/policies/review_mode.yaml#counter_draft_forbidden_patterns`를 단일 소스로 삼는다. 대표 금지 표현:

- 아래 문구로 교체
- 최종 수정안
- 다음 조항으로 대체
- 이 문구를 사용

실패 시 단정 문구를 힌트형으로 재작성하고 재검증한다. 재검증도 실패하면 해당 필드를 생략한다.

## Failure Handling

| 실패 차원 | 조치 |
|-----------|------|
| Citation | 해당 인용을 `[UNVERIFIED]` 또는 `[INSUFFICIENT]`로 낮추고, 필요하면 소스 Grade를 하향한다 |
| Legal Substance | 논리 연결을 재점검하고, 결론 유지가 어려우면 결론을 유보한다 |
| Client Alignment | 질문을 재해석하거나 필요한 회사 맥락을 묻는다 |
| Counter-drafting | 단정 문구를 힌트형으로 바꾸거나 해당 필드를 생략한다 |

## Metadata Format

전부 통과:

```markdown
---
🔍 **자가 검증**: Citation 3/3 ✓ | Legal Substance ✓ | Client Alignment ✓ | Counter-draft ✓
```

계약 검토 아닌 응답:

```markdown
---
🔍 **자가 검증**: Citation 3/3 ✓ | Legal Substance ✓ | Client Alignment ✓ | Counter-draft n/a
```

일부 확인 불가:

```markdown
---
🔍 **자가 검증**: Citation 2/3 ⚠ | Legal Substance ✓ | Client Alignment ✓ | Counter-draft ✓
   - 경업금지 판례 원문 확인 불가 -> [UNVERIFIED] 표시됨
```

인용이 0개인 절차 안내, 용어 설명 등은 `Citation n/a`로 표기한다.

## 법률 AI 할루시네이션 연구

- **Stanford 2025** — 상업 법률 AI 도구(LexisNexis+, Westlaw AI-Assisted Research, Practical Law 등)도 **1/6 ~ 1/3 쿼리**에서 할루시네이션(존재하지 않는 판례·조문·오인용)이 발생한다고 보고. 법률 분야에서 부정확한 인용은 실제 피해로 이어진다.
  - Dim 1이 존재 여부, 조항 번호, 취지 일치, 판례 사건번호 형식을 확인하는 근거.
  - 링크는 연구 공개 시점에 확인해 갱신한다. 본 문서는 claim 출처 트래킹용이다.

## 설계 메모

- 자가 검증은 Source Grading의 `downgrade_triggers`(`assets/policies/source_grades.yaml`)와 연동한다.
- tag 체계 외 새 타입을 도입하지 않고 기존 6개 상태 태그만 사용한다.
- 향후 연구 인용이 추가되면 본 문서 하단에 append-only로 쌓아 `SKILL.md`가 길어지지 않도록 한다.
