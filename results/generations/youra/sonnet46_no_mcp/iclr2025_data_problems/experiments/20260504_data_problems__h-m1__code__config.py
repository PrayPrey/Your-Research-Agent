from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import os
import yaml


@dataclass
class Config:
    # Reproducibility
    seed: int = 1

    # N-gram settings (WIMBD standard)
    ngram_n: int = 13
    num_perm: int = 128
    lsh_threshold: float = 0.5
    min_token_length: int = 13

    # Text formatting
    text_format: str = "question_choices"  # or "question_only"

    # Corpus index paths
    pile_index_path: str = "indices/pile_index.pkl"
    c4_index_path: str = "indices/c4_index.pkl"
    redpajama_index_path: str = "indices/redpajama_index.pkl"

    # Corpus HF identifiers
    corpus_configs: dict = field(default_factory=lambda: {
        "pile":      {"hf_path": "monology/pile-uncopyrighted",          "config": None},
        "c4":        {"hf_path": "allenai/c4",                         "config": "en.noclean"},
        "redpajama": {"hf_path": "togethercomputer/RedPajama-Data-1T", "config": None},
    })

    # Checkpoint and retry
    checkpoint_interval: int = 500_000
    retry_attempts: int = 3
    sample_fraction: float = 0.1  # fallback fraction if streaming fails

    # Benchmark HF identifiers
    hellaswag_hf_id: str = "Rowan/hellaswag"
    hellaswag_split: str = "validation"
    bbh_hf_id: str = "lukaemon/bbh"
    bbh_split: str = "test"

    # Output paths
    results_dir: str = "results"
    figures_dir: str = "figures"
    indices_dir: str = "indices"

    # Gate thresholds
    gate_p_threshold: float = 0.05
    min_pair_diff_pp: float = 0.02
    wimbd_spearman_min_rho: float = 0.7
    wimbd_pile_tolerance_pp: float = 0.05

    # All 57 MMLU sub-tasks (fixed list)
    mmlu_tasks: List[str] = field(default_factory=lambda: [
        "abstract_algebra", "anatomy", "astronomy", "business_ethics",
        "clinical_knowledge", "college_biology", "college_chemistry",
        "college_computer_science", "college_mathematics", "college_medicine",
        "college_physics", "computer_security", "conceptual_physics",
        "econometrics", "electrical_engineering", "elementary_mathematics",
        "formal_logic", "global_facts", "high_school_biology",
        "high_school_chemistry", "high_school_computer_science",
        "high_school_european_history", "high_school_geography",
        "high_school_government_and_politics", "high_school_macroeconomics",
        "high_school_mathematics", "high_school_microeconomics",
        "high_school_physics", "high_school_psychology",
        "high_school_statistics", "high_school_us_history",
        "high_school_world_history", "human_aging", "human_sexuality",
        "international_law", "jurisprudence", "logical_fallacies",
        "machine_learning", "management", "marketing", "medical_genetics",
        "miscellaneous", "moral_disputes", "moral_philosophy", "nutrition",
        "philosophy", "prehistory", "professional_accounting",
        "professional_law", "professional_medicine", "professional_psychology",
        "public_relations", "security_studies", "sociology",
        "us_foreign_policy", "virology", "world_religions",
    ])


def load_config(path: Optional[str] = None) -> Config:
    """Load config from YAML file with env var overrides."""
    cfg = Config()

    if path is None:
        path = os.environ.get("H_M1_CONFIG_PATH")

    if path and os.path.exists(path):
        with open(path) as f:
            data = yaml.safe_load(f)
        if data:
            for k, v in data.items():
                if hasattr(cfg, k):
                    setattr(cfg, k, v)

    if os.environ.get("H_M1_INDICES_DIR"):
        cfg.indices_dir = os.environ["H_M1_INDICES_DIR"]
    if os.environ.get("H_M1_RESULTS_DIR"):
        cfg.results_dir = os.environ["H_M1_RESULTS_DIR"]

    return cfg
