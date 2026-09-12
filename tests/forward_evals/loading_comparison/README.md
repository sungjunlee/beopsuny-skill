# Claude 로딩 경로 비교 — 2026-09-12

**정상 스킬 로딩은 확인됐지만 회귀 해결은 입증되지 않았다.** 대표 사례 2건에서 각 경로 1회씩 유효 관측을 얻었다. 정상 로딩 두 출력 모두 중대한 문제가 남아 사전등록한 반복·holdout 확대 조건을 충족하지 못했다. runtime 정책·버전은 유지하며 #323 AC5와 v0.9.0 릴리즈 게이트는 미충족이다.

| 사례 | 기존 주입 | 정상 스킬 로딩 |
| --- | --- | --- |
| 고정 계약 | REVIEW_REQUIRED | FAIL — 책임한도 변경을 강행규정으로 분류; 미제공 감독 수단을 없다고 서술 |
| 대외 회신 | FAIL — 원문 없는 조항의 불균형·일방성 단정 | FAIL — 나머지 조항 수용·본 조항만 조정하면 마무리 가능하다는 미확인 단정 |

[최종 판정과 실행별 연결](result.json)에 유효 4건(FAIL 3, REVIEW_REQUIRED 1), 제외 1건을 분리했다. 실행은 5건 모두 종료0으로 완료됐다. 법률 품질 판정은 모델 의미 리뷰이며 전문가 gold가 아니다. 초안의 편집 가능한 골격 제공과 근거·사실 오류를 구별한다. 원문에 없는 새 협상조건을 제안한 것 자체는 실패 근거가 아니다.

## 비교 조건과 로딩 증거

준비 시점 `9c03725`, 실행 당시 main `4022d86`이며 runtime 41파일의 내용은 같다([manifest](runtime-manifest.json), [검증](verification.json)). 사전등록·runner의 `runtime_commit`은 준비 시점 내용 식별자다. 기존에 통합된 패킷 준비기로 고정 입력을 다시 만들었고 runtime 규칙은 수정하지 않았다.

- CLI 2.1.269, 요청 모델 `claude-opus-5`, effort `high`, 각 900초+강제 종료 유예10초, fresh process, 자동 재시도0.
- legacy는 과거 최종 smoke의 별도 `--safe-mode --restricted --system-prompt` adapter다. 저장소 기본 append runner와 구별한다.
- native는 기본 system을 유지하고 복사한 plugin을 `--plugin-dir`로 제공했다. 질문에 추가 slash 호출을 붙이지 않았으며 실제 `Skill(beopsuny:beopsuny)` 호출, 성공 반환, 확장된 SKILL 본문과 기준 경로를 보존했다. YAML frontmatter를 제외하고 strip한 본문 전체가 원본과 일치한다. 고정 계약에서는 reference 7개를 실제 읽었다.
- 두 arm의 질문·법률 자료와 runtime 내용은 같다. fixed legacy는 완성 context/no-tools, fixed native는 필요한 runtime reference를 선택해 읽는다. external은 같은 동결 미러와 Read/Glob/Grep 권한을 받으며 native에 Skill이 추가된다. 기본 system·번들링·참조 선택·읽는 시점이 함께 달라지는 **로딩 경로 비교**다. system-prompt 하나의 인과효과나 모델 일반 성능 차이로 단정할 수 없다.
- 고정 base context hash는 `3807999aec556f9db464e159e69691e00a6ff1b586c7483673bcd4a1c056deae`, 질문은 `f19e9388e90233df3de69b123a03e2afde655eb022b607927c6b34af27732ed6`다. 실제 legacy system에는 공통 환경 설명이 더해져 hash가 다르다. native는 context 파일을 주입하지 않는다. `pre-execution.json`에 실제 argv·system/append hash를 따로 남겼으며 native 기본 system 전문은 수집하지 않았다.
- 실제 주 모델은 init과 modelUsage에서 Opus5로 확인했다. **모든 실행에 Haiku4.5 보조 사용도 보고됐다.** 용도는 미확인이다. Opus 단독 비용이라고 부르지 않는다. 실행별 USD는 CLI의 list 가격 보고값으로 Max 실제 청구액이 아니다. 표본 1회로 지연·비용 개선을 추론하지 않는다.

## 준비 오류와 통제 감사

[최초 사전등록](preregistered.json)은 당시 PREPARED 상태 그대로 보존했다. [실행 전 보완](preregistered-amendment.json)은 기존 완전 패킷 준비기 적용과 양쪽에 동일한 runtime 파일 읽기 허용 설명을 기록한다. 최초 경로 증명 추출기는 `/tmp`와 `/private/tmp` 별칭을 잘못 구분했다. 실제 probe의 성공/실패 대조로 교정했으며 [추출기 교정](extractor-correction.json)을 보존한다. 로딩 probe는 품질 관측이 아니다.

최초 external legacy(`084335`)는 준비 context에 다른 사건 setup이 포함됐다고 잘못 가정해 실행했다. 실제 target에는 없고 judge에는 있던 정보이므로 **INVALID_SETUP / INVALID_REVIEW_INPUT**으로 제외한다. 답변·잘못된 리뷰도 원래대로 보존한다. [교정 사전등록](setup-correction-preregistered.json)을 남긴 후 legacy 1회만 대체 실행(`085034`)했고 유효 native는 재사용했다. 교정 실행에서는 실제 setup 바이트·질문·runtime·미러·권한이 대응한다. 이는 품질 실패의 맹목 재시도나 조건부 확대가 아니다.

[최초 감사](control-audit.json)와 [교정 실행 감사](corrected-control-audit.json)는 보존 trace와 actual argv를 검사한다. `summary.json`의 `setup_candidates`는 휴리스틱 후보이며 최종 판정이 아니다. cwd의 빈 Glob과 거부된 부모 경로 탐색은 성공한 범위 밖 읽기로 세지 않는다. 관측된 성공 읽기는 자기 plugin과 공유 data 안에 있었다. 두 미러는 교정 실행 후에도 지정 HEAD와 clean 상태였다.

세션 설정으로 개인 memory·hooks·추가 skill을 끄고 target init에는 beopsuny만 나타났다. 다른 skill 호출이나 개인 파일 본문 유입은 관측되지 않았다. 이 증거가 전역 내부 상태·상속 환경변수 전체나 OS 물리 격리를 증명하지는 않는다. 공식 동작 설명은 [Claude skills](https://code.claude.com/docs/en/skills)와 [settings](https://code.claude.com/docs/en/settings)를 참고했다.

## 판정의 범위

각 출력은 모델·arm을 숨긴 입력으로 GPT native 독립 검토를 받았다. reviewer의 backend model id와 비용은 반환되지 않아 특정 GPT 버전으로 표시하지 않는다. 질문·실제 제공 자료·전체 답변을 읽었으며 external은 실제 접근한 법령 구간만 제공했다. 공개 reviewer 입력의 rubric은 판정 기준이고 기대 정답은 아니다.

Root는 전체 답변을 읽고 리뷰를 통합했다. fixed native의 F2(동의 경로·거부 항목)는 표현상 이견이 있어 결정적 veto로 쓰지 않는다. F1의 법정 요건/협상 수단 혼동과 F3의 미제공 사실 단정으로 FAIL을 유지한다. external native의 초안 골격은 존재하며 independent utility FAIL을 '초안 미제공'으로 확대하지 않는다. 교정 legacy는 다른 사건의 30억 한도를 현재 사건으로 옮기지 않았지만 현재 계약의 불균형·일방성 단정이 남았다. 실제 외부 송부는 없었다.

## 검증과 인계

main `4022d86`에서 unit 136건, O1, O2(11 outputs/13 unsafe), rescore(19 corpus/94 messages, delta0)를 통과했다. [검증 로그](checks/)는 소스 도달성 OK2/WARN3/FAIL0/미설치2를 구별한다. 비교의 두 동결 미러는 최신 upstream과 다르며 이번 비교 중 갱신하지 않았다. 현재 운영 최신성 통과 근거로 쓰지 않는다.

외부 knowledge main `f1561d1`에서 core/overlay의 `post_search_audit_only`와 stable manifest hash 일치를 재확인했다([메타데이터](knowledge-usage-status.json)). 기존 usage 용어 불일치는 해소됐지만 전체 ingest·품질·채택 검증을 뜻하지 않는다. 비공개 자산 본문은 포함하지 않았다.

#272·#325·#316은 현재 CLOSED 상태를 유지한다. #323 AC5·#317·milestone·sprint·릴리즈는 완료 처리하지 않는다. 기존 필수 smoke의 실패는 이 2사례 실험으로 대체되지 않는다. 이번 기록은 로딩 가설의 유한 검증을 마치며, 같은 질문 반복이나 금지 문구 추가를 정당화하지 않는다.

## 파일 읽는 순서

`result.json` → 각 run의 `root-adjudication.json` → `final-answer.md` / `review-input.json` / `independent-review.json` 순으로 본다. `summary.json`의 pending 문구는 추출 당시 원본이며 최종 판정은 root 파일에 있다. 실제 argv는 `pre-execution.json`, 도구 결과는 `tool-trace.jsonl`, native 본문 로딩은 `skill-load-proof.json`에 있다.

원시 stream·stderr·인증 정보·비공개 knowledge 본문·모델 thinking은 공개하지 않는다. `runner-snapshots/*.txt`는 당시 로컬 경로를 사용하는 평가기 보존 사본이며 production runner나 바로 실행할 도구가 아니다. 모든 파일 무결성은 `artifact-manifest.json`으로 확인한다(자기 자신 제외).
