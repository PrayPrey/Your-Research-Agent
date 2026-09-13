"""E3: Parse lm-eval JSON outputs; build accuracy[size][corpus][benchmark] matrix."""
import json
from glob import glob
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
RESULTS_DIR = BASE_DIR / "results"
CHECKPOINT_MAP_FILE = BASE_DIR / "checkpoint_map.json"
OUTPUT_FILE = BASE_DIR / "results_matrix.json"

BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
SIZES = ["160m", "410m", "1b", "6.9b"]

# lm-eval 0.4.x uses "acc,none" as the metric key
ACC_KEY = "acc,none"


def load_accuracy(result_dir: str, task: str) -> float:
    """Load acc,none from lm-eval JSON output directory for a single task."""
    pattern = str(Path(result_dir) / task / "**" / "*.json")
    matches = glob(pattern, recursive=True)
    # Exclude samples_ files
    result_files = [f for f in matches if "samples_" not in Path(f).name]
    if not result_files:
        raise FileNotFoundError(f"No result JSON found in {result_dir}/{task}")
    # Load the first (should be only) results file
    data = json.loads(Path(result_files[0]).read_text())
    results = data.get("results", {})
    # task key may be exact or prefixed
    task_results = results.get(task) or results.get(task.replace("_", "-"))
    if task_results is None:
        # Try finding any key containing the task name
        for k, v in results.items():
            if task in k:
                task_results = v
                break
    if task_results is None:
        raise KeyError(f"Task '{task}' not found in results keys: {list(results.keys())}")
    acc = task_results.get(ACC_KEY)
    if acc is None:
        raise KeyError(f"'{ACC_KEY}' not in task results: {list(task_results.keys())}")
    return float(acc)


def build_accuracy_matrix(checkpoint_map: dict) -> dict:
    matrix = {}
    for size in SIZES:
        matrix[size] = {"pile": {}, "dedup": {}}
        pile_step = checkpoint_map[size]["pile_step"]
        dedup_step = checkpoint_map[size]["dedup_step"]

        for corpus, step in [("pile", pile_step), ("dedup", dedup_step)]:
            if corpus == "pile":
                hf_slug = f"EleutherAI-pythia-{size}-step{step}"
            else:
                hf_slug = f"EleutherAI-pythia-{size}-deduped-step{step}"
            result_dir = str(RESULTS_DIR / hf_slug)

            for benchmark in BENCHMARKS:
                try:
                    acc = load_accuracy(result_dir, benchmark)
                    matrix[size][corpus][benchmark] = acc
                    print(f"  {size} {corpus} {benchmark}: {acc:.4f}")
                except (FileNotFoundError, KeyError) as e:
                    print(f"  [WARN] Missing: {size} {corpus} {benchmark} — {e}")
                    matrix[size][corpus][benchmark] = None
    return matrix


def main() -> None:
    checkpoint_map = json.loads(CHECKPOINT_MAP_FILE.read_text())
    print("Building accuracy matrix...")
    matrix = build_accuracy_matrix(checkpoint_map)
    OUTPUT_FILE.write_text(json.dumps(matrix, indent=2))
    print(f"\nWrote {OUTPUT_FILE}")

    # Quick sanity: count populated cells
    populated = sum(
        1
        for s in SIZES
        for c in ["pile", "dedup"]
        for b in BENCHMARKS
        if matrix.get(s, {}).get(c, {}).get(b) is not None
    )
    total = len(SIZES) * 2 * len(BENCHMARKS)
    print(f"Populated: {populated}/{total} cells")


if __name__ == "__main__":
    main()
