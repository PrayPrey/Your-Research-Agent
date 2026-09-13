import sys
import os
import json
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, _HERE)
from config import Config
from scg import init_selfcheck, compute_all_scg_scores, verify_scg_mechanism
from evaluate import load_bootstrap_auroc, compute_all_aurocs
from visualize import generate_all_figures


def load_artifacts(cfg: Config) -> tuple:
    """Load samples_map, se_scores, te_scores, em_labels as qid-keyed dicts.

    h-e1 stores scores as .npy arrays in order of get_pilot_questions(seed=42).
    We reconstruct qid order using the same function to align arrays with qids.
    """
    he1_code_dir = os.path.abspath(os.path.join(_HERE, cfg.he1_code_dir))
    he1_results_dir = os.path.abspath(os.path.join(_HERE, cfg.he1_results_dir))

    if he1_code_dir not in sys.path:
        sys.path.insert(0, he1_code_dir)
    from data import load_h_e2v2_samples, get_pilot_questions

    samples_map_full = load_h_e2v2_samples()
    questions = get_pilot_questions(samples_map_full, n=cfg.n_questions, seed=cfg.seed)
    qids = [q["question_id"] for q in questions]

    # Subset samples_map to pilot questions only
    samples_map = {qid: samples_map_full[qid] for qid in qids}

    # Load pre-computed SE/TE/correctness arrays from h-e1/results
    se_arr = np.load(os.path.join(he1_results_dir, "se_scores.npy"))
    te_arr = np.load(os.path.join(he1_results_dir, "te_scores.npy"))
    corr_arr = np.load(os.path.join(he1_results_dir, "correctness.npy"))

    # h-e1 negates scores for AUROC (higher uncertainty = more incorrect)
    # se_arr and te_arr are raw uncertainty scores (higher = more uncertain)
    # For h-m3 gate: we compare SCG AUROC vs SE AUROC using same direction convention
    # SCG: higher score = more uncertain (same direction as SE)
    # We keep original sign so bootstrap_auroc sees consistent predictor direction
    se_scores = {qid: float(se_arr[i]) for i, qid in enumerate(qids)}
    te_scores = {qid: float(te_arr[i]) for i, qid in enumerate(qids)}
    em_labels = {qid: int(corr_arr[i]) for i, qid in enumerate(qids)}

    # Validation
    assert len(samples_map) == cfg.n_questions, f"Expected {cfg.n_questions} questions, got {len(samples_map)}"
    assert all(len(v["samples"]) == cfg.K for v in samples_map.values()), "Expected K=10 samples per question"
    assert set(em_labels.values()) <= {0, 1}, "em_labels must be binary"
    assert set(samples_map.keys()) == set(se_scores.keys()), "qid mismatch se_scores"
    assert set(samples_map.keys()) == set(te_scores.keys()), "qid mismatch te_scores"

    return samples_map, se_scores, te_scores, em_labels


def save_results(results: dict, path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[Results] Saved to {path}")


def main() -> None:
    cfg = Config()

    # Resolve paths relative to this file
    cfg.he1_code_dir = os.path.abspath(os.path.join(_HERE, cfg.he1_code_dir))
    cfg.hm2_code_dir = os.path.abspath(os.path.join(_HERE, cfg.hm2_code_dir))
    cfg.he1_results_dir = os.path.abspath(os.path.join(_HERE, cfg.he1_results_dir))
    figures_dir = os.path.abspath(os.path.join(_HERE, cfg.figures_dir))
    results_path = os.path.abspath(os.path.join(_HERE, cfg.results_path))

    print(f"[H-M3] Config: K={cfg.K}, seed={cfg.seed}, n_questions={cfg.n_questions}, delta_gate={cfg.delta_auroc_gate}")

    print("\n[1/6] Loading artifacts...")
    samples_map, se_scores, te_scores, em_labels = load_artifacts(cfg)
    print(f"  Loaded {len(samples_map)} questions, {sum(em_labels.values())} correct")

    print("\n[2/6] Initializing SelfCheckBERTScore...")
    selfcheck = init_selfcheck(cfg.rescale_with_baseline)

    print("\n[3/6] Computing SCG scores for all questions...")
    scg_scores = compute_all_scg_scores(samples_map, selfcheck)
    scg_list = list(scg_scores.values())
    print(f"  SCG: mean={np.mean(scg_list):.4f}, std={np.std(scg_list):.4f}, min={np.min(scg_list):.4f}, max={np.max(scg_list):.4f}")

    print("\n[4/6] Mechanism verification...")
    bootstrap_auroc_fn = load_bootstrap_auroc(cfg.hm2_code_dir)
    qids = list(scg_scores.keys())
    labels_list = [em_labels[q] for q in qids]
    se_auroc_point, _, _ = bootstrap_auroc_fn(
        [se_scores[q] for q in qids], labels_list, n_boot=100, seed=cfg.seed
    )
    activated, indicators, delta_mech = verify_scg_mechanism(
        scg_scores, em_labels, se_auroc_point, bootstrap_auroc_fn
    )
    print(f"  Mechanism activated={activated}, indicators={indicators}, delta={delta_mech:.4f}")

    print("\n[5/6] Computing AUROC evaluation...")
    results = compute_all_aurocs(scg_scores, se_scores, te_scores, em_labels, cfg)
    print(f"  SCG AUROC={results['auroc_scg']:.4f} CI=[{results['ci_scg'][0]:.4f},{results['ci_scg'][1]:.4f}]")
    print(f"  SE  AUROC={results['auroc_se']:.4f}  CI=[{results['ci_se'][0]:.4f},{results['ci_se'][1]:.4f}]")
    print(f"  TE  AUROC={results['auroc_te']:.4f}  CI=[{results['ci_te'][0]:.4f},{results['ci_te'][1]:.4f}]")
    print(f"  delta=|SCG-SE|={results['delta']:.4f}, gate<=0.03: {results['gate_passed']}")

    # Merge all into results
    results["scg_scores"] = scg_scores
    results["se_scores"] = se_scores
    results["te_scores"] = te_scores
    results["em_labels"] = em_labels
    results["mechanism_indicators"] = indicators
    results["mechanism_activated"] = activated
    results["n_questions"] = cfg.n_questions
    results["K"] = cfg.K
    results["seed"] = cfg.seed

    print("\n[6/6] Generating figures and saving...")
    generate_all_figures(scg_scores, se_scores, te_scores, em_labels, results, figures_dir)
    save_results(results, results_path)

    verdict = "PASS" if results["gate_passed"] else "FAIL"
    print(f"\n[Gate] delta={results['delta']:.4f} threshold={cfg.delta_auroc_gate} -> {verdict}")
    print(f"[AUROC] SCG={results['auroc_scg']:.4f} SE={results['auroc_se']:.4f} "
          f"TE={results['auroc_te']:.4f} SCG_vs_TE={results['scg_vs_te_advantage']:+.4f}")
    print(f"[H-M3] Gate verdict: {verdict}")


if __name__ == "__main__":
    main()
