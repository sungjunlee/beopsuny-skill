#!/usr/bin/env python3
"""Synthetic recovery boundaries for the source-reachability workflow."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / ".github" / "scripts" / "source_reachability_state.py"
SPEC = importlib.util.spec_from_file_location("source_reachability_state", MODULE_PATH)
assert SPEC and SPEC.loader
state = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = state
SPEC.loader.exec_module(state)


def result(*checks: tuple[str, str]) -> dict[str, object]:
    statuses = [status for _axis, status in checks]
    overall = "FAIL" if "FAIL" in statuses else "WARN" if "WARN" in statuses else "OK"
    return {
        "result": overall,
        "summary": f"RESULT: {overall}",
        "checks": [
            {"axis": axis, "status": status, "detail": "synthetic"}
            for axis, status in checks
        ],
    }


def bot_history(*, complete: bool = True, failed_axes: list[str]) -> dict[str, object]:
    return {
        "author": {"login": "github-actions"},
        "body": state.encode_state(complete=complete, failed_axes=failed_axes),
        "comments": [],
    }


class RecoveryDecisionTest(unittest.TestCase):
    def test_fail_then_warn_preserves_the_axis_and_defers_recovery(self) -> None:
        decision = state.evaluate(
            [result(("axis-a", "FAIL")), result(("axis-a", "WARN"))],
            existing_issue=True,
            issue_history=bot_history(failed_axes=["axis-a"]),
        )
        self.assertEqual("defer", decision["action"])
        self.assertEqual("recovery_unconfirmed", decision["reason"])
        self.assertEqual(["axis-a"], decision["unresolved_axes"])
        self.assertEqual(2, decision["attempt_count"])

        next_history = {
            "author": {"login": "github-actions"},
            "body": decision["state_marker"],
            "comments": [],
        }
        self.assertEqual(
            ["axis-a"], state.latest_trusted_state(next_history)["failed_axes"]
        )

    def test_fail_then_same_axis_ok_records_recovery(self) -> None:
        decision = state.evaluate(
            [
                result(("axis-a", "FAIL"), ("accepted-warning", "WARN")),
                result(("axis-a", "OK"), ("accepted-warning", "WARN")),
            ],
            existing_issue=True,
            issue_history=bot_history(failed_axes=["axis-a"]),
        )
        self.assertEqual("recover", decision["action"])
        self.assertTrue(decision["can_close"])
        self.assertEqual(["axis-a"], decision["recovered_axes"])

    def test_unrelated_warn_does_not_block_a_confirmed_axis(self) -> None:
        decision = state.evaluate(
            [result(("axis-a", "OK"), ("axis-b", "WARN"))],
            existing_issue=True,
            issue_history=bot_history(failed_axes=["axis-a"]),
        )
        self.assertEqual("recover", decision["action"])

    def test_existing_issue_without_state_is_not_closed(self) -> None:
        history = {
            "author": {"login": "github-actions"},
            "body": "old report without structured state",
            "comments": [],
        }
        decision = state.evaluate(
            [result(("axis-a", "OK"))],
            existing_issue=True,
            issue_history=history,
        )
        self.assertEqual("defer", decision["action"])
        self.assertEqual("missing_prior_state", decision["reason"])

    def test_no_issue_and_warn_does_not_manufacture_recovery(self) -> None:
        decision = state.evaluate(
            [result(("axis-a", "WARN"))],
            existing_issue=False,
        )
        self.assertEqual("none", decision["action"])
        self.assertFalse(decision["can_close"])

    def test_new_final_failure_gets_complete_tracking_state(self) -> None:
        decision = state.evaluate(
            [result(("axis-a", "FAIL"))],
            existing_issue=False,
        )
        self.assertEqual("failure", decision["action"])
        self.assertTrue(decision["state_complete"])

        history = {
            "author": {"login": "github-actions[bot]"},
            "body": decision["state_marker"],
            "comments": [],
        }
        self.assertEqual(
            ["axis-a"], state.latest_trusted_state(history)["failed_axes"]
        )

    def test_new_failure_keeps_a_previously_failed_deferred_axis(self) -> None:
        decision = state.evaluate(
            [result(("axis-a", "WARN"), ("axis-b", "FAIL"))],
            existing_issue=True,
            issue_history=bot_history(failed_axes=["axis-a"]),
        )
        self.assertEqual("failure", decision["action"])
        self.assertEqual(["axis-a", "axis-b"], decision["unresolved_axes"])

        history = {
            "author": {"login": "github-actions"},
            "body": decision["state_marker"],
            "comments": [],
        }
        self.assertEqual(
            ["axis-a", "axis-b"],
            state.latest_trusted_state(history)["failed_axes"],
        )

    def test_human_comment_cannot_replace_bot_state(self) -> None:
        history = bot_history(failed_axes=["axis-a"])
        history["comments"] = [
            {
                "author": {"login": "someone-else"},
                "body": state.encode_state(complete=True, failed_axes=["axis-b"]),
            }
        ]
        self.assertEqual(
            ["axis-a"], state.latest_trusted_state(history)["failed_axes"]
        )

    def test_invalid_retry_result_makes_state_incomplete(self) -> None:
        decision = state.evaluate(
            [result(("axis-a", "FAIL")), {"not": "checker JSON"}],
            existing_issue=True,
            issue_history=bot_history(failed_axes=["axis-a"]),
        )
        self.assertEqual("defer", decision["action"])
        self.assertEqual("invalid_structured_result", decision["reason"])
        self.assertFalse(decision["state_complete"])

    def test_cli_issue_bot_author_is_trusted_separately_from_comments(self) -> None:
        history = {
            "author": {"is_bot": True, "login": "app/github-actions"},
            "body": state.encode_state(complete=True, failed_axes=["axis-a"]),
            "comments": [],
        }
        decision = state.evaluate(
            [result(("axis-a", "OK"))],
            existing_issue=True,
            issue_history=history,
        )
        self.assertEqual("recover", decision["action"])
        self.assertTrue(decision["can_close"])
        self.assertEqual(
            ["axis-a"], state.latest_trusted_state(history)["failed_axes"]
        )

        comment_only = {
            "author": {"login": "someone-else"},
            "body": "human-opened issue without a bot marker",
            "comments": [
                {
                    "author": {"is_bot": True, "login": "app/github-actions"},
                    "body": state.encode_state(complete=True, failed_axes=["axis-a"]),
                }
            ],
        }
        decision = state.evaluate(
            [result(("axis-a", "OK"))],
            existing_issue=True,
            issue_history=comment_only,
        )
        self.assertEqual("recover", decision["action"])

    def test_partial_recovery_keeps_required_axes_until_close(self) -> None:
        initial = state.evaluate(
            [result(("axis-a", "FAIL"), ("axis-b", "FAIL"))],
            existing_issue=False,
        )
        self.assertEqual("failure", initial["action"])
        history = {
            "author": {"login": "github-actions"},
            "body": initial["state_marker"],
            "comments": [],
        }
        self.assertEqual(
            ["axis-a", "axis-b"],
            state.latest_trusted_state(history)["failed_axes"],
        )

        follow_up = state.evaluate(
            [result(("axis-a", "OK"), ("axis-b", "WARN"))],
            existing_issue=True,
            issue_history=history,
        )
        self.assertEqual("defer", follow_up["action"])
        self.assertEqual(["axis-b"], follow_up["unresolved_axes"])
        next_history = {
            "author": {"login": "github-actions"},
            "body": follow_up["state_marker"],
            "comments": [],
        }
        self.assertEqual(
            ["axis-a", "axis-b"],
            state.latest_trusted_state(next_history)["failed_axes"],
        )

        later = state.evaluate(
            [result(("axis-a", "WARN"), ("axis-b", "OK"))],
            existing_issue=True,
            issue_history=next_history,
        )
        self.assertEqual("defer", later["action"])
        self.assertFalse(later["can_close"])
        self.assertEqual(["axis-a"], later["unresolved_axes"])



if __name__ == "__main__":
    unittest.main()
