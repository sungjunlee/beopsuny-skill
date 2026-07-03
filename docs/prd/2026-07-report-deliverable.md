# PRD: 법률 검토 리포트 산출물 (HTML Report Deliverable)

- 상태: **승인 — 에픽/이슈 등록 진행** (2026-07-03). 결정 포인트 D1-D5는 제안값 채택(D1 접근 A, D2 기본 위치만, D3 internal_legal_memo, D4 중간 수위, D5 S1 우선) — 구현 중 재론 가능
- 작성 배경: Claude Code(CLI)에 Artifacts 도입(2026-07) → 시각 산출물 논의 재점화. 사용자 방향: "HTML로 리포트 만드는 것도 검토해볼만한 상황"
- 관련: 에픽 #96(역할·목적지 출력 계약), #107(내부 메모/비즈니스 요약/외부 초안 분리), 보류된 Artifacts/Mermaid 검토

> ⚠️ **결정 포인트**로 표시된 항목은 사용자 확인이 필요한 가정이다. 나머지는 기존 계약에서 도출된 제안.

## 1. 문제

beopsuny의 산출물은 현재 터미널/채팅 텍스트가 전부다. 실무에서 검토 결과는 "전달·보관·재열람되는 문서"로 소비되는데, 텍스트 출력은 다음에서 약하다:

- **대량 표 검토**(`bulk_tabular_review`): 계약 20개 × 조항 grid는 터미널 마크다운 표의 가독 한계를 넘는다. values/sources 이중 표는 특히.
- **계약 검토 결과**: 조항별 위험·협상 포인트·근거를 재열람·비교할 문서 형태가 없다.
- **전달**: 법무팀 내부 회람, 현업 공유 시 대화 로그 복사가 유일한 경로다.

한편 destination 계약(output-formats.md)은 이미 "무엇을 담고 무엇을 빼는지"를 정의해뒀지만, **어떤 매체로 나가는지**에 대한 계약이 없다.

## 2. 목표 / 비목표

### 목표

1. 검토 결과를 **self-contained HTML 리포트 파일**로 생성하는 계약을 정의한다 — 렌더 레이어이며, 내용 규칙은 기존 destination 계약을 그대로 소비한다.
2. 환경별 전달 채널을 능력 기반으로 정의한다: 로컬 파일(기본) → Claude Code Artifact(요청 시) → Chat 탭 Artifacts(Lite 대체).
3. 첫 소비자 2개: `bulk_tabular_review` grid, 계약 검토 리포트.

### 비목표

- **Mermaid/다이어그램 시각화** — 별도 보류 상태 유지. 이 PRD는 HTML 문서 리포트만 다룬다. 표·타임라인은 HTML/인라인 SVG로 충분한 범위만.
- **역할·목적지 내용 계약 변경** — #96/#107의 영역. 이 PRD는 그 계약의 렌더 타깃을 추가할 뿐, 내용 규칙을 재정의하지 않는다.
- **자동 발송/공유** — 리포트 생성까지만. 이메일 발송, 자동 업로드, 스케줄 생성은 하지 않는다 (charter의 pull-first, 대외 행동 gate와 일관).
- **리포트가 대화 답변을 대체** — 텍스트 응답(근거·라벨·자가 검증 포함)이 항상 원본이고 리포트는 파생물이다. charter: "시각화는 텍스트 법적 근거를 대체하지 않는다"의 확장 적용.

## 3. 사용자 시나리오

| # | 시나리오 | 산출물 |
| --- | --- | --- |
| S1 | 사내변호사가 "이 NDA 12개에서 해지·손배 조항만 비교해서 리포트로 만들어줘" | bulk grid 리포트: 정렬 가능한 values 표 + sources 표 토글, cell state 색상 코딩, 읽은 범위·자가 검증 표기 |
| S2 | 법무 담당자가 "이 계약 검토 결과를 팀에 공유할 문서로" | 계약 검토 리포트: 횡단 이슈 → 조항별 위험(why_risky/negotiation_points) → 권고, destination=`business_summary` 규칙 적용 |
| S3 | (Claude Code) "이거 URL로 줘, 변호사님한테 보여드리게" | 같은 리포트를 Artifact로 배포 — 공유 가정 구성(면책 포함, 내부 메타 제외) 강제 |

## 4. 요구사항 (계약)

### R1. 렌더 레이어 원칙

- 리포트는 항상 **하나의 destination 계약을 선택**하고 그 내용 규칙(포함/제외 항목)을 따른다. 사용자가 지정하지 않으면 기본값 적용.
- ⚠️ **결정 포인트 D3**: 기본 destination — 제안: `internal_legal_memo`(검토자 메모·자가 검증 포함). 대안: 공유 가능성을 전제로 한 보수 기본(`business_summary` 스타일).
- `non_overrides` 유지: 출처 권위 라벨, verification status, 면책 고지는 어떤 리포트 스타일로도 생략 불가.

### R2. 파일 규격

- Self-contained HTML 1파일: 인라인 CSS, 외부 리소스(폰트·CDN·이미지 URL) 금지. 근거: Artifact CSP 호환 + 오프라인/메일 첨부 호환을 한 규격으로.
- 저장 위치: `${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/reports/{YYYY-MM-DD}-{slug}.html` — ⚠️ **결정 포인트 D2**: 프로젝트 디렉토리 저장 옵션 필요 여부.
- 문서 하단 고정 블록: 생성일, 검토 범위(읽은 범위), 최신성 한계, 면책 고지. destination이 내부용이면 자가 검증 블록 포함.

### R3. 전달 채널 (능력 기반)

| 환경 | 기본 | 요청 시 |
| --- | --- | --- |
| Claude Code (Full) | 로컬 파일 | Artifact 배포 (S3) |
| Codex CLI (Full) | 로컬 파일 | — (Artifact 없음) |
| Desktop Chat 탭 (Lite) | Artifacts (파일 영속 없음) | — |

- SKILL.md 시각화 섹션의 "Lite 모드나" 조건을 능력 기반("환경이 지원하면")으로 교체.

### R4. Artifact 배포 시 추가 gate (S3)

- Artifact는 호스팅 URL = 공유 가능 산출물로 취급한다. 배포 시 **공유 가정 구성 강제**: `external_draft` 수준은 아니어도 — 내부 검토자 메모·미확인 내부 노트 제외, 면책 고지 포함, "법무 검토 전 대외 사용 금지" 표시.
- ⚠️ **결정 포인트 D4**: 이 수위가 적절한가 (더 보수: 아예 external_draft 규칙 강제 / 더 완화: 사용자 재량).

### R5. 라우팅

- 새 의도를 추가하지 않는다. 기존 의도(`bulk_tabular_review`, `contract_review` 등)의 **출력 옵션**으로, 트리거는 사용자 발화("리포트로", "HTML로", "문서로 만들어", "공유용으로 정리").
- 새 reference 1개: `references/report-deliverable.md` (규격·채널·gate). SKILL.md에는 시각화 섹션 개정 + 라우터 gate 표 불변.

### R6. 검증 (O1/O2 편입)

- O1: report-deliverable.md 계약 존재·SKILL.md 시각화 섹션 능력 기반 문구·필수 하단 블록 규칙 static check.
- O2: unsafe fixture — (a) 리포트가 출처 권위 라벨 없이 결론 표를 담은 출력, (b) Artifact 배포에 내부 자가 검증 블록이 그대로 포함된 출력.

## 5. 접근안 비교 (검토 기록)

| 접근 | 요지 | 판정 |
| --- | --- | --- |
| **A. 파일 우선, 얇은 렌더 계약** (채택 제안) | HTML 파일이 1급, Artifact는 배포 채널. destination 계약 소비 | 환경 독립, #96과 직교, 보류한 공유 고민 최소화 |
| B. Artifact-native | 호스팅 URL이 1급 산출물, 공유 워크플로 포함 | 체감 크지만 Codex CLI 배제, 공유 계약 설계 선행 필요 — S3로 부분 수용 |
| C. #96 통합 재설계 | 내용+매체+시각화 단일 PRD | 범위 과대. 내용 계약은 #96에 남기고 본 PRD는 렌더만 |

⚠️ **결정 포인트 D1**: 접근 A 채택 여부 (사용자 발화 "HTML로 리포트" 방향에 근거한 가정).

## 6. 에픽/이슈 후보 (PRD 승인 후 등록)

- **[EPIC] 리포트 산출물 레이어** — 본 PRD 구현
  - [Report] `references/report-deliverable.md` 계약 + SKILL.md 시각화 섹션 능력 기반 개정
  - [Report] bulk_tabular_review grid HTML 템플릿 (S1) — values/sources, cell state 색상, 정렬
  - [Report] 계약 검토 리포트 템플릿 (S2) — destination 규칙 소비
  - [Report] Artifact 배포 gate (S3) — 공유 가정 구성 + unsafe fixture
  - [Tests] O1 static check + O2 fixture (R6)
- 기존 #96과의 관계: 본 에픽은 #96의 렌더 타깃을 제공 — #107(destination 분리)이 먼저 끝나면 좋으나 강한 의존은 아님 (현행 5개 destination 정의로 충분히 시작 가능).
- ⚠️ **결정 포인트 D5**: 첫 구현 대상 — 제안: S1(bulk grid, 체감 최대) 먼저.

## 7. 리스크

| 리스크 | 완화 |
| --- | --- |
| 리포트가 "완성 문서"처럼 보여 법무 검토 없이 대외 사용 | 하단 고정 블록 + Artifact gate(R4) + 기존 legal_effect_triggers 연동 |
| 템플릿 HTML이 스킬 문서를 비대화 | 템플릿은 `assets/templates/`에 두고 reference는 규칙만 (progressive disclosure 유지) |
| Chat 탭(Lite)과 CLI 규격 분화 | R2 self-contained 규격을 공통 분모로 — Chat 탭 Artifacts도 동일 HTML 소비 가능 |
| 프루닝 직후 재비대화 | 새 의도 0개, SKILL.md 순증 목표 ≤ 5줄, 상세는 전부 reference/template로 |
