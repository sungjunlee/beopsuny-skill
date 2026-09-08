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
- [~] #325 [experiment] privacy 검색 힌트 순서의 비용·누락 효과 비교 — 선행: #320, #321. [branch:codex/milestone-8-model-era-refresh] · evidence: `tests/forward_evals/model_era/integration-report.md`

### 초안·표현·평가 계약 순차 정렬

- [~] #323 [contract] 검토용 완성 조항 초안과 수정 제안 지원 — 선행: #318, #322, #319. [branch:codex/milestone-8-model-era-refresh] · evidence: `tests/forward_evals/model_era/integration-report.md`
- [x] #272 [skill] fwd-11 — 절차 모양을 바꾼 답변에서 출처 권위 라벨이 빠졌다 (실위반, 경미) — 선행: #323.
- [x] #324 [tests] counter-draft 금지 문자열 오탐을 의미 평가로 이관 — 선행: #323, #272, #284.

### 통합 검증과 도입 판정

- [x] #326 [release-readiness] 고급 모델 비교·최종 제거 감사·도입 판정 — 선행: #319, #322, #272, #324, #325, #284.

## Running Context

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

완료 범위는 #318/#271/#319/#320/#321/#284/#322/#272/#324 및 #326의 통합 보고·검토용 산출물이다. 완성 초안·유연한 절차의 구현 자체와 광범위한 법률 성능 도입은 구별한다. O5–O7은 active, sprint/마일스톤은 완료가 아니다.

- #323 남은 일: Opus 고정 계약 사례에서 미제공 별첨을 부재로 단정한 B1, 의미 경계 보완 후에도 같은 서술을 남긴 B2를 검토한다. 재개 입력/응답·source hash는 `model_era/evidence/*claude-contract*`. 새 금지어·형식 강제로 점수를 맞추지 말고 사실 근거와 결론 강도를 평가한다. 독립 재검토와 필요 시 반복/holdout 후 닫는다.
- #325 남은 일: manifest 준비는 성공했으나 Grok 환경/실행 실패, Claude SaaS 양군 timeout으로 품질 비교 불가. 검색 순서 runtime은 유지. `model_era/evidence/privacy-execution.json`의 조건·호출 순서에서 재개하되 timeout을 모델 성능이나 NO-GO로 세지 않는다. tags·반복·incident holdout 미측정.
- 그 밖의 완료 표시는 commit에 담긴 구현·검증/보고 완료이며 merge·release·배포 승인이 아니다. 고정 의미 fixture의 독립 모델 판정은 expert gold가 아니다. 실제 새 출력의 pending 기록은 자동 PASS로 바꾸지 않는다.

## Progress

- 2026-09-08 구현: e05ecda 기준선 보존, 승인 core 구현·죽은 소비자/검사 제거, 독립 Grok 최종 리뷰의 병렬 pending 종료·상태 중복 집계·live 축 정렬 지적 처리. 검증 가능한 통합 commit과 draft PR로 인계한다. #323/#325 잔여를 열어 두며 sprint는 active다.

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
