# beopsuny-skill

> 한국 법무 실무를 위한 Claude Code skill

## 핵심 원칙

1. **정확한 인용**: 법령 조문은 반드시 법령명 + 조/항/호를 명시. 추정하지 않는다
2. **공식 링크 필수**: law.go.kr 링크를 함께 제공
3. **행정규칙 확인**: 법률/시행령만이 아니라 고시/훈령도 확인
4. **시행일 확인**: 공포일과 시행일이 다를 수 있음을 항상 체크
5. **환각 방지**: 확실하지 않으면 "확인 필요"로 표시. 없는 조문을 만들지 않는다

## 전문 리뷰어

| 리뷰어 | 역할 | 예시 |
|--------|------|------|
| 컴플라이언스 | 규제 준수, 법령 변경 영향 | "이 법 개정되면 우리 회사에 영향?" |
| 계약 | 계약서 조항 분석, 위험 식별 | "이 조항 불리한 거 없어?" |
| 노동 | 근로계약, 인사 이슈 | "이 해고 사유 정당해?" |
| 개인정보 | PIPA 준수, 데이터 처리 | "이 데이터 수집 동의 필요해?" |
| 공정거래 | 하도급, 독점 규제 | "이 계약 구조 하도급법 위반?" |
| 분쟁 | 리스크 평가, 소송 전략 | "소송 가면 승산은?" |

## 회사 맥락 메모리

| 컨텍스트 | 예시 | 활용 |
|----------|------|------|
| 회사 프로필 | 업종, 규모, 지역 | 같은 법이라도 적용이 다르다 |
| 관심 법령 | 자주 찾는 법, 소관 규제 | 법 개정 시 자동 알림 |
| 과거 검토 | 이전에 확인한 계약서, 해석 | 같은 질문 반복 방지 |
| 컴플라이언스 상태 | 연간 의무 이행 현황 | 캘린더 연동 |
| 회사 내규 | 사내 규정, 결재 기준 | 법령 + 내규 교차 검토 |

## 데이터 소스 우선순위

Full 모드 (로컬 데이터 있음) 기준. Lite 모드(Chat 탭)는 법망 API → WebSearch 순. 상세는 SKILL.md 참조.

```
법순이 → legalize-kr + precedent-kr (로컬)     ← 1순위: 법령 + 판례
       → 법망 API (무인증)                      ← 2순위: 행정규칙, 해석례, 의안
       → korean-law-mcp (OC 코드)               ← 3순위: 헌재, 행심, 자치법규, 조약 등
       → law.go.kr / glaw.scourt.go.kr          ← 링크 제공용
```

- **legalize-kr**: [legalize-kr/legalize-kr](https://github.com/legalize-kr/legalize-kr) — 법령 Markdown (6,907 파일)
- **precedent-kr**: [legalize-kr/precedent-kr](https://github.com/legalize-kr/precedent-kr) — 판례 Markdown (123,469건)
- **법망**: [api.beopmang.org](https://api.beopmang.org/) — REST API (무인증, 행정규칙/해석례/의안)

## 프로젝트 구조

```
skills/beopsuny/SKILL.md          # 스킬 본체 (Full/Lite 모드 지원)
skills/beopsuny/assets/           # YAML 데이터 (법령 인덱스, 체크리스트 등)
skills/beopsuny/references/       # 가이드 문서 (API, 외부사이트, 메모리 등)
docs/desktop-chat-guide.md        # Chat 탭 사용자 가이드 + 프로젝트 지침 템플릿
tests/scenarios/                  # 테스트 시나리오
```
