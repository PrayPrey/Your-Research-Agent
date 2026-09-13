"""
Main Experiment Runner for h-m1: Phase 1 Execution-Heavy Weight Validation
Task: M-1
Hypothesis: h-m1
"""

import os
import sys
import torch
import random
import numpy as np
from datetime import datetime
import importlib.util

# Setup paths - CRITICAL: Import h-m1 modules BEFORE adding h-e1 to path
_script_dir = os.path.dirname(os.path.abspath(__file__))
_h_e1_dir = os.path.abspath(os.path.join(_script_dir, '../../h-e1/code'))

# Step 1: Add ONLY h-m1 to path first
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

# Step 2: Import h-m1 specific modules IMMEDIATELY (before h-e1 is added)
from config.phase1_config import Phase1ExperimentConfig
from models.phase1_tri_modal_aggregator import Phase1AnalysisTriModalAggregator
import evaluation.phase1_metrics as phase1_metrics_module
Phase1Analyzer = phase1_metrics_module.Phase1Analyzer
from utils.checkpoint_logger import CheckpointLogger
from utils.visualization import (
    plot_weight_trajectory, plot_pass_at_1_trajectory,
    plot_phase_improvement_rates, plot_gate_metrics
)

# Import Phase1PPOTrainer using direct file loading
_phase1_trainer_path = os.path.join(_script_dir, "train", "phase1_ppo_trainer.py")
_spec = importlib.util.spec_from_file_location("phase1_ppo_trainer_module", _phase1_trainer_path)
_phase1_module = importlib.util.module_from_spec(_spec)
sys.modules['phase1_ppo_trainer_module'] = _phase1_module
_spec.loader.exec_module(_phase1_module)
Phase1PPOTrainer = _phase1_module.Phase1PPOTrainer

# Step 3: NOW add h-e1 to path (h-m1 modules already imported)
if _h_e1_dir not in sys.path:
    sys.path.insert(1, _h_e1_dir)

# Step 4: Import h-e1 base components
from data.dataset import CodeGenerationDataset
from models.feedback_collectors import FeedbackCollector
# Import evaluator explicitly from h-e1 (not from h-m1's evaluation package)
import sys as _sys_temp
_evaluator_path = os.path.join(_h_e1_dir, "evaluation", "evaluator.py")
_eval_spec = importlib.util.spec_from_file_location("h_e1_evaluator", _evaluator_path)
_eval_module = importlib.util.module_from_spec(_eval_spec)
_eval_spec.loader.exec_module(_eval_module)
CodeEvaluator = _eval_module.CodeEvaluator

print(f"="*70)
print("H-M1: Phase 1 Execution-Heavy Weight Validation")
print(f"="*70)
print(f"Start time: {datetime.now().isoformat()}")
print()


def set_seed(seed: int):
    """Set random seed for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True


def main():
    print("=" * 70)
    print("H-M1: Phase 1 Execution-Heavy Weight Validation")
    print("=" * 70)
    print(f"Start time: {datetime.now().isoformat()}")
    print()

    # 1. Load configuration
    config = Phase1ExperimentConfig()
    set_seed(config.seed)

    print(f"✓ Configuration loaded")
    print(f"  Experiment: {config.experiment_name}")
    print(f"  Total episodes: {config.ppo.total_steps}")
    print(f"  Checkpoints: {config.phase1.checkpoints}")
    print()

    # 2. Setup dataset (reuse h-e1)
    print("📊 Loading dataset...")
    from data.dataset import create_dataloaders
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(config.model.model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    train_loader, val_loader, test_loader = create_dataloaders(
        tokenizer=tokenizer,
        cache_dir=config.data.cache_dir,
        batch_size=config.ppo.batch_size,
        seed=config.seed
    )

    print(f"✓ Dataset loaded")
    print(f"  Train: {len(train_loader.dataset)} samples")
    print(f"  Val: {len(val_loader.dataset)} samples")
    print()

    # 3. Initialize Phase 1 aggregator
    print("🔧 Initializing Phase 1 Tri-Modal Aggregator...")
    aggregator_config = config.aggregator
    aggregator = Phase1AnalysisTriModalAggregator(
        config=aggregator_config.__dict__ if hasattr(aggregator_config, '__dict__') else aggregator_config,
        phase1_checkpoints=config.phase1.checkpoints[:4]  # Only Phase 1 checkpoints
    )
    print(f"✓ Aggregator initialized")
    print()

    # 4. Initialize feedback collector (reuse h-e1)
    print("🔍 Initializing Feedback Collector...")
    feedback_collector = FeedbackCollector(config.feedback)
    print(f"✓ Feedback collector initialized")
    print()

    # 5. Initialize Phase 1 PPO Trainer
    print("🚀 Initializing Phase 1 PPO Trainer...")
    trainer_config = {
        'learning_rate': config.ppo.learning_rate,
        'checkpoint_dir': config.checkpoint_dir,
        'device': config.device,
        **config.ppo.__dict__
    }

    trainer = Phase1PPOTrainer(
        model_name=config.model.model_name,
        aggregator=aggregator,
        feedback_collector=feedback_collector,
        config=trainer_config
    )
    print(f"✓ Trainer initialized")
    print()

    # 6. Run training with checkpoints
    print("=" * 70)
    print("TRAINING START")
    print("=" * 70)
    print()

    training_history = trainer.train(
        train_dataloader=train_loader,
        val_dataloader=val_loader,
        total_episodes=config.ppo.total_steps
    )

    print()
    print("=" * 70)
    print("TRAINING COMPLETE")
    print("=" * 70)
    print()

    # 7. Load checkpoint data
    print("📊 Loading checkpoint data for analysis...")
    checkpoint_logger = trainer.checkpoint_logger

    weight_trajectory = checkpoint_logger.load_weights_trajectory()
    pass_at_1_trajectory = checkpoint_logger.load_pass_at_1_trajectory()

    print(f"✓ Loaded {len(weight_trajectory)} weight checkpoints")
    print(f"✓ Loaded {len(pass_at_1_trajectory)} pass@1 checkpoints")
    print()

    # 8. Run Phase 1 analysis
    print("=" * 70)
    print("GATE VALIDATION")
    print("=" * 70)
    print()

    analyzer = Phase1Analyzer(weight_trajectory, pass_at_1_trajectory)
    gate_result = analyzer.validate_gate_criteria()

    print(f"Gate Result: {gate_result['gate_result']}")
    print()
    print(gate_result['rationale'])
    print()

    # 9. Generate figures
    print("=" * 70)
    print("GENERATING FIGURES")
    print("=" * 70)
    print()

    os.makedirs('./figures', exist_ok=True)

    plot_weight_trajectory(weight_trajectory, './figures/weight_trajectory.png')
    plot_pass_at_1_trajectory(pass_at_1_trajectory, './figures/pass_at_1_trajectory.png')
    plot_phase_improvement_rates(gate_result['metric2_pass_at_1_improvement'], './figures/phase_improvement_rates.png')
    plot_gate_metrics(gate_result, './figures/gate_metrics.png')

    print()
    print(f"✓ All figures saved to ./figures/")
    print()

    # 10. Save results summary
    print("=" * 70)
    print("SAVING RESULTS")
    print("=" * 70)
    print()

    import json

    results = {
        'hypothesis_id': 'h-m1',
        'experiment_name': config.experiment_name,
        'timestamp': datetime.now().isoformat(),
        'gate_result': gate_result['gate_result'],
        'gate_metrics': {
            'weight_dominance': {
                'passed': gate_result['metric1_weight_dominance']['passed'],
                'violations': gate_result['metric1_weight_dominance']['violation_count']
            },
            'pass_at_1_improvement': {
                'passed': gate_result['metric2_pass_at_1_improvement']['passed'],
                'phase1_rate': gate_result['metric2_pass_at_1_improvement']['phase1_rate'],
                'later_rate': gate_result['metric2_pass_at_1_improvement']['later_rate']
            },
            'weight_correlation': {
                'passed': gate_result['metric3_weight_correlation']['passed'],
                'correlation': gate_result['metric3_weight_correlation']['correlation'],
                'p_value': gate_result['metric3_weight_correlation']['p_value']
            }
        },
        'training_episodes': config.ppo.total_steps,
        'checkpoints_logged': len(weight_trajectory)
    }

    with open('experiment_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"✓ Results saved to experiment_results.json")
    print()

    print("=" * 70)
    print("EXPERIMENT COMPLETE")
    print("=" * 70)
    print(f"End time: {datetime.now().isoformat()}")
    print(f"Gate: {gate_result['gate_result']}")
    print("=" * 70)

    return gate_result['gate_result']


if __name__ == "__main__":
    gate_status = main()
    sys.exit(0 if gate_status == 'PASS' else 1)
