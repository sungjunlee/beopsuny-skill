---
id: BACK-176
title: '[Prune] 과잉 라우팅 금지 규칙 5곳 → 1곳 통합'
status: To Do
labels:
  - area:architecture
  - area:refactor
priority: medium
milestone:
created_date: '2026-07-02'
---
## Description
Part of #174 — #175 이후 진행 (통합 위치가 그때 명확해짐)

## 문제

"단순 조문 확인은 가볍게 처리하고 과잉 라우팅하지 않는다"는 같은 의미가 5곳에 산재:

| 위치 | 표현 |
| --- | --- |
| SKILL.md:65 | gate 표 하단 "계약/체크리스트/knowledge workflow를 추가 로딩하라는 뜻이 아니다" |
| SKILL.md:69-71 | 라우팅 원칙 1·3 |
| references/research-workflow.md Right-Sizing | 질문 유형별 조사 범위 |
| references/self-verification.md:56 (Dim 3) | "과잉 라우팅하지 않았는가" |
| references/knowledge-injection.md | Right-sized 사용 판단 |

같은 경고를 5번 반복해야 한다는 것 자체가, 구조가 과잉 로딩을 유발하기 쉽고 경고문으로 패치 중이라는 신호 (writing-great-skills의 duplication/sediment).

## 작업

1. SKILL.md 의도 라우터의 라우팅 원칙 아래 "Right-sizing" 한 블록으로 통합 (authoritative 위치)
2. research-workflow.md Right-Sizing은 조사 깊이 조절이라는 고유 내용만 남기고 과잉 라우팅 문구 제거
3. self-verification Dim 3, knowledge-injection의 해당 문구는 삭제 또는 SKILL.md pointer로 교체

## AC

- [ ] "과잉 라우팅 금지" 의미의 authoritative 위치가 SKILL.md 라우팅 원칙 1곳
- [ ] 나머지 4곳은 삭제되거나 pointer만 존재
- [ ] tests/scenarios에서 단순 조문 확인 시나리오가 계약/체크리스트 reference를 로드하지 않음

