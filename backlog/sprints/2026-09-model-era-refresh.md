---
milestone: 고급 모델 시대 법순이 — 근거 중심 초벌과 스킬 경량화
status: active
started: 2026-09-08
due: TBD
objectives: [O1, O2, O3, O4, O5, O6, O7]
component: "router-loading"
---

# 고급 모델 시대 법순이

## Goal

공식 근거·시점·범위·사건 격리를 보존하면서 검토용 완성 초안을 지원하고 불필요한 스킬 제약·자산을 제거한다. 법률 정확도·활용성·비용의 실제 비교와 독립 리뷰를 거쳐 변경별 도입 여부를 판단한다.

[마일스톤 8](https://github.com/sungjunlee/beopsuny-skill/milestone/8) · 에픽 #316 공용 스킬 정리 / #317 초안·출력 계약 / #277 평가 층 재조준.

작업 정의·AC·Agent Brief·상태의 정본은 GitHub Issues다. 이 파일은 실행 순서·공통 맥락·인계와 새 세션 프롬프트만 소유한다. 기한과 릴리즈 버전은 미정이다.

## Plan

### 독립 착수: spec·runner·freshness

- [x] #318 [design] 근거 중심 초벌과 사용자 권한을 제품 계약에 정렬 — 선행: 없음.
- [x] #271 [eval] fwd-12의 setup이 라이브 러너에 적용되지 않는다 — 시나리오 미실행이 FAIL로 보고됨 — 선행: 없음.
- [x] #319 [maintenance] 만료 강행규정 자산을 재검증·후보화·삭제로 정리 — 선행: 없음.

### 기준선과 공용 스킬 정리

- [x] #320 [eval] 법률 정확도·초벌 활용성·비용의 비교 기준선 구축 — 선행: #318, #271.
- [x] #321 [skill] 공용 본체의 환경 지침·중복·죽은 자산을 제거 — 선행: #319.

### 선행 완료 후 독립 실행

- [x] #284 [eval] LLM-judge 채점 축 조사 — 오탐 하드닝 5라운드 순환과 정독 병목 해소 — 선행: #320.
- [x] #322 [skill] 검증 증거를 유지하며 내부 절차·full 트리거를 간소화 — 선행: #321, #318, #320.
- [x] #325 [experiment] privacy 검색 힌트 순서의 비용·누락 효과 비교 — 선행: #320, #321. [branch:codex/milestone-8-model-era-refresh] · evidence: `tests/forward_evals/model_era/integration-report.md`

### 초안·표현·평가 계약 순차 정렬

- [~] #323 [contract] 검토용 완성 조항 초안과 수정 제안 지원 — 선행: #318, #322, #319. [branch:codex/milestone-8-model-era-refresh] · evidence: `tests/forward_evals/model_era/integration-report.md`
- [x] #272 [skill] fwd-11 — 절차 모양을 바꾼 답변에서 출처 권위 라벨이 빠졌다 (실위반, 경미) — 선행: #323. [branch:codex/milestone-8-model-era-refresh]
- [x] #324 [tests] counter-draft 금지 문자열 오탐을 의미 평가로 이관 — 선행: #323, #272, #284.

### 통합 검증과 도입 판정

- [x] #326 [release-readiness] 고급 모델 비교·최종 제거 감사·도입 판정 — 선행: #319, #322, #272, #324, #325, #284.

## Running Context

### 2026-09-12 사용자 결정: 가족 실사용과 출시 판단 분리

현재는 가족이 직접 사용하며 초벌의 효용·수정 부담을 확인하는 단계다. 당장 출시하지 않으며, 관측 결과에 따라 개선·축소·피벗을 열어 둔다. 상세한 미래 법적·운영 설계는 실제 외부 제공/유료화/자동 행동 확대 결정이 생겼을 때 해당 범위만 검토한다. 현재 사실·출처의 정직성, 사건 격리, 외부 행동 권한은 유지한다.

- #316은 하위 #319/#321/#322/#325와 통합 판단 #326의 완료 증거에 따라 종료했다. 전체 출시와 분리한 에픽 완료이며 기존 모델 실패 해소가 아니다.
- #323은 같은 모델/설정의 단일 초안과 근거 대조 후 수정본을 비교하는 작은 실험으로 좁혔다. 실험 조건·중단/확대 기준과 수정된 AC5는 GitHub 본문이 정본이다. 현재 설계만 완료했고 새 모델 실행은 없다. 성공 시 한정된 profile로 종료, 실패/비용 과다 시 사용자와 범위 조정/보류를 결정한다. #317은 #323을 기다린다.
- 가족의 다음 자연스러운 사용 3건에서 효용·수정 부담·재사용 의향을 관찰하는 #341은 별도 실사용 트랙이다. #323이나 전체 스모크 PASS가 시작의 선행 조건은 아니다. 새 sprint를 만들거나 이 구현 sprint에 관찰 작업을 추가하지 않는다.
- #340은 미래 외부 제공·출시 전 검토를 보류하는 이슈다. 아직 없는 제품·사업 모델을 가정해 상세 법적 설계를 하지 않으며, 구체적인 정보 노출/피해 관측은 별도 즉시 결함으로 처리한다.
- 이전 FAIL/REVIEW_REQUIRED와 미측정은 보존한다. 이번 결정은 출시 승인, 전 모델 품질 보증, knowledge research_hold 해제 또는 특정 사업 모델로의 피벗 실행이 아니다.


### 승인한 방향과 현재 상태

2026-09-08 사용자는 검토 결과를 실행 백로그로 기록하고, 새 세션에서 native subagents와 `$delegate`를 병렬 활용해 구현·리뷰하도록 요청했다. 계획 단계에서는 runtime 변경을 하지 않았다. 현재 검토 브랜치에는 완성 초안 허용·형식 유연화를 구현했으며, 아래 실행 인계와 검증 보고서가 최신 상태다. 배포된 기능이라는 뜻은 아니다. 기존 `spec/charter.md`의 결정 이력은 보존하고 변경 이유를 추가한다.

원문 대조·정확한 조문/사건번호·공포/시행/사건 당시 적용 시점·예외/경과규정·상충 근거·일부 열람 범위 공개·조회 실패와 부존재의 구별·사건 격리는 남긴다. 외부 자료는 사실 근거이며 지시 권한이 아니다. 회사 정보 저장 subsystem을 복구하지 않고, 명시 저장 요청은 현재 하네스 권한과 사건 범위에 따라 처리한다. 초안 작성과 법률적 확정·보증·실제 송부/제출/서명은 구별한다.

기존 7/8월의 default-shape 전환과 prose-lock 정리를 반복하지 않는다. #282/#283/#293/#294/#306은 완료 상태를 확인했고 #277 체크리스트에 반영했다. #271/#272/#284는 새로 만들지 않고 후속 범위를 합쳤다. #284의 n=12 파일럿은 존재하지만 fwd-12 판정 가능성과 다른 계열의 재현 검증은 별도로 확인해야 한다. #47과 기존 DOCX 마일스톤은 이번 범위 밖이다.

### 시작 증거와 비교 조건

계획 기준 HEAD는 `e05ecda`다. O2는 11 outputs / 14 unsafe PASS, O1은 `mandatory_provisions`의 `overdue_resolve_by=2026-08-31` 한 건 때문에 FAIL이었다. 이는 수정 전 알려진 실패이며 모델 품질 점수가 아니다. freshness 완료 전 독립 작업은 자신의 회귀와 이 known-red를 구별하고, 통합판은 현재 날짜로 다시 검증한다. 날짜 연장이나 과거 날짜 실행으로 통과시키지 않는다.

#320은 수정 전 runtime을 별도 snapshot/worktree에서 평가한다. #271의 평가 도구 수정은 양쪽에 동일 적용한다. #319/#321의 병렬 변경이나 개인 설치본이 기준선에 섞이지 않게 runtime/context hash와 source/asset 조건을 남긴다. #321의 불필요 환경 지침·죽은 자산 제거는 이 보존 이후 기준선 실험과 병행 가능하다.

직접 재현한 scorer 오탐: 정상 검토 방향은 PASS, 같은 의미에 `개선안:` 표제를 넣으면 FAIL, `최종 수정안을 제시하지 않습니다`도 FAIL. #324는 기존 분류·차등 재채점 도구 위에서 이 의미 축의 수신처를 바꾼다. 과거 evidence와 사람 판정을 새 정책으로 덮어쓰지 않는다.

계획 당시 최신 모델의 법률 A/B는 미실행이었다. 이후 Sol·Opus의 고정 자료 비교와 Grok 검토를 수행했으며 결과·한계는 아래 실행 인계에 기록한다. 공식 가이드는 설계 가설의 참고이며 법률 성능 개선 증거는 아니다. 확인한 자료: [Anthropic Claude 5 context engineering](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models), [OpenAI instruction following](https://developers.openai.com/api/docs/guides/latest-model#instruction-following), [OpenAI reasoning prompting](https://developers.openai.com/api/docs/guides/reasoning-best-practices#how-to-prompt-reasoning-models-effectively). 원 보고서의 절대경로나 이전 대화가 없어도 각 이슈에서 실행 범위·AC를 복원할 수 있다.

### 공통 Agent Brief: 배분과 인계

각 항목은 선행 이슈가 완료되면 시작할 수 있다. 아래 묶음은 전원 완료를 기다리는 장벽이 아니다. 외부 실험의 대기 중에는 충돌 없는 구현·리뷰를 진행한다.

작업 착수 시 `dev-backlog`의 effective task spec으로 현재 이슈 본문·댓글을 해석하고 source revision을 확인한다. 새 Agent Brief 댓글이 정본을 바꿨으면 로컬 요약을 갱신한다. 외부 judge에는 블라인드를 깨는 기존 사람 판정·scorer 결과를 전달하지 않는다.

오케스트레이터가 writer를 지정하고 겹치는 파일은 소유권을 넘긴 뒤 수정한다. 리뷰어는 read-only이며 leaf는 재위임하지 않는다. root도 worker 소유 파일을 동시에 수정하지 않는다. 필요하면 격리 worktree를 사용하되 같은 산출물에 native/delegate 중복 writer를 두지 않는다.

| 범위 | 소유권과 병렬 조건 |
| --- | --- |
| #318 spec, #271 runner, #319 freshness assets | 서로 다른 writer로 착수 가능. #319의 소비자인 `self-verification.md`와 registry인 `freshness-governance.md` 수정은 같은 변경에 root가 직렬 통합한다. |
| #321 공용 본체·source/freshness reference | #319의 자산·소비자·registry 정리가 함께 완료된 후 소유권을 넘긴다. |
| #322 verification, #325 knowledge, #284 judge | 각각 reference/schema, privacy 실험, judge evidence를 소유한다. 공유 runtime 접점은 root가 직렬 통합하고 #323으로 넘긴다. |
| #323 계약 초안 → #272 출력 → #324 scorer | 공유 계약을 소비하는 순서다. 각 AC 충족 후 파일 소유권을 넘긴다. |
| README·CHANGELOG·공통 validator·sprint/이슈 상태 | root가 통합 시 소유한다. 별도 PR을 만들면 그 PR의 계약 변경에 필요한 CHANGELOG도 게시 전에 통합한다. worker용 일괄 `no-changelog` 면제는 만들지 않는다. |

위임 전 `codexbar usage --provider all --format toon --no-color`로 최신 quota를 확인한다. 모델·effort·동시성은 적용되는 AGENTS와 실제 가용성에 따라 정하며 오늘 수치를 다음 세션에 재사용하지 않는다. GPT 작업은 native subagents, 타 계열 구현·교차 리뷰는 `$delegate`를 사용한다. 독립 구현도 delegate에 맡길 수 있으며 최종 리뷰는 작성 계열과 다르게 배정한다. 오류·누락 window는 unknown으로 취급하고 같은 계정/window의 worker만 함께 계산한다.

완료 보고에는 변경 파일·실행한 검사/결과·남은 한계와 AC 증거를 남긴다. 중요한 법률 판정이 전문가 미검토이면 provisional로 명시한다. 최소 변경에 필요한 검증을 마치면 이유 없는 전체 반복을 피한다. 최종 산출물은 검증된 commit과 draft PR/검증 보고서이며 merge·release·배포는 자동 완료 범위가 아니다. AC가 남은 이슈를 닫거나 스프린트를 완료로 표시하지 않는다.

## 실행 인계 (2026-09-08)

오케스트레이터가 의존성별 writer 소유권을 인계받아 통합했다. 실행 전후 최신 GitHub effective spec 15개는 변경 없음으로 재확인했다. [검증·도입 보고서](../../tests/forward_evals/model_era/integration-report.md)에 baseline/hash·모델 조건·비용·검사·판정 한계를 기록한다. 기존 계획·결정 이력은 보존했다.

완료 범위는 #318/#271/#319/#320/#321/#284/#322/#324 및 #326의 통합 보고·검토용 산출물이다. 완성 초안·유연한 절차의 구현 자체와 광범위한 법률 성능 도입은 구별한다. O5–O7은 active, sprint/마일스톤은 완료가 아니다.

- #272 남은 일: 기존 fwd-11 직접 변형의 독립 리뷰가 timeout으로 미판정이다. `model_era/evidence/fwd11-variants-*`에서 AC1을 재개한다. 별도 형식 fixture PASS와 원본 변형 검증을 혼동하지 않는다.
- #323 남은 일: Opus 고정 계약 사례에서 미제공 별첨을 부재로 단정한 B1, 의미 경계 보완 후에도 같은 서술을 남긴 B2를 검토한다. 재개 입력/응답·source hash는 `model_era/evidence/*claude-contract*`. 새 금지어·형식 강제로 점수를 맞추지 말고 사실 근거와 결론 강도를 평가한다. 독립 재검토와 필요 시 반복/holdout 후 닫는다.
- #325 남은 일: manifest 준비는 성공했으나 Grok 환경/실행 실패, Claude SaaS 양군 timeout으로 품질 비교 불가. 검색 순서 runtime은 유지. `model_era/evidence/privacy-execution.json`의 조건·호출 순서에서 재개하되 timeout을 모델 성능이나 NO-GO로 세지 않는다. tags·반복·incident holdout 미측정.
- 그 밖의 완료 표시는 commit에 담긴 구현·검증/보고 완료이며 merge·release·배포 승인이 아니다. 고정 의미 fixture의 독립 모델 판정은 expert gold가 아니다. 실제 새 출력의 pending 기록은 자동 PASS로 바꾸지 않는다.

## Progress

- 2026-09-08 구현: e05ecda 기준선 보존, 승인 core 구현·죽은 소비자/검사 제거, 독립 Grok 최종 리뷰의 병렬 pending 종료·상태 중복 집계·live 축 정렬 지적 처리. 검증 가능한 통합 commit과 draft PR로 인계한다. #272/#323/#325 잔여를 열어 두며 sprint는 active다.

- 2026-09-08 실행: `codex/milestone-8-model-era-refresh`에서 착수. 기존 계획 변경 보존, e05ecda detached worktree와 42개 runtime 파일 SHA256 manifest 보존. #318 spec 목표 계약 구현, #271 격리 setup/실행 상태 구현(52개 관련 검사), #319 인덱스 삭제·소비자 통합 후 현재 날짜 O1 PASS/O2 11+14 PASS 및 전체 119 unit PASS. 독립 리뷰·live 검증·통합 전까지 해당 항목은 in-flight다. #321 native writer와 #320 평가 준비 writer는 파일 소유권을 분리했다.

- 2026-09-08: 마일스톤 8, 에픽 3개와 실행 이슈 12개를 기록했다. 신규 11개(에픽 2 + 실행 9), 기존 #277/#271/#272/#284 재사용. 각 실행 이슈에 AC·제거/보존 범위·Agent Brief·선행 관계를 기록했다.
- 2026-09-08: native 계획 리뷰와 Claude Opus 5 high 교차 리뷰를 통합했다. freshness 소비자 원자적 정리, known-red 처리, 초안 강행규정 검증, 기존 평가 체계 재사용을 보완했다. 소유권 충돌과 불필요한 기준선 대기 순서를 정리했다.
- 2026-09-08: runtime 구현 미착수. 다음 세션은 최신 작업 상태와 quota를 확인한 뒤 #318/#271/#319의 독립 범위부터 시작한다. 계획 파일의 커밋되지 않은 변경이 있으면 보존한다.

- 2026-09-08: GitHub 15개 본문/마일스톤 readback 및 실행 이슈 12개 effective spec의 AC 해석 확인. backlog doctor 8개 검사 PASS. 기존 완료 sprint reassess 권고는 별도 운영 신호다. 새 세션 프롬프트를 아래 블록에서 추출해 pbcopy하고 동일성을 확인했다.

## 새 세션 프롬프트

아래 블록이 프롬프트 정본이다. 클립보드용 텍스트는 이 블록에서 추출한다.

```text
현재 beopsuny-skill 저장소에서 마일스톤 8을 구현하고 검증 가능한 commit과 draft PR로 정리해줘.
https://github.com/sungjunlee/beopsuny-skill/milestone/8

저장소 루트를 기준으로 backlog/sprints/2026-09-model-era-refresh.md와 backlog/sprints/_context.md, 현행 spec을 읽고, dev-backlog로 각 GitHub 이슈의 최신 본문·댓글·Agent Brief를 확인해 실행해. 기존 계획 문서 변경은 보존하고, 로컬 요약보다 최신 이슈의 작업 정의를 우선해. 이미 승인한 방향은 재확인하지 말고 구체화해줘.

목표는 공식 원문·적용 시점·불확실성·사건 격리를 지키면서 검토용 완성 초안을 지원하고, 불필요한 절차·고정 형식·hint-only 제약·환경 지침·죽은 자산과 관련 테스트를 실제로 제거하는 것이야. 줄 수 감량이나 다른 파일로 이동만 하는 것으로 끝내지 말고, 기존 경량화·평가 도구를 재사용해줘.

네가 오케스트레이터로 최종 판단과 통합을 맡아. 최신 quota와 실제 모델 가용성을 확인하고, 독립 작업에는 native subagents와 $delegate를 적절히 병렬 활용해 구현과 리뷰를 배분해줘. 같은 산출물의 writer는 하나만 두고 leaf는 재위임하지 않게 해. sprint의 의존성과 파일 소유권 인계를 지키되, 고정된 인원이나 불필요한 배치 대기는 만들지 마. 최종 리뷰는 작성 주체와 다른 모델 계열로 수행해줘.

변경 전 e05ecda runtime을 보존해 기준선과 비교하고, 알려진 freshness 만료는 날짜만 연장하지 말고 해결해. 평가 준비 실패·판정 불가·미측정은 PASS나 모델 실패로 바꾸지 말고, 금지 문자열 검사를 없애면서 실제 위반의 의미 평가까지 없애지 마. 법률 정확도·초안 활용성·안전 회귀·비용을 구별해 관측하고, 실험의 채택 여부는 결과에 따라 판단해줘.

각 이슈의 AC에 맞는 구현·삭제·검증과 필요한 README/CHANGELOG/spec 정합성을 마치고, 실제 증거에 맞춰 이슈·에픽·sprint 인계를 갱신해줘. 완료한 범위와 남은 범위, 도입 판단과 검증 한계를 보고해. merge·release·배포는 이번 완료 범위에 포함하지 않아.
```

### GitHub 실행 인계 확인

Draft PR: https://github.com/sungjunlee/beopsuny-skill/pull/327. 구현 commit `45d7ac6`. 15개 이슈 본문·상태를 갱신하고 readback으로 확인했다. 실행 이슈 #318/#271/#319/#320/#321/#284/#322/#324/#326과 에픽 #277은 CLOSED, #272/#323/#325 및 에픽 #316/#317은 OPEN이다. 마일스톤·sprint는 완료 처리하지 않았다. 최종 문서 반영 후 O1 PASS. 원격 Contract Tests 실행은 확인되지 않았으며 로컬 검증과 구별한다.

### 추가 독립 리뷰 완료

사용자 후속 요청에 따라 Sol의 코드/계약 독립 리뷰와 Grok·Opus 교차 리뷰를 병렬 수행하고 root가 최소 수정을 통합했다. false PASS·setup 결합·상태 표시 오류와 hint-only/고정 메모 잔재를 제거했으며 각 범위 재리뷰는 LGTM. 구현 `b97c5e2`, 상세 검토·재현은 `tests/forward_evals/model_era/review-cycle.md`. 전체119개 unit 후 최종 수정 대상21개 회귀, O1/O2·19 corpus rescore·CHANGELOG gate 통과. #272/#323/#325와 에픽 #316/#317은 여전히 OPEN이며 실험 GO/출시로 해석하지 않는다.

- 2026-09-08 추가 인계: 사용자 PR #327 머지 승인. main `909f206` 통합 충돌 해소, Sol 지적 보완·Grok 교차 LGTM 및 실제 Contract Tests PASS. #272 직접 변형 출처 경로 누락은 미완료 유지; #323 최종 runtime Opus 재실행은 세션 한도(01:30 KST reset)로 답변 없이 실패, 품질 미측정. #325도 미판정 유지. 외부 knowledge legacy usage 불일치·미러 upstream WARN 및 릴리즈 대상 스모크가 남아 v0.9.0은 아직 발행하지 않는다. 증거: `tests/forward_evals/model_era/review-cycle.md`.

- 2026-09-08 후속 검증: PR #327은 `d1373c0`으로 머지됐고 main CI PASS. 후속 draft PR #330에 반복·holdout 증거(`75b0740`)와 실제 법인격 사실 승격/예외 적용 요건 보완(`bd43d61`)을 반영했다. 제안 의무에 대괄호를 강제하는 리뷰 지적은 철회하고, 실제 미확인 사실 오류만 수정했다. 최종 runtime 계약 재평가와 스모크는 진행 중이며 #323/#272는 닫지 않았다. knowledge #325는 별도 draft PR #77의 공식 manifest 준비 차단과 재개 조건을 최신 댓글로 인계했고 INCONCLUSIVE다. 상세 실행 상태는 `tests/forward_evals/model_era/followup-plan.md`를 따른다.

- 2026-09-09 현재 인계: runtime `313a919`의 지침 최소 수정은 Grok LGTM·120 unit/O1/O2/rescore·실제 CI PASS. 그러나 수정본 계약과 별첨 holdout의 미제공→실제 결함 단정은 독립 FAIL로 #323 AC5가 남는다. 최종 Claude guardrails/o4 실행과 fwd11의 300초 timeout 후 같은 실행의 늦은 출력은 분리 보존했다. #272 교정3형식의 유한 검증은 유지하고, #325는 private 전송 미승인으로 INCONCLUSIVE다. 실행 중 생긴 미러 upstream WARN도 기록했다. 최신 조율 지시상 새 merge/release/배포는 하지 않으며 sprint·milestone·에픽을 닫지 않는다. 현재 판정과 재개 근거는 `tests/forward_evals/model_era/followup-plan.md` 상단 및 `evidence/direct-duty-*`를 따른다.

- 2026-09-09 Claude 승인 후 최신 인계: #323의 같은 고정 입력 Opus 실험에서 후보1은 독립 Sol FAIL, 후보2는 독립 Sol major_revision/material_concerns를 root가 FAIL로 판정해 모두 되돌렸다. runtime41파일은3e76b25와 일치한다. #325 SaaS·tags 네 조건은900초 상한 내 완료하고 순서·호출한도를 지켰으나, SaaS의 지원 결함과 tags의 미확인 사실 승격 veto가 관측돼 후보 채택NO_GO·타이밍 인과효과INCONCLUSIVE·확대 없음·운영 순서 유지다. #325의 작은 비교와 조건부 확대 판단은 마쳤으며 PR통합 전OPEN이다. strict ingestion ready인 결합 knowledge 후보는 여전히 unpublished/PR77·78 draft다. Private 전문은 공개하지 않는다.120 unit/O1/O2/rescore는 PASS지만 #323AC5와milestone·epic은미완료이며 출시하지 않는다. 최신판정은 followup-plan 상단과 knowledge-claude-initial-pairs.json을 따른다.

- 2026-09-09 입력 구성 보완: fixed/no-tools 패킷에 기존 research-workflow·source-grading 전문을 추가했다. runtime 정책은 유지하고 A는 준비만 검증했다. B Opus5 high 1회에서도 별첨 미제공→부존재 단정이 남아 root FAIL·확대 없음이다. #323 AC5 미완료, #325 NO_GO 완료 판단 및 #272 유한 검증은 유지한다. 상세 증거는 followup-plan 최신 입력 구성 절과 core-contract-opus.json에 보존한다.

- 2026-09-09 구조 정리: 요건/수단 문구 후보는 고정 Opus 실행 FAIL로 되돌렸다. 별도로 출처 상태→사안 결론 대응표를 삭제하고 기존 등급·검증 계약에 참조를 모았으며, 사건 사실 검증 범위와 하급심 라벨을 맞춰 Opus 코드 LGTM을 받았다. 같은 고정 계약 1회는 법정 의무와 제안 수단을 혼동하는 단정이 남아 root·독립 Sol 전체 FAIL이다(축별 판정 차이는 별도 보존). 구조 정리는 유지하되 회귀 해결로 채택하지 않으며 반복·holdout 확대 없음.120 unit/O1/O2/rescore PASS. #323 AC5와 최신 runtime 릴리즈 스모크는 미완료다. 사용자의 조건부 merge·release 승인에도 완료 증거가 없어 draft·0.8.0을 유지한다. 상세는 followup-plan 최신 절과 binding-* 증거.

- 2026-09-09 자가검증 정리: 중복 차원별 목록·역참조를 삭제하고 기존 정본에 연결했다. 고유 데이터 무결성 표시 의무는 유지해 Opus 코드 재검토 LGTM. 고정 계약 1회는 미제공→부재/법적 근거 미성립 단정으로 root·독립 Sol FAIL이며 활용성·행동 권한은 PASS다. 구조 정리는 유지하되 회귀 해결 채택·반복·holdout 확대 없음.120 unit/O1/O2/rescore PASS, 소스 OK3/WARN2/FAIL0/미설치2. #323 AC5·최종 runtime 스모크·출시는 미완료다. 상세는 followup-plan 최신 절과 selfverify-* 증거.

- 2026-09-09 review mode 정리: 중복 출처·태그·산출물 규칙을 삭제하고 모드 고유 값·실제 로드 경로를 보존해 Opus 코드 LGTM. 고정 Opus 1회는 법정 요건/계약상 수단 혼동 및 미제공 감독 수단 부재 서술로 FAIL이며 완성 초안·직접 통지 의무 보존은 별도 관측이다. fresh Fable A/B 1쌍도 현재 B의 직접 통지 제한 등으로 Sol·root FAIL, 초기 Luna 판정 차이는 보존했다. 두 실험 모두 확대 없음. 구조 정리를 회귀 해결로 채택하지 않으며 #323 AC5·최종 runtime 스모크·출시는 미완료다. 120 unit/O1/O2/rescore PASS, source OK3/WARN2/FAIL0/미설치2. 상세는 followup-plan 최신 절과 review-mode/fable 증거.

- 2026-09-09 최종 runtime 스모크: `8fad7d8`의 guardrails12/o4 8건을 기존 병렬 runner로 실행 완료했다. 실행 오류·timeout0이며 실제 의미 위반은 독립 판정과 root 통합으로 보존한다. 검증용 미러를 upstream으로 실제 갱신해 source OK4/WARN1/FAIL0/미설치2, 120 unit/O1/O2/rescore PASS. 스모크 실행 완료와 게이트 통과를 구별하며 #323 AC5·릴리즈는 미완료다. #272 유한 검증과 #325 작은 비교 NO_GO 완료 판단을 유지하고 draft·0.8.0·milestone/epic OPEN을 유지한다. 상세는 followup-plan 최상단 및 final-runtime-smoke 증거.


### 2026-09-09 — 최종 스모크의 사용자 전제 채점 오탐 수정

#333은 별도 scorer 유지보수로 처리했다. fwd-07의 절차 단어 검사를 기존 hash-bound 의미 수신처로 이관하고 실제 응답·미검토/검토 FAIL 대조군을 검증했다. 19 corpus 중 fwd-07 8건의 판정 차이와 이전 기대값은 `premise-scorer-rescore-delta.json`에 보존하며 PASS 승격은 없다. #323 독립 감사는 해당 경계의 실제 로딩 후 모델 불이행을 재확인했고 정당화된 새 runtime 수정은 없었다. runtime8fad7d8·#323 AC5 미완료·릴리즈 NO_GO를 유지한다. #333은 마일스톤 완료의 대체물이 아니다.


### 2026-09-09 — Astra native profile 유한 검증

동일 고정 질문·원문·현재 runtime으로 Astra medium 초기 A/B와 B 반복·별첨·사건 분리 holdout을 완료했다. Grok 독립5건 PASS; root는 기준선 A의 미제공/부재 표현을 REVIEW_REQUIRED로 유지하고 현재4건에서 중대한 위반은 확인하지 않았다. 반복 초안의 조문 지칭 모호성은 편집 항목으로 보존한다. 비용·편집 부담 감소는 미측정이므로 채택 INCONCLUSIVE이며 이전 Opus/Fable·필수 스모크 실패는 변하지 않는다. #323·출시·milestone/epic은 완료 처리하지 않았다. 상세는 followup-plan의 Astra 절과 astra-profile-qualification.json.

- 2026-09-12: PR330 현재 범위를 재확인했다. runtime은 #334에 이미 반영돼 main과 동일하고, 남은 평가 기록·준비기·보존 출력 회귀를 별도 통합한다. 현재/최종 표기를 당시 commit에 한정하고 main #336 테스트 분리를 합쳤다. 준비기 잠금·참조·평가 정보 비유입 CLI 회귀를 추가했다. 실행·검증 범위는 followup-plan 상단, 작업 완료 판정은 GitHub #272/#325/#323이 정본이다. #323·릴리즈는 열린 상태다.

- 2026-09-12 통합 완료: PR330은 평가 기록·준비기·회귀 범위로 main f6d0737에 병합했고 main CI도 PASS다. #272·#325는 한정된 AC 근거로 종료했다. #323 AC5·에픽·milestone·릴리즈와 이 sprint는 열린 상태다. agy Gemini3.8 Flash medium 보조 리뷰는 최종 판정 없이 1055.4초 후 필요한 primary 리뷰·CI 완료에 따라 종료했다(dispatch_cli_error, interrupted); 통과 근거에 포함하지 않는다.

- 2026-09-12 방향 반영: #316 종료, #323의 한정된 profile·근거 대조 실험 설계와 AC5 범위 명확화, #317 인계 갱신. 가족 실사용 #341과 미래 확장 검토 #340을 분리했다. runtime/평가 원본은 변경하지 않았고 실험은 미실행이다.
