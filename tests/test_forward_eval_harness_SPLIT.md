# #303 split — `test_forward_eval_harness.py`

(a) 하네스 구조·런처·합성 프로브 — `tests/test_forward_eval_harness.py`에 잔류.
(b) 커밋된 라이브 corpus 채점 재현 — `tests/check_rescore_baseline.py` / `tests/test_rescore_baseline.py`가 대체.

| Test | Class | Why |
| --- | --- | --- |
| `test_unregistered_category_fails_config_load` | (a) | config load 구조 |
| `test_registered_category_with_no_rules_is_accepted` | (a) | 카테고리 레지스트리 |
| `test_every_shipped_config_category_is_registered` | (a) | 출하 config 등록 |
| `test_downgrade_rules_accept_every_failure_status_tag` | (a) | 태그 집합 집 1곳 |
| `test_contract_downgrade_tags_match_the_skill_contract` | (a) | 계약 문서 파생 |
| `test_declarations_come_from_the_named_router_scenario` | (a) | 선언 plumbing |
| `test_a_cross_matter_leak_fails_the_live_layer` | (a) | 선언 유출 합성 프로브 |
| `test_a_clean_answer_does_not_trip_the_live_layer` | (a) | 과억제 합성 프로브 |
| `test_sample_outputs_score_and_write_deterministic_evidence` | (a) | sample 런처·evidence write |
| `test_failure_report_includes_prompt_category_and_output_evidence` | (a) | 실패 리포트 구조 |
| `test_o4_sample_outputs_all_pass` | (a) | o4 sample 런처 |
| `test_o4_fabricated_trap_output_is_caught` | (a) | 합성 함정 프로브 (evidence 없음) |
| `test_2026_07_09_false_positives_now_pass` | (b) | 20260709 corpus |
| `test_fwd02_recheck_2026_07_10_passes` | (b) | fwd02-recheck corpus |
| `test_fwd02_original_violation_still_fails` | (b) | 20260709 fwd-02 |
| `test_verified_conditional_forbidden_needs_provenance` | (a) | 합성 프로브 |
| `test_push_commitment_still_fails_when_automation_requested` | (a) | 합성 프로브 |
| `test_rhetorical_negation_does_not_whitewash_violation` | (a) | 합성 프로브 |
| `test_injection_compliance_quoting_ignore_still_fails` | (a) | 합성 프로브 |
| `test_guardrails_v050_release_corpus_all_pass` | (b) | v050 corpus |
| `test_o4_driver_corpus_2026_07_10_all_pass` | (b) | o4-driver corpus |
| `test_guardrails_v051_release_corpus_all_pass` | (b) | v051 corpus |
| `test_o4_v051_release_corpus_all_pass` | (b) | o4 v051 corpus |
| `test_quoted_forbidden_phrase_in_refusal_is_suppressed` | (a) | 합성 프로브 |
| `test_quote_does_not_shield_assertion_outside_the_quote` | (a) | 합성 프로브 |
| `test_new_negation_marker_suppresses_reading_warning` | (a) | 합성 프로브 |
| `test_premise_refutation_route_satisfies_downgrade` | (a) | 합성 프로브 |
| `test_schema_template_refusal_route_satisfies_schema_first` | (a) | 합성 프로브 |
| `test_data_root_item_counts_satisfy_investigation` | (a) | 합성 프로브 |
| `test_assumed_availability_without_inspection_still_fails` | (a) | 합성 프로브 |
| `test_shape_deviating_output_with_evidence_passes` | (a) | sample 출력 프로브 |
| `test_shape_case_fails_on_missing_evidence_not_on_shape` | (a) | 합성 프로브 |
| `test_guardrails_v070_release_corpus_matches_human_judgment` | (b) | v070 corpus (rubric 잔여는 (a)로 분리) |
| `test_fwd08_write_claim_lives_on_the_prompt_rubric` | (a) | v070에서 분리한 config rubric |
| `test_fwd10_confidential_lives_on_the_prompt_rubric` | (a) | v070에서 분리한 config rubric |
| `test_refusal_object_direct_action_is_suppressed` | (a) | 합성 프로브 |
| `test_direct_send_paraphrase_is_reserved_for_live_reading` | (a) | 합성 프로브 |
| `test_refused_pattern_label_suppresses_forbidden_phrase` | (a) | 합성 프로브 |
| `test_refusal_route_needs_both_stems_and_stays_sentence_scoped` | (a) | 합성 프로브 |
| `test_context_collection_in_conversation_satisfies_route` | (a) | 합성 프로브 |
| `test_write_promise_paraphrase_is_not_a_static_common_rule` | (a) | 합성 프로브 |
| `test_past_tense_write_claim_fails` | (a) | 합성 프로브 |
| `test_blind_write_without_redirect_still_fails` | (a) | 합성 프로브 |
| `test_full_refusal_route_satisfies_scope_boundary` | (a) | 합성 프로브 |
| `test_scope_route_single_stem_does_not_credit_and_overclaim_still_fails` | (a) | 합성 프로브 |
| `test_verification_gap_prose_satisfies_contradiction_and_strength` | (a) | 합성 프로브 |
| `test_fwd11_authority_label_miss_is_not_papered_over` | (b) | v070 fwd-11 |
| `test_hedge_stems_do_not_whitewash_memory_only_conclusion` | (a) | 합성 프로브 |
