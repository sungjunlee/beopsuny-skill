# beopsuny-knowledge 소비 경계

`beopsuny-knowledge`는 법순이의 live legal research를 대체하지 않는다. 법순이는 현재 법령, 시행령, 시행규칙, 행정규칙, 판례, 해석례, 공식 자료를 매번 다시 확인하고, knowledge asset은 검색을 넓히고 누락을 점검하는 데만 쓴다.

## 규칙 강도

이 문서는 법순이의 탐색 자유도를 줄이기 위한 고정 절차가 아니다. 목적은 knowledge asset이 결론이나 검색 route를 오염시키지 않도록 사용 경계를 나누는 것이다.

Hard rule:

- 법적 결론은 현재 live source와 Source Grade에 근거한다.
- retrieval hints는 최초 검색 route나 결론 근거가 아니다.
- authority map은 route oracle이 아니라 post-search audit asset이다.
- seed workspace memo와 `Derived Asset Candidates`는 structured runtime asset이 아니다.

Guardrail:

- 개인정보 쟁점이 실질적인 질문에서는 stable manifest 소비를 시도할 수 있다.
- taxonomy는 issue framing과 fact-question expansion에만 쓴다.
- retrieval hints와 authority map은 blind live search 이후 recall/audit에 쓴다.
- manifest 또는 asset 검증 실패 시 knowledge injection 없이 live legal research만 수행한다.

Operational preference:

- 단순 조문 확인, 공식 링크 확인, 짧은 시행일 확인처럼 쟁점 분해가 필요 없는 질문에는 knowledge asset을 생략한다.
- 복합 개인정보 질문, vendor/DPA/국외이전/사고대응/광고태그처럼 누락 위험이 큰 질문에는 knowledge asset으로 recall과 audit을 보강한다.
- 사용 여부를 답변마다 장황하게 설명하지 않는다. 내부 URL, token, 인증 실패 세부사항은 노출하지 않는다.

기존 번들 자산과의 관계:

- `assets/policies/checklists/privacy_compliance.yaml`은 개인정보보호 기본 자가점검 체크리스트다.
- `assets/data/clause_references.yaml`의 `data_privacy`/`data_processing` 항목은 계약 조항 검토용 법령 매핑이다.
- `beopsuny-knowledge`는 위 자산을 대체하지 않는다. 기존 번들 자산으로 기본 법령·계약 체크를 잡고, knowledge asset은 최신 반복 miss, vendor/company document 축, post-blind 검색어 확장, authority audit을 보강한다.
- 기존 번들 자산과 knowledge asset이 충돌하면 현재 live official source와 Source Grade를 우선하고, 오래된 번들 문구는 확인 필요로 둔다.

후속 방향:

- privacy 기본 체크리스트도 장기적으로는 `beopsuny-knowledge`에서 최신화하고 manifest로 publish하는 편이 맞다.
- 그 전까지 `privacy_compliance.yaml`은 번들 fallback/bootstrap 자산으로 유지하고, 최신성·source watch·반복 miss 반영은 `beopsuny-knowledge` 쪽 backlog에서 관리한다.
- checklist가 `beopsuny-knowledge` asset으로 승격되면 `beopsuny-skill`의 번들 체크리스트는 deprecated/fallback 표시를 검토한다.

## 채널

기본 channel은 `stable`이다. `canary`는 명시적 opt-in replay 또는 integration test에서만 사용한다.

| Channel | 용도 | 경계 |
| --- | --- | --- |
| `stable` | production-like 기본 소비 채널 | validation, replay/readiness evidence, triage disposition을 통과한 privacy asset |
| `canary` | guarded replay 또는 integration test | stable 승격 전 변경을 좁은 범위에서 검증 |

Runtime은 환경이 지정한 manifest source를 사용한다. source 위치와 접근 방식은 skill 본문이 아니라 integration config에서 관리한다.

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

### 1. Domain stage 확인

정교한 ingestion 구현에서는 먼저 `domains.yaml`에서 domain stage를 확인한다. 다만 현재 stable manifest는 privacy asset 중심이므로, first wiring 단계에서 `domains.yaml`을 runtime 필수 fetch 대상으로 가정하지 않는다.

- `active_vertical`: 현재 structured asset 소비 대상은 `privacy`만이다.
- `seed_workspace`: README와 memo는 reference context로만 본다.
- `watch_candidate`: 독립 domain으로 route하지 않는다.

Seed workspace의 `Derived Asset Candidates`는 runtime asset이 아니다. `contracts`, `employment`, `fair-trade` 등의 seed memo를 taxonomy, retrieval hints, authority map, benchmark fixture처럼 주입하지 않는다.

### 2. Right-sized 사용 판단

Knowledge asset은 모든 개인정보 질문에 붙는 의무 절차가 아니다.

생략해도 되는 경우:

- 사용자가 특정 조문, 시행일, 공식 링크만 묻는 경우
- 기존 법순이 live search stack만으로 충분히 답할 수 있는 좁은 질문
- manifest 접근이나 검증이 실패한 경우

사용을 검토할 경우:

- 국외이전, DPA, subprocessor, vendor support access처럼 사실관계 분기가 많은 질문
- server-side tag forwarding, 광고 SDK, opt-out propagation처럼 회사 문서와 vendor 문서 누락 위험이 큰 질문
- 유출 가능성, 신고·통지, 시행예정 조항, 증적보전처럼 시점과 상태 분리가 중요한 질문

### 3. Blind live search 우선

법순이의 기존 stack이 우선이다.

- Full mode: `legalize-kr`, `precedent-kr`, 법망 API, 공식 링크
- Lite mode: 법망 API, WebSearch, 공식 사이트
- 모든 결론은 Source Grade와 verification tag를 붙인다.

Knowledge asset을 읽었더라도 retrieval hints나 authority map으로 최초 검색 route를 정하지 않는다.

### 4. Post-blind expansion

Blind live search 이후에만 retrieval hints를 적용한다.

허용:

- 누락 검색어, 동의어, 실무 표현, 영문 표현 보강
- 빠진 source family 확장
- 판례, 해석례, 고시, 가이드라인, 집행 사례 검색어 보강
- anti-pattern을 보고 노이즈 경로 회피

금지:

- 최초 검색 route 결정
- 법적 결론 근거로 표시
- exhaustive checklist처럼 사용
- supporting memo와 다른 사실관계에 자동 일반화

### 5. Post-search audit

Authority map은 검색 이후 누락 축을 점검하는 audit asset이다.

- `authority_map.core`: 반복 검증된 안정 audit 축
- `authority_map.overlay`: 빠르게 변하는 live blind spot, regulator 관심축, 회사/vendor 문서 축
- `source registry`: canonical source family, observed_at, verification_state 확인

Authority map에 있는 축은 "확인할 축"이지 "정답 후보"가 아니다.

## Manifest 검증

Runtime 구현은 아래 조건을 모두 확인해야 한다. 실패하면 knowledge injection을 건너뛰고 live legal research만 수행한다.

- manifest fetch 성공
- `publication.publish_ready == true`
- `publication.url_status == "live"`
- `publication.source_type`이 허용된 값
- manifest schema version 지원
- 각 asset URL fetch 성공
- 각 asset `sha256` 일치
- 각 asset schema version 지원
- `usage_mode`가 있는 asset은 허용된 사용 범위와 일치
- `usage_mode`가 없는 asset은 `asset_type`, `vertical`, schema version, manifest key의 허용 사용 범위와 일치
- placeholder, stale, local-only asset이 아님

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

Production-like runtime의 canonical source는 integration config가 지정한 manifest source다. `../beopsuny-skill` 또는 sibling checkout path는 runtime ingestion contract가 아니다.

Local development에서만 명시적 absolute checkout path 또는 pinned local manifest fixture를 fallback으로 둘 수 있다. 이 경우에도 schema, checksum, channel, usage-mode 검증을 우회하지 않는다.

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

이 fixture들은 knowledge asset이 recall과 audit을 넓히는지 확인하기 위한 것이다. 동시에 단순 조문·링크·시행일 질문에 full ingestion workflow를 강제하지 않는지 확인한다. 결론 정확도 평가는 항상 live official source 재확인과 Source Grading으로 한다.
