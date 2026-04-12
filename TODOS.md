# TODOS

법순이 로드맵. `/gstack-plan-eng-review` (2026-04-12) 결과.

---

## TODO 1: DESIGN.md 생성 — 분리 트리거 로드맵

**What**: 멀티 스킬 전환 트리거 + 아키텍처 결정 기록 문서

**Why**: Codex 리뷰 후 "지금은 단일 스킬 유지" 결정을 객관적 트리거 조건과 함께 기록.
아내 피드백 루프에서 데이터 수집 기준이 되고, 3개월 후에도 맥락 잃지 않음.

**Context**:
- 2026-04-12 `/gstack-plan-eng-review`에서 처음 3개 스킬 분리 결정했다가 Codex 독립 리뷰에서 되돌림
- 주요 리스크: `skills/shared/`는 플랫폼 관습 아님, 스킬 자동 발견 불안정 (GitHub Issue #9716 open), Desktop paste 모드 호환성
- 진화 방향: 문서 처리형으로 이동 예정 + 비전문가 타깃 확장 고려

**Content (초안)**:
```markdown
# DESIGN.md

## 현재 아키텍처 (v0.0.x)
단일 Claude Code 스킬. `~/.claude/skills/beopsuny/` 설치 또는 플러그인 마켓플레이스.

## 사용자 페르소나
- Primary: 사내변호사 (첫 사용자)
- Secondary: 사내변호 이상 확장 업무
- Stretch: 법률 비전문가

## Multi-skill 전환 트리거

아래 중 하나라도 발생하면 플러그인 내 3개 스킬로 분리:

- **기능 트리거**: DOCX 파싱/redline 생성 기능 첫 추가 (계약)
- **기능 트리거**: 법정 의무 자동 알림/스케줄링 (컴플라이언스)
- **피드백 트리거**: 사용자 "X만 쓰고 싶다" 3회 이상
- **규모 트리거**: SKILL.md 800줄 초과

## 전환 시 구조 (미래)

skills/
├── research/SKILL.md     # 현재 SKILL.md의 법령 조사 섹션
├── contract/SKILL.md     # 계약 워크플로우 + DOCX 처리
└── compliance/SKILL.md   # 체크리스트 + 연간 의무

assets/  # 공유 (${CLAUDE_PLUGIN_ROOT}/assets/로 참조)
references/  # 공유

**중요**: `../` 트래버설 금지, `${CLAUDE_PLUGIN_ROOT}/` 절대경로 사용.

## 아키텍처 결정 기록

### 2026-04-12: 단일 스킬 유지 (reversed from multi-skill)
- 초기 결정: 3개 스킬로 분리
- Codex 독립 리뷰: skills/shared/는 플랫폼 관습 아님, 라우팅 불확실, Desktop paste 깨짐
- 최종 결정: 단일 유지, 위 트리거 발동 시 재평가
```

**Pros**: 미래 결정 객관적 기준. 아내 피드백 수집 틀.
**Cons**: 문서 유지 부담 (1페이지 규모).
**Depends on**: 없음 (독립 실행)

---

## TODO 2: Source Grading A/B/C/D 적용 (첫 PR)

**What**:
- `skills/beopsuny/references/source-grading.md` 생성 (규칙 문서)
- `skills/beopsuny/assets/policies/source_grades.yaml` 생성 (PIPA-expert 패턴)
- `skills/beopsuny/SKILL.md`의 "데이터 소스" 섹션 재작성 — 기존 3-tier 우선순위를 A/B/C/D로 통합
- 기존 태그 `[VERIFIED]`, `[UNVERIFIED]`, `[INSUFFICIENT]` 유지하되 Grade와 병기

**Why**:
- 3개 패턴 중 가장 임팩트 크고 기존 "확인 필요" 원칙과 자연스럽게 통합
- 상업적 AI 법률 도구(LexisNexis, Westlaw) 산업 표준
- 인용 신뢰도 명시적으로 표시 → 환각 방지 강화

**Context**:
- PIPA-expert의 `config/source-grades.json` 패턴 차용
- YAML으로 변환 (주석 달기 쉬움)
- 등급:
  - Grade A: 법령 원문, 대법원 판례, 법제처 유권해석
  - Grade B: 처분례, 하급심 판례, 규제기관 가이드라인
  - Grade C: 로펌 뉴스레터, 학술 논문 (단독 근거 불가)
  - Grade D: 일반 뉴스, AI 요약, 위키 (제외)

**출력 예시**:
```
[Grade A] [VERIFIED] 개인정보보호법 제15조 제1항 제1호
> "정보주체의 동의를 받은 경우"
```

**Pros**: 응답 신뢰도 명시적. 환각 사전 차단.
**Cons**: 태그가 응답에 노이즈 추가. 미술적 오버헤드.
**Depends on**: 없음 (첫 PR로 실행 가능)

---

## TODO 3: YAML Policy 구조 리팩터링

**What**:
- `assets/` 플랫 구조 → `assets/policies/` (규칙) + `assets/data/` (레퍼런스 데이터) 분리
- `assets/policies/`: source_grades.yaml (TODO 2), clause_taxonomy.yaml (신규), review_mode.yaml (신규)
- `assets/data/`: law_index.yaml, permits.yaml, forms.yaml, legal_terms.yaml, compliance_calendar.yaml, checklists/

**Why**:
- 현재는 "룰"과 "데이터"가 섞여 있음
- kipeum86의 contract-review-agent 패턴 차용
- 미래 멀티 스킬 전환 시 경계가 뉴트럴 (공유 자산 이동 쉬움)

**Context**:
- 현재: 7개 최상위 YAML + 11개 checklists + 5개 schemas
- 변경 영향: SKILL.md, references/, tests/scenarios/의 경로 참조 모두 업데이트
- 리팩터링 수준: 몇 시간 소요

**Pros**: kipeum86 패턴 채용. v0.2.0 분리 준비.
**Cons**: 기존 파일 경로 변경 → 참조 전부 업데이트.
**Depends on**: TODO 2 (Source Grading이 policies/ 구조의 시작점)

---

## TODO 4: 7차원 리뷰 Phase 1 — 자가 검증 레이어

**What**:
- SKILL.md에 60-80줄 추가
- 응답 생성 후, 출력 전 3차원 자가 검증:
  1. **Citation 검증**: 인용한 모든 조문/판례가 실제 존재하는가?
  2. **Legal Substance**: 논리 비약 없는가? 결론이 근거와 연결되는가?
  3. **Client Alignment**: 실제 질문에 답했는가? 실무적 시사점이 있는가?
- 검증 실패 시 해당 부분을 `[UNVERIFIED]` 또는 "확인 필요"로 다운그레이드

**Why**:
- 3개 패턴 중 마지막 적용
- LexisNexis/Westlaw도 막지 못한 할루시네이션 문제 (Stanford 2025 연구) 대응
- Phase 2 (4-7차원: 작문/구조/포맷/문서간)는 문서 처리형 기능 없이 무의미 → 제외

**Context**:
- kipeum86의 second-review-agent Dim 1/2/3에 해당
- 가벼운 버전으로 시작 — 별도 서브에이전트 호출 없이 SKILL.md 내 자가 검증 프롬프트

**Pros**: 인용 오류 사전 차단. 본질적 도입 가치 높음.
**Cons**: 응답 시간 10-30% 증가. 더 보수적 답변 경향.
**Depends on**: TODO 2 (Source Grading이 자가 검증의 기준)

---

## 실행 순서

```
1. TODO 1 (DESIGN.md 생성) — 독립 실행 가능, 문서만
2. TODO 2 (Source Grading) — 첫 코드 PR
3. TODO 3 (YAML 리팩터링) — TODO 2 이후
4. TODO 4 (자가 검증 레이어) — TODO 2 이후, TODO 3과 독립
```

1-2는 같은 PR에 번들링 가능. 3-4는 각자 별도 PR.
