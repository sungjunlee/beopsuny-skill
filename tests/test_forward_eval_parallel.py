"""Same RUN_DIR cannot mix two parallel-eval publications (#377)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import forward_eval_harness as harness

PROMPT_IDS = (
    "fwd-02-law-change-automation-request",
    "fwd-03-business-user-external-reply",
)
DRIVER = harness.ROOT / "tests/forward_evals/run_live_parallel.sh"


def write_stub(path: Path) -> None:
    path.write_text(
        "#!/bin/sh\n"
        'printf "%s %s\\n" "$BEOPSUNY_EVAL_MODEL" "$BEOPSUNY_EVAL_PROMPT_ID" '
        '> "$BEOPSUNY_EVAL_OUTPUT_FILE"\n',
        encoding="utf-8",
    )
    path.chmod(0o755)


def write_config(path: Path) -> None:
    full = harness.load_forward_eval(harness.ROOT / "tests/forward_evals/beopsuny_guardrails.yaml")
    selected = [prompt for prompt in full["prompts"] if prompt["id"] in PROMPT_IDS]
    if len(selected) != len(PROMPT_IDS):
        raise AssertionError(f"missing prompts: {selected!r}")
    path.write_text(
        yaml.safe_dump({**full, "prompts": selected}, allow_unicode=True),
        encoding="utf-8",
    )


def publication(run_dir: Path):
    evidence_path = run_dir / "evidence.yaml"
    capture_path = run_dir / "capture.yaml"
    status_path = run_dir / "publish.json"
    if not (evidence_path.exists() and capture_path.exists() and status_path.exists()):
        return None
    return (
        json.loads(status_path.read_text(encoding="utf-8")),
        yaml.safe_load(capture_path.read_text(encoding="utf-8")),
        yaml.safe_load(evidence_path.read_text(encoding="utf-8")),
    )


class ParallelPublicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.config = self.root / "config.yaml"
        self.stub = self.root / "stub.sh"
        self.run_dir = self.root / "run"
        write_config(self.config)
        write_stub(self.stub)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def env(self, model: str, hook: Path | None = None, **extra: str) -> dict[str, str]:
        env = {
            **os.environ,
            "CONFIG": str(self.config),
            "RUN_DIR": str(self.run_dir),
            "RUNNER": str(self.stub),
            "PAR": "1",
            "MODEL": model,
        }
        if hook is not None:
            env["PYTHONPATH"] = str(hook)
        env.update(extra)
        return env

    def run_driver(self, model: str, hook: Path | None = None, **extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(DRIVER)],
            env=self.env(model, hook, **extra),
            capture_output=True,
            text=True,
        )

    def assert_one_run(self, model: str) -> None:
        published = publication(self.run_dir)
        self.assertIsNotNone(published, "published files are not a completed run")
        status, capture, evidence = published
        self.assertEqual(status["status"], "complete")
        self.assertEqual(status["run_id"], capture["run_id"])
        self.assertEqual(status["run_id"], evidence["run_id"])
        self.assertEqual(status["model"], model)
        self.assertEqual(capture["model"], model)
        self.assertEqual(evidence["model"], model)
        captured = {item["prompt_id"]: item for item in capture["prompts"]}
        scored = {item["prompt_id"]: item for item in evidence["results"]}
        self.assertEqual(sorted(status["prompt_ids"]), sorted(captured))
        self.assertEqual(set(scored), set(captured))
        for prompt_id, item in captured.items():
            text = (self.run_dir / "outputs" / f"{prompt_id}.txt").read_text(encoding="utf-8")
            self.assertEqual(text, item["output"])
            self.assertEqual(text, scored[prompt_id]["output"])
            self.assertTrue(text.startswith(model + " "), text)

    def test_partial_write_does_not_keep_previous_success(self) -> None:
        first = self.run_driver("model-old")
        if publication(self.run_dir) is None:
            self.fail(
                f"first run did not publish\nstdout={first.stdout}\nstderr={first.stderr}"
            )
        self.assert_one_run("model-old")
        previous_evidence = (self.run_dir / "evidence.yaml").read_text(encoding="utf-8")
        hook = self.root / "fail-hook"
        hook.mkdir()
        (hook / "sitecustomize.py").write_text(
            textwrap.dedent(
                """\
                from pathlib import Path
                _orig = Path.write_text
                _seen = {"n": 0}
                def _write(self, *args, **kwargs):
                    if self.suffix == ".txt" and "outputs" in self.parts:
                        _seen["n"] += 1
                        if _seen["n"] >= 2:
                            raise OSError("injected output write failure")
                    return _orig(self, *args, **kwargs)
                Path.write_text = _write
                """
            ),
            encoding="utf-8",
        )
        second = self.run_driver("model-new", hook)
        self.assertNotEqual(second.returncode, 0, second.stderr)
        self.assertIn("publish aborted", second.stderr)
        self.assertIsNone(publication(self.run_dir))
        self.assertFalse((self.run_dir / "evidence.yaml").exists())
        self.assertFalse((self.run_dir / "capture.yaml").exists())
        self.assertFalse((self.run_dir / "outputs").exists())
        self.assertNotIn("model-old", second.stdout)
        self.assertNotIn(previous_evidence, second.stdout)

    def test_overlapping_invocation_cannot_mix_published_files(self) -> None:
        barrier = self.root / "barrier"
        barrier.mkdir()
        hook = self.root / "race-hook"
        hook.mkdir()
        (hook / "sitecustomize.py").write_text(
            textwrap.dedent(
                """\
                import os
                import time
                from pathlib import Path
                _orig = Path.write_text
                def _write(self, *args, **kwargs):
                    result = _orig(self, *args, **kwargs)
                    if self.name == "capture.yaml" and os.environ.get("BEOPSUNY_EVAL_RACE_ROLE") == "A":
                        barrier = Path(os.environ["BEOPSUNY_EVAL_RACE_BARRIER"])
                        _orig(barrier / "a_capture", "1", encoding="utf-8")
                        release = barrier / "release_a"
                        for _ in range(200):
                            if release.exists():
                                return result
                            time.sleep(0.05)
                        raise TimeoutError("race barrier expired before release")
                    return result
                Path.write_text = _write
                """
            ),
            encoding="utf-8",
        )
        first = subprocess.Popen(
            ["bash", str(DRIVER)],
            env=self.env(
                "model-a",
                hook,
                BEOPSUNY_EVAL_RACE_ROLE="A",
                BEOPSUNY_EVAL_RACE_BARRIER=str(barrier),
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        appeared = False
        for _ in range(400):
            if (barrier / "a_capture").exists():
                appeared = True
                break
            if first.poll() is not None:
                break
            time.sleep(0.05)
        if not appeared:
            if first.poll() is None:
                first.kill()
            out, err = first.communicate()
            self.fail(f"capture barrier missing\nstdout={out}\nstderr={err}")
        second = self.run_driver("model-b", hook)
        (barrier / "release_a").write_text("1", encoding="utf-8")
        try:
            out, err = first.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            first.kill()
            out, err = first.communicate()
            self.fail(f"first invocation hung\nstdout={out}\nstderr={err}")
        self.assertNotEqual(second.returncode, 0, second.stderr)
        self.assertIn("RUN_DIR busy", second.stderr)
        if publication(self.run_dir) is None:
            self.fail(f"first run did not publish\nstdout={out}\nstderr={err}")
        self.assert_one_run("model-a")
        published_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (
                self.run_dir / "capture.yaml",
                self.run_dir / "evidence.yaml",
                self.run_dir / "publish.json",
            )
        )
        for prompt_id in PROMPT_IDS:
            published_text += (self.run_dir / "outputs" / f"{prompt_id}.txt").read_text(
                encoding="utf-8"
            )
        self.assertNotIn("model-b", published_text)
        self.assertEqual(first.returncode is not None or out or err, True)


if __name__ == "__main__":
    unittest.main()
