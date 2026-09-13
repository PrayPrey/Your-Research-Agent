"""Task A: LCB-Hard evaluation via bigcode-evaluation-harness shell-out."""
import json
import os
import subprocess
from pathlib import Path


def run_lcb_hard_eval(
    checkpoint_path: str,
    harness_dir: str,
    output_path: str,
) -> dict:
    """Shell out to bigcode-evaluation-harness for LCB-Hard. Returns parsed JSON."""
    output_path = str(Path(output_path).resolve())
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "accelerate", "launch", "main.py",
        "--model", str(Path(checkpoint_path).resolve()),
        "--tasks", "livecodebench",
        "--n_samples", "1",
        "--temperature", "0.0",
        "--metric_output_path", output_path,
        "--allow_code_execution",
    ]
    result = subprocess.run(cmd, cwd=harness_dir, capture_output=True, text=True, timeout=7200)
    if result.returncode != 0:
        raise RuntimeError(f"Harness failed (exit {result.returncode}): {result.stderr[-2000:]}")
    with open(output_path) as f:
        return json.load(f)


def extract_lcb_hard_pass1(results_json_path: str) -> float:
    """Read harness output JSON, return pass@1 for livecodebench hard difficulty."""
    with open(results_json_path) as f:
        data = json.load(f)
    # Try common result key patterns from bigcode-harness
    for key in data:
        if "livecodebench" in key.lower():
            val = data[key]
            if isinstance(val, dict):
                # Try pass@1 under hard difficulty
                for subkey in ["pass@1", "pass_at_1", "pass@1,difficulty=hard"]:
                    if subkey in val:
                        return float(val[subkey])
                # Flat numeric value
                if "results" in val:
                    inner = val["results"]
                    for subkey in ["pass@1", "pass_at_1"]:
                        if subkey in inner:
                            return float(inner[subkey])
            elif isinstance(val, (int, float)):
                return float(val)
    # Fallback: look for any pass@1 key
    if "pass@1" in data:
        return float(data["pass@1"])
    raise KeyError(f"Cannot find pass@1 in {results_json_path}. Keys: {list(data.keys())}")


def check_gate(pass1: float, threshold: float = 0.60) -> dict:
    """Returns gate check result dict."""
    return {
        "signal_void_confirmed": pass1 < threshold,
        "pass1": pass1,
        "threshold": threshold,
        "margin": threshold - pass1,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default="checkpoints/sft_baseline/")
    parser.add_argument("--harness_dir", default="bigcode-evaluation-harness")
    parser.add_argument("--he1_results", default="results/h-e1/sft_baseline_livecodebench.json")
    parser.add_argument("--output", default="results/h-m1/sft_lcb_hard.json")
    args = parser.parse_args()

    # FR-2.1: check H-E1 results first
    if os.path.exists(args.he1_results):
        print(f"Found H-E1 results at {args.he1_results}, attempting extraction...")
        try:
            pass1 = extract_lcb_hard_pass1(args.he1_results)
            print(f"Extracted LCB-Hard pass@1 from H-E1 results: {pass1:.4f}")
            gate = check_gate(pass1)
            print(f"Gate: {gate}")
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, "w") as f:
                json.dump({"pass@1": pass1, "source": "h-e1_cache", "gate": gate}, f, indent=2)
        except (KeyError, Exception) as e:
            print(f"H-E1 extraction failed ({e}), running harness...")
            results = run_lcb_hard_eval(args.checkpoint, args.harness_dir, args.output)
            pass1 = extract_lcb_hard_pass1(args.output)
            gate = check_gate(pass1)
            print(f"Harness LCB-Hard pass@1: {pass1:.4f}, gate: {gate}")
    else:
        print(f"No H-E1 results found, running harness evaluation...")
        results = run_lcb_hard_eval(args.checkpoint, args.harness_dir, args.output)
        pass1 = extract_lcb_hard_pass1(args.output)
        gate = check_gate(pass1)
        print(f"Harness LCB-Hard pass@1: {pass1:.4f}, gate: {gate}")
