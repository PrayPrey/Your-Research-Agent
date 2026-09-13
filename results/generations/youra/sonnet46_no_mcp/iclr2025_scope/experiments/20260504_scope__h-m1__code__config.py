"""
config.py — Configuration dataclasses for H-M1 attention entropy mechanistic analysis.

H-M1 is an inference-only analysis experiment (no re-training).
Loads pre-trained LoRA adapters from H-E1 outputs.
"""
import os
from dataclasses import dataclass, field
from typing import List, Optional

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "1")
os.environ.setdefault("WANDB_DISABLED", "true")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# H-E1 output directory (where trained adapters are stored)
_H_E1_OUTPUTS = os.path.join(
    os.path.dirname(__file__),
    "../../h-e1/code/outputs/h-e1",
)

LONGBENCH_TASKS: List[str] = [
    "narrativeqa",
    "qasper",
    "multifieldqa_en",
    "multifieldqa_zh",
    "hotpotqa",
    "2wikimqa",
    "musique",
    "dureader",
    "gov_report",
    "qmsum",
    "multi_news",
    "vcsum",
    "trec",
    "triviaqa",
    "samsum",
    "lsht",
    "passage_count",
    "passage_retrieval_en",
    "passage_retrieval_zh",
    "lcc",
    "repobench-p",
]

LONGBENCH_CATEGORIES: dict = {
    "single-doc-qa": ["narrativeqa", "qasper", "multifieldqa_en", "multifieldqa_zh"],
    "multi-doc-qa": ["hotpotqa", "2wikimqa", "musique", "dureader"],
    "summarization": ["gov_report", "qmsum", "multi_news", "vcsum"],
    "few-shot": ["trec", "triviaqa", "samsum", "lsht"],
    "synthetic": ["passage_count", "passage_retrieval_en", "passage_retrieval_zh"],
    "code": ["lcc", "repobench-p"],
}


@dataclass
class InferenceConfig:
    model_name: str = ""
    adapter_checkpoint: str = ""
    condition: str = ""           # "eviction-aware" | "baseline"
    kv_budget_ratio: float = 0.5
    heavy_ratio: float = 0.1
    recent_ratio: float = 0.1
    max_seq_length: int = 4096
    batch_size: int = 1
    seed: int = 1
    fp16: bool = True
    top_ratio: float = 0.2        # heavy-hitter top-20% threshold
    output_dir: str = ""


@dataclass
class ExperimentConfig:
    experiment_id: str = "h-m1"
    longbench_tasks: List[str] = field(default_factory=lambda: list(LONGBENCH_TASKS))
    min_samples_per_category: int = 500
    significance_threshold: float = 0.05
    gate_layer_fraction: float = 0.5    # >=50% layers must pass
    figures_dir: str = "figures"
    results_dir: str = "outputs"
    models: List[InferenceConfig] = field(default_factory=list)


def get_experiment_config() -> ExperimentConfig:
    """Return default experiment config using H-E1 adapter checkpoints."""
    h_e1_base = _H_E1_OUTPUTS

    llama_baseline = InferenceConfig(
        model_name="meta-llama/Llama-2-7b-hf",
        adapter_checkpoint=os.path.join(h_e1_base, "llama2-7b-baseline"),
        condition="baseline",
        kv_budget_ratio=0.5,
        output_dir="outputs/h-m1/llama2-baseline",
    )
    llama_eviction = InferenceConfig(
        model_name="meta-llama/Llama-2-7b-hf",
        adapter_checkpoint=os.path.join(h_e1_base, "llama2-7b-eviction-aware"),
        condition="eviction-aware",
        kv_budget_ratio=0.5,
        output_dir="outputs/h-m1/llama2-eviction",
    )
    mistral_baseline = InferenceConfig(
        model_name="mistralai/Mistral-7B-v0.1",
        adapter_checkpoint=os.path.join(h_e1_base, "mistral-7b-baseline"),
        condition="baseline",
        kv_budget_ratio=0.5,
        output_dir="outputs/h-m1/mistral-baseline",
    )
    mistral_eviction = InferenceConfig(
        model_name="mistralai/Mistral-7B-v0.1",
        adapter_checkpoint=os.path.join(h_e1_base, "mistral-7b-eviction-aware"),
        condition="eviction-aware",
        kv_budget_ratio=0.5,
        output_dir="outputs/h-m1/mistral-eviction",
    )

    return ExperimentConfig(
        models=[llama_baseline, llama_eviction, mistral_baseline, mistral_eviction],
    )


def validate_config(cfg: ExperimentConfig) -> None:
    """Validate experiment configuration."""
    assert cfg.significance_threshold > 0, "significance_threshold must be positive"
    assert 0.0 < cfg.gate_layer_fraction <= 1.0, "gate_layer_fraction must be in (0,1]"
    assert cfg.min_samples_per_category > 0, "min_samples_per_category must be positive"
    for inf_cfg in cfg.models:
        assert inf_cfg.condition in ("baseline", "eviction-aware"), (
            f"condition must be 'baseline' or 'eviction-aware', got: {inf_cfg.condition}"
        )
        assert inf_cfg.model_name != "", "model_name must be set"
        assert 0.0 < inf_cfg.kv_budget_ratio < 1.0, (
            f"kv_budget_ratio must be in (0,1), got: {inf_cfg.kv_budget_ratio}"
        )
