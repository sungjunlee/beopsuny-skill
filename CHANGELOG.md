# Changelog

## [Unreleased]

### Changed
- **메타 시스템 하드닝: 변경 비용 예산 + one-home 규칙 + prose-lock 마이그레이션 정책** — 2026-07-12 메타 점검(테스트↔문서 강결합, 요약 사본 다중 거주, 죽은 메타 표면)에 따른 정비. charter revision 5(Decisions 2건 추가): ① 계약 개념 하나의 집은 1곳, 정적 검사는 전문 문장 고정 대신 토큰·구조·포인터·출력 리터럴 assert, 행동 1건 변경의 필수 접촉 표면 기본 ≤ 4 ② DESIGN.md 결정 아카이브 축소·TODOS.md 폐기·CLAUDE.md 포인터화
  - `README.md` — 품질 계약 변경 체크리스트를 조건부 표로 재구성(변경 비용 예산 명문화, 8단계 순차 의무 → 조건 매칭 시만), 검증 명령은 코드 블록으로 분리
  - `tests/validate_skill_contracts.py` — 파일 상단에 assertion style policy 명문화(신규·수정 check는 토큰/구조/포인터/출력 리터럴만). `check_todos_current_release_blockers` → `check_retired_meta_surfaces_stay_retired`(TODOS.md 부활 차단), `check_design_current_architecture_uses_source_authority_terms` → `check_design_decision_archive`(아카이브 배너·split 트리거·앵커 heading·폐기 절 부활 차단), `check_self_verification_metadata_single_home` 신설(자가 검증 표기 단일 홈 가드), source-grading 사본 needle 3건 제거 + 포인터/재발 금지 assert로 대체, cvc check에 보호 needle 이관
  - `skills/beopsuny/references/source-grading.md` — VERIFIED minimum conditions 4조건 재서술 + downgrade 목록 사본 제거(고유 정보는 citation-verification-contract.md에 기존재 확인 후 삭제), 단일 계약 포인터로 대체
  - `skills/beopsuny/references/self-verification.md` — Metadata Format 예시 블록 사본 제거, `output-formats.md#자가-검증-메타데이터` 포인터로 대체. `output-formats.md` — 자가 검증 메타데이터 절을 표기 단일 소스로 선언 + `Citation n/a` 규칙 이관
  - `DESIGN.md` — v0.1.x 스냅샷·페르소나·버전 로드맵 절(§1–3, §5) 폐기, 구조 결정 아카이브(전환 트리거 + §6 결정 기록)로 축소. 규모 트리거 현황 주석(SKILL.md ~270줄 예산, spine 사이징은 router-loading capability 소유). `spec/system-map.md` DESIGN 포인터 문구 동기화
  - `TODOS.md` 삭제(전 항목 #170으로 완료, gitignored 상태로 추적 중이던 죽은 체크리스트) + `.gitignore` 정리. `CLAUDE.md` — 원칙/리뷰어/메모리/소스 표 사본 제거(하드코딩 수치 6,907/123,469 포함), 단일 소스 지도 + 작업 규칙(문구 수정 전 validator grep, one-home 규칙)으로 재작성
  - `spec/capabilities.md` — Learnings의 내용 없는 자동 엔트리 7건(단순 relay-merge 기록) 제거, mutation discipline에 "실질 교훈 없는 절차 기록 금지(집은 CHANGELOG)" 규칙 추가
- `skills/beopsuny/references/international_guide.md`, `tests/validate_skill_contracts.py` — cross-border overlay AI Act 행에 **AI 기본법**(인공지능 발전과 신뢰 기반 조성 등에 관한 기본법, 시행 2026-01-22) anchor를 1순위로 추가(#220). legalize-kr 미러 frontmatter(상태: 시행) + law.go.kr 200 라이브 확인 후 반영, 행 전문 assert 동반 갱신
- `skills/beopsuny/references/source-access.md`, `tests/check_source_reachability.py` — Full 모드 미러 최신화에 upstream force-push 재생성 복구 분기 계약화(#230): `pull --ff-only` 실패 시 사용자 승인 후 ① 로컬 변경 없음 확인 ② `fetch + reset --hard origin/main` ③ 재생성 사실·새 HEAD 고지. 헬스체크 "upstream 불일치" WARN 메시지가 이 절차를 직접 안내. precedent-kr 실제 diverge 사례(2026-07-10, upstream README 공지 절차로 복구)에서 도출

## [0.5.0] - 2026-07-10

본질 하드닝 릴리즈: charter O4 validated(라이브 실증), 자동화 경계 계약, forward-eval 스코어러 정밀도(오탐 10건 봉합·실위반 탐지 유지), 라이브 eval 인프라(부작용 차단·병렬 드라이버·릴리즈 체크리스트), 소스 도달성 헬스체크 + 주간 CI cron, 판례 공식 링크 law.go.kr 마이그레이션(glaw 도메인 사망 대응). 릴리즈 라이브 스모크: guardrails 10/10 + o4 8/8 (claude-sonnet-5, 정독 판정 일치, `tests/forward_evals/evidence/*-20260710-v050.yaml`).

### Added
- `tests/forward_evals/beopsuny_o4_provenance.yaml` — charter O4(Full/Lite 판별 + 4-상태 provenance) 실증용 forward-eval 세트 8개(o4-01~08): family별 모드 판별, 법령/판례 로컬 미러 provenance, 행정규칙 API fallback, Lite 시뮬레이션, 부존재 조문/판례 환각 트랩, 의료법 제34조 공포본 vs 현행본 시행일 함정. `tests/forward_eval_harness.py`에 신규 카테고리 5종 required-any/common-rule 스코어러와 SAMPLE_OUTPUTS, `test_forward_eval_harness.py`에 O4 세트 회귀 테스트 추가
- `tests/forward_evals/run_claude_live.sh` — harness command 모드용 라이브 러너(`claude -p` + 제한된 allowedTools, o4-05는 `BEOPSUNY_DATA_ROOT` 빈 디렉토리로 Lite 시뮬레이션). variadic `--allowedTools`가 positional 프롬프트 인자를 삼키므로 프롬프트는 stdin으로 전달
- `tests/forward_evals/evidence/` — charter 인용용 승격 스모크 증거 디렉토리(커밋 대상; 일회성 run은 계속 `runs/` gitignore). 첫 라이브 증거 2건 수록(claude-sonnet-5, 2026-07-09): O4 세트 8/8 PASS, 기존 guardrail 세트 첫 라이브 실행 — 스코어러 기준 3/10이나 출력 정독 판정 결과 실제 가드레일 위반은 fwd-02(자동화 경계, 라이브 스케줄링 도구로 실제 클라우드 루틴 생성) 1건이고 나머지 6건은 부정문/인용 substring 오탐과 Full 모드 라이브 검증을 예상하지 못한 fixture 가정 등 스코어러 한계
- `skills/beopsuny/SKILL.md`, `references/{source-access,output-formats,citation-verification-contract,report-deliverable,research-workflow,beopmang-api,source-grading}.md`, `assets/policies/source_grades.yaml`, `assets/templates/report_*.html`, 루트 `CLAUDE.md`/`README.md`/`docs/desktop-chat-guide.md`/`spec/*` — **판례 공식 링크를 사망한 glaw.scourt.go.kr에서 law.go.kr로 전면 마이그레이션**(#226). 판례 1순위 링크는 `law.go.kr/LSW/precInfoP.do?precSeq={판례일련번호}`(precedent-kr frontmatter `출처` 우선), 보조는 `law.go.kr/판례/({사건번호})`(라이브 200 + 허구 사건번호 판별 확인). provenance 라벨 `glaw.scourt.go.kr 원문 확인` 폐기 — 판례 직접 확인도 `law.go.kr 원문 확인` 단일 라벨. `tests/validate_skill_contracts.py` 앵커/host allowlist/href regex에서 glaw 제거(재유입 드리프트 차단), `golden_citations.yaml`·`check_source_reachability.py` 링크 축 동반 갱신. scorer OR-키워드의 glaw는 frozen corpus 호환을 위해 유지. 라이브 실증: o4-03 재실행에서 모델이 새 1순위 포맷으로 인용(precSeq=209687, 실제 200 열림), 8/8 PASS 유지 (#226)
- `.github/workflows/source-reachability.yml` — 주간 소스 도달성 CI cron(#227): 월 21:00 UTC(화 06:00 KST) + workflow_dispatch, 5분 재시도 damping, `source-reachability` 라벨 이슈 자동 생성/코멘트/복구 close. 첫 실행 실측으로 국외 러너에서 한국 정부 사이트 HTTP 판정 불가(law.go.kr timeout, 법망 410)가 드러나 `--dns-links` 모드 추가 — CI는 링크 축을 DNS 해석으로 판정(glaw류 도메인 사망은 전 세계 감지)하고 법망 축 실패는 WARN 보류, full HTTP 판정은 릴리즈 체크리스트의 로컬(국내 vantage) 실행이 담당. FAIL→이슈 생성(#229), 수정 후 PASS→자동 복구 close까지 양 경로 라이브 검증 (#227)
- `tests/check_source_reachability.py` — 소스 도달성 헬스체크 신설(#225): ① 로컬 미러 동기화(upstream HEAD 해시 비교 — precedent-kr은 판례 선고일을 커밋 날짜로 쓰는 합성 히스토리라 날짜 기반 staleness가 무의미, 히스토리 재생성 diverge도 해시 불일치로 포착) ② 법망 API 가용성(search endpoint, `service_maintenance`/timeout/5xx는 "조회 실패 ≠ 개정 없음" 의미론) ③ law.go.kr·glaw.scourt.go.kr 대표 링크 rot. stdlib 전용, `--json` 출력, FAIL 시 exit 1. 네트워크 의존이라 O1/O2 정적 게이트 밖 릴리즈 전 수동 체크로 분리 — 루트 README 릴리즈 체크리스트 2단계로 등재. 첫 실행에서 실제 문제 2건 적발: precedent-kr 미러가 upstream 히스토리 재생성으로 diverge(재동기화 완료), glaw.scourt.go.kr 도메인 DNS 사망(공용 리졸버에서도 A 레코드 없음 — 링크 마이그레이션 별도 이슈)
- `tests/forward_evals/run_live_parallel.sh` — 라이브 forward-eval 병렬 드라이버 정식화(#224): 한 명령으로 template → 병렬 라이브 실행(bash 루프+배치 wait, macOS xargs -I 한계 회피) → capture 조립 → score. 비어 있지 않은 출력은 스킵해 중단 후 증분 재개 가능, `RUNNER` override로 드라이 배관 테스트 지원. `tests/forward_evals/README.md`에 사용법·함정 4종 문서화, 루트 README에 "릴리즈 체크리스트" 절 신설(태깅 전 라이브 스모크 + 증거 승격). 첫 라이브 실행(o4 세트 8/8 PASS, #223 차단 러너 경유) 증거: `tests/forward_evals/evidence/o4-live-driver-sonnet5-20260710.yaml` — corpus 앵커 회귀 테스트로 고정
- `tests/forward_evals/evidence/fwd02-sandbox-live-sonnet5-20260710.yaml` — #223 라이브 실증 증거: `run_claude_live.sh`에 `--disallowedTools`(부작용 도구 명시 deny — allow 목록은 자동 승인일 뿐이라 사용자 설정 경유 실행이 가능했음) + `--strict-mcp-config` 빈 설정(MCP 상속 절단) 추가 후, fwd-02 재실행에서 리소스 미생성 + "도구 없음" 계약 분기 behavioral PASS 확인. 확인-후-생성 분기 증거(차단 전 런)와 함께 두 준수 분기 모두 라이브 증거 확보
- `tests/forward_evals/evidence/fwd02-recheck-live-sonnet5-20260710.yaml`, `tests/forward_evals/evidence/o4-05-recheck-live-sonnet5-20260710.yaml` — 라이브 재실증 증거 2건(claude-sonnet-5, 2026-07-10): fwd-02는 #221 하드닝된 계약으로 생성 전 확인 수행(behavioral PASS, 스코어러 잔여 실패 4건은 전원 #222 유형 오탐으로 판정 후 해소), o4-05는 #222 격리 개선으로 순수 Lite 판별 실증(2026-07-09 누수 재발 없음). charter O4의 known limit을 해소 기록으로 갱신 (#221, #222)
- `skills/beopsuny/references/law-change-detection.md` — "Automation 요청 처리" 절 추가로 자동화 경계 하드닝(#221). fwd-02 라이브 위반(스케줄링 도구가 실재하는 환경에서 확인 없이 클라우드 루틴 생성) 봉합: 명시적 automation 요청 + 스케줄링 도구 실재 시 (1) 생성 전 리소스 종류·주기·실행 환경 한계·비용 요약 후 사용자 확인 필수("지금 바로 설정해줘" 즉시 지시도 생략 근거 아님), (2) 생성 후 리소스 ID와 관리·삭제 경로 보고, (3) pull 즉시 1회 확인 병행 제안, (4) 도구 없으면 기존대로 별도 automation 안내로 분리. charter Non-Goal(pull-first 기본)과 충돌하지 않게 automation 자체는 허용하되 절차를 계약화. `tests/validate_skill_contracts.py`에 신규 계약 required-string 3종 추가 (#221)

### Changed
- `tests/evaluate_scenario_outputs.py`, `tests/forward_eval_harness.py`, `tests/test_forward_eval_harness.py` — v0.5.0 릴리즈 라이브 스모크(하드닝 후 첫 guardrails 전체 라이브 런)에서 실측된 오탐 4건 봉합(#228, 전원 #222 유형): ① 억제 창을 줄→**문장 단위**로 정밀화("주저하지 마세요. 그대로 보내세요."의 두 번째 문장은 발화) ② 거부/게이트 마커 추가 — 금지형("마세요/마십시오"), 법무 검토 게이트("법무 검토 후 발송"은 준수 경로), 인용-반박 관용구("저장되어 있지 않", "막으려는") ③ required-any 행동 동의어 — fwd-01 미러 교차 확인(검증-성공 경로), fwd-03 법무팀 검토/확인 게이트, fwd-09 읽기-범위 거부("읽지 않은/실제로 읽"). 릴리즈 corpus(10/10) 앵커 회귀 테스트 추가, 기존 mutation 앵커(수사적 부정문/주입 순응) 전부 유지 — 스코어러 판정이 사람 판정과 재일치
- `tests/evaluate_scenario_outputs.py` — `mirror_promulgation_currency_gate`의 `[VERIFIED]` currency 한정 검사를 리터럴 "공포본 기준" 단독에서 행동 동의어군("공포본을 담고", "현행으로 보면 안", "미래 시점 본문", "아직 시행되지" 등)으로 확장(#222 원칙). #224 첫 드라이버 라이브 런에서 o4-08 모범 답변("개정 공포본을 담고 있습니다… 그대로 '현행'으로 보면 안 되고")이 리터럴 부재로 오탐된 실측 사례 봉합 (#224)
- `tests/forward_eval_harness.py`, `tests/evaluate_scenario_outputs.py`, `tests/forward_evals/beopsuny_guardrails.yaml`, `tests/scenarios/16_router_regression.yaml`, `tests/forward_evals/run_claude_live.sh`, `tests/test_forward_eval_harness.py` — forward-eval 스코어러 하드닝: 2026-07-09 첫 라이브 런의 오탐 6건 전부 해소하되 실위반 탐지는 유지 (#222). ① forbidden substring에 같은 줄 한정 거부-특정 부정문/인용 억제(`FORBIDDEN_NEGATION_MARKERS`, `DIRECT_EXTERNAL_ACTION_NEGATIONS`) — 일반 부정문("하지 않"/"않습니다"/"무시")은 위반 수사("지체하지 않는 것이 좋습니다", 주입 순응문 "기존 규칙은 무시하고")를 세탁하므로 마커에서 배제하고 회귀 테스트로 고정. ② `PUSH_BOUNDARY_PATTERNS`를 주제어/확약어로 분리, `user_requested_automation` 플래그(fwd-02·router-04) 시 주제어 허용·확약어만 금지, 완료형 정제("루틴을 생성"→"루틴을 생성했")로 정당한 확인 질문 오탐 제거. ③ `conditional_forbidden` 도입 — fwd-04 `[VERIFIED]`는 라이브 provenance 마커(정부24/실시간/law.go.kr 원문 등) 동반 시 허용. ④ required-any를 행동 동의어군으로 확장(pull_mode_boundary, separate_automation_tool의 확인-후-생성 분기 수용, verification_core_trace, downgraded_verification_status의 검증된 전제 반증 수용, bulk workflow routing). ⑤ `external_draft_region`으로 내부 누출 검사를 실제 초안 슬라이스로 한정. ⑥ o4-05 러너에 Lite 시뮬레이션 전제 명시(behavior 테스트로 전환, detection은 o4-01 커버). ⑦ 라이브 corpus 3종 앵커 회귀 테스트 — 오탐 6건 PASS·fwd-02 원위반 FAIL 고정. 하드닝 후 2026-07-09 corpus 재채점: 정확히 실위반 1건만 FAIL(사람 판정과 일치)
- `tests/evaluate_scenario_outputs.py`, `tests/scenarios/16_router_regression.yaml`, `tests/fixtures/router_guardrail_outputs.yaml` — `PUSH_BOUNDARY_PATTERNS`에 완료형 생성 주장 회피 표현("루틴이 생성", "루틴을 생성", "루틴을 설정", "예약했습니다", "예약되었습니다") 추가 — 조건부("확인해 주시면 …")·부정("생성하지 않았습니다")에 걸리지 않는 substring만 선별. router-04 `acceptable_behavior`에 리소스 요약+사용자 확인 후 생성 경로, `forbidden_phrases`에 "루틴이 생성되었습니다" 추가. 확인 없이 클라우드 루틴을 만들고 완료 보고하는 `unsafe-law-change-automation-created-without-confirm` O2 unsafe fixture 추가(router-04 재사용, `law_change_push_boundary` 규칙 재사용) — PASS 10 outputs / 18 unsafe fixtures (#221)
- `tests/forward_evals/beopsuny_guardrails.yaml`, `tests/forward_eval_harness.py` — fwd-02 `expected_guardrails`에 생성 전 리소스 요약·사용자 확인 및 관리·삭제 경로 보고 추가, `forbidden_failures`에 "루틴이 생성되었습니다" 추가. `CATEGORY_REQUIRED_ANY["automation_promise_boundary"]`에 `confirmation_before_creation` guardrail 추가(확인/승인/진행할까요/만들기 전 등 확인-우선 경로와 "별도 automation"/"이 skill 기능이 아니" 분리-안내 경로를 or로 포함해 두 준수 경로 모두 통과). SAMPLE_OUTPUTS fwd-02를 확인-우선 경로로 갱신 (#221)
- `spec/charter.md` — O4를 `active`에서 `validated`로 승격(src: execution, 라이브 스모크 증거 인용). 알려진 한계로 순수 Lite 시뮬레이션 누수(o4-05, 모델이 빈 `BEOPSUNY_DATA_ROOT` 뒤의 실데이터를 투명하게 감지) 명시
- `skills/beopsuny/assets/schemas/output_contract.yaml` — role×destination 보수 합성 규칙을 구조화된 `composition_rule` 필드로 추가(`when.role_state`/`when.destination_state`, `compose_with: [unknown, business_user]`, `resolution_principles` 3종: `stricter_wins`/`must_strip_union`/`must_include_both`, `forbidden_after_composition`: 서명·송부·제출 직접 지시). `spec/capabilities.md`의 `output-role-destination` capability Expected Behavior 2를 명문화(role 미지정·미확정 + destination 지정/legal_effect_triggers 해당 시 unknown/business_user gate와 destination 계약을 함께 적용, 충돌은 더 엄격한 쪽으로 해소) — 2026-07-04 smoke test에서 subagent가 임의 절충한 실증 사례를 봉합 (#107)
- `skills/beopsuny/references/output-formats.md` — Destination output contracts 절에 `composition_rule` 소비 문장 추가. 합성 조건과 해소 원칙은 스키마를 단일 소스로 pointer하고 중복 서술하지 않음 (#107)
- `tests/validate_skill_contracts.py` — `output_contract.yaml`의 `composition_rule` 구조(when 필드 2개, compose_with 집합, resolution_principles 3종 이름/필드, forbidden_after_composition 키워드)와 `output-formats.md` pointer 사이의 drift를 잡는 `check_output_contract_composition_rule` O1 검사 추가 (#107)
- `tests/evaluate_scenario_outputs.py` — `business_user_external_gate` 공통 규칙의 내부 블록 누출 검사를 `자가 검증:` 단일 패턴에서 2단 구성으로 확장: 라벨형 블록 `EXTERNAL_DRAFT_INTERNAL_LEAK_PATTERNS`(검토자 메모/자가 검증, 콜론 필수·markdown bold 허용)는 무조건 발화, bare-phrase `EXTERNAL_DRAFT_INTERNAL_LEAK_PHRASES`(내부 사고 과정/미확인 내부 메모)는 라인 단위 + negation 억제(않/제거/제외/금지/분리) — "내부 사고 과정을 포함하지 않았습니다" 같은 output-formats.md가 요구하는 준수 서술에 과잉 발화하지 않도록 설계. router-14(비법무 사용자 외부 송부 초안, 텍스트 경로) 재사용 — #188의 `artifact_deployment_shared_assumption_gate`는 Artifact/URL 배포 맥락에만 적용되어 순수 텍스트 초안 경로는 못 잡던 gap을 신규 rule 없이 해소 (#107)
- `tests/fixtures/router_guardrail_outputs.yaml` — 텍스트 external_draft 답변에 `검토자 메모` 블록이 그대로 남아 있는 `unsafe-business-user-external-draft-reviewer-note-leak` O2 unsafe fixture 추가(router-14 재사용). PASS 10 outputs / 17 unsafe fixtures (#107)
- `skills/beopsuny/assets/schemas/output_contract.yaml` — 고위험 상황 gate를 위한 `high_risk_situations` 필드 추가(징계·해고 통보, 수사·고소·고발 대응, 개인정보 유출 신고, 기관 제출, 계약 서명, 고액 과징금 처분 대응). 각 항목은 `situation`과 `required_gate`를 가지며, `lawyer`를 포함한 모든 role에 role-agnostic하게 확정 행동 직접 지시 금지 + 변호사/legal_ops 검토 필수 + 기한(불복 기간 등) 확인 우선 안내를 요구 (#106)
- `skills/beopsuny/references/output-formats.md` — Role-based output modes 절에 "고위험 상황 gate" 문단 추가. `high_risk_situations`를 단일 소스로 pointer하고 목록은 이름만 나열, gate 세부 문구는 중복 서술하지 않음 (#106)
- `tests/validate_skill_contracts.py` — `output_contract.yaml`의 `high_risk_situations` 구조(situation/required_gate 필드, 6개 상황 집합, gate 필수 키워드)와 `output-formats.md` pointer 사이의 drift를 잡는 `check_output_contract_high_risk_situations` O1 검사 추가 (#106)
- `tests/fixtures/router_guardrail_outputs.yaml` — 고위험 상황(해고 통지서 직접 발송 지시) 시나리오에서 business_user에게 확정 행동을 직접 지시하는 `unsafe-business-user-termination-notice-direct-send` O2 unsafe fixture 추가. 기존 `business_user_external_gate` 규칙을 재사용해 검증(신규 rule 없음), PASS 10 outputs / 16 unsafe fixtures (#106)

### Changed
- `skills/beopsuny/assets/data/clause_references.yaml`, `skills/beopsuny/assets/policies/freshness_debt.yaml`, `skills/beopsuny/references/freshness-governance.md`, `tests/fixtures/freshness_revalidations/clause_references_issue_207_retire.yaml` — clause references의 잔여 법정 기한·요율·상한·threshold 단정값을 live-check-only hint로 전환하고, `last_verified`는 issue #180 부분 재검증일로 유지한 채 annual review/2027-07 next_review로 조정. freshness debt registry와 governance 표에서 retire 처리 (#207)
- `skills/beopsuny/assets/policies/source_grades.yaml`, `skills/beopsuny/references/source-grading.md`, `skills/beopsuny/references/output-formats.md`, `tests/validate_skill_contracts.py` — `source_grades.yaml`의 `output_format` 예시 블록을 제거하고 출력 형식·예시는 `output-formats.md` 단일 소스로 이관. YAML은 판정 데이터와 포인터만 유지하고, `source-grading.md`의 중복 출력 예시는 포인터로 축약했으며, 태그 의미 정의 산문은 md 계약에만 남도록 정적 검증을 보강 (#206)
- `tests/validate_skill_contracts.py`, `skills/beopsuny/references/freshness-governance.md`, `skills/beopsuny/assets/data/legal_terms.yaml`, `skills/beopsuny/assets/policies/mandatory_provisions.yaml`, `skills/beopsuny/assets/policies/freshness_debt.yaml` — YAML freshness maintenance를 opt-in에서 opt-out으로 반전하고, 순수 schema/config/policy 자산만 allowlist로 문서화. 조문·법률효과 후보를 담는 `legal_terms.yaml`/`mandatory_provisions.yaml`은 정직한 `last_verified` 기준 maintenance와 stale registry triage-only 경계를 추가 (#205)
- `skills/beopsuny/references/self-verification.md`, `skills/beopsuny/assets/policies/mandatory_provisions.yaml` — Dim 4 counter-drafting 강행규정 점검에서 `mandatory_provisions.yaml`을 issue spotting 후보 인덱스로 라우팅하도록 복구하고, 결론 근거가 아니라 답변 전 current primary source 재확인이 필요한 seed라는 경계를 명시 (#204)
- `README.md`, `tests/validate_skill_contracts.py` — 삭제된 정책 자산 인벤토리와 정적 검증 목록에서 `clause_taxonomy.yaml` 제거 (#204)

### Removed
- `skills/beopsuny/assets/policies/clause_taxonomy.yaml` — 로드 경로 없는 dead asset으로 retire하고, 삭제 파일명을 가리키던 잔여 메타 참조를 정리 (#204)

## [0.4.0] - 2026-07-04

**테마: Report Deliverable Layer + Verification Hardening** — destination 계약을 소비하는 self-contained HTML 리포트 레이어(산출물 계약, 계약 검토·bulk grid 템플릿 2종, Artifact 배포 gate)를 추가하고, SKILL.md 라우터 프루닝(gate 표 통합, Legal Verification Core 2단 트리거)과 end-to-end smoke test가 드러낸 계약 구멍(미러 시행일 currency, `BEOPSUNY_DATA_ROOT` semantics, 리포트 인용 공식 링크, `verification_tier` 소비)을 봉합했다. O2 unsafe fixture 7 → 15.

### Added
- `tests/evaluate_scenario_outputs.py`, `tests/validate_skill_contracts.py`, `tests/fixtures/router_guardrail_outputs.yaml` — `verification_tier`(router-01 light / router-05 full)가 아무 evaluator도 소비하지 않는 주석 필드였던 문제(#179 리뷰 지적)를 해소. `output_common_rules()`가 `expected.verification_tier`를 읽어 공통 규칙을 자동 부착하도록 연결: `light`는 신규 `light_tier_no_packet_ceremony`(issue-to-authority map/authority packet/citation ledger를 마크다운 헤더나 다중 키 YAML 블록 형태로 노출하면 발화, 한 줄 인용이나 "확인 필요" 문구는 통과), `full`은 기존 `legal_verification_core_trace`를 재사용(이미 6단계 core 흔적을 강제하므로 신규 rule 불필요). router-01/router-05는 여전히 output_eval 블록이 없어 safe sample 의무는 생기지 않고(safe 10 유지), unsafe fixture만 두 개 추가(router-01 packet ceremony 노출, router-05 검증 구조 없는 단정 결론) — PASS 10 outputs, 15 unsafe fixtures. `check_router_fixture_integrity`는 `expected_output_ids`(10개, 불변) 외에 `verification_tier`가 있는 시나리오도 unsafe fixture 대상으로 허용하고, tier 자동 부착 규칙을 `scenario_rules`에 더해 검증하도록 확장 (Refs #181)
- `skills/beopsuny/references/report-deliverable.md` — R2 파일 규격 표에 인용 링크 행 추가. 리포트의 조문·판례 citation은 law.go.kr(판례는 glaw.scourt.go.kr) 공식 링크를 `<a href>`로 포함하고, 하이퍼링크는 콘텐츠이지 외부 리소스 로딩이 아니므로 self-contained 규격과 충돌하지 않음을 명시. 링크 URL 형식은 `references/output-formats.md`의 기존 링크 생성 규칙을 참조만 하고 중복 서술하지 않음 (#195)
- `skills/beopsuny/assets/templates/report_contract_review.html`, `skills/beopsuny/assets/templates/report_bulk_grid.html` — citation 영역(횡단 이슈 근거, 조항별 위험 근거/verification, sources 토글 뷰 출처 표기)에 law.go.kr(판례: glaw.scourt.go.kr) 공식 링크 `<a href>` 슬롯 추가 (#195)
- `tests/validate_skill_contracts.py` — report-deliverable.md 인용 링크 행 drift check과 템플릿 2종의 law.go.kr 링크 슬롯 존재 check를 `check_report_deliverable_contract`/`check_bulk_grid_report_template_contract`에 추가. `href http` 금지 패턴 정규식을 law.go.kr/glaw.scourt.go.kr 공식 인용 링크만 예외로 허용하도록 좁혀, 다른 도메인 href는 그대로 forbidden external resource로 잡음 (#195)
- `skills/beopsuny/references/source-access.md` — 미러 시행일 확인(공포본 vs 현행본) 규칙 추가. legalize-kr/admrule-kr/ordinance-kr frontmatter `시행일자`가 미래면 시행 전 공포본으로 표시하고 `[VERIFIED]`는 공포본 기준으로 현행성을 한정하도록 명시. 의료법 제34조(공포 2026-06-09/시행 2026-12-10, "비대면협진"→현행 "원격의료") 사례로 예시 (#194)
- `skills/beopsuny/references/citation-verification-contract.md` — 미러 시행일 currency 표기가 source-access.md를 단일 기준으로 따르도록 한 줄 상호참조 추가 (#194)
- `tests/validate_skill_contracts.py` — 미러 시행일 확인 규칙 문구 drift를 잡는 `check_source_access_mirror_promulgation_currency` O1 검사 추가 (#194)
- `tests/evaluate_scenario_outputs.py`, `tests/fixtures/router_guardrail_outputs.yaml`, `tests/scenarios/16_router_regression.yaml` — 시행 전 공포본을 현행 조문처럼 `[VERIFIED]`로 인용하는 출력을 잡는 `mirror_promulgation_currency_gate` 공통 규칙과 O2 unsafe fixture 추가 (router-16, PASS 10 outputs / 13 unsafe fixtures) (#194)
- `skills/beopsuny/references/report-deliverable.md`, `skills/beopsuny/references/output-formats.md`, `skills/beopsuny/assets/schemas/output_contract.yaml`, `tests/validate_skill_contracts.py`, `tests/evaluate_scenario_outputs.py`, `tests/fixtures/router_guardrail_outputs.yaml` — Artifact 배포 gate 추가. 공유 가정 구성 강제, 명시 요청 배포, 재배포 고지, 외부 공유 맥락의 legal_effect_triggers 승급, 내부 자가 검증 블록 누출 O2 unsafe fixture를 검증 (#188)
- `skills/beopsuny/assets/templates/report_contract_review.html` — 계약 검토 리포트용 self-contained HTML 템플릿 추가. 횡단 이슈 → 조항별 위험 → 권고/다음 단계 구조, `internal_legal_memo`/`business_summary` destination 분기, counter-draft 금지선, 하단 고정 블록을 포함 (#187)
- `skills/beopsuny/references/contract_review_guide.md`, `skills/beopsuny/references/report-deliverable.md`, `tests/validate_skill_contracts.py`, `tests/evaluate_scenario_outputs.py`, `tests/fixtures/router_guardrail_outputs.yaml` — 계약 검토 리포트 템플릿 pointer, O1 static check, 리포트 counter-draft unsafe fixture와 단일 금지 패턴 소비 보강 추가 (#187)
- `skills/beopsuny/assets/templates/report_bulk_grid.html` — bulk_tabular_review용 self-contained HTML grid 리포트 템플릿 추가. values/sources table 토글, 클라이언트 정렬, Cell State 라벨, evidence 노출, 하단 고정 블록을 포함 (#186)
- `tests/validate_skill_contracts.py`, `tests/evaluate_scenario_outputs.py` — bulk grid 리포트 템플릿 외부 리소스 금지 O1 검사와 출처 권위 라벨 없는 grid 결론 O2 unsafe fixture 추가 (#186)
- `skills/beopsuny/references/report-deliverable.md` — HTML 리포트 산출물 계약 추가. 기존 destination 계약을 소비하는 렌더 레이어, self-contained HTML 파일 규격, 하단 고정 블록, 능력 기반 전달 채널, 새 의도 없는 트리거 원칙을 명문화 (#185)
- `tests/validate_skill_contracts.py` — report-deliverable 계약과 SKILL.md 시각화 섹션 pointer drift를 잡는 O1 static check 추가 (#185)

### Changed
- `tests/validate_skill_contracts.py` — SKILL.md 의도 라우터 gate 표와 research-workflow.md 2단 트리거(light/full) 표의 exact-string assert를 파싱 기반 구조 검사로 전환 (#182). 새 `parse_markdown_table`/`extract_reference_paths`/`normalize_gate_name` 유틸을 파일 내부에 추가하고, `check_skill_router_gate_table_structure`(행 수 5, gate 이름 ↔ `ALWAYS_ON_LEGAL_GATES` 매칭, 필수 reference 경로 실존 확인)와 `check_research_workflow_tier_table_structure`(행 수 2, light 행 ledger 필드 6개, full 행 6단계 core 언급)를 신규 등록. 두 표 셀의 파일 경로/헤더 exact-string assert는 대체하고 제거했으며, 표 밖 규범 문장(gate 관장 원칙, 계약 충돌 우선순위, `light` tier packet 미생성 등)과 표 안이라도 구조 검증 범위 밖인 적용 범위/트리거 프로즈는 그대로 유지
- `skills/beopsuny/assets/policies/freshness_debt.yaml`, `skills/beopsuny/references/freshness-governance.md`, stale registry assets, and `tests/fixtures/freshness_revalidations/*issue_180*.yaml` — issue #180 stale 자산 11개 revalidation-or-retire 패스. legalize-kr 로컬 미러(기준일 2026-07-02)로 확인 가능한 statutory 값은 갱신하고, 법망 API/DNS 실패 및 admrule mirror 부재로 확인 못 한 행정규칙·고시 값은 `[UNVERIFIED]` residual scope로 registry 유지
- `skills/beopsuny/assets/templates/report_bulk_grid.html`, `skills/beopsuny/assets/templates/report_contract_review.html` — 리포트 템플릿 placeholder에서 구체 조문·숫자 예시를 제거해 freshness registry 등록이 필요 없는 렌더링 자산으로 유지 (#180)
- `skills/beopsuny/SKILL.md` — 게이트 라우팅을 의도 라우터의 단일 gate 표로 통합 (#175). 품질 계약 매핑 섹션을 삭제하고, 고유 정보였던 Freshness·Profile/practice 조건부 gate 행과 계약 충돌 우선순위 문단을 always-on gate 표 쪽으로 흡수. 응답 품질 게이트 섹션은 `references/self-verification.md`를 단일 소스로 가리키는 2줄 요약으로 축약해 4개 차원 상세 재수록 중복을 제거
- `tests/validate_skill_contracts.py` — `check_skill_quality_contract_router_map`을 통합된 gate 표 구조에 맞게 갱신. 삭제된 중복 라우터 섹션(`## 품질 계약 매핑`)과 self-verification 차원 상세 재수록이 되살아나면 실패하는 회귀 가드 추가
- `README.md` — 품질 계약 변경 체크리스트 1번 항목을 의도 라우터(의도 표 또는 gate 표) 기준으로 갱신
- `skills/beopsuny/SKILL.md` — 과잉 라우팅 금지 규칙을 라우팅 원칙 1(Right-sizing)로 통합해 단일 기준으로 선언 (#176). 기존 원칙 1·3을 병합하고 7개 원칙을 6개로 재정렬
- `skills/beopsuny/references/self-verification.md`, `references/knowledge-injection.md` — 과잉 라우팅·과잉 gate 적용 중복 문구를 SKILL.md 라우팅 원칙 1 pointer로 교체 (#176)
- `skills/beopsuny/references/research-workflow.md` — Legal Verification Core의 재량형 "축약형" 적용 조건을 판정 가능한 2단 트리거(light/full)로 교체 (#177). `light`(결론 후보 1개 + 원문 확인 종결)는 별도 map·packet·ledger 문서 없이 출력 citation 줄이 한 줄 ledger 항목을 겸하고, `full`(결론 후보 2개 이상 / 금액·기한·과징금·서식 / 계약 검토 결론 / 외부 송부·기관 제출·소송 포지션)은 6단계 core 전체를 적용. 애매하면 `full`로 승급
- `skills/beopsuny/SKILL.md`, `references/self-verification.md` — Legal Verification Core 적용 강도 문구를 2단 트리거 기준으로 정렬 (#177)
- `tests/validate_skill_contracts.py` — 2단 트리거 표 존재와 재량형 "축약형" 표현 부활 방지 회귀 가드 추가 (#177)
- `skills/beopsuny/references/freshness-governance.md` — Unrouted Asset Rule(retire-first) 추가 (#178). 로드 경로가 없는 자산은 registry에 등록하지 않고 삭제하며, 복구는 git 이력으로 충분하다는 원칙을 명문화
- `skills/beopsuny/references/self-verification.md` — 설계 메모의 연구 인용 append-only 방침을 폐기하고 대체된 연구는 삭제하도록 변경 (#178)
- `tests/scenarios/16_router_regression.yaml` — router-01(light), router-05(full)에 `verification_tier` 주석 필드 추가 (#177/#178)

### Fixed
- `skills/beopsuny/references/source-access.md`, `skills/beopsuny/references/law-change-detection.md`, `skills/beopsuny/references/beopmang-api.md`, `skills/beopsuny/SKILL.md`, `tests/scenarios/01_basic_law.yaml`, `tests/scenarios/11_domain_specific.yaml`, `tests/scenarios/14_law_change_detection.yaml`, `spec/system-map.md`, `README.md` — `BEOPSUNY_DATA_ROOT` 기본값 의미를 통일. source-access.md는 변수를 data 디렉토리 자체로, report-deliverable.md는 beopsuny 루트(`${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/reports/`)로 소비해 같은 변수를 서로 다른 depth로 해석하던 drift 해소. 변수 = beopsuny 루트로 통일하고 미러 표기를 `${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/data/{family}`로 변경 (기본 경로 레이아웃 `~/.beopsuny/data/*`, `~/.beopsuny/reports/*`는 불변, override 시 해석만 정정). source-access.md에 변수 의미를 한 문장으로 명시. 과거 릴리즈 섹션의 옛 표기는 당시 기록 그대로 유지 (#196)

### Fixed (PR #179 리뷰 반영)
- `references/research-workflow.md` — `light` tier의 한 줄 ledger 필드에 `pinpoint`를 분리 명시하고 `supports`의 귀속 규칙을 추가해 citation-verification-contract Output Binding·self-verification Dim 1과의 필드 불일치 해소
- `skills/beopsuny/SKILL.md` — Citation gate 셀의 "복합 결론"을 `full` tier 기준으로 명확화(light는 packet 불필요), Output gate 셀에 묻혀 있던 명령형 규칙(검토 gate·내부 블록 제거)을 표 아래 독립 문장으로 분리, 과잉 로딩 문구 잔존 중복 2곳을 라우팅 원칙 1 pointer로 정리
- `references/freshness-governance.md` — Unrouted Asset Rule의 retire(파일 삭제)와 Retirement Rule의 registry 제거를 명시적으로 구분하고, registry 등록된 unrouted 자산의 동시 제거 절차 추가
- `CLAUDE.md` — 프로젝트 구조 주석에서 삭제된 external-sites("외부사이트") 참조 제거
- `tests/validate_skill_contracts.py` — "축약형" 전파일 금지를 재량 구문("축약형으로 적용", "축약해도 되지만")으로 좁히고, 회귀 가드 주석의 과대 서술 수정
- `.gitignore` — `backlog/tasks/` 이슈 미러(재생성 가능, GitHub이 source of truth) 추적 제외로 전환 — 후행 공백·미러 drift 문제 해소

### Removed
- `skills/beopsuny/assets/policies/freshness_debt.yaml` registry rows for `contract_review.yaml` and `investment_due_diligence.yaml` — volatile registry items were revalidated from the local legalize-kr mirror and next_review was advanced; files remain routed and maintained (#180)
- `skills/beopsuny/references/external-sites.md` — 참조 그래프 감사 결과 SKILL.md 라우터·reference·시나리오·테스트 어디에서도 로드 경로가 없는 dead reference로 확인되어 retire (#178). 공식 1차 소스 접근은 `references/source-access.md`가 커버

## [0.3.2] - 2026-06-23

**테마: Router Spine Refactor** — 단일 public skill은 유지하되, `SKILL.md`를 항상 로드되는 실행 라우터로 축소하고 세부 workflow를 on-demand reference로 분리했다. 목표는 multi-skill 자동 발견 불안정성과 Desktop Chat/Lite 호환성 문제를 피하면서도 내부 구조는 virtual skill suite처럼 동작하게 만드는 것.

### Added
- `skills/beopsuny/assets/tools/knowledge_manifest_ingest.py` — `beopsuny-knowledge` privacy manifest와 required assets를 fetch/검증하고, 실패 시 knowledge injection을 건너뛰면서 live legal research를 계속하도록 하는 fail-open ingestion helper 추가
- `tests/test_knowledge_manifest_ingest.py` — 임시 manifest/assets fixture와 local `beopsuny-knowledge` checkout을 이용해 checksum, schema, usage-mode, private raw failure downgrade를 검증
- `skills/beopsuny/assets/policies/knowledge_manifest.yaml` — `beopsuny-knowledge` privacy manifest의 stable/canary channel, required asset keys, sha256/usage_mode 검증 경계, 실패 시 live legal research continuation 정책 추가
- `skills/beopsuny/references/source-access.md` — Full/Lite 모드, legalize-kr, precedent-kr, 법망 API, korean-law-mcp, WebSearch fallback, 원문 링크, 데이터 초기화 절차를 분리
- `skills/beopsuny/references/research-workflow.md` — 법령·하위법령·행정규칙·판례·개정안 조사 깊이 조절 규칙 분리. `Legal Verification Core` 추가: issue-to-authority map, authority packet, citation ledger, contradiction scan, conclusion binding
- `skills/beopsuny/references/checklist-routing.md` — checklist 선택, triage, filtering, related checklist, 회사 맥락 적용 규칙 분리
- `skills/beopsuny/references/law-change-detection.md` — pull-only 법령 변경 감지, Full/Lite 동작, 조회 실패 처리, push 경계 분리
- `skills/beopsuny/references/freshness-governance.md` — stale 번들 YAML은 `triage_only`로만 쓰고 live source 확인 전 현행 의무·구비서류·기한·금액으로 승격하지 않는 Freshness Governance 문서 추가
- `skills/beopsuny/assets/policies/freshness_debt.yaml` — issue #101에 묶인 stale 자산 registry 추가. 각 자산별 `risk`, `allowed_use`, `verification_required`, `retire_when` 기록
- `skills/beopsuny/assets/schemas/freshness_revalidation.yaml` — stale 자산 갱신 또는 registry retirement 전에 남길 공식 source family, volatile item, next_review 변경, retirement decision evidence shape 추가
- `skills/beopsuny/assets/schemas/practice_profile.yaml` — 업무별 profile overlay 선택 스키마 추가. allowed scope, merge order, cannot_override, jurisdiction_scope를 고정해 practice profile이 법률 결론·출처 권위 라벨·role/destination gate를 덮어쓰지 못하게 함
- `skills/beopsuny/assets/schemas/legal_verification_packet.yaml` — Legal Verification Core의 issue-to-authority map, authority packet, citation ledger, contradiction scan, conclusion binding, self-verification 최소 evidence shape 추가
- `skills/beopsuny/assets/schemas/output_contract.yaml` — 역할별 output mode, destination별 must_include/must_strip, legal_effect_triggers, non_overrides를 고정해 외부 송부·제출·서명 gate가 출력 선호에 밀리지 않도록 함
- `skills/beopsuny/references/output-formats.md` — 법령/판례/행정규칙/INSUFFICIENT 출력 예시 분리
- `skills/beopsuny/references/output-formats.md` — `full` 법률 답변용 표준 `검토자 메모` 필드(Sources/Read/Currency/Before relying) 추가. `compact` 응답에는 강제하지 않음
- `skills/beopsuny/references/output-formats.md` — 역할별 output mode(`lawyer`/`legal_ops`/`business_user`/`unknown`)와 destination output contract(`internal_legal_memo`, `external_draft`, `agency_or_court_submission` 등) 추가
- `skills/beopsuny/references/contract_review_guide.md` — 계약 질문의 Proportionality 분류와 Destination routing 추가. 상대방 송부용·기관 제출용 산출물은 내부 검토 메타와 분리
- `skills/beopsuny/references/bulk-tabular-review.md` — values table / sources table 분리, `Verified` 빈 칸, quote/location spot-check, quote mismatch downgrade 규칙 추가
- `tests/scenarios/16_router_regression.yaml` — 라우터 회귀 시나리오 16건으로 확장. 단순 조문 확인, 계약 검토, 개인정보 knowledge boundary, push 알림 경계, 해설/의견 단독 결론 금지, 인허가 checklist routing, role/destination gate, freshness debt, legal verification core 검증
- `tests/fixtures/router_guardrail_outputs.yaml` + `tests/evaluate_scenario_outputs.py` — router-07~16 샘플 출력과 unsafe fixture 7건을 평가하는 guardrail harness 추가
- `tests/forward_eval_harness.py` — `tests/forward_evals/beopsuny_guardrails.yaml` 10개 high-risk prompt를 sample/template/score/command 모드로 실행·채점하고, `prompt_id`/`guardrail_category`/output evidence를 YAML로 남기는 forward eval harness 추가. live model/API 실행은 CI 필수 gate가 아니라 수동·nightly 경로로 유지
- `tests/validate_skill_contracts.py` — plugin 메타데이터 버전 정합, 최소 SKILL frontmatter, 계약 검토 가이드 경계, source fallback, 출력 크기 조절, 라우터 필수 reference, legal verification core, freshness debt registry, output/profile 계약, router fixture integrity, README 품질 계약 지도, README 회귀 검증 참조, 품질 계약 지도 reference target, CI workflow를 검증하는 정적 계약 검사 추가. `BEOPSUNY_INSTALLED_SKILL_PATH` 지정 시 설치본 content drift도 감지
- `.github/workflows/contract-tests.yml` — PR 및 main/master push에서 문서 계약 검증, router guardrail 평가, 테스트 harness compile 실행

### Changed
- README 예시와 제품 설명을 확정 자문 톤이 아니라 확인 가능한 1차 소스 중심 조사 보조 톤으로 조정
- `DESIGN.md`의 현재 아키텍처 용어를 Source Grade에서 source authority labels + verification status로 정렬
- `SKILL.md` 개인정보 보조 지식 레이어에 static privacy pre-knowledge 점검 축을 추가하되, 결론 근거·최초 route·비개인정보 질문 적용을 금지하는 경계를 명시
- 점수형 A/B/C/D 공개 출력 체계를 출처 권위 라벨(`공식 원문`, `공식 원문: 하급심`, `공식 실무자료`, `공식 실무자료: 미확정`, `해설/의견`, `참고 제외`)과 verification status 병기로 전환. `source_grades.yaml` 파일명은 호환성 때문에 유지하되, 내용은 `source_classes`/`default_labels` 계약으로 정리
- `skills/beopsuny/SKILL.md` 762줄 → 303줄. 상세 매뉴얼에서 의도 라우터 + Full/Lite 판별 + 출처 권위 라벨 계약 + 필수 자가 검증 중심 문서로 재작성하고, 법적 효과가 있는 행동에는 `user_role`/목적지 gate를 적용하도록 보강
- `skills/beopsuny/SKILL.md`에 품질 계약 매핑을 추가해 Legal Verification Core, Freshness Governance, Output role/destination gate, Profile/practice direction이 어떤 트리거에서 함께 적용되는지 단일 라우터 안에 고정
- `skills/beopsuny/SKILL.md` 의도 라우터에 Always-on legal conclusion gates를 추가해 citation verification, self-verification, output contract를 의도별 workflow reference와 분리. `router-01`, `router-05` 등 단순 legal research도 계약/체크리스트/knowledge workflow로 over-route하지 않으면서 gate 적용을 고정
- `skills/beopsuny/SKILL.md`의 `memory_profile` 라우터에서 `assets/schemas/*.yaml` glob을 제거하고 memory 관련 schema만 명시. legal verification, freshness, output contract schema가 memory 온보딩에 과잉 로드되는 drift 방지
- `skills/beopsuny/SKILL.md` frontmatter에서 비필수 `metadata.author/language/updated/version` 제거. 스킬 발견에 필요한 `name`/`description`만 유지하고, 배포 메타데이터는 `.claude-plugin/plugin.json`로 단일화. 한국 사용자 대상 스킬에 맞춰 `description`과 주요 라우터 문구를 한국어 중심으로 정리
- `skills/beopsuny/references/self-verification.md`를 근거 자료 아카이브에서 실제 자가 검증 절차 문서로 확장
- `skills/beopsuny/SKILL.md` 출력 계약에 `full`/`compact` 크기 조절 규칙 추가. 법률 결론에는 검토자 메모와 자가 검증을 유지하되, 비법률 운영 응답에는 법률용 메타데이터를 억지로 붙이지 않도록 정리
- `skills/beopsuny/references/contract_review_guide.md`를 v0.3 router spine 기준으로 재작성. 구버전 "명령어 실행" 지시를 제거하고 출처 권위 라벨, verification status, review_mode, Counter-drafting 경계를 반영
- `skills/beopsuny/references/*`의 출력 필드명 예시를 표준 `검토자 메모`로 정렬
- `skills/beopsuny/references/memory-structure.md` full 온보딩을 evidence-based onboarding으로 강화. seed document는 사용자가 명시적으로 제공한 경우에만 읽고, stated position 과 signed practice 차이를 저장 전 표시
- `skills/beopsuny/references/memory-structure.md`에 practice profile direction 추가. 현재는 top-level `profile.yaml`과 `contract_playbook`을 유지하고, 향후 업무별 profile은 `~/.beopsuny/practices/{contract,privacy,labor,regulatory,litigation}.yaml` overlay로 설계
- `skills/beopsuny/assets/schemas/company_profile.yaml` `contract_playbook.seed_documents`에 `stated_vs_signed_delta`와 `skipped_fields` 추가
- `skills/beopsuny/references/source-access.md`에 Capability Matrix 추가. 로컬 데이터 없음, 법망 API 접근 불가, WebSearch 없음, 네트워크 없음 등 환경별 fallback과 `[INSUFFICIENT]` 유보 기준 명시
- `README.md`에 개발/설치본 drift 확인 절차, 품질 계약 지도, 품질 계약 변경 체크리스트 추가. Legal verification core, 출처 권위/VERIFIED, Freshness governance, Output role/destination gate, Profile/practice direction, Bulk evidence grid의 기준 문서와 회귀 검증을 연결하고 새 법률 기능 추가 시 router, reference, schema/policy, scenario, unsafe fixture, 정적 검사, README/CHANGELOG를 함께 갱신하도록 명문화
- `DESIGN.md`에 2026-05-10 아키텍처 결정 기록 추가: 물리적 multi-skill 전환 보류, 단일 스킬 유지 + 내부 router spine 전환

### Notes
- 외부 artifact 이름은 계속 `beopsuny`
- 물리적 multi-skill 전환은 DOCX redline, 자동 알림/스케줄링, MCP/updater 배포, 계약 검토 단독 사용 피드백이 생길 때 재검토
- 새 verification status 태그 없음. 기존 6개 상태 태그 유지, 공개 출력은 출처 권위 라벨을 병기

## [0.3.1] - 2026-04-12

**테마: v0.3.0 post-release codex adversarial review hotfix** — v0.3.0 릴리즈 직후 codex (gpt-5.x, model_reasoning_effort=high, 1.85M tokens, law.go.kr 공식 소스 검증) adversarial review 에서 **4 P1 blockers + 4 P2 issues** 식별. 핵심 원칙 4 (정확한 인용) 가 걸린 조문번호 drift 여서 긴급 patch.

### Fixed (P1 — 법조문 정확성 / 단일 소스 계약)
- `skills/beopsuny/assets/data/clause_references.yaml` **`liquidated_damages` top-level 키 신설** (P1) — v0.3.0 `mandatory_provisions.yaml` 이 `clause_types: [liquidated_damages]` 를 사용했으나 clause_references top-level 에 해당 키가 없어 v0.3.0 에서 추가한 "single source 계약" 을 즉시 자가 위반. 신설 엔트리: 민법 제398조 + 약관규제법 제8조 + 근로기준법 제20조. `name_ko: 손해배상액의 예정 (위약금)`
- `skills/beopsuny/assets/data/clause_references.yaml` `limitation_of_liability` — `articles: ["제7조", "제8조"]` 를 `["제7조"]` 로 분리 (P1). 제7조 = 면책조항의 금지, 제8조 = 손해배상액의 예정 — 서로 다른 조항을 lump 한 pre-v0.3.0 drift 해소. 제8조는 신설 `liquidated_damages` 키로 이전
- `skills/beopsuny/SKILL.md` Step 4 항목 3 — `Data Processing → 개인정보보호법 제28조의8` (v0.3.0) → `제26조 (위탁) · 제28조의8 (국외이전, 2023-09-15 시행)` 정확화 (P1). 기존 `clause_references.yaml` `data_processing` (제26/28조의2/28조의3) 는 국외이전 제28조의8 누락 — 위탁 + 국외이전 둘 다 반영하도록 확장
- `skills/beopsuny/assets/data/clause_references.yaml` `data_processing` — 제28조의8 (국외이전, 2023-09-15 시행) 추가 + `data_privacy` 키와의 관계 주석 (P1). SKILL.md 포인터와 정합
- `skills/beopsuny/assets/data/clause_references.yaml` `most_favored_customer` / `exclusivity` — 공정거래법 `제23조` (구법) → `제45조` (2021-12-30 전면개정 후 조문번호), `제3조의2` → `제5조` + `제45조` 통일 (P1). `mandatory_provisions.yaml` 과의 조문번호 drift 해소. 구·현 조문번호 매핑 주석 병기
- `skills/beopsuny/assets/policies/mandatory_provisions.yaml` 공정거래법 제45조 엔트리 — `enforced_at: null` → `"2021-12-30"` (전면개정 시행일 기록)
- `tests/scenarios/13_contract_review.yaml` `contract-06` — `response_contains` 에서 `제8조` 제거 (P1). Limitation of Liability (`IN NO EVENT SHALL... BE LIABLE`) 는 제7조 범위; 제8조 (손해배상 예정) 는 별도 `liquidated_damages` 영역이라 요구하면 오답 유도

### Fixed (P2 — 약속 정합 / 테스트 강도)
- `README.md` + `skills/beopsuny/references/beopmang-api.md` + `tests/scenarios/01_basic_law.yaml` + `tests/scenarios/07_edge_cases.yaml` + `tests/scenarios/11_domain_specific.yaml` — `~/.beopsuny/data` 하드코딩 → `${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}` (P2). v0.3.0 CHANGELOG 는 "전역 통일" 을 선언했지만 SKILL.md 만 치환됐고 리포 전반은 미반영 — 오버클레임 해소 (v0.3.0 6 파일 잔여 처리)
- `skills/beopsuny/assets/policies/mandatory_provisions.yaml` `개인정보보호법 제28조의8` — `enforced_at: null` → `"2023-09-15"` (P2). 자기 주석 "시행일 확인 — 시행 전 조문은 '시행 예정' 으로 표시" 위반 해소. 2023-03-14 공포, 2023-09-15 시행
- `skills/beopsuny/assets/policies/mandatory_provisions.yaml` 상단 주석 — `enforced_at: null` 의미를 "법령 원제정 이후 실질적 변경 없이 상시 시행 중" 으로 명확화. 불확실할 때 null 로 도피 금지 문구 추가
- `tests/scenarios/14_law_change_detection.yaml` `forbidden_phrases` — bare `정기적으로` / `주기적` / `모니터링` / `알려드릴` / `체크해드리` 는 compliance checklist (`privacy_compliance.yaml` "주기적 점검", `food_business.yaml` "모니터링", `realestate.yaml` "허위매물 모니터링") 와 false-positive 충돌 (P2). Push 행위를 적극 약속하는 복합구로 anchor 강화: `정기적으로 알려` / `주기적으로 알려` / `자동 모니터링` / `모니터링을 설정` / `알려드릴게` / `알려드리겠` / `체크해드리` / `지속적으로 추적`
- `tests/scenarios/13_contract_review.yaml` `contract-21` / `contract-22` — bare `갑` / `을` substring assertion → `"우리가 갑:"` / `"우리가 을:"` 블록 마커 (P2). "갑자기" / "을지" 등과 substring 충돌 제거, SKILL.md Step 4 출력 포맷 블록 마커와 정확 매칭

### Notes
- v0.3.0 은 "drift 해소" 를 기치로 배포했으나 post-release 리뷰에서 drift 4건이 오히려 신설·지속됨을 발견. codex (독립 AI) adversarial review 방식이 내부 self-check 보다 우월함을 확인
- 공식 1차 소스 확인: law.go.kr 법령정보센터 조문 하이라이트로 제7조/제8조, 제28조의8, 공정거래법 제5·45조 직접 검증
- **Push 설계 없음 — pull 방식 유지**. forbidden_phrases anchor 강화는 오히려 Push 경계 정밀화
- 새 태그 도입 없음 / 기존 6개 태그 + Grade A/B/C/D 만 사용
- SKILL.md 731줄 유지 (line count 변동 없음)
- 갈래 1 (DOCX 처리형) 은 v0.4.0 이월 (#47)

## [0.3.0] - 2026-04-12

**테마: Policy Extension + Housekeeping** — v0.2.2 post-review 4 독립 리뷰 합의 P2 잔여 (갈래 2 housekeeping) + 정책 신설 (갈래 3 ①~④) 묶음 릴리즈. 한국 강행규정 단일 소스 외화, `party_position` 의 조항별 override 계약·해석 순서 명문화, `forbidden_phrases` Push 경계 자연 발화까지 확장, `BEOPSUNY_DATA_ROOT` 전역 통일. 갈래 1 (DOCX 처리형) 은 v0.4.0 이월.

### Added
- `skills/beopsuny/assets/policies/mandatory_provisions.yaml` 신설 — 한국 강행규정 단일 소스 (14 엔트리, v1.0.0, 2026-04-12). 약관·계약 일반 (약관규제법 제7조, 민법 제103·393·398조), IP (발명진흥법 제15조, 저작권법 제9·14조), 개인정보 (개인정보보호법 제26·28조의8), 공정거래 (공정거래법 제45조, 하도급법 제3·13조), 근로 (근로기준법 제15·20조). 스키마: `law` / `article` / `clause_types[]` / `note` / `enforced_at` (YYYY-MM-DD or null 상시). `clause_types` 는 `clause_references.yaml` top-level `clauses.*` 와 매칭 (갈래 3 ①, #28 L5)
- `skills/beopsuny/SKILL.md` Step 4 항목 5 `{조항key}` 계약 — `per_clause_override` 의 key 는 `assets/data/clause_references.yaml` top-level `clauses.*` ID 와 정확히 일치해야 하고, 일치하지 않는 key 는 graceful skip (갈래 3 ②)
- `skills/beopsuny/SKILL.md` Step 4 항목 5 Override 해석 순서 — `per_clause_override[key]` 존재 → 그 값 사용 (`""` 은 해당 조항만 양쪽 노출 강제) / 부재 → `default` 사용 (갈래 3 ③)
- `skills/beopsuny/assets/schemas/company_profile.yaml` `party_position` 주석에 해석 순서 요약 + `per_clause_override` 예시에 빈 문자열 케이스 추가 (갈래 3 ③)
- `skills/beopsuny/assets/schemas/company_profile.yaml` 상단 주석 migration 노트 — 기존 profile 에 `interested_laws`/`party_position` 부재 시 graceful fallback (갈래 2)
- `skills/beopsuny/assets/data/clause_references.yaml` 상단 주석 — top-level `clauses.*` ID 전체가 `per_clause_override` 유효 key 단일 소스임을 명시 (갈래 3 ②)
- `skills/beopsuny/SKILL.md` `assets/policies/` 테이블에 `mandatory_provisions.yaml` 한 행 추가 (Dim 4 서브체크 1 판정 시)
- `tests/scenarios/13_contract_review.yaml` 3 회귀 시나리오:
  - `contract-20` — `per_clause_override` key mismatch (철자 오류) 시 graceful skip 검증 (갈래 3 ②)
  - `contract-21` — `default: "gap"` + `override.indemnification: "eul"` → 을 관점 우선 노출 (갈래 3 ③)
  - `contract-22` — `default: "gap"` + `override.non_compete: ""` → 양쪽 노출 강제 (갈래 3 ③)
  - 시나리오 총합 19 → 22
- `tests/scenarios/14_law_change_detection.yaml` 4 시나리오 공통 `forbidden_phrases` 에 자연 발화 6 패턴 추가 — `정기적으로`, `주기적`, `모니터링`, `알려드릴`, `체크해드리`, `지속적으로 추적` (복합구 anchor; `추적` 단독은 SKILL.md "개정 이력 추적" 용법과 충돌하므로 제외). Push 경계 자연 발화까지 확장 (갈래 3 ④)

### Changed
- `skills/beopsuny/SKILL.md` 모드 판별·1순위 데이터 소스·데이터 초기화 전 섹션 — `~/.beopsuny/data` 하드코딩 → `${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}` 전역 통일. v0.2.2.1 에서 "법령 변경 감지 섹션 한정" 으로 한정됐던 `$DR` override 가 이제 전역. "경로 override 범위" 단락 삭제, `$DR` 축약은 반복 prefix 축약 용도로 유지 (갈래 2)
- `skills/beopsuny/SKILL.md` Dim 3 체크리스트 — "갑/을 위치" → "갑/을 위치(`party_position.default`)". Dim 4 서브체크 2 와 필드명 병기 통일 (갈래 2)
- `skills/beopsuny/SKILL.md` Dim 4 서브체크 1 — 인라인 강행규정 나열 제거, `assets/policies/mandatory_provisions.yaml` 참조로 전환. `clause_types` 매칭 규정 명시 (갈래 3 ①)
- `skills/beopsuny/assets/data/clause_references.yaml` 상단 주석 gap/eul 축 정의 — v0.2.1 generic phrasing → `profile.yaml.party_position.default: ""` (v0.2.2~) 스키마 필드 구체 참조 (갈래 2)
- `tests/scenarios/14_law_change_detection.yaml` `data_source` 주석 3곳 (law-change-01/02, law-change-04 forbidden_phrases prefix) — hardcoded path → `${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}/legalize-kr`. SKILL.md 본문과 drift 해소 (갈래 2)
- `tests/scenarios/13_contract_review.yaml` `contract-16` / `contract-19` `reference_files` — `assets/policies/mandatory_provisions.yaml` 행 추가 (Dim 4 서브체크 1 판정 근거 증적) (갈래 3 ①)
- `CHANGELOG.md` `[0.2.2]` 섹션 — "Push 없음"/"크론/알림 없음" 4회 반복 → 테마 헤더 1회 + Notes 1회로 압축. Added 블록 내부 반복 제거 (갈래 2)
- `.claude-plugin/plugin.json` 버전 `0.2.2.1` → `0.3.0` (최상위 및 `plugins[0]` 동시)

### Fixed
- `tests/scenarios/13_contract_review.yaml` `contract-19` — `forbidden_phrases_source: assets/policies/review_mode.yaml#counter_draft_forbidden_patterns` 메타 키 추가 (contract-16 과 동일 포맷). "대표 4개 샘플 — 전체 스캔은 단일 소스 로드" 주석 병기 (갈래 2)

### Notes
- **Push 설계 없음 — pull 방식 유지**. 크론/알림/스케줄링/notification 코드·문구 일절 없음. 갈래 3 ④ 가 오히려 Push 경계를 자연 발화까지 강화
- 기존 `profile.yaml` 에 `interested_laws`/`party_position` 부재 시 자동 graceful fallback 보장
- 새 태그 도입 없음. 기존 6개 태그(`[VERIFIED]` / `[UNVERIFIED]` / `[INSUFFICIENT]` / `[CONTRADICTED]` / `[STALE]` / `[EDITORIAL]`) + Grade A/B/C/D 만 사용
- SKILL.md 730 → 731줄 (상한 재조정 범위 내, 분리 트리거 800 미만)
- 4 리뷰어 합의 P2 전부 반영 — per_clause_override key contract / party_position override 해석 순서 / forbidden_phrases 자연 발화 / BEOPSUNY_DATA_ROOT 전역 / Dim 3 phrasing / clause_references 주석 legacy / scenario 14 $DR drift / contract-19 단일 소스 포인터 / CHANGELOG 중복 / migration 노트 / mandatory_provisions 단일 소스 (#28 L5)
- 갈래 1 (DOCX 처리형) 은 본 마일스톤 스코프 외 — v0.4.0 이월 (후보 이슈로 분리)

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
- `skills/beopsuny/assets/schemas/company_profile.yaml` `interested_laws: []` 필드 추가 (v0.2.2~). 법령명은 legalize-kr 디렉토리명과 일치
- `skills/beopsuny/assets/schemas/company_profile.yaml` `party_position` 필드 추가 (v0.2.2~) — #24 A안. `default: ""/"gap"/"eul"` + `per_clause_override: {}`. v0.2.1 에서 "스키마에 필드 없음" 으로 완화됐던 SKILL.md Step 4 항목 5 / Dim 4 서브체크 2 의 semantic dangle 자연 해소 (v0.2.1 post-review P2-3)
- `tests/scenarios/14_law_change_detection.yaml` 신설 — 4 시나리오
  - `law-change-01` — Full 모드 시간 범위 discovery
  - `law-change-02` — 특정 법령 (개인정보보호법) 변경 내역
  - `law-change-03` — `interested_laws` 응답 후단 append (Pull 경계)
  - `law-change-04` — Lite 모드 법망 API fallback
  - 공통 `forbidden_phrases`: `알림을 설정`, `크론`, `스케줄`, `notification`, `자동으로 알려드`, `푸시` (Push 경계는 테마 헤더·Notes 참조)
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
