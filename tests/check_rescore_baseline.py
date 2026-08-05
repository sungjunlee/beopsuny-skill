#!/usr/bin/env python3
"""차등 재채점 게이트 (#294) — 스코어러 판정 변화를 diff로 드러낸다.

커밋된 라이브 evidence corpus(`tests/forward_evals/evidence/*.yaml`)를 **현재
스코어러**로 전량 재채점해 체크인된 baseline(`tests/forward_evals/rescore_baseline.json`)과
대조한다. 이 파일이 이 계약의 집이다 — README 품질 계약 변경 체크리스트와
`tests/test_rescore_baseline.py`는 포인터만 둔다.

입력·출력: evidence의 `source_eval`로 config를 찾아 `score_one_prompt`에 태우고,
출력은 `{corpus: {prompt_id: [failure message]}}` 결정론적 직렬화(정렬 + JSON)다.

**핵심은 어휘가 아니라 구조다.** 이 게이트는 어떤 룰이 옳은지 판단하지 않는다 —
"판정이 바뀌었는데 아무도 그걸 선언하지 않았다"만 잡는다. 그래서 진동하지 않는다:

- baseline에 실패가 있고 실제 채점에 없으면 **완화**(스코어러가 느슨해짐)
- baseline에 없고 실제 채점에 있으면 **조임**(억제가 강해짐)

어느 쪽이든 판정 변화를 만든 PR은 **같은 PR에서 baseline을 명시적으로 갱신**
(`--write-baseline`)해야 그린이다. 갱신 없이 판정 변화가 diff에 남으면 FAIL한다 —
완화든 조임든 "조용한 통과"가 구조적으로 불가능하다.

**완화는 조임보다 강한 문구로 경고한다.** 이 레포의 사고는 완화 쪽에서 났다
(#282: 게이트 3종이 전부 그린인 채 FAIL 메시지 65 → 35가 통과했고, 그중 21건이
haiku 열화 모델 코퍼스였다). 완화 1건마다 baseline 갱신 PR에 근거를 남긴다.
조임도 조용히 통과시키지 않는다 — 의도된 억제 강화도 baseline 갱신으로 선언해야
한다.

corpus의 prompt가 현재 config에 없으면(은퇴·rename 누락) `["<prompt not in
current config>"]` 마커로 기록한다. 매핑되지 않은 rename은 `RENAMED_PROMPT_IDS`에
없으면 KeyError로 "채점 불가"가 되는데, 그 상태를 "계약이 바뀌어 실패"로 착각하지
않도록 마커가 명시적으로 드러낸다 (PR #261 선례).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "tests/forward_evals/evidence"
BASELINE_PATH = ROOT / "tests/forward_evals/rescore_baseline.json"

MISSING_PROMPT_MARKER = "<prompt not in current config>"

# 포인터용: 계약의 집은 이 모듈 docstring이다. 축약된 산문이 여기를 가리킨다 —
# `forward_eval_harness.py`의 `active_sentence_hit` docstring과
# `test_suppression_window_limits.py` 모듈 docstring.


def load_harness() -> Any:
    """테스트가 쓰는 것과 같은 방식으로 하네스를 로드한다 (importlib)."""
    spec = importlib.util.spec_from_file_location(
        "forward_eval_harness", ROOT / "tests/forward_eval_harness.py"
    )
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load tests/forward_eval_harness.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rescore_all() -> dict[str, dict[str, list[str]]]:
    """모든 커밋된 evidence corpus를 현재 스코어러로 재채점한다.

    반환: {corpus_파일_스템: {prompt_id: [실패 메시지]}} — 결정론적.
    corpus 키는 파일 스템이다 (evidence의 `name`이 아니라 — 이름은 바뀔 수
    있지만 파일 스템이 체크인 단위다).
    """
    harness = load_harness()
    result: dict[str, dict[str, list[str]]] = {}
    for path in sorted(EVIDENCE_DIR.glob("*.yaml")):
        data = harness.load_yaml(path)
        source_eval = str(data.get("source_eval") or "")
        config_path = (ROOT / source_eval) if source_eval else Path()
        if not config_path.exists():
            raise AssertionError(
                f"{path.name}: source_eval config not found: {source_eval!r}"
            )
        config = harness.load_forward_eval(config_path)
        prompts = {str(prompt["id"]): prompt for prompt in config["prompts"]}
        outputs = harness.load_outputs_capture(path)

        corpus: dict[str, list[str]] = {}
        for prompt_id, output in sorted(outputs.items()):
            if prompt_id not in prompts:
                corpus[prompt_id] = [MISSING_PROMPT_MARKER]
                continue
            scored = harness.score_one_prompt(prompts[prompt_id], output)
            messages = sorted(
                failure["message"] for failure in scored["failed_guardrails"]
            )
            if messages:
                corpus[prompt_id] = messages
        result[path.stem] = corpus
    return result


def serialize_failures(failures: dict[str, dict[str, list[str]]]) -> str:
    """결정론적 직렬화 — 같은 채점 결과는 항상 같은 바이트다."""
    return json.dumps(failures, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def load_baseline() -> dict[str, dict[str, list[str]]]:
    if not BASELINE_PATH.is_file():
        raise AssertionError(
            f"{BASELINE_PATH}: baseline 파일이 없다 — `python tests/check_rescore_baseline.py --write-baseline`으로 생성"
        )
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


def write_baseline(failures: dict[str, dict[str, list[str]]]) -> None:
    BASELINE_PATH.write_text(serialize_failures(failures), encoding="utf-8")


def classify_diffs(
    actual: dict[str, dict[str, list[str]]],
    baseline: dict[str, dict[str, list[str]]],
) -> tuple[dict[str, dict[str, list[str]]], dict[str, dict[str, list[str]]]]:
    """(완화, 조임)을 돌려준다 — 각각 {corpus: {prompt_id: [메시지]}}.

    완화 = baseline 실패가 실제에서 사라짐, 조임 = baseline 통과가 실제에서 실패.
    메시지 단위로 대조한다 — 같은 prompt의 일부 실패만 사라져도 완화로 잡힌다.
    """
    relaxed: dict[str, dict[str, list[str]]] = {}
    tightened: dict[str, dict[str, list[str]]] = {}
    for corpus in sorted(set(actual) | set(baseline)):
        actual_prompts = actual.get(corpus, {})
        baseline_prompts = baseline.get(corpus, {})
        for prompt_id in sorted(set(actual_prompts) | set(baseline_prompts)):
            actual_messages = set(actual_prompts.get(prompt_id, []))
            baseline_messages = set(baseline_prompts.get(prompt_id, []))
            lost = sorted(baseline_messages - actual_messages)
            gained = sorted(actual_messages - baseline_messages)
            if lost:
                relaxed.setdefault(corpus, {})[prompt_id] = lost
            if gained:
                tightened.setdefault(corpus, {})[prompt_id] = gained
    return relaxed, tightened


def _message_count(diffs: dict[str, dict[str, list[str]]]) -> int:
    return sum(
        len(messages)
        for prompt_messages in diffs.values()
        for messages in prompt_messages.values()
    )


def build_report(
    actual: dict[str, dict[str, list[str]]],
    baseline: dict[str, dict[str, list[str]]],
) -> tuple[str, int]:
    """(리포트 텍스트, exit code) — exit 1이면 판정 변화가 있다.

    완화는 조임보다 강한 문구로 경고한다 — 이 레포의 사고는 완화 쪽에서 났다 (#282).
    """
    relaxed, tightened = classify_diffs(actual, baseline)
    if not relaxed and not tightened:
        total_failures = sum(
            len(messages)
            for prompt_messages in actual.values()
            for messages in prompt_messages.values()
        )
        return (
            f"PASS: 판정 변화 0건 — baseline과 일치 "
            f"(corpus {len(actual)}, 실패 메시지 {total_failures}건)",
            0,
        )

    relaxed_count = _message_count(relaxed)
    tightened_count = _message_count(tightened)
    total_count = relaxed_count + tightened_count
    lines = [
        f"FAIL: 판정 변화 {total_count}건 (완화 {relaxed_count}건, 조임 {tightened_count}건) — "
        "baseline 갱신 없이는 이 게이트가 막는다. 스코어러/하네스 판정 로직을 "
        "건드렸으면 `--write-baseline`으로 baseline을 함께 갱신하고 PR 본문에 "
        "baseline diff를 붙인다."
    ]
    for corpus in sorted(set(relaxed) | set(tightened)):
        for prompt_id in sorted(
            set(relaxed.get(corpus, {})) | set(tightened.get(corpus, {}))
        ):
            if prompt_id in relaxed.get(corpus, {}):
                messages = relaxed[corpus][prompt_id]
                lines.append(
                    f"[완화] {corpus} / {prompt_id} — baseline 실패 {len(messages)}건이 사라졌다"
                )
                for message in messages:
                    lines.append(f"    - {message}")
                lines.append(
                    "    ← 스코어러가 느슨해졌다. 완화는 조임보다 강한 경고다 — "
                    "이 레포의 사고 방향이다 (#282). 같은 PR에서 baseline을 갱신하고 "
                    "완화 1건마다 근거를 남긴다."
                )
            if prompt_id in tightened.get(corpus, {}):
                messages = tightened[corpus][prompt_id]
                lines.append(
                    f"[조임] {corpus} / {prompt_id} — 새 실패 {len(messages)}건"
                )
                for message in messages:
                    lines.append(f"    - {message}")
                lines.append(
                    "    → 억제가 강해졌다 (조임). 의도된 변경이면 baseline 갱신으로 "
                    "선언하고, 아니면 되돌린다."
                )
    return "\n".join(lines) + "\n", 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="차등 재채점 게이트 — evidence corpus를 현재 스코어러로 재채점해 baseline과 대조한다"
    )
    parser.add_argument(
        "--write-baseline",
        action="store_true",
        help="현재 스코어러 판정으로 baseline을 재생성한다 (스코어러 변경 PR에서 사용).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="현재 재채점 결과를 결정론적 JSON으로 stdout에 출력한다 (PR 본문 diff용).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    actual = rescore_all()

    if args.json:
        sys.stdout.write(serialize_failures(actual))
        return 0

    if args.write_baseline:
        write_baseline(actual)
        changed = sum(
            len(messages)
            for prompt_messages in actual.values()
            for messages in prompt_messages.values()
        )
        print(
            f"baseline 갱신: {BASELINE_PATH} (corpus {len(actual)}, 실패 메시지 {changed}건)"
        )
        return 0

    baseline = load_baseline()
    report, exit_code = build_report(actual, baseline)
    sys.stdout.write(report)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
