---
id: BACK-177
title: '[Prune] Legal Verification Core에 체크 가능한 2단 트리거 도입 (light/full)'
status: To Do
labels:
  - area:architecture
  - area:refactor
  - area:docs
priority: high
milestone: 
created_date: '2026-07-02'
---
## Description
Part of #174 — #175, #176로 기준선 확보 후 진행 (행동 변화 폭이 가장 큼)

## 문제

Legal Verification Core(references/research-workflow.md:16-125)는 6단계 파이프라인(issue-to-authority map → authority packet → citation ledger → contradiction scan → conclusion binding → verification packet)에 5개의 자체 조어를 요구하는 무거운 기계장치인데, 적용 강도 조절 기준이 checkable하지 않음:

> "짧은 조문 확인처럼 단순한 경우에도 **축약형으로** 적용한다" (research-workflow.md:18)

"축약형"이 무엇을 생략해도 되는지 정의가 없어 실행이 run마다 갈리고, ledger-형태 텍스트만 만드는 의식(ceremony)으로 전락할 위험. 관련 실패 모드: 검증 없이 `🔍 자가 검증: Citation 3/3 ✓` 블록만 채우는 형식화 — 형식 준수는 체크 가능하지만 실제 검증 여부는 체크 불가능.

## 작업

"축약형" 표현을 체크 가능한 2단 트리거로 대체. 예시:

| Tier | 트리거 | 적용 |
| --- | --- | --- |
| light | 결론 후보 1개 + 조문 원문 확인으로 종결 | ledger·packet 생략, 출처 권위 라벨 + verification status만 |
| full | 결론 후보 2개 이상, 또는 금액·기한·과징금, 또는 외부 송부·기관 제출·소송 포지션 | 6단계 core 전체 |

- 트리거는 라우팅 시점에 판정 가능한 조건만 사용 (질문 형태·주제로 판별)
- self-verification.md, SKILL.md의 관련 문구("축약형", "단순한 경우에도")를 동일 트리거로 정렬
- 가능하면 조어 수 축소 검토 (예: authority packet과 citation ledger 통합)

## AC

- [ ] "축약형" 같은 판정 불가능한 표현이 제거되고 2단 트리거로 대체됨
- [ ] light tier에서 생략 가능한 단계가 명시적으로 열거됨
- [ ] tests/scenarios: 단순 조문 확인 → light, 복합 결론/금액/외부 송부 → full로 일관되게 라우팅
- [ ] full tier 시나리오에서 기존 검증 품질(ledger 필드, contradiction scan) 유지

