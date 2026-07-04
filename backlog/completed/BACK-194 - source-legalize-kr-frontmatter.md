---
id: BACK-194
title: '[Source] legalize-kr 미러의 시행 전 공포본 구분 — frontmatter 시행일자 확인을 미러 검증 계약에 추가'
status: To Do
labels:
  - enhancement
  - area:refactor
priority: high
milestone:
created_date: '2026-07-04'
---
## Description
## 문제 (#180 실행 중 발견, PR #193 봇 리뷰가 표면화)

legalize-kr 미러는 **최신 공포본**을 담으며, 이는 아직 시행되지 않은 개정본일 수 있다. 실제 사례:

- `kr/의료법/법률.md`: frontmatter `공포일자: 2026-06-09, 시행일자: 2026-12-10` — 제34조 제목이 시행 전 개정본의 "비대면협진"으로 표시됨. 현행(2026-07 시점) 조문 제목은 "원격의료".
- #180 revalidation에서 executor가 이를 근거로 checklist 앵커를 미래 시행본 기준으로 "정정"했고, 봇 리뷰가 잡아냄 (PR #193에서 수정).

이는 스킬 핵심 원칙 4(공포일 ≠ 시행일)가 **미러 소스 자체에도 적용**되어야 함을 뜻한다. 현재 source-access.md의 미러 검증 규칙은 frontmatter 시행일자 확인을 요구하지 않아, Full 모드 [VERIFIED] 후보 판정이 시행 전 텍스트에 앵커될 수 있다.

## 작업

1. `references/source-access.md` 미러 검증 규칙에 추가: 미러 파일을 읽을 때 frontmatter `시행일자`가 미래면 현행 텍스트가 아님 — provenance/currency에 "시행 전 공포본 (시행일 YYYY-MM-DD)" 표시, [VERIFIED] 판정은 현행성 한정
2. `references/citation-verification-contract.md` currency 규칙과 교차 확인 (모순 없게)
3. O2 unsafe fixture: 시행 전 공포본을 현행 조문처럼 [VERIFIED] 인용한 출력이 FAIL로 잡힘
4. (선택) legalize-kr 미러가 현행본/공포본을 어떻게 구분하는지 upstream 확인 — 두 버전을 모두 제공하면 현행본 우선 규칙 명시

## AC

- [ ] source-access.md에 시행일자 확인 규칙 존재
- [ ] unsafe fixture + rule 추가, O1/O2 PASS
- [ ] #180에서 수정한 의료법 사례가 새 규칙의 예시로 참조됨
