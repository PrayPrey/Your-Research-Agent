from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import os

BASE_DIR = Path(__file__).parent.parent  # h-e1/


@dataclass
class ExperimentConfig:
    """Fixed single-run config for h-e1 EXISTENCE PoC."""

    seed: int = 42
    ngram_n: int = 13
    ngram_buckets: int = 500
    sbert_model: str = "all-MiniLM-L6-v2"
    sbert_batch_size: int = 256
    faiss_index_type: str = "IndexFlatIP"
    stratum_percentile: float = 75.0
    minkpp_k: float = 0.20
    bootstrap_n: int = 10_000
    contamination_rate: float = 0.10
    corpora: list = field(default_factory=lambda: ["pile", "c4", "redpajama"])
    benchmarks: list = field(default_factory=lambda: ["mmlu", "hellaswag", "gsm8k"])
    pile_max_docs: int = 1_000_000
    c4_max_docs: int = 1_000_000
    redpajama_max_docs: int = 1_000_000
    llama2_7b_id: str = "meta-llama/Llama-2-7b-hf"
    mistral_7b_id: str = "mistralai/Mistral-7B-v0.1"
    pythia_7b_id: str = "EleutherAI/pythia-6.9b"
    pythia_2b_id: str = "EleutherAI/pythia-2.8b"
    figures_dir: str = str(BASE_DIR / "figures")
    results_dir: str = str(BASE_DIR / "results")
    index_dir: str = str(BASE_DIR / "indices")

    def validate(self) -> None:
        assert 0.0 < self.minkpp_k < 1.0
        assert 0.0 < self.stratum_percentile < 100.0
        assert self.bootstrap_n >= 1000
        assert 0.0 < self.contamination_rate < 1.0
        assert self.ngram_n > 0
        for d in [self.figures_dir, self.results_dir, self.index_dir]:
            Path(d).mkdir(parents=True, exist_ok=True)


def get_config() -> ExperimentConfig:
    cfg = ExperimentConfig()
    cfg.validate()
    return cfg
