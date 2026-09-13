"""FR-2/3: lm-eval CLI wrapper with resume-safe skip-on-existing logic."""
import json
import os
import pathlib
import subprocess
import sys
from config import (
    PYTHIA_ID, PYTHIA_REVISION,
    OLMO_ID, OLMO_REVISION,
    TASKS, FEWSHOT_MAP, RESULTS_DIR,
)


def build_lm_eval_cmd(
    model_id: str,
    revision: str,
    output_dir: str,
    fewshot_map: dict[str, int] = None,
    tasks: list[str] = None,
    limit: int | None = None,
    batch_size: str = "auto",
) -> list[str]:
    """Return argv list for lm_eval CLI."""
    if tasks is None:
        tasks = TASKS
    # Use same python env's lm_eval binary, not system lm_eval
    lm_eval_bin = os.path.join(os.path.dirname(sys.executable), "lm_eval")
    cmd = [
        lm_eval_bin,
        "--model", "hf",
        "--model_args", f"pretrained={model_id},revision={revision},dtype=float16,trust_remote_code=True",
        "--tasks", ",".join(tasks),
        "--batch_size", batch_size,
        "--output_path", output_dir,
        "--log_samples",
    ]
    if limit is not None:
        cmd += ["--limit", str(limit)]
    return cmd


def run_evaluation(
    model_id: str,
    revision: str,
    output_dir: str,
    fewshot_map: dict[str, int] = None,
    tasks: list[str] = None,
    force_rerun: bool = False,
) -> pathlib.Path:
    """Run lm_eval; skip if results.json already exists. Returns path to results.json."""
    if fewshot_map is None:
        fewshot_map = FEWSHOT_MAP
    if tasks is None:
        tasks = TASKS

    out_path = pathlib.Path(output_dir)
    # Resume-safe: check for existing results
    existing = sorted(out_path.rglob("results.json"), key=lambda p: p.stat().st_mtime)
    if existing and not force_rerun:
        print(f"[SKIP] Results already exist at {existing[-1]}")
        return existing[-1]

    out_path.mkdir(parents=True, exist_ok=True)
    cmd = build_lm_eval_cmd(model_id, revision, output_dir, fewshot_map, tasks)
    print(f"[EVAL] Running: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        # Retry with batch_size=1 on potential OOM
        print(f"[WARN] lm_eval failed (exit={e.returncode}), retrying with batch_size=1...")
        cmd_retry = build_lm_eval_cmd(model_id, revision, output_dir, fewshot_map, tasks, batch_size="1")
        subprocess.run(cmd_retry, check=True)

    candidates = sorted(out_path.rglob("results.json"), key=lambda p: p.stat().st_mtime)
    if not candidates:
        raise FileNotFoundError(f"lm-eval completed but no results.json found under {output_dir}")
    return candidates[-1]


def load_results(results_path: pathlib.Path) -> dict[str, dict]:
    """Load lm-eval results JSON; validate required keys present."""
    with open(results_path) as f:
        data = json.load(f)

    raw = data.get("results", {})
    if not raw:
        raise ValueError(f"No 'results' key in {results_path} — lm-eval may have failed silently")

    required_non_mmlu = {"hellaswag", "arc_easy", "arc_challenge"}
    present = set(raw.keys())
    mmlu_keys = {k for k in present if k.startswith("mmlu_")}

    missing = required_non_mmlu - present
    if missing:
        raise KeyError(f"Missing expected task results: {missing}")
    if len(mmlu_keys) < 10:
        raise ValueError(
            f"Only {len(mmlu_keys)} MMLU subjects found (expected 57); partial evaluation?"
        )

    return raw


def evaluate_both_models() -> tuple[dict, dict]:
    """Evaluate Pythia then OLMo; return (pythia_results, olmo_results)."""
    pythia_path = run_evaluation(
        PYTHIA_ID, PYTHIA_REVISION,
        f"{RESULTS_DIR}/pythia-6.9b-300B",
    )
    olmo_path = run_evaluation(
        OLMO_ID, OLMO_REVISION,
        f"{RESULTS_DIR}/olmo-7b-300B",
    )
    return load_results(pythia_path), load_results(olmo_path)
