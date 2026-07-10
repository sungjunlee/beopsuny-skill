# 소스 접근과 런타임 모드

이 문서는 법순이가 어떤 소스를 어떤 환경에서 어떻게 접근하는지 정리한다. `SKILL.md`는 우선순위와 게이트만 들고, 실제 명령·URL·fallback은 여기서 확인한다.

`[VERIFIED]`, provenance, source family별 확인 조건은 `references/citation-verification-contract.md`를 단일 계약으로 따른다. 이 문서의 source priority는 접근 순서이지, 요약·스니펫을 `[VERIFIED]`로 승격하는 규칙이 아니다.

## Sourcing Model

소싱은 네 축을 분리한다.

| 축 | 의미 | 예시 |
| --- | --- | --- |
| `source_family` | 어디서 찾았는가 | `legalize-kr`, `admrule-kr`, `law.go.kr`, `법망 API wrapper` |
| `source_authority` | 소스 자체의 법적 성격 | `공식 원문`, `공식 원문 기반 로컬 미러`, `해설/의견` |
| `verification_status` | 이번 응답에서 실제 확인했는가 | `[VERIFIED]`, `[UNVERIFIED]`, `[INSUFFICIENT]` |
| `provenance` | 이번 응답의 실제 확인 경로 | `admrule-kr 로컬 미러 확인 (직접 공식 사이트 확인 아님)` |

`source_family`가 늘어나도 출처 권위 라벨과 `[VERIFIED]` 조건은 바뀌지 않는다. 새 source family는 아래 family map에 추가하고, 라벨은 `assets/policies/source_grades.yaml`, 검증 조건은 `references/citation-verification-contract.md`를 따른다.

## Primary Sourcing Rule

영속 환경에서는 Git으로 받은 공식 원문 기반 로컬 미러를 우선한다. 즉, 법령은 `legalize-kr`, 행정규칙은 `admrule-kr`, 판례는 `precedent-kr`, 지역이 특정된 자치법규는 `ordinance-kr` 파일을 먼저 탐색한다.

법망 API, law.go.kr, korean-law-mcp는 다음 경우에 사용한다.

- 해당 source family가 로컬에 없거나 Lite 모드인 경우
- 키워드 discovery가 로컬 파일 탐색보다 효율적인 경우
- 로컬 미러의 최신성, 첨부파일, `본문출처: parsing-failed`를 공식 원문으로 교차확인해야 하는 경우
- 로컬 미러가 커버하지 않는 해석례, 헌재, 행정심판, 조세심판, 조약, 정책·제재 동향을 확인하는 경우

## Source Family Map

| Source family | 주 용도 | 기본 라벨 | 사용 기준 |
| --- | --- | --- | --- |
| `legalize-kr` | 법률, 시행령, 시행규칙, 법령 개정 이력 | 공식 원문 기반 로컬 미러 | Full 모드 기본 1차 경로. 법령명 디렉토리와 본문 파일을 직접 읽은 경우만 `[VERIFIED]` 후보 |
| `admrule-kr` | 고시, 훈령, 예규, 행정규칙 본문과 첨부 메타데이터 | 공식 원문 기반 로컬 미러 | 행정규칙이 실무 기준이면 Full 모드 기본 1차 경로 |
| `precedent-kr` | 대법원/하급심 판례 전문 | 공식 원문 기반 로컬 미러 / 하급심 caveat | 사건번호를 알 때 직접 조회. 키워드 discovery는 법망 API가 더 적합 |
| `ordinance-kr` | 조례, 규칙 등 자치법규 | 공식 원문 기반 로컬 미러 | 지자체·지역이 특정된 질문의 1차 경로. 전역 검색은 비용이 크므로 피한다 |
| `law.go.kr` | 법령, 행정규칙, 자치법규, 판례 공식 화면 | 공식 원문 | 직접 원문 화면 또는 공식 응답을 연 경우. 판례는 로컬 미러 frontmatter `출처`(precSeq) 우선, 없으면 `판례/({사건번호})` |
| `법망 API wrapper` | Lite 모드 검색/원문 조회, 법령·행정규칙·해석례·판례 discovery | 공식 원문 또는 공식 실무자료: 미확정 | 검색 결과만으로는 `[VERIFIED]` 금지. 원문 필드나 verify 결과 필요 |
| `korean-law-mcp` | 헌재, 행정심판, 조세심판, 자치법규, 조약, 별표/서식 | 공식 원문 | OC 코드 또는 설치된 MCP 도구가 있을 때 사용 |
| `WebSearch` | 공식 사이트 discovery, 정책·제재 동향, 보도자료·해설 보조 | 공식 실무자료 / 해설·의견 / 참고 제외 | 공식 원문 접근을 돕는 보조. 검색 스니펫 자체는 `[VERIFIED]` 아님 |

로컬 미러를 읽은 경우 provenance는 각 source family를 명시한다. 예: `legalize-kr 로컬 미러 확인 (직접 공식 사이트 확인 아님)`, `admrule-kr 로컬 미러 확인 (직접 공식 사이트 확인 아님)`, `ordinance-kr 로컬 미러 확인 (직접 공식 사이트 확인 아님)`, `precedent-kr 로컬 미러 확인 (직접 공식 사이트 확인 아님)`. `law.go.kr 원문 확인`은 해당 공식 사이트/공식 응답을 실제로 연 경우에만 쓴다.

## Mode Detection

`BEOPSUNY_DATA_ROOT`는 beopsuny 루트 디렉토리(기본 `~/.beopsuny`)를 가리키며, 미러는 그 아래 `data/`에, 리포트는 `reports/`에 놓인다 (`references/report-deliverable.md` 참고).

공통 데이터 루트:

```bash
${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/data
```

Source family inventory:

```bash
ls ${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/data/legalize-kr/kr/
test -d ${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/data/admrule-kr
test -d ${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/data/precedent-kr
test -d ${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/data/ordinance-kr
```

`legalize-kr/kr/`가 있으면 법령 Full 모드다. 다른 로컬 미러는 family별 capability로 판단한다. 예를 들어 `legalize-kr`만 있으면 법령은 Full, 행정규칙은 법망 API/law.go.kr fallback이다. 데이터가 없다고 자동 clone하지 않는다. 사용자가 Full 모드 설정 또는 데이터 다운로드를 요청할 때만 초기화한다.

## Capability Matrix

실행 환경마다 사용할 수 있는 소스가 다르다. 없는 도구를 있다고 가정하지 말고, 가능한 경로로 좁히거나 결론을 유보한다.

- 로컬 데이터 없음: Lite 모드로 안내하고 법망 API, WebSearch, 공식 링크를 사용한다. 로컬 전문·git history 전제는 금지한다.
- 법망 API 접근 불가: 사용 가능한 local data, law.go.kr, WebSearch 공식 자료로 좁힌다. 그래도 원문을 확인하지 못한 범위는 `[INSUFFICIENT]` 또는 `[UNVERIFIED]`로 낮춘다.
- WebSearch 없음: local data, 법망 API, 사용 가능한 MCP/공식 링크만 사용한다. 정책 동향·제재 동향은 생략하거나 확인 필요 표시를 한다.
- korean-law-mcp 또는 OC 코드 없음: 헌재·행정심판·조세심판·조약 등은 가능한 범위만 답하고 필요 시 OC 코드 안내로 남긴다.
- 네트워크 없음: 사용 가능한 local mirror만 사용하고, 최신성·정책 동향·공식 링크 검증 한계를 표시한다.
- 로컬 데이터와 네트워크 모두 없음: 번들 YAML은 후보·체크리스트로만 쓰고 법률 결론을 만들지 않는다.

Fallback 원칙:

- 조회 실패는 결론이 아니다. 실패 원인과 확인하지 못한 범위를 표시한다.
- 번들 `assets/data/*.yaml`은 조항·용어 후보이지 현행 법적 결론 근거가 아니다. 법령 ID, 인허가 요건, 공식 서식, 법정 기한은 번들 캐시 없이 실시간 공식 소스로 확인한다.
- 링크 패턴이 확실하지 않으면 추정 링크를 만들지 않는다.
- 현재 소스로 확인할 수 없는 조문·판례·시행일·금액은 만들지 않는다.

## Freshness Gate

번들 YAML과 과거 검토 이력은 현행 법령을 대신하지 않는다. 특히 아래 항목은 stale 가능성이 높으므로 답변 전에 live source로 재확인한다.

- 과징금, 과태료, 벌칙, 신고기한, 처리기간, 수수료
- 직원 수, 매출, 거래금액, 정보주체 수 같은 적용 threshold
- 최저임금, 보험료율, 세율, 원천징수율
- 인허가 구비서류, 관할 기관, 서식 번호
- 행정규칙, 고시, 감독기준, 가이드라인

`maintenance.next_review`가 지난 자산이나 `last_verified`가 오래된 항목은 답변에서 다음 중 하나로 처리한다. 등록된 stale 자산 목록과 제거 조건은 `references/freshness-governance.md`와 `assets/policies/freshness_debt.yaml`을 따른다. 자산을 갱신하거나 registry에서 제거하려면 `assets/schemas/freshness_revalidation.yaml` 형식으로 확인한 공식 source family, volatile item 검토 결과, retirement decision을 남긴다.

1. live source로 재확인하고 provenance를 표시한다.
2. 재확인에 실패하면 `[STALE]` 또는 `[INSUFFICIENT]`로 낮추고 결론을 유보한다.
3. 단순 후보로만 쓰고, 현행 법적 결론의 근거로 쓰지 않는다.

Freshness gate는 출처 권위 라벨을 대체하지 않는다. 공식 원문 소스나 공식 원문 기반 로컬 미러라도 이번 응답에서 현행성을 확인하지 못했으면 provenance와 최신성 한계를 표시한다.

## Local Git Mirror Commands

법령명 디렉토리는 띄어쓰기를 제거한 이름을 사용한다. `git log --name-only`로 한국어 경로를 볼 때는 octal escape 방지를 위해 `-c core.quotePath=false`를 붙인다.

| Source family | 대표 탐색 |
| --- | --- |
| `legalize-kr` | `ls ${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/data/legalize-kr/kr/ \| grep 개인정보`; `cat .../legalize-kr/kr/{법령명}/법률.md`; `git -C .../legalize-kr log --oneline -20 -- kr/{법령명}/` |
| `admrule-kr` | `rg -l '개인정보|과징금|안전보건' .../admrule-kr -g '본문.md'`; `git -C .../admrule-kr -c core.quotePath=false log --oneline -20 -- '{기관경로}/{행정규칙종류}/{행정규칙명}/본문.md'` |
| `precedent-kr` | `find .../precedent-kr -name "*2022다12345*"`; 사건번호가 없으면 먼저 법망 API로 discovery |
| `ordinance-kr` | `{광역}/{기초 또는 _본청 또는 _교육청}/{자치법규종류}/{자치법규명}/본문.md`; 지역을 먼저 좁힌 뒤 탐색 |

`admrule-kr`와 `ordinance-kr`의 frontmatter는 citation ledger 후보로 쓴다. 핵심 필드는 식별자, 명칭, 종류, 발령·공포기관, 발령·공포일자, 시행일자, `본문출처`, `출처`, `첨부파일`이다. `본문출처: parsing-failed`이면 metadata와 첨부 링크만으로 결론을 확정하지 말고 law.go.kr 원문 또는 첨부 파일을 다시 확인한다.

## 미러 시행일 확인 (공포본 vs 현행본)

`legalize-kr`·`admrule-kr`·`ordinance-kr` 미러는 최신 공포본을 담으며, 아직 시행되지 않은 개정본일 수 있다. 미러 파일을 읽을 때는 frontmatter `시행일자`를 확인한다. `시행일자`가 오늘보다 미래면 그 본문은 현행이 아니라 시행 전 공포본이다.

이 경우 provenance/currency에 `시행 전 공포본 (시행일 YYYY-MM-DD)`을 표시하고, `[VERIFIED]`는 공포본 기준으로 현행성을 한정한다. 현행 조문 확인은 law.go.kr 현행본으로 별도 확인한다.

예: `kr/의료법/법률.md`는 공포일자 2026-06-09, 시행일자 2026-12-10으로 제34조 제목이 시행 전 개정본 기준 "비대면협진"이다. 2026-07 현재 시행 중인 조문 제목은 "원격의료"다. `assets/policies/checklists/healthcare.yaml`의 health-09 노트가 이 표기의 실전 예시다.

## 법망 API

무인증 무료 API다. 상세 엔드포인트는 `references/beopmang-api.md`를 읽는다.

대표 사용:

```text
https://api.beopmang.org/api/v4/law?action=search&q={검색어}&type=admrul
https://api.beopmang.org/api/v4/law?action=get&law_id={law_id}&article={조문}
https://api.beopmang.org/api/v4/case?action=search&q={키워드}
```

법망 API는 Lite 모드의 기본 검색 경로이고, Full 모드에서도 discovery와 교차확인에 유용하다. `admrule-kr` 또는 `ordinance-kr`가 없으면 행정규칙·자치법규는 법망 API, law.go.kr, korean-law-mcp로 확인한다.

법망 응답이 `service_maintenance`, timeout, 5xx, 빈 응답이면 조회 실패로 표시한다. 이는 검색 0건, 규범 부존재, 개정 없음의 근거가 아니다.

## korean-law-mcp

법제처 API를 AI 친화적으로 래핑한 MCP 서버다. 아래 영역에서 사용한다.

- 헌재 결정
- 행정심판, 조세심판
- 자치법규, 조례
- 조약
- 별표, 서식
- 위임입법 분석

OC 코드가 없으면 건너뛴다. `~/.beopsuny/config.yaml`의 `oc_code`를 확인하거나 사용자에게 물어본다.

```text
https://korean-law-mcp.fly.dev/mcp?oc={OC코드}
```

로컬 MCP 서버가 설치되어 있으면 해당 MCP 도구를 직접 사용한다.

## WebSearch Fallback

WebSearch는 공식 API와 1차 소스로 커버되지 않는 정책 동향, 부처 해설, 제재 동향 조사에서만 사용한다.

| 도메인 | 예시 | 출처 권위 라벨 |
|--------|------|-------|
| 정부·규제기관 공식 | `*.go.kr`, PIPC, MOEL, FTC, FSC | 공식 실무자료 |
| 로펌·학술·법률매체 | 로펌 뉴스레터, 법률신문 | 해설/의견 |
| 뉴스·블로그·SNS | 언론, 개인 블로그 | 참고 제외 |

해설/의견은 `[EDITORIAL]` 보조 자료다. 참고 제외는 결론 근거로 쓰지 않는다.

## 원문 링크

링크는 검증 가능한 경우에만 만든다. 추정 링크를 만들지 않는다.

| 대상 | URL 패턴 |
|------|----------|
| 법령 조문 | `https://www.law.go.kr/법령/{법령명}/제{N}조` |
| 법령 조문 항 | `https://www.law.go.kr/법령/{법령명}/제{N}조제{M}항` |
| 시행령 | `https://www.law.go.kr/법령/{법령명}시행령` |
| 판례 (정밀, 로컬 미러 `출처`) | `https://www.law.go.kr/LSW/precInfoP.do?precSeq={판례일련번호}` |
| 판례 (사건번호) | `https://www.law.go.kr/판례/({사건번호})` |
| 행정규칙 검색 | `https://www.law.go.kr/행정규칙/{고시명}` |
| 의안 | `https://likms.assembly.go.kr/bill/billDetail.do?billId={의안ID}` |

## 데이터 초기화

영속 파일시스템이 있는 환경에서 사용자가 Full 모드 설정을 요청할 때만 실행한다. Desktop Chat처럼 채팅마다 스토리지가 초기화되는 환경에서는 권장하지 않는다.

`--depth`를 쓰지 않는다. 개정 이력 추적에 전체 히스토리가 필요하다.

```bash
mkdir -p ${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/data
git clone https://github.com/legalize-kr/legalize-kr.git ${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/data/legalize-kr
git clone https://github.com/legalize-kr/precedent-kr.git ${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/data/precedent-kr
git clone https://github.com/legalize-kr/admrule-kr.git ${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/data/admrule-kr
```

자치법규까지 다루는 환경에서만 `ordinance-kr`를 추가한다. 체크아웃 파일 수가 매우 많으므로 기본 초기화에 강제하지 않는다.

```bash
git clone https://github.com/legalize-kr/ordinance-kr.git ${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/data/ordinance-kr
```

이미 있으면 pull한다. `legalize-kr`, `admrule-kr`, `ordinance-kr` 계열은 upstream 파이프라인 개선으로 force-push될 수 있으므로 `pull --ff-only` 실패가 "데이터 없음"을 뜻하지 않는다. 동기화 정책은 사용자가 요청한 데이터 루트에만 적용한다.

```bash
for repo in legalize-kr precedent-kr admrule-kr; do
  git -C "${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/data/${repo}" pull --ff-only
done
```

`pull --ff-only`가 force-push 때문에 실패하면 자동으로 덮어쓰지 않는다. 사용자가 해당 데이터 루트 재동기화를 요청한 경우에만 해당 repo를 새로 clone하거나 upstream 안내에 따라 재설정한다.

사용자가 재동기화를 승인하면 아래 순서로 복구한다 (upstream README가 안내하는 절차).

1. 로컬 변경이 없는지 확인한다: `git status --porcelain`이 비어 있고, 로컬 전용 커밋이 upstream 재생성 이전 스냅샷의 데이터 커밋뿐인지 본다. 사용자 파일이 섞여 있으면 중단하고 보고한다.
2. 재생성된 히스토리를 채택한다:

```bash
git -C "${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/data/${repo}" fetch origin
git -C "${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/data/${repo}" reset --hard origin/main
```

3. 재생성이 있었다는 사실과 새 HEAD를 사용자에게 고지한다. `tests/check_source_reachability.py`의 "upstream 불일치" WARN도 이 절차로 해소한다.
