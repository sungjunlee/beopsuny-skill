# Changelog

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
