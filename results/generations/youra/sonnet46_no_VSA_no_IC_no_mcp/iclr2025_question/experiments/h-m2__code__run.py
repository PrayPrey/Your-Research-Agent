import sys
import os
import json

# Resolve paths relative to this file
_HERE = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, _HERE)
from config import Config
from ablation import compute_ablation_scores
from evaluate import compute_delta_auroc, compute_secondary_metrics, verify_mechanism_activated
from visualize import generate_all_figures


def load_and_validate_config() -> Config:
    cfg = Config()
    he1_code_dir = os.path.abspath(os.path.join(_HERE, cfg.he1_code_dir))
    hm1_code_dir = os.path.abspath(os.path.join(_HERE, cfg.hm1_code_dir))
    he1_results_dir = os.path.abspath(os.path.join(_HERE, cfg.he1_results_dir))
    assert os.path.isdir(he1_code_dir), f"he1_code_dir not found: {he1_code_dir}"
    assert os.path.isdir(hm1_code_dir), f"hm1_code_dir not found: {hm1_code_dir}"
    assert 0 < cfg.paraphrase_subset_size <= cfg.n_questions
    assert 0.0 < cfg.entailment_threshold < 1.0
    assert cfg.delta_auroc_gate > 0.0
    # store resolved absolute paths back
    cfg.he1_code_dir = he1_code_dir
    cfg.hm1_code_dir = hm1_code_dir
    cfg.he1_results_dir = he1_results_dir
    return cfg


def load_artifacts(cfg: Config) -> tuple:
    """Load questions, samples, cluster_assignments, em_labels from H-M1/H-E1 cache."""
    if cfg.hm1_code_dir not in sys.path:
        sys.path.insert(0, cfg.hm1_code_dir)
    from cache_loader import load_or_recompute
    data = load_or_recompute(
        he1_results_dir=cfg.he1_results_dir,
        he1_code_dir=cfg.he1_code_dir,
        n=cfg.n_questions,
        seed=cfg.seed,
        nli_model_id=cfg.nli_model_name,
        nli_device=0,
    )
    questions = data["questions"]
    samples_map = data["samples_map"]
    cluster_assignments = data["cluster_assignments"]
    em_labels = [int(c) for c in data["correctness"]]

    assert len(questions) == cfg.n_questions, f"Expected {cfg.n_questions} questions, got {len(questions)}"
    assert len(em_labels) == cfg.n_questions
    assert set(em_labels) <= {0, 1}, f"em_labels not binary: {set(em_labels)}"
    qids = [q["question_id"] for q in questions]
    assert all(qid in cluster_assignments for qid in qids), "Missing qids in cluster_assignments"
    return questions, samples_map, cluster_assignments, em_labels


def get_paraphrase_subset(questions: list, cluster_assignments: dict, n: int = 20) -> list:
    """Returns first n question_ids with >=1 multi-member cluster."""
    subset = []
    for q in questions:
        qid = q["question_id"]
        cids = list(cluster_assignments[qid].values())
        from collections import Counter
        if max(Counter(cids).values()) >= 2:
            subset.append(qid)
        if len(subset) >= n:
            break
    return subset


def save_results(results: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[H-M2] Results saved to {path}")


def main() -> None:
    print("[H-M2] Starting SE NLI Clustering Ablation Study")
    cfg = load_and_validate_config()
    print(f"[H-M2] Config: K={cfg.K}, seed={cfg.seed}, n_questions={cfg.n_questions}, delta_auroc_gate={cfg.delta_auroc_gate}")

    print("[H-M2] Loading artifacts from H-M1/H-E1 cache...")
    questions, samples_map, cluster_assignments, em_labels = load_artifacts(cfg)
    question_ids = [q["question_id"] for q in questions]
    print(f"[H-M2] Loaded {len(questions)} questions, {sum(em_labels)} correct")

    print("[H-M2] Computing ablation scores...")
    se_clustered, within_fracs, cluster_counts = compute_ablation_scores(
        cluster_assignments, question_ids, K=cfg.K
    )
    print(f"[H-M2] mean_SE_clustered={sum(se_clustered)/len(se_clustered):.4f}, "
          f"mean_within_frac={sum(within_fracs)/len(within_fracs):.4f}, "
          f"mean_cluster_count={sum(cluster_counts)/len(cluster_counts):.2f}")

    print("[H-M2] Computing AUROC comparison...")
    auroc_results = compute_delta_auroc(se_clustered, within_fracs, em_labels, cfg)
    print(f"[H-M2] AUROC_clustered={auroc_results['auroc_clustered']:.4f} [{auroc_results['ci_clustered'][0]:.4f}, {auroc_results['ci_clustered'][1]:.4f}]")
    print(f"[H-M2] AUROC_ablated={auroc_results['auroc_ablated']:.4f} [{auroc_results['ci_ablated'][0]:.4f}, {auroc_results['ci_ablated'][1]:.4f}]")
    print(f"[H-M2] delta_AUROC={auroc_results['delta_auroc']:.4f} (gate>={cfg.delta_auroc_gate})")

    print("[H-M2] Computing secondary metrics...")
    subset_ids = get_paraphrase_subset(questions, cluster_assignments, n=cfg.paraphrase_subset_size)
    secondary = compute_secondary_metrics(within_fracs, cluster_assignments, subset_ids)
    print(f"[H-M2] secondary={secondary}")

    # Build results dict for mechanism verification
    combined = {**auroc_results, **secondary}
    gate_pass, mechanism_active, indicators = verify_mechanism_activated(combined)
    print(f"[H-M2] Mechanism indicators: {indicators}")
    print(f"[H-M2] mechanism_active={mechanism_active}, gate_pass={gate_pass}")

    # Full results for saving
    results = {
        "hypothesis_id": "h-m2",
        "seed": cfg.seed,
        "n_questions": cfg.n_questions,
        "K": cfg.K,
        "full_auroc": auroc_results["auroc_clustered"],
        "full_auroc_ci": auroc_results["ci_clustered"],
        "ablated_auroc": auroc_results["auroc_ablated"],
        "ablated_auroc_ci": auroc_results["ci_ablated"],
        "delta_auroc": auroc_results["delta_auroc"],
        "gate_passed": gate_pass,
        "gate_verdict": auroc_results["gate_verdict"],
        "mechanism_active": mechanism_active,
        "mechanism_indicators": indicators,
        "paraphrase_subset_size": len(subset_ids),
        "mean_within_cluster_fraction": secondary["mean_within_cluster_fraction"],
        "entailment_coclustering_rate": secondary["entailment_coclustering_rate"],
        "mean_cluster_count": secondary["mean_cluster_count"],
        "figures": ["auroc_comparison.png", "within_cluster_scatter.png",
                    "cluster_count_hist.png", "se_boxplot.png"],
    }

    print("[H-M2] Generating figures...")
    figures_dir = os.path.abspath(os.path.join(_HERE, cfg.figures_dir))
    generate_all_figures(
        results=auroc_results,
        se_clustered=se_clustered,
        within_fracs=within_fracs,
        cluster_counts=cluster_counts,
        question_ids=question_ids,
        subset_ids=subset_ids,
        figures_dir=figures_dir,
    )
    print(f"[H-M2] Figures saved to {figures_dir}")

    results_path = os.path.abspath(os.path.join(_HERE, cfg.results_path))
    save_results(results, results_path)

    print("\n" + "="*60)
    print(f"[H-M2] GATE VERDICT: {auroc_results['gate_verdict']}")
    print(f"  delta_AUROC = {auroc_results['delta_auroc']:.4f} (threshold={cfg.delta_auroc_gate})")
    print(f"  mechanism_active = {mechanism_active}")
    for k, v in indicators.items():
        print(f"    {k}: {v}")
    print("="*60)


if __name__ == "__main__":
    main()
