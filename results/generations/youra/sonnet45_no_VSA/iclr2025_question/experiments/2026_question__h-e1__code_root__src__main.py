"""Main execution script for h-e1 semantic entropy baseline validation."""

import logging
import sys
import os
import json
from datetime import datetime
import torch

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from data.data_loader import TriviaQALoader
from generation.llama_generator import LLaMAGenerator, CacheManager
from baselines.baseline_scorer import BaselineRunner
from semantic_entropy.entropy_computer import DeBERTaEntailment, SemanticEntropyComputer
from evaluation.metrics import EvaluationRunner

# Setup logging (use parent directory logs)
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'experiment.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def set_reproducibility(seed: int = 42):
    """Set random seeds for reproducibility."""
    import random
    import numpy as np
    
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    
    # Deterministic operations (may reduce performance)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    
    logger.info(f"Set random seed to {seed}")


def main():
    """Run complete experiment pipeline."""
    logger.info("=== Starting h-e1 Semantic Entropy Baseline Validation ===")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    # Set reproducibility
    set_reproducibility(seed=42)
    
    # Configuration
    SUBSET_SIZE = 3000
    NUM_SAMPLES = 10
    
    # Change to parent directory for cache/results
    os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    
    # Step 1: Load and split data
    logger.info("\n=== Step 1: Load and Split Data ===")
    data_loader = TriviaQALoader(subset_size=SUBSET_SIZE)
    dev_samples, test_samples = data_loader.load_and_split()
    data_loader.save_split_metadata(dev_samples, test_samples, "cache/split_metadata.json")
    
    # Use smaller subset for dev (to save time)
    dev_samples = dev_samples[:500]
    test_samples = test_samples[:500]
    logger.info(f"Using {len(dev_samples)} dev, {len(test_samples)} test samples")
    
    # Step 2: Generate answers
    logger.info("\n=== Step 2: Generate Answers ===")
    cache_manager = CacheManager(cache_dir="cache")
    generator = LLaMAGenerator()
    
    logger.info("Generating dev set answers...")
    dev_generations = generator.batch_generate(dev_samples, cache_manager)
    
    logger.info("Generating test set answers...")
    test_generations = generator.batch_generate(test_samples, cache_manager)
    
    # Unload LLaMA to free GPU memory
    del generator.model
    del generator.tokenizer
    torch.cuda.empty_cache()
    logger.info("Unloaded LLaMA model")
    
    # Step 3: Compute baseline scores
    logger.info("\n=== Step 3: Compute Baseline Scores ===")
    baseline_runner = BaselineRunner()
    
    dev_baselines = baseline_runner.compute_all_baselines(dev_generations, dev_samples)
    test_baselines = baseline_runner.compute_all_baselines(test_generations, test_samples)
    
    # Data quality check
    from evaluation.metrics import AUROCComputer, check_answer_correctness
    import numpy as np
    
    auroc_comp = AUROCComputer()
    dev_labels = []
    dev_msp = []
    for sample in dev_samples:
        eid = sample['example_id']
        if eid in dev_generations and eid in dev_baselines['msp']:
            first_ans = dev_generations[eid][0].text
            is_correct = check_answer_correctness(first_ans, sample['ground_truth'])
            dev_labels.append(0 if is_correct else 1)
            dev_msp.append(dev_baselines['msp'][eid])
    
    msp_auroc = auroc_comp.compute_auroc(np.array(dev_labels), np.array(dev_msp))
    logger.info(f"MSP AUROC on dev set: {msp_auroc:.4f}")
    
    if msp_auroc < 0.6:
        logger.error(f"CRITICAL: MSP AUROC ({msp_auroc:.4f}) < 0.6 - data quality issue!")
        logger.error("Stopping experiment as per protocol")
        return False
    
    # Step 4: Compute semantic entropy
    logger.info("\n=== Step 4: Compute Semantic Entropy ===")
    entailment_model = DeBERTaEntailment()
    se_computer = SemanticEntropyComputer(entailment_model)
    
    logger.info("Computing semantic entropy for dev set...")
    dev_se_scores = se_computer.batch_compute(dev_generations, dev_samples)
    
    logger.info("Computing semantic entropy for test set...")
    test_se_scores = se_computer.batch_compute(test_generations, test_samples)
    
    # Step 5: Evaluate on dev set
    logger.info("\n=== Step 5: Evaluate on Dev Set ===")
    evaluator = EvaluationRunner()
    dev_results = evaluator.evaluate_all_methods(
        dev_samples, dev_generations, dev_baselines, dev_se_scores
    )
    
    # Step 6: Evaluate on test set
    logger.info("\n=== Step 6: Evaluate on Test Set ===")
    test_results = evaluator.evaluate_all_methods(
        test_samples, test_generations, test_baselines, test_se_scores
    )
    
    # Step 7: Check gate criteria
    logger.info("\n=== Step 7: Gate Verification ===")
    se_auroc = test_results['semantic_entropy']['auroc']
    msp_auroc_test = test_results['msp']['auroc']
    improvement = se_auroc - msp_auroc_test
    error_reduction = test_results['error_reduction_80']
    
    gate_passed = True
    checks = []
    
    # AC-01: Semantic entropy AUROC >= 0.75
    check1 = se_auroc >= 0.75
    checks.append(f"AC-01 (SE AUROC >= 0.75): {se_auroc:.4f} - {'PASS' if check1 else 'FAIL'}")
    gate_passed &= check1
    
    # AC-02: Improvement >= 0.10
    check2 = improvement >= 0.10
    checks.append(f"AC-02 (Improvement >= 0.10): {improvement:.4f} - {'PASS' if check2 else 'FAIL'}")
    gate_passed &= check2
    
    # AC-03: Error reduction >= 15%
    check3 = error_reduction >= 0.15
    checks.append(f"AC-03 (Error reduction >= 15%): {error_reduction:.2%} - {'PASS' if check3 else 'FAIL'}")
    gate_passed &= check3
    
    # AC-04: All baselines > 0.6
    check4 = all(test_results[m]['auroc'] > 0.6 for m in ['msp', 'token_entropy'])
    checks.append(f"AC-04 (All baselines > 0.6): {'PASS' if check4 else 'FAIL'}")
    gate_passed &= check4
    
    logger.info("\n=== Gate Criteria ===")
    for check in checks:
        logger.info(check)
    
    logger.info(f"\n{'='*50}")
    logger.info(f"MUST_WORK GATE: {'PASSED' if gate_passed else 'FAILED'}")
    logger.info(f"{'='*50}")
    
    # Save results
    final_results = {
        'dev_results': dev_results,
        'test_results': test_results,
        'gate_checks': checks,
        'gate_passed': gate_passed,
        'timestamp': datetime.now().isoformat()
    }
    
    os.makedirs('results', exist_ok=True)
    with open('results/final_results.json', 'w') as f:
        json.dump(final_results, f, indent=2)
    
    logger.info("\n=== Experiment Complete ===")
    logger.info(f"Results saved to results/final_results.json")
    
    return gate_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
