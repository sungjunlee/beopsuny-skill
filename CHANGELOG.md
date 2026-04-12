# Changelog

## [0.1.0] - 2026-04-12

### Added
- `DESIGN.md` (레포 루트) — 아키텍처 결정 기록 + Multi-skill 전환 트리거 로드맵
  - 단일 스킬 유지 결정(2026-04-12) 객관적 근거 4가지 기록
  - v0.2.0 분리 트리거: DOCX 처리, 스케줄링, 피드백 3회, SKILL.md 800줄 초과
- Source Grading A/B/C/D 체계 (kipeum86/PIPA-expert 패턴 차용)
  - `skills/beopsuny/assets/policies/source_grades.yaml` — 정책 파일 (policies/ 디렉토리 신규)
  - `skills/beopsuny/references/source-grading.md` — 사람이 읽는 규칙 문서
  - 핵심 원칙 6번에 Source Grading 추가
  - 출력 포맷 예시에 `[Grade X] [VERIFIED]` 태그 반영
  - 2차 소스 `[EDITORIAL]` 태그, `[INSUFFICIENT]` 유보 예시 추가

### Changed
- `skills/beopsuny/SKILL.md` 데이터 소스 섹션 재작성
  - 기존 모드별 우선순위 표에 Grade 컬럼 추가
  - 각 순위 소스별 기본 Grade 명시 (legalize-kr=A, 하급심=B, 법망 API=A, WebSearch=C/D 등)
  - WebSearch 백업 도메인별 Grade 매핑 추가
- 기존 `[VERIFIED]` / `[UNVERIFIED]` / `[INSUFFICIENT]` 태그는 **유지**하고 Grade와 병기

### Notes
- SKILL.md 548줄 (분리 트리거 800 미만)
- 기존 자산 경로 변경 없음 (이슈 #4에서 처리 예정)
- 자가 검증 레이어는 이슈 #5에서 후속 작업

## [0.0.3] - 2026-04-11

### Fixed
- 자동 clone 제거: 데이터 없으면 Lite 모드 진입, clone은 영속 환경(Claude Code, Codex CLI)에서만 권장
- Chat 탭 채팅마다 스토리지 초기화 확인 — ephemeral 환경에서 clone 무의미
- `--depth 1` shallow clone 명시적 금지 (git log 개정 이력에 전체 히스토리 필요)
- 한글 깨짐 수정

## [0.0.2] - 2026-04-11

### Added
- Chat 탭 Lite 모드: Claude Desktop Chat 탭과 Codex CLI에서 법순이 사용 가능
- 능력 기반 모드 판별 (Full/Lite) — 플랫폼이 아니라 로컬 데이터 접근 여부로 분기
- 법률 조사 워크플로우에 Full/Lite 컬럼 추가 (●/⬚ 표기)
- Lite 모드 시각화 가이드: Mermaid 다이어그램, HTML table 등 Artifacts 활용
- 메모리 운영 모드별 분기 (Lite: 구두 수집, 기록 생략)
- `docs/desktop-chat-guide.md`: Chat 탭 설정 가이드 + 독립 프로젝트 지침 템플릿
- CLAUDE.md에 프로젝트 구조 섹션

### Changed
- 데이터 소스 명령어를 Bash 우선으로 변경 (Codex CLI 호환)
- 데이터 소스 우선순위를 모드별 테이블로 재구성

### Removed
- Glob/Grep 네이티브 도구 의존 제거
- `mkdir -p` 직접 호출 제거 (setup.js가 담당)

## [0.0.1] - 2026-04-11

- 초기 릴리즈: 법령/판례 조사, 계약서 검토, 컴플라이언스 체크
