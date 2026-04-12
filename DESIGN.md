# DESIGN.md — 법순이 아키텍처 결정 기록

> 법순이(beopsuny)의 구조적 선택과 진화 로드맵. 3개월 후에도 맥락을 잃지 않기 위한 문서.

## 1. 현재 아키텍처 (v0.0.x ~ v0.1.x)

**단일 Claude Code 스킬**.

```
beopsuny-skill/                      # 레포
├── .claude-plugin/plugin.json        # 플러그인 메타 (plugins[].source = ./skills/beopsuny)
├── skills/
│   └── beopsuny/                     # 단일 스킬
│       ├── SKILL.md                  # 본체 (Full/Lite 모드)
│       ├── assets/                   # YAML 데이터 + 체크리스트
│       └── references/               # 가이드 문서 (on-demand read)
├── docs/desktop-chat-guide.md        # Chat 탭 사용자 가이드
└── tests/scenarios/                  # 13종 시나리오
```

### 설치 경로

사용자 머신에서는 아래 중 하나로 설치된다.

| 방식 | 경로 | 비고 |
|------|------|------|
| 마켓플레이스 (Claude Code) | `~/.claude/plugins/.../beopsuny-skill/` | `plugin.json`의 `plugins[]` 기반 |
| 심링크 (로컬 dev) | `~/.claude/skills/beopsuny → .../skills/beopsuny` | README 참조 |
| zip 배포 | 사용자 지정 경로 | Custom Instructions paste도 지원 |
| Desktop Chat (Lite) | 설치 없음 — `docs/desktop-chat-guide.md`의 프로젝트 지침 템플릿 paste | 채팅마다 스토리지 초기화 |

### 런타임 데이터

코드와 데이터 분리 원칙 (gstack 패턴):

- **코드**: `skills/beopsuny/` (레포 내, 읽기 전용)
- **데이터**: `~/.beopsuny/` (사용자 머신, 프로필/데이터/이력)

---

## 2. 사용자 페르소나

| 페르소나 | 설명 | 우선순위 |
|----------|------|----------|
| **Primary** | 사내변호사 (개발자의 배우자가 첫 사용자) — 법령 조사 → 계약 검토 → 컴플라이언스를 한 흐름에서 처리 | **이 페르소나가 모든 설계 결정의 기준점** |
| **Secondary** | 사내변호 경계를 넘어선 확장 업무 (M&A 초기 검토, 해외 진출 초기 리서치 등) | 현재 워크플로우 커버 |
| **Stretch** | 법률 비전문가 (스타트업 창업자, 개인사업자) | v0.2.0 이후 |

Primary 페르소나의 워크플로우가 "통합형"이라는 사실은 **단일 스킬 유지 결정의 핵심 근거**다 (§5 참조).

---

## 3. 진화 방향

현재는 **조사·참조형** 스킬. 다음 단계는 **문서 처리형** 기능 추가.

| 단계 | 초점 | 대표 기능 |
|------|------|-----------|
| v0.0.x | 조사·참조 | 법령 조문 검색, 판례 조회, 체크리스트, 회사 맥락 메모리 |
| v0.1.x | **패턴 고도화** (현재) | Source Grading A/B/C/D, YAML Policy 구조, 자가 검증 레이어 |
| v0.2.0 | **문서 처리형** | DOCX 파싱 / redline 생성, 법정 의무 자동 알림·스케줄링 |
| v0.3.0+ | 비전문가 확장 | 평이한 설명 모드, 의사결정 도우미 |

v0.2.0 착수가 곧 §4의 **Multi-skill 전환 트리거**와 맞물린다.

---

## 4. Multi-skill 전환 트리거

아래 중 **하나라도** 발생하면 v0.2.0에서 플러그인 내 3개 스킬로 분리한다.

| 트리거 | 조건 | 근거 |
|--------|------|------|
| **기능 트리거 A** | DOCX 파싱·redline 생성 기능 첫 추가 | 계약 워크플로우가 단순 "조회"에서 "편집"으로 넘어감 → 계약 스킬을 독립 컨텍스트로 |
| **기능 트리거 B** | 법정 의무 자동 알림·스케줄링 추가 | 컴플라이언스는 "시간축 상태"를 가지므로 조사형 스킬과 결합 시 컨텍스트 오염 |
| **피드백 트리거** | 사용자가 "X 기능만 쓰고 싶다" 3회 이상 | Primary 페르소나의 워크플로우 분기가 실제로 발생한다는 신호 |
| **규모 트리거** | `wc -l skills/beopsuny/SKILL.md` > 800 | Claude 권장선(500줄) + 여유. 초과 시 성능·정확도 저하 |

**트리거 발동 시 행동**: `DESIGN.md`에 재평가 결정을 기록하고, v0.2.0 마일스톤을 연다. 트리거 없이는 분리하지 않는다.

---

## 5. 전환 시 구조 (미래, 정보용)

트리거 발동 시 아래 구조로 이동한다.

```
beopsuny-skill/
├── .claude-plugin/plugin.json       # plugins[] 3개
└── skills/
    ├── research/
    │   └── SKILL.md                 # 법령/판례/행정규칙 조사
    ├── contract/
    │   └── SKILL.md                 # 계약 검토 + DOCX 처리
    ├── compliance/
    │   └── SKILL.md                 # 체크리스트 + 연간 의무 + 스케줄링
    └── ... (공유 자산은 각 SKILL.md에서 ${CLAUDE_PLUGIN_ROOT}/assets/로 참조)
```

### 공유 자산 참조 규칙 (강제)

- **금지**: `../` 상대경로 트래버설. Claude Code `${CLAUDE_SKILL_DIR}`은 per-skill이라 cross-skill 트래버설은 플랫폼이 보장하지 않는다.
- **필수**: `${CLAUDE_PLUGIN_ROOT}/assets/...` 절대경로. 플러그인 레벨에서 공유 자산은 플러그인 루트 기준으로 접근한다.
- **금지**: `skills/shared/` 디렉토리 (비관습, 자동 발견 불안정).

### 제거 시점

사용자가 관습적으로 한 스킬만 쓰는 패턴이 확립되면 나머지 스킬을 별도 플러그인으로 옮길 수 있으나, 이는 v0.3.0 이후 결정.

---

## 6. 아키텍처 결정 기록

### 2026-04-12: 단일 스킬 유지 (reversed from multi-skill)

**컨텍스트**: `/gstack-plan-eng-review` 세션에서 처음 3개 스킬(research/contract/compliance)로 분리하는 방향으로 갔다가, Codex 독립 리뷰에서 아래 지적을 받고 되돌렸다.

**되돌린 이유**:

1. **`skills/shared/`는 Claude Code 플랫폼 관습이 아님**
   - `${CLAUDE_SKILL_DIR}`은 per-skill로 정의되며, cross-skill `../` 트래버설은 공식 지원되지 않는다.
   - 공유 자산은 플러그인 레벨에서 `${CLAUDE_PLUGIN_ROOT}/`로만 가능 — 3개 스킬로 나눴을 때 어디에 둘지 합의된 관습이 없다.

2. **스킬 자동 발견 불안정 — [anthropics/claude-code#9716](https://github.com/anthropics/claude-code/issues/9716)**
   - OPEN, 69 reactions. 멀티 스킬 환경에서 "어느 스킬이 트리거될지" 예측이 안 되는 리포트 다수.
   - 법률 도메인은 "틀리면 피해가 크다" — 라우팅 불확실성을 수용할 수 없다.

3. **Desktop Chat (Lite) paste 모드 호환성**
   - Lite 사용자는 `docs/desktop-chat-guide.md`의 프로젝트 지침 템플릿을 복사해서 쓴다.
   - 멀티 스킬 구조는 여러 SKILL.md를 하나로 합치는 사전 처리를 요구하거나, 사용자에게 파일 선택 부담을 준다.
   - 단일 파일 paste 가능성이 Primary 페르소나의 실제 접근성을 좌우한다.

4. **Primary 페르소나(사내변호사)의 통합 워크플로우**
   - 사내변호사의 하루: 계약 검토 중 "이 조항 강행규정 맞아?" → 법령 조회 → "이거 컴플라이언스 이슈야?" → 체크리스트 → 다시 계약.
   - 3개 스킬로 쪼개면 매 전환마다 컨텍스트 손실. 통합형 단일 스킬이 실제 업무 리듬과 맞는다.

5. **현재 규모가 분리 임계점에 못 미침**
   - SKILL.md 475줄 (Claude 권장 500줄 미만). 분리 동기가 공학적이지 않다.

**결정**: 단일 스킬 유지. §4의 트리거 중 하나라도 발동하면 재평가.

**대체 안 (기각됨)**: 3개 스킬 분리 + `skills/shared/` 공유 자산. 기각 사유 = 위 1~4번.

---

## 변경 이력

| 날짜 | 변경 | PR |
|------|------|----|
| 2026-04-12 | 초안 작성 — 단일 스킬 결정, 분리 트리거 정의, v0.2.0 로드맵 | #2 |
