---
id: BACK-205
title: freshness maintenance 메타데이터 opt-in → 의무화 반전 + legal_terms.yaml 등록
status: To Do
labels:
  - area:refactor
priority: high
milestone:
created_date: '2026-07-05'
---
## Description
## 배경 (2026-07-05 YAML 자산 전수 감사)

\`check_asset_freshness_metadata_tracked\`는 \`maintenance:\` dict가 **있는** 자산만 검사하고 없으면 조용히 skip(opt-in). 그 결과 최대 자산 \`assets/data/legal_terms.yaml\`(1,908줄, 최종 업데이트 2024-12-07, 조문 인용성 항목 130건)이 freshness 체계 완전 밖에 있음 — freshness_debt.yaml에도 미등록. 새 자산 추가 시 maintenance를 잊으면 같은 구멍이 재발하는 구조.

## AC

- [ ] check를 opt-out으로 반전: \`assets/\` 하위 YAML은 maintenance 블록 의무. 예외는 명시적 allowlist(예: \`schemas/\` 사용자 상태 템플릿, \`policies/\` 중 순수 정책 파일 등 휘발성 사실이 없는 자산)로만 허용
- [ ] allowlist 선정 기준을 references/freshness-governance.md에 한 단락으로 문서화
- [ ] legal_terms.yaml에 maintenance 블록 추가(review_cycle, next_review, last_verified, source_url, freshness_days, must_reverify). last_verified를 현행화할 수 없으면 freshness_debt.yaml에 stale_registered로 등록하고 triage_only 사용 경계 명시
- [ ] 기존 30개 YAML 전부 반전된 check 통과(각 파일이 maintenance 보유 또는 allowlist 등재)
- [ ] O1 + O2 PASS
