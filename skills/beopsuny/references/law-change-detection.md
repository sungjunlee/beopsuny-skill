# 법령 변경 감지

법령 변경 감지는 pull 방식이다. 사용자가 묻거나 `profile.yaml.interested_laws`가 있을 때 응답 후단에 한 줄로 붙인다. 자동 알림, 크론, 스케줄링, 지속 모니터링은 이 스킬의 기본 기능이 아니다.

## Supported Queries

| 질의 | Full 모드 | Lite 모드 |
|------|-----------|-----------|
| 최근 한 달 개정된 법령 | `git log --since`로 discovery 후 법령별 재조회 | 직접 discovery 미지원, 지정 법령 또는 관심 법령만 조회 |
| 특정 법령 변경 | `git log` -> SHA -> `git show` | 법망 API `law?action=history/diff` |
| 관심 법령 일괄 | `profile.yaml.interested_laws` 순회 | 동일, 가능한 소스로 조회 |

## Full Mode Commands

공통 prefix:

```bash
DR=${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}
```

시간 범위 discovery:

```bash
git -c core.quotePath=false -C "$DR/legalize-kr" log --since="1 month ago" --name-only kr/
```

특정 법령:

```bash
git -C "$DR/legalize-kr" log -n 5 --follow kr/{법령명}/법률.md
git -C "$DR/legalize-kr" show {SHA} -- kr/{법령명}/법률.md
```

한국어 경로가 깨지지 않도록 `--name-only`에는 `-c core.quotePath=false`를 사용한다.

## Lite Mode

Lite 모드에서는 사용자가 특정 법령을 지정했거나 `interested_laws`가 있을 때 법망 API history/diff를 사용한다. 시간 범위 전체 discovery는 지원하지 않는다고 말하고, 법령명을 좁혀 달라고 요청한다.

## Output Fields

법령당 아래를 분리한다.

- 개정일자: git commit date 또는 API 변경일
- 공포일자: 공포 정보가 있으면 별도 표시
- 시행일자: YAML frontmatter 또는 공식 API로 확인
- 변경 조문: diff 요약
- 출처 링크: legalize-kr commit, law.go.kr 법령 링크

공포일과 시행일은 다를 수 있다. 같은 날짜라고 가정하지 않는다.

## Interested Laws Append

`profile.yaml.interested_laws`가 비어 있지 않고, 본문 답변 후 관심 법령 개정 정보가 있으면 아래 순서로 붙인다.

```text
본문
---
🔍 자가 검증: ...
💡 최근 개정: {법령1} (YYYY-MM-DD), ...
면책 고지
```

모든 관심 법령이 개정 없음이고 조회 실패도 없으면 `💡`를 생략한다. 조회 실패가 있으면 `💡 조회 실패: ...`로 표시한다.

## Failure Handling

조회 실패는 개정 없음이 아니다.

아래는 모두 실패로 표시한다.

- `git` non-zero exit
- Lite API timeout/error
- 법령명과 legalize-kr 디렉토리명 mismatch
- diff/history endpoint가 빈 값이지만 원인 불명

표현:

```text
💡 "{법령명}" 조회 실패 — 데이터/법령명 확인 필요
```

## Push Boundary

사용자가 명시적으로 automation을 요청하지 않으면 아래 표현을 하지 않는다.

- 알림을 설정
- 크론
- 스케줄
- notification
- 자동으로 알려드림
- 푸시
- 정기적으로 알려드릴게요
- 주기적으로 체크해드리겠습니다
- 자동 모니터링
- 지속적으로 추적해드리겠습니다

사용자가 automation을 요청하면 현재 대화의 automation 도구 또는 별도 작업으로 처리해야 하며, 이 스킬의 기본 변경 감지와 섞지 않는다.
