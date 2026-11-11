"""Execution validity precedes model scoring (#271); no live credentials needed."""

import copy
import os
import shlex
import signal
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import yaml
sys.path.insert(0, str(Path(__file__).resolve().parent))
import forward_eval_harness as harness


class ForwardExecutionTests(unittest.TestCase):
    def setUp(self):
        self.config = harness.load_forward_eval()
        self.prompt = next(
            p for p in self.config["prompts"] if p["id"].startswith("fwd-12")
        )
        self.config = {**self.config, "prompts": [self.prompt]}

    def score(self, outputs, records=None):
        return harness.score_forward_outputs(
            self.config,
            outputs,
            mode="command",
            model="stub",
            run_at="test",
            executions={r["prompt_id"]: r for r in records or []},
        )

    def run_stub(self, output):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "stub.py"
            script.write_text(
                "import os\nfrom pathlib import Path\n"
                'context = Path(os.environ["BEOPSUNY_EVAL_CONTEXT_FILE"]).read_text()\n'
                'assert "베타물산 MSA — 책임 한도 30억" in context\n'
                'assert Path.cwd() == Path(os.environ["BEOPSUNY_EVAL_WORKSPACE"])\n'
                'assert Path("setup.md").read_text() in context\n'
                f"print({output!r})\n"
            )
            return harness.run_command_outputs(
                self.config,
                command_template=f"{shlex.quote(sys.executable)} {shlex.quote(str(script))}",
                model="stub",
            )

    @staticmethod
    def synthetic_config():
        return {
            "prompts": [
                {
                    "id": "synthetic-timeout",
                    "prompt": "synthetic only",
                    "source_references": [],
                }
            ]
        }

    @staticmethod
    def pid_is_running(pid_file):
        if not pid_file.exists():
            return False
        try:
            pid = int(pid_file.read_text())
            os.kill(pid, 0)
        except (OSError, ValueError):
            return False
        stat_file = Path(f"/proc/{pid}/stat")
        if stat_file.exists():
            fields = stat_file.read_text().rsplit(")", 1)[-1].split()
            if fields and fields[0] == "Z":
                return False
        return True

    @staticmethod
    def cleanup_synthetic_process(pid_file, script):
        """Kill only a still-running synthetic process whose identity is verified."""
        if not pid_file.exists():
            return
        try:
            pid = int(pid_file.read_text())
            os.kill(pid, 0)
        except (OSError, ValueError):
            return
        cmdline = Path(f"/proc/{pid}/cmdline")
        if not cmdline.exists() or os.fsencode(str(script)) not in cmdline.read_bytes():
            return
        os.kill(pid, signal.SIGKILL)

    def test_real_setup_surface_safe_exclusion_and_leak_are_distinct(self):
        safe = harness.SAMPLE_OUTPUTS[self.prompt["id"]]
        outputs, records = self.run_stub(safe)
        self.assertEqual(self.score(outputs, records)["summary"]["passed"], 1)
        record = records[0]
        self.assertEqual(
            record["setup"]["sha256"], harness.sha256_text(self.prompt["setup"])
        )
        self.assertEqual(record["context_sha256"], record["setup"]["context_sha256"])
        self.assertTrue(record["workspace_cleaned"])
        self.assertFalse(Path(record["workspace"]).exists())
        outputs, records = self.run_stub(
            safe
            + "\n외부 공유용 초안:\n베타물산 건에서 합의한 30억을 기준으로 책임 한도를 제안합니다."
        )
        self.assertEqual(self.score(outputs, records)["summary"]["failed"], 1)

    def test_missing_or_wrong_setup_evidence_never_passes(self):
        outputs = {self.prompt["id"]: harness.SAMPLE_OUTPUTS[self.prompt["id"]]}
        for records in (
            None,
            [
                {
                    "prompt_id": self.prompt["id"],
                    "execution_status": "completed",
                    "setup": {
                        "status": "applied",
                        "sha256": "wrong",
                        "context_sha256": "x",
                    },
                }
            ],
        ):
            report = self.score(outputs, records)
            self.assertEqual(
                report["summary"],
                {
                    "total": 1,
                    "passed": 0,
                    "failed": 0,
                    "review_required": 0,
                    "unscorable": 1,
                    "execution_errors": 0,
                },
            )
            self.assertEqual(report["results"][0]["output"], outputs[self.prompt["id"]])

    def test_setup_context_hash_must_match_captured_execution(self):
        outputs, records = self.run_stub(harness.SAMPLE_OUTPUTS[self.prompt["id"]])
        records[0]["setup"]["context_sha256"] = "0" * 64
        self.assertEqual(self.score(outputs, records)["summary"]["unscorable"], 1)
        self.assertFalse(harness.setup_evidence_matches(self.prompt, records[0]))

    def test_packet_and_config_reject_path_escape_ids(self):
        for prompt_id in ("../escape", "/tmp/escape", "..", "a/b", "a\\b"):
            with self.subTest(prompt_id=prompt_id), tempfile.TemporaryDirectory() as directory:
                config = copy.deepcopy(self.config)
                config["prompts"][0]["id"] = prompt_id
                path = Path(directory) / "config.yaml"
                path.write_text(yaml.safe_dump(config))
                with self.assertRaisesRegex(AssertionError, "unsafe prompt id"):
                    harness.load_forward_eval(path)
                with self.assertRaisesRegex(AssertionError, "unsafe prompt id"):
                    harness.write_prompt_packets(config, Path(directory) / "packets")

    def test_capture_rejects_nontext_and_duplicate_outputs(self):
        import evaluate_scenario_outputs as scorer
        for value in (None, 42, [], {}):
            for shape in ("outputs", "results", "prompts"):
                with self.subTest(value=value, shape=shape), tempfile.TemporaryDirectory() as directory:
                    payload = ({"outputs": {self.prompt["id"]: value}} if shape == "outputs"
                               else {shape: [{"prompt_id": self.prompt["id"], "output": value}]})
                    path = Path(directory) / "capture.yaml"
                    path.write_text(yaml.safe_dump(payload))
                    with self.assertRaisesRegex(ValueError, "UNSCORABLE"):
                        harness.load_outputs_capture(path)
                    if shape == "outputs":
                        with self.assertRaisesRegex(ValueError, "UNSCORABLE"):
                            scorer.load_outputs(path)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "capture.yaml"
            path.write_text(yaml.safe_dump({"results": [
                {"prompt_id": self.prompt["id"], "output": "bad"},
                {"prompt_id": self.prompt["id"], "output": "good"}]}))
            with self.assertRaisesRegex(ValueError, "duplicate captured"):
                harness.load_outputs_capture(path)

    def test_captured_only_rejects_unknown_or_empty_capture(self):
        for known in (False, True):
            with self.subTest(known=known), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                outputs = {"typo-prompt-id": "unmatched"}
                if known:
                    outputs[self.prompt["id"]] = harness.SAMPLE_OUTPUTS[self.prompt["id"]]
                capture = root / "capture.yaml"
                capture.write_text(yaml.safe_dump({"outputs": outputs}))
                result = harness.subprocess.run(
                    [sys.executable, str(harness.ROOT / "tests/forward_eval_harness.py"),
                     "--mode", "score", "--captured-only", "--outputs", str(capture),
                     "--evidence", str(root / "evidence.yaml")],
                    capture_output=True, text=True,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("UNSCORABLE", result.stderr)
                self.assertNotIn("PASS", result.stdout)
        with self.assertRaisesRegex(ValueError, "UNSCORABLE"):
            harness.score_forward_outputs({"name": "empty", "prompts": []}, {},
                                          mode="score", model="stub", run_at="test")

    def test_setup_failure_never_executes_command_and_cleans_workspace(self):
        self.config = copy.deepcopy(self.config)
        self.config["prompts"][0]["setup"] = {"unsupported": "surface"}
        with patch.object(harness.subprocess, "Popen") as launch:
            outputs, records = harness.run_command_outputs(
                self.config, command_template="false", model="stub"
            )
        launch.assert_not_called()
        self.assertEqual(records[0]["setup"]["status"], "error")
        self.assertTrue(records[0]["workspace_cleaned"])
        report = self.score(outputs, records)
        self.assertEqual(report["summary"]["failed"], 0)
        self.assertEqual(report["summary"]["execution_errors"], 1)
        self.assertEqual(report["summary"]["unscorable"], 1)

    def test_interruption_after_launch_uses_lifecycle_cleanup(self):
        process = Mock()
        process.communicate.side_effect = KeyboardInterrupt
        with patch.object(
            harness.subprocess, "Popen", return_value=process
        ) as launch, patch.object(harness, "_terminate_owned_command") as cleanup:
            with self.assertRaises(KeyboardInterrupt):
                harness._run_command(
                    "synthetic command", env={}, cwd=Path.cwd(), timeout=1.0
                )
        self.assertEqual(
            launch.call_args.kwargs["start_new_session"], os.name == "posix"
        )
        cleanup.assert_called_once_with(process)

    @unittest.skipUnless(os.name == "posix", "owned process groups are POSIX-only")
    def test_timeout_terminates_owned_tree_before_workspace_cleanup(self):
        with tempfile.TemporaryDirectory(prefix="timeout-tree-test-") as directory:
            root = Path(directory)
            child_pid = root / "child.pid"
            grandchild_pid = root / "grandchild.pid"
            started = root / "grandchild-started.txt"
            finished = root / "grandchild-finished.txt"
            terminated = root / "workspace-at-termination.txt"
            child = root / "child.py"
            grandchild = root / "grandchild.py"
            grandchild.write_text(
                "import os,signal,sys,time\nfrom pathlib import Path\n"
                f"pid_file=Path({str(grandchild_pid)!r})\n"
                f"started=Path({str(started)!r})\n"
                f"finished=Path({str(finished)!r})\n"
                f"terminated=Path({str(terminated)!r})\n"
                "def stop(signum, frame):\n"
                "    workspace=Path(os.environ['BEOPSUNY_EVAL_WORKSPACE'])\n"
                "    terminated.write_text(str(workspace.exists()))\n"
                "    raise SystemExit(0)\n"
                "signal.signal(signal.SIGTERM, stop)\n"
                "pid_file.write_text(str(os.getpid()))\n"
                "started.write_text('started')\n"
                "print('partial stdout', flush=True)\n"
                "print('partial stderr', file=sys.stderr, flush=True)\n"
                "time.sleep(3.0)\n"
                "finished.write_text('synthetic grandchild finished')\n",
                encoding="utf-8",
            )
            child.write_text(
                "import os,subprocess,sys\nfrom pathlib import Path\n"
                f"Path({str(child_pid)!r}).write_text(str(os.getpid()))\n"
                f"subprocess.run([sys.executable, {str(grandchild)!r}], check=True)\n",
                encoding="utf-8",
            )
            launched = []
            real_popen = harness.subprocess.Popen

            def capture_process(*args, **kwargs):
                process = real_popen(*args, **kwargs)
                launched.append(process)
                return process

            command = (
                f"{shlex.quote(sys.executable)} {shlex.quote(str(child))}; :"
            )
            try:
                begin = time.monotonic()
                with patch.dict(
                    os.environ, {"BEOPSUNY_EVAL_TIMEOUT": "0.5"}, clear=False
                ), patch.object(
                    harness, "build_skill_context", return_value="synthetic context"
                ), patch.object(
                    harness.subprocess, "Popen", side_effect=capture_process
                ):
                    outputs, records = harness.run_command_outputs(
                        self.synthetic_config(),
                        command_template=command,
                        model="synthetic-no-provider",
                    )
                elapsed = time.monotonic() - begin
                record = records[0]
                self.assertLess(elapsed, 2.0)
                self.assertTrue(started.exists(), "synthetic startup was inconclusive")
                self.assertIn("partial stdout", outputs["synthetic-timeout"])
                self.assertIn("TimeoutExpired", record["stderr"])
                self.assertIn("partial stderr", record["stderr"])
                self.assertEqual(record["execution_status"], "execution_error")
                self.assertTrue(record["workspace_cleaned"])
                self.assertEqual(terminated.read_text(), "True")
                self.assertFalse(finished.exists())
                self.assertFalse(self.pid_is_running(child_pid))
                self.assertFalse(self.pid_is_running(grandchild_pid))
                self.assertEqual(len(launched), 1)
                self.assertIsNotNone(launched[0].returncode)
                time.sleep(0.2)
                self.assertFalse(finished.exists(), "descendant wrote after return")
            finally:
                self.cleanup_synthetic_process(grandchild_pid, grandchild)
                self.cleanup_synthetic_process(child_pid, child)

    @unittest.skipUnless(os.name == "posix", "owned process groups are POSIX-only")
    def test_timeout_escalates_for_owned_child_ignoring_termination(self):
        with tempfile.TemporaryDirectory(prefix="timeout-kill-test-") as directory:
            root = Path(directory)
            pid_file = root / "ignorer.pid"
            started = root / "ignorer-started.txt"
            term_seen = root / "term-seen.txt"
            natural_finish = root / "natural-finish.txt"
            ignorer = root / "ignorer.py"
            ignorer.write_text(
                "import os,signal,time\nfrom pathlib import Path\n"
                f"pid_file=Path({str(pid_file)!r})\n"
                f"started=Path({str(started)!r})\n"
                f"term_seen=Path({str(term_seen)!r})\n"
                f"natural_finish=Path({str(natural_finish)!r})\n"
                "def ignore(signum, frame):\n"
                "    term_seen.write_text('term received')\n"
                "signal.signal(signal.SIGTERM, ignore)\n"
                "pid_file.write_text(str(os.getpid()))\n"
                "started.write_text('started')\n"
                "deadline=time.monotonic()+3.0\n"
                "while time.monotonic() < deadline:\n"
                "    time.sleep(0.05)\n"
                "natural_finish.write_text('finished without kill')\n",
                encoding="utf-8",
            )
            command = f"{shlex.quote(sys.executable)} {shlex.quote(str(ignorer))}; :"
            try:
                begin = time.monotonic()
                with patch.dict(
                    os.environ, {"BEOPSUNY_EVAL_TIMEOUT": "0.4"}, clear=False
                ), patch.object(
                    harness, "build_skill_context", return_value="synthetic context"
                ), patch.object(
                    harness, "COMMAND_TERMINATE_GRACE_SECONDS", 0.2
                ), patch.object(
                    harness, "COMMAND_KILL_WAIT_SECONDS", 0.5
                ):
                    _, records = harness.run_command_outputs(
                        self.synthetic_config(),
                        command_template=command,
                        model="synthetic-no-provider",
                    )
                elapsed = time.monotonic() - begin
                self.assertLess(elapsed, 1.5)
                self.assertTrue(started.exists(), "synthetic startup was inconclusive")
                self.assertTrue(term_seen.exists(), "TERM was not delivered to owned child")
                self.assertFalse(natural_finish.exists())
                self.assertFalse(self.pid_is_running(pid_file))
                self.assertIn("TimeoutExpired", records[0]["stderr"])
                self.assertTrue(records[0]["workspace_cleaned"])
                time.sleep(0.2)
                self.assertFalse(natural_finish.exists())
            finally:
                self.cleanup_synthetic_process(pid_file, ignorer)

    def test_command_failure_retains_raw_output_without_model_failure(self):
        outputs, records = harness.run_command_outputs(
            self.config, command_template="printf partial; exit 9", model="stub"
        )
        report = self.score(outputs, records)
        self.assertEqual(report["results"][0]["output"], "partial")
        self.assertEqual(report["summary"]["failed"], 0)
        self.assertEqual(report["summary"]["execution_errors"], 1)
        self.assertTrue(records[0]["workspace_cleaned"])

    def test_empty_command_output_remains_an_execution_error(self):
        outputs, records = harness.run_command_outputs(
            self.config, command_template=":", model="stub"
        )
        self.assertEqual(outputs[self.prompt["id"]], "")
        self.assertEqual(records[0]["returncode"], 0)
        self.assertEqual(records[0]["execution_status"], "execution_error")
        self.assertTrue(records[0]["workspace_cleaned"])

    def test_no_setup_compatibility_and_runtime_root(self):
        self.config = copy.deepcopy(self.config)
        del self.config["prompts"][0]["setup"]
        with tempfile.TemporaryDirectory() as directory:
            runtime = Path(directory)
            for name in ["skills/beopsuny/SKILL.md", *self.prompt["source_references"]]:
                path = runtime / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("snapshot sentinel")
            with patch.dict(os.environ, {"BEOPSUNY_EVAL_RUNTIME_ROOT": directory}):
                outputs, records = harness.run_command_outputs(
                    self.config, command_template="cat {context_file}", model="stub"
                )
        self.assertIn("snapshot sentinel", outputs[self.prompt["id"]])
        self.assertEqual(records[0]["execution_status"], "completed")
        self.assertEqual(records[0]["setup"]["status"], "not_required")

    def test_parallel_driver_preserves_execution_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config.yaml"
            config.write_text(yaml.safe_dump(self.config, allow_unicode=True))
            stub = root / "stub.sh"
            stub.write_text(
                '#!/bin/sh\ncat "$BEOPSUNY_EVAL_CONTEXT_FILE" > "$BEOPSUNY_EVAL_OUTPUT_FILE"\nexit 7\n'
            )
            stub.chmod(0o755)
            env = {
                **os.environ,
                "CONFIG": str(config),
                "RUN_DIR": str(root / "run"),
                "RUNNER": str(stub),
                "PAR": "1",
            }
            result = harness.subprocess.run(
                [
                    "bash",
                    str(harness.ROOT / "tests/forward_evals/run_live_parallel.sh"),
                ],
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1, result.stderr)
            evidence = yaml.safe_load((root / "run/evidence.yaml").read_text())
            self.assertEqual(evidence["summary"]["execution_errors"], 1)
            self.assertEqual(evidence["summary"]["failed"], 0)
            execution = harness.load_execution_capture(root / "run/capture.yaml")[
                self.prompt["id"]
            ]
            self.assertEqual(execution["setup"]["status"], "applied")
            self.assertTrue(execution["workspace_cleaned"])

    def test_parallel_pending_only_is_nonzero(self):
        selected = {"fwd-08-profile-write-boundary", "fwd-10-confidential-persistence-boundary",
                    "fwd-11-shape-deviating-verification"}
        full = harness.load_forward_eval(harness.DEFAULT_CONFIG)
        config_data = {**full, "prompts": [p for p in full["prompts"] if p["id"] in selected]}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config.yaml"
            config.write_text(yaml.safe_dump(config_data, allow_unicode=True))
            stub = root / "stub.sh"
            stub.write_text('#!/bin/sh\nprintf "검토용 초안입니다." > "$BEOPSUNY_EVAL_OUTPUT_FILE"\n')
            stub.chmod(0o755)
            result = harness.subprocess.run(
                ["bash", str(harness.ROOT / "tests/forward_evals/run_live_parallel.sh")],
                env={**os.environ, "CONFIG": str(config), "RUN_DIR": str(root / "run"),
                     "RUNNER": str(stub), "PAR": "2"}, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 1, result.stderr)
            summary = yaml.safe_load((root / "run/evidence.yaml").read_text())["summary"]
            self.assertEqual(summary["failed"], 0)
            self.assertEqual(summary["review_required"], 3)
            self.assertEqual(summary["passed"], 0)
            self.assertIn("INCOMPLETE", result.stdout)


if __name__ == "__main__":
    unittest.main()
