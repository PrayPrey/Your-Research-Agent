"""evaluate.py — E-5: Evaluation runner using bigcode-evaluation-harness for H-E1"""
import json
import os
import subprocess
import sys
from pathlib import Path


TASK_MAP = {
    "humaneval": "humaneval",
    "mbpp": "mbpp",
    "lcb_easy": "livecodebench",
    "lcb_medium": "livecodebench",
    "lcb_hard": "livecodebench",
}

LCB_DIFFICULTY_MAP = {
    "lcb_easy": "easy",
    "lcb_medium": "medium",
    "lcb_hard": "hard",
}


def find_harness_main() -> str:
    """Find bigcode-evaluation-harness main.py."""
    candidates = [
        "bigcode-evaluation-harness/main.py",
        "../bigcode-evaluation-harness/main.py",
        os.path.expanduser("~/bigcode-evaluation-harness/main.py"),
        "/opt/bigcode-evaluation-harness/main.py",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    raise FileNotFoundError(
        "bigcode-evaluation-harness/main.py not found. "
        "Run: git clone https://github.com/bigcode-project/bigcode-evaluation-harness.git && "
        "cd bigcode-evaluation-harness && pip install -e ."
    )


def run_harness(
    checkpoint_path: str,
    task: str,
    output_path: str,
    n_samples: int = 1,
    temperature: float = 0.2,
    harness_main: str = None,
) -> dict:
    """Shell out to bigcode-evaluation-harness. Returns parsed JSON results."""
    if harness_main is None:
        harness_main = find_harness_main()

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    harness_task = TASK_MAP[task]
    cmd = [
        "accelerate", "launch", harness_main,
        "--model", checkpoint_path,
        "--tasks", harness_task,
        "--n_samples", str(n_samples),
        "--temperature", str(temperature),
        "--allow_code_execution",
        "--metric_output_path", output_path,
    ]

    # For LiveCodeBench, filter by difficulty
    if task in LCB_DIFFICULTY_MAP:
        difficulty = LCB_DIFFICULTY_MAP[task]
        cmd += ["--difficulty", difficulty]

    print(f"Running evaluation: {task} on {checkpoint_path}")
    print(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
    if result.returncode != 0:
        print(f"Harness stderr: {result.stderr[-2000:]}")
        raise RuntimeError(f"Harness failed for {task}: {result.returncode}")

    with open(output_path) as f:
        return json.load(f)


def run_all(
    sft_ckpt: str,
    rlef_ckpt: str,
    results_dir: str,
    harness_main: str = None,
) -> dict:
    """Run all 5 benchmarks × 2 models. Returns nested results dict."""
    Path(results_dir).mkdir(parents=True, exist_ok=True)
    tasks = ["humaneval", "mbpp", "lcb_easy", "lcb_medium", "lcb_hard"]
    models = {"sft": sft_ckpt, "rlef": rlef_ckpt}

    results = {}
    for model_key, ckpt in models.items():
        results[model_key] = {}
        for task in tasks:
            out_path = f"{results_dir}/{model_key}_{task}.json"
            if Path(out_path).exists():
                print(f"✓ Cached: {model_key}/{task}")
                with open(out_path) as f:
                    results[model_key][task] = json.load(f)
                continue
            try:
                r = run_harness(ckpt, task, out_path, harness_main=harness_main)
                results[model_key][task] = r
                print(f"✓ Done: {model_key}/{task}")
            except Exception as e:
                print(f"✗ Failed: {model_key}/{task}: {e}")
                results[model_key][task] = {"error": str(e), "pass@1": 0.0}

    return results


def extract_pass_at_1(results: dict, model_key: str, task: str) -> float:
    """Extract pass@1 float from harness output dict."""
    r = results.get(model_key, {}).get(task, {})
    # Harness stores in different keys depending on version
    for key in ["pass@1", "pass_at_1", "results"]:
        if key in r:
            val = r[key]
            if isinstance(val, dict):
                # nested: {"pass@1": 0.x}
                val = val.get("pass@1", val.get("pass_at_1", 0.0))
            return float(val) if val is not None else 0.0
    return 0.0


if __name__ == "__main__":
    import yaml
    cfg_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)
    sft_dir = f"{cfg['paths']['checkpoints_dir']}/sft_baseline"
    rlef_dir = f"{cfg['paths']['checkpoints_dir']}/rlef_fraction"
    results = run_all(sft_dir, rlef_dir, cfg["paths"]["results_dir"])
    print(json.dumps(results, indent=2))
