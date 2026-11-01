#!/usr/bin/env python3
"""차등 재채점 게이트 (#294) — 스코어러 판정 변화를 diff로 드러낸다.

커밋된 라이브 evidence corpus(`tests/forward_evals/evidence/*.yaml`)를 **현재
스코어러**로 전량 재채점해 체크인된 baseline(`tests/forward_evals/rescore_baseline.json`)과
대조한다. 이 파일이 이 계약의 집이다 — README 품질 계약 변경 체크리스트와
`tests/test_rescore_baseline.py`는 포인터만 둔다.

입력·출력: evidence의 `source_eval`로 config를 찾아 `score_one_prompt`에 태우고,
출력은 schema 2 스냅샷이다. `failures`는
`{corpus: {prompt_id: [failure 또는 REVIEW_REQUIRED 또는 UNSCORABLE message]}}`
이고, 메시지가 없는 통과 입력은 넣지 않는다(빈 메시지 배열로 통과를 표시하지
않는다). `inventory`는 `{corpus: [prompt_id, ...]}`로 그 capture에 들어 있던
id만 정렬해 담는다. id는 `outputs` 키와 `results`/`prompts`의 `prompt_id`를
합친 것이다. 현재 config의 전체 id를 부분 capture에 채우지 않는다.

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

커밋된 corpus를 다시 채점하던 하네스 테스트는 이 스캔이 대체한다 (#303).
합성 프로브·런처 구조는 `tests/test_forward_eval_harness.py`가 남긴다.

통과 입력이 capture에서 빠지면 실패 메시지는 그대로라 메시지 diff만으로는
PASS가 된다 (#373). inventory diff가 그 누락·추가를 `[입력 누락]`/`[입력 추가]`로
보고한다. 출력 문자열이 비어 있으면 계속 `UNSCORABLE`이고, 실행 기록만 남고
출력이 없는 id도 `UNSCORABLE`이다. 누락과 채점불가는 모델 실패나 스코어러
완화로 보고하지 않는다.

schema 없는 구형 baseline은 실패 맵으로 읽는다. 새 스냅샷과 비교할 때
inventory가 없으면 id 누락을 통과로 세지 않고, 완화로 이름 붙이지 않은 채
`--write-baseline`을 요구한다.
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
MISSING_OUTPUT_MARKER = "UNSCORABLE: captured output missing"
SCHEMA_VERSION = 2

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


def capture_inventory(harness: Any, data: dict[str, Any]) -> list[str]:
    """capture가 스스로 선언한 prompt id. config 전체로 채우지 않는다."""
    seen: set[str] = set()

    def add(raw: object) -> None:
        prompt_id = harness.canonical_prompt_id(str(raw))
        seen.add(prompt_id)

    outputs = data.get("outputs")
    if isinstance(outputs, dict):
        for key in outputs:
            add(key)
    for row_key in ("results", "prompts"):
        rows = data.get(row_key)
        if not isinstance(rows, list):
            continue
        for item in rows:
            if isinstance(item, dict) and item.get("prompt_id"):
                add(item["prompt_id"])
    return sorted(seen)


def rescore_all() -> dict[str, Any]:
    """모든 커밋된 evidence corpus를 현재 스코어러로 재채점한다.

    반환: schema 2 스냅샷 — failures는 메시지가 있는 id만, inventory는 capture에
    들어 있던 id 전부. corpus 키는 파일 스템이다 (evidence의 `name`이 아니라 —
    이름은 바뀔 수 있지만 파일 스템이 체크인 단위다).
    """
    harness = load_harness()
    failures: dict[str, dict[str, list[str]]] = {}
    inventory: dict[str, list[str]] = {}
    for path in sorted(EVIDENCE_DIR.glob("*.yaml")):
        data = harness.load_yaml(path)
        if not isinstance(data, dict):
            raise AssertionError(f"{path.name}: expected mapping")
        source_eval = str(data.get("source_eval") or "")
        config_path = (ROOT / source_eval) if source_eval else Path()
        if not config_path.exists():
            raise AssertionError(
                f"{path.name}: source_eval config not found: {source_eval!r}"
            )
        config = harness.load_forward_eval(config_path)
        prompts = {str(prompt["id"]): prompt for prompt in config["prompts"]}
        outputs = harness.load_outputs_capture(path)
        executions = harness.load_execution_capture(path)
        captured_ids = capture_inventory(harness, data)

        corpus: dict[str, list[str]] = {}
        for prompt_id in captured_ids:
            if prompt_id not in prompts:
                corpus[prompt_id] = [MISSING_PROMPT_MARKER]
                continue
            if prompt_id not in outputs:
                corpus[prompt_id] = [MISSING_OUTPUT_MARKER]
                continue
            output = outputs[prompt_id]
            prompt = prompts[prompt_id]
            execution = executions.get(prompt_id, {})
            if execution.get("execution_status", "completed") != "completed" or not output.strip():
                corpus[prompt_id] = ["UNSCORABLE: captured execution did not complete"]
                continue
            if prompt.get("setup") is not None:
                if not harness.setup_evidence_matches(prompt, execution):
                    corpus[prompt_id] = ["UNSCORABLE: required setup evidence absent or mismatched"]
                    continue
            scored = harness.score_one_prompt(prompt, output)
            messages = sorted(
                failure["message"] for failure in scored["failed_guardrails"]
            )
            messages.extend(
                f"REVIEW_REQUIRED: semantic rule {review['rule']} — {review['reason']}"
                for review in scored.get("review_required", [])
            )
            messages.sort()
            if messages:
                corpus[prompt_id] = messages
        failures[path.stem] = corpus
        inventory[path.stem] = captured_ids
    return {"schema": SCHEMA_VERSION, "failures": failures, "inventory": inventory}


def serialize_failures(failures: dict[str, Any]) -> str:
    """결정론적 직렬화 — 같은 채점 결과는 항상 같은 바이트다."""
    return json.dumps(failures, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def split_snapshot(
    data: dict[str, Any],
) -> tuple[dict[str, dict[str, list[str]]], dict[str, list[str]] | None]:
    """schema 2 스냅샷 또는 구형 실패 맵을 (failures, inventory|None)으로 나눈다."""
    if (
        isinstance(data, dict)
        and data.get("schema") == SCHEMA_VERSION
        and isinstance(data.get("failures"), dict)
        and isinstance(data.get("inventory"), dict)
    ):
        return data["failures"], data["inventory"]
    if isinstance(data, dict) and all(isinstance(value, dict) for value in data.values()):
        return data, None
    raise AssertionError(
        "rescore baseline shape is not a failure map or schema 2 snapshot"
    )


def load_baseline() -> dict[str, Any]:
    if not BASELINE_PATH.is_file():
        raise AssertionError(
            f"{BASELINE_PATH}: baseline 파일이 없다 — `python tests/check_rescore_baseline.py --write-baseline`으로 생성"
        )
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


def write_baseline(failures: dict[str, Any]) -> None:
    BASELINE_PATH.write_text(serialize_failures(failures), encoding="utf-8")


def _inventory_ids(inventory: dict[str, list[str]], corpus: str) -> set[str]:
    value = inventory.get(corpus, [])
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise AssertionError(f"{corpus}: inventory must be a list of prompt ids")
    return set(value)


def classify_diffs(
    actual: dict[str, Any],
    baseline: dict[str, Any],
) -> tuple[
    dict[str, dict[str, list[str]]],
    dict[str, dict[str, list[str]]],
    dict[str, Any] | None,
]:
    """(완화, 조임, inventory 변화)를 돌려준다.

    완화 = baseline 실패가 실제에서 사라짐, 조임 = baseline 통과가 실제에서 실패.
    메시지 단위로 대조한다 — 같은 prompt의 일부 실패만 사라져도 완화로 잡힌다.
    inventory는 양쪽이 구형 실패 맵이면 None이다. 한쪽만 inventory가 없으면
    `undeclared`이고, 둘 다 있으면 missing/added id를 돌려준다. 빠지거나
    추가된 id는 메시지 diff와 별도다.
    """
    actual_failures, actual_inventory = split_snapshot(actual)
    baseline_failures, baseline_inventory = split_snapshot(baseline)
    relaxed: dict[str, dict[str, list[str]]] = {}
    tightened: dict[str, dict[str, list[str]]] = {}
    for corpus in sorted(set(actual_failures) | set(baseline_failures)):
        actual_prompts = actual_failures.get(corpus, {})
        baseline_prompts = baseline_failures.get(corpus, {})
        for prompt_id in sorted(set(actual_prompts) | set(baseline_prompts)):
            actual_messages = set(actual_prompts.get(prompt_id, []))
            baseline_messages = set(baseline_prompts.get(prompt_id, []))
            lost = sorted(baseline_messages - actual_messages)
            gained = sorted(actual_messages - baseline_messages)
            if lost:
                relaxed.setdefault(corpus, {})[prompt_id] = lost
            if gained:
                tightened.setdefault(corpus, {})[prompt_id] = gained
    if actual_inventory is None and baseline_inventory is None:
        return relaxed, tightened, None
    if actual_inventory is None or baseline_inventory is None:
        return relaxed, tightened, {"undeclared": True, "missing": {}, "added": {}}
    missing: dict[str, list[str]] = {}
    added: dict[str, list[str]] = {}
    for corpus in sorted(set(actual_inventory) | set(baseline_inventory)):
        lost_ids = sorted(
            _inventory_ids(baseline_inventory, corpus) - _inventory_ids(actual_inventory, corpus)
        )
        gained_ids = sorted(
            _inventory_ids(actual_inventory, corpus) - _inventory_ids(baseline_inventory, corpus)
        )
        if lost_ids:
            missing[corpus] = lost_ids
        if gained_ids:
            added[corpus] = gained_ids
    return relaxed, tightened, {"undeclared": False, "missing": missing, "added": added}


def _message_count(diffs: dict[str, dict[str, list[str]]]) -> int:
    return sum(
        len(messages)
        for prompt_messages in diffs.values()
        for messages in prompt_messages.values()
    )


def _append_inventory_lines(lines: list[str], inventory: dict[str, Any]) -> None:
    """id 추가·누락은 내용 판정과 따로 적는다. 완화/조임 라벨을 쓰지 않는다."""
    if inventory.get("undeclared"):
        lines.append(
            "입력 inventory가 없다 — 통과 입력 누락을 검사할 수 없다. "
            "`--write-baseline`으로 schema 2 스냅샷에 입력 집합을 선언한다. "
            "이 불일치는 스코어러 완화나 모델 실패가 아니다."
        )
        return
    for corpus in sorted(set(inventory["missing"]) | set(inventory["added"])):
        missing = inventory["missing"].get(corpus, [])
        added = inventory["added"].get(corpus, [])
        if missing:
            lines.append(
                f"[입력 누락] {corpus} — capture에 있던 입력 {len(missing)}건이 없다"
            )
            lines.extend(f"    - {prompt_id}" for prompt_id in missing)
            lines.append(
                "    ← 출력 항목이 빠졌다. 모델 실패나 스코어러 완화로 세지 않는다."
            )
        if added:
            lines.append(
                f"[입력 추가] {corpus} — baseline에 없던 입력 {len(added)}건"
            )
            lines.extend(f"    - {prompt_id}" for prompt_id in added)
            lines.append(
                "    ← 부분 capture에 현재 config 전체를 강제하지 않는다. "
                "추가된 입력만 선언한다."
            )


def build_report(
    actual: dict[str, Any],
    baseline: dict[str, Any],
) -> tuple[str, int]:
    """(리포트 텍스트, exit code) — exit 1이면 판정 또는 입력 집합이 바뀌었다.

    완화는 조임보다 강한 문구로 경고한다 — 이 레포의 사고는 완화 쪽에서 났다 (#282).
    입력 누락·추가는 그 판정과 별도 라벨이다.
    """
    actual_failures, actual_inventory = split_snapshot(actual)
    relaxed, tightened, inventory = classify_diffs(actual, baseline)
    inventory_clean = inventory is None or (
        not inventory.get("undeclared")
        and not inventory.get("missing")
        and not inventory.get("added")
    )
    if not relaxed and not tightened and inventory_clean:
        total_failures = sum(
            len(messages)
            for prompt_messages in actual_failures.values()
            for messages in prompt_messages.values()
        )
        input_note = ""
        if actual_inventory is not None:
            input_count = sum(len(prompt_ids) for prompt_ids in actual_inventory.values())
            input_note = f", 입력 {input_count}건"
        return (
            f"PASS: 판정 변화 0건 — baseline과 일치 "
            f"(corpus {len(actual_failures)}, 실패/검토대기 메시지 {total_failures}건"
            f"{input_note})",
            0,
        )

    relaxed_count = _message_count(relaxed)
    tightened_count = _message_count(tightened)
    total_count = relaxed_count + tightened_count
    summary = []
    if relaxed or tightened:
        summary.append(
            f"판정 변화 {total_count}건 (제거 {relaxed_count}건, 추가 {tightened_count}건)"
        )
    if inventory and inventory.get("undeclared"):
        summary.append("입력 inventory 미선언")
    elif inventory:
        missing_count = sum(len(prompt_ids) for prompt_ids in inventory["missing"].values())
        added_count = sum(len(prompt_ids) for prompt_ids in inventory["added"].values())
        if missing_count or added_count:
            summary.append(
                f"입력 집합 변화 (누락 {missing_count}건, 추가 {added_count}건)"
            )
    lines = [
        f"FAIL: {'; '.join(summary)} — "
        "baseline 갱신 없이는 이 게이트가 막는다. 스코어러/하네스 판정 로직을 "
        "건드렸으면 `--write-baseline`으로 baseline을 함께 갱신하고 PR 본문에 "
        "baseline diff를 붙인다."
    ]
    if inventory is not None:
        _append_inventory_lines(lines, inventory)
    if any("REVIEW_REQUIRED:" in message for group in tightened.values() for messages in group.values() for message in messages):
        lines.append("REVIEW_REQUIRED 증가는 의미 검토 수신처의 미검토 범위이며 모델 실패/위반 탐지로 세지 않는다.")
    for corpus in sorted(set(relaxed) | set(tightened)):
        for prompt_id in sorted(
            set(relaxed.get(corpus, {})) | set(tightened.get(corpus, {}))
        ):
            if prompt_id in relaxed.get(corpus, {}):
                removed = relaxed[corpus][prompt_id]
                pending = [m for m in removed if m.startswith(("REVIEW_REQUIRED:", "UNSCORABLE:"))]
                messages = [m for m in removed if m not in pending]
                if pending:
                    lines.append(f"[검토/채점 상태 변경] {corpus} / {prompt_id} — 미검토/채점불가 {len(pending)}건 제거")
                    lines.extend(f"    - {message}" for message in pending)
                    lines.append("    ← 검토/실행 증거 또는 수신처 변경을 확인한다. 메시지 제거만으로 검토 완료나 모델 개선을 추론하지 않는다.")
                if messages:
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
                pending_only = all(message.startswith(("REVIEW_REQUIRED:", "UNSCORABLE:")) for message in messages)
                label = "미검토/채점불가" if pending_only else "조임"
                lines.append(
                    f"[{label}] {corpus} / {prompt_id} — 새 판정 {len(messages)}건"
                )
                for message in messages:
                    lines.append(f"    - {message}")
                lines.append(
                    "    → 검토 또는 실행 증거가 필요하다. 위반 탐지나 모델 실패가 아니다."
                    if pending_only else
                    "    → 억제가 강해졌다 (조임). 의도된 변경이면 baseline 갱신으로 선언하고, 아니면 되돌린다."
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
        failures, listed = split_snapshot(actual)
        changed = sum(
            len(messages)
            for prompt_messages in failures.values()
            for messages in prompt_messages.values()
        )
        inputs = sum(len(prompt_ids) for prompt_ids in (listed or {}).values())
        print(
            f"baseline 갱신: {BASELINE_PATH} "
            f"(corpus {len(failures)}, 판정/검토대기 메시지 {changed}건, 입력 {inputs}건)"
        )
        return 0

    baseline = load_baseline()
    report, exit_code = build_report(actual, baseline)
    sys.stdout.write(report)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
