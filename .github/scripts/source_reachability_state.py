#!/usr/bin/env python3
"""Decide whether a source-reachability tracking issue can be closed.

The checker deliberately exits zero for both OK and WARN.  This helper keeps
the issue workflow from treating that process-level success as recovery: only
axes that previously failed (including an earlier retry attempt) matter, and
each of those axes must be explicitly OK in the final structured result.

State is embedded in comments made by github-actions.  Human-authored markers
are ignored so an issue comment cannot manufacture recovery state.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


STATE_VERSION = 1
STATE_PREFIX = "<!-- source-reachability-state:"
STATE_RE = re.compile(rf"{re.escape(STATE_PREFIX)}([A-Za-z0-9_-]+) -->")
TRUSTED_BOT_LOGINS = {"github-actions", "github-actions[bot]"}
VALID_STATUSES = {"OK", "WARN", "FAIL", "NOT_INSTALLED"}


def _ordered_unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))


def encode_state(*, complete: bool, failed_axes: list[str]) -> str:
    payload = {
        "version": STATE_VERSION,
        "complete": complete,
        "failed_axes": _ordered_unique(failed_axes),
    }
    raw = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    encoded = base64.urlsafe_b64encode(raw).decode().rstrip("=")
    return f"{STATE_PREFIX}{encoded} -->"


def _decode_state(encoded: str) -> dict[str, Any] | None:
    try:
        padding = "=" * (-len(encoded) % 4)
        state = json.loads(base64.urlsafe_b64decode(encoded + padding))
    except (binascii.Error, UnicodeDecodeError, ValueError, json.JSONDecodeError):
        return None
    if not isinstance(state, dict) or state.get("version") != STATE_VERSION:
        return None
    complete = state.get("complete")
    failed_axes = state.get("failed_axes")
    if not isinstance(complete, bool) or not isinstance(failed_axes, list):
        return None
    if not all(isinstance(axis, str) and axis for axis in failed_axes):
        return None
    return {
        "version": STATE_VERSION,
        "complete": complete,
        "failed_axes": _ordered_unique(failed_axes),
    }


def _login(entry: dict[str, Any]) -> str:
    author = entry.get("author")
    if not isinstance(author, dict):
        return ""
    login = author.get("login")
    return login if isinstance(login, str) else ""


def latest_trusted_state(history: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return the last valid marker authored by the workflow bot."""
    if not isinstance(history, dict):
        return None

    entries: list[dict[str, Any]] = [history]
    comments = history.get("comments")
    if isinstance(comments, list):
        entries.extend(comment for comment in comments if isinstance(comment, dict))

    latest = None
    for entry in entries:
        if _login(entry) not in TRUSTED_BOT_LOGINS:
            continue
        body = entry.get("body")
        if not isinstance(body, str):
            continue
        for match in STATE_RE.finditer(body):
            decoded = _decode_state(match.group(1))
            if decoded is not None:
                latest = decoded
    return latest


def _validated_attempt(payload: Any) -> list[dict[str, str]]:
    if not isinstance(payload, dict):
        raise ValueError("attempt result is not an object")
    if payload.get("result") not in {"OK", "WARN", "FAIL"}:
        raise ValueError("attempt result has no valid result")
    checks = payload.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ValueError("attempt result has no checks")

    validated = []
    seen = set()
    for check in checks:
        if not isinstance(check, dict):
            raise ValueError("check is not an object")
        axis = check.get("axis")
        status = check.get("status")
        if not isinstance(axis, str) or not axis or status not in VALID_STATUSES:
            raise ValueError("check has no valid axis/status")
        if axis in seen:
            raise ValueError(f"duplicate axis: {axis}")
        seen.add(axis)
        validated.append({"axis": axis, "status": status})
    return validated


def evaluate(
    attempts: list[Any],
    *,
    existing_issue: bool,
    issue_history: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a conservative issue action and the state for the next run."""
    prior_state = latest_trusted_state(issue_history) if existing_issue else None
    prior_axes = prior_state["failed_axes"] if prior_state else []
    state_complete = prior_state["complete"] if prior_state else not existing_issue

    try:
        validated = [_validated_attempt(attempt) for attempt in attempts]
        if not validated:
            raise ValueError("no attempt results")
    except ValueError as exc:
        marker = encode_state(complete=False, failed_axes=prior_axes)
        return {
            "action": "defer" if existing_issue else "none",
            "can_close": False,
            "reason": "invalid_structured_result",
            "reason_detail": str(exc),
            "attempt_count": len(attempts),
            "prior_state_found": prior_state is not None,
            "state_complete": False,
            "required_axes": [
                {"axis": axis, "status": "UNKNOWN"} for axis in prior_axes
            ],
            "recovered_axes": [],
            "unresolved_axes": prior_axes,
            "final_fail_axes": [],
            "state_marker": marker,
        }

    failed_in_attempts = _ordered_unique(
        check["axis"]
        for checks in validated
        for check in checks
        if check["status"] == "FAIL"
    )
    final_status = {check["axis"]: check["status"] for check in validated[-1]}
    final_fail_axes = [
        check["axis"] for check in validated[-1] if check["status"] == "FAIL"
    ]
    required = _ordered_unique([*prior_axes, *failed_in_attempts])
    required_statuses = [
        {"axis": axis, "status": final_status.get(axis, "MISSING")}
        for axis in required
    ]
    recovered = [
        item["axis"] for item in required_statuses if item["status"] == "OK"
    ]
    unresolved = [
        item["axis"] for item in required_statuses if item["status"] != "OK"
    ]
    tracked_axes = _ordered_unique([*unresolved, *final_fail_axes])

    if final_fail_axes:
        action = "failure"
        reason = "final_fail"
    elif not existing_issue:
        action = "none"
        reason = "no_tracking_issue"
    elif prior_state is None:
        action = "defer"
        reason = "missing_prior_state"
    elif not state_complete:
        action = "defer"
        reason = "incomplete_prior_state"
    elif unresolved:
        action = "defer"
        reason = "recovery_unconfirmed"
    elif not required:
        action = "defer"
        reason = "no_failed_axes"
    else:
        action = "recover"
        reason = "failed_axes_ok"

    marker = encode_state(complete=state_complete, failed_axes=tracked_axes)
    return {
        "action": action,
        "can_close": action == "recover",
        "reason": reason,
        "attempt_count": len(validated),
        "prior_state_found": prior_state is not None,
        "state_complete": state_complete,
        "required_axes": required_statuses,
        "recovered_axes": recovered,
        "unresolved_axes": unresolved,
        "final_fail_axes": final_fail_axes,
        "state_marker": marker,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", action="append", type=Path, default=[])
    parser.add_argument("--existing-issue", action="store_true")
    parser.add_argument("--issue-history", type=Path)
    return parser.parse_args(argv)


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    attempts = []
    invalid_error = None
    for path in args.result:
        try:
            attempts.append(_load_json(path))
        except (OSError, json.JSONDecodeError) as exc:
            invalid_error = f"{path}: {exc}"
            break

    history = None
    if args.issue_history:
        try:
            history = _load_json(args.issue_history)
        except (OSError, json.JSONDecodeError) as exc:
            invalid_error = f"{args.issue_history}: {exc}"

    if invalid_error:
        # Feed an invalid object through the same fail-safe path.  The detail is
        # only diagnostic; the emitted state is deliberately incomplete.
        attempts = [{"load_error": invalid_error}]

    decision = evaluate(
        attempts,
        existing_issue=args.existing_issue,
        issue_history=history,
    )
    if invalid_error:
        decision["reason_detail"] = invalid_error
    json.dump(decision, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
