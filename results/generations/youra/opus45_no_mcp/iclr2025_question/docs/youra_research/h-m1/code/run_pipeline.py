"""Main pipeline: generate -> entropy -> correctness -> stats -> figures"""
import json
import os
import sys
import time
import argparse

import config
from load_data import load_triviaqa_val
from generate import load_model, generate_responses
from entropy import compute_token_entropy
from correctness import evaluate_correctness, majority_answer
from stats import compute_correlation
from checkpoint import CheckpointManager
from visualize import plot_gate_metrics, plot_entropy_distribution, plot_roc_curve


def run(limit: int = None, resume: bool = True):
    """Run full pipeline on TriviaQA validation set."""
    print(f"[Pipeline] Starting H-M1 entropy-correctness experiment")
    start_time = time.time()

    # Load data
    print(f"[Data] Loading TriviaQA validation set...")
    questions = load_triviaqa_val(limit)
    print(f"[Data] Loaded {len(questions)} questions")

    # Load model
    print(f"[Model] Loading {config.MODEL_NAME}...")
    model, tokenizer = load_model()
    print(f"[Model] Loaded successfully")

    # Checkpoint
    ckpt = CheckpointManager(config.CHECKPOINT_PATH, config.CHECKPOINT_EVERY)
    if resume:
        ckpt_data = ckpt.load()
        results = ckpt_data.get("results", [])
        done_ids = {r["qid"] for r in results}
        print(f"[Checkpoint] Resuming from {len(results)} completed questions")
    else:
        results = []
        done_ids = set()

    # Process questions
    for idx, q in enumerate(questions):
        if q["qid"] in done_ids:
            continue

        try:
            # Generate responses
            responses = generate_responses(model, tokenizer, q["question"])

            # Compute entropy for each response, average
            entropies = [compute_token_entropy(r["scores"]) for r in responses]
            mean_entropy = sum(entropies) / len(entropies) if entropies else 0.0

            # Evaluate correctness
            texts = [r["text"] for r in responses]
            maj = majority_answer(texts)
            correct = evaluate_correctness(maj, q["answer_aliases"])

            results.append({
                "qid": q["qid"],
                "question": q["question"][:100],  # truncate for storage
                "entropy": mean_entropy,
                "correct": correct,
                "majority_answer": maj[:100]
            })

            if (idx + 1) % 10 == 0:
                elapsed = time.time() - start_time
                rate = (len(results) - len(done_ids)) / elapsed if elapsed > 0 else 0
                eta = (len(questions) - len(results)) / rate if rate > 0 else 0
                print(f"[Progress] {len(results)}/{len(questions)} | "
                      f"Rate: {rate:.2f} q/s | ETA: {eta/60:.1f} min")

            if ckpt.should_save(idx):
                ckpt.save(idx, results)
                print(f"[Checkpoint] Saved at idx {idx}")

        except Exception as e:
            print(f"[Error] Question {q['qid']}: {e}")
            continue

    # Final save
    ckpt.save(len(questions), results)

    # Compute statistics
    print(f"[Stats] Computing correlation statistics...")
    entropies = [r["entropy"] for r in results]
    correctness = [r["correct"] for r in results]
    stats_result = compute_correlation(entropies, correctness)

    # Print gate results
    print(f"\n{'='*50}")
    print(f"GATE RESULTS (MUST_WORK)")
    print(f"{'='*50}")
    print(f"p-value:         {stats_result['p_value']:.6f} (target: < 0.05) "
          f"{'PASS' if stats_result['p_value'] < 0.05 else 'FAIL'}")
    print(f"AUROC:           {stats_result['auroc']:.4f} (target: > 0.55) "
          f"{'PASS' if stats_result['auroc'] > 0.55 else 'FAIL'}")
    print(f"Direction:       mean_incorrect={stats_result['mean_incorrect']:.4f} > "
          f"mean_correct={stats_result['mean_correct']:.4f} "
          f"{'PASS' if stats_result['mean_incorrect'] > stats_result['mean_correct'] else 'FAIL'}")
    print(f"Cohen's d:       {stats_result['cohens_d']:.4f}")
    print(f"Pearson r:       {stats_result['pearson_r']:.4f}")
    print(f"{'='*50}")

    # Gate verdict
    gate_pass = (stats_result['p_value'] < config.P_VALUE_TARGET and
                 stats_result['auroc'] > config.AUROC_TARGET and
                 stats_result['mean_incorrect'] > stats_result['mean_correct'])
    print(f"GATE VERDICT:    {'PASS' if gate_pass else 'FAIL'}")
    print(f"{'='*50}\n")

    # Generate figures
    print(f"[Figures] Generating visualizations...")
    os.makedirs(config.FIGURES_DIR, exist_ok=True)

    plot_gate_metrics(stats_result['auroc'], config.AUROC_TARGET,
                     stats_result['p_value'], f"{config.FIGURES_DIR}/gate_metrics.png")
    plot_entropy_distribution(entropies, correctness,
                             f"{config.FIGURES_DIR}/entropy_distribution.png")
    plot_roc_curve(entropies, correctness, f"{config.FIGURES_DIR}/roc_curve.png")

    # Save results
    os.makedirs(os.path.dirname(config.OUTPUT_PATH), exist_ok=True)
    output = {
        "hypothesis": "H-M1",
        "gate_type": "MUST_WORK",
        "gate_result": "PASS" if gate_pass else "FAIL",
        "stats": stats_result,
        "config": {
            "model": config.MODEL_NAME,
            "n_questions": len(results),
            "n_samples": config.NUM_RESPONSES,
            "temperature": config.TEMPERATURE
        },
        "results": results,
        "runtime_seconds": time.time() - start_time
    }

    with open(config.OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"[Output] Saved results to {config.OUTPUT_PATH}")

    # Also save to CSV
    csv_path = "outputs/results.csv"
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w") as f:
        f.write("qid,entropy,correct\n")
        for r in results:
            f.write(f"{r['qid']},{r['entropy']},{r['correct']}\n")
    print(f"[Output] Saved CSV to {csv_path}")

    print(f"[Pipeline] Complete in {time.time() - start_time:.1f}s")

    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Limit questions")
    parser.add_argument("--no-resume", action="store_true", help="Start fresh")
    args = parser.parse_args()

    run(limit=args.limit, resume=not args.no_resume)
