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

Sol high의 코드/계약 독립 리뷰는 각각 위 문제를 수정한 뒤 **LGTM**. 코드 리뷰어는 관련31개 테스트 및 shell 구문을 확인했다. Grok4.6 high의 첫 리뷰도 unknown/0개 PASS·혼합 상태·setup 결합 누락을 독립 재현했다. Grok은 round2에서 빠진 문서 diff를 요청했고, round3에서 삭제한 계약·템플릿과 의미 수신처를 함께 확인한 뒤 **LGTM**. Opus는 수치·hash 무결성을 확인했고, 중간 runtime과 과제별 metadata의 보고 범위를 재검토 중이다.

## 검증

전체119개 unit PASS 후 마지막 빈-output rescore 정렬 및 회귀를 포함한 focused21개 PASS. 최종 O1/O2 PASS(11 outputs/13 unsafe), 변경 Python8파일 compile, diff whitespace 검사 통과. 기존19개 corpus 판정은 rescore 기록으로 확인한다. 새 문자열 금지나 고정 메모 형식 테스트를 추가하지 않았다. 회귀 테스트는 잘못된 입력·false PASS·증거/상태 결합을 직접 검사한다.

과거 모델 응답·원문·평가 baseline은 덮어쓰지 않는다. 현재 runtime 수정으로 옛 paired 응답이 최종 runtime의 재실행 결과가 되지는 않는다. 원격 CI와 모델/전문가 법률 검증은 로컬 코드 테스트와 별개다.

## 실행·quota 기록

[기계 판독 기록](evidence/review-cycle.json)에 각 검토 범위·결과, 검증 로그와 source hash를 남긴다. 토큰·비용 미제공 값은 0으로 바꾸지 않는다. 아래 quota는 해당 계정 창의 관측이며 이번 작업만의 소모가 아니다.

- Codex Pro, 12:06:46Z, 주간24% 사용/76% 잔여, reset 09-15 10:56:38Z. source OAuth, confidence exact. 5시간/월간 및 pace·소진 ETA unknown; 별도 credits0.
- Claude, 12:07:39Z, 5시간14%/86%, reset 09-08 16:29Z; 주간1%/99%, reset 09-12 15:59Z. source claude, confidence percentOnly. 5시간 pace onTrack, 당시 ETA3h58m; 주간 lasts until reset. 앞선 세션 snapshot과 차이가 커 실행별 차감으로 추론하지 않음.
- Grok SuperGrok Heavy, 12:26:05Z, duration 미제공 창19%/81%, reset 09-13 15:42:04Z, lasts until reset. source grok-cli-proxy, confidence unknown. 주간·월간으로 임의 재명명하지 않음.

Opus 후속 지적 중 과거 합집합 hash와 신규 과제별 hash의 시제를 명확히 구별했고, 신규 필드명은 `task_runtime_inputs`로 정리했다. builder는 항상 SKILL과 해당 iteration의 source_references를 읽는다. 기존 builder를 바꾸거나 별도 추적 체계를 추가하지 않고 두 과제 실제 context의3/8개 입력·hash를 준비 probe로 대조했다. `per_clause_override`는 현행 runtime에 없는 퇴역 키여서 고아 주석을 복원하지 않았다. 중간 working-tree 변경은 root가 독립 리뷰 지적을 통합하던 승인된 수정이며 자동 오염이 아니었다.
