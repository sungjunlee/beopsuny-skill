---
id: BACK-183
title: '[Prune] SKILL.md 2차 프루닝 실익 평가 (~180줄 목표 재검토)'
status: To Do
labels:
  - area:architecture
  - area:refactor
priority: low
milestone:
created_date: '2026-07-03'
---
## Description
## 배경

프루닝 스프린트(#174) 결과 SKILL.md는 326 → 303줄. 크리틱의 목표치 ~180줄에는 미달이다. 다만 이번 라운드에서 확인된 교훈: 무리한 압축은 gate 표 셀 과밀 같은 역효과를 낸다 (PR #179 리뷰 finding ⑤⑥).

이 이슈는 실행이 아니라 **평가**다 — 더 줄일 실익이 있는지 먼저 판단한다.

## 작업

1. SKILL.md 섹션별 줄 수/역할 분해표 작성
2. 후보 평가:
   - 개인정보 보조 지식 레이어의 "기본 점검 축" 목록(~15줄) → `references/knowledge-injection.md`로 내릴 수 있는지 (라우터에 남길 최소 트리거는?)
   - 출력 계약 섹션의 형식 예시 2개 → `references/output-formats.md` pointer로 대체 가능한지
   - Full/Lite 판별의 경로 블록 → source-access.md와 중복인지
3. 각 후보에 대해: 절감 줄 수 vs 라우팅 신뢰도 하락 위험을 명시하고 go/no-go 판정
4. go 판정이 있으면 실행 이슈로 분리, 전부 no-go면 목표치를 현실화(~300줄)하고 이 이슈로 종결

## AC

- [x] 섹션별 분해표 + 후보별 go/no-go 판정 기록 (#183 코멘트)
- [x] 결론이 에픽 #174에 코멘트로 연결됨 (목표치 수정 포함: ~180 폐기 → ~270)

