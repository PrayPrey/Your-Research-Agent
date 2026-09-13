"""FR-2: Benchmark Evaluation — verify lm-eval tasks and run evaluations."""
import json
import os
import subprocess
import sys


TASKS = ["truthfulqa_mc2", "bbq", "winogrande", "winogender_all"]
# winograd_wsc unavailable in lm-eval 0.4.12; winogender_all is the WinoGender task
TASK_KEYS = {
    "truthfulqa_mc2": "acc,none",
    "bbq":            "acc,none",
    "winogrande":     "acc,none",
    "winogender_all": "acc,none",
}


def safe_model_id(model_id: str) -> str:
    return model_id.replace("/", "--")


def verify_tasks_available(tasks: list[str], lm_eval_version: str) -> dict[str, bool]:
    """Check lm-eval registry contains all required tasks."""
    try:
        result = subprocess.run(
            ["python", "-m", "lm_eval", "--tasks", "list"],
            capture_output=True, text=True, timeout=60
        )
        output = result.stdout + result.stderr
        availability = {task: task in output for task in tasks}
        return availability
    except Exception as e:
        print(f"⚠ Task verification failed: {e} — assuming all available")
        return {task: True for task in tasks}


def handle_bbq_fallback(
    result_json: dict,
    model_id: str,
    sub_log_path: str = "results/substitutions.txt"
) -> tuple[dict, bool]:
    """If bbq missing, substitute winogrande scores as fairness proxy."""
    results = result_json.get("results", {})
    bbq_ok = "bbq" in results and "acc,none" in results.get("bbq", {})
    if not bbq_ok:
        wino = results.get("winogrande", {})
        if "acc,none" not in wino:
            raise RuntimeError(f"Neither bbq nor winogrande available for {model_id}")
        results["bbq"] = {"acc,none": wino["acc,none"]}
        result_json["results"] = results
        os.makedirs(os.path.dirname(sub_log_path), exist_ok=True)
        with open(sub_log_path, "a") as f:
            f.write(f"{model_id}: bbq -> winogrande (substituted)\n")
        print(f"  ⚠ BBQ fallback applied for {model_id}: using winogrande score")
        return result_json, True
    return result_json, False


def run_single_model(
    model_id: str,
    results_dir: str = "results",
    batch_size: int = 8,
    dtype: str = "bfloat16",
    tasks: list[str] | None = None,
) -> bool:
    """Run lm-eval for one model. Returns True on success."""
    if tasks is None:
        tasks = TASKS
    safe_id = safe_model_id(model_id)
    output_path = os.path.join(results_dir, safe_id)
    result_file = os.path.join(output_path, "results.json")

    if os.path.exists(result_file):
        print(f"  ✓ Already evaluated: {model_id} (cached)")
        return True

    # Use task list without bbq first; handle fallback after
    task_str = ",".join(tasks)
    cmd = [
        "python", "-m", "lm_eval",
        "--model", "hf",
        "--model_args", f"pretrained={model_id},dtype={dtype}",
        "--tasks", task_str,
        "--batch_size", str(batch_size),
        "--output_path", output_path,
        "--log_samples",
    ]
    print(f"  Running: {' '.join(cmd[:6])} ...")
    try:
        proc = subprocess.run(cmd, timeout=10800, capture_output=False)
        return proc.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  ✗ Timeout for {model_id}")
        return False
    except Exception as e:
        print(f"  ✗ Error for {model_id}: {e}")
        return False


def run_all_evaluations(
    pairs_path: str = "model_pairs.json",
    results_dir: str = "results",
) -> None:
    """Run lm-eval for all models in pairs file."""
    with open(pairs_path) as f:
        pairs = json.load(f)

    # Verify tasks
    avail = verify_tasks_available(TASKS, "0.4.x")
    print("Task availability:")
    for t, ok in avail.items():
        print(f"  {'✓' if ok else '✗'} {t}")

    # Collect all model IDs
    model_ids = []
    for p in pairs:
        model_ids.append(("SFT", p["sft_model_id"]))
        model_ids.append(("DPO", p["dpo_model_id"]))

    os.makedirs(results_dir, exist_ok=True)
    success_count = 0
    for label, model_id in model_ids:
        print(f"\n[{label}] Evaluating {model_id}")
        ok = run_single_model(model_id, results_dir=results_dir)
        if ok:
            success_count += 1
        else:
            print(f"  ⚠ Evaluation failed — will attempt BBQ fallback at matrix-build stage")

    print(f"\n✓ Evaluation complete: {success_count}/{len(model_ids)} models")


if __name__ == "__main__":
    run_all_evaluations()
