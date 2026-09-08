# Model-era comparison (#320, #325)

`../model_era.yaml`는 9종 과제 각각의 fixed/live 정의 18개를 담는다. 현재 실행·도입 상태는 [통합 보고서](integration-report.md)에 기록한다. 기존 guardrail corpus와 과거 evidence는 보존한다. 이 corpus는 표현 일치 채점·검증배지 개수·이상형 답안을 법률 정확도 대용으로 쓰지 않는다.

## 원문과 시점

`sources/manifest.json`에는 실제 `legalize-kr` Git 미러에서 취득한 개인정보 보호법 두 버전의 commit, 공식 URL, capture 시점, 시행일, SHA256과 발췌의 원문 행 연결이 있다. `privacy-2025.md`와 `privacy-2026.md`는 미러 파일 전문을 보존한다. 발췌는 metadata와 제15·26·28조의8·29·34조를 그대로 추출했다. 별도 첨부·시행령·판례 corpus는 확보하지 않았으므로 그러한 결론은 준비된 자료만으로 판단할 수 없다. capture는 공식 사이트 직접 재확인을 의미하지 않는다.

평가 기준일 2026-09-08에 최신 미러 파일은 2026-09-11 시행 예정본이다. 사건 시점에 맞는 버전을 선택하는지가 실제 평가 대상이며, manifest의 `상태: 시행` 문구나 최신 파일명만으로 현행을 확정해서는 안 된다. 소스가 두 버전이라는 사실만으로 다른 개정·경과조치가 없다는 법률 gold가 성립하지 않는다. 모든 법률 판정은 전문가 검증 전 `unadjudicated/provisional`이다.

## 입력 준비와 실행 인계

기존 `forward_eval_harness.py`의 `write_prompt_packets`와 `build_skill_context`를 그대로 사용한다. 새 runner/scorer는 만들지 않았다. `prepare_packets.py`는 같은 source bundle을 양쪽 prompt에 넣고, runtime 루트만 선택한다. 기본 `source_references`는 해당 runtime의 source-access와 citation-verification-contract다. 계약/대외초안 과제는 계약 guide·review_mode·self-verification·output-formats·output schema를 추가로 읽으며 실제 목록과 hash를 metadata에 남긴다. baseline runtime은 사용자가 지정한 e05ecda 원본이어야 하며, runner 수정이나 freshness 변경을 baseline 파일에 복사하지 않는다.

```bash
python3 tests/forward_evals/model_era/prepare_packets.py \
  --runtime-root /tmp/beopsuny-m8/baseline --arm A \
  --output /tmp/beopsuny-m8/model-era-ready
python3 tests/forward_evals/model_era/prepare_packets.py \
  --runtime-root . --arm B --output /tmp/beopsuny-m8/model-era-ready
```

출력은 `model-inputs/{A,B}/{task-id}/{context.md,prompt.txt}`와 별도의 `evaluator-only/*-metadata.json`이다. 모델에는 해당 context와 prompt만 준다. rubric, evaluator metadata, 다른 출력, 저장소 접근을 주지 않는다. 기존 출력은 덮어쓰지 않으며 runtime이 변하면 새 output 경로로 다시 준비한다. 재현하려면 baseline manifest에 기록된 runtime 해시와 이 준비 metadata의 입력 해시를 대조한다. source bundle과 prompt hash는 paired arm에서 동일해야 한다.

기본 smoke는 simple-statute-fixed, future-effective-fixed 각 1회/arm이다. 첫 과제는 A→B, 다음은 B→A로 실행한다. 호출마다 새 프로세스·세션과 별도 cwd를 쓰고 같은 실제 model ID/effort/도구 설정을 적용한다. fixed는 실행기에서 도구를 실제 차단해야 한다. prompt에 금지 문구만 적거나 기본 live runner를 그대로 호출하는 것으로 차단했다고 기록하지 않는다. live는 `--tasks m8-future-effective-live`처럼 명시적으로 준비하며, 양군에 동일한 읽기/검색 도구를 허용하고 실제 access log·확인 원문 revision·시각을 기록한다. 개인 설치 skill, 사용자 설정, 대화 이력 상속을 차단하지 못한 실행은 그 한계를 남긴다.

`missing-annex`, `case-isolation` 두 종류는 holdout이다. `--include-holdout` 없이 준비할 수 없다. 초기 신호가 있는 경우에만 rubric의 반복·확대 조건을 기록하고 해제한다. 18개 정의 중 실행하지 않은 셀은 `not_measured`이며 자동 PASS가 아니다. template 생성이나 source checksum 통과도 모델 성능이 아니다.

## 판정과 관측

`rubric.json`은 모델 입력과 분리된 사전 채택 기준이다. 근거 지지/적용 시점, 쟁점 누락, 초안 활용성, 과잉거부/불필요한 질문, 안전, 비용/시간, scorer 오탐을 각각 기록한다. 실제 위반의 의미는 답변 구간과 근거 구간을 연결해 판단한다. 금지 문자열이 없더라도 날조·사건 전이·미시행 법률 오적용은 veto이며 평균 점수로 상쇄하지 않는다.

준비 metadata의 null은 실행 후 실제 관측치와 그 출처로 채운다. model ID/effort, 세션·실행기 버전과 해시, 도구 allow/deny, 소요시간, input/output/cache tokens, 비용, 소스 접근 로그, raw output 위치/해시를 남긴다. 제공되지 않는 비용·토큰은 null과 unavailable 이유를 유지한다. 준비 실패, 실행 오류, 판정 불가는 성능 실패나 PASS로 바꾸지 않는다. judge 자체 판단은 expert gold가 아니다.

## Privacy 순서 실험

인증된 기존 GitHub API로 취득한 stable manifest 및 5개 asset을 고정하고 기존 ingestion helper로 검증한다. 인증되지 않은 기본 raw URL의 404와 인증된 snapshot 검증 성공은 별개 관측이다. private asset 전문은 이 저장소에 재게시하지 않고 명시적인 snapshot 경로를 사용한다.

```bash
python3 tests/forward_evals/model_era/prepare_knowledge.py \
  --knowledge-root /tmp/beopsuny-m8/knowledge-snapshot \
  --output /tmp/beopsuny-m8/privacy-stages
```

`privacy-saas.txt`, `privacy-tags.txt`는 양군 공통이다. 양군 모두 taxonomy를 먼저 받으며, blind-first는 첫 독립 검색을 마친 뒤 hints를 받고 hints-first는 첫 검색 전에 받는다. authority map audit은 양군 모두 검색 후다. 원본 hints의 usage 표시는 보존하며 실험 supervisor가 hints-first 조건에 한해서 사전 사용을 명시한다. 이를 production 권한 변경으로 해석하지 않는다. 같은 current runtime·모델·법률 source 조건을 쓰고 실제 hints 수신 시점/첫 검색 순서를 로그로 입증한다. 소스가 이미 전부 prompt에 주어진 tool-free 비교만으로 검색 순서 개선을 측정했다고 부르지 않는다.

순서는 SaaS blind→hints, tags hints→blind다. 누락 감소 신호와 새 anchoring 오류 부재가 있을 때만 각 pair를 한 번 반복하고 incident/effective-date holdout pair를 추가한다. 단계 전달을 통제하지 못하면 `INCONCLUSIVE`다. GO가 확인되기 전 runtime 순서 규칙은 유지하고, privacy 외 지식을 활성화하지 않는다. 평가 준비 성공은 GO의 근거가 아니다.

## 기준선 실행 증거

`evidence/baseline-claude-simple.json`과 `.txt`는 오케스트레이터가 실제 실행한 e05ecda A/simple-statute fixed-source 응답을 보존한다. Claude Opus 5 high, 도구 차단·빈 MCP·새 세션 조건이며 외부 측정 70.735초, exit 0이다. 제공된 usage/cost와 실제 output hash, 입력 context/prompt/source/harness hash를 함께 기록했다. 법률 판정은 unadjudicated다. 같은 조건의 B 응답과 후속 비교는 통합 보고서에 연결하며 이 기준선 실행 성공 자체는 법률 정확도·개선·채택 PASS를 의미하지 않는다.
