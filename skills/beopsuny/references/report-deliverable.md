# 리포트 산출물 계약

HTML 리포트는 법률 결론을 새로 만드는 workflow가 아니라, 기존 의도 결과를 보관·전달 가능한 문서로 렌더링하는 얇은 layer다. 내용 규칙은 항상 `references/output-formats.md`의 role/destination 계약을 따른다.

## 적용 범위

| 항목 | 계약 |
| --- | --- |
| 산출물 | Self-contained HTML report file |
| 기본 destination | `internal_legal_memo` |
| 기본 저장 위치 | `${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/reports/{YYYY-MM-DD}-{slug}.html` |
| 기본 전달 채널 | 로컬 파일 |

## R1. 렌더 레이어 원칙

계약 문장: 리포트는 새로운 내용 규칙을 만들지 않는다. 리포트 생성 전 반드시 하나의 destination 계약을 선택하고, `references/output-formats.md`의 해당 destination이 정한 포함/제외 항목을 그대로 소비한다.

| 상황 | 적용 |
| --- | --- |
| 사용자가 destination을 지정하지 않음 | `internal_legal_memo` |
| 내부 검토·법무팀 메모 | `internal_legal_memo` |
| 현업 공유용 요약 | `business_summary` |
| 임원 보고 | `executive_report` |
| 상대방·고객·기관 등 외부 공유 | `external_draft` 또는 `agency_or_court_submission` |

`output-formats.md`와 `assets/schemas/output_contract.yaml`의 `non_overrides`는 리포트에서도 그대로 유효하다. 출처 권위 라벨, verification status, Legal Verification Core, Freshness Governance, Role / Destination Gate, 변호사/법무 검토 필요 조건, 면책 고지는 리포트 스타일이나 시각적 축약으로 생략할 수 없다.

계약 검토 리포트에도 `assets/policies/review_mode.yaml#counter_draft_forbidden_patterns`가 그대로 적용된다. `alt_wording_hint`는 협상·검토 방향을 보존하기 위한 힌트 필드일 뿐이며, "아래 문구로 교체", "최종 수정안", "이 문구를 사용" 같은 대체 문구 제공으로 렌더링하지 않는다.

## R2. 파일 규격

계약 문장: 리포트는 self-contained HTML 1파일로 저장한다. 인라인 CSS만 사용하고 외부 리소스는 금지한다.

| 규격 | 계약 |
| --- | --- |
| 파일 수 | HTML 1파일 |
| CSS | `<style>` 안의 인라인 CSS만 허용 |
| JavaScript | 기본 금지. 필요한 정렬·토글은 외부 dependency 없이 작성한 짧은 inline script만 예외적으로 허용 |
| 외부 리소스 | CDN, 외부 폰트, 이미지 URL, `<script src>`, `<link href>`, `@import`, `fetch`, XHR 금지 |
| 이미지·도형 | 필요한 경우 data URI 또는 인라인 SVG만 사용 |
| 콘텐츠 이스케이프 | 사용자 제공 문서·출처 발췌 등 동적 텍스트는 HTML에 삽입하기 전에 이스케이프한다 (`<`, `>`, `&`, 따옴표) |
| 저장 경로 | `${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/reports/{YYYY-MM-DD}-{slug}.html` |

파일명 `{slug}`는 사용자 요청이나 matter 이름을 ASCII-safe하게 축약한다. 충돌하면 `-2`, `-3`처럼 suffix를 붙인다.

### 하단 고정 블록

계약 문장: 모든 리포트 하단에는 고정 metadata/footer block을 둔다.

| 필수 요소 | 내용 |
| --- | --- |
| 생성일 | 리포트 생성일과 가능한 경우 생성 시각 |
| 읽은 범위 | 읽은 문서, 페이지, 조항, 별첨, 조문 목록과 제외 범위 |
| 최신성 한계 | 현행성 확인 기준일, 조회 실패, 미확인 source, stale source 여부 |
| 면책 고지 | 법률 자문이 아니며 일반적인 법률 정보 제공 목적이고, 구체적 사안은 변호사와 상담해야 한다는 취지 |

destination이 `internal_legal_memo`처럼 내부용이고 내부 block 허용 destination이면 하단에 자가 검증 블록을 포함한다. destination이 `business_summary`, `executive_report`, `external_draft`, `agency_or_court_submission`처럼 외부 또는 비내부용이면 내부 검토자 메모, 자가 검증 블록, internal scratchpad를 그대로 포함하지 않는다.

## R3. 전달 채널

계약 문장: 전달 채널은 모드 이름이 아니라 현재 세션의 능력(capability)으로 고른다. 환경 감지에 실패하면 로컬 파일을 먼저 시도한다. 파일 영속 쓰기가 불가한 환경이면 사용 가능한 Chat 탭 Artifacts 채널로 폴백할 수 있고, Claude Code Artifact 배포는 R4의 명시 요청 gate를 따른다.

| 채널 | 사용 조건 | 계약 |
| --- | --- | --- |
| 로컬 파일 | 파일시스템 영속 쓰기가 가능할 때 (기본) | 지정 경로에 HTML 파일을 저장하고 텍스트 답변에 경로를 함께 알린다 |
| Claude Code Artifact | Artifact 도구가 현재 세션에 있고 사용자가 Artifact/URL 배포를 명시적으로 요청했을 때 | 같은 self-contained HTML을 Artifact로 제공할 수 있다. 배포 시점부터 공유 가능 산출물로 취급하고 R4. Artifact 배포 gate를 적용한다 |
| Chat 탭 Artifacts | 파일 영속성이 없는 Lite 환경 | 같은 HTML 내용을 Chat 탭 Artifact로 표시한다. 영속 저장이 아님을 텍스트 답변에 표시한다 |

Artifact나 Chat 탭 Artifacts가 가능해도 기본 법률 답변은 생략하지 않는다. 리포트는 텍스트 답변의 파생물이며, 출처 권위 라벨과 검증 상태를 숨기는 대체 출력이 아니다.

## R4. Artifact 배포 gate

계약 문장: Claude Code Artifact는 호스팅 URL이므로, 생성 시 내부용으로 만들었더라도 배포 시점부터 공유 가능 산출물로 취급한다. 이 gate는 PRD D4의 중간 수위다.

| 항목 | 계약 |
| --- | --- |
| 공유 가정 구성 강제 | Artifact로 배포하는 리포트는 기존 destination이 무엇이었든 배포본에서 내부 검토자 메모, 자가 검증 블록, 미확인 내부 노트를 제외한다. 면책 고지를 포함하고, 리포트 상단에 `법무/변호사 검토 전 대외 사용 금지` 배너를 명시한다 |
| 명시 요청 시에만 배포 | 사용자가 "Artifact", "URL", "공유 링크"처럼 배포를 명시적으로 요청할 때만 Artifact로 배포한다. 자동 배포 금지. 로컬 파일 저장은 기본 경로를 그대로 사용한다 |
| 재배포 고지 | 같은 파일 경로 재배포는 같은 URL 갱신일 수 있다. 이전 버전을 본 사람이 새 버전을 보게 되고, 배포 이력이 남을 수 있음을 사용자에게 알린다 |
| 승급 경로 | 배포 요청이 "상대방에게 보여줄", "고객에게 보낼", "기관에 제출할" 같은 외부 송부·공유·제출 맥락이면 단순 Artifact gate로 처리하지 않는다. `assets/schemas/output_contract.yaml#legal_effect_triggers`에 해당하는 요청으로 보아 `references/output-formats.md#destination-output-contracts`의 `external_draft` destination 규칙 + role/destination gate로 승급한다. 기관·법원 제출 맥락이면 같은 destination 표의 `agency_or_court_submission` 계약도 함께 확인한다 |

## R5. 트리거

계약 문장: 리포트는 새 의도가 아니다. `bulk_tabular_review`, `contract_review`, `legal_research`, `compliance_checklist` 같은 기존 의도 결과에 렌더 레이어를 얹는 출력 옵션이다.

| 사용자 발화 예시 | 처리 |
| --- | --- |
| "리포트로 만들어줘" | 기존 의도 수행 후 report deliverable 생성 |
| "HTML로 만들어" | 기존 의도 수행 후 self-contained HTML 파일 생성 |
| "문서로 정리해줘" | destination을 추정하거나 필요 시 확인하고 report deliverable 생성 |
| "팀에 공유할 문서로" | `business_summary` 등 공유 목적 destination gate 적용 |

리포트 요청이 있어도 텍스트 답변을 대체하지 않는다. 항상 텍스트 답변과 함께 리포트 위치, 적용 destination, 읽은 범위, 최신성 한계를 짧게 표시한다.
