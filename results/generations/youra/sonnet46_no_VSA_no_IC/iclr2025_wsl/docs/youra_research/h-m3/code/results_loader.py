"""Load baselines (Flat-MLP, GNN-NFN) from H-E1/H-M2 stored results."""
import json
import os


def load_baselines(h_m2_json: str) -> dict:
    """Load flat_mlp and gnn_nfn from H-M2 learning_curve_results.json.

    Returns {encoder: {zoo: {size_str: {mean_r2, ci_lo, ci_hi, seed_r2s}}}}.
    Raises FileNotFoundError if missing. Does NOT re-train anything.
    """
    if not os.path.exists(h_m2_json):
        raise FileNotFoundError(
            f"H-M2 results not found: {h_m2_json}\n"
            "Run H-M2 experiment first."
        )

    with open(h_m2_json) as f:
        raw = json.load(f)

    results = raw.get("results", raw)
    baselines = {}
    for encoder in ["flat_mlp", "gnn_nfn"]:
        if encoder not in results:
            raise KeyError(f"Encoder '{encoder}' not in H-M2 results. Keys: {list(results.keys())}")
        baselines[encoder] = results[encoder]

    return baselines


def save_results(all_results: dict, out_path: str) -> dict:
    """Save merged results dict to JSON."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"[H-M3] Results saved to {out_path}")
    return all_results
