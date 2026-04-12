# Changelog

## [0.2.2.1] - 2026-04-12

**테마: v0.2.2 post-release execution polish** — v0.2.2 릴리즈 직후 4 독립 리뷰 (codex gpt-5.4 / code-reviewer / silent-failure-hunter / comment-analyzer) 에서 합의된 P1 실행 문제 5건 + P2 2건 정리. 이전 릴리즈는 문서·정책 정합이 맞았으나 Full 모드 git 명령이 실제 구현 단계에서 한국어 경로 octal escape, SHA 누락, wrong-repo 실행, discovery 메타 부재 등의 이유로 실패할 수 있었음. **법령 조회 결과 정확성** 문제라 긴급 patch.

### Fixed
- `skills/beopsuny/SKILL.md` `## 법령 변경 감지` 섹션 — Full 모드 `git log --name-only` 에 `-c core.quotePath=false` 추가 (P1). 기본값 `core.quotePath=true` 로 한국어 경로가 octal escape (`kr/\352\260\234...`) 로 출력되어 법령명 추출 실패하던 버그 해소
- `skills/beopsuny/SKILL.md` 특정 법령 변경 내역 row — `git log -n 5 --follow kr/{법령명}/법률.md` + `git show` 가 `-C $DR/legalize-kr` 없이 작성돼 스킬 working directory 에서 wrong repo 로 실행되던 문제 수정 (P1). `git show` 에 명시적 `{SHA} --` 전달 포맷 추가 — bare `git show` 가 HEAD 를 반환해 선택된 커밋과 무관한 diff 를 요약하던 버그 해소
- `skills/beopsuny/SKILL.md` discovery row — `--name-only` 결과는 법령 리스트만 포함해 `개정일자`/`공포일자`/`시행일자`/`변경 조문` 메타를 hallucinate 할 여지 있었음 (P1). "각 법령마다 아래 row 로 재조회해 메타 추출" 명시 + 출력 포맷 bullet 의 3개 날짜 축에 **각각의 데이터 소스** 병기 (`git log 커밋 날짜`, `커밋 메시지`, `법률.md YAML frontmatter`)
- `skills/beopsuny/SKILL.md` Lite 모드 시간 범위 discovery 열 — 법망 API `law?action=history` 는 `id={법령ID}` 필수이므로 "직접 discovery" 불가 (P1). "사용자 지정 법령 or `interested_laws` 로 각각 `law?action=history&id={법령ID}`" 로 좁히고 `law?action=diff` 에도 `id={법령ID}` 필수 명시
- `skills/beopsuny/assets/schemas/company_profile.yaml` `interested_laws` 예시값 `"하도급거래 공정화에 관한 법률"` → `"하도급거래공정화에관한법률"` (P2). 자기 주석 ("legalize-kr 디렉토리명과 일치 — 띄어쓰기 없음") 을 위반해 copy-paste 시 lookup 실패하던 문제 해소
- `tests/scenarios/14_law_change_detection.yaml` `data_source` 주석 3곳 (law-change-01/02/04) — 정정된 명령·URL 반영 (quotePath flag, `-C` prefix, SHA 명시, `/api/v4/` prefix, `id={법령ID}` 필수)

### Added
- `skills/beopsuny/SKILL.md` `## 법령 변경 감지` 섹션 **실패 분기** 단락 신설 (P1). `git` non-zero exit, Lite API timeout/error, 법령명 ↔ 디렉토리명 mismatch 는 **"조회 실패" ≠ "개정 없음"** 으로 명시. `💡 "{법령명}" 조회 실패 — 데이터/법령명 확인 필요` 한 줄로 표시. 법률 맥락에서 "최근 개정 없음" 과 "조회 실패" 를 동일시하는 것은 material misrepresentation 이라 명시적으로 분기
- `skills/beopsuny/SKILL.md` `## 법령 변경 감지` 섹션 **응답 후단 append 순서** 단락 (P1) — 본문 → `🔍 자가 검증` 블록 → `💡 최근 개정: ...` 또는 `💡 조회 실패: ...` → 면책 고지. v0.2.2 에서는 "면책 고지 직전" 이 법령 변경 감지 append 와 자가 검증 블록 둘 다에 쓰여 상대 순서가 SKILL.md 내부에서 ambiguous 했음 — 이제 명시
- `skills/beopsuny/SKILL.md` `## 법령 변경 감지` 섹션 **모드 판별 backref** 한 줄 — 신규 섹션이 서두 "모드 판별 (Full / Lite)" 섹션의 `ls ~/.beopsuny/data/legalize-kr/kr/` 로직을 재사용함을 명시
- `skills/beopsuny/SKILL.md` `## 법령 변경 감지` 섹션 **경로 override 범위** 단락 (P2) — `${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}` override 가 이 섹션 한정 실험적 지원임을 명시. v0.2.2 에서 "경로 추상화 허용" 으로 포괄적 표현했으나 실제로는 모드 판별·데이터 초기화는 하드코딩 — drift 양성화. 전역 통일은 v0.3.0 예정
- `skills/beopsuny/SKILL.md` `## 법령 변경 감지` 섹션에 `$DR` 축약 도입 — Full 모드 명령 공통 prefix `${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}` 를 반복 노출 대신 축약
- `skills/beopsuny/assets/schemas/company_profile.yaml` `interested_laws` 주석에 mismatch 처리 포인터 추가 — "mismatch 시 '개정 없음' 이 아니라 '조회 실패' (SKILL.md 법령 변경 감지 → 실패 분기 참조)"
- `tests/scenarios/14_law_change_detection.yaml` `law-change-01` 에 `quote_path_flag` validation + `response_contains` 에 `core.quotePath=false` 검증

### Changed
- `.claude-plugin/plugin.json` 버전 `0.2.2` → `0.2.2.1` (최상위 및 `plugins[0]` 동시)

### Notes
- **SKILL.md 상한 재조정**: 724 → 730줄. 분리 트리거 800 미만 유지. v0.2.2 에서 합의됐던 725 상한을 법령 변경 감지 섹션의 실행 가능성(8줄 증가) 확보 위해 732 로 재조정. 전역 CLAUDE.md `SKILL.md < 800` 경계는 준수
- 새 태그 도입 없음. 기존 6개 태그 (`[VERIFIED]` / `[UNVERIFIED]` / `[INSUFFICIENT]` / `[CONTRADICTED]` / `[STALE]` / `[EDITORIAL]`) + Grade A/B/C/D 만 사용
- Push 경계 그대로 — 크론/알림/스케줄링 코드·문구 일절 없음
- 4 독립 리뷰 중 나머지 P2 (per_clause_override key contract, forbidden_phrases 자연 발화 패턴 보강, CHANGELOG "Push 없음" 중복, Dim 3 "갑/을 위치" legacy phrasing 등) 는 v0.3.0 이월
- 4 리뷰어 합의 findings: https://github.com/sungjunlee/beopsuny-skill/releases/tag/v0.2.2 참조

## [0.2.2] - 2026-04-12

**테마: 법령 변경 감지 (Law Change Detection)** — legalize-kr 의 `git log` 기반 pull 방식으로 "최근 뭐 바뀌었어?" 류 질의에 응답. 스케줄링/알림(Push) 설계는 외부 환경 의존성이 커서 제외 — **Push 없음, Pull 만**. Lite 모드는 법망 API `law?action=history` + `law?action=diff` fallback. 부록으로 v0.2.1 post-review P2 finding 2건 housekeeping 포함 (ship blocker 없음, 정확성 폴리시).

### Added
- `skills/beopsuny/SKILL.md` `## 법령 변경 감지` 섹션 신설 (#17)
  - 지원 질의 3종: 시간 범위 discovery / 특정 법령 변경 내역 / `interested_laws` 일괄
  - 모드별 명령·API: Full 은 `git log --since=` + `git show`, Lite 는 법망 API
  - 출력 포맷: 개정일자 / 공포일자 / 시행일자 (핵심 원칙 4 준수 — 공포 ≠ 시행) + 변경 조문 + legalize-kr 커밋 URL + law.go.kr
  - 응답 후단 append 규정: `interested_laws` 비어있지 않으면 본문 → 자가 검증 → `💡 최근 개정: ...` → 면책 고지 순서로 한 줄 append. 개정 없으면 생략
  - 경계: Push 금지 — 크론/알림 코드 없음
- `skills/beopsuny/assets/schemas/company_profile.yaml` `interested_laws: []` 필드 추가 (v0.2.2~). 법령명은 legalize-kr 디렉토리명과 일치
- `skills/beopsuny/assets/schemas/company_profile.yaml` `party_position` 필드 추가 (v0.2.2~) — #24 A안. `default: ""/"gap"/"eul"` + `per_clause_override: {}`. v0.2.1 에서 "스키마에 필드 없음" 으로 완화됐던 SKILL.md Step 4 항목 5 / Dim 4 서브체크 2 의 semantic dangle 자연 해소 (v0.2.1 post-review P2-3)
- `tests/scenarios/14_law_change_detection.yaml` 신설 — 4 시나리오
  - `law-change-01` — Full 모드 시간 범위 discovery
  - `law-change-02` — 특정 법령 (개인정보보호법) 변경 내역
  - `law-change-03` — `interested_laws` 응답 후단 append (Pull 경계)
  - `law-change-04` — Lite 모드 법망 API fallback
  - 공통 `forbidden_phrases`: `알림을 설정`, `크론`, `스케줄`, `notification`, `자동으로 알려드`, `푸시` — Push 뉘앙스 금지
- `tests/scenarios/13_contract_review.yaml` 상단 주석 블록 — `**foo**` 접두 (블록 헤더 존재 검증) vs plain substring (금지 패턴 뉘앙스 검증) 두 용도 구분 명문화 (PR #37, v0.2.1 post-review P2)
- `tests/scenarios/13_contract_review.yaml` `contract-19` forbidden_phrases 에 단일 소스 참조 포인터 주석 (PR #37)

### Fixed
- `tests/scenarios/13_contract_review.yaml` `contract-19` 의 `아래 문구로 교체하세요` → `아래 문구로 교체` — 단일 소스 `review_mode.yaml#counter_draft_forbidden_patterns` 와 drift 해소 (PR #37, v0.2.1 post-review P2-1)

### Changed
- `skills/beopsuny/SKILL.md` 회사 맥락 활용 예시에 2줄 추가 — `interested_laws: [...]` 가 후단 append 로 연결되는 로직, `party_position.default` 가 `negotiation_points` 우선 노출에 연결되는 로직
- `skills/beopsuny/SKILL.md` Step 4 항목 5 — "v0.2.x 스키마에 해당 필드가 없으므로 사실상 항상 양쪽 노출" → "`profile.yaml.party_position` (v0.2.2~) 에 맞춰 `gap`/`eul` 중 관련 관점 우선 노출. 조항별 override 는 `party_position.per_clause_override.{조항key}`"
- `skills/beopsuny/SKILL.md` Dim 4 서브체크 2 — `profile.yaml` 의 당사자 위치 → `profile.yaml.party_position` (v0.2.2~) 명시
- `tests/scenarios/13_contract_review.yaml` `contract-17` / `contract-18` 의 블록 헤더 검증용 `forbidden_phrases` — plain substring → **`**` prefix 앵커** (`"**협상 포인트**"`, `"**대체 문구 힌트**"`). 설명 prose 에서 단어 자연발생 시 false-positive 제거 (PR #37, v0.2.1 post-review P2-2)
- `.claude-plugin/plugin.json` 버전 `0.2.1` → `0.2.2` (최상위 및 `plugins[0]` 동시)

### Notes
- **Push 설계 없음 — pull 방식 유지**. 크론/알림/스케줄링/notification 코드·문구 일절 없음. `interested_laws` 있으면 응답 후단 한 줄 append 만
- 외부 의존성 0 — legalize-kr clone 이 이미 되어있다는 전제 (`~/.beopsuny/data/legalize-kr/`). Lite 모드는 기존 법망 API 만 사용
- 경로 추상화: `${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}` 로 environment variable override 허용
- #24 A안 포함 처리 — v0.2.1 에서 follow-up 으로 연기됐던 `party_position` 필드가 `interested_laws` 와 같은 스키마 파일 수정이므로 묶어서 처리
- 새 태그 도입 없음. 기존 6개 태그(`[VERIFIED]` / `[UNVERIFIED]` / `[INSUFFICIENT]` / `[CONTRADICTED]` / `[STALE]` / `[EDITORIAL]`) + Grade A/B/C/D 만 사용
- SKILL.md 703 → 724줄 (분리 트리거 800 미만, 상한 725 이하)
- Epic #13 종료. 다음 릴리즈는 v0.3.0 — DOCX 처리형 또는 후보 주제 재평가

## [0.2.1] - 2026-04-12

**테마: Review Polish** — v0.2.0 릴리즈 직후 세 독립 리뷰(code-reviewer / pr-test-analyzer / comment-analyzer) 에서 식별된 일관성·정확성·커버리지 이슈 7건을 다듬은 릴리즈. 동작 변경 없이 **flag 의미 ↔ 실행 경로 정합**, **단일 소스 통합**, **축 통일**, **정확성 보강** 에 집중.

### Fixed
- `clause_references.yaml` `non_compete.why_risky` — "~경향이 확립되어 있다" (단정적 표현) → "다수 판례가 ~ 무효로 판시한다". 경업금지는 사안별 종합판단 — Source Grading 환각 방지 원칙과 정합 (#28)
- `clause_references.yaml` `work_product.why_risky` — 저작권법 제9조 4요소 뒤에 **"(단, 계약·근무규칙에 다른 정함이 없는 때에 한함)"** 단서 추가. 외주 계약 실무 핵심 (#28)
- `contract_review_guide.md:23` 포인터 오류 — "수정안 자동 생성 금지" 원칙은 실제 `:21` 에 있음. SKILL.md 2곳 + `clause_references.yaml` 상단 주석 + `tests/scenarios/13_contract_review.yaml:438` 일괄 수정. 라인 번호 대신 **섹션 제목** 참조(`"법순이가 하지 않는 것"` 섹션) 로 전환 (#24)

### Added
- `review_mode.yaml` 신규 키 **`counter_draft_forbidden_patterns`** — Counter-drafting 자동 생성 금지 패턴 단일 소스, 총 18개 (#26)
  - 기존 SKILL.md Dim 4 서브체크 3 (4개) + `contract-16` (6개) 분산 관리 → 통합 + 확장 6개
  - 확장: `수정안:`, `변경안:`, `개선안:`, `확정안`, `권고 문구`, `대체 문언`, `다음과 같이 변경`, `아래와 같이 고치`, `아래와 같이 기재`, `바꾸어야 합니다`, `이렇게 바꿔`, `로 바꿔 넣으세요` 등
  - SKILL.md Dim 4 + `contract-16` 둘 다 이 키 참조
- `tests/scenarios/13_contract_review.yaml` 모드별 필터 회귀 시나리오 3건 — 시나리오 총합 **16 → 19** (#27)
  - `contract-17` — moderate 에서 `alt_wording_hint` 블록 부재 검증
  - `contract-18` — loose 에서 `negotiation_points` + `alt_wording_hint` 둘 다 부재 검증
  - `contract-19` — Dim 4 서브체크 3 실패 유도 → 힌트형 재작성 → 재검증 실패 시 필드 생략 관찰
- SKILL.md Dim 4 블록에 **미출력 필드 처리 규정** — "출력되지 않은 필드 대상 서브체크는 `n/a` (pass 집계). 판정식: 출력된 필드 대상 서브체크 전부 pass → ✓" (#25)
- SKILL.md 부분 실패 예시에 **맥락 캡션** 추가 (계약 검토 중 경업금지 조항 분석 + 힌트 출력 응답) — `Counter-draft ✓` 이유가 명확해짐 (#25)
- `references/self-verification.md` 신설 — 자가 검증 근거(Stanford 2025 등) append-only 아카이브. references 테이블에 한 행 추가 (#28)
- `tests/scenarios/13_contract_review.yaml` `contract-16` 에 `forbidden_phrases_source` 메타 키 — 단일 소스 참조 경로 표시 (#26)

### Changed
- `review_mode.yaml` `output.include_counter_drafting_hints` (단일 boolean) → **3 필드 분해** `include_why_risky` / `include_negotiation_points` / `include_alt_wording_hint` (#22)
  - 기존 단일 플래그는 "hint 를 낼지 말지" 의미였으나 SKILL.md Step 4 표는 모드별로 필드를 **차등 출력** 하도록 설계되어 불일치 → 3키 분해로 1:1 대응
  - strict: 3 키 모두 `true` / moderate: `why_risky` + `negotiation_points` `true` / loose: `why_risky` 만 `true`
  - SKILL.md Step 4 필터 표 헤더에 대응 flag 이름 괄호 표기, `clause_references.yaml` 상단 주석도 반영
- `clause_references.yaml` 7개 고위험 조항의 `negotiation_points.gap`/`.eul` **축 통일** (#23)
  - 축 정의: `gap` = 계약 상위 당사자 (발주자·위탁자·사용자·수요자), `eul` = 계약 하위 당사자 (공급자·수탁자·근로자·수행자)
  - `indemnification` / `limitation_of_liability` / `exclusion_of_damages`: gap↔eul swap (포인트 내용 바이트 보존, 라벨 위치만 교체)
  - 나머지 4개 (`work_product` / `data_processing` / `non_compete` / `invention_assignment`): 이미 축 일치 — 검증만
  - 상단 주석에 "gap/eul 축 정의" 블록 추가
- SKILL.md Dim 4 서브체크 3 — 단정 표현 목록을 인라인 4개 → `review_mode.yaml#counter_draft_forbidden_patterns` 참조 (#26)
- SKILL.md Step 4 항목 5 — 당사자 위치 fallback 기본값 문구 강화: `profile.yaml` 필드 부재 시 **양쪽 모두 노출** 이 기본값임을 명시 (v0.2.x 스키마에 필드 없음 — A안 스키마 신설은 후속) (#24)
- SKILL.md L526 — "Stanford 2025" 인라인 인용을 간결 본문 + `references/self-verification.md` 포인터로 재구성. 본문 rot 방지 (#28)
- `clause_references.yaml` 버전 앵커 주석 rot 완화: "(v0.2.0~, 위험도 high 우선 확장)" → "(현재 정책 — 확장 계획은 Epic/Issue 참조)" (#28)
- `review_mode.yaml` 버전 `1.0.0` → `1.1.0`
- `.claude-plugin/plugin.json` 버전 `0.2.0` → `0.2.1` (최상위 및 `plugins[0]` 동시)

### Notes
- **하위 호환**: moderate(default) + 비고위험 조항은 v0.1.3 과 동일한 출력. v0.2.0 에서 이미 유효했던 모드별 필터 의미가 flag 수준에서도 정합해졌을 뿐이며 사용자 응답 형식은 그대로
- 기존 51개 조항 key/value 바이트 동일 보존 — 7개 고위험 조항의 `negotiation_points` 는 라벨 위치 swap 만, 포인트 텍스트 보존
- 새 태그 도입 없음. 기존 6개 태그(`[VERIFIED]` / `[UNVERIFIED]` / `[INSUFFICIENT]` / `[CONTRADICTED]` / `[STALE]` / `[EDITORIAL]`) + Grade A/B/C/D 만 사용
- SKILL.md 700 → 703줄 (분리 트리거 800 미만, 720 목표 유지)
- CHANGELOG `[0.2.0]` Notes — SKILL.md 증가분 "+47" → "+48" 실측 정정 (#28 소급)
- Epic #21 종료. 다음 릴리즈는 v0.2.2 (법령 변경 감지, Epic #13)

## [0.2.0] - 2026-04-12

**테마: 계약 검토 심화 (Contract Review Depth)** — v0.1.3 에서 선언만 되어 있던 `review_mode.yaml` 의 `include_counter_drafting_hints: true` 를 실제 동작으로 연결. 위험 조항 발견 시 `why_risky` / `negotiation_points` / `alt_wording_hint` 3 필드를 모드별 필터로 출력한다. 자가 검증 레이어에 Dim 4 (Counter-drafting Quality) 가 조건부 차원으로 추가됐다.

### Added
- `assets/data/clause_references.yaml` 고위험(risk: high) 조항 7개에 counter-drafting 힌트 3 필드 추가 (#14)
  - `why_risky` (3줄 이내, 한국 강행규정·실무 기준)
  - `negotiation_points.gap` / `.eul` (갑/을 관점 2–3개씩)
  - `alt_wording_hint` (방향·원칙만, 완성된 수정안 아님)
  - 대상: `indemnification`, `limitation_of_liability`, `exclusion_of_damages`, `work_product`, `data_processing`, `non_compete`, `invention_assignment`
  - 파일 상단 주석에 "힌트 vs 자동 생성" 경계 명문화 (`references/contract_review_guide.md:23` 원칙 연계)
- `skills/beopsuny/SKILL.md` 계약서 검토 워크플로우 Step 4 에 **Counter-drafting 힌트 출력 로직** 추가 (#15)
  - 모드별 필터: `strict` → 3 필드 모두, `moderate` → `why_risky` + `negotiation_points`, `loose` → `why_risky` 만
  - `profile.yaml` 당사자 위치(갑/을) 기반 `negotiation_points.gap`/`.eul` 우선 노출
  - 조항당 출력 블록 포맷(이름/이슈/근거법령/why/negotiation/alt) 확정
- `tests/scenarios/13_contract_review.yaml` 회귀 시나리오 `contract-16` — "자동 생성 뉘앙스 금지" forbidden_phrases 스캔 + strict 모드 3 필드 출력 검증 (#15)
- 자가 검증 Phase 2 **Dim 4: Counter-drafting Quality** — 계약 검토 힌트 출력 응답에 조건부 적용 (#16)
  - 서브체크 1: `alt_wording_hint` 방향이 한국 강행규정(약관규제법 제7조, 민법 제103·393·398조, 발명진흥법 제15조, 저작권법 제9조, 개인정보보호법 제26조 등) 하에서 유효 가능한 범위인가
  - 서브체크 2: `negotiation_points.gap`/`.eul` 선택이 `profile.yaml` 당사자 위치와 일관되나
  - 서브체크 3: 단정적 자동 생성 표현 스캔 (`아래 문구로 교체`, `최종 수정안`, `다음 조항으로 대체`, `이 문구를 사용` 패턴 부재)
  - 실패 시 처리: 1/2 실패 → `[EDITORIAL]` 재태깅 + `downgrade_triggers` 발동. 3 실패 → 힌트형 재작성 후 재검증 (재검증 실패 시 해당 필드 출력 생략)
  - 메타데이터 라인에 `Counter-draft ✓ / ⚠ / n/a` 추가 (계약 검토 외 응답은 `n/a`)

### Changed
- `clause_references.yaml` 버전 `1.1.0` → `1.2.0` (스키마 확장)
- `.claude-plugin/plugin.json` 버전 `0.1.3` → `0.2.0` (최상위 및 `plugins[0]` 동시)

### Notes
- 기존 51개 조항 key/value 바이트 동일 보존 — 고위험 조항 7개에 **추가만** 수행
- 나머지 고위험 조항 15개 점진 확장은 v0.2.x 이후 예정
- 새 태그 도입 없음. 기존 6개 태그(`[VERIFIED]` / `[UNVERIFIED]` / `[INSUFFICIENT]` / `[CONTRADICTED]` / `[STALE]` / `[EDITORIAL]`) + Grade A/B/C/D 만 사용
- `contract_review_guide.md:23` "수정안 자동 생성 안 함" 원칙 v0.2.0 에서도 유지 — 힌트는 방향·원칙 서술, 완성 문구 확정은 사용자 몫
- SKILL.md 653 → 700줄 (분리 트리거 800 미만, 목표 720 이하 달성 — +48줄 증가분 내 Step 4 힌트 로직 +30, 자가 검증 Dim 4 +17, 기타 +1)
- Epic #12 종료. DOCX 처리형 주제는 v0.3.0 마일스톤으로 이전

## [0.1.3] - 2026-04-12

### Added
- `assets/policies/clause_taxonomy.yaml` 신설 — 계약 조항 분류·위험도 정책 파일
  - 5개 카테고리 (boilerplate, risk_allocation, ip_data, employment, core_terms) 정의
  - 3단계 위험도 (low/medium/high) 정의 + 판단 기준 (`classification_rules`) 신설
  - 신규 조항 추가 템플릿(`_template`)을 정책 쪽으로 이전
- `assets/policies/review_mode.yaml` 신설 — 계약 리뷰 엄격도 정책 (strict/moderate/loose)
  - 기본값 `moderate` (하위 호환 — 기존 사용자 경험 무변화)
  - 사용자 발화 힌트 기반 모드 감지 ("엄격히" → strict, "간단히" → loose)
  - 모드별 Phase 0 범위, 위험도 플래그 임계, Grade C 결론 허용 여부 차등화

### Changed
- `assets/data/clause_references.yaml` 슬림화 — 조항→법령 매핑 데이터만 유지
  - 51개 조항 key/값 바이트 동일 보존 (내용 무손실)
  - top-level `categories` / `_template` 제거 → `policies/clause_taxonomy.yaml` 로 이전
  - `taxonomy_ref` 필드 추가 (Claude 가 규칙 위치를 파일에서 직접 발견 가능)
- `skills/beopsuny/SKILL.md`
  - 번들 리소스 `assets/policies/` 테이블에 `clause_taxonomy.yaml`, `review_mode.yaml` 2행 추가
  - 계약서 검토 워크플로우 **Step 3.5 (리뷰 모드 판정)** 신규 삽입
  - Step 4 조항별 검토에 모드별 `risk_flagging.threshold` 적용 명시

### Notes
- 이슈 #4 **완전 close** — 잔여 2개 체크리스트(`clause_references.yaml` 분할 + `review_mode.yaml` 신설) 완료
- Epic #1 (3개 패턴 도입: Source Grading + YAML Policy 구조 + 자가 검증) 종료 단계
- 새 태그 도입 없음. 기존 6개 태그(`[VERIFIED]` / `[UNVERIFIED]` / `[INSUFFICIENT]` / `[CONTRADICTED]` / `[STALE]` / `[EDITORIAL]`)만 사용
- SKILL.md 620 → 653줄 (분리 트리거 800 미만, 목표 670 이하 달성)
- `plugin.json` 버전 bump 없음 — `[0.1.1]` / `[0.1.2]` 엔트리와 함께 다음 릴리즈 PR에서 일괄 반영

## [0.1.2] - 2026-04-12

### Changed
- `assets/` 디렉토리 구조 리팩터링 — 룰/데이터 분리 (kipeum86/contract-review-agent 패턴 일부 차용)
  - `assets/policies/` (룰·정책): `source_grades.yaml`, `checklists/*.yaml` 11종
  - `assets/data/` (레퍼런스 데이터): `law_index`, `compliance_calendar`, `clause_references`, `legal_terms`, `permits`, `forms`
  - `assets/schemas/` (메모리 스키마): 유지
- `skills/beopsuny/SKILL.md` 번들 리소스 섹션 — policies/ / data/ 서브테이블로 재구성
- `tests/scenarios/13_contract_review.yaml` reference_files 경로 13곳 업데이트

### Notes
- 이슈 #4 **부분 close**: 디렉토리 재구성 + 경로 참조 업데이트 완료
- **남은 작업** (follow-up): `clause_references.yaml` 분할(조항 분류 → policies/), `review_mode.yaml` 신설
- 커밋 2단계 분리: (1) `git mv` 순수 이동 (2) 경로 참조 업데이트 — 리뷰 시 rename 추적 명확화
- SKILL.md 611 → 620줄 (분리 트리거 800 미만)
- v0.2.0 멀티 스킬 분리 시 `${CLAUDE_PLUGIN_ROOT}/policies/` vs `/data/` 경계 준비

## [0.1.1] - 2026-04-12

### Added
- 자가 검증 레이어 Phase 1 — `skills/beopsuny/SKILL.md`에 `## 자가 검증 (응답 전)` 섹션 (60줄)
  - Dim 1 Citation: 조문 존재·조항 번호·취지 일치·판례 사건번호 형식 검증
  - Dim 2 Legal Substance: 전제-결론 연결·법률 위계·단서 조항·행정규칙 누락 검증
  - Dim 3 Client Alignment: 질문 본질 응답·실무 시사점·`profile.yaml` 맥락 반영 검증
- 검증 실패 → 기존 Source Grading 다운그레이드 트리거와 연동 (`downgrade_triggers`)
- 출력 메타데이터: 응답 끝에 `🔍 자가 검증: Citation n/n ✓ | Legal Substance ✓ | Client Alignment ✓` 표기

### Notes
- kipeum86/second-review-agent 7차원 중 답변 생성형에 유의미한 3개 차원만 적용 (Phase 2는 v0.2.0 이후)
- Stanford 2025 연구 대응: LexisNexis 1/6, Westlaw 1/3 할루시네이션 → 자가 검증이 업계 표준
- 새 태그 도입 없음. 기존 6개 태그(`[VERIFIED]` / `[UNVERIFIED]` / `[INSUFFICIENT]` / `[CONTRADICTED]` / `[STALE]` / `[EDITORIAL]`)만 사용
- SKILL.md 608줄 (분리 트리거 800 미만, 목표 620 이하)
- `plugin.json` 버전 bump 없음 — 다음 릴리즈(이슈 #4 YAML 리팩터링 이후)에 함께 반영

## [0.1.0] - 2026-04-12

### Added
- `DESIGN.md` (레포 루트) — 아키텍처 결정 기록 + Multi-skill 전환 트리거 로드맵
  - 단일 스킬 유지 결정(2026-04-12) 객관적 근거 4가지 기록
  - v0.2.0 분리 트리거: DOCX 처리, 스케줄링, 피드백 3회, SKILL.md 800줄 초과
- Source Grading A/B/C/D 체계 (kipeum86/PIPA-expert 패턴 차용)
  - `skills/beopsuny/assets/policies/source_grades.yaml` — 정책 파일 (policies/ 디렉토리 신규)
  - `skills/beopsuny/references/source-grading.md` — 사람이 읽는 규칙 문서
  - 핵심 원칙 6번에 Source Grading 추가
  - 출력 포맷 예시에 `[Grade X] [VERIFIED]` 태그 반영
  - 2차 소스 `[EDITORIAL]` 태그, `[INSUFFICIENT]` 유보 예시 추가

### Changed
- `skills/beopsuny/SKILL.md` 데이터 소스 섹션 재작성
  - 기존 모드별 우선순위 표에 Grade 컬럼 추가
  - 각 순위 소스별 기본 Grade 명시 (legalize-kr=A, 하급심=B, 법망 API=A, WebSearch=C/D 등)
  - WebSearch 백업 도메인별 Grade 매핑 추가
- 기존 `[VERIFIED]` / `[UNVERIFIED]` / `[INSUFFICIENT]` 태그는 **유지**하고 Grade와 병기

### Notes
- SKILL.md 548줄 (분리 트리거 800 미만)
- 기존 자산 경로 변경 없음 (이슈 #4에서 처리 예정)
- 자가 검증 레이어는 이슈 #5에서 후속 작업

## [0.0.3] - 2026-04-11

### Fixed
- 자동 clone 제거: 데이터 없으면 Lite 모드 진입, clone은 영속 환경(Claude Code, Codex CLI)에서만 권장
- Chat 탭 채팅마다 스토리지 초기화 확인 — ephemeral 환경에서 clone 무의미
- `--depth 1` shallow clone 명시적 금지 (git log 개정 이력에 전체 히스토리 필요)
- 한글 깨짐 수정

## [0.0.2] - 2026-04-11

### Added
- Chat 탭 Lite 모드: Claude Desktop Chat 탭과 Codex CLI에서 법순이 사용 가능
- 능력 기반 모드 판별 (Full/Lite) — 플랫폼이 아니라 로컬 데이터 접근 여부로 분기
- 법률 조사 워크플로우에 Full/Lite 컬럼 추가 (●/⬚ 표기)
- Lite 모드 시각화 가이드: Mermaid 다이어그램, HTML table 등 Artifacts 활용
- 메모리 운영 모드별 분기 (Lite: 구두 수집, 기록 생략)
- `docs/desktop-chat-guide.md`: Chat 탭 설정 가이드 + 독립 프로젝트 지침 템플릿
- CLAUDE.md에 프로젝트 구조 섹션

### Changed
- 데이터 소스 명령어를 Bash 우선으로 변경 (Codex CLI 호환)
- 데이터 소스 우선순위를 모드별 테이블로 재구성

### Removed
- Glob/Grep 네이티브 도구 의존 제거
- `mkdir -p` 직접 호출 제거 (setup.js가 담당)

## [0.0.1] - 2026-04-11

- 초기 릴리즈: 법령/판례 조사, 계약서 검토, 컴플라이언스 체크
