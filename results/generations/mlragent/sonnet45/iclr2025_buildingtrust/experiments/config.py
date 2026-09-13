"""
Configuration for Adaptive Confidence Calibration Experiments
"""
import os

# Experiment settings
EXPERIMENT_CONFIG = {
    'n_samples': 200,  # Number of samples to use from each dataset (reduced for testing)
    'ensemble_size': 3,  # Number of models in ensemble (reduced for efficiency)
    'n_response_samples': 2,  # Number of samples per model per query
    'temperature': 0.7,
    'random_seed': 42,
    'batch_size': 5,  # Process in small batches to avoid rate limits
}

# Model configuration - Using API-based LLMs
MODEL_CONFIG = {
    'models': [
        'gpt-4o-mini',  # OpenAI model
        'claude-3-5-haiku-20241022',  # Anthropic model (smaller, faster)
        'gpt-3.5-turbo',  # Another OpenAI model for diversity
    ],
    'max_tokens': 512,
    'timeout': 30,
}

# Dataset configuration
DATASET_CONFIG = {
    'datasets': [
        'trivia_qa',  # Factual QA
        'commonsense_qa',  # Reasoning
    ],
    'split': 'validation',
    'max_samples_per_dataset': 100,
}

# Calibration settings
CALIBRATION_CONFIG = {
    'train_ratio': 0.7,
    'val_ratio': 0.15,
    'test_ratio': 0.15,
    'n_bins': 10,
    'learning_rate': 0.001,
    'n_epochs': 20,
    'batch_size': 16,
    'lambda_sharpness': 0.1,
}

# Disagreement metrics
DISAGREEMENT_METRICS = [
    'semantic_dispersion',
    'cluster_diversity',
    'length_variance',
]

# Confidence levels
CONFIDENCE_LEVELS = {
    'high': (0.8, 1.0),
    'medium': (0.5, 0.8),
    'low': (0.0, 0.5),
}

# API Keys (from environment variables)
API_KEYS = {
    'openai': os.getenv('OPENAI_API_KEY'),
    'anthropic': os.getenv('ANTHROPIC_API_KEY'),
}

# Output paths
OUTPUT_DIR = '/home/anonymous/mlbench/mlrbench/MLRagent_tasks_youra_result_sonnet45_experiment/iclr2025_buildingtrust/claude_code'
RESULTS_DIR = os.path.join(OUTPUT_DIR, 'results')
FIGURES_DIR = os.path.join(RESULTS_DIR, 'figures')
