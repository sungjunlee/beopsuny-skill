**LGTM.** 제공 패킷(README.md, result.json, corrected-control-audit.json, verification.json)만 대조했다. 중대한 분모 오류, INVALID 누락, 교정·재시도 혼동, 로딩·격리·비용 과장, 문서와 기계 결과 불일치는 없다.

교차 확인만 적는다. 실행 5건, 유효 품질 4건(FAIL 3, REVIEW_REQUIRED 1), 제외 1건이 같다. `084335`는 `INVALID_SETUP` / `INVALID_REVIEW_INPUT`이고 `quality_included: false`라 2×2 표에 넣지 않았다. `085034`는 setup 대체이며 `expansion: false`라 품질 재시도로 쓰지 않았다. native 로딩 입증(`actual_skill_body_proven: true` 2건)과 품질 미해결(`NO_GO_LOADING_FIX`, release `NO_GO`)을 분리했고, 물리 격리·Opus 단독 비용·지연 개선을 주장하지 않는다. Haiku 보조와 list USD 한계도 README와 `review_limits`가 같다. unit 136, O2 11/13, rescore 19/94 delta0, 소스 OK2/WARN3/FAIL0/미설치2가 verification과 같고, 동결 미러 WARN을 운영 최신성 통과로 쓰지 않는다. summary pending은 추출 원본, 최종은 root로 둔다는 점도 문서와 result가 같이 적는다.

**범위/한계:** 공개 기록의 분모·제외·교정 성격·과장·교차 숫자만 봤다. 법률 정답, runner 구현, 패킷 밖 파일(preregistered/summary/root-adjudication/modelUsage 등)은 미검증이다. 새 법률 오류 추측과 runtime 정책 제안은 하지 않았다.
