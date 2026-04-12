# beopsuny-skill (법순이)

한국 법무 실무를 위한 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill.

A Claude Code skill for Korean legal work — statute/case law research, contract review, and compliance checks.

[legalize-kr](https://github.com/legalize-kr/legalize-kr)의 법령 데이터와 [법망](https://api.beopmang.org/) API를 활용하여, 외부 API 키 없이 정확한 법률 정보를 제공한다.

```
You: "이 계약서 검토해줘"

법순이: 계약 유형: SaaS 라이선스 | 상대방: 해외법인 | 당사 위치: 고객

  횡단 이슈
  - 국제거래 세금: 해당 (법인세법 제93조, 원천징수 22%)
  - 약관규제법: 해당 (다수 이용자 대상 표준 약관)

  주요 위험 조항
  | 조항              | 위험도 | 이슈                              |
  | Indemnification  | 상     | 고의/중과실 면책 불가 (약관규제법 제7조) |
  | Data Processing  | 상     | 국외이전 요건 미충족 (개인정보보호법 제28조의8) |
  ...
```

## 기능

- **법령 조사** — 법률 → 시행령 → 시행규칙 연쇄 조회. 조문 단위 인용 + [law.go.kr](https://www.law.go.kr/) 직접 링크
- **판례 조회** — 대법원/하급심 판례 검색. [대법원 종합법률정보](https://glaw.scourt.go.kr/) 원문 링크
- **계약서 검토** — 계약 유형별 체크리스트 + 조항별 위험 분석 + 강행규정 충돌 탐지
- **컴플라이언스** — 업종별 규제 확인, 연간 법정 의무 일정, 인허가 요건
- **전문 리뷰어** — 컴플라이언스/계약/노동/개인정보/공정거래/분쟁 영역별 전문 관점
- **회사 맥락 메모리** — 회사 프로필(업종, 규모)과 과거 검토 이력을 기억해서 맥락 있는 답변

## 데이터 소스

외부 API 키 없이 동작한다.

| 순위 | 소스 | 내용 | 인증 |
|------|------|------|------|
| 1순위 | [legalize-kr](https://github.com/legalize-kr/legalize-kr) + [precedent-kr](https://github.com/legalize-kr/precedent-kr) | 법령 6,907파일 + 판례 123,469건 (로컬 Markdown) | 없음 |
| 2순위 | [법망 API](https://api.beopmang.org/) | 행정규칙, 해석례, 의안 등 | 없음 |
| 3순위 | [korean-law-mcp](https://github.com/chrisryugj/korean-law-mcp) | 헌재, 행정심판, 조세심판, 자치법규, 조약, 별표 등 | OC 코드 (무료) |

1~2순위만으로 대부분의 법무 업무를 커버한다. 3순위는 OC 코드(법제처 Open API 인증키)가 있으면 추가로 사용할 수 있다.

법령/판례 원문 확인 링크는 [law.go.kr](https://www.law.go.kr/)과 [대법원 종합법률정보](https://glaw.scourt.go.kr/)를 제공한다.

## 설치

### 방법 1: 심볼릭 링크

레포를 clone한 뒤 skill 디렉토리를 Claude Code에 연결한다.

```bash
git clone https://github.com/sungjunlee/beopsuny-skill.git
ln -s "$(pwd)/beopsuny-skill/skills/beopsuny" ~/.claude/skills/beopsuny
```

### 방법 2: Claude Code Plugin

Claude Code에서 GitHub 레포를 plugin으로 설치한다.

```
/plugin marketplace add sungjunlee/beopsuny-skill
/plugin install beopsuny-skill@sungjunlee-beopsuny-skill
```

### 방법 3: zip 다운로드 (Claude Desktop 등)

[Releases](https://github.com/sungjunlee/beopsuny-skill/releases)에서 zip 파일을 받는다.

1. 최신 릴리스의 `beopsuny-skill-vX.X.X.zip` 다운로드
2. 압축 해제
3. `skills/beopsuny/SKILL.md` 내용을 Claude Desktop의 Project > Custom Instructions에 붙여넣기
4. 체크리스트 등 참조 파일이 필요하면 Project에 파일로 업로드

> Claude Desktop에서는 로컬 파일 접근이 제한되므로 일부 기능(법령 로컬 조회, 메모리)은 사용할 수 없다.

### OC 코드 발급 (선택, 무료)

법제처 Open API 인증키가 있으면 [korean-law-mcp](https://github.com/chrisryugj/korean-law-mcp)를 통해 헌재 결정, 행정심판, 자치법규, 조약 등 추가 데이터에 접근할 수 있다.

1. [법제처 Open API 신청 페이지](https://open.law.go.kr/LSO/openApi/guideList.do) 접속
2. 회원가입 → 로그인 → "Open API 사용 신청"
3. 신청서 작성하면 인증키(OC)가 바로 발급된다

> OC 코드 없이도 1~2순위 데이터 소스(legalize-kr + 법망)만으로 법령, 판례, 행정규칙의 대부분은 커버된다.

### 법령/판례 로컬 데이터 설정 (선택)

로컬 데이터를 설정하면 응답이 더 정확하고 빠르다. 설정하지 않아도 법망 API를 통해 기본 기능은 동작한다.

`BEOPSUNY_DATA_ROOT` 환경변수로 경로 override 가능 (기본 `~/.beopsuny/data`).

```bash
mkdir -p ${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}
cd ${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}

# 법령 (약 500MB)
git clone https://github.com/legalize-kr/legalize-kr.git

# 판례 (약 2GB)
git clone https://github.com/legalize-kr/precedent-kr.git
```

## 사용 예시

Claude Code에서 자연어로 질문하면 skill이 자동으로 활성화된다.

```
근로기준법에서 해고예고수당 규정 찾아줘
이 계약서 검토해줘 (파일 첨부)
개인정보 수집 동의 필요한지 확인해줘
중대재해법 우리 회사에 적용돼?
다음 달까지 해야 하는 법정 의무 뭐 있어?
```

## 포함된 자산

### 체크리스트 (11종)

| 체크리스트 | 용도 |
|-----------|------|
| `contract_review` | 계약서 검토 (유형별 분기) |
| `labor_hr` | 노동/인사 이슈 |
| `privacy_compliance` | 개인정보보호법 준수 |
| `fair_trade` | 공정거래/하도급 |
| `serious_accident` | 중대재해처벌법 |
| `startup` | 스타트업 법무 |
| `food_business` | 식품사업 인허가 |
| `healthcare` | 의료/헬스케어 규제 |
| `realestate` | 부동산 거래/임대 |
| `mobility` | 모빌리티/운송 |
| `investment_due_diligence` | 투자 실사 |

### 참조 자료

| 파일 | 용도 |
|------|------|
| `compliance_calendar.yaml` | 연간 법정 의무 일정 |
| `clause_references.yaml` | 계약 조항별 관련 법령 매핑 |
| `permits.yaml` | 업종별 인허가 요건 |
| `legal_terms.yaml` | 영한 법률용어 사전 |
| `law_index.yaml` | 주요 법령 + 행정규칙 인덱스 |

## Acknowledgments

이 프로젝트는 한국 법률 정보를 오픈 데이터로 만들어온 프로젝트들 위에 만들어졌다.

- **[legalize-kr](https://github.com/legalize-kr/legalize-kr)** — 대한민국 법령 전문을 Git으로 관리하는 오픈소스 프로젝트 (MIT). 법순이의 1순위 데이터 소스
- **[precedent-kr](https://github.com/legalize-kr/precedent-kr)** — 대법원/하급심 판례 123,469건을 Markdown으로 제공하는 오픈 데이터 (MIT). legalize-kr의 자매 프로젝트
- **[법망 (Beopmang)](https://api.beopmang.org/)** — 행정규칙, 해석례, 의안 등을 무인증 API로 제공하는 무료 서비스. legalize-kr이 커버하지 않는 영역을 보완
- **[korean-law-mcp](https://github.com/chrisryugj/korean-law-mcp)** — 법제처 API를 AI 친화적으로 래핑한 MCP 서버 (MIT). 헌재, 행정심판, 자치법규, 조약까지 커버하는 91개 도구
- **[국가법령정보센터 (law.go.kr)](https://www.law.go.kr/)** — 대한민국 법제처가 운영하는 공식 법령 정보 서비스. 모든 법률 데이터의 원천

법령 텍스트는 대한민국 정부 공공저작물로서 자유롭게 이용할 수 있다.

## 라이선스

MIT
