---
milestone: litigation-template
status: active
started: 2026-07-07
due: TBD
objectives: [O1]
component: "source-citation"
---

# litigation-template

에픽 #97 — Korean legal workflow suite 후속. workflow-suite(#109) 종결 후 사용자 선택으로 #110 착수. 착수 전 `spec-grill contract-review`로 마지막 capability 후보 결정화 완료(2026-07-07, 잔여 후보 0).

## Goal
분쟁형 질문과 판례 인용이 법원식 판단 구조로 정리된다: 요건사실·인정사실·미확인 사실·증거·잠정 결론이 분리되고, 판례 출력이 사건번호 확인에 그치지 않고 사안의 유사점/차이점·적용 한계·distinguishing을 포함한다. research-workflow 또는 litigation reference에 템플릿을 얹되 새 라우터 의도·always-on gate 변경 없이(router-loading HC1), 정적 구조 검증(O1)이 템플릿을 고정한다.

## Plan

- [ ] #110 (Batch 1, ~1 session) court-style element/fact analysis template — 분쟁 판단 템플릿(요건/인정/미확인/증거/잠정결론 분리) + 판례 출력 distinguishing 필드(유사점·차이점·적용 한계) + 구조 검증 추가

## Running Context
- **계약 앵커**: `source-citation` capability — #110의 최선명 완료 기준("판례 인용이 사건번호 확인에 그치지 않는다")이 인용 깊이 요구다. court-style 요건사실 분리는 더 근거 있는 인용을 만드는 workflow 구조. distinguishing/유사·차이는 판례 인용을 사건번호에서 실질 비교로 심화 — source-citation의 citation-verification 도메인.
- **capability 경계 주의**: #110은 litigation workflow이며 방금 landed된 `contract-review`가 **아니다**(contract-review Out-of-scope에 #110 명시). 작업 중 별개 결정 경계로 판명되면(신규 litigation capability 필요) 중단·보고 — 지금은 source-citation 확장으로 처리.
- **금지 유지**: 형량·승패 예측은 계속 금지(#111과 공통). 템플릿은 판단 구조를 제공하지 결과 예측을 하지 않는다.
- **workflow map 정합**: `references/workflow-map.md` litigation 행이 #110 court-style template 자리표시를 이미 둠 — 채우되 행 구조는 유지, required references에 새 파일 추가 시 map도 갱신.
- **후속 예약**: #111 enforcement/criminal response, #112 cross-border overlay. #111까지 쌓이면 litigation capability 여부 `spec-grill map` 재검토.
- 테스트↔문서 강결합 + 이동 문자열 보호 assert + codex PR 본문 truncate 보강 + **redispatch는 --run-id resume**은 `_context.md` 참조.

## Progress
- 2026-07-07: 스프린트 생성. #110만 스코프(#111-112 후속 예약). component source-citation, objective O1. 착수 전 contract-review grill 완료로 spec 축 정리됨.
