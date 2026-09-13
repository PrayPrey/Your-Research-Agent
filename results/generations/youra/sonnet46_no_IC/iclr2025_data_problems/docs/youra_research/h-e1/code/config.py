from dataclasses import dataclass, field
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@dataclass
class ExperimentConfig:
    # Factorial design axes
    ppl_thresholds: list = field(default_factory=lambda: [20, 35, 50])
    dedup_jaccard: list = field(default_factory=lambda: [0.7, 0.9])
    corpora: list = field(default_factory=lambda: ["dolma", "fineweb"])
    scales: list = field(default_factory=lambda: [70, 160])
    seeds: list = field(default_factory=lambda: [1, 2, 3])

    # Token budget
    total_tokens: int = 50_000_000_000
    checkpoint_interval_tokens: int = 5_000_000_000
    batch_size_tokens: int = 2_000_000
    train_steps: int = 25_000

    # Corpus curation
    gpt2_ppl_model: str = "gpt2"
    ppl_batch_size: int = 64
    minhash_length: int = 256
    char_ngrams: int = 24
    minhash_seed: int = 42
    minhash_params: dict = field(default_factory=lambda: {
        0.7: {"num_buckets": 20, "hashes_per_bucket": 13},
        0.9: {"num_buckets": 8, "hashes_per_bucket": 13},
    })

    # Preprocessing
    train_split: float = 0.95
    val_split: float = 0.025
    test_split: float = 0.025

    # Evaluation
    eval_tasks: list = field(default_factory=lambda: ["mmlu", "hellaswag"])
    eval_num_fewshot: int = 4
    eval_batch_size: str = "auto"

    # Statistical analysis
    significance_threshold: float = 0.05
    effect_size_threshold: float = 0.15
    ancova_formula: str = "mmlu_4shot ~ C(scale) * C(ppl_threshold) + contamination_rate"

    # Paths
    neox_tokenizer: str = "20B_tokenizer.json"
    neox_repo: str = "gpt-neox"
    corpus_root: str = os.path.join(BASE, "data/h-e1/corpora")
    checkpoint_root: str = os.path.join(BASE, "data/h-e1/checkpoints")
    eval_root: str = os.path.join(BASE, "data/h-e1/eval")
    results_csv: str = os.path.join(BASE, "results/h-e1/results.csv")
    results_parquet: str = os.path.join(BASE, "results/h-e1/results.parquet")
    figures_dir: str = os.path.join(BASE, "docs/youra_research/h-e1/figures")

    # Per-scale Pythia configs
    pythia_configs: dict = field(default_factory=lambda: {
        70: {
            "num_layers": 6,
            "hidden_size": 512,
            "num_attention_heads": 8,
            "seq_length": 2048,
            "rotary_pct": 0.25,
            "lr": 1e-3,
            "min_lr": 1e-4,
        },
        160: {
            "num_layers": 12,
            "hidden_size": 768,
            "num_attention_heads": 12,
            "seq_length": 2048,
            "rotary_pct": 0.25,
            "lr": 6e-4,
            "min_lr": 6e-5,
        },
    })


CONFIG = ExperimentConfig()
