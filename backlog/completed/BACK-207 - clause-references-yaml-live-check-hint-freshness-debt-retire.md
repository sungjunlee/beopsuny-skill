---
id: BACK-207
title: clause_references.yaml 휘발성 값 live-check-hint 전환 (freshness_debt retire 조건 실행)
status: To Do
labels:
  - area:refactor
priority: high
milestone:
created_date: '2026-07-05'
---
## Description
## 배경 (2026-07-05 YAML 자산 전수 감사)

\`assets/data/clause_references.yaml\`(1,595줄)은 freshness_debt.yaml에 stale_registered·triage_only로 등록된 최대 리스크 자산. 레지스트리 스스로 retire 조건을 "남은 휘발성 값을 공식 소스로 갱신하거나 **live-check-only hint로 전환**"으로 명시. 후자를 실행한다 — 요율·기한·상한 같은 휘발성 숫자를 제거하고 "무엇을 어디서 확인하라" 힌트로 축약하면 갱신 주기가 필요 없는 issue-spotting 인덱스가 되어 유지보수 리스크가 구조적으로 소멸.

## AC

- [ ] clause_references.yaml의 휘발성 리터럴(요율·법정 기한·상한액·과징금·최저 기준 등 시간이 지나면 틀려지는 숫자) 전수 식별 후 제거, 각 항목을 "확인 대상(법령 family·조문 위치) + 확인 경로(로컬 미러/법망 API/law.go.kr)" 힌트로 대체
- [ ] 조항 유형 구조·issue-spotting 트리거·한국법 쟁점 힌트 등 비휘발성 가치는 보존 (파일의 목적은 계약 조항 이슈 후보 상기)
- [ ] freshness_debt.yaml에서 clause_references 엔트리 retire — assets/schemas/freshness_revalidation.yaml 필드 규격대로 revalidation record 작성, maintenance.next_review 갱신
- [ ] check_volatile_data_assets_runtime_contracts 등 이 파일에 결합된 static check 짝 수정
- [ ] O1 + O2 PASS
