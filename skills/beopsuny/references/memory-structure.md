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
    ├── project.yaml                # 프로젝트 상태와 맥락
    ├── learnings.jsonl            # 법률 지식 축적 (append-only)
    ├── reviews.jsonl              # 검토 이력 (append-only)
    ├── verification_log.jsonl      # 사용자 확인 이력 (append-only)
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

## Quick / Full 온보딩

사용자가 "회사 정보를 저장해줘", "법순이 설정해줘"처럼 프로필 설정을 요청하면 `memory_profile` 의도로 처리한다. 기본은 quick 온보딩이다.

다만 요청에 playbook 설정 의도(예: "계약 검토 playbook을 맞춰줘")가 포함되면 full 온보딩으로 즉시 전환한다. 모호한 경우에는 quick 시작 전에 "계약 playbook 항목까지 함께 설정할까요?"라고 확인한다.

### quick 온보딩

필수 질문은 짧게 묶는다.

1. 회사명 또는 비공개 여부
2. 업종, 회사 유형, 직원 수
3. 주요 사업장/관할과 해외 사업 여부
4. 개인정보 처리 여부와 정보주체 규모
5. 관심 법령
6. 사용자 역할: 변호사/법무 담당자/비법무 담당자/미확인

저장 전에는 요약을 보여주고 "저장할까요?"를 확인한다. 사용자가 건너뛴 항목은 빈 값 또는 `unknown`으로 남기되, 조용히 추정하지 않는다.

### full 온보딩

quick 항목에 아래 계약 검토 playbook 항목을 추가한다.

- 기본 역할: 고객/공급자/플랫폼/미확인 (`contract_playbook.default_role`)
- 조항별 당사자 위치: 기존 `party_position`의 `gap`/`eul` 체계를 유지
- 위험 선호: conservative/moderate/aggressive
- 표준 입장: 책임제한, 면책, 개인정보, 해지, 준거법·분쟁해결
- 허용 fallback
- 절대 불가 항목
- 자동 escalation trigger
- 참고할 seed document의 존재 여부와 종류

seed document는 사용자가 명시적으로 제공한 경우에만 읽는다. 자동으로 다운로드하거나 저장하지 않는다. seed document에서 추출한 playbook 후보는 저장 전 사용자에게 확인받는다.

### 재실행과 수정

- 일부 수정 요청은 해당 필드만 갱신한다.
- full 온보딩 재실행은 기존 값을 먼저 요약하고, 덮어쓸 항목을 확인한다.
- 사용자 확인 없이 `~/.beopsuny/profile.yaml`에 쓰지 않는다.
- Lite 모드처럼 파일 쓰기가 불가능한 환경에서는 저장 예정 요약만 제공하고, 영속 저장을 약속하지 않는다.

## 글로벌 vs 프로젝트

| 데이터 | 위치 | 이유 |
|--------|------|------|
| 회사 프로필 | 글로벌 (`profile.yaml`) | 회사 정보는 프로젝트와 무관 |
| 관심 법령 | 글로벌 (`profile.yaml`) | 어떤 프로젝트든 같은 법령 추적 |
| 사내 규정 | 글로벌 (`profile.yaml`) | 회사 단위 |
| 컴플라이언스 상태 | 글로벌 (`profile.yaml`) | 연간 의무는 회사 단위 |
| 검토 이력 | 프로젝트별 (`reviews.jsonl`) | 맥락이 프로젝트에 종속 |
| 법률 지식 | 프로젝트별 (`learnings.jsonl`) | 발견한 인사이트는 맥락 의존 |
| 사용자 확인 이력 | 프로젝트별 (`verification_log.jsonl`) 또는 글로벌 | 프로젝트별 사실은 프로젝트에, 반복 사용되는 일반 법령 확인은 글로벌에 기록 |

## 프로젝트 workspace 경계

프로젝트는 거래, 계약 묶음, 분쟁, 컴플라이언스 점검처럼 맥락이 유지되어야 하는 작업 단위다.

기본 원칙:

- 사내법무 기본값은 글로벌 회사 프로필 + 명시된 프로젝트 맥락이다.
- 프로젝트별 검토에서는 다른 프로젝트의 `reviews.jsonl`, `learnings.jsonl`, `verification_log.jsonl`을 자동으로 읽지 않는다.
- cross-project context 기본값은 `off`다.
- 사용자가 "다른 프로젝트와 비교", "지난 계약들 기준으로", "전체 이력에서"처럼 명시한 경우에만 필요한 프로젝트를 묻고 읽는다.
- 프로젝트 archive는 삭제가 아니라 `projects/_archived/{slug}/`로 보관하는 개념이다.

`project.yaml` 최소 구조:

```yaml
slug: ""
status: "active"        # active | archived
opened_at: ""
closed_at: ""
client_or_business_unit: ""
counterparty: ""
matter_type: ""         # contract | compliance | dispute | research | other
confidentiality: "standard"  # standard | heightened
key_facts: ""
overrides:
  party_position: ""
  contract_playbook: {}
cross_project_context: "off"
```

프로젝트 맥락이 필요한지 질문해야 하는 경우:

- 계약 검토에서 같은 상대방/거래의 이전 수정 이력을 참조하려는 경우
- 컴플라이언스 체크리스트에서 특정 제품, 사업장, 인허가 상태가 누적되는 경우
- verification log나 과거 검토 이력을 근거 후보로 사용할 경우

단순 조문 확인, 법령 시행일 확인, 일반 용어 설명은 프로젝트 선택을 요구하지 않는다.

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

## verification_log.jsonl 엔트리 구조

사용자 또는 담당자가 1차 소스로 확인한 사실을 append-only로 기록한다. 이 기록은 결론 근거가 아니라 재확인 힌트다. Source Grade A/B는 현재 세션에서 원문 또는 공식 API를 확인했을 때만 부여한다.

```json
{
  "id": "2026-05-20-001",
  "fact_type": "law|precedent|regulation|deadline|amount|form|other",
  "key": "pipa-article-28-8-cross-border-transfer",
  "statement": "개인정보 국외이전은 개인정보 보호법 제28조의8 기준으로 확인한다.",
  "verified_by": "user",
  "source": "law.go.kr 개인정보 보호법 제28조의8",
  "source_url": "https://www.law.go.kr/법령/개인정보보호법/제28조의8",
  "verdict": "confirmed",
  "freshness_days": 90,
  "verified_at": "2026-05-20T09:00:00+09:00"
}
```

운영 규칙:

- 쓰기 전 사용자에게 "이 확인 이력을 기록할까요?"라고 묻는다.
- `verdict`는 `confirmed`, `corrected`, `could_not_verify` 중 하나를 사용한다.
- `freshness_days`가 지나면 이전 확인 사실을 그대로 결론에 쓰지 않고 재확인 필요로 표시한다.
- Lite 모드에서는 파일 기록 대신 대화 내 확인 메모만 제공한다.
- 법령 개정 가능성이 큰 시행일, 과징금 기준, 고시, 행정규칙은 짧은 freshness window를 둔다.
