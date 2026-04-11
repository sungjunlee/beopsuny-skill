# 법순이 메모리 구조

## 런타임 데이터 위치: `~/.beopsuny/`

gstack 패턴을 따른다. 코드(`.claude/skills/`)와 데이터(`~/.beopsuny/`)를 분리.

```
~/.beopsuny/
├── config.yaml                    # 글로벌 설정
├── profile.yaml                   # 사용자 + 회사 프로필 (글로벌)
├── data/                          # 외부 데이터 소스 (git clone)
│   ├── legalize-kr/               # 법령 Markdown (full clone)
│   └── precedent-kr/              # 판례 Markdown (full clone)
└── projects/{slug}/               # 프로젝트별
    ├── learnings.jsonl            # 법률 지식 축적 (append-only)
    ├── reviews.jsonl              # 검토 이력 (append-only)
    ├── timeline.jsonl             # 스킬 실행 이력
    └── checkpoints/               # 세션 스냅샷
```

## 스키마 템플릿: `assets/schemas/`

`assets/schemas/` 디렉토리의 YAML은 초기 데이터 구조 참조용.
실제 데이터는 `~/.beopsuny/`에 저장된다.

| 스키마 | 용도 | 런타임 위치 |
|--------|------|------------|
| `company_profile.yaml` | 회사 속성 정의 | `~/.beopsuny/profile.yaml`의 company 섹션 |
| `watched_laws.yaml` | 관심 법령 구조 | `~/.beopsuny/profile.yaml`의 watched_laws 섹션 |
| `past_reviews.yaml` | 검토 이력 엔트리 구조 | `~/.beopsuny/projects/{slug}/reviews.jsonl` |
| `compliance_status.yaml` | 의무 이행 추적 구조 | `~/.beopsuny/profile.yaml`의 compliance 섹션 |
| `internal_rules.yaml` | 사내 규정 구조 | `~/.beopsuny/profile.yaml`의 internal_rules 섹션 |

## 글로벌 vs 프로젝트

| 데이터 | 위치 | 이유 |
|--------|------|------|
| 회사 프로필 | 글로벌 (`profile.yaml`) | 회사 정보는 프로젝트와 무관 |
| 관심 법령 | 글로벌 (`profile.yaml`) | 어떤 프로젝트든 같은 법령 추적 |
| 사내 규정 | 글로벌 (`profile.yaml`) | 회사 단위 |
| 컴플라이언스 상태 | 글로벌 (`profile.yaml`) | 연간 의무는 회사 단위 |
| 검토 이력 | 프로젝트별 (`reviews.jsonl`) | 맥락이 프로젝트에 종속 |
| 법률 지식 | 프로젝트별 (`learnings.jsonl`) | 발견한 인사이트는 맥락 의존 |

## learnings.jsonl 엔트리 구조

gstack 패턴 동일. append-only, read 시 key+type으로 dedup.

```json
{
  "type": "law|precedent|regulation|pitfall|preference|compliance",
  "key": "pipa-consent-exception-14yo",
  "insight": "14세 미만 아동의 개인정보 수집 시 법정대리인 동의 필요 (개인정보보호법 제22조의2)",
  "confidence": 10,
  "source": "law-verified|user-stated|inferred",
  "laws": ["개인정보 보호법 제22조의2"],
  "ts": "2026-04-11T03:00:00Z"
}
```

## reviews.jsonl 엔트리 구조

```json
{
  "id": "2026-04-11-001",
  "category": "개인정보",
  "question": "이 데이터 수집에 동의가 필요한지?",
  "conclusion": "법정대리인 동의 필요 (14세 미만 포함)",
  "laws": ["개인정보 보호법 제22조의2"],
  "caveats": "다만, 법률에 특별한 규정이 있는 경우 예외",
  "ts": "2026-04-11T03:00:00Z"
}
```
