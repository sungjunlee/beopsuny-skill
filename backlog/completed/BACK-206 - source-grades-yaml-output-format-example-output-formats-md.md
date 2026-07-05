---
id: BACK-206
title: '출력 예시 단일화: source_grades.yaml output_format/example 블록을 output-formats.md로 이관'
status: To Do
labels:
  - area:refactor
priority: medium
milestone:
created_date: '2026-07-05'
---
## Description
## 배경 (2026-07-05 YAML 자산 전수 감사)

출처 권위 라벨 출력 형식·예시가 3곳에 표현됨: \`assets/policies/source_grades.yaml\`(output_format + example_* 5블록), \`references/source-grading.md\`, \`references/output-formats.md\`. 태그 6종 정의성 서술도 SKILL.md, source-grading.md, source_grades.yaml, citation-verification-contract.md 4곳에 산재(나머지 파일들은 사용이라 무해). 원칙: **yaml=판정 데이터, md=절차, 출력 예시는 output-formats.md 한 곳**.

## AC

- [ ] source_grades.yaml에서 output_format/example_* 블록 제거. 예시가 output-formats.md에 없으면 이관, 있으면 중복 제거 후 yaml에는 output-formats.md 포인터 한 줄만
- [ ] 태그 의미의 정의 서술은 citation-verification-contract.md(VERIFIED 조건 계약) + source-grading.md(등급·다운그레이드)로 한정하고, source_grades.yaml existing_tag_mapping은 매핑 데이터만 유지
- [ ] 이관 과정에서 예시 문구 3곳 간 불일치가 발견되면 output-formats.md 기준으로 통일하고 차이점을 PR 본문에 기록
- [ ] validate_skill_contracts.py의 관련 check(source_grades 스키마·문구 assert) 짝 수정
- [ ] O1 + O2 PASS
