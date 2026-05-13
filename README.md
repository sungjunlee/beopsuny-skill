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

- **법령 조사** — 법률→시행령→시행규칙 연쇄 조회, 조문 단위 인용 + [law.go.kr](https://www.law.go.kr/) 링크
- **판례 조회** — 대법원/하급심 판례 검색 + [종합법률정보](https://glaw.scourt.go.kr/) 원문 링크
- **계약서 검토** — 유형별 체크리스트 + 조항 위험 분석 + 강행규정 충돌 탐지
- **컴플라이언스** — 업종별 규제, 연간 법정 의무 일정, 인허가 요건
- **법령 변경 감지** — `watched_laws` 등록 법령의 개정 이력 추적 (`git log` + 법망 API)
- **자가 검증 태그** — 답변마다 `[VERIFIED]`/`[UNVERIFIED]`/`[STALE]` 등 6종 태그 + 소스 Grade A–D → 환각 방지
- **Full / Lite 모드** — 로컬 데이터가 있으면 Full(조문·판례 전문 직접 조회), 없으면 법망 API 기반 Lite로 자동 fallback
- **지식 자산 보강 경계** — `beopsuny-knowledge` privacy manifest는 필요한 경우 recall 확장과 audit 보강에만 사용
- **전문 리뷰어** — 컴플라이언스/계약/노동/개인정보/공정거래/분쟁 영역별 관점
- **회사 맥락 메모리** — 회사 프로필·과거 검토 이력 기반 맥락 답변

## 데이터 소스

1·2순위는 외부 API 키 없이 바로 동작한다. 3순위는 OC 코드(법제처 Open API 무료 인증키)가 있을 때 추가로 사용. 1·2순위만으로 법령·판례·행정규칙 대부분은 커버된다.

| 순위 | 소스 | 내용 |
|------|------|------|
| 1 | [legalize-kr](https://github.com/legalize-kr/legalize-kr) + [precedent-kr](https://github.com/legalize-kr/precedent-kr) | 법령 6,907파일 + 판례 123,469건 (로컬 Markdown) |
| 2 | [법망 API](https://api.beopmang.org/) | 행정규칙, 해석례, 의안 (무인증) |
| 3 | [korean-law-mcp](https://github.com/chrisryugj/korean-law-mcp) | 헌재·행정심판·자치법규·조약 등 (OC 코드 필요) |

원문 확인 링크는 [law.go.kr](https://www.law.go.kr/) · [대법원 종합법률정보](https://glaw.scourt.go.kr/)로 제공된다.

## 설치

### 방법 1: Claude Code (권장)

Claude Code 프롬프트에서 아래 두 줄을 **한 줄씩** 실행한다. OS 무관.

1) 이 레포를 플러그인 마켓플레이스로 등록 (`.claude-plugin/marketplace.json` 기준, 이름: `beopsuny-skill`):

```
/plugin marketplace add sungjunlee/beopsuny-skill
```

2) 등록된 마켓플레이스에서 `beopsuny` 플러그인 설치:

```
/plugin install beopsuny@beopsuny-skill
```

설치 후 새 세션에서 스킬이 자동 활성화된다. 업데이트는 `/plugin marketplace update beopsuny-skill` 후 다시 install.

### 방법 2: Codex 등 다른 AI 코딩 에이전트

Codex CLI, Cursor, GitHub Copilot, Gemini CLI 등 [`skills` CLI](https://github.com/vercel-labs/skills)가 지원하는 에이전트에서는 터미널 한 줄로 설치:

```bash
npx skills add sungjunlee/beopsuny-skill -g -y
```

특정 에이전트만 지정하려면 `-a codex` / `-a cursor`. 제거는 `npx skills remove beopsuny -g -y`.

### 방법 3: Claude Desktop (Chat 탭) / claude.ai 웹

채팅 UI에서는 **Skill zip 파일을 그대로 업로드**한다. 압축 해제나 Custom Instructions 붙여넣기는 필요 없다.

**전제조건** — Settings → Capabilities에서 **Code execution and file creation** 활성화 (Free / Pro / Max / Team / Enterprise 모두 지원).

1. [Releases 페이지](https://github.com/sungjunlee/beopsuny-skill/releases)에서 최신 `beopsuny-skill-vX.X.X.zip` 다운로드 (압축 해제 X)
2. Claude Desktop 또는 claude.ai → **Customize → Skills** → `+` → `+ Create skill` → **Upload a skill**
3. zip 선택 → 업로드 완료 후 Skills 목록에서 **beopsuny** 토글 ON
4. 새 대화에서 법무 질문(예: `"이 계약서 봐줘"`)을 하면 자동 활성화

> UI 경로는 Anthropic이 자주 바꾼다. 다르면 공식 가이드 참고: [KO](https://support.claude.com/ko/articles/12512180-claude에서-스킬-사용하기) · [EN](https://support.claude.com/en/articles/12512180-use-skills-in-claude)
>
> **Chat 환경의 한계** — 로컬 파일시스템 접근 불가 → Lite 모드만 동작. 회사 프로필·검토 이력 등 영속 메모리도 대화 단위. Skills 기능을 못 쓰는 환경이면 [Chat 탭 가이드](docs/desktop-chat-guide.md)의 Projects + Custom Instructions fallback을 참조.

## 고급 설정 (선택)

### 개발/설치본 드리프트 확인

레포의 `skills/beopsuny/SKILL.md`와 실제 에이전트가 읽는 설치본이 다르면 수정 결과가 런타임에 반영되지 않는다. 릴리즈 전에는 기본 계약 검증을 실행한다.

```bash
python3 tests/validate_skill_contracts.py
```

시나리오 샘플 출력만 따로 확인하려면:

```bash
python3 tests/evaluate_scenario_outputs.py
```

로컬 전역 설치본까지 비교하려면 설치 경로를 명시한다.

```bash
BEOPSUNY_INSTALLED_SKILL_PATH=~/.agents/skills/beopsuny python3 tests/validate_skill_contracts.py
```

### Full 모드 로컬 데이터 (권장)

Claude Code · Codex CLI처럼 영속 파일시스템이 있는 환경에서는 **Full 모드를 권장한다**. 로컬 Markdown을 직접 읽어서 조문 맥락·판례 전문·`git log` 개정 이력까지 다각도로 조회할 수 있고, 오프라인에서도 1차 소스를 열어볼 수 있다.

법순이에게 요청하면 된다:

> "Full 모드로 해줘" / "법령·판례 데이터 다운로드해줘"

법순이가 `${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}` 경로에 두 레포를 clone한다 (합쳐 약 2.5GB — 법령 500MB + 판례 2GB). 이미 있으면 `git pull`로 최신화. 경로를 바꾸려면 `BEOPSUNY_DATA_ROOT` 환경변수로 override.

### OC 코드 발급 (무료)

[korean-law-mcp](https://github.com/chrisryugj/korean-law-mcp)를 통해 헌재 결정·행정심판·자치법규·조약 등 추가 데이터가 필요할 때만 발급받는다. 1·2순위 데이터 소스만으로도 대부분의 법무 업무는 커버된다.

1. [법제처 Open API 신청 페이지](https://open.law.go.kr/LSO/openApi/guideList.do) → 회원가입 → "Open API 사용 신청"
2. 신청서 작성 시 인증키(OC) 즉시 발급

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

법순이의 판단 근거는 **4개 레이어**로 분리되어 있다. 단일 소스 원칙(single source of truth)을 따라서 같은 사실이 여러 파일에 중복되지 않고, 법령 개정과 판정 로직 갱신을 독립적으로 할 수 있다.

```
 ① 체크리스트 (진입점)  ──┐
                          │
 ② 데이터 (사실 베이스) ──┼──► ③ 정책 (판정 로직) ──► 검토 출력
                          │
 ④ 메모리 (사용자 상태) ─┘       (Full 모드 한정)
```

### ① 체크리스트 — `assets/policies/checklists/` (11종)

질문이 들어오면 먼저 어느 체크리스트로 진입할지 결정한다. 계약서가 오면 `contract_review`에서 계약 유형을 감지한 뒤 업종별 체크리스트와 교차.

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

법령·조항·일정 같은 **사실 기반 레퍼런스**. 모든 파일은 `law_index.yaml`을 앵커로 서로 참조한다.

| 파일 | 용도 |
|------|------|
| `law_index.yaml` | 주요 법령 + 행정규칙 인덱스 (앵커) |
| `clause_references.yaml` | 계약 조항 → 관련 법령 매핑 |
| `compliance_calendar.yaml` | 연간 법정 의무 일정 |
| `permits.yaml` | 업종별 인허가 요건 |
| `legal_terms.yaml` | 영한 법률용어 사전 |
| `forms.yaml` | 법정 서식·양식 포인터 |

### ③ 정책 — `assets/policies/` (4 files)

"어느 조항을 강행규정 위반으로 볼지", "어느 출처를 결론 근거로 받아들일지" 같은 **판정 로직**. 데이터와 분리돼 있어 독립적으로 갱신 가능.

| 파일 | 용도 |
|------|------|
| `mandatory_provisions.yaml` | 한국 강행규정 단일 소스 (약관규제법·민법·개인정보보호법·공정거래법·하도급법·근로기준법) |
| `clause_taxonomy.yaml` | 계약 조항 분류 체계 |
| `review_mode.yaml` | 계약 검토 모드(`strict`/`moderate`/`loose`) 출력 스키마 |
| `source_grades.yaml` | 인용 소스 등급(A/B/C/D) 기준 |

### ④ 메모리 스키마 — `assets/schemas/` (5 files, Full 모드 전용)

회사 프로필·과거 검토 이력을 기억해서 맥락 있는 답을 돌려준다. Chat 탭·zip 환경에서는 대화 단위로만 유지되므로 실질적으로 **Full 모드(Claude Code / Codex CLI)에서만 발휘**된다.

| 파일 | 용도 |
|------|------|
| `company_profile.yaml` | 회사 프로필 (업종, 규모, `interested_laws`, `party_position`) |
| `internal_rules.yaml` | 사내 규정·결재 기준 |
| `past_reviews.yaml` | 과거 검토 이력 |
| `watched_laws.yaml` | 변경 감지 대상 법령 |
| `compliance_status.yaml` | 연간 컴플라이언스 이행 상태 |

## Acknowledgments

한국 법률 정보를 오픈 데이터로 만들어온 프로젝트들 위에 만들어졌다.

- **[legalize-kr](https://github.com/legalize-kr/legalize-kr)** — 대한민국 법령 전문을 Git으로 관리하는 오픈소스 (MIT). 1순위 데이터 소스
- **[precedent-kr](https://github.com/legalize-kr/precedent-kr)** — 대법원/하급심 판례 123,469건 Markdown (MIT). legalize-kr 자매
- **[법망 (Beopmang)](https://api.beopmang.org/)** — 행정규칙·해석례·의안 무인증 API
- **[korean-law-mcp](https://github.com/chrisryugj/korean-law-mcp)** — 법제처 API를 AI 친화적으로 래핑한 MCP (MIT). 헌재·행정심판·자치법규·조약까지 91개 도구
- **[국가법령정보센터 (law.go.kr)](https://www.law.go.kr/)** — 법제처 공식 서비스. 모든 법률 데이터의 원천

법령 텍스트는 대한민국 정부 공공저작물로서 자유롭게 이용할 수 있다.

## 라이선스

MIT
