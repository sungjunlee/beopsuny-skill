# 같은 CLI의 입력 단순화 비교 결과

2026-09-16 KST, Claude Opus5 high / CLI2.1.271 / 동결 runtime41파일과 법령미러를 유지해 각1회 실행했다. 대조군은 PR348 실제 append, 단순화군은 실행자 설명과 5행 강제를 덜어낸 묶음 처치다. 두 실행 모두 rc0/provider success, Skill 로드 확인, 사후 전체 trace상 범위 밖 성공읽기0이다.

| 조건 | 소요 시간 | 도구 호출 | CLI list 가격 | root / 독립 |
| --- | ---: | ---: | ---: | --- |
| 대조군 | 110.921초 | 9 | $0.550622 | FAIL / FAIL |
| 단순화군 | 132.022초 | 13 | $0.734798 | FAIL / FAIL |

대조군은 수정안 검토·내부 검토 진행, 단순화군은 수정안 검토·현재 문언의 불명확성을 제공 자료 없이 서술했다. 둘 다 별건30억은 배제했고 편집 가능한 초안을 제공했다. 법률 근거/적용 한계는 독립 REVIEW_REQUIRED이며 전문가 정답 보증이 아니다. 별첨 초안을 실제 답변에 제공한 것과 파일을 실제 발송한 것은 구별한다.

판정은 **개선책 채택 NO_GO**다. 입력 단순화만으로 이 쌍의 오류는 해결되지 않았다. n=1씩·묶음 처치·순차실행/캐시 때문에 단순화가 무효하거나 더 비싸다는 인과 결론은 내리지 않는다. 총 list 가격 $1.28542는 Max 현금 청구액이 아니다. 반복/holdout/새 정책 문구 추가 없이 종료한다.

blind-review-input.json의 X=단순화,Y=대조이며 reviewer에게 mapping·모델·기대판정을 제공하지 않았다. independent-review.json과 root result.json을 분리했다. raw stream/사고 내용/인증자료는 공개하지 않는다. summary의 과거 extractor setup 후보는 지우지 않고 audit.json에서 실제 허용 roots/거부복구 규칙으로 대조했다. plan.json의 상속된 과거 metadata와 실행을 구별하며 execution-plan.json이 현재 argv와 재계산 hash를 제공한다.

스킬 정책 변경 없음. 기존 평가 오탐 수정의 타당성과 모델 출력 회귀 해결은 별개다. AC5/릴리즈 완료 근거가 아니며 #323 자동 CLOSED를 PASS로 해석하지 않는다.
