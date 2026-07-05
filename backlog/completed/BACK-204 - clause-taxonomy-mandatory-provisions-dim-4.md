---
id: BACK-204
title: '죽은 자산·끊긴 라우팅 수리: clause_taxonomy 삭제 + mandatory_provisions Dim 4 라우팅 복구'
status: To Do
labels:
  - area:architecture
  - area:refactor
priority: high
milestone:
created_date: '2026-07-05'
---
## Description
## 배경 (2026-07-05 YAML 자산 전수 감사)

- \`assets/policies/clause_taxonomy.yaml\`(160줄)은 SKILL.md·references 어디서도 로드하지 않는 죽은 자산. 참조는 README 자산 표 한 줄뿐이고, \`check_readme_asset_inventory_counts\`가 그 표 기재를 강제해 죽은 자산을 화석화 중.
- \`assets/policies/mandatory_provisions.yaml\`(133줄)은 헤더가 "SKILL.md Dim 4 서브체크 1에서 참조"라 선언하지만, Dim 4는 \`references/self-verification.md\`로 이관됐고 해당 서브체크(강행규정, 87행 부근)는 이 파일을 가리키지 않음. 실제 참조는 source-grading.md 지나가는 언급 1회.

프루닝 원칙(에픽 #174): 죽은 자산은 retire-first(등록 아닌 삭제).

## AC

- [ ] clause_taxonomy.yaml 삭제. README 자산 표에서 제거, \`validate_skill_contracts.py\`의 policy_name 목록(2553행 부근)과 README 인벤토리 check 짝 수정
- [ ] mandatory_provisions.yaml을 self-verification.md Dim 4 강행규정 서브체크에서 명시 라우팅(후보 인덱스로 참조, 결론 근거 아님 경계 유지)
- [ ] mandatory_provisions.yaml 헤더의 죽은 anchor를 현행 구조(self-verification.md Dim 4)로 수정
- [ ] clause_taxonomy 삭제로 끊기는 참조 0건 확인 (\`grep -r clause_taxonomy\` 잔존 없음)
- [ ] O1(\`validate_skill_contracts.py\`) + O2(\`evaluate_scenario_outputs.py\`) PASS
