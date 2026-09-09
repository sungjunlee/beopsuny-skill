#!/usr/bin/env python3
"""Prepare isolated A/B/C knowledge-value model packets; never run or judge a model."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TESTS = ROOT / "tests"
sys.path.insert(0, str(TESTS))
import forward_eval_harness as harness  # noqa: E402


PREPARE_KNOWLEDGE = ROOT / "tests/forward_evals/model_era/prepare_knowledge.py"
EXPERIMENT = HERE / "experiment.json"
COMMON_REFERENCES = (
    "skills/beopsuny/references/source-access.md",
    "skills/beopsuny/references/citation-verification-contract.md",
    "skills/beopsuny/assets/policies/checklists/privacy_compliance.yaml",
    "skills/beopsuny/assets/data/clause_references.yaml",
)
KNOWLEDGE_INJECTION = "skills/beopsuny/references/knowledge-injection.md"
CANDIDATE_MEMO_DIRECTORY = "research/privacy/memos"
LEGACY_CANDIDATE_MEMO_DIRECTORY = "privacy/research/memos"
STAGED_SECTIONS = {
    "taxonomy": "taxonomy.txt",
    "retrieval_hints": "hints.txt",
    "authority_map.core": "audit-core.txt",
    "authority_map.overlay": "audit-overlay.txt",
}
FORBIDDEN_CANDIDATE_INPUT = re.compile(
    r"(?im)^#{1,6}\s*(?:candidate\s*metadata|metadata|hypothesis|hypotheses|examples?|"
    r"expected\s*answers?|answers?|rubric|후보\s*메타데이터|메타데이터|가설|예시|정답|채점)\b"
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def copy_runtime_file(runtime: Path, relative: str) -> Path:
    source = ROOT / relative
    if not source.is_file():
        raise FileNotFoundError(f"required runtime file is missing: {source}")
    target = runtime / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return target


def remove_markdown_section(text: str, heading: str) -> str:
    match = re.search(rf"(?m)^{re.escape(heading)}\s*$", text)
    if not match:
        raise ValueError(f"required markdown heading is missing: {heading}")
    following = re.search(r"(?m)^##\s+", text[match.end():])
    end = match.end() + following.start() if following else len(text)
    return text[:match.start()] + text[end:]


def build_arm_a_skill(skill: str) -> str:
    lines = []
    for line in skill.splitlines(keepends=True):
        if line.startswith("| `privacy_knowledge_layer`"):
            continue
        if line.startswith("1. Right-sizing"):
            line = line.replace("계약/체크리스트/지식 레이어", "계약/체크리스트")
            line = line.replace(" 개인정보 질문이라도 단순 조문 확인이면 `privacy_knowledge_layer`를 생략한다.", "")
            line = line.replace(" 지식 자산은 결론 근거가 아니라 회상/점검 보조다.", "")
        lines.append(line)
    transformed = remove_markdown_section(
        "".join(lines), "## 개인정보 보조 지식 레이어"
    )
    if "1. Right-sizing" not in transformed:
        raise ValueError("A must retain the common right-sizing rule")
    if "knowledge-injection.md" in transformed or "privacy_knowledge_layer" in transformed:
        raise ValueError("A variant still contains a knowledge-layer route or reference")
    return transformed


def build_arm_c_injection(reference: str) -> str:
    start = "Privacy 사전지식 — 기본 점검 축:"
    end = "## 채널"
    if start not in reference or end not in reference:
        raise ValueError("knowledge-injection boundary markers changed; cannot build C safely")
    before, rest = reference.split(start, 1)
    _, after = rest.split(end, 1)
    transformed = before.rstrip() + "\n\n" + end + after
    if start in transformed:
        raise ValueError("C variant still contains the embedded seven-axis summary")
    return transformed


def extract_evaluation_candidate(memo: Path) -> str:
    text = memo.read_text(encoding="utf-8")
    heading = re.search(r"(?m)^##\s+Evaluation Candidate\s*$", text)
    if not heading:
        raise ValueError(f"{memo} lacks the required ## Evaluation Candidate section")
    next_heading = re.search(r"(?m)^##\s+", text[heading.end():])
    end = heading.end() + next_heading.start() if next_heading else len(text)
    candidate = text[heading.end():end].strip()
    if not candidate:
        raise ValueError(f"{memo} has an empty Evaluation Candidate section")
    if FORBIDDEN_CANDIDATE_INPUT.search(candidate):
        raise ValueError(
            f"{memo} Evaluation Candidate contains evaluator-only material; do not inject it"
        )
    return candidate + "\n"


def discover_evaluation_candidate_memos(knowledge_root: Path) -> list[Path]:
    """Require the frozen snapshot to identify exactly the two C inputs."""
    directory = knowledge_root / CANDIDATE_MEMO_DIRECTORY
    # Historical frozen checkouts retain their original layout and input receipts.
    if not directory.is_dir():
        directory = knowledge_root / LEGACY_CANDIDATE_MEMO_DIRECTORY
    if not directory.is_dir():
        raise FileNotFoundError(f"candidate memo directory is missing: {directory}")
    candidates = [
        path
        for path in sorted(directory.glob("*.md"))
        if re.search(r"(?m)^##\s+Evaluation Candidate\s*$", path.read_text(encoding="utf-8"))
    ]
    if len(candidates) != 2:
        raise ValueError(
            "C requires exactly two frozen memos with ## Evaluation Candidate; "
            f"found {len(candidates)} in {directory}"
        )
    return candidates


def load_source_bundle(bundle: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest_path = bundle / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"source bundle manifest is required: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("access_mode") != "fixed":
        raise ValueError("this preparer accepts only a fixed source bundle; live access is not prepared")
    sources = manifest.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("source bundle manifest requires a non-empty sources list")

    receipts: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("each source bundle entry must be an object")
        source_id = str(source.get("id", ""))
        filename = str(source.get("file", ""))
        expected = str(source.get("sha256", ""))
        if not source_id or source_id in seen_ids or not filename or not expected:
            raise ValueError("source bundle entries require unique id, file, and sha256")
        relative = Path(filename)
        if relative.is_absolute() or ".." in relative.parts or relative.suffix != ".md":
            raise ValueError(f"source bundle file must be a relative .md path: {filename}")
        path = bundle / relative
        if not path.is_file():
            raise FileNotFoundError(f"source bundle file is missing: {path}")
        actual = sha256_file(path)
        if actual != expected:
            raise ValueError(f"source checksum mismatch: {filename}")
        seen_ids.add(source_id)
        receipts.append(
            {
                "id": source_id,
                "file": filename,
                "sha256": actual,
                "chars": len(path.read_text(encoding="utf-8")),
                "official_url": source.get("official_url"),
                "captured_at": source.get("captured_at"),
                "text": path.read_text(encoding="utf-8"),
            }
        )
    return manifest, receipts


def load_questions(questions_dir: Path) -> list[dict[str, str]]:
    files = sorted(questions_dir.glob("*.txt"))
    if len(files) != 2:
        raise ValueError("the initial smoke requires exactly two question .txt files")
    questions: list[dict[str, str]] = []
    seen: set[str] = set()
    for path in files:
        question_id = path.stem
        if not question_id or question_id in seen:
            raise ValueError(f"question ids must be unique non-empty file stems: {path}")
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            raise ValueError(f"question is empty: {path}")
        seen.add(question_id)
        questions.append({"id": question_id, "text": text, "sha256": sha256_file(path)})
    return questions


def fixed_source_prompt(receipts: list[dict[str, Any]]) -> str:
    parts = [
        "[Evaluation source condition]",
        "Use only the fixed source texts below for material legal claims. Do not use tools, local files, prior evaluations, or other sources. If the bundle does not establish a point, say so rather than inferring it. The source bundle is a captured text bundle; metadata does not mean a live official-site check.",
    ]
    for receipt in receipts:
        parts.extend(
            [
                "",
                f"## Fixed source: {receipt['id']}",
                receipt["text"].rstrip(),
            ]
        )
    return "\n".join(parts).rstrip() + "\n"


def git_value(*args: str) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        text=True,
        check=False,
        shell=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def prepare_loader_sections(
    knowledge_root: Path, output: Path, max_asset_chars: int
) -> tuple[Path, dict[str, Any]]:
    stage = output / "loader-stage" / "B"
    command = [
        sys.executable,
        str(PREPARE_KNOWLEDGE),
        "--knowledge-root",
        str(knowledge_root),
        "--output",
        str(stage),
        "--max-asset-chars",
        str(max_asset_chars),
    ]
    result = subprocess.run(
        command, capture_output=True, text=True, check=False, shell=False
    )
    metadata_path = stage.parent / f"{stage.name}-metadata.json"
    metadata = (
        json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata_path.is_file()
        else {"status": "missing_loader_metadata"}
    )
    if result.returncode != 0 or metadata.get("status") != "prepared_not_measured":
        raise RuntimeError(
            "S1 loader preparation failed; inspect loader-stage/B-metadata.json. "
            f"stdout={result.stdout.strip()!r} stderr={result.stderr.strip()!r}"
        )
    missing = [filename for filename in STAGED_SECTIONS.values() if not (stage / filename).is_file()]
    if missing:
        raise RuntimeError(f"S1 loader did not write required rendered sections: {missing}")
    return stage, metadata


def write_variant(
    arm: str,
    output: Path,
    baseline_skill: str,
    knowledge_root: Path,
    loader_stage: Path | None,
) -> tuple[Path, list[str], dict[str, Any]]:
    runtime = output / "variants" / arm
    for relative in COMMON_REFERENCES:
        copy_runtime_file(runtime, relative)

    skill_path = ROOT / "skills/beopsuny/SKILL.md"
    skill = baseline_skill if arm != "A" else build_arm_a_skill(baseline_skill)
    target_skill = runtime / "skills/beopsuny/SKILL.md"
    target_skill.parent.mkdir(parents=True, exist_ok=True)
    target_skill.write_text(skill, encoding="utf-8")

    extra_references: list[str] = []
    candidate_receipts: list[dict[str, str]] = []
    if arm == "B":
        injection_target = copy_runtime_file(runtime, KNOWLEDGE_INJECTION)
        extra_references.append(KNOWLEDGE_INJECTION)
        assert loader_stage is not None
        for key, filename in STAGED_SECTIONS.items():
            source = loader_stage / filename
            relative = f"skills/beopsuny/references/rendered-knowledge/{filename}"
            target = runtime / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            extra_references.append(relative)
    elif arm == "C":
        injection = (ROOT / KNOWLEDGE_INJECTION).read_text(encoding="utf-8")
        injection_target = runtime / KNOWLEDGE_INJECTION
        injection_target.parent.mkdir(parents=True, exist_ok=True)
        injection_target.write_text(build_arm_c_injection(injection), encoding="utf-8")
        extra_references.append(KNOWLEDGE_INJECTION)
        for memo in discover_evaluation_candidate_memos(knowledge_root):
            target_relative = (
                "skills/beopsuny/references/evaluation-candidates/" + memo.name
            )
            target = runtime / target_relative
            target.parent.mkdir(parents=True, exist_ok=True)
            candidate = extract_evaluation_candidate(memo)
            target.write_text(candidate, encoding="utf-8")
            extra_references.append(target_relative)
            candidate_receipts.append(
                {
                    "memo": str(memo.relative_to(knowledge_root)),
                    "memo_sha256": sha256_file(memo),
                    "candidate_sha256": sha256_bytes(candidate.encode("utf-8")),
                }
            )

    diff = "".join(
        difflib.unified_diff(
            baseline_skill.splitlines(keepends=True),
            skill.splitlines(keepends=True),
            fromfile="baseline/skills/beopsuny/SKILL.md",
            tofile=f"variant-{arm}/skills/beopsuny/SKILL.md",
        )
    )
    diff_path = output / "evaluator-only" / "variant-diffs" / f"{arm}-SKILL.md.diff"
    diff_path.parent.mkdir(parents=True, exist_ok=True)
    diff_path.write_text(diff, encoding="utf-8")
    hashes = {
        str(path.relative_to(runtime)): sha256_file(path)
        for path in sorted(runtime.rglob("*"))
        if path.is_file()
    }
    return runtime, [*COMMON_REFERENCES, *extra_references], {
        "runtime_root": str(runtime),
        "runtime_files": hashes,
        "variant_sha256": sha256_bytes(
            "".join(f"{path}:{digest}\n" for path, digest in hashes.items()).encode("utf-8")
        ),
        "skill_sha256": sha256_file(target_skill),
        "skill_diff": str(diff_path),
        "skill_diff_sha256": sha256_file(diff_path),
        "candidate_receipts": candidate_receipts,
    }


def build_prompts(
    questions: list[dict[str, str]],
    source_text: str,
    references: list[str],
) -> list[dict[str, Any]]:
    prompts: list[dict[str, Any]] = []
    for question in questions:
        prompts.append(
            {
                "id": question["id"],
                "source_references": references,
                "prompt": question["text"] + "\n\n" + source_text,
            }
        )
    return prompts


def write_arm_packets(
    arm: str, runtime: Path, prompts: list[dict[str, Any]], output: Path
) -> list[dict[str, str]]:
    packet_dir = output / "model-inputs" / arm
    if packet_dir.exists():
        raise ValueError(f"refusing to overwrite model packets: {packet_dir}")
    prior_runtime = os.environ.get("BEOPSUNY_EVAL_RUNTIME_ROOT")
    os.environ["BEOPSUNY_EVAL_RUNTIME_ROOT"] = str(runtime)
    try:
        harness.write_prompt_packets({"prompts": prompts}, packet_dir)
    finally:
        if prior_runtime is None:
            os.environ.pop("BEOPSUNY_EVAL_RUNTIME_ROOT", None)
        else:
            os.environ["BEOPSUNY_EVAL_RUNTIME_ROOT"] = prior_runtime
    return [
        {
            "question_id": str(prompt["id"]),
            "context": str(packet_dir / str(prompt["id"]) / "context.md"),
            "context_sha256": sha256_file(packet_dir / str(prompt["id"]) / "context.md"),
            "prompt": str(packet_dir / str(prompt["id"]) / "prompt.txt"),
            "prompt_sha256": sha256_file(packet_dir / str(prompt["id"]) / "prompt.txt"),
        }
        for prompt in prompts
    ]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--knowledge-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-bundle", type=Path, required=True)
    parser.add_argument("--questions-dir", type=Path, required=True)
    parser.add_argument("--max-asset-chars", type=int, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.max_asset_chars < 1:
        raise ValueError("--max-asset-chars must be at least 1")
    knowledge_root = args.knowledge_root.resolve()
    output = args.output.resolve()
    source_bundle = args.source_bundle.resolve()
    questions_dir = args.questions_dir.resolve()
    if output.exists():
        raise ValueError(f"refusing to overwrite output: {output}")
    if not knowledge_root.is_dir() or not source_bundle.is_dir() or not questions_dir.is_dir():
        raise ValueError("--knowledge-root, --source-bundle, and --questions-dir must be directories")
    if not PREPARE_KNOWLEDGE.is_file():
        raise FileNotFoundError(f"S1 loader preparer is missing: {PREPARE_KNOWLEDGE}")

    experiment = json.loads(EXPERIMENT.read_text(encoding="utf-8"))
    questions = load_questions(questions_dir)
    source_manifest, source_receipts = load_source_bundle(source_bundle)
    output.mkdir(parents=True)
    loader_stage, loader_metadata = prepare_loader_sections(
        knowledge_root, output, args.max_asset_chars
    )
    baseline_skill = (ROOT / "skills/beopsuny/SKILL.md").read_text(encoding="utf-8")
    source_text = fixed_source_prompt(source_receipts)

    variants: dict[str, Any] = {}
    packets: dict[str, list[dict[str, str]]] = {}
    for arm in ("A", "B", "C"):
        runtime, references, variant = write_variant(
            arm, output, baseline_skill, knowledge_root, loader_stage
        )
        prompts = build_prompts(questions, source_text, references)
        variants[arm] = {**variant, "source_references": references}
        packets[arm] = write_arm_packets(arm, runtime, prompts, output)

    common_source_hashes = {receipt["id"]: receipt["sha256"] for receipt in source_receipts}
    cells = [
        {
            "cell_id": f"{question['id']}:{arm}:family-{family}",
            "question_id": question["id"],
            "arm": arm,
            "model_family_slot": family,
            "execution_status": "not_measured",
            "assessment": "not_measured",
            "legal_adjudication": "unadjudicated",
            "source_mode": "fixed",
            "live_performance_claim": False,
            "unavailable_reason": "preparation only; no model execution was requested",
        }
        for question in questions
        for arm in ("A", "B", "C")
        for family in (1, 2)
    ]
    metadata = {
        "status": "prepared_not_measured",
        "experiment": {
            "path": str(EXPERIMENT),
            "sha256": sha256_file(EXPERIMENT),
            "rubric": "tests/forward_evals/model_era/rubric.json (#320/#326)",
        },
        "runtime": {
            "root": str(ROOT),
            "git_commit": git_value("rev-parse", "HEAD"),
            "git_status_porcelain": git_value("status", "--porcelain"),
            "baseline_skill_sha256": sha256_file(ROOT / "skills/beopsuny/SKILL.md"),
            "harness_sha256": sha256_file(TESTS / "forward_eval_harness.py"),
        },
        "knowledge": {
            "root": str(knowledge_root),
            "max_asset_chars": args.max_asset_chars,
            "loader_stage": str(loader_stage),
            "loader_metadata": loader_metadata,
            "rendered_receipt_authority": "S1 loader metadata delivery.receipt",
        },
        "source_bundle": {
            "root": str(source_bundle),
            "manifest_sha256": sha256_file(source_bundle / "manifest.json"),
            "manifest": source_manifest,
            "receipts": [{k: v for k, v in item.items() if k != "text"} for item in source_receipts],
            "common_source_hashes": common_source_hashes,
            "mode": "fixed",
            "live_access": "not_prepared; no live performance claim",
        },
        "questions": questions,
        "variants": variants,
        "packets": packets,
        "cells": cells,
        "model_input_exclusions": experiment["model_input_exclusions"],
        "limitations": [
            "No model, judge, repeat, holdout, or live-access run occurred.",
            "Preparation success, loader receipt, and matching hashes are not performance results.",
            "Unadjudicated cells are provisional metadata only and are not expert legal gold or production validation.",
        ],
    }
    metadata_path = output / "evaluator-only" / "preparation-metadata.json"
    write_json(metadata_path, metadata)
    print(
        json.dumps(
            {
                "status": "prepared_not_measured",
                "output": str(output),
                "metadata": str(metadata_path),
                "cells": len(cells),
                "model_execution": "not_started",
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
