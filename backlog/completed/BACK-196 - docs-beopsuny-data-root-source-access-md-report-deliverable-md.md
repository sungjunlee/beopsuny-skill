---
id: BACK-196
title: '[Docs] BEOPSUNY_DATA_ROOT 기본값 의미가 source-access.md와 report-deliverable.md에서 불일치'
status: To Do
labels:
  - bug
  - area:docs
priority: medium
milestone:
created_date: '2026-07-04'
---
## Description
## 발견 (2026-07-04 리포트 실사용 smoke test)

같은 환경변수를 두 문서가 다른 의미로 소비한다:

- `references/source-access.md`: `${BEOPSUNY_DATA_ROOT:-~/.beopsuny/data}/legalize-kr/...` — 변수 = **data 디렉토리 자체**
- `references/report-deliverable.md`: `${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/reports/...` — 변수 = **루트** (PRD D2 결정)

사용자가 `BEOPSUNY_DATA_ROOT=/x`를 설정하면 미러는 `/x/legalize-kr`(기본 레이아웃 `~/.beopsuny/data/legalize-kr`와 다른 depth), 리포트는 `/x/reports`가 되어 레이아웃이 갈라진다.

## 작업

한쪽 의미로 통일 (제안: 변수 = 루트 `~/.beopsuny`, 미러는 `${ROOT}/data/{family}`). source-access.md의 clone/탐색 커맨드 전부와 O1 drift check를 짝 수정.

## AC
- [ ] 두 문서가 같은 semantics 사용, 기본 경로 레이아웃 불변 (`~/.beopsuny/data/*`, `~/.beopsuny/reports/*`)
- [ ] O1/O2 PASS
