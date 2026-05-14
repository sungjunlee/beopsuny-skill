# 법망 API 레퍼런스

기본 URL: `https://api.beopmang.org/api/v4/{endpoint}?action={action}`

이 문서는 API 사용 패턴과 fallback을 정리한다. 인증 방식, rate limit, endpoint 상태, 데이터 규모 같은 운영 정보는 변동될 수 있으므로 답변에서 확정 사실처럼 말하기 전에 현재 응답 또는 공식 안내를 확인한다.

API timeout, 5xx, maintenance 응답, 빈 응답은 "결과 없음"이 아니다. Full 모드면 legalize-kr/precedent-kr 로컬 데이터로 fallback하고, Lite 모드면 확인 실패 범위를 `[INSUFFICIENT]` 또는 `[UNVERIFIED]`로 표시한다.

## 엔드포인트 맵

| 엔드포인트 | 액션 | 핵심 용도 | 실패 시 |
|-----------|------|----------|---------|
| `law` | `search` | 법령/행정규칙/해석례 검색 | law.go.kr, local data, WebSearch 공식 자료 |
| `law` | `get` | 법령 조문 조회 | 원문 확인 실패로 표시 |
| `law` | `diff` | 개정 전후 비교 | `history`, git log, 공식 법령 페이지 |
| `law` | `history` | 개정 이력 | git log 또는 공식 법령 페이지 |
| `case` | `search` | 판례 키워드 검색 | glaw.scourt.go.kr, precedent-kr |
| `case` | `get` | 판례 상세 조회 | 판례 원문 미확인 표시 |
| `tools` | `verify` | 인용 검증 | 직접 원문 재조회 |
| `tools` | `compare` | 법령 간 비교 | 각 법령을 따로 조회해 수동 비교 |
| `bill` | `search` | 의안 검색 | 국회 의안정보 또는 WebSearch 공식 자료 |

---

## 실무 활용 패턴

### 행정규칙 찾기 (legalize-kr에 없는 핵심 자료)

```
# "과징금" 관련 고시/훈령/예규 검색
WebFetch "https://api.beopmang.org/api/v4/law?action=search&query=과징금부과기준&type=admrul"

# "개인정보 안전성 확보조치" 고시
WebFetch "https://api.beopmang.org/api/v4/law?action=search&query=안전성확보조치&type=admrul"

# 특정 행정규칙 본문 조회 (검색 결과의 admrul_id 사용)
WebFetch "https://api.beopmang.org/api/v4/law?action=get&id={admrul_id}"
```

### 법령해석례 (법제처 유권해석)

```
# "해고" 관련 법령해석례
WebFetch "https://api.beopmang.org/api/v4/law?action=search&query=해고예고&type=expc"

# "개인정보 동의" 관련 해석례
WebFetch "https://api.beopmang.org/api/v4/law?action=search&query=개인정보+동의+예외&type=expc"
```

### 판례 검색 (로컬 grep보다 빠름)

```
# 키워드 검색
WebFetch "https://api.beopmang.org/api/v4/case?action=search&query=부당해고"

# 판례 상세 (검색 결과의 prec_id 사용)
WebFetch "https://api.beopmang.org/api/v4/case?action=get&id={prec_id}"
```

검색 결과에서 `prec_id`를 얻으면 precedent-kr 로컬에서 전문을 읽을 수도 있다:
```
Glob "*{사건번호}*" --path ${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}/precedent-kr
```

### 법령 개정 비교 / 이력

```
# 개정 전후 diff (법령ID 필요 — law search로 먼저 확인)
WebFetch "https://api.beopmang.org/api/v4/law?action=diff&id={법령ID}"

# 개정 이력
WebFetch "https://api.beopmang.org/api/v4/law?action=history&id={법령ID}"
```

legalize-kr의 git log도 같은 용도로 쓸 수 있다. 법망은 구조화된 JSON, git log는 커밋 메시지 기반.

### 법령 간 비교

```
# 두 법령의 구조/내용 비교
WebFetch "https://api.beopmang.org/api/v4/tools?action=compare&law1={법령명1}&law2={법령명2}"
```

### 인용 검증 (환각 방지)

2단계 호출. 답변에서 인용한 조문/판례가 실제 존재하는지 확인할 때 사용.

```
# 1단계: 티켓 발급
WebFetch "https://api.beopmang.org/api/v4/tools?action=verify&citation=개인정보보호법 제15조"
# → ticket_id 수신 (300초 유효)

# 2단계: 티켓으로 검증
WebFetch "https://api.beopmang.org/api/v4/tools?action=verify&citation=개인정보보호법 제15조&ticket_id={ticket_id}"
```

---

## 검색 파라미터

| 파라미터 | 설명 | 예시 |
|---------|------|------|
| `query` | 검색어 (필수) | `개인정보`, `부당해고` |
| `type` | 법령 유형 필터 | `admrul`, `expc`, `law`, `prec`, `ordin`, `detc` |
| `page` | 페이지 번호 | `1`, `2` |
| `limit` | 페이지당 결과 수 | `10`, `20` |

## 응답 구조

```json
{
  "data": {
    "total": 5572,
    "page": 1,
    "results": [
      {
        "law_id": "001706",
        "name": "민법",
        "type": "법률",
        "case_count": 21116
      }
    ]
  }
}
```

행정규칙 결과:
```json
{
  "admrul_id": "2100000182410",
  "admrul_name": "감가규정",
  "admrul_type": "훈령",
  "issuing_org": "조달청"
}
```

판례 결과:
```json
{
  "prec_id": "617235",
  "case_no": "2025두35547",
  "case_name": "취득세등경정거부처분취소",
  "decision_date": "2026-03-12",
  "court": "대법원"
}
```

maintenance류 응답 예:
```json
{
  "ok": false,
  "error": "service_maintenance",
  "retry_after": 3600
}
```

## 운영 정보

데이터 규모, 동기화 주기, rate limit, endpoint별 장애 상태는 문서에 고정하지 않는다. 조사 중 API 응답에서 직접 확인했거나 공식 안내를 확인한 경우에만 검토 메모에 적는다.
