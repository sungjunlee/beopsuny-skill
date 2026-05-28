---
snapshot_date: "2026-05-27"
source_assets:
  - file: "beopsuny-knowledge:privacy/assets/taxonomy.yaml"
    version: "2026.04.20.1"
    updated_at: "2026-04-20T11:10:00+09:00"
  - file: "beopsuny-knowledge:privacy/assets/authority-map.core.yaml"
    version: "2026.05.02.1"
    updated_at: "2026-05-02T20:05:00+09:00"
  - file: "beopsuny-knowledge:privacy/assets/authority-map.overlay.yaml"
    version: "2026.04.24-overlay.18"
    updated_at: "2026-05-02T20:42:00+09:00"
note: >
  beopsuny-knowledge source asset에서 추출한 정적 스냅숏.
  source asset 갱신 시 이 파일도 수동 sync.
  snapshot_date가 30일 이상 지났으면 최신성 주의.
---

# 개인정보 사전지식

## 1. Issue framing — taxonomy (blind search 전)

복합 개인정보 질문에서는 live search에 들어가기 전에 아래 축으로
쟁점을 분해한다. 이 축은 검색 방향을 넓히기 위한 framing 도구일 뿐,
결론을 강제하지 않으며 체크리스트로 쓰지 않는다.

| 축 | code | 질문 분해 시 확인할 포인트 |
|----|------|--------------------------|
| **수집·이용** | `collection_use` | 동의 근거 유형(법령상 의무 vs 계약 이행 vs 동의), 목적 범위 초과 여부, 최소수집 원칙, 보유기간, 2차 활용 경로 |
| **제공·위탁** | `sharing_structure` | 수탁사 vs 제3자 제공 분기, 재위탁 구조, 처리방침의 이전받는 자 정보와 실제 위탁 계약의 일치 여부 |
| **국외이전** | `cross_border` | 저장(Storage)·접근(Access)·백업(Backup)·지원접근(Support Access) 경로 분리 확인, DPA 체결, 서브프로세서 목록 최신성, 처리방침 고지 충실성 |
| **안전성 확보조치** | `security_controls` | 접근권한 관리, 암호화(전송·저장), 접속기록(보존·점검), 내부관리계획 |
| **정보주체 권리** | `data_subject_rights` | 열람·정정·삭제·처리정지 청구 절차, 본인확인 방법, 처리기한(열람 10일·그 외 30일), opt-out 전파 확인(삭제요청 → 수탁사/서브프로세서까지) |
| **침해사고** | `incident_response` | 통지·신고 기준(1천명 기준·민감정보 분기), 72시간 이내 PIPC 신고·지체 없이 정보주체 통지, 증적보전, 초기 차단 조치, 현행법 결론과 시행예정(2026.9.11 개정법: 유출 가능성 통지제) 전환 리스크 분리 |

**사용법**: 질문에 해당하는 축 1~2개를 골라서 검색어와 확인할 source family를 넓힌다.
6개 축을 전부 적용하지 않는다.

## 2. Post-search audit — authority map (blind search 후)

Live search로 1차 답변을 만든 뒤, 아래 축을 빠뜨리지 않았는지 점검한다.
authority map은 search route oracle이 아니라 사후 누락 점검표다.

- DPA가 처리방침의 이전받는 자 정보와 일치하는지 — 불일치는 live search에서 놓치기 쉬운 함정
- 서브프로세서 목록의 **최신 변경일**이 언제인지 — 목록이 오래됐으면 그 자체가 위험 신호
- SDK/태그 이벤트가 **목적별로 매핑**되어 있는지 — "서비스 필수" vs "광고·분석·맞춤형" 구분 없이 수집되고 있다면 동의 기반 취약
- 보존 예외 데이터의 **접속기록**이 정기적으로 점검되는지 — 파기유예 중인 개인정보는 보안 수준을 평소보다 강화해야 함
- 통지·신고 판단표에 **현행법 결론과 시행예정 전환 리스크**가 분리되어 있는지 — 시행예정 개인정보보호법(2026.9.11 시행, 유출 가능성 통지제 신설)을 현행법 기준으로 오답변하지 않도록
- **server-side tag forwarding** 경로가 벤더별로 매핑되어 있는지 — 태그 매니저 이벤트가 2차·3차로 전파되는 경로를 모르면 국외이전·제3자 제공 판단이 불완전

**사용법**: 1차 답변을 완성한 뒤, 해당 쟁점의 audit 축을 빠르게 훑는다.
누락이 발견되면 추가 live search로 보강한다. 결론을 이 축으로 교체하지 않는다.

## 경계

- Section 1(taxonomy)은 blind search 전 issue framing용, Section 2(authority map)는 post-search audit용
- blind search를 건너뛰고 authority map으로 초기 route를 정하지 않는다
- 법적 결론은 항상 live search + Source Grade에 근거한다 — 이 파일의 텍스트를 결론 근거로 인용하지 않는다
- 단순 조문·시행일·링크 확인 질문에는 이 파일 전체를 생략한다
- `snapshot_date`가 30일 이상 지났으면 live search 결과를 우선하고 이 파일의 구체적 수치(처리기한, 시행일 등)는 확인 필요로 취급한다
- `knowledge-injection.md`의 blind-first 원칙이 이 파일보다 우선한다
