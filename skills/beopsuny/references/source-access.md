# 소스 접근과 런타임 모드

이 문서는 법순이가 어떤 소스를 어떤 환경에서 어떻게 접근하는지 정리한다. `SKILL.md`는 우선순위와 게이트만 들고, 실제 명령·URL·fallback은 여기서 확인한다.

## Source Priority

| 순위 | Full 모드 | Lite 모드 | 기본 Grade |
|------|----------|----------|-----------|
| 1 | 로컬 Git `legalize-kr` + `precedent-kr` | 법망 API | A, 하급심은 B |
| 2 | 법망 API | WebSearch | 행정규칙/해석례 A, 의안 B |
| 3 | korean-law-mcp, OC 코드 필요 | korean-law-mcp, OC 코드 필요 | A |
| 링크 | law.go.kr / glaw.scourt.go.kr | law.go.kr / glaw.scourt.go.kr | A |
| 백업 | WebSearch 공식/해설 자료 | WebSearch 공식/해설 자료 | B/C/D |

## Mode Detection

공통 데이터 루트:

```bash
${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}
```

Full 모드 판별:

```bash
ls ${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}/legalize-kr/kr/
```

결과가 있으면 Full 모드, 없으면 Lite 모드다. 데이터가 없다고 자동 clone하지 않는다. 사용자가 Full 모드 설정 또는 데이터 다운로드를 요청할 때만 초기화한다.

## Capability Matrix

실행 환경마다 사용할 수 있는 소스가 다르다. 없는 도구를 있다고 가정하지 말고, 가능한 경로로 좁히거나 결론을 유보한다.

| 상황 | 사용 가능한 경로 | 답변 경계 |
| --- | --- | --- |
| Full 모드 + 네트워크 가능 | local legalize-kr/precedent-kr, 법망 API, korean-law-mcp, WebSearch | 가장 강한 모드. 그래도 행정규칙·최신 개정은 API/공식 링크로 확인 |
| 로컬 데이터 없음 | 법망 API, WebSearch, 공식 링크 | Lite 모드로 안내. 로컬 전문·git history 전제 금지 |
| 법망 API 접근 불가 | local data, law.go.kr/glaw.scourt.go.kr, WebSearch 공식 자료 | 행정규칙·해석례 원문 확인 실패 시 `[INSUFFICIENT]` 또는 `[UNVERIFIED]` |
| WebSearch 없음 | local data, 법망 API, 사용 가능한 MCP/공식 링크 | 정책 동향·제재 동향은 생략하거나 확인 필요 표시 |
| korean-law-mcp 또는 OC 코드 없음 | local data, 법망 API, WebSearch | 헌재·행정심판·자치법규·조약 등은 가능한 범위만 답하고 필요 시 OC 코드 안내 |
| 네트워크 없음 | local legalize-kr/precedent-kr만 사용 | 최신성, 행정규칙, 정책 동향, 공식 링크 검증을 제한사항으로 표시 |
| 로컬 데이터와 네트워크 모두 없음 | 번들 YAML은 후보·체크리스트로만 사용 | 법률 결론을 만들지 말고 `[INSUFFICIENT]`로 유보 |

Fallback 원칙:

- 조회 실패는 결론이 아니다. 실패 원인과 확인하지 못한 범위를 표시한다.
- 번들 `assets/data/*.yaml`은 탐색 후보이지 현행 법적 결론 근거가 아니다.
- 링크 패턴이 확실하지 않으면 추정 링크를 만들지 않는다.
- 현재 소스로 확인할 수 없는 조문·판례·시행일·금액은 만들지 않는다.

## Full Mode: legalize-kr

경로:

```text
${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}/legalize-kr/
```

법령명 디렉토리는 띄어쓰기를 제거한 이름을 사용한다.

```bash
ls ${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}/legalize-kr/kr/ | grep 개인정보
cat ${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}/legalize-kr/kr/{법령명}/법률.md
cat ${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}/legalize-kr/kr/{법령명}/시행령.md
ls ${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}/legalize-kr/kr/{법령명}/
git -C ${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}/legalize-kr log --oneline -20 -- kr/{법령명}/
```

`git log --name-only`로 한국어 경로를 볼 때는 octal escape 방지를 위해 `-c core.quotePath=false`를 사용한다.

## Full Mode: precedent-kr

경로:

```text
${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}/precedent-kr/
```

사건번호를 아는 경우에만 직접 파일을 찾는다. 키워드 검색은 파일 수가 많으므로 법망 API가 기본이다.

```bash
find ${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}/precedent-kr -name "*2022다12345*"
cat ${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}/precedent-kr/민사/대법원/2022다12345.md
```

## 법망 API

무인증 무료 API다. 상세 엔드포인트는 `references/beopmang-api.md`를 읽는다.

대표 사용:

```text
https://api.beopmang.org/api/v4/law?action=search&query={검색어}&type=admrul
https://api.beopmang.org/api/v4/case?action=search&query={키워드}
```

legalize-kr에는 행정규칙이 없다. 고시, 훈령, 예규, 구체적 과징금·절차·서식 기준은 법망 API 또는 공식 사이트로 확인한다.

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

| 도메인 | 예시 | Grade |
|--------|------|-------|
| 정부·규제기관 공식 | `*.go.kr`, PIPC, MOEL, FTC, FSC | B |
| 로펌·학술·법률매체 | 로펌 뉴스레터, 법률신문 | C |
| 뉴스·블로그·SNS | 언론, 개인 블로그 | D |

Grade C는 `[EDITORIAL]` 보조 자료다. Grade D는 결론 근거로 쓰지 않는다.

## 원문 링크

링크는 검증 가능한 경우에만 만든다. 추정 링크를 만들지 않는다.

| 대상 | URL 패턴 |
|------|----------|
| 법령 조문 | `https://www.law.go.kr/법령/{법령명}/제{N}조` |
| 법령 조문 항 | `https://www.law.go.kr/법령/{법령명}/제{N}조제{M}항` |
| 시행령 | `https://www.law.go.kr/법령/{법령명}시행령` |
| 대법원 판례 | `https://glaw.scourt.go.kr/wsjo/intesrch/sjo022.do?query={사건번호}` |
| law.go.kr 판례 | `https://www.law.go.kr/판례/({사건번호})` |
| 행정규칙 검색 | `https://www.law.go.kr/행정규칙/{고시명}` |
| 의안 | `https://likms.assembly.go.kr/bill/billDetail.do?billId={의안ID}` |

## 데이터 초기화

영속 파일시스템이 있는 환경에서 사용자가 Full 모드 설정을 요청할 때만 실행한다. Desktop Chat처럼 채팅마다 스토리지가 초기화되는 환경에서는 권장하지 않는다.

`--depth`를 쓰지 않는다. 개정 이력 추적에 전체 히스토리가 필요하다.

```bash
mkdir -p ${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}
git clone https://github.com/legalize-kr/legalize-kr.git ${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}/legalize-kr
git clone https://github.com/legalize-kr/precedent-kr.git ${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}/precedent-kr
```

이미 있으면 pull한다. `legalize-kr` pull 실패 시 re-clone할 수 있다.

```bash
git -C ${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}/legalize-kr pull --ff-only || \
  (rm -rf ${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}/legalize-kr && \
   git clone https://github.com/legalize-kr/legalize-kr.git ${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}/legalize-kr)
```
