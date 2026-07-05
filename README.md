# beopsuny-skill (법순이)

한국 법무 실무를 위한 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill.

A Claude Code skill for Korean legal work — statute/case law research, contract review, and compliance checks.

[legalize-kr](https://github.com/legalize-kr/legalize-kr)의 법령 데이터와 [법망](https://api.beopmang.org/) API를 활용하여, 외부 API 키 없이 확인 가능한 1차 소스 중심의 법률 조사를 보조한다. 최종 답변은 출처 권위 라벨, verification status, 최신성 caveat를 함께 표시한다.

```
You: "이 계약서 검토해줘"

법순이: 계약 유형: SaaS 라이선스 | 상대방: 해외법인 | 당사 위치: 고객

  횡단 이슈
  - 국제거래 세금: [INSUFFICIENT] 법인세법·조세조약·원천징수율은 live source 확인 전 결론 금지
  - 약관규제법: [UNVERIFIED] 다수 이용자 대상 표준 약관 가능성. 약관성·거래구조 확인 필요

  주요 위험 조항
  | 조항              | 위험도 | 이슈                              |
  | Indemnification  | 상     | [UNVERIFIED] 고의/중과실 면책 제한 가능성. 약관규제법 제7조 원문과 계약 구조 확인 필요 |
  | Data Processing  | 상     | [UNVERIFIED] 위탁·국외이전 쟁점 후보. 개인정보보호법 제26조 · 제28조의8 및 하위 기준 확인 필요 |
  ...
```

## 기능

- **법령 조사** — 법률→시행령→시행규칙 연쇄 조회, 조문 단위 인용 + [law.go.kr](https://www.law.go.kr/) 링크
- **판례 조회** — 대법원/하급심 판례 검색 + [종합법률정보](https://glaw.scourt.go.kr/) 원문 링크
- **계약서 검토** — 유형별 체크리스트 + 조항 위험 분석 + 강행규정 충돌 탐지
- **컴플라이언스** — 업종별 규제, 연간 법정 의무 일정, 인허가 요건
- **법령 변경 감지** — `watched_laws` 등록 법령의 개정 이력 추적 (`git log` + 법망 API)
- **자가 검증 태그** — 답변마다 `[VERIFIED]`/`[UNVERIFIED]`/`[STALE]` 등 6종 태그 + 출처 권위 라벨 → 환각 방지
- **Legal verification core** — 결론 후보별 authority mapping, citation ledger, contradiction scan, conclusion binding
- **Freshness governance** — stale 번들 자산은 triage 후보로만 사용하고, live source 확인 전 현행 의무로 승격 금지
- **Role / destination output gate** — 비법무 사용자·외부 송부·기관 제출 문안은 법무 검토 전 단계와 실제 외부 행동을 분리
- **Full / Lite 모드** — 로컬 데이터가 있으면 Full(조문·판례 전문 직접 조회), 없으면 법망 API 기반 Lite로 자동 fallback
- **지식 자산 보강 경계** — `beopsuny-knowledge` privacy manifest는 필요한 경우 recall 확장과 audit 보강에만 사용
- **전문 리뷰어** — 컴플라이언스/계약/노동/개인정보/공정거래/분쟁 영역별 관점
- **회사 맥락 메모리** — 회사 프로필·과거 검토 이력 기반 맥락 답변

## 데이터 소스

기본 관점은 “Git으로 받은 공식 원문 기반 로컬 미러를 먼저 파일로 탐색하고, 없는 family나 discovery·교차확인이 필요한 범위는 법망 API와 공식 링크로 fallback”이다. 1·2순위는 외부 API 키 없이 바로 동작한다. 3순위는 OC 코드(법제처 Open API 무료 인증키)가 있을 때 추가로 사용한다.

| 순위 | 소스 | 내용 |
|------|------|------|
| 1 | [legalize-kr](https://github.com/legalize-kr/legalize-kr) + [admrule-kr](https://github.com/legalize-kr/admrule-kr) + [precedent-kr](https://github.com/legalize-kr/precedent-kr) | 법령·행정규칙·판례 공식 원문 기반 로컬 미러 Markdown (직접 공식 사이트 확인과 provenance 분리; 최신 개수는 upstream repo 확인) |
| 선택 | [ordinance-kr](https://github.com/legalize-kr/ordinance-kr) | 자치법규 로컬 미러. 파일 수가 커서 지역·지자체 질문이 많은 환경에서 선택 설치 |
| 2 | [법망 API](https://api.beopmang.org/) | 법령·행정규칙·해석례·의안·자치법규 discovery 및 Lite 모드 원문 조회 (무인증) |
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
PYTHON=${PYTHON:-python3}
$PYTHON -m pip install --no-input --disable-pip-version-check --target .test-deps -r requirements-dev.txt
PYTHONPATH=.test-deps $PYTHON tests/validate_skill_contracts.py
```

시나리오 샘플 출력만 따로 확인하려면:

```bash
PYTHONPATH=.test-deps $PYTHON tests/evaluate_scenario_outputs.py
```

high-risk forward eval harness를 dry/sample 모드로 확인하려면:

```bash
PYTHONPATH=.test-deps $PYTHON tests/forward_eval_harness.py --mode sample \
  --evidence tests/forward_evals/runs/sample.yaml
```

로컬 전역 설치본까지 비교하려면 설치 경로를 명시한다.

```bash
BEOPSUNY_INSTALLED_SKILL_PATH=~/.agents/skills/beopsuny PYTHONPATH=.test-deps $PYTHON tests/validate_skill_contracts.py
```

### 품질 계약 지도

법순이는 단일 public skill을 유지하되, 내부 문서 계약을 아래처럼 나눠 관리한다. 새 법률 기능을 추가할 때는 해당 계약 문서와 회귀 테스트를 함께 갱신한다.

| 품질 계약 | 기준 문서 | 회귀 검증 |
| --- | --- | --- |
| Always-on legal conclusion gates | `skills/beopsuny/references/citation-verification-contract.md`, `skills/beopsuny/references/self-verification.md`, `skills/beopsuny/references/output-formats.md` | `check_skill_quality_contract_router_map`, `check_router_always_on_legal_gates`, `router-01`, `router-05` |
| Legal verification core | `skills/beopsuny/references/research-workflow.md#legal-verification-core`, `skills/beopsuny/assets/schemas/legal_verification_packet.yaml`, `skills/beopsuny/references/self-verification.md`, `skills/beopsuny/references/citation-verification-contract.md`, `skills/beopsuny/references/source-grading.md` | `tests/validate_skill_contracts.py`, `tests/scenarios/16_router_regression.yaml` `router-16` |
| 출처 권위 / VERIFIED 계약 | `skills/beopsuny/references/citation-verification-contract.md`, `skills/beopsuny/references/source-grading.md`, `skills/beopsuny/assets/policies/source_grades.yaml`, `tests/fixtures/golden_citations.yaml` | `check_citation_verification_contract_single_source`, `check_golden_citation_fixtures`, `check_source_authority_verified_contract`, `legal_status_tag`, `no_verified_uncertainty` |
| Freshness governance | `skills/beopsuny/references/freshness-governance.md`, `skills/beopsuny/assets/policies/freshness_debt.yaml`, `skills/beopsuny/assets/schemas/freshness_metadata.yaml`, `skills/beopsuny/assets/schemas/freshness_revalidation.yaml`, `skills/beopsuny/references/source-access.md#freshness-gate` | `check_freshness_metadata_schema`, `check_freshness_debt_registry`, `check_freshness_revalidation_records`, `router-15` |
| Output role/destination gate | `skills/beopsuny/references/output-formats.md`, `skills/beopsuny/assets/schemas/output_contract.yaml`, `skills/beopsuny/references/self-verification.md#role--destination-gate` | `check_output_role_destination_contracts`, `router-14` |
| Profile / practice direction | `skills/beopsuny/references/memory-structure.md`, `skills/beopsuny/assets/schemas/company_profile.yaml`, `skills/beopsuny/assets/schemas/practice_profile.yaml` | `check_memory_profile_workflow`, `check_memory_practice_profile_direction`, `router-10`, `router-13` |
| Bulk evidence grid | `skills/beopsuny/references/bulk-tabular-review.md` | `check_bulk_tabular_review_reference`, `router-12` |

`tests/evaluate_scenario_outputs.py`는 법률 정답 채점기가 아니라 출력 guardrail 회귀 테스트다. 샘플 출력은 법률 결론의 정답이 아니라, 금지해야 할 실패모드와 반드시 드러내야 할 메타데이터를 고정한다.

`tests/forward_evals/beopsuny_guardrails.yaml`은 실제 모델 응답을 수동 또는 `tests/forward_eval_harness.py`로 점검하는 forward-eval prompt set이다. CI의 빠른 gate는 아니며, sample/template/score/command 모드 evidence는 `tests/forward_evals/runs/`에 기록한다. 실패 시 `prompt_id`, `guardrail_category`, `source_router_scenario`, output evidence 기준으로 이슈를 남긴다.

GitHub Actions의 `.github/workflows/contract-tests.yml` `Contract Tests` 워크플로는 pull request와 `main`/`master` push에서 위 계약 검증, router guardrail 평가, forward eval/knowledge manifest ingest 테스트, 테스트 harness compile을 실행한다.

### 품질 계약 변경 체크리스트

새 법률 기능, 업무 영역, 출력 모드, stale 자산, profile overlay를 추가할 때는 아래 순서로 갱신한다.

1. `skills/beopsuny/SKILL.md`의 의도 라우터(의도 표 또는 gate 표)에 새 트리거와 적용 계약을 연결한다.
2. 기준 문서(`references/*.md`)에 성공 기준, 금지 행동, 실패 시 downgrade 방식을 적는다.
3. 구조화가 필요한 계약이면 `assets/schemas/*.yaml` 또는 `assets/policies/*.yaml`에 최소 evidence shape를 추가한다.
4. `tests/scenarios/16_router_regression.yaml`에 대표 정상 시나리오를 추가하거나 기존 router 시나리오의 `must_do`/`forbidden_behavior`를 갱신한다.
5. `tests/fixtures/router_guardrail_outputs.yaml`와 `tests/evaluate_scenario_outputs.py`에 unsafe fixture 또는 guardrail rule을 추가해 금지 실패모드를 잡는다.
6. `tests/validate_skill_contracts.py`에 문서·스키마·README·CHANGELOG drift 검사를 추가한다.
7. README 품질 계약 지도와 CHANGELOG를 갱신한다.
8. `PYTHON=${PYTHON:-python3}`, `$PYTHON -m pip install --no-input --disable-pip-version-check --target .test-deps -r requirements-dev.txt`, `PYTHONPATH=.test-deps $PYTHON tests/validate_skill_contracts.py`, `PYTHONPATH=.test-deps $PYTHON tests/evaluate_scenario_outputs.py`, `PYTHONPATH=.test-deps $PYTHON tests/forward_eval_harness.py --mode sample --evidence tests/forward_evals/runs/sample.yaml`, `PYTHONPATH=.test-deps $PYTHON -m unittest tests/test_forward_eval_harness.py tests/test_knowledge_manifest_ingest.py`, `$PYTHON -m py_compile tests/validate_skill_contracts.py tests/evaluate_scenario_outputs.py tests/forward_eval_harness.py skills/beopsuny/assets/tools/knowledge_manifest_ingest.py tests/test_knowledge_manifest_ingest.py`, `git diff --check`를 실행한다.

기존 장점인 단일 라우터, 한국법 원문주의, 출처 권위 라벨, 자가 검증을 약화시키는 변경은 기능 추가로 보지 않는다. 새 계약은 기존 gate를 우회하지 말고, 필요한 경우 결론 강도를 낮추는 방식으로 연결한다.

### Full 모드 로컬 데이터 (권장)

Claude Code · Codex CLI처럼 영속 파일시스템이 있는 환경에서는 **Full 모드를 권장한다**. 공식 원문 기반 로컬 미러 Markdown을 직접 읽어서 조문 맥락·판례 전문·`git log` 개정 이력까지 다각도로 조회할 수 있고, 오프라인에서도 원문 기반 자료를 열어볼 수 있다. 출력에서는 `공식 원문 기반 로컬 미러`와 `로컬 미러 확인 (직접 공식 사이트 확인 아님)` provenance를 사용해 law.go.kr/glaw.scourt.go.kr 직접 확인과 구분한다.

법순이에게 요청하면 된다:

> "Full 모드로 해줘" / "법령·판례·행정규칙 데이터 다운로드해줘"

법순이가 `${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/data` 경로에 필요한 source family를 clone한다. 기본 권장은 법령(`legalize-kr`), 판례(`precedent-kr`), 행정규칙(`admrule-kr`)이고, 자치법규(`ordinance-kr`)는 파일 수가 커서 지역 규제 업무가 많을 때 선택한다. 이미 있으면 `git pull --ff-only`로 최신화를 시도한다. 경로를 바꾸려면 `BEOPSUNY_DATA_ROOT` 환경변수로 override.

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

법순이의 보조 자산은 **4개 레이어**로 분리되어 있다. 현행 법령·인허가·서식·기한은 번들 데이터에 저장하지 않고 공식 소스로 실시간 확인하며, 체크리스트와 후보 데이터는 조사 범위를 좁히는 용도로만 쓴다.

```
 ① 체크리스트 (진입점)  ──┐
                          │
 ② 데이터 (후보·용어) ───┼──► ③ 정책 (판정 로직) ──► 공식 소스 확인 ──► 검토 출력
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

### ② 데이터 — `assets/data/` (2 files)

계약 조항과 법률용어를 식별하기 위한 **후보·해석 보조 레퍼런스**. 현행 법령 ID, 인허가 요건, 공식 서식, 법정 기한은 번들 캐시로 두지 않고 공식 소스에서 실시간 확인한다.

| 파일 | 용도 |
|------|------|
| `clause_references.yaml` | 계약 조항 → 관련 법령 후보 매핑 (`triage_only`, live source 확인 전 결론 근거 아님) |
| `legal_terms.yaml` | 영한 법률용어 사전 |

### ③ 정책 — `assets/policies/` (5 files)

"어느 조항을 강행규정 위반으로 볼지", "어느 출처를 결론 근거로 받아들일지" 같은 **판정 로직**. 데이터와 분리돼 있어 독립적으로 갱신 가능.

| 파일 | 용도 |
|------|------|
| `mandatory_provisions.yaml` | 한국 강행규정 후보 인덱스 (약관규제법·민법·개인정보보호법·공정거래법·하도급법·근로기준법) |
| `review_mode.yaml` | 계약 검토 모드(`strict`/`moderate`/`loose`) 출력 스키마 |
| `source_grades.yaml` | 인용 소스의 출처 권위 라벨과 사용 가능성 기준 |
| `freshness_debt.yaml` | stale 번들 자산 registry. 등록 자산은 live source 확인 전 `triage_only` |
| `knowledge_manifest.yaml` | `beopsuny-knowledge` privacy manifest channel, asset key, checksum, usage-mode 소비 경계 |

### ④ 메모리/검증 스키마 — `assets/schemas/` (10 files, Full 모드 전용)

회사 프로필·과거 검토 이력을 기억해서 맥락 있는 답을 돌려준다. Chat 탭·zip 환경에서는 대화 단위로만 유지되므로 실질적으로 **Full 모드(Claude Code / Codex CLI)에서만 발휘**된다.

| 파일 | 용도 |
|------|------|
| `company_profile.yaml` | 회사 프로필 (업종, 규모, `interested_laws`, `party_position`) |
| `practice_profile.yaml` | 업무별 profile overlay (`contract`, `privacy`, `labor`, `regulatory`, `litigation`) |
| `legal_verification_packet.yaml` | Legal Verification Core의 authority packet, citation ledger, contradiction scan, conclusion binding 구조 |
| `freshness_metadata.yaml` | 번들 asset의 `next_review`, `last_verified`, `source_url`, `freshness_days`, `must_reverify` 공통 metadata 구조 |
| `freshness_revalidation.yaml` | stale 자산 갱신·retirement 전 공식 source 확인과 volatile item 검토 기록 |
| `output_contract.yaml` | 역할별 output mode와 destination별 법적 효과 gate 구조 |
| `internal_rules.yaml` | 사내 규정·결재 기준 |
| `past_reviews.yaml` | 과거 검토 이력 |
| `watched_laws.yaml` | 변경 감지 대상 법령 |
| `compliance_status.yaml` | 연간 컴플라이언스 이행 상태 |

## Acknowledgments

한국 법률 정보를 오픈 데이터로 만들어온 프로젝트들 위에 만들어졌다.

- **[legalize-kr](https://github.com/legalize-kr/legalize-kr)** — 대한민국 법령 전문을 Git으로 관리하는 오픈소스 (MIT). 공식 원문 기반 로컬 미러 데이터 소스
- **[admrule-kr](https://github.com/legalize-kr/admrule-kr)** — 고시·훈령·예규 등 행정규칙 Markdown (MIT). 공식 원문 기반 로컬 미러
- **[precedent-kr](https://github.com/legalize-kr/precedent-kr)** — 대법원/하급심 판례 Markdown (MIT). 공식 원문 기반 로컬 미러; 최신 개수는 upstream repo 확인
- **[ordinance-kr](https://github.com/legalize-kr/ordinance-kr)** — 조례·규칙 등 자치법규 Markdown (MIT). 공식 원문 기반 로컬 미러, 선택 설치 권장
- **[법망 (Beopmang)](https://api.beopmang.org/)** — 법령·행정규칙·해석례·의안·자치법규 discovery와 무인증 API
- **[korean-law-mcp](https://github.com/chrisryugj/korean-law-mcp)** — 법제처 API를 AI 친화적으로 래핑한 MCP (MIT). 헌재·행정심판·자치법규·조약까지 91개 도구
- **[국가법령정보센터 (law.go.kr)](https://www.law.go.kr/)** — 법제처 공식 서비스. 모든 법률 데이터의 원천

법령 텍스트는 대한민국 정부 공공저작물로서 자유롭게 이용할 수 있다.

## 라이선스

MIT
