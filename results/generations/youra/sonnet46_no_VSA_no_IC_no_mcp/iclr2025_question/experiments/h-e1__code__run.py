"""H-E1 Orchestrator: SE vs TE AUROC comparison on TriviaQA/Llama-2-7B."""
import argparse
import os
import sys
import json
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from data import load_h_e2v2_samples, get_pilot_questions
from compute_te import load_llama, compute_te_scores
from compute_se import load_nli_model, compute_se_scores
from evaluate import (
    em_correctness, bootstrap_auroc, verify_mechanism,
    save_results, plot_figures
)

CONFIG = {
    "model_id": "meta-llama/Llama-2-7b-hf",
    "nli_model_id": "cross-encoder/nli-deberta-v3-large",
    "nli_device": 0,
    "K": 10,
    "n_pilot": 98,
    "seed": 42,
    "bootstrap_iterations": 1000,
    "gap_threshold": 0.05,
    "gap_extend_low": 0.03,
    "avg_clusters_min": 1.5,
    "out_dir": "docs/youra_research/h-e1/results/",
    "figures_dir": "docs/youra_research/h-e1/figures/",
}


def parse_args():
    p = argparse.ArgumentParser(description="H-E1: SE vs TE AUROC on TriviaQA/Llama-2-7B")
    p.add_argument("--samples-path", type=str, default=None,
                   help="Path to h-e2-v2 samples JSONL (default: archive interim_cache.jsonl)")
    p.add_argument("--n", type=int, default=98, metavar="N")
    p.add_argument("--out-dir", type=str, default=CONFIG["out_dir"])
    p.add_argument("--figures-dir", type=str, default=CONFIG["figures_dir"])
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--smoke-test", action="store_true",
                   help="Run N=5 only; verify no crash.")
    p.add_argument("--skip-te", action="store_true",
                   help="Reuse cached te_scores.npy from out_dir if present.")
    p.add_argument("--skip-llama", action="store_true",
                   help="Use pre-computed te_score from h-e2-v2 cache.")
    return p.parse_args()


def main():
    args = parse_args()
    n = 5 if args.smoke_test else args.n
    seed = args.seed
    out_dir = args.out_dir
    figures_dir = args.figures_dir

    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)

    print(f"=== H-E1: SE vs TE AUROC (N={n}, seed={seed}) ===")

    # Step 1: Load samples
    print("\n[1/6] Loading h-e2-v2 samples...")
    samples_map = load_h_e2v2_samples(args.samples_path) if args.samples_path else load_h_e2v2_samples()
    questions = get_pilot_questions(samples_map, n=n, seed=seed)
    print(f"  Loaded {len(questions)} questions with K=10 samples")

    # Step 2: Token Entropy
    print("\n[2/6] Computing Token Entropy...")
    te_cache = os.path.join(out_dir, "te_scores.npy")
    if args.skip_te and os.path.exists(te_cache):
        te_scores = np.load(te_cache).tolist()
        print(f"  Loaded cached TE from {te_cache}")
    elif args.skip_llama:
        # Use pre-computed te_score from h-e2-v2
        te_scores = []
        for q in questions:
            qid = q["question_id"]
            cached_te = samples_map[qid].get("te_score")
            if cached_te is not None:
                te_scores.append(float(cached_te))
            else:
                te_scores.append(0.0)
        print(f"  Using pre-computed TE scores from h-e2-v2 cache")
    else:
        model, tokenizer = load_llama(CONFIG["model_id"])
        te_scores = compute_te_scores(questions, model, tokenizer)
        # free GPU mem
        del model
        import torch; torch.cuda.empty_cache()

    print(f"  TE scores: mean={np.mean(te_scores):.4f}, std={np.std(te_scores):.4f}")

    # Step 3: Semantic Entropy
    print("\n[3/6] Computing Semantic Entropy...")
    print("  Loading NLI model...")
    nli = load_nli_model(CONFIG["nli_model_id"], CONFIG["nli_device"])
    se_scores, avg_clusters = compute_se_scores(questions, samples_map, nli)
    print(f"  SE scores: mean={np.mean(se_scores):.4f}, avg_clusters={avg_clusters:.2f}")

    # Step 4: EM correctness labels
    print("\n[4/6] Computing EM correctness labels...")
    # Use cached is_correct if available, otherwise compute from greedy_answer
    correctness = []
    for q in questions:
        qid = q["question_id"]
        cached_correct = samples_map[qid].get("is_correct")
        if cached_correct is not None:
            correctness.append(int(cached_correct))
        else:
            pred = [q.get("greedy_answer", "")]
            refs = q.get("answers", [])
            c = em_correctness(pred, [refs])
            correctness.append(c[0])
    print(f"  Accuracy: {np.mean(correctness):.3f} ({sum(correctness)}/{len(correctness)} correct)")

    # Step 5: AUROC + Bootstrap
    print("\n[5/6] Computing AUROC...")
    y_true = np.array(correctness)
    te_arr = np.array(te_scores)
    se_arr = np.array(se_scores)

    # negate: higher uncertainty → should predict incorrectness → AUROC against correctness
    auroc_te, te_ci = bootstrap_auroc(y_true, -te_arr, CONFIG["bootstrap_iterations"], seed)
    auroc_se, se_ci = bootstrap_auroc(y_true, -se_arr, CONFIG["bootstrap_iterations"], seed)
    gap = auroc_se - auroc_te

    print(f"  TE AUROC: {auroc_te:.4f} [{te_ci[0]:.4f}, {te_ci[1]:.4f}]")
    print(f"  SE AUROC: {auroc_se:.4f} [{se_ci[0]:.4f}, {se_ci[1]:.4f}]")
    print(f"  Gap (SE - TE): {gap:.4f}")

    # Mechanism verification
    mech_ok, diag = verify_mechanism(te_scores, se_scores, correctness, avg_clusters)
    print(f"\n  Mechanism verification: {'PASS' if mech_ok else 'FAIL'}")
    print(f"  Diagnostics: {diag}")

    # Gate decision
    print("\n=== GATE DECISION ===")
    if gap >= CONFIG["gap_threshold"]:
        verdict = "PASS"
        print(f"PASS: gap={gap:.4f} >= {CONFIG['gap_threshold']} — H-E1 CONFIRMED")
    elif gap >= CONFIG["gap_extend_low"]:
        verdict = "EXTEND"
        print(f"EXTEND: gap={gap:.4f} in [{CONFIG['gap_extend_low']}, {CONFIG['gap_threshold']}] — recommend N=500 extension")
    else:
        verdict = "FAIL"
        print(f"FAIL: gap={gap:.4f} < {CONFIG['gap_extend_low']} — H-E1 NOT CONFIRMED")

    if args.smoke_test:
        print("\nSmoke test complete. No crash.")
        return

    # Step 6: Save results + figures
    print("\n[6/6] Saving results and figures...")
    save_results(te_scores, se_scores, correctness, auroc_te, auroc_se,
                 te_ci, se_ci, avg_clusters, out_dir)

    # Bootstrap samples for histogram
    rng = np.random.default_rng(seed)
    def _bootstrap_samples(y_true, y_score, n=1000):
        from sklearn.metrics import roc_auc_score as ras
        pos_idx = np.where(y_true == 1)[0]
        neg_idx = np.where(y_true == 0)[0]
        aurocs = []
        for _ in range(n):
            boot_pos = rng.choice(pos_idx, size=len(pos_idx), replace=True)
            boot_neg = rng.choice(neg_idx, size=len(neg_idx), replace=True)
            idx = np.concatenate([boot_pos, boot_neg])
            try:
                aurocs.append(ras(y_true[idx], y_score[idx]))
            except:
                aurocs.append(0.5)
        return np.array(aurocs)

    bootstrap_te_samples = _bootstrap_samples(y_true, -te_arr)
    bootstrap_se_samples = _bootstrap_samples(y_true, -se_arr)

    plot_figures(te_scores, se_scores, correctness, auroc_te, auroc_se,
                 te_ci, se_ci, bootstrap_te_samples, bootstrap_se_samples, figures_dir)

    print(f"\n=== SUMMARY ===")
    print(f"N={len(questions)}, TE AUROC={auroc_te:.4f}, SE AUROC={auroc_se:.4f}, Gap={gap:.4f}")
    print(f"avg_clusters={avg_clusters:.2f}, accuracy={np.mean(correctness):.3f}")
    print(f"Gate verdict: {verdict}")

    return {
        "auroc_te": auroc_te, "auroc_se": auroc_se, "gap": gap,
        "te_ci": te_ci.tolist(), "se_ci": se_ci.tolist(),
        "avg_clusters": avg_clusters, "verdict": verdict,
        "n": len(questions),
    }


if __name__ == "__main__":
    main()
