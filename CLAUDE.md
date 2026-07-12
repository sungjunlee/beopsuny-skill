# beopsuny-skill

> 한국 법무 실무를 위한 Claude Code skill. 이 파일은 에이전트 온보딩용 포인터 문서다 — 내용 사본을 두지 않는다 (사본은 drift 검사 없이 썩는다).

## 단일 소스 지도

| 무엇 | 단일 소스 |
|------|-----------|
| 스킬 본체 — 의도 라우터, always-on gate, Full/Lite, 법률 원칙(정확 인용·공식 링크·시행일·환각 방지) | `skills/beopsuny/SKILL.md` |
| 워크플로우·계약 상세 (소스 접근, 조사, 계약 검토, 출력, 메모리 등) | `skills/beopsuny/references/*.md` (SKILL.md 라우터가 로딩 지점) |
| 데이터 소스 우선순위, source family, 초기화 절차 | `skills/beopsuny/references/source-access.md` |
| 사용자 안내, 설치, 자산 인벤토리, 품질 계약 지도, 변경·릴리즈 체크리스트 | `README.md` |
| 제품 방향, Non-Goals, Objectives, 전역 Decisions | `spec/charter.md` |
| 시스템 경계와 소유권 | `spec/system-map.md` |
| capability 계약 (6종) | `spec/capabilities.md` |
| 구조 결정 아카이브 (단일 스킬 vs split, 전환 트리거) | `DESIGN.md` |

## 작업 규칙

- **문서 문구를 고치기 전에** `tests/validate_skill_contracts.py`에서 해당 문구를 grep한다 — 다수의 check가 문서 문자열에 결합되어 있다. check를 고칠 때는 전문 문장 재고정 대신 토큰·구조 검사로 옮긴다.
- 하나의 계약 개념은 집이 1곳이다. 다른 문서에는 재요약 대신 포인터만 둔다.
- 변경 절차와 검증 게이트는 README의 `품질 계약 변경 체크리스트`를 따른다. 최소 게이트:

```bash
PYTHONPATH=.test-deps python3 tests/validate_skill_contracts.py
PYTHONPATH=.test-deps python3 tests/evaluate_scenario_outputs.py
```
