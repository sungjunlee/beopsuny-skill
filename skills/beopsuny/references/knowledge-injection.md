# beopsuny-knowledge 소비 경계

`beopsuny-knowledge`는 법순이의 live legal research를 대체하지 않는다. 현재 법령·하위법령·행정규칙·판례·해석례·공식 자료는 매번 다시 확인하고, knowledge asset은 검색을 넓히고 누락을 점검하는 데만 쓴다.

## 규칙 강도

목적은 knowledge asset이 결론이나 검색 route를 오염시키지 않도록 사용 경계를 나누는 것이다 — 탐색 자유도를 줄이는 고정 절차가 아니다.

Hard rule:

- 법적 결론은 현재 live source와 출처 권위 라벨에 근거한다.
- retrieval hints는 최초 검색 route나 결론 근거가 아니다.
- authority map은 route oracle이 아니라 post-search audit asset이다.
- seed workspace memo와 `Derived Asset Candidates`는 structured runtime asset이 아니다.

Guardrail:

- 개인정보 쟁점이 실질적인 질문에서는 stable manifest 소비를 시도할 수 있다.
- taxonomy는 issue framing과 fact-question expansion에만 쓴다.
- retrieval hints와 authority map은 blind live search 이후 recall/audit에 쓴다.
- manifest 또는 asset 검증 실패 시 knowledge injection 없이 live legal research만 수행한다.

Operational preference:

- 쟁점 분해가 필요 없는 좁은 질문(조문·공식 링크·시행일 확인)에는 knowledge asset을 생략한다.
- 복합 개인정보 질문, vendor/DPA/국외이전/사고대응/광고태그처럼 누락 위험이 큰 질문에는 recall과 audit을 보강한다.
- 사용 여부를 답변마다 설명하지 않는다. 내부 URL, token, 인증 실패 세부사항은 노출하지 않는다.

Privacy 사전지식 — 기본 점검 축:

blind live search 전에 빠뜨리기 쉬운 사실 질문을 떠올리기 위한 보조 프레임이다. 결론을 강제하지 않으며, 개인정보 쟁점이 없는 질문에는 적용하지 않는다.

- 수집·이용: 동의 근거, 목적 범위, 최소수집, 보유기간, 2차 활용
- 제공·위탁: 위탁 vs 제3자 제공 분기, 재위탁 구조, 공개의무
- 국외이전: 저장·접근·백업 경로 분리, DPA, subprocessor 목록
- 안전성 확보조치: 접근권한, 암호화, 접속기록, 내부관리계획
- 정보주체 권리: 열람·정정·삭제·처리정지, opt-out 전파
- 침해사고: 통지·신고 기준, 증적보전, 초기 차단, effective-date boundary
- vendor/company document: 처리방침, DPA, subprocessor 변경일, SDK·태그 이벤트, server-side tag forwarding 경로

기존 번들 자산과의 관계:

- `assets/policies/checklists/privacy_compliance.yaml` — 개인정보보호 기본 자가점검 체크리스트 (번들 fallback).
- `assets/data/clause_references.yaml`의 `data_privacy`/`data_processing` — 계약 조항 검토용 법령 매핑.
- `beopsuny-knowledge`는 위 자산을 대체하지 않는다 — 기본 법령·계약 체크는 번들 자산으로 잡고, 최신 반복 miss·vendor/company document 축·post-blind 검색어 확장·authority audit만 보강한다.
- 충돌하면 현재 live official source와 출처 권위 라벨을 우선하고, 오래된 번들 문구는 확인 필요로 둔다.

## 채널

기본 channel은 `stable`이다. `canary`는 명시적 opt-in replay 또는 integration test에서만 사용한다.

| Channel | 용도 | 경계 |
| --- | --- | --- |
| `stable` | production-like 기본 소비 채널 | validation, replay/readiness evidence, triage disposition을 통과한 privacy asset |
| `canary` | guarded replay 또는 integration test | stable 승격 전 변경을 좁은 범위에서 검증 |

Runtime은 환경이 지정한 manifest source를 사용하며, source 위치와 접근 방식은 integration config에서 관리한다. 기본 채널과 허용 asset key는 `assets/policies/knowledge_manifest.yaml`에 기록한다.

## 소비 순서

```text
user question
-> 개인정보 쟁점이 실질적인지 판단
-> active vertical assets for issue framing (필요한 경우)
-> blind live search
-> retrieval hints expansion (필요한 경우)
-> authority/source audit (필요한 경우)
-> reference context check (필요한 경우)
-> answer from current live sources
```

blind live search 우선은 경계다(Hard rule) — knowledge asset은 최초 검색 route나 결론 근거가 될 수 없다. 나머지 단계 구성은 기본형이며, 경계를 충족하면 질문에 맞게 조정할 수 있다. live search stack은 `references/source-access.md`를 따르고, 모든 결론에 출처 권위 라벨과 verification tag를 붙인다.

- **Domain stage** — structured asset 소비 대상은 `active_vertical`인 `privacy`만이다. seed workspace memo와 `Derived Asset Candidates`는 runtime asset이 아니다: `contracts`, `employment`, `fair-trade` 등 seed memo를 taxonomy, retrieval hints, authority map, benchmark fixture처럼 주입하지 않는다. `watch_candidate`는 독립 domain으로 route하지 않는다.
- **Right-sized 사용** — 생략/사용 판단은 SKILL.md 라우팅 원칙 1(Right-sizing)을 따른다. 국외이전·DPA·subprocessor·vendor support access, server-side tag forwarding·광고 SDK·opt-out propagation, 신고·통지·시행예정 조항·증적보전처럼 사실관계 분기와 문서 누락 위험이 큰 질문에서 사용을 검토한다. manifest 접근·검증이 실패하면 생략한다.
- **Post-blind expansion** — blind live search 이후에만 retrieval hints를 적용한다. 허용: 누락 검색어·동의어·실무/영문 표현 보강, 빠진 source family 확장, 판례·해석례·고시·가이드라인·집행 사례 검색어 보강, anti-pattern 기반 노이즈 경로 회피. 금지:
  - 최초 검색 route 결정
  - 법적 결론 근거로 표시
  - exhaustive checklist처럼 사용
  - supporting memo와 다른 사실관계에 자동 일반화
- **Post-search audit** — authority map은 검색 이후 누락 축을 점검하는 audit asset이다. `authority_map.core`는 반복 검증된 안정 audit 축, `authority_map.overlay`는 빠르게 변하는 live blind spot·regulator 관심축·회사/vendor 문서 축, `source registry`는 canonical source family·observed_at·verification_state 확인. map의 축은 "확인할 축"이지 "정답 후보"가 아니다.

## Manifest 검증

검증 조건의 구현 단일 소스는 `assets/tools/knowledge_manifest_ingest.py`다. helper는 stable manifest와 required asset을 fetch한 뒤 `publication.publish_ready`/`publication.url_status` 게이트, 각 asset의 `sha256`, `schema_version`, `usage_mode`(없으면 `asset_type`·`vertical`·manifest key 기준 허용 사용 범위)를 검증하고, 성공하면 answer 근거가 아닌 보조 `injection_packet`을 만든다. private raw URL은 `BEOPSUNY_KNOWLEDGE_TOKEN` 또는 `GITHUB_TOKEN`이 있을 때만 인증 헤더를 붙인다. 어떤 실패든 기본은 fail-open이다 — `status: skipped`, `continue_live_legal_research: true`로 knowledge injection을 건너뛰고 live legal research만 수행한다. 배포 gate나 fixture 검증에서 실패를 잡고 싶을 때만 `--strict`를 쓴다.

현재 manifest asset key와 허용 usage:

| Key | 허용 사용 |
| --- | --- |
| `taxonomy` | issue framing과 fact-question expansion |
| `retrieval_hints` | blind live search 이후 recall expansion |
| `authority_map.core` | post-search audit only |
| `authority_map.overlay` | post-search audit only |
| `session_schema` | validation/reference |

현재 first wiring에서 stable manifest가 직접 제공하지 않는 `domains.yaml`과 source registry는 runtime 필수 asset으로 취급하지 않는다. 후속 구현에서 필요하면 manifest key와 checksum 검증 대상으로 승격한 뒤 소비한다.

## Local fallback

Production-like runtime의 canonical source는 `assets/policies/knowledge_manifest.yaml`의 stable channel 또는 integration config가 명시적으로 지정한 manifest source다. `../beopsuny-skill` 또는 sibling checkout path는 runtime ingestion contract가 아니다.

Local development에서만 명시적 absolute checkout path 또는 pinned local manifest fixture를 fallback으로 둘 수 있다. 이 경우에도 schema, checksum, channel, usage-mode 검증을 우회하지 않는다.

```bash
python3 assets/tools/knowledge_manifest_ingest.py \
  --manifest-file /absolute/path/to/beopsuny-knowledge/_system/manifests/stable.json \
  --knowledge-root /absolute/path/to/beopsuny-knowledge
```

## 답변 경계

Knowledge asset은 답변에서 현재 법적 결론의 최종 근거가 아니다.

- 법적 결론은 현재 live source로 재확인된 공식 출처에 근거한다.
- knowledge asset은 "검색 확장과 누락 점검에 사용한 보조 자산"으로만 취급한다.
- memo, benchmark, reference context의 과거 판단을 현재 법령·판례 결론처럼 쓰지 않는다.
- manifest 또는 asset 검증 실패 시 사용자에게 내부 URL/token 세부사항을 노출하지 않는다.

## Privacy replay fixtures

첫 boundary 검증은 단순 조문 확인 1개와 복합 privacy replay 3개로 한다.

- `eval-privacy-000`: 단순 개인정보 조문 확인
- `eval-privacy-001`: 해외 SaaS CRM 국외이전
- `eval-privacy-002`: server-side tag forwarding 공개·변경 이력
- `eval-privacy-003`: vendor incident notice와 effective-date boundary

이 fixture들은 knowledge asset이 recall과 audit을 넓히는지, 동시에 단순 조문·링크·시행일 질문에 full ingestion workflow를 강제하지 않는지 확인한다. 결론 정확도 평가는 항상 live official source 재확인과 Source Grading으로 한다.
