# 리포트 산출물 계약

HTML 리포트는 법률 결론을 새로 만드는 workflow가 아니라, 기존 의도 결과를 보관·전달 가능한 문서로 렌더링하는 얇은 layer다. 내용 규칙은 항상 `references/output-formats.md`의 role/destination 계약을 따른다.

## 적용 범위

| 항목 | 계약 |
| --- | --- |
| 산출물 | Self-contained HTML report file |
| 기본 destination | `internal_legal_memo` |
| 기본 저장 위치 | `${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/reports/{YYYY-MM-DD}-{slug}.html` |
| 기본 전달 채널 | 로컬 파일 |
| 보관 범위 | 건별이 아니라 전역 디렉터리에 누적된다 |

## R1. 렌더 레이어 원칙

계약 문장: 리포트는 새로운 내용 규칙을 만들지 않는다. 리포트 생성 전 반드시 하나의 destination 계약을 선택하고, `references/output-formats.md`의 해당 destination이 정한 포함/제외 항목을 그대로 소비한다.

| 상황 | 적용 |
| --- | --- |
| 사용자가 destination을 지정하지 않음 | `internal_legal_memo` |
| 내부 검토·법무팀 메모 | `internal_legal_memo` |
| 현업 공유용 요약 | `business_summary` |
| 임원 보고 | `executive_report` |
| 상대방·고객·기관 등 외부 공유 | `external_draft` 또는 `agency_or_court_submission` |

`output-formats.md`와 `assets/schemas/output_contract.yaml`의 `non_overrides`는 리포트에서도 그대로 유효하다. 출처 성격·verification status·실제 확인 경로·적용 시점과 미확인 범위는 리포트에서도 인용과 연결한다. 표·각주·본문 어디에 표시해도 되며 같은 내용을 반복하지 않는다. 검토 상태와 필요한 전문 검토·외부 행동 전 확인 사항은 관련 위치에서 한 번 알린다.

계약 검토 리포트는 `references/contract_review_guide.md`의 요청 범위를 따른다. 수정 요청에는 `draft_clause`로 검토용 완성 문구를 제공할 수 있으며 이유·전제·미확인 사항을 함께 둔다. `alt_wording_hint`는 기존 후보 입력과의 호환 필드일 뿐 힌트형 출력만 허용하는 제한이 아니다. 무근거 적법성 보증·미확인 사실 확정·무권한 송부는 허용하지 않는다.

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
| 인용 링크 | 리포트의 조문·판례 citation에는 law.go.kr 공식 링크를 `<a href>`로 포함한다. 하이퍼링크는 콘텐츠이며 외부 리소스 로딩이 아니므로 self-contained 규격과 충돌하지 않는다. 링크 URL 형식은 `references/output-formats.md`의 링크 생성 규칙을 그대로 따른다 |
| 저장 경로 | `${BEOPSUNY_DATA_ROOT:-~/.beopsuny}/reports/{YYYY-MM-DD}-{slug}.html` |

파일명 `{slug}`는 사용자 요청이나 matter 이름을 ASCII-safe하게 축약한다. 충돌하면 `-2`, `-3`처럼 suffix를 붙인다.

`{slug}`가 matter 이름을 담고 본문이 그 건의 사실을 담으므로, 이 디렉터리는 건을 식별하는 산출물이 전역에 쌓이는 자리다. 스킬은 리포트를 자동으로 지우지 않는다 — 보존과 삭제는 사용자 책임이므로, 저장 경로를 처음 안내할 때 그 점과 `BEOPSUNY_DATA_ROOT`로 보관 위치를 건별·클라이언트별로 분리할 수 있다는 점을 함께 밝힌다. 이 디렉터리에 이미 있는 다른 건의 리포트는 사용자가 그 리포트와 건을 지명하지 않는 한 읽지 않는다 — 현재 건 답변을 만들면서 자동으로 참조하지 않는다. 지명 요청으로 읽어 비교한 결과가 대외 destination으로 나갈 때는 다른 건 식별 사실을 다시 제외한다. 근거 규칙은 SKILL.md `## 회사 맥락`의 matter 범위 제약과 `references/output-formats.md`의 destination 계약이다.

### 확인 범위와 생성 정보

생성일, 실제 읽은 범위와 제외 범위, 적용 시점·조회 실패·미확인 source가 결론에 미치는 영향을 문서에서 확인할 수 있게 한다. 본문이나 각주에 이미 있으면 고정 footer로 반복하지 않는다. 별도 내부 검토자 메모나 자가 검증 배지는 요청된 검토 기록에 유용할 때만 제공한다. 외부·비내부용 destination에는 내부 검토자 메모, 자가 검증 블록, internal scratchpad를 그대로 포함하지 않는다.

## R3. 전달 채널

계약 문장: 전달 채널은 모드 이름이 아니라 현재 세션의 능력(capability)으로 고른다. 환경 감지에 실패하면 로컬 파일을 먼저 시도한다. 파일 영속 쓰기가 불가한 환경이면 사용 가능한 Chat 탭 Artifacts 채널로 폴백할 수 있고, Claude Code Artifact 배포는 R4의 명시 요청 gate를 따른다.

| 채널 | 사용 조건 | 계약 |
| --- | --- | --- |
| 로컬 파일 | 파일시스템 영속 쓰기가 가능할 때 (기본) | 지정 경로에 HTML 파일을 저장하고 텍스트 답변에 경로를 함께 알린다 |
| Claude Code Artifact | Artifact 도구가 현재 세션에 있고 사용자가 Artifact/URL 배포를 명시적으로 요청했을 때 | 같은 self-contained HTML을 Artifact로 제공할 수 있다. 배포 시점부터 공유 가능 산출물로 취급하고 R4. Artifact 배포 gate를 적용한다 |
| Chat 탭 Artifacts | 파일 영속성이 없는 환경 | 같은 HTML 내용을 Chat 탭 Artifact로 표시한다. 영속 저장이 아님을 텍스트 답변에 표시한다 |

리포트 요청에는 파일 위치와 중요한 확인 한계를 짧게 안내하면 된다. 같은 법률 답변 전체를 채팅에 반복하지 않는다. 리포트 자체의 출처 성격과 확인 상태는 유지한다.

## R4. Artifact 배포 gate

계약 문장: Claude Code Artifact는 호스팅 URL이므로, 생성 시 내부용으로 만들었더라도 배포 시점부터 공유 가능 산출물로 취급한다. 이 gate는 공유 가정(내부 산출물을 외부로 내보내는 시점)의 중간 수위다 — 아래 표가 그 수위를 규정한다.

| 항목 | 계약 |
| --- | --- |
| 공유 가정 구성 강제 | Artifact로 배포하는 리포트는 기존 destination이 무엇이었든 배포본에서 내부 검토자 메모, 자가 검증 블록, 미확인 내부 노트를 제외한다. 검토용 초안 상태와 대외 사용 전 필요한 법무/변호사 검토를 배포본의 안내에서 명확히 표시한다. 고정 배너나 중복 면책은 요구하지 않는다 |
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

리포트 위치와 적용 destination, 사용에 영향을 주는 확인 한계를 짧게 안내한다. 리포트 본문을 채팅에 중복 출력하지 않는다.
