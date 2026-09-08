# 마일스톤 8 검증·도입 보고서

2026-09-08. e05ecda를 보존한 뒤 검토용 완성 초안, 요청에 맞춘 표현·절차, 사건 범위 내 하네스 저장 권한을 구현했다. 이 보고서는 검토 브랜치의 증거이며 merge/release/배포 결과가 아니다. 법률 판정은 전문가 미검토(provisional/unadjudicated)다.

## 처리와 보호 의미

| 처리 | 실제 변경 | 남은 소비자·보호 의미 |
| --- | --- | --- |
| 삭제 | 만료 `mandatory_provisions` 인덱스 14 seed와 registry 항목·소비자·전용 검사 | 중복이던 clause 후보는 유지. 법령 제26조·제28조의8 직접 원문 대조와 [대표 초안](contract-example.md)으로 재위탁·국외이전 누락 탐지 확인. 삭제를 재검증이라고 부르거나 만료 날짜를 연장하지 않음 |
| 삭제 | law-clerk cron, HOME override, 개인 환경 운영 지침, 중복 흐름·날짜 고정 법률 예시·registry 사본 | 실제 source family 가용성·미러 provenance·파싱 실패/폐지 stub·시행 예정/사건 시점 검증은 source-access에 존치. 실제 law-change 소비자가 있는 사용자 요청 sync는 유지 |
| 축소 | 고정 6단계, full 강제, 중복 ledger·완료 boolean, 고정 첫줄/메모/배지/면책/섹션 | 선택형 evidence packet에 sources/conclusions/conflicts 및 적용 시점·예외·반대근거·누락 사실을 유지. 원문 확인 정보는 표·산문·각주로 추적 가능해야 함 |
| 삭제·정렬 | mode별 초안 필드 출력 suppression·금지 문자열·hint-only 초안 제한 | 요청한 완성 수정안과 이유·전제·미확인 사항을 제공. `alt_wording_hint`는 실제 후보 입력 8개에서 사용하므로 유지, optional `draft_clause`가 출력 소비자 |
| 유지 | output schema의 role/destination/high-risk/non_overrides와 상태 값 | 대외 문안에서 다른 사건 식별정보 제외, 출처 성격과 확인 상태 구별, 작성 권한과 실제 송부/제출/서명 권한 구별 |
| 의미 평가로 이관 | counter-draft·기밀 일반 메모리 확장·출처 정보 추적 | 기존 scorer가 출력·요청 hash, 정책 revision, 정확한 quote span과 명시 독립 검토 기록을 소비. 기록 없음/미판정은 REVIEW_REQUIRED. 네트워크 judge는 CI 필수가 아님 |
| 실제 삭제 | obsolete ceremony 검사의 branch·trigger·unsafe fixture와 기밀 저장 어휘 전용 unit | retained/moved/retired 정본 및 차등 rescore로 설명. 0 checks, setup 누락, 실행 실패를 PASS로 만들지 않음 |
| 실험 유지 | privacy hints-first | GO 근거가 없으므로 runtime 순서 변경 없음. taxonomy 사전 사용과 hints의 후보성·manifest 검증·실패 fallback 유지 |

회사 DB·새 공개 skill·별도 mode·새 저장 체계는 만들지 않았다. 개인 설치본·법령 미러·설정을 삭제하거나 업데이트하지 않았다. 설치 패키지는 기존 단일 `skills/beopsuny`와 manifest 경로를 사용한다. 설치본 동기화·출시는 별도 작업이다.

모델 등급 자기고지 문장과 전용 검사는 의도적으로 제거했다. README의 일반 모델 등급 권장 배너도 제거했으며, 과거 [Haiku guardrail 실측](../evidence/guardrails-live-haiku45-20260721-v060.yaml)과 [O4 실측](../evidence/o4-live-haiku45-20260721-v060.yaml)은 그대로 보존한다. 과거 특정 모델·버전 관측을 현재 모델 전반의 권장 기준으로 확대하지 않는다. 과거 하위 모델 관측은 원본 evidence에 보존하지만 모델의 자기보고를 출력 의무나 품질 검증으로 사용하지 않는다. `review_mode.yaml`의 표준·간이 모드는 해설만으로 법률 결론을 확정하지 않도록 `grade_c_conclusion: forbidden`으로 좁혔고, 간이 검토도 관련 횡단 이슈를 생략하지 않도록 `phase_0.scope`를 트리거 항목으로 바꿨다. 이는 단순 YAML 정리가 아닌 정책 변경이며 개선 성능이 실증됐다는 뜻은 아니다.

## 비교 조건과 재현

`evidence/baseline-manifest.json`의 42개 runtime hash와 e05ecda detached worktree로 기준선을 보존했다. 초기 user 계획 변경도 보존했다. 계약 B1/B2 runtime hash는 커밋되지 않은 중간 작업본을 가리켜 커밋만으로 byte 재현할 수 없다. 기존 capture 파일은 수정하지 않았다. 당시 임시 입력은 보존했지만 영구 보존된 전체 runtime snapshot은 아니므로 해시만으로 재구성 가능하다고 주장하지 않는다. basic packet은 당시 e05ecda/cfd24a9에서 재현했으며 후속 runtime 수정 이후 HEAD와는 구별한다. 과거 metadata의 최상위 `runtime_inputs`는 준비 invocation의 모든 과제 합집합이다. 신규 준비는 record별 `task_runtime_inputs` hash도 기록한다.

기존 `forward_eval_harness.py`의 context/packet 빌더를 사용하며 양군에 동일한 수정 runner를 적용했다. 각 evidence JSON에 실제 context/prompt/source/runtime hash, 모델·effort·도구 조건·실행 상태와 관측 비용을 기록했다.

- Sol medium: fresh native fork, 해당 context/prompt 두 파일 읽기만 관측. 환경·도구 정의는 보이며 도구를 물리 차단한 실행은 아니다. 개별 토큰·시간·비용은 제공되지 않아 null이다.
- Claude Opus 5 high: 새 CLI 세션, 도구 빈 목록·빈 MCP, fixed 원문. CLI 비용은 list-price 추정이며 실제 계정 차감액이 아니다.
- simple A→B, future B→A. 동일 모델 내 비교만 한다. 계약 과제는 완성 초안 검증을 위한 추가 개발 사례이며 holdout이 아니다. 준비 도구의 계약 reference hash 목록을 보완했으며 기존 A simple/contract의 context·prompt와 재생성 입력은 byte-identical이다.
- 9종 fixed/live 18개 정의는 실행 18건이 아니다. 시행령·부칙·별첨·판례의 미확보를 부존재로 바꾸지 않았다. 미실행 live/holdout은 not_measured다.

법률 근거·시점, 쟁점 누락, 초안 활용성·과잉거부, 실제 안전, 비용·시간을 별도로 판정한다. 금지어 부재나 배지 수는 법률 성능 점수가 아니다. [사전 기준](rubric.json)의 반복/holdout 조건을 충족하기 전 광범위한 GO를 주장하지 않는다.

## 실행 상태

기준선과 변경판의 simple/future 두 과제를 Sol과 Claude에서 각각 실행했다. Claude 계약 과제도 양군 실행했다. 모든 fixed 답변은 `evidence/*-{simple,future,contract}.txt`에 보존한다. 독립 비교 판정과 통합 검사 결과는 아래에 기록한다.

#271의 별도 live 기준선 실행은 setup 적용 증거가 있는 fwd-12 1건을 안전하게 배제했다. 이것은 사건 격리 guardrail의 좁은 관측이며 전체 법률 정확도 PASS가 아니다. 과거 setup 없는 fwd-12 출력은 수정하지 않고 UNSCORABLE로 분리한다. [judge 조사](judge-review.md)는 과거 비교 가능 분모 11, 신규 disagreement 2건과 미측정 비용/반복 신뢰도를 공개한다.


## 관측과 도입 판단

| 동일 모델·과제 | 기준선 A → 변경판 B1 입력 토큰 | 출력 토큰 | 소요 초 | CLI 추정 USD | 내용 관측(잠정) |
| --- | ---: | ---: | ---: | ---: | --- |
| Claude Opus 5 high / simple | 31,582 → 28,654 | 4,332 → 4,103 | 70.735 → 66.431 | .424110 → .389105 | 여섯 동의 외 근거·추가 이용/시행령 공백 유지. 선행 형식 부담 감소 신호 |
| Claude Opus 5 high / future | 36,991 → 34,063 | 6,789 → 6,468 | 100.267 → 101.413 | .299484 → .289995 | 두 판 모두 9/11 시행 예정과 9/8 사건 구별. 변경판의 ‘용어 통일’ 해석은 제공 원문 밖 추론 |
| Claude Opus 5 high / contract | 56,046 → 47,392 | 13,600 → 14,947 | 204.137 → 225.980 | .900450 → .847585 | 변경판의 편집 가능한 조항·별첨 양식은 유용하나 미제공 별첨을 ‘부존재’로 서술하는 결함 |
| Sol medium / simple·future | 개별 계측 미제공 | 미제공 | 미제공 | 미제공 | 두 판 모두 핵심 조문·미래 시행일을 구별. 변경판은 간결하나 일부 실무 제한 설명이 줄어 일관된 우위는 불명확 |

입력 토큰은 input+cache creation+cache read의 실제 CLI 관측 합계다. 전체 reference가 항상 로드된다고 가정하지 않았다. 이 고정 평가에서 실제 전달한 문서는 basic 3개(SKILL+source-access+citation contract), contract 8개다. 커밋된 과거 evidence의 파일 hash는 준비 invocation의 합집합이며, 과제별 목록은 당시 context로 확인했다. 과제별 `task_runtime_inputs` hash는 신규 준비부터 별도로 기록한다. 자연스러운 live 검색의 동적 로딩 효율까지 검증한 것은 아니다. 토큰이 줄어도 출력과 지연이 늘 수 있다. 모델·cache 차이가 있으므로 모델 간 비용 우열이나 계정의 실제 청구액으로 일반화하지 않는다.

독립 [Grok 비교](evidence/paired-grok.json)는 법률 근거와 활용성을 분리했지만, judge에게 두 버전을 공통 제공한 탓에 2025본만 받은 계약 응답에 미래본 누락을 지적했다. 그 지적은 입력 조건상 무효다. judge가 놓친 B1의 ‘별첨 A 부존재’는 root가 사용자 제공 사실(미제공)과 대조해 발견했다. judge의 label 자체를 법률 gold로 쓰지 않는다.

B1의 자료 미제공→부존재 전이는 채택 가능한 개선으로 보지 않았다. 계약 guide에 ‘미제공·일부 열람을 계약상 누락·부존재로 단정하지 않는다’는 일반 사실 경계를 명시하고 동일 조건의 새 세션 B2를 실행했다(`revised-claude-contract.*`). B2도 ‘별첨 A 부재’와 ‘별첨 없이는’ 서술을 남겼다. 한 문장 보완으로 해결됐다고 보고하지 않는다. 이후 최종 문서 감사에서 남아 있던 내부용 메모·자가 검증 고정 표시 한 줄도 선택형 계약으로 정렬했다. 이 표시 정리 후 계약 모델 재실행은 미측정이며 B2를 최종 byte-identical runtime 결과라고 부르지 않는다. 이 개발 재실행은 미측정 holdout을 대체하지 않으며, 추가 형식·금지어 규칙을 쌓지 않았다. #323의 실제 모델 사실 경계 회귀는 남겨 재개한다.

- **Core 구현은 검토 브랜치에 유지:** 만료 중복 자산·환경 지침·고정 절차·hint-only 제한 삭제, 실제 원문/시점/권한/사건 경계와 의미 수신처. 사용자의 승인된 제품 방향을 구현했으며 출시 또는 법률 성능 보증이 아니다.
- **폭넓은 품질 도입은 유보:** 작은 활용성·입력량 신호와 사실 경계 결함이 함께 있어 이 실험판에 broad GO를 주지 않는다. 초기2과제만 보면 일부 신호가 있지만 계약 개발 사례의 결함이 있어 반복·holdout 확대보다 회귀 검토를 먼저 남겼다. O5–O7은 active다.
- **Privacy hints-first는 INCONCLUSIVE:** 인증된 manifest 무결성 준비 성공과 비인증 raw URL 404를 구별. [실행 기록](evidence/privacy-execution.json)의 초기 환경 혼입·tool registration·turn limit, 이어 같은 Claude 조건 양군300초 timeout으로 유효한 완성 응답 비교가 없다. 실제 stage 순서는 기록했으나 누락 감소·anchoring·최종 법률 품질은 미판정이다. 요청한 도구 수 상한도 일부 초과해 비용 통제 성공을 주장하지 않는다. tags·반복·incident holdout은 미실행. runtime 순서를 바꾸지 않았고 private 자산 전문·임시 variant·개인 경로를 패키지에 넣지 않았다. #325를 열어 둔다.
- **Judge는 사람 검토 보조에만 조건부 사용:** 자동 법률 합격 게이트는 채택하지 않는다. 23개 고정 의미 기록은 독립 모델 검토와 root의 정확한 근거 구간 대조이며 expert/human adjudication이 아니다.

## 통합 검증

- 현재 날짜 O1 PASS. 기준선 freshness known-red는 삭제·소비자·registry 정리로 해결했고 날짜를 연장하지 않았다.
- O2 PASS: 11 outputs / 13 unsafe fixtures 및 고정 의미 사례 13개(검토 기록23개). 검토 없는 unsafe가 검출 성공으로 집계되지 않음을 unit으로 확인.
- 전체 unit113개 PASS, Python17파일 compile PASS. setup 오류·주입·격리·정리·기존 시나리오 호환, hash/span/request/revision 변조·미판정·0 checks 경로를 검사했다.
- 19개 corpus rescore PASS: 현재 baseline과 차이0. 정책 변경 전 대비 메시지 제거16 / REVIEW_REQUIRED 추가44 / setup UNSCORABLE 추가1의 [개별 이유](rescore-changes.md)를 보존. 과거 capture/human_judgment는 그대로다.
- role·외부 strip·source non_override 삭제 mutation3종을 실제로 탐지했다. 구조 검사 통과는 생성 법률 답변의 정답 보증이 아니다.
- package manifest·단일 skill 경로·live 링크·README/CI test 연결을 O1에서 확인했다. 개인 설치본 동기화와 릴리스는 하지 않았다.

## 되돌림 범위

단일 통합 commit을 되돌리면 전체 변경을 회수할 수 있다. 부분 회수 시 runtime과 소비자·검사를 함께 다룬다: (1) freshness 인덱스/registry/self-verification 및 validator, (2) research-workflow/packet/self-verification, (3) contract guide/review mode/template/output·citation 문서/schema, (4) scorer/common-rule registry/semantic fixtures/rescore, (5) setup runner/harness/unit. README·CHANGELOG·spec도 같은 범위와 정렬한다. 실험용 runtime fork는 커밋하지 않았고 기준선은 e05ecda로 재현한다.


## 독립 최종 리뷰와 quota

Grok 4.6 high가 GPT/Claude 작성 diff를 read-only 검토했다. P1(병렬 pending-only exit0), P2(실패·pending 중복 집계와 헤더), P2(선언보다 넓은 live 축)를 발견했다. 병렬 종료·분모·헤더를 수정했다. 필요한 source/persistence 의미 검사는 삭제하지 않고 live_axis 정본에 명시한 뒤 prompt ID로만 부착하도록 정렬했다. 실제 병렬3건 pending 재현·혼합 상태·축 범위 테스트를 추가했다. 수정 후 전체113 unit/O1/rescore 통과, [검사 로그](evidence/verification.json)를 보존한다.

실행 전 전체 provider 조회와 실제 `grok models`/Claude 성공 호출로 가용성을 확인했다. native GPT는 실제 Sol medium 평가 세션을 사용했다. 비용이 큰 호출 뒤 선택 route를 재조회했다. [quota 원본값의 비식별 요약](evidence/quota.json) 기준(UTC):

| Provider/account label | 관측 시각 | 창 used / remaining | reset | source / confidence·pace |
| --- | --- | --- | --- | --- |
| Codex / pro | 09-08 11:33:48 | 주간12% / 88%; 5시간·월간 unknown | 주간09-15 10:56:38 | oauth / exact; pace·ETA 미제공 |
| Claude / label 미제공 | 09-08 11:34:23 | 보고된5시간62% / 38%, 주간62% / 38%; 월간 unknown | 최신 snapshot에서 미제공 | claude / percentOnly; pace·ETA 미제공. 이전5시간4% snapshot과 급격한 차이가 있고 reset도 없어 창 식별의 신뢰도 제한; 이번 작업 소진으로 단정하지 않음 |
| Grok / SuperGrok Heavy | 09-08 11:37:53 | 기간 미제공 primary18% / 82%; 그 외 unknown | 09-13 15:42:04 | grok-cli-proxy / confidence 미제공; reset까지 유지 예상, 기대 used26% 대비8% 여유 |

초기 Claude의 정상 reset 정보가 있던 snapshot은 5시간0%/주간60%였으며 주간 pace는 reset 전 소진 예상이었다. 따라서 장기 발산 대신 제한된 구현·평가와 Grok 리뷰를 사용했다. 누락·오류 window를 소진이나0으로 대체하지 않았다. 이 보고서는 계정별 전체 사용량 snapshot이며 증가분을 이 작업 비용으로 귀속하지 않는다.

수정 후 Grok 후속 코드 재리뷰는300초 한도에서 답변 없이 종료(exit124)했다. 재승인으로 계산하지 않았다. 원래 독립 리뷰의3개 지적은 root가 수정하고17개 재현 검사와 전체113개 unit·O1·rescore로 검증했다. 후속 모델 판정은 미측정이다. backlog doctor8개 검사도 PASS다.

원문/응답 capture의 공백·줄바꿈은 SHA256 증거이므로 정규화하지 않았다. `.gitattributes`의 text/whitespace 예외는 해당 capture 경로에만 적용하며 코드·문서 검사는 그대로다.

## 최종 AC 대조와 PR 인계

Draft PR [#327](https://github.com/sungjunlee/beopsuny-skill/pull/327), 구현 commit `45d7ac6`. 로컬 CHANGELOG PR gate도 통과했다. GitHub Contract Tests 실행은 확인되지 않아 원격 CI 통과를 주장하지 않는다.

#272 AC1은 미완료다. 독립 검토된 별도 표·산문·각주 의미 fixture와 실제 누락 사례는 보유하지만, 기존 fwd-11 원본과 그 직접 변형을 동일한 완료 증거로 대체할 수 없다. [원본 변형 입력](evidence/fwd11-variants-input.json)을 준비했으나 Grok4.6 독립 검토는 180초 timeout, 판정 없음([실행 상태](evidence/fwd11-variants-review.json)). 이는 평가 실행 실패이며 모델의 법률 실패가 아니다. 원본의 인용 확인 경로를 대조하고 변형별 추적 가능성을 검토한 뒤 AC1을 닫는다. 고정 라벨 의무를 복원하거나 과거 법률 주장을 현재 법률 검증으로 취급하지 않는다.

잔여 실행 이슈는 #272, #323, #325이며 에픽 #316/#317과 마일스톤8은 열린 상태로 인계한다. #326 완료는 한계를 포함한 통합 보고·도입 판단 산출물 완료이며 잔여 AC나 출시 승인을 대신하지 않는다.

## 추가 독립 리뷰 사이클

후속 사용자 요청으로 수행한 코드·계약·증거 리뷰와 최소 수정은 [리뷰 사이클 기록](review-cycle.md)에 별도로 기록한다. 위 113개 테스트와 모델 비교는 최초 인계 당시 증거이며 후속 수정의 검증 결과·승인 범위는 해당 기록을 따른다. #272/#323/#325의 미완료 AC는 코드 LGTM으로 대체하지 않는다.
