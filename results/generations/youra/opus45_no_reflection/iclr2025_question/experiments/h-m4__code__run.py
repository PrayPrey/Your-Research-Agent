"""H-M4 Orchestration: Probe vs Output-Level Baselines Comparison."""
import json
import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import HM4Config
from reuse_probe import get_probe_scores
from generate import load_model, run_generation_batch
from baselines import compute_all_baselines
from evaluate import compute_labels, compute_auroc_all, compute_deltas, check_gate, get_roc_curves
from visualize import (
    plot_gate_comparison, plot_roc_overlay,
    plot_confidence_distributions, plot_score_scatter
)


def load_validation_questions(n_val: int = 1700) -> list:
    """Load TriviaQA validation questions."""
    from datasets import load_dataset
    print(f"Loading TriviaQA validation set ({n_val} samples)...")
    dataset = load_dataset("trivia_qa", "rc.nocontext", split=f"validation[:{n_val}]")
    questions = []
    for i, ex in enumerate(dataset):
        questions.append({
            "id": i,
            "question_id": ex.get("question_id", str(i)),
            "question": ex["question"],
            "answer": ex["answer"]
        })
    print(f"Loaded {len(questions)} questions")
    return questions


def main(hypothesis_folder: str = None, skip_generation: bool = False) -> dict:
    """Run H-M4 experiment."""
    cfg = HM4Config()

    # Resolve paths
    if hypothesis_folder:
        base_path = Path(hypothesis_folder).resolve()
    else:
        base_path = Path(__file__).parent.parent.resolve()

    code_path = base_path / "code"
    os.chdir(code_path)

    # Output paths
    figures_dir = code_path / cfg.figures_dir
    figures_dir.mkdir(exist_ok=True)
    results_path = code_path / cfg.results_json

    print("=" * 60)
    print("H-M4: Probe vs Output-Level Baselines Comparison")
    print("=" * 60)

    # Step 1: Retrain probe (identical to H-M3)
    print("\n[1/5] Retraining H-M3 probe...")
    probe_result = get_probe_scores(cfg.h_m1_cache_folder, cfg.h_m3_code_path, cfg.seed)
    probe_scores = probe_result["probe_scores"]
    probe_auroc_sanity = probe_result["probe_auroc"]
    print(f"  Probe retrained. AUROC sanity: {probe_auroc_sanity:.4f}")

    # Check if cached generation exists
    gen_cache_path = code_path / "gen_outputs.json"
    if skip_generation and gen_cache_path.exists():
        print("\n[2/5] Loading cached generation outputs...")
        import torch
        with open(gen_cache_path, "r") as f:
            gen_data = json.load(f)
        gen_outputs = gen_data["outputs"]
        # Convert scores back to tensors
        for out in gen_outputs:
            out["scores"] = torch.tensor(out["scores"])
            out["generated_ids"] = torch.tensor(out["generated_ids"])
    else:
        # Step 2: Load model
        print("\n[2/5] Loading Llama-3-8B-Instruct...")
        model, tokenizer = load_model(cfg.model_id)

        # Step 3: Load questions
        print("\n[3/5] Loading validation questions...")
        questions = load_validation_questions(cfg.n_val)

        # Step 4: Generate with scores
        print("\n[4/5] Running generation with scores...")
        gen_outputs = run_generation_batch(model, tokenizer, questions, cfg.max_new_tokens)

        # Cache for resume
        print("  Caching generation outputs...")
        cache_data = {
            "outputs": [
                {
                    "id": out["id"],
                    "question": out["question"],
                    "gold_answers": out["gold_answers"],
                    "text": out["text"],
                    "scores": out["scores"].cpu().tolist(),
                    "generated_ids": out["generated_ids"].cpu().tolist()
                }
                for out in gen_outputs
            ]
        }
        with open(gen_cache_path, "w") as f:
            json.dump(cache_data, f)

        # Free model memory
        del model
        import torch
        torch.cuda.empty_cache()

    # Step 5: Compute baselines
    print("\n[5/5] Computing baselines and evaluation...")
    baselines = compute_all_baselines(gen_outputs)
    entropy_scores = baselines["entropy_scores"]
    nll_scores = baselines["nll_scores"]

    # Compute labels from live generation
    labels = compute_labels(gen_outputs)
    print(f"  Labels: {labels.sum()} correct / {len(labels)} total ({labels.mean()*100:.1f}%)")

    # Compute AUROCs
    aurocs = compute_auroc_all(probe_scores, entropy_scores, nll_scores, labels)
    print(f"  Probe AUROC:    {aurocs['probe_auroc']:.4f}")
    print(f"  Entropy AUROC:  {aurocs['entropy_auroc']:.4f}")
    print(f"  NLL AUROC:      {aurocs['nll_auroc']:.4f}")

    # Compute deltas
    deltas = compute_deltas(aurocs)
    print(f"  Delta (Probe-Entropy): {deltas['delta_entropy']:.4f}")
    print(f"  Delta (Probe-NLL):     {deltas['delta_nll']:.4f}")

    # Gate check
    gate_result = check_gate(deltas, cfg.delta_gate)
    print(f"\n  Gate threshold: {cfg.delta_gate}")
    print(f"  Gate pass (Entropy): {gate_result['gate_entropy_pass']}")
    print(f"  Gate pass (NLL):     {gate_result['gate_nll_pass']}")
    print(f"  Overall gate:        {'PASS' if gate_result['gate_pass'] else 'FAIL'}")

    # Generate visualizations
    print("\nGenerating visualizations...")
    plot_gate_comparison(aurocs, cfg.delta_gate, str(code_path / cfg.gate_comparison_fig))
    curves = get_roc_curves(labels, probe_scores, entropy_scores, nll_scores)
    plot_roc_overlay(curves, str(code_path / cfg.roc_curve_fig))
    plot_confidence_distributions(labels, probe_scores, entropy_scores, str(code_path / cfg.dist_fig))
    plot_score_scatter(probe_scores, entropy_scores, labels, str(code_path / cfg.scatter_fig))
    print("  Figures saved to figures/")

    # Compile results
    results = {
        "hypothesis_id": "h-m4",
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "probe_auroc": float(aurocs["probe_auroc"]),
            "entropy_auroc": float(aurocs["entropy_auroc"]),
            "nll_auroc": float(aurocs["nll_auroc"]),
            "delta_entropy": float(deltas["delta_entropy"]),
            "delta_nll": float(deltas["delta_nll"])
        },
        "gate": {
            "type": "SHOULD_WORK",
            "threshold": cfg.delta_gate,
            "gate_entropy_pass": gate_result["gate_entropy_pass"],
            "gate_nll_pass": gate_result["gate_nll_pass"],
            "gate_pass": gate_result["gate_pass"],
            "result": "PASS" if gate_result["gate_pass"] else "FAIL"
        },
        "dataset": {
            "n_val": len(labels),
            "n_correct": int(labels.sum()),
            "accuracy": float(labels.mean())
        },
        "figures": [
            cfg.gate_comparison_fig,
            cfg.roc_curve_fig,
            cfg.dist_fig,
            cfg.scatter_fig
        ]
    }

    # Save results
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_path}")

    print("\n" + "=" * 60)
    print(f"H-M4 COMPLETE: Gate {'PASS' if gate_result['gate_pass'] else 'FAIL'}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hypothesis-folder", type=str, default=None)
    parser.add_argument("--skip-generation", action="store_true")
    args = parser.parse_args()
    main(args.hypothesis_folder, args.skip_generation)
