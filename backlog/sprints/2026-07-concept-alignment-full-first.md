# Sprint Spec — 컨셉 정렬: Full-first 전환 + 초벌 북극성

- **status**: completed (2026-07-25) — 에픽 #234 + T1~T4(#235 #236 #237 #238) 전량 머지, PR #239
- **created**: 2026-07-24
- **후속**: 잔존 Lite 명명 #240, 리뷰 후속 에픽 #241
- **decision origin**: 2026-07-24 리뷰 세션 (사용자 방향 확정)
- **theme**: chat-Lite ceremony 폐기, Full-first 재정렬, "편집 가능한 초벌"을 1급 목표로

---

## 1. 배경 / 결정

리뷰 세션에서 사용자가 확정한 방향 전환:

- **주 사용자** = 사내변호사(아내), **주 환경** = 로컬 데스크톱 앱(Full 모드, 영속 파일시스템).
- 산업 흐름상 챗 모드는 쇠퇴하고 agentic 로컬 앱(Claude Code / Codex 데스크톱)이 비개발자에게도 열리는 중 → **챗 대응 Lite 모드를 1급 표면으로 유지할 이유가 없다.**
- 조사 결과(2026-07): 두 벤더 모두 **로컬(CLI/데스크톱/IDE)=진짜 영속, 클라우드/웹=세션별 ephemeral(재구성+캐시)**. 로컬 앱 타겟이 두 벤더에서 견고. (상세: memory `project_full_first_direction`)

핵심 통찰: `Full 모드 vs Lite 모드`는 **ceremony(기본형)**였고, 진짜 정보를 나르는 **경계**는 이미 provenance 라벨이다. 따라서 "Lite 삭제"가 아니라 **이분법 붕괴 + degradation 재명명**이 맞다 — boundary/shape 철학(charter 2026-07-21)과 정합.

## 2. 북극성 (North Star)

> 주 사용자는 사내변호사, 주 환경은 로컬 앱(Full). 목표는 완벽한 자문이 아니라 **변호사가 몇 군데만 터치하면 쓸 수 있는, 근거가 정확한 초벌**.

## 3. 스코프

### In — "컨셉 정렬(A)": 사용자 신호 없이 옳은, 확정 방향의 구현
1. **Full/Lite 이분법 붕괴** + API/web을 **source degradation**으로 재명명 (`로컬 미러 → 원격 재구성 → 확인 불가`). provenance 라벨은 경계로 유지.
2. **초벌 북극성 명문화** + 기본 출력을 **draft-first**로 (기본 가정을 `unknown`/보수 → 사내변호사 전제; 단 `business_user`/외부송부 gate는 유지).
3. **hedge 밀도 합리적 기본값** — Full-first면 인용 다수가 `[VERIFIED]` → 과잉 유보를 걷어 "보여줄 만한" 수준. (완벽 튜닝 아님)
4. **charter O4 재정의** — "Full/Lite mode 식별" 제거, "provenance 투명성"은 유지.

### Out — "취향 튜닝(B)": 아내 dogfood 후로 명시적 연기
- draft-usefulness forward-eval **세부 기준** 설계 (그녀 취향 반영 필요)
- hedge 밀도/artifact 우선순위 **미세조정**
- 메타층(테스트 74 checks) 경량화 — 별건, 이 스프린트 이후
- 클라우드 setup-script / git-repo-memory 구현 — defer (문서 한 줄만)

## 4. 파일 레벨 변경 지도

| 대상 | 변경 |
| --- | --- |
| `spec/charter.md` | Approach에 Full-first·초벌 북극성 한 줄; Decisions에 2026-07-24 항목; **O4 재작성**(mode-ID 제거) |
| `skills/beopsuny/SKILL.md` | `Full / Lite 판별` 절 → "source 가용성 + degradation"으로 재작성, Lite 안내 메시지 제거; 출력 계약 기본 가정을 draft-first로; 밀도 기본값 한 줄 |
| `skills/beopsuny/references/source-access.md` | mode 언어 → degradation 언어. family map·provenance는 유지 |
| `skills/beopsuny/references/output-formats.md` | `lawyer` draft-first 강조, 밀도 기본값(과잉 `[UNVERIFIED]` 억제) |
| `docs/desktop-chat-guide.md`, `desktop-chat-dogfood.md` | deprecate 또는 삭제 (chat-Lite 종료) |
| `README.md` | 방법3(챗)·"Chat 한계" 절 정리, 데이터소스/설치를 Full-first 프레이밍, 품질 계약 지도 갱신 |
| `DESIGN.md` | 2026-04-12 결정의 "Desktop Chat paste 호환성" 근거를 historical로 주석 (단일 스킬 결정 자체는 다른 근거로 유지) |
| `tests/validate_skill_contracts.py` | mode-ceremony 관련 check 제거/조정 (토큰·구조만) |
| `tests/forward_evals/beopsuny_guardrails.yaml` + o4 세트 | o4-01(family Full/Lite 식별)·o4-05(Lite behavior)을 provenance-투명성 기준으로 재작성 |
| `CHANGELOG.md` | Unreleased에 항목 |

## 5. charter O4 재정의 (초안)

- **현행**: "…can identify whether Beopsuny is in **Full or Lite mode** and see provenance that distinguishes local official-source mirrors, direct official-source checks, API fallback, and insufficient-source states."
- **개정**: "A user on a persistent local app (Claude Code / Codex desktop or CLI) runs Beopsuny in Full mode by default; when a source family is not locally mirrored, the skill **gracefully degrades** to API/official-link checks and **sees provenance that distinguishes local official-source mirrors, direct official-source checks, API fallback, and insufficient-source states.**" (mode 식별 → provenance 투명성 + degradation)

## 6. 완료 기준 (Acceptance)

- SKILL/reference에 "Lite 모드" ceremony(판별 절·안내 메시지)가 없고, degradation 언어 + provenance 라벨만 남는다.
- 기본 출력 가정이 draft-first(사내변호사 전제)로 바뀌되, `business_user`/`unknown`/외부송부 gate는 그대로 통과(회귀 없음).
- charter Approach/Decision/O4가 Full-first를 반영.
- **게이트 그린**: `validate_skill_contracts.py` PASS, `evaluate_scenario_outputs.py` PASS.
- o4 forward-eval 세트가 mode-ID가 아니라 provenance 투명성을 검증.
- README/docs가 Full-first 프레이밍. CHANGELOG 갱신.

## 7. 리스크 / 안 할 것

- ❌ multi-skill 분리 (charter Non-Goal, 트리거 미발동)
- ❌ degradation/API 경로 **완전 삭제** (신선 설치·클라우드 fallback에 필요 — 재명명만)
- ❌ R2/메모리 동기화 구현 (premature)
- ⚠️ 리스크: 기본 가정 변경(→ 사내변호사)이 외부송부/비법무 gate를 약화시키지 않도록, 해당 unsafe fixture 회귀를 반드시 유지.

## 8. Epic / Task 분해 (GitHub 등록 예정)

- **EPIC**: 컨셉 정렬 — Full-first 전환 + 초벌 북극성 (chat-Lite ceremony 폐기)
  - **T1 [direction]**: charter 개정 — Full-first Approach/Decision + O4 재정의
  - **T2 [behavior]**: SKILL Full/Lite 이분법 붕괴 + source degradation 재명명 (SKILL·source-access + o4 forward-eval 재작성 + 정적검사 정리 + CHANGELOG)
  - **T3 [behavior]**: 초벌 북극성 — 기본 출력 draft-first(사내변호사 전제) + hedge 밀도 기본값 (SKILL 출력계약·output-formats + scenario/fixture)
  - **T4 [docs]**: README/desktop-chat/DESIGN Full-first 정리

## 9. 검증 게이트 (각 task 공통)

```bash
PYTHONPATH=.test-deps python3 tests/validate_skill_contracts.py
PYTHONPATH=.test-deps python3 tests/evaluate_scenario_outputs.py
```
