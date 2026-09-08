# 실행 절차와 재현 경계

모델 패킷은 기존 forward_eval_harness가 만든 context.md와 prompt.txt다. 실행은 orchestrator의 bounded one-shot CLI 호출이며 새 제품 runner나 scorer가 아니다. 세션마다 새 프로세스를 사용하고 resume하지 않았다. 공통 cwd는 저장소 밖의 빈 `/tmp/beopsuny-kv-clean`이었다. 환경·전역 지시 감사는 execution-environment.json을 참조한다.

실제 user 입력은 아래 세 부분의 정확한 연결이다. 18개 답변 모두 연결 결과의 SHA-256이 receipt.input_sha256과 같음을 다시 확인했다.

1. 공통 prefix (끝에 줄바꿈 두 개): `Use the following supplied product context for the task. The task-specific fixed-source restriction takes precedence over generic instructions to research live. Do not call any tools.`
2. 해당 context.md 전문
3. `\n\n# User task\n` + 해당 prompt.txt 전문

각 receipt.command의 마지막에 이 입력 전체를 하나의 argv 원소로 넘겼다. Grok의 마지막 `-p`는 그 입력을 받는다. stdin은 DEVNULL이다. stdout/stderr를 동시에 파일로 비우는 supervisor가 모델 호출 1,800초, READY probe 120초에 종료하도록 했고, 종료 시 SIGTERM 후 최대 10초 뒤 SIGKILL 절차를 둔다. 실제 18개 호출은 모두 제한 안에서 완료됐다. 원문 source와 다른 arm 출력·rubric·메타데이터를 추가 입력으로 읽지 않도록 했다.

Codex는 ignore-user-config·ephemeral·read-only, Claude는 tools 빈 목록·skills/MCP 설정 제한·setting-sources 빈 목록·no-session-persistence, Grok은 built-in tools 빈 목록·web/subagents 비활성·verbatim을 사용했다. 이는 모든 provider의 system prompt가 같거나 Grok MCP가 물리적으로 제거됐다는 주장이 아니다. 실제 완성 기록의 오류 여부·tool event·모델 호출 수를 확인했고 고정 source 실행으로 분류했다.

GPT는 turn.completed와 최종 답변, Claude는 is_error가 아닌 JSON result, Grok은 stopReason=end_turn·num_turns=1의 JSON text를 확인했다. Grok READY probe에서 처음에는 result 키로 잘못 읽었으나 기존 raw의 text=READY를 재파싱했으며 재호출하지 않았다. 원 모델의 reasoning은 이 저장소에 옮기지 않았다.

v1 A는 일반 right-sizing 삭제 오류 때문에 제외했다. v2 A만 다시 실행했고 B/C의 context·prompt 해시가 v1/v2에서 같음을 확인하여 기존 완성 답변을 재사용했다. 수정 후 knowledge memo에 추가한 Evaluation follow-up은 Candidate 절 밖이므로 실제 공급 본문은 결과의 candidate-inputs와 같다. independent-semantic-review는 답변 생산이 끝난 뒤 별도 프로세스에서 모델·arm 라벨을 가린 패킷만 읽었다.

Cache 상태·동시 부하·provider system prompt는 실험의 한계다. 재실행할 때 원문·후보·공통 runtime·model/effort·도구 경계를 다시 동결하고, 새 결과를 기존 답변에 덮어쓰지 않는다. 이 개발 질문의 통제 복구 실행은 독립 반복·holdout이 아니다.
