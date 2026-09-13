"""Main experiment orchestrator for h-e1: KLE vs SE comparison."""

import torch
import numpy as np
import random
import os
import sys
import json
from tqdm import tqdm

from config import CONFIG
from data.pipeline import TriviaQALoader, AnswerSampler, Embedder
from stratification.density import compute_boundary_density, stratify_terciles
from uncertainty.semantic_entropy import SemanticEntropy
from uncertainty.kernel_entropy import KernelEntropy
from oracle.search import OracleSearch
from evaluation.metrics import StratumEval, spearman_correlation


def set_seed(seed):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def run_experiment(config):
    """Run the full experiment pipeline."""

    print("\n" + "="*80)
    print("h-e1: Kernel Language Entropy vs Semantic Entropy")
    print("="*80)

    # Initialize
    set_seed(config["random_seed"])
    device = config["models"]["qa_model"]["device"]

    # Step 1: Load TriviaQA
    print("\n=== Step 1: Load TriviaQA ===")
    loader = TriviaQALoader(
        cache_dir=config["dataset"]["cache_dir"],
        seed=config["random_seed"]
    )

    val_data = loader.load_validation(config["dataset"]["validation_size"])

    # Split into dev (80%) and holdout (20%) for oracle search
    split_idx = int(0.8 * len(val_data))
    dev_data = val_data[:split_idx]
    holdout_data = val_data[split_idx:]

    print(f"Dev: {len(dev_data)}, Holdout: {len(holdout_data)}")

    # Step 2: Sample answers
    print("\n=== Step 2: Sample Answers ===")
    sampler = AnswerSampler(
        model_name=config["models"]["qa_model"]["name"],
        device=device,
        cache_dir=config["cache"]["answers_dir"]
    )

    dev_questions = [d['question'] for d in dev_data]
    dev_answers = sampler.sample(
        dev_questions,
        n=config["sampling"]["n_samples"],
        temp=config["sampling"]["temperature"],
        batch=config["sampling"]["batch_size"]
    )

    holdout_questions = [d['question'] for d in holdout_data]
    holdout_answers = sampler.sample(
        holdout_questions,
        n=config["sampling"]["n_samples"],
        temp=config["sampling"]["temperature"],
        batch=config["sampling"]["batch_size"]
    )

    # Step 3: Extract embeddings
    print("\n=== Step 3: Extract Embeddings ===")
    embedder = Embedder(
        model_name=config["models"]["embedding_model"]["name"],
        device=device,
        batch_size=config["models"]["embedding_model"]["batch_size"]
    )

    print("Embedding dev answers...")
    dev_embeddings = []
    dev_similarities = []
    for answers in tqdm(dev_answers):
        emb = embedder.embed(answers)
        S = embedder.similarity_matrix(emb)
        dev_embeddings.append(emb)
        dev_similarities.append(S)

    print("Embedding holdout answers...")
    holdout_embeddings = []
    holdout_similarities = []
    for answers in tqdm(holdout_answers):
        emb = embedder.embed(answers)
        S = embedder.similarity_matrix(emb)
        holdout_embeddings.append(emb)
        holdout_similarities.append(S)

    # Compute ground truth labels (correctness)
    dev_labels = np.array([
        int(any(loader.check_correctness(ans, d['answer']) for ans in answers))
        for d, answers in zip(dev_data, dev_answers)
    ])

    holdout_labels = np.array([
        int(any(loader.check_correctness(ans, d['answer']) for ans in answers))
        for d, answers in zip(holdout_data, holdout_answers)
    ])

    print(f"Dev correctness: {dev_labels.mean():.2%}")
    print(f"Holdout correctness: {holdout_labels.mean():.2%}")

    # Step 4: Oracle search
    print("\n=== Step 4: Oracle Hyperparameter Search ===")
    oracle = OracleSearch(dev_data, dev_labels)

    epsilon_star, se_auroc = oracle.search_epsilon(
        config["uncertainty"]["se"]["epsilon_grid"],
        dev_similarities
    )

    sigma_star, kle_auroc = oracle.search_sigma(
        config["uncertainty"]["kle"]["sigma_grid"],
        dev_similarities
    )

    # Gate 4: Oracle pre-gate
    if not oracle.pre_gate(kle_auroc, se_auroc, config["gates"]["oracle_pre_gate_threshold"]):
        print("\n❌ EXPERIMENT FAILED: Oracle pre-gate not satisfied")
        print("ROUTE_TO_PHASE_0: Effect size too small")
        return {
            'gate_result': 'FAIL',
            'gate_type': 'MUST_WORK',
            'reason': 'Oracle improvement < 0.03 AUROC',
            'oracle_improvement': kle_auroc - se_auroc
        }

    # Step 5: Boundary density stratification
    print("\n=== Step 5: Boundary Density Stratification ===")
    holdout_densities = np.array([
        compute_boundary_density(S, epsilon_star, config["stratification"]["window"])
        for S in holdout_similarities
    ])

    strata = stratify_terciles(holdout_densities)

    print(f"LOW stratum: {strata['LOW'].sum()} questions")
    print(f"MID stratum: {strata['MID'].sum()} questions")
    print(f"HIGH stratum: {strata['HIGH'].sum()} questions")

    # Step 6: Uncertainty quantification
    print("\n=== Step 6: Uncertainty Quantification ===")
    se = SemanticEntropy(epsilon_star)
    kle = KernelEntropy(sigma_star)

    holdout_se = []
    holdout_kle = []

    print("Computing SE and KLE for holdout set...")
    for S in tqdm(holdout_similarities):
        h_se = se.compute(S)
        h_kle, _ = kle.compute(S)
        holdout_se.append(h_se)
        holdout_kle.append(h_kle)

    holdout_se = np.array(holdout_se)
    holdout_kle = np.array(holdout_kle)

    # Step 7: Evaluation
    print("\n=== Step 7: Evaluation ===")
    evaluator = StratumEval(holdout_se, holdout_kle, holdout_labels)

    results = {}
    for stratum_name in ['LOW', 'MID', 'HIGH']:
        print(f"\n{stratum_name} Stratum:")
        result = evaluator.eval_stratum(strata[stratum_name])
        results[stratum_name] = result

        print(f"  SE AUROC: {result['auroc_se']:.4f}")
        print(f"  KLE AUROC: {result['auroc_kle']:.4f}")
        print(f"  Divergence: {result['divergence']:.4f}")
        print(f"  p-value: {result['p_value']:.4f}")

    # Gate 7: Primary success criterion
    high_div = results['HIGH']['divergence']
    high_p = results['HIGH']['p_value']

    primary_pass = (high_div >= config["gates"]["primary_auroc_threshold"]) and \
                   (high_p < config["evaluation"]["significance_alpha"])

    print(f"\n=== Gate 7: Primary Success Criterion ===")
    print(f"HIGH stratum divergence: {high_div:.4f} (threshold: {config['gates']['primary_auroc_threshold']})")
    print(f"p-value: {high_p:.4f} (alpha: {config['evaluation']['significance_alpha']})")
    print(f"Result: {'PASS ✅' if primary_pass else 'FAIL ❌'}")

    # Spearman correlation
    auroc_divergences = np.array([
        evaluator.eval_stratum(np.array([True] * len(holdout_labels)))['divergence']
    ])

    # Save results
    results_summary = {
        'hypothesis': 'h-e1',
        'oracle': {
            'epsilon_star': epsilon_star,
            'sigma_star': sigma_star,
            'se_auroc': float(se_auroc),
            'kle_auroc': float(kle_auroc),
            'improvement': float(kle_auroc - se_auroc)
        },
        'strata_results': {
            k: {kk: float(vv) if isinstance(vv, (np.number, np.ndarray)) else vv
                for kk, vv in v.items()}
            for k, v in results.items()
        },
        'gate_result': {
            'primary_pass': primary_pass,
            'high_divergence': float(high_div),
            'high_p_value': float(high_p),
            'verdict': 'PASS' if primary_pass else 'PARTIAL'
        }
    }

    results_path = os.path.join(CONFIG["RESULTS_DIR"], "h-e1_results.json")
    with open(results_path, 'w') as f:
        json.dump(results_summary, f, indent=2)

    print(f"\nResults saved to: {results_path}")

    return results_summary


def main():
    """Main entry point."""
    try:
        results = run_experiment(CONFIG)

        # Check gate
        if results.get('gate_result') == 'FAIL':
            print("\n❌ EXPERIMENT FAILED")
            return False

        gate_verdict = results['gate_result']['verdict']

        if gate_verdict == 'PASS':
            print("\n✅ EXPERIMENT PASSED")
            return True
        else:
            print("\n⚠️  EXPERIMENT PARTIAL")
            return False

    except Exception as e:
        print(f"\n❌ EXPERIMENT ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
