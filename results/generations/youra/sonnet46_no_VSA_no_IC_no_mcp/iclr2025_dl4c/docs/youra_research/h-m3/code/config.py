"""config.py — H-M3: Configuration for RLEF-Binary vs RLEF-Fraction comparison."""
import sys
from dataclasses import dataclass, field
from pathlib import Path

H_E1_CODE = Path(__file__).parents[2] / "h-e1" / "code"

# Add h-E1 code to path so we can reuse its modules
if str(H_E1_CODE) not in sys.path:
    sys.path.insert(0, str(H_E1_CODE))


@dataclass
class H_M3_Config:
    # Model
    model_name: str = "deepseek-ai/deepseek-coder-1.3b-base"  # 1.3B for smoke test; upgrade to 7B for full run
    sft_checkpoint: str = str(H_E1_CODE / "checkpoints" / "sft_baseline")
    fraction_checkpoint: str = str(H_E1_CODE / "checkpoints" / "rlef_fraction")
    binary_checkpoint_dir: str = "checkpoints/rlef_binary"

    # Training (match h-E1 RLEF-Fraction exactly for controlled comparison)
    lr: float = 1e-6
    batch_size: int = 1
    grad_accum: int = 4
    num_epochs: int = 1
    max_length: int = 512
    max_new_tokens: int = 512
    seed: int = 42
    beta: float = 0.04
    temperature: float = 0.8
    num_generations: int = 4  # G=4 for smoke; 8 for full
    warmup_steps: int = 10
    max_steps: int = 80       # smoke-test budget: ~80 steps
    logging_steps: int = 10

    # Monitoring
    verify_interval_steps: int = 20
    checkpoint_interval_steps: int = 40

    # Data
    apps_n_samples: int = 500   # smoke subset

    # Output
    figures_dir: str = str(Path(__file__).parents[3] / "figures")
    results_dir: str = "results"
    logs_dir: str = "logs"

    # Bootstrap test
    n_bootstrap: int = 5000
    bootstrap_seed: int = 42
