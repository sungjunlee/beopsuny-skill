# Virtual Workflow Map

이 문서는 기존 `SKILL.md` 의도 라우터 위에 얹는 named workflow 인덱스다. 새 라우터 의도, 새 gate, 새 상세 절차를 만들지 않고 각 workflow가 이미 존재하는 의도와 reference를 어떻게 소비하는지만 보여준다.

| workflow | trigger 예시 | 주 의도(기존 라우터 의도명) | required references(기존 파일명) | output mode | verification 요구(Source Grade/freshness) |
| --- | --- | --- | --- | --- | --- |
| `commercial` | 계약 검토, NDA/SaaS 조항 위험, 협상 포인트 | `contract_review` | `contract_review_guide.md`, `checklist-routing.md`(해당 시), 조항 후보 자산은 `contract_review_guide.md`가 소유 | 위험 분석, 협상 포인트, 방향 힌트. 대외 redline 원문 또는 최종 수정안 금지 | 법률 결론은 공식 원문 또는 공식 응답으로 확인하고 Source Grade/verification status를 유지 |
| `privacy` | 개인정보 수집·이전·위탁·동의, 과징금 또는 고시 확인 | `legal_research`, 복잡한 개인정보 쟁점이면 보조 `privacy_knowledge_layer` | `source-access.md`, `research-workflow.md`, `knowledge-injection.md` | 개인정보 법률 조사 답변, 검색어 보강 또는 authority audit은 복잡한 경우에만 보조로 사용 | Source Grade 적용. 고시·과징금·제재 기준은 freshness gate와 live source 확인 필요 |
| `labor` | 근로계약, 인사규정, 징계·해고 절차, 임금·근로시간 | `legal_research` | `source-access.md`, `research-workflow.md` | 법령·행정규칙·판례 기반 조사 메모와 실무상 확인 항목 | 조문·행정규칙·판례 원문 확인. 기한·금액·제재는 freshness 상태 표시 |
| `regulatory` | 업종별 컴플라이언스, 인허가, 연간 의무, 준비 서류 | `compliance_checklist` | `checklist-routing.md` | 후보 체크리스트, 준비 항목, 확인 필요 정보. 현재 의무 단정은 live 확인 뒤에만 | 현행 의무·기한·과징금·서식·관할기관은 live source 확인 전 `[STALE]` 또는 `[INSUFFICIENT]` |
| `litigation` | 분쟁 쟁점, 판례, 소송·기관 제출 전 법리 검토 | `legal_research` | `research-workflow.md`, `self-verification.md` | 판례 중심 조사 메모와 요건·사실·증거 분리 판단 구조 + 판례 distinguishing. 결과 예측이 아니라 검토용 쟁점 정리 | 판례는 사건번호·선고일·공식 원문을 확인. self-verification 통과 전 결론 강도 유보 |
| `startup` | 설립·지분·계약·개인정보·규제가 섞인 초기기업 질문 | `legal_research` 기본, 계약 쟁점이면 `contract_review`, 인허가·규제면 `compliance_checklist`; 복합 요청은 주 의도 1개 선택 후 필요한 보조 workflow만 추가 | 선택한 주 의도 row의 조합: `research-workflow.md`, `contract_review_guide.md`, `checklist-routing.md`, `knowledge-injection.md`, `source-access.md` | 주 의도 산출물 우선. 보조 workflow는 누락 쟁점 인덱스나 확인 질문으로만 사용 | 선택된 workflow별 Source Grade/freshness 요구를 그대로 합성하고, 실패 라우트는 `[INSUFFICIENT]`로 degrade |
| `cross-border` | 한국회사의 해외진출, 해외직접투자, 전략물자, 국제조세, 국외이전 | 새 의도 아님: `legal_research` 또는 `compliance_checklist` | `international_guide.md`를 인덱스로 소비하고, 주 의도에 따라 `research-workflow.md` 또는 `checklist-routing.md` | 한국법 overlay 쟁점 지도와 확인 항목. #112 확장 로드맵은 후속 자리만 둠 | jurisdiction/currency/source caveat 기본 포함. 해외/한국 source 모두 결론 근거는 현재 확인한 공식 소스로 한정 |

모든 workflow에 always-on 법률 결론 gate가 그대로 적용되며, map은 어떤 gate도 workflow별로 분리·약화하지 않는다.

물리적 plugin split 전 = 단일 `beopsuny` 안의 virtual workflow 인덱스이며, 이 문서의 workflow 이름은 라우터 의도명이 아니다. 물리적 plugin split 후 = per-workflow plugin으로 승격될 수 있는 문서 경계지만, split 판단은 [DESIGN.md §6 후속 트리거 참조](../../../DESIGN.md#2026-05-10-단일-스킬-유지--내부-router-spine-전환)에만 정렬하고 추가 trigger를 만들지 않는다.
