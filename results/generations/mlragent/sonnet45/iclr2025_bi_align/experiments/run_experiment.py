"""
Main experiment script for Adaptive Alignment
"""

import os
import sys
import json
import numpy as np
import torch
import torch.optim as optim
from tqdm import tqdm
import logging
from datetime import datetime

# Import local modules
from config import *
from value_evolution import InteractionEnvironment
from alignment_models import create_model
from evaluation import AlignmentEvaluator
from visualization import (
    plot_training_curves, plot_model_comparison, plot_temporal_tracking,
    plot_model_value_evolution, plot_human_value_evolution,
    plot_scenario_comparison, plot_radar_chart, plot_aggregate_comparison
)

# Setup logging
def setup_logging(log_file):
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def set_seed(seed):
    """Set random seeds for reproducibility"""
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def train_model(model, environment, num_epochs, learning_rate, batch_size,
               temporal_lambda, device, logger):
    """Train a model on the interaction environment"""
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    model.train()

    loss_history = []

    for epoch in range(num_epochs):
        epoch_losses = []

        # Generate training batches
        num_batches = 50  # batches per epoch
        for _ in range(num_batches):
            states, contexts, actions, timesteps = environment.generate_batch_data(batch_size)
            states = states.to(device)
            contexts = contexts.to(device)
            actions = actions.to(device)
            timesteps = timesteps.to(device)

            optimizer.zero_grad()

            # Compute loss based on model type
            if hasattr(model, 'compute_loss'):
                loss = model.compute_loss(states, contexts, actions, timesteps, temporal_lambda)
            else:
                logits = model(states, contexts, timesteps)
                if isinstance(logits, tuple):
                    logits = logits[0]
                loss = torch.nn.functional.cross_entropy(logits, actions)

            loss.backward()
            optimizer.step()

            epoch_losses.append(loss.item())

        avg_loss = np.mean(epoch_losses)
        loss_history.append(avg_loss)

        if (epoch + 1) % EVAL_EVERY == 0:
            logger.info(f"Epoch {epoch + 1}/{num_epochs}, Loss: {avg_loss:.4f}")

    return loss_history

def run_scenario_experiment(scenario, device, logger):
    """Run experiment for a single scenario"""
    logger.info(f"\n{'='*60}")
    logger.info(f"Running scenario: {scenario}")
    logger.info(f"{'='*60}\n")

    # Create environment
    environment = InteractionEnvironment(
        num_users=NUM_USERS,
        feature_dim=FEATURE_DIM,
        action_dim=ACTION_DIM,
        num_contexts=NUM_CONTEXTS,
        num_timesteps=NUM_TIMESTEPS,
        scenario=scenario,
        seed=RANDOM_SEED
    )

    # Create evaluator
    evaluator = AlignmentEvaluator(FEATURE_DIM, ACTION_DIM, NUM_CONTEXTS)

    # Results storage
    scenario_results = {}
    training_histories = {}
    tracking_results = {}

    # Split users for training and evaluation
    train_users = list(range(NUM_USERS // 2))
    eval_users = list(range(NUM_USERS // 2, NUM_USERS))

    # Train and evaluate each model
    for model_name in BASELINES.keys():
        logger.info(f"\nTraining model: {model_name}")

        # Create model
        model = create_model(
            model_name, FEATURE_DIM, ACTION_DIM, HIDDEN_DIM, NUM_CONTEXTS, device
        )

        # Train model
        loss_history = train_model(
            model, environment, NUM_EPOCHS, LEARNING_RATE, BATCH_SIZE,
            TEMPORAL_LAMBDA, device, logger
        )
        training_histories[model_name] = loss_history

        logger.info(f"Training completed. Final loss: {loss_history[-1]:.4f}")

        # Evaluate model
        logger.info("Evaluating model...")
        results = evaluator.evaluate_model(model, environment, eval_users, device)
        scenario_results[model_name] = results

        logger.info(f"Results for {model_name}:")
        for metric, value in results.items():
            logger.info(f"  {metric}: {value:.4f}")

        # Track preference evolution
        tracking = evaluator.evaluate_preference_tracking(
            model, environment, eval_users[:5], device  # Use subset for tracking
        )
        tracking_results[model_name] = tracking

    return scenario_results, training_histories, tracking_results, environment

def main():
    """Main experiment execution"""
    # Setup
    set_seed(RANDOM_SEED)
    device = DEVICE

    # Create results directory
    results_dir = os.path.join(os.path.dirname(__file__), 'figures')
    os.makedirs(results_dir, exist_ok=True)

    # Setup logging
    log_file = os.path.join(os.path.dirname(__file__), 'log.txt')
    logger = setup_logging(log_file)

    logger.info("="*80)
    logger.info("Adaptive Alignment Experiment")
    logger.info(f"Device: {device}")
    logger.info(f"Random Seed: {RANDOM_SEED}")
    logger.info("="*80)

    # Storage for all results
    all_scenario_results = {}
    all_training_histories = {}
    all_tracking_results = {}

    # Run experiments for each scenario
    for scenario in SCENARIOS:
        scenario_results, training_histories, tracking_results, environment = \
            run_scenario_experiment(scenario, device, logger)

        all_scenario_results[scenario] = scenario_results
        all_training_histories[scenario] = training_histories
        all_tracking_results[scenario] = tracking_results

        # Visualize human value evolution for this scenario
        logger.info(f"\nGenerating visualizations for {scenario}...")
        plot_human_value_evolution(
            environment, scenario,
            os.path.join(results_dir, f'human_value_evolution_{scenario}.png')
        )

        # Plot model-specific tracking
        for model_name, tracking in tracking_results.items():
            plot_model_value_evolution(
                tracking, scenario, model_name, results_dir
            )

        # Plot alignment comparison for this scenario
        plot_temporal_tracking(
            tracking_results,
            os.path.join(results_dir, f'alignment_comparison_{scenario}.png'),
            metric='alignment_over_time',
            title=f'Alignment Over Time - {scenario.replace("_", " ").title()}'
        )

    # Generate aggregate visualizations
    logger.info("\n" + "="*80)
    logger.info("Generating aggregate visualizations...")
    logger.info("="*80)

    # Aggregate metrics comparison
    plot_aggregate_comparison(
        all_scenario_results,
        os.path.join(results_dir, 'aggregate_metrics_comparison.png')
    )

    # Scenario-wise comparisons for key metrics
    key_metrics = ['accuracy', 'user_satisfaction', 'stability', 'agency_preservation']
    for metric in key_metrics:
        plot_scenario_comparison(
            all_scenario_results, metric,
            os.path.join(results_dir, f'scenario_comparison_{metric}.png')
        )

    # Radar chart for each scenario
    for scenario in SCENARIOS:
        plot_radar_chart(
            all_scenario_results[scenario],
            ['accuracy', 'alignment_score', 'stability', 'user_satisfaction'],
            os.path.join(results_dir, f'model_metrics_radar.png')
        )

    # Save results to JSON
    logger.info("\nSaving results...")
    results_json = {
        'scenario_results': {
            scenario: {
                model: {k: float(v) if isinstance(v, (np.floating, float)) else v
                       for k, v in results.items()}
                for model, results in scenario_results.items()
            }
            for scenario, scenario_results in all_scenario_results.items()
        },
        'config': {
            'num_users': NUM_USERS,
            'num_timesteps': NUM_TIMESTEPS,
            'num_epochs': NUM_EPOCHS,
            'scenarios': SCENARIOS
        }
    }

    results_file = os.path.join(os.path.dirname(__file__), 'results.json')
    with open(results_file, 'w') as f:
        json.dump(results_json, f, indent=2)

    logger.info(f"Results saved to {results_file}")

    # Generate summary table
    logger.info("\n" + "="*80)
    logger.info("EXPERIMENT SUMMARY")
    logger.info("="*80)

    for scenario in SCENARIOS:
        logger.info(f"\nScenario: {scenario.upper()}")
        logger.info("-" * 60)
        results = all_scenario_results[scenario]

        # Create comparison table
        models = list(results.keys())
        metrics = ['accuracy', 'alignment_score', 'user_satisfaction', 'agency_preservation']

        logger.info(f"{'Model':<25} " + " ".join([f"{m[:8]:>10}" for m in metrics]))
        logger.info("-" * 60)

        for model in models:
            values = [results[model].get(m, 0) for m in metrics]
            logger.info(f"{model:<25} " + " ".join([f"{v:>10.4f}" for v in values]))

    # Compute and log improvements
    logger.info("\n" + "="*80)
    logger.info("IMPROVEMENTS OVER BASELINE (Static Alignment)")
    logger.info("="*80)

    for scenario in SCENARIOS:
        logger.info(f"\nScenario: {scenario.upper()}")
        logger.info("-" * 60)

        baseline_results = all_scenario_results[scenario]['static_alignment']

        for model_name in ['ceva_basic', 'ceva_full', 'adaptive_alignment']:
            model_results = all_scenario_results[scenario][model_name]
            logger.info(f"\n{model_name}:")

            for metric in ['accuracy', 'alignment_score', 'user_satisfaction']:
                baseline_val = baseline_results[metric]
                model_val = model_results[metric]
                improvement = ((model_val - baseline_val) / baseline_val) * 100
                logger.info(f"  {metric}: {improvement:+.2f}%")

    logger.info("\n" + "="*80)
    logger.info("Experiment completed successfully!")
    logger.info("="*80)

if __name__ == "__main__":
    main()
