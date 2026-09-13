"""Main pipeline: orchestrates data loading, generation, entropy, consistency."""
import json
import os
import sys
import numpy as np
import torch
from tqdm import tqdm

from config import CONFIG, validate_config
from load_data import load_triviaqa_questions
from generate import load_model, generate_responses
from entropy import compute_token_entropy
from consistency import SemanticConsistency
from checkpoint import CheckpointManager


def process_question(
    question_id: str,
    question: str,
    model,
    tokenizer,
    consistency_calc: SemanticConsistency,
    cfg
) -> dict:
    """Process single question: generate responses, compute entropy + consistency."""
    try:
        responses = generate_responses(
            model, tokenizer, question,
            n_samples=cfg.n_samples,
            temperature=cfg.temperature,
            top_p=cfg.top_p,
            max_new_tokens=cfg.max_new_tokens,
            seed=cfg.seed
        )

        # Compute entropy for each response
        entropies = []
        for r in responses:
            h = compute_token_entropy(r["scores"])
            entropies.append(h)
            del r["scores"]  # free memory

        torch.cuda.empty_cache()

        mean_entropy = np.nanmean(entropies) if entropies else float('nan')

        # Compute consistency from response texts
        texts = [r["text"] for r in responses if r["text"].strip()]
        consistency = consistency_calc.compute(texts)

        success = not (np.isnan(mean_entropy) or np.isnan(consistency))

        return {
            "question_id": question_id,
            "entropy": float(mean_entropy),
            "consistency": float(consistency),
            "success": success,
            "n_responses": len(texts)
        }

    except torch.cuda.OutOfMemoryError:
        torch.cuda.empty_cache()
        return {
            "question_id": question_id,
            "entropy": float('nan'),
            "consistency": float('nan'),
            "success": False,
            "n_responses": 0
        }


def evaluate_existence(results: list[dict]) -> dict:
    """Compute success metrics."""
    successful = [r for r in results if r["success"]]
    success_rate = len(successful) / len(results) * 100 if results else 0

    entropies = [r["entropy"] for r in successful]
    consistencies = [r["consistency"] for r in successful]

    return {
        "success_rate": success_rate,
        "n_successful": len(successful),
        "n_total": len(results),
        "entropy_mean": float(np.mean(entropies)) if entropies else float('nan'),
        "entropy_std": float(np.std(entropies)) if entropies else float('nan'),
        "entropy_min": float(np.min(entropies)) if entropies else float('nan'),
        "entropy_max": float(np.max(entropies)) if entropies else float('nan'),
        "consistency_mean": float(np.mean(consistencies)) if consistencies else float('nan'),
        "consistency_std": float(np.std(consistencies)) if consistencies else float('nan'),
        "consistency_min": float(np.min(consistencies)) if consistencies else float('nan'),
        "consistency_max": float(np.max(consistencies)) if consistencies else float('nan'),
        "gate_pass": success_rate >= 99.0 and (np.std(entropies) > 0 if entropies else False) and (np.std(consistencies) > 0 if consistencies else False)
    }


def run_pipeline():
    """Main pipeline execution."""
    print("Loading config...")
    cfg = CONFIG
    validate_config(cfg)

    os.makedirs(cfg.output_dir, exist_ok=True)
    checkpoint_path = os.path.join(cfg.output_dir, "checkpoint.json")
    results_path = os.path.join(cfg.output_dir, cfg.results_file)

    print(f"Loading questions (limit={cfg.n_questions})...")
    questions = load_triviaqa_questions(
        split=cfg.dataset_split,
        limit=cfg.n_questions,
        seed=cfg.dataset_seed
    )
    print(f"Loaded {len(questions)} questions")

    print("Loading model...")
    model, tokenizer = load_model(cfg.model_name, cfg.hf_token, cfg.torch_dtype)
    print("Model loaded")

    print("Loading embedding model...")
    consistency_calc = SemanticConsistency(cfg.embedding_model)
    print("Embedding model loaded")

    checkpoint_mgr = CheckpointManager(checkpoint_path, cfg.checkpoint_every)
    state = checkpoint_mgr.load()
    results = state["results"]
    start_idx = state["last_idx"] + 1

    if start_idx > 0:
        print(f"Resuming from checkpoint at index {start_idx}")

    done_ids = {r["question_id"] for r in results}

    for idx in tqdm(range(start_idx, len(questions)), desc="Processing"):
        q = questions[idx]
        if q["question_id"] in done_ids:
            continue

        result = process_question(
            q["question_id"], q["question"],
            model, tokenizer, consistency_calc, cfg
        )
        results.append(result)

        if checkpoint_mgr.should_save(idx):
            checkpoint_mgr.save(idx, results)
            print(f"\nCheckpoint saved at {idx+1}/{len(questions)}")

    # Final save
    checkpoint_mgr.save(len(questions) - 1, results)

    # Compute metrics
    metrics = evaluate_existence(results)

    # Save final results
    output = {
        "config": {
            "model": cfg.model_name,
            "n_samples": cfg.n_samples,
            "temperature": cfg.temperature,
            "n_questions": len(questions)
        },
        "metrics": metrics,
        "results": results
    }

    with open(results_path, "w") as f:
        json.dump(output, f, indent=2)

    print("\n=== RESULTS ===")
    print(f"Success rate: {metrics['success_rate']:.2f}%")
    print(f"Entropy: mean={metrics['entropy_mean']:.4f}, std={metrics['entropy_std']:.4f}")
    print(f"Consistency: mean={metrics['consistency_mean']:.4f}, std={metrics['consistency_std']:.4f}")
    print(f"Gate PASS: {metrics['gate_pass']}")

    return metrics


if __name__ == "__main__":
    metrics = run_pipeline()
    sys.exit(0 if metrics["gate_pass"] else 1)
