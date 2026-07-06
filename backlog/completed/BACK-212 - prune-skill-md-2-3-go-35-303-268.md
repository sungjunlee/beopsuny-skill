---
id: BACK-212
title: '[Prune] SKILL.md 2차 프루닝 실행 — 3건 GO 항목 (~35줄, 303→~268)'
status: To Do
labels:
  - area:architecture
  - area:refactor
priority: medium
milestone:
created_date: '2026-07-06'
---
## Description
## 배경

#183 실익 평가 결과 부분 GO 3건. 판정 근거와 분해표는 #183 코멘트, 목표치 수정(~270줄)은 에픽 #174 코멘트 참조.

## 작업

1. **privacy 기본 점검 축 하강 (~13줄)**: SKILL.md 237–247의 축 목록+소개문을 `references/knowledge-injection.md`로 이동. SKILL.md에는 사용 조건·금지·pointer만 유지.
   - 짝 수정: `check_static_privacy_preknowledge_boundaries` 분리 — 축 문자열(수집·이용 ~ server-side tag forwarding)은 knowledge-injection.md에서 assert, 경계 문자열("이 축이 결론을 강제하지 않는다", "지식 자산을 최초 경로…")은 SKILL.md에서 assert 유지.
2. **law_change 순서 코드 블록 삭제 (~10줄)**: SKILL.md 293–301 삭제. 226줄의 한 줄 순서 명시가 단일 소스.
3. **Full/Lite 경로 블록 압축 (~12줄)**: SKILL.md 112–123 경로 블록을 원칙 문장 2–3줄로 압축 (`${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/data/` 하위 family 존재로 판별, 명령·family map은 source-access.md). Lite 안내 blockquote·family 묶음 개념·no-auto-clone 원칙 유지.

## 준수 계약

- spec/capabilities.md `router-loading` Hard Constraint 1: 스파인 축소를 이유로 always-on gate를 상시 로딩 표면에서 분리하지 않는다.
- 이동/삭제 전 해당 문자열을 assert하는 check 함수 grep (테스트↔문서 강결합).

## AC

- [ ] SKILL.md ~268줄 이하, 3건 반영
- [ ] 축 목록이 knowledge-injection.md에 존재하고 SKILL.md에는 트리거·금지만 남음
- [ ] check_static_privacy_preknowledge_boundaries 분리 반영, 재발 방지 유지
- [ ] O1 (validate_skill_contracts.py) PASS + O2 (evaluate_scenario_outputs.py) PASS
