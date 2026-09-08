# Knowledge-value A/B/C validation

이 디렉터리는 #329의 입력 준비와 동결된 실행·검토 기록을 보관한다. 새 runner·judge·rubric을 만들지 않고, [기존 harness](../../forward_eval_harness.py)의 `write_prompt_packets`와 `build_skill_context`로 모델 입력을 쓴다. 판정 기준은 [#320/#326 공통 rubric](../model_era/rubric.json)이다.

`prepare.py`는 모델을 실행하거나 채점하지 않는다. 실행 전 root가 동결한 정확히 두 개의 질문과 하나의 고정 source bundle을 받아 12개 `not_measured` smoke cell을 기록한다. holdout·반복·36회 확대는 생성하지 않으며, 결과와 quota를 본 root의 별도 결정이 필요하다.

## 입력 계약

`--questions-dir`에는 질문 본문만 담은 `.txt` 두 개가 있어야 한다. 파일명 stem이 question ID가 되며, 질문·정답·예시·가설·rubric은 이 준비기가 만들지 않는다.

`--source-bundle`은 아래와 같은 `manifest.json`과 해당 `.md` 파일을 포함한 디렉터리다. 파일 본문은 A/B/C 모든 prompt에 동일하게 넣고, 각 SHA-256이 일치하지 않으면 중단한다.

```json
{
  "access_mode": "fixed",
  "sources": [
    {
      "id": "source-id",
      "file": "source-id.md",
      "sha256": "<sha256 of source-id.md>",
      "official_url": "<optional>",
      "captured_at": "<optional>"
    }
  ]
}
```

`--knowledge-root`에는 S1 loader가 읽는 manifest snapshot과, C가 읽는 두 memo가 있어야 한다. 두 memo의 `## Evaluation Candidate`는 모델에 줄 내용만 담아야 한다. 후보 메타데이터·가설·예시·정답·rubric heading이 있으면 이 준비기는 중단한다.

## Arm boundary

| Arm | 모델 입력 |
| --- | --- |
| A | baseline SKILL의 knowledge-layer 연결만 제거하고 일반 right-sizing을 보존한 사본 + 공통 4 references |
| B | 현재 SKILL + 전체 knowledge-injection + S1 loader가 실제로 렌더한 taxonomy/hints/audit-core/audit-overlay |
| C | 현재 SKILL + 7축 내장 요약을 뺀 knowledge-injection 소비 경계 + 두 memo의 Evaluation Candidate 본문 |

공통 4 references는 `source-access`, `citation-verification-contract`, `privacy_compliance` checklist, `clause_references`다. A도 이 제품 기본 자산은 유지한다. A/B/C의 고정 source bundle과 질문은 동일하다.

## 실행 인계

root가 inputs를 동결한 뒤에만 다음처럼 준비한다. `--max-asset-chars`는 생략할 수 없으며 B의 S1 loader 실행에 그대로 전달된다.

```bash
python3 tests/forward_evals/knowledge_value/prepare.py \
  --knowledge-root /absolute/path/to/beopsuny-knowledge-snapshot \
  --source-bundle /absolute/path/to/sources \
  --questions-dir /absolute/path/to/questions \
  --max-asset-chars 9812 \
  --output /tmp/beopsuny-knowledge-value-ready
```

출력의 `model-inputs/{A,B,C}/<question-id>/{context.md,prompt.txt}`만 모델에 준다. `evaluator-only/preparation-metadata.json`에는 runtime commit, variant diff/hash, source manifest/receipt, loader receipt, context/prompt hash, 12개 `not_measured` cell이 남으며 모델에 주지 않는다. source가 고정 bundle이므로 live 접근이나 live 성능을 주장하지 않는다.

실행 후의 GO/NO_GO/INCONCLUSIVE와 regression veto는 `model_era/rubric.json`을 재사용한다. 준비 성공·hash 일치·loader receipt은 성능, 법률 정확성, 전문가 검증, 실운영 효과의 증거가 아니다.

현재 stable 자산 다섯 개는 기본 1,800자를 모두 초과하므로 기본 준비는 skip/fallback이다. 이번 고정 비교는 `--max-asset-chars 9812`를 명시하고 같은 상한의 loader receipt를 확인했다. 기존 model_era README의 무지정 명령은 더 이상 전체 자산 수신을 뜻하지 않는다. M8 원 작업 디렉터리와 공통 harness/rubric은 수정하지 않았다.


## 2026-09-08 판정

[결과 index](results/2026-09-08/index.json): Sol/Grok의 조건을 맞춘 12셀, 짝 없는 Claude 2셀, 잘못된 A 통제 4셀을 분리했다. 총 실행18회와 probe3회이며 유효 비교12회를 총 호출12회로 표현하지 않는다. Claude quota 포화 후 Grok의 전체 행렬을 사용했고, v1 A의 일반 right-sizing 삭제 오류를 고친 v2 A만 다시 실행했다. B/C context·prompt 해시는 동일했다. `execution-plan.json`에 수정 이유가 있다.

독립 의미 리뷰는 모델·arm 라벨을 가린 유효 답변14개를 공통 source/rubric으로 검토했다. 결론은 **INCONCLUSIVE / research_hold**다. 핵심 판단은 A/B/C에 공통이었고 C만의 뚜렷한 편익이 없었다. C의 AI 답변 두 건은 인쇄/물리 쪽수 표기가 혼동됐으며, 이 관측을 확정된 법적 허위나 인과관계로 확대하지 않는다. 신규 C의 운영 공급·stable/core 승격은 하지 않는다.

`results/2026-09-08/candidate-inputs/`는 실제 공급한 C 본문이다. knowledge memo의 후속 평가 기록은 candidate 밖에 추가됐으며 실제 후보 본문 해시는 같다. `preparation-v1.json`과 `preparation-v2.json`, variant diff, 개별 최종 답변·receipt, 독립 리뷰·라벨 mapping을 보존한다. 원 모델의 내부 reasoning은 이 결과 묶음에 보관하지 않는다. 기존 shared scorer는 실행하지 않아 null이며 전문가/live/독립 반복/holdout도 미실행이다.

입력·원문·비용 필드를 재현할 때 provider의 cache 회계를 같은 의미로 합산하지 않는다. `execution-environment.json`에 CLI 버전·일반 전역 지시·관측된 도구 경계가 있다. 실제 one-shot argv·usage·input hash는 각 receipt에 있고 [실행 절차](execution-protocol.md)에 입력 조립·실행 경계를 남겼다. 별도 provider runner·judge를 제품 코드에 추가하지 않았다.

검증:

```bash
python3 tests/test_knowledge_manifest_ingest.py
python3 tests/test_knowledge_value_prepare.py
python3 tests/validate_skill_contracts.py
```
