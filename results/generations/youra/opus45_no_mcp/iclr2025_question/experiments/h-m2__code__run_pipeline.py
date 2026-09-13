"""H-M2 Pipeline: Semantic Consistency as Hallucination Predictor"""
import json
import os
import time
from datetime import datetime

import config
from load_data import load_triviaqa_val
from generate import load_model, generate_responses
from entropy import compute_token_entropy
from consistency import SemanticConsistencyScorer
from correctness import evaluate_correctness, majority_answer
from checkpoint import CheckpointManager
from stats import compute_correlation, pearson_entropy_consistency
import visualize


def run(limit: int = None, resume: bool = True) -> dict:
    """Run H-M2 pipeline: generate -> entropy + consistency -> correctness -> stats -> figures."""
    limit = limit or config.N_QUESTIONS
    print(f"[H-M2] Starting pipeline with {limit} questions...")

    # Load data
    questions = load_triviaqa_val(limit)
    print(f"[H-M2] Loaded {len(questions)} questions")

    # Load checkpoint
    ckpt_manager = CheckpointManager(config.CHECKPOINT_PATH, config.CHECKPOINT_EVERY)
    ckpt = ckpt_manager.load() if resume else {"last_idx": -1, "results": []}
    results = ckpt["results"]
    start_idx = ckpt["last_idx"] + 1
    print(f"[H-M2] Resuming from index {start_idx}")

    # Load model
    print("[H-M2] Loading Llama-2-7B-chat...")
    model, tokenizer = load_model()
    print("[H-M2] Model loaded")

    # Load consistency scorer
    print(f"[H-M2] Loading embedding model: {config.EMBEDDING_MODEL}")
    scorer = SemanticConsistencyScorer()
    print("[H-M2] Embedding model loaded")

    # Process questions
    for idx in range(start_idx, len(questions)):
        q = questions[idx]
        t0 = time.time()

        # Generate 10 responses
        responses = generate_responses(model, tokenizer, q["question"])
        texts = [r["text"] for r in responses]

        # Compute entropy (mean across 10 responses)
        entropies = [compute_token_entropy(r["scores"]) for r in responses]
        mean_entropy = sum(entropies) / len(entropies)

        # Compute consistency (pairwise cosine sim)
        consistency = scorer.compute_consistency(texts)

        # Correctness via majority answer
        maj = majority_answer(texts)
        correct = evaluate_correctness(maj, q["answer_aliases"])

        result = {
            "qid": q["qid"],
            "question": q["question"][:100],  # Truncate for storage
            "entropy": mean_entropy,
            "consistency": consistency,
            "correct": correct,
            "majority_answer": maj[:100]  # Truncate
        }
        results.append(result)

        elapsed = time.time() - t0
        print(f"[H-M2] Q{idx+1}/{len(questions)}: entropy={mean_entropy:.4f}, "
              f"consistency={consistency:.4f}, correct={correct}, time={elapsed:.1f}s")

        # Checkpoint
        if ckpt_manager.should_save(idx):
            ckpt_manager.save(idx, results)
            print(f"[H-M2] Checkpoint saved at index {idx}")

    # Final checkpoint
    ckpt_manager.save(len(questions) - 1, results)

    # Compute statistics
    print("[H-M2] Computing statistics...")
    consistencies = [r["consistency"] for r in results]
    entropies = [r["entropy"] for r in results]
    correctness = [r["correct"] for r in results]

    stats_result = compute_correlation(consistencies, correctness)
    stats_result["pearson_r_entropy_consistency"] = pearson_entropy_consistency(entropies, consistencies)
    stats_result["n_questions"] = len(results)

    print(f"[H-M2] Stats: p={stats_result['p_value']:.4f}, AUROC={stats_result['auroc']:.4f}, "
          f"Cohen's d={stats_result['cohens_d']:.4f}")

    # Generate figures
    print("[H-M2] Generating figures...")
    os.makedirs(config.FIGURES_DIR, exist_ok=True)
    visualize.plot_gate_metrics(
        stats_result["auroc"], config.AUROC_TARGET, stats_result["p_value"],
        os.path.join(config.FIGURES_DIR, "gate_metrics.png")
    )
    visualize.plot_consistency_distribution(
        consistencies, correctness,
        os.path.join(config.FIGURES_DIR, "consistency_dist.png")
    )
    visualize.plot_roc_curve(
        consistencies, correctness,
        os.path.join(config.FIGURES_DIR, "roc_curve.png")
    )
    visualize.plot_entropy_vs_consistency(
        entropies, consistencies, correctness,
        os.path.join(config.FIGURES_DIR, "entropy_vs_consistency.png")
    )
    print("[H-M2] Figures saved")

    # Write final results
    output = {
        "hypothesis": "h-m2",
        "description": "Semantic Consistency as Hallucination Predictor",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "model": config.MODEL_NAME,
            "embedding_model": config.EMBEDDING_MODEL,
            "n_questions": len(results),
            "n_responses": config.NUM_RESPONSES,
            "temperature": config.TEMPERATURE,
            "seed": config.SEED
        },
        "stats": stats_result,
        "results": results
    }

    os.makedirs(os.path.dirname(config.OUTPUT_PATH), exist_ok=True)
    with open(config.OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"[H-M2] Results saved to {config.OUTPUT_PATH}")

    # Gate check
    gate_pass = (
        stats_result["p_value"] < config.P_VALUE_TARGET and
        stats_result["auroc"] > config.AUROC_TARGET and
        stats_result["mean_correct"] > stats_result["mean_incorrect"]
    )
    print(f"[H-M2] Gate check: {'PASS' if gate_pass else 'SHOULD_WORK-FAIL'}")

    return stats_result


if __name__ == "__main__":
    run()
