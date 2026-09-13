"""
ExperimentConfig for H-E1 EXISTENCE PoC
Cross-encoder NLI hallucination detection on HaluEval.
"""
from dataclasses import dataclass, field
from typing import Tuple, Dict


@dataclass
class ExperimentConfig:
    # Model
    model_name: str = "cross-encoder/nli-deberta-v3-large"

    # Inference
    batch_size: int = 32
    batch_size_fallback: int = 16   # OOM fallback
    max_length: int = 512
    truncation: bool = True

    # Reproducibility
    seed: int = 42

    # Evaluation thresholds
    auroc_threshold: float = 0.55
    delong_alpha: float = 0.05
    cohen_d_threshold: float = 0.2
    tasks_required_to_pass: int = 2   # out of 3

    # Label audit
    label_audit_n: int = 200

    # Dataset
    halueval_hf_id: str = "pminervini/HaluEval"
    tasks: Tuple[str, ...] = ("dialogue", "qa", "summarization")

    # HaluEval HuggingFace config names per task
    # NOTE: actual HF configs are 'dialogue', 'qa', 'summarization' (NOT *_data variants)
    hf_config_names: Dict[str, str] = field(default_factory=lambda: {
        "dialogue": "dialogue",
        "qa": "qa",
        "summarization": "summarization",
    })

    # HaluEval dataset structure:
    # Each example has right_X and hallucinated_X columns.
    # We construct binary labels by interleaving both.
    # premise_fields: the grounding context column
    # hypothesis_right_fields: non-hallucinated response column (label=0)
    # hypothesis_hall_fields: hallucinated response column (label=1)
    premise_fields: Dict[str, str] = field(default_factory=lambda: {
        "dialogue": "knowledge",
        "qa": "knowledge",
        "summarization": "document",
    })
    hypothesis_right_fields: Dict[str, str] = field(default_factory=lambda: {
        "dialogue": "right_response",
        "qa": "right_answer",
        "summarization": "right_summary",
    })
    hypothesis_hall_fields: Dict[str, str] = field(default_factory=lambda: {
        "dialogue": "hallucinated_response",
        "qa": "hallucinated_answer",
        "summarization": "hallucinated_summary",
    })

    # Output
    results_dir: str = "results"
    figures_dir: str = "figures"
    save_scores: bool = True    # save full (N,3) matrix for H-M series reuse
    scores_filename: str = "h-e1_results.json"
    summary_filename: str = "h-e1_summary.json"


def get_config() -> ExperimentConfig:
    """Factory function returning default ExperimentConfig."""
    return ExperimentConfig()
