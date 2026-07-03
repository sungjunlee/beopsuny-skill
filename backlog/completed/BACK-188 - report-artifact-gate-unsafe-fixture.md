---
id: BACK-188
title: '[Report] Artifact 배포 gate — 공유 가정 구성 강제 + unsafe fixture'
status: To Do
labels:
  - enhancement
  - area:architecture
  - area:patterns
  - area:refactor
priority: low
milestone:
created_date: '2026-07-03'
---
## Description
Part of #184 — PRD S3/R4, #185·후속 템플릿 이후 (계약·템플릿 안정 후 마지막)

## 작업

Claude Code 환경에서 리포트를 Artifact(호스팅 URL)로 배포할 때의 gate. Artifact는 "생성 시 내부용 → 나중에 한 클릭 공유" 경로가 있으므로 공유 가능 산출물로 취급한다.

1. `references/report-deliverable.md`에 Artifact 배포 절 추가 (채택 수위 D4=중간):
   - 배포 시 **공유 가정 구성 강제**: 내부 검토자 메모·미확인 내부 노트 제외, 면책 고지 포함, "법무 검토 전 대외 사용 금지" 배너
   - 사용자가 명시 요청할 때만 배포 (자동 배포 금지 — pull-first와 일관)
   - 재배포는 같은 URL 갱신임을 사용자에게 고지 (이전 버전 노출 이력 주의)
2. legal_effect_triggers 연동: 배포 요청이 외부 송부 맥락("상대방에게 보여줄", "기관에")이면 external_draft 규칙 + role/destination gate로 승급
3. O2 unsafe fixture: 내부 자가 검증 블록이 그대로 포함된 Artifact 배포 출력이 FAIL로 잡힘

## AC

- [ ] Artifact 배포 절이 report-deliverable.md에 존재, D4 수위 명문화
- [ ] unsafe fixture + guardrail rule 추가, 정상 배포 출력은 PASS
- [ ] 외부 송부 맥락 승급 경로가 output-formats destination 계약과 모순 없음
- [ ] O1/O2 PASS

참고: Mermaid/다이어그램은 여전히 범위 밖 (보류 유지).

