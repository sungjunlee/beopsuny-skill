---
id: BACK-181
title: '[Guardrail] light/full tier 위반을 잡는 unsafe fixture + evaluator rule 추가'
status: To Do
labels:
  - enhancement
  - area:architecture
  - area:patterns
  - area:refactor
priority: medium
milestone:
created_date: '2026-07-03'
---
## Description
## 문제

#177에서 Legal Verification Core에 light/full 2단 트리거를 도입했지만, 현재 보호 장치는 문서와 static string check뿐이다. `tests/scenarios/16_router_regression.yaml`의 `verification_tier` 필드(router-01: light, router-05: full)는 **아무 evaluator도 소비하지 않는 주석**이라 (PR #179 리뷰에서 확인), 트리거를 어기는 출력이 나와도 O2가 잡지 못한다.

## 작업

1. `tests/fixtures/router_guardrail_outputs.yaml`에 unsafe fixture 추가: light 시나리오(단순 조문 확인)인데 issue-to-authority map / authority packet / citation ledger 문서 형태를 출력에 노출한 사례
2. `tests/evaluate_scenario_outputs.py`에 대응 guardrail rule 추가 (예: `light_tier_no_packet_ceremony`)
3. 가능하면 반대 방향도: full 트리거(금액·과징금·외부 송부)인데 검증 구조 없이 단정 결론만 낸 unsafe fixture
4. `verification_tier` 필드를 rule이 실제로 읽도록 연결 — 연결이 과하면 필드 제거하고 fixture id 매핑으로 대체

## AC

- [ ] light tier 위반 unsafe fixture가 O2에서 FAIL로 잡힘
- [ ] 정상 light/full 출력은 PASS 유지
- [ ] `verification_tier` 필드가 소비되거나 제거됨 (죽은 주석으로 남기지 않음)
- [ ] O1/O2 전체 PASS

