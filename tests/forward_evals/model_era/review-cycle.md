# PR #327 독립 리뷰·최소 수정 사이클

2026-09-08. 기준 `cfd24a9`, 원래 비교 기준 `e05ecda` 유지. Root만 수정했고 리뷰어는 read-only로 분리했다. 리뷰 승인 범위는 구현·계약·보고이며 법률 성능 GO나 #272/#323/#325의 미완료 AC를 대신하지 않는다.

## 발견 → 수정 → 재검토

| 범위 | 재현된 문제 | 최소 수정 |
| --- | --- | --- |
| 캡처 | captured-only의 unknown/0개가 PASS, null이 문자열 None으로 PASS | 미매칭·빈 평가 집합 및 비문자열 입력 거부. 중복 ID 덮어쓰기 거부. 동일 loader의 두 목록 분기 통합 |
| setup | setup context hash 존재만 확인 | 캡처된 execution hash와 64hex·동등성 검사. 과거 runtime을 현재 runtime hash와 혼동하지 않음 |
| 파일 경로 | prompt ID로 출력 디렉터리 탈출 | config/packet/command 입구에서 동일 slug 검사 |
| 판정 표시 | FAIL+pending을 INCOMPLETE로 표시, pending 소실을 완화로 오표기 | pending-only에만 INCOMPLETE; pending 제거와 실제 실패 제거 구별. 빈 rescore 출력도 UNSCORABLE |
| 검토 기록 | 동일 작성자·검토자, 잘못된 일자도 reviewed로 수용 | 기존 metadata에서 ID·작성자/검토자 구분·ISO 일자 확인. 의미 판정기나 새 기록 체계 추가 없음 |
| 계약 자산 | clause 후보 머리말이 hint-only와 삭제된 include_* 필드를 지시 | 고아·구형 주석 삭제; 실제 후보 데이터 보존 |
| 출력·명세 | unknown-role 확인 ceremony, ledger/supports 필드, 고정 메모·면책·자가검증 잔존 | schema 키는 유지하며 적용 범위를 좁힘. 템플릿 블록·죽은 CSS·문자열 고정 검사 삭제. 실제 한계는 관련 위치에 표시 |
| 중복 코드 | retired tier 자동 부착과 validator의 별도 intent map | 기존 평가기 부착 함수를 재사용하고 죽은 분기 삭제 |

Sol high의 코드/계약 독립 리뷰는 각각 위 문제를 수정한 뒤 **LGTM**. 코드 리뷰어는 관련31개 테스트 및 shell 구문을 확인했다. Grok4.6 high의 첫 리뷰도 unknown/0개 PASS·혼합 상태·setup 결합 누락을 독립 재현했다. Grok은 round2에서 빠진 문서 diff를 요청했고, round3에서 삭제한 계약·템플릿과 의미 수신처를 함께 확인한 뒤 **LGTM**. Opus는 수치·hash 무결성을 확인하고, 보고 시제·재현 범위·과제별 metadata 지적 해소 후 마지막 CHANGELOG 구조 수정까지 round4에서 확인해 **LGTM**.

## 검증

전체119개 unit PASS 후 마지막 빈-output rescore 정렬 및 회귀를 포함한 focused21개 PASS. 통합 O1/O2 PASS(11 outputs/13 unsafe), 변경 Python8파일 compile, diff whitespace 검사 통과. 기존19개 corpus 판정은 rescore 기록으로 확인한다. 새 문자열 금지나 고정 메모 형식 테스트를 추가하지 않았다. 회귀 테스트는 잘못된 입력·false PASS·증거/상태 결합을 직접 검사한다.

과거 모델 응답·원문·평가 baseline은 덮어쓰지 않는다. 현재 runtime 수정으로 옛 paired 응답이 최종 runtime의 재실행 결과가 되지는 않는다. 원격 CI와 모델/전문가 법률 검증은 로컬 코드 테스트와 별개다.

## 실행·quota 기록

[기계 판독 기록](evidence/review-cycle.json)에 각 검토 범위·결과, 검증 로그와 source hash를 남긴다. 토큰·비용 미제공 값은 0으로 바꾸지 않는다. 아래 quota는 해당 계정 창의 관측이며 이번 작업만의 소모가 아니다.

- Codex Pro, 12:06:46Z, 주간24% 사용/76% 잔여, reset 09-15 10:56:38Z. source OAuth, confidence exact. 5시간/월간 및 pace·소진 ETA unknown; 별도 credits0.
- Claude, 12:07:39Z, 5시간14%/86%, reset 09-08 16:29Z; 주간1%/99%, reset 09-12 15:59Z. source claude, confidence percentOnly. 5시간 pace onTrack, 당시 ETA3h58m; 주간 lasts until reset. 앞선 세션 snapshot과 차이가 커 실행별 차감으로 추론하지 않음.
- Grok SuperGrok Heavy, 12:26:05Z, duration 미제공 창19%/81%, reset 09-13 15:42:04Z, lasts until reset. source grok-cli-proxy, confidence unknown. 주간·월간으로 임의 재명명하지 않음.

Opus 후속 지적 중 과거 합집합 hash와 신규 과제별 hash의 시제를 명확히 구별했고, 신규 필드명은 `task_runtime_inputs`로 정리했다. builder는 항상 SKILL과 해당 iteration의 source_references를 읽는다. 기존 builder를 바꾸거나 별도 추적 체계를 추가하지 않고 두 과제 실제 context의3/8개 입력·hash를 준비 probe로 대조했다. `per_clause_override`는 현행 runtime에 없는 퇴역 키여서 고아 주석을 복원하지 않았다. 중간 working-tree 변경은 root가 독립 리뷰 지적을 통합하던 승인된 수정이며 자동 오염이 아니었다.

최종 승인: Sol 코드/계약 두 범위, Grok 코드·계약, Opus 증거·보고 모두 LGTM. Grok이 언급한 잘린 주석은 이미 삭제된 부분이며 복원하지 않았다. 비차단 문장·푸터 열/CSS·죽은 토큰은 정리했다. Opus가 발견한 CHANGELOG Added 누락/Changed 중복은 항목 내용 보존 후 병합했고, 섹션 순서·유일성 assert PASS. 구현 commit `b97c5e2` 후 인계 변경은 CHANGELOG 구조와 검토 기록·sprint뿐이다. 원격 Contract Tests 실행은 여전히 확인되지 않았으며 CodeRabbit 상태만 SUCCESS다.

최종 quota 재조회(12:48:22Z): Codex Pro 주간42% 사용/58% 잔여, reset 09-15 10:56:38Z, OAuth/exact, pace·ETA 및 다른 창 unknown. Claude/Grok 재조회는45초 timeout으로 unknown이며 마지막 성공 snapshot을 소진으로 바꾸지 않는다. 모델 리뷰 호출은 모두 정상 완료했고 개인별 소비량으로 quota 차이를 귀속하지 않는다.


## main 통합 — 2026-09-08

`909f206`의 plugin metadata drift 검사, knowledge usage 거부, corpus 테스트 분리를 보존했다. 삭제한 mandatory asset을 대상으로 한 partial-refresh fixture도 제거했다. 해당 과거 기록은 main 이력에 남아 있으며 날짜 연장으로 현재 검증을 대체하지 않는다. corpus별 옛 PASS/문자열 FAIL 앵커는 현행 의미 검토 대기와 구별하고, 19 corpus 전체 baseline 일치 검사와 원본은 유지했다.

개인 절대 경로의 sibling knowledge checkout을 읽는 테스트는 제거했다. 임시 자산 5개로 실제 build_packet을 검증하는 기존 검사와 현행 usage 수용/구형 usage 거부 검사는 유지한다. 제거 전 실제 로컬 통합은 `audit_only`와 `post_search_audit_only` 불일치로 실패했다. 외부 지식 자산의 호환성은 해결되지 않았고 ready로 보고하지 않는다.

통합 후 118 unittest, O1, O2(11 outputs/13 unsafe), 19 corpus 재채점(66 메시지, 변화 0), diff whitespace 검사가 통과했다. 소스 도달성은 WARN(OK 2/WARN 3/FAIL 0/미설치 2): 두 로컬 미러 upstream 불일치, 법망 공지 중단, law.go.kr 두 링크 HTTP 200. HTTP 성공은 조문 내용·적용 시점 검증이 아니다. #272/#323/#325 및 릴리즈 스모크의 남은 검증은 유지한다.


추가 인계: Sol 독립 검토가 개인 체크아웃 검사 삭제로 생기는 `--knowledge-root` URL 재매핑 검증 공백을 지적해, 기존 5자산 임시 manifest 검사에서 한 자산을 raw URL+임시 root로 읽도록 바꿨다(나머지는 file URL). 해당 5 tests PASS. 외부 지식 자산을 수정하거나 불일치를 통과시키지 않았다.

`a0ce843`의 불변 runtime으로 #323 고정 계약 입력을 재준비했으나 Opus 5 high가 4.336초에 세션 한도를 반환해 답변 없이 종료했다. reset은 2026-09-09 01:30 KST이며 자동 재시도하지 않았다. `evidence/merged-contract-execution.json`의 판정·비용은 null/미측정이다. #272 직접 변형을 Sol이 읽기 전용 검토한 결과 원본·산문·짧은 답변 일부에서 실제 출처 경로가 복원되지 않아 AC1은 유지한다. 원본을 실패 대조군으로 보존하고 교정 변형을 따로 검증해야 하며 역사적 법률 사실을 현재법 검증으로 쓰지 않는다.

Quota 관측: 2026-09-08 13:05:21Z Grok SuperGrok Heavy primary used 20%/잔여 80%, reset 2026-09-13 15:42:04Z, pace reset까지 유지(source grok-cli-proxy, confidence 미제공; 창 길이 미제공, 다른 창 unknown). Codex Pro 주간 used 46%/잔여 54%, reset 2026-09-15 10:56:38Z(app API, 다른 창·pace unknown). all-provider와 Claude quota 조회는 45초 timeout으로 unknown이며, 이후 실제 Claude 호출에서 세션 한도 도달이 확인됐다. 잔여율을 추정하지 않는다.


최종 통합 리뷰: Grok 4.6 high가 통합 및 마지막 개인 경로 제거/URL 재매핑 보완 모두 LGTM으로 판정했다(`evidence/main-integration-review.json`). `bec1ac1`의 실제 GitHub Contract Tests가 PASS했다([run](https://github.com/sungjunlee/beopsuny-skill/actions/runs/34230436637)). CodeRabbit 성공 상태는 manual review required로 자동 검토를 건너뛴 것이므로 독립 코드 리뷰 근거로 세지 않는다. CHANGELOG PR gate와 Python compile도 PASS. 사용자가 PR #327 머지를 명시 승인했으며, v0.9.0 발행은 남은 AC와 태깅 커밋 스모크가 충족될 때까지 보류한다.
