# DESIGN.md — 법순이 아키텍처 결정 아카이브

> 이 문서는 **구조 결정(단일 스킬 vs multi-skill split)의 결정 아카이브**다. 현재 아키텍처와 시스템 경계는 [`spec/system-map.md`](spec/system-map.md), 제품 방향·Non-Goals·전역 Decisions는 [`spec/charter.md`](spec/charter.md), capability 계약은 [`spec/capabilities.md`](spec/capabilities.md)가 단일 소스다. 과거의 아키텍처 스냅샷·페르소나·버전 로드맵 절(§1–3, §5)은 spec/으로 대체되어 폐기했다 (2026-07-12, git 이력 참조).

## Multi-skill 전환 트리거

아래 중 **하나라도** 발생하면 물리적 multi-skill 분리를 재평가한다. 트리거 없이는 분리하지 않는다 (charter Non-Goal: "내부 정돈만을 위한 공개 스킬 분리 금지"와 정렬).

| 트리거 | 조건 | 근거 |
|--------|------|------|
| **기능 트리거 A** | DOCX 파싱·redline 생성 기능 첫 추가 | 계약 워크플로우가 단순 "조회"에서 "편집"으로 넘어감 → 계약 스킬을 독립 컨텍스트로 |
| **기능 트리거 B** | 법정 의무 자동 알림·스케줄링 추가 | 컴플라이언스는 "시간축 상태"를 가지므로 조사형 스킬과 결합 시 컨텍스트 오염 |
| **피드백 트리거** | 사용자가 "X 기능만 쓰고 싶다" 3회 이상 | Primary 페르소나의 워크플로우 분기가 실제로 발생한다는 신호 |
| **규모 트리거** | `wc -l skills/beopsuny/SKILL.md` > 800 | Claude 권장선(500줄) + 여유. 초과 시 성능·정확도 저하 |

**트리거 발동 시 행동**: 이 문서에 재평가 결정을 기록하고 마일스톤을 연다.

참고: 2026-07 프루닝 이후 SKILL.md는 ~270줄 예산으로 관리되며(규모 트리거 대비 충분한 여유), spine 사이징은 `spec/capabilities.md`의 `router-loading` capability가 소유한다.

### 전환 시 공유 자산 참조 규칙 (강제)

- **금지**: `../` 상대경로 트래버설. Claude Code `${CLAUDE_SKILL_DIR}`은 per-skill이라 cross-skill 트래버설은 플랫폼이 보장하지 않는다.
- **필수**: `${CLAUDE_PLUGIN_ROOT}/assets/...` 절대경로. 플러그인 레벨에서 공유 자산은 플러그인 루트 기준으로 접근한다.
- **금지**: `skills/shared/` 디렉토리 (비관습, 자동 발견 불안정).

---

## 6. 아키텍처 결정 기록

(§ 번호는 기존 외부 참조 유지를 위해 보존한다.)

### 2026-05-10: 단일 스킬 유지 + 내부 router spine 전환

**컨텍스트**: `SKILL.md`가 762줄까지 커져 multi-skill 전환 트리거(800줄)에 근접했다. 단순한 분량보다 더 큰 문제는 법률 조사, 계약 검토, 체크리스트, 변경 감지, 메모리, knowledge injection, 출력 예시가 모두 항상 로드되는 spine에 섞인 점이다.

**결정**: 외부 artifact는 단일 `beopsuny` skill로 유지하되, 내부 구조는 virtual skill suite처럼 재정렬한다.

```
User question
  -> SKILL.md router spine
  -> intent-specific reference
  -> source authority labels + verification status + self verification
  -> answer
```

**이유**:

1. §6의 2026-04-12 단일 스킬 유지 근거는 여전히 유효하다. Desktop Chat/Lite paste 호환성, 통합형 사내변호사 workflow, multi-skill 자동 발견 불안정성이 남아 있다.
2. 하지만 `SKILL.md`가 매뉴얼이 되면 단순 조문 질문에도 계약 검토, checklist, 변경 감지, memory 규칙이 모델 context에 올라와 오답 리스크가 커진다.
3. 따라서 물리적 multi-skill 전환 대신 `SKILL.md`는 router + mandatory gates로 축소하고, source access, research, checklist, law change, output formats를 on-demand reference로 이동한다.

**후속 트리거**: DOCX redline, 자동 알림/스케줄링, 공식 MCP/updater 배포, 계약 검토 단독 사용 피드백이 쌓이면 물리적 multi-skill 또는 plugin escalation을 다시 검토한다.

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
   - 결정 시점(2026-04-12 pre-PR): SKILL.md 475줄 — Claude 권장 500줄 미만.
   - v0.1.0 PR 반영 후: 548줄 — 여전히 분리 트리거(800줄) 대비 충분한 여유.
   - 분리 동기가 공학적이지 않다.

**결정**: 단일 스킬 유지. 위 전환 트리거 중 하나라도 발동하면 재평가.

**대체 안 (기각됨)**: 3개 스킬 분리 + `skills/shared/` 공유 자산. 기각 사유 = 위 1~4번.

---

## 변경 이력

| 날짜 | 변경 | PR |
|------|------|----|
| 2026-07-12 | 아키텍처 스냅샷·로드맵 절(§1–3, §5) 폐기 — spec/으로 대체, 결정 아카이브로 축소 | — |
| 2026-05-10 | 단일 스킬 유지 + 내부 router spine 전환 결정 | TBD |
| 2026-04-12 | 초안 작성 — 단일 스킬 결정, 분리 트리거 정의, v0.2.0 로드맵 | #2 |
