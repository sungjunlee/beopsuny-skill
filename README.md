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
  | Data Processing  | 상     | 위탁·국외이전 요건 미충족 (개인정보보호법 제26조 · 제28조의8) |
  ...
```

## 기능

- **법령 조사** — 법률 → 시행령 → 시행규칙 연쇄 조회. 조문 단위 인용 + [law.go.kr](https://www.law.go.kr/) 직접 링크
- **판례 조회** — 대법원/하급심 판례 검색. [대법원 종합법률정보](https://glaw.scourt.go.kr/) 원문 링크
- **계약서 검토** — 계약 유형별 체크리스트 + 조항별 위험 분석 + 강행규정 충돌 탐지
- **컴플라이언스** — 업종별 규제 확인, 연간 법정 의무 일정, 인허가 요건
- **법령 변경 감지** — `watched_laws`에 등록한 법령의 최근 개정 이력을 git log + 법망 API로 추적. "조회 실패 ≠ 개정 없음" 경계 보존
- **자가 검증 태그** — 모든 답변에 `[VERIFIED]` / `[UNVERIFIED]` / `[INSUFFICIENT]` / `[CONTRADICTED]` / `[STALE]` / `[EDITORIAL]` + 소스 Grade A~D 부여 → 환각 방지
- **Full 모드 (권장) / Lite 모드** — Full은 로컬 `legalize-kr` + `precedent-kr`을 직접 조회해 조문 원문·판례 전문·개정 이력을 다각도로 분석. 로컬 데이터가 없으면 법망 API + WebSearch 기반 Lite로 자동 fallback
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

### 방법 1: Claude Code Plugin (권장)

Claude Code 안에서 플러그인 마켓플레이스로 추가·설치한다. OS 무관하게 Claude Code CLI 한 줄씩이면 끝.

```
/plugin marketplace add sungjunlee/beopsuny-skill
/plugin install beopsuny@beopsuny-skill
```

- 첫 줄은 이 레포를 마켓플레이스로 등록한다 (이름: `beopsuny-skill`, `.claude-plugin/marketplace.json` 기준).
- 둘째 줄은 마켓플레이스에서 `beopsuny` 플러그인을 설치한다. 새 세션에서 스킬이 자동 활성화된다.
- 업데이트는 `/plugin marketplace update beopsuny-skill` 후 다시 install.

> **Windows 사용자 주의**
> - PowerShell에서 `/plugin ...` 명령을 붙여넣을 때 파싱이 깨지면 인자를 `"..."`로 감싼다: `/plugin install "beopsuny@beopsuny-skill"`.
> - `git config --global core.symlinks true`가 꺼져 있으면 plugin clone 시 내부 심볼릭 링크가 깨질 수 있다. `git config --global --get core.symlinks`로 확인.
> - 마켓플레이스 클론 위치는 `%USERPROFILE%\.claude\plugins\`. 설치가 꼬이면 해당 폴더에서 마켓플레이스 디렉토리를 지우고 다시 `/plugin marketplace add`.

### 방법 2: `skills` CLI (Claude Code 바깥에서 설치)

Claude Code를 열지 않은 상태에서 터미널로 설치하거나 Cursor/Copilot 등 여러 에이전트에 한꺼번에 깔고 싶을 때. [vercel-labs/skills](https://github.com/vercel-labs/skills) CLI를 사용한다.

```bash
npx skills add sungjunlee/beopsuny-skill -g -y
```

- `-g` — 전역(유저 레벨, `~/.claude/skills/`) 설치
- `-y` — 확인 프롬프트 스킵
- `-a claude-code` — Claude Code에만 한정하고 싶으면 추가 (기본은 감지된 모든 에이전트)
- 제거: `npx skills remove beopsuny -g -y`

### 방법 3: zip 업로드 (Claude Desktop / claude.ai 웹)

Claude Desktop과 claude.ai 웹에서는 **Skill을 zip 파일 그대로 업로드**한다. 압축 해제하거나 Custom Instructions에 본문을 붙여넣을 필요 없다.

**전제조건** — Settings → Capabilities에서 **Code execution and file creation**이 켜져 있어야 한다. (Free/Pro/Max/Team/Enterprise 모두 지원)

1. [Releases](https://github.com/sungjunlee/beopsuny-skill/releases)에서 `beopsuny-skill-vX.X.X.zip` 다운로드 (압축 해제 X)
2. Claude Desktop (또는 claude.ai) → **Customize → Skills** → `+` → `+ Create skill` → **Upload a skill**
3. 다운로드한 zip 선택 → 업로드 완료 후 Skills 목록에서 **beopsuny** 토글 ON
4. 새 대화에서 "이 계약서 봐줘" 같은 법무 질문을 하면 자동으로 활성화된다

> UI 경로(예: `Customize`, `Skills` 메뉴 위치)는 Anthropic이 자주 업데이트한다. 현재 화면과 다르면 공식 가이드를 참고:
> - 한국어: [Claude에서 스킬 사용하기](https://support.claude.com/ko/articles/12512180-claude에서-스킬-사용하기) · [사용자 정의 Skills 만드는 방법](https://support.claude.com/ko/articles/12512198-사용자-정의-skills를-만드는-방법)
> - English: [Use Skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude)

**제약사항** — Claude Desktop/웹의 Skill 실행 환경은 사용자 PC의 로컬 파일에 접근할 수 없다. 따라서 로컬 `legalize-kr`/`precedent-kr` 데이터는 사용 못 하고, 법망 API + WebSearch 기반 **Lite 모드**로 동작한다. 회사 프로필·검토 이력 같은 영속 메모리도 대화 단위로만 유지된다.

> Skills 기능을 쓸 수 없는 환경이라면 [Claude Desktop Chat 탭 가이드](docs/desktop-chat-guide.md)의 Projects + Custom Instructions 방식을 fallback으로 사용할 수 있다.

### OC 코드 발급 (선택, 무료)

법제처 Open API 인증키가 있으면 [korean-law-mcp](https://github.com/chrisryugj/korean-law-mcp)를 통해 헌재 결정, 행정심판, 자치법규, 조약 등 추가 데이터에 접근할 수 있다.

1. [법제처 Open API 신청 페이지](https://open.law.go.kr/LSO/openApi/guideList.do) 접속
2. 회원가입 → 로그인 → "Open API 사용 신청"
3. 신청서 작성하면 인증키(OC)가 바로 발급된다

> OC 코드 없이도 1~2순위 데이터 소스(legalize-kr + 법망)만으로 법령, 판례, 행정규칙의 대부분은 커버된다.

### Full 모드 로컬 데이터 (권장)

Claude Code·Codex CLI처럼 영속 파일시스템이 있는 환경에서는 **Full 모드를 권장한다**. 법망 API만 쓰는 Lite 모드와 비교해:

- **조문·판례 전문 직접 조회** — 키워드 검색이 아니라 Markdown 파일을 직접 읽어서 맥락·주석까지 확인
- **법령 개정 이력 추적** — `git log`로 특정 조문이 언제 어떻게 바뀌었는지 시점별 diff
- **판례 123,469건 풀텍스트 검색** — API 페이징·rate limit 없이 `grep`/`rg` 수준의 속도
- **오프라인 동작** — 인터넷 없이도 1차 소스 조회 가능

법순이에게 그냥 이렇게 요청하면 된다:

> "Full 모드로 해줘" / "법령·판례 데이터 다운로드해줘"

법순이가 `${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}` 경로에 두 레포를 clone한다 (합쳐 약 2.5GB — 법령 500MB + 판례 2GB). 이미 있으면 `git pull`로 최신화. 경로를 바꾸려면 `BEOPSUNY_DATA_ROOT` 환경변수로 override.

> Desktop Chat 탭/claude.ai 웹처럼 대화마다 파일시스템이 초기화되는 환경에서는 clone이 무의미하므로 **Lite 모드가 자동 기본값**이다. 이 경우 본 섹션은 무시.

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

법순이의 판단 근거는 **4개 레이어**로 분리되어 있다. 각 레이어는 단일 소스 원칙(single source of truth)을 따르고, 같은 사실이 여러 파일에 중복되지 않도록 관리된다. 이 구조 덕분에 법령 개정이 있어도 데이터만 갱신하면 판정 로직은 건드리지 않아도 된다.

```
 ① 체크리스트 (진입점)  ──┐
                          │
 ② 데이터 (사실 베이스) ──┼──► ③ 정책 (판정 로직) ──► 검토 출력
                          │
 ④ 메모리 (사용자 상태) ─┘       (Full 모드 한정)
```

### ① 체크리스트 — `assets/policies/checklists/` (11종)

질문이 들어오면 먼저 어느 체크리스트로 진입할지 결정한다. 계약서가 오면 `contract_review`에서 계약 유형을 감지한 뒤 업종별 체크리스트와 교차한다. 업종/시나리오가 확실하면 바로 해당 체크리스트로 진입.

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

### ② 데이터 — `assets/data/` (6 files)

법령·조항·일정처럼 **사실 기반 레퍼런스**. 모든 파일은 `law_index.yaml`을 앵커로 서로 참조한다 — 예: `clause_references.yaml`의 조항이 어느 법의 어느 조문에 매핑되는지, `permits.yaml`의 인허가가 어느 법률·행정규칙에 근거하는지가 한 지점으로 수렴한다.

| 파일 | 용도 |
|------|------|
| `law_index.yaml` | 주요 법령 + 행정규칙 인덱스 (다른 파일들의 앵커) |
| `clause_references.yaml` | 계약 조항 → 관련 법령 매핑 (단일 소스) |
| `compliance_calendar.yaml` | 연간 법정 의무 일정 |
| `permits.yaml` | 업종별 인허가 요건 |
| `legal_terms.yaml` | 영한 법률용어 사전 |
| `forms.yaml` | 법정 서식·양식 포인터 |

### ③ 정책 — `assets/policies/` (4 files)

"어느 조항을 강행규정 위반으로 볼지", "어느 출처를 결론 근거로 받아들일지" 같은 **판정 로직**. 데이터와 분리돼 있어 법령 개정 없이도 검토 기준만 갱신할 수 있고, 반대로 기준이 그대로여도 법령 텍스트는 매주 업데이트된다.

| 파일 | 용도 |
|------|------|
| `mandatory_provisions.yaml` | 한국 강행규정 단일 소스 (약관규제법·민법·개인정보보호법·공정거래법·하도급법·근로기준법) |
| `clause_taxonomy.yaml` | 계약 조항 분류 체계 |
| `review_mode.yaml` | 계약 검토 모드별(`strict` / `moderate` / `loose`) 출력 스키마 |
| `source_grades.yaml` | 인용 소스 등급(A/B/C/D) 기준 |

### ④ 메모리 스키마 — `assets/schemas/` (5 files, Full 모드 전용)

회사 프로필과 과거 검토 이력을 기억해서 맥락 있는 답을 돌려준다. 같은 계약을 두 번 검토하거나, 회사가 관심 등록한 법령의 개정을 응답 끝에 한 줄로 알려주는 식. Chat 탭·zip 환경에서는 대화 단위로만 유지되므로 실질적으로 **Full 모드(Claude Code / Codex CLI)에서만 발휘**된다.

| 파일 | 용도 |
|------|------|
| `company_profile.yaml` | 회사 프로필 (업종, 규모, `interested_laws`, `party_position`) |
| `internal_rules.yaml` | 사내 규정·결재 기준 |
| `past_reviews.yaml` | 과거 검토 이력 |
| `watched_laws.yaml` | 변경 감지 대상 법령 |
| `compliance_status.yaml` | 연간 컴플라이언스 이행 상태 |

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
