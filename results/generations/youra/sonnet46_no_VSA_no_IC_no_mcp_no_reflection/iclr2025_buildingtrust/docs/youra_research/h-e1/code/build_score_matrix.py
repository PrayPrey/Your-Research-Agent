"""FR-3: Score Matrix Builder — load lm-eval results → X, y arrays."""
import json
import os
import glob

import numpy as np

from run_evaluations_wrapper import safe_model_id, handle_bbq_fallback

TASK_KEYS = {
    "truthfulqa_mc2": "acc,none",
    "bbq":            "acc,none",
    "winogrande":     "acc,none",
    "winogender_all": "acc,none",  # winograd_wsc unavailable in lm-eval 0.4.12; winogender_all is WinoGender
}
TASK_ORDER = ["truthfulqa_mc2", "bbq", "winogrande", "winogender_all"]


def _find_results_json(results_dir: str, safe_id: str) -> str | None:
    """Find results.json — lm-eval may nest output under a timestamp subdir or use timestamp filename.
    Also tries single-dash variant (launch_eval.sh uses / -> - while safe_model_id uses / -> --)."""
    # Both safe_id variants: double-dash (safe_model_id) and single-dash (launch_eval.sh)
    safe_id_single = safe_id.replace("--", "-")
    for sid in [safe_id, safe_id_single]:
        direct = os.path.join(results_dir, sid, "results.json")
        if os.path.exists(direct):
            return direct
        for pattern in [
            os.path.join(results_dir, sid, "**", "results.json"),
            os.path.join(results_dir, sid, "**", "results_*.json"),
        ]:
            matches = glob.glob(pattern, recursive=True)
            if matches:
                return sorted(matches)[-1]
    return None


def load_result(results_dir: str, model_id: str) -> dict[str, float]:
    """Load results.json for model_id, extract 4 task scores in [0, 1]."""
    safe_id = safe_model_id(model_id)
    path = _find_results_json(results_dir, safe_id)
    if path is None:
        raise FileNotFoundError(
            f"No results.json for {model_id} (safe_id={safe_id}) under {results_dir}"
        )

    with open(path) as f:
        data = json.load(f)

    # Apply BBQ fallback if needed
    data, substituted = handle_bbq_fallback(data, model_id)

    results = data.get("results", {})
    scores: dict[str, float] = {}
    for task, metric in TASK_KEYS.items():
        task_results = results.get(task, {})
        score = task_results.get(metric)
        if score is None:
            # Try alternate metric keys
            for key in task_results:
                if "acc" in key.lower():
                    score = task_results[key]
                    break
        if score is None:
            raise ValueError(f"Missing score for task '{task}' (metric '{metric}') in {path}")
        assert 0.0 <= float(score) <= 1.0, (
            f"Score out of range for {task}: {score} in {path}"
        )
        scores[task] = float(score)

    return scores


def build_matrix(
    pairs_path: str = "model_pairs.json",
    results_dir: str = "results",
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Build X: (2n, 4) and y: (2n,) from all model results.
    Also returns model_ids list for visualization.
    """
    with open(pairs_path) as f:
        pairs = json.load(f)

    rows: list[list[float]] = []
    labels: list[int] = []
    model_ids: list[str] = []
    failed: list[str] = []

    for p in pairs:
        for label, key in [(0, "sft_model_id"), (1, "dpo_model_id")]:
            mid = p[key]
            try:
                scores = load_result(results_dir, mid)
                row = [scores[t] for t in TASK_ORDER]
                rows.append(row)
                labels.append(label)
                model_ids.append(mid)
                print(f"  {'SFT' if label==0 else 'DPO'} {mid}: {[f'{s:.3f}' for s in row]}")
            except FileNotFoundError:
                print(f"  ⚠ Skipping {mid} — results not found")
                failed.append(mid)

    if failed:
        print(f"\n⚠ {len(failed)} models missing results: {failed}")

    n_sft = labels.count(0)
    n_dpo = labels.count(1)
    assert n_sft == n_dpo, f"Unbalanced labels: n_SFT={n_sft}, n_DPO={n_dpo}"
    assert len(rows) >= 4, f"Need ≥4 models (≥2 pairs) for classification, got {len(rows)}"

    X = np.array(rows, dtype=np.float64)
    y = np.array(labels, dtype=np.int64)

    print(f"\n✓ Score matrix: X={X.shape}, y={y.shape} ({n_sft} SFT, {n_dpo} DPO)")
    return X, y, model_ids


def main() -> tuple[np.ndarray, np.ndarray, list[str]]:
    X, y, model_ids = build_matrix()
    return X, y, model_ids


if __name__ == "__main__":
    X, y, model_ids = main()
    print(f"X shape: {X.shape}")
    print(f"y: {y}")
