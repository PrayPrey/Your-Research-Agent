"""
Configuration file for AMR experiments
"""
import torch

class Config:
    """Configuration for experiments"""

    # Device configuration
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # Dataset configuration
    dataset_name = 'waterbirds'  # Options: waterbirds, celeba, colored_mnist
    data_dir = './data'

    # Model configuration
    model_arch = 'resnet18'  # Lighter model for faster experiments
    pretrained = True

    # Training configuration
    batch_size = 32
    num_epochs = 30
    learning_rate = 1e-3
    weight_decay = 1e-4
    momentum = 0.9

    # AMR specific parameters
    m_target = 1.0  # Target margin
    mu_0 = 0.5  # Initial regularization strength
    tau = 5  # Lookback window for gradient acceleration
    eta = 5.0  # Sigmoid scaling for sample weighting
    delta = 0.5  # Threshold for spurious feature score
    alpha = 0.5  # Weight for confidence/acceleration indicator
    beta = 0.5  # Weight for margin term
    gamma_c = 0.8  # Confidence threshold
    gamma_a = 0.5  # Acceleration threshold
    lambda_log = 0.1  # Weight for logarithmic margin penalty
    epsilon = 1e-8  # Small constant for numerical stability

    # Gradient clipping
    clip_grad_norm = 1.0
    clip_spurious = 0.5
    tau_s = 0.6  # Threshold for batch spurious score

    # Evaluation
    eval_every = 2  # Evaluate every N epochs
    save_dir = './results'

    # Random seed
    seed = 42

    # Number of workers for data loading
    num_workers = 4

    # Baseline methods to compare
    baselines = ['ERM', 'JTT', 'GroupDRO', 'AMR']

    @classmethod
    def get_config(cls, **kwargs):
        """Get configuration with optional overrides"""
        config = cls()
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config
