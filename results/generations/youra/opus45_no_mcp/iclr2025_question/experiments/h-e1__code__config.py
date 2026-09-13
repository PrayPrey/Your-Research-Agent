"""H-E1 Configuration - Fixed constants for existence test."""
import os
from dataclasses import dataclass, field

@dataclass
class HE1Config:
    # Model
    model_name: str = "meta-llama/Llama-2-7b-chat-hf"
    torch_dtype: str = "float16"
    device_map: str = "auto"
    hf_token: str = field(default_factory=lambda: os.environ.get("HF_TOKEN", ""))

    # Generation
    temperature: float = 0.7
    top_p: float = 0.9
    max_new_tokens: int = 128
    n_samples: int = 10
    do_sample: bool = True

    # Dataset
    dataset_name: str = "trivia_qa"
    dataset_config: str = "rc.nocontext"
    dataset_split: str = "validation"
    n_questions: int = 50  # PoC subset for validation (reduced for runtime)
    dataset_seed: int = 42

    # Embedding
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Output paths
    output_dir: str = "results/h-e1"
    checkpoint_every: int = 10
    results_file: str = "h-e1_results.jsonl"

    # Reproducibility
    seed: int = 42


def validate_config(cfg: HE1Config) -> None:
    """Validate config before run."""
    if not cfg.hf_token:
        raise ValueError("HF_TOKEN env var must be set for gated Llama-2 model")
    if cfg.n_samples < 2:
        raise ValueError("n_samples must be >= 2 for consistency computation")
    if cfg.temperature <= 0 or cfg.temperature > 2.0:
        raise ValueError("temperature must be in (0, 2.0]")


CONFIG = HE1Config()
