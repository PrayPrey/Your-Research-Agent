import os
from dataclasses import dataclass, field
from typing import List

_H_E1_OUTPUTS = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../h-e1/code/outputs/h-e1"))
_H_M1_CODE = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../h-m1/code"))

BUDGET_RATIOS: List[float] = [0.25, 0.50, 0.75]

LONGBENCH_TASKS: List[str] = [
    "narrativeqa", "qasper", "multifieldqa_en", "multifieldqa_zh",
    "hotpotqa", "2wikimqa", "musique", "dureader",
    "gov_report", "qmsum", "multi_news", "vcsum",
    "trec", "triviaqa", "samsum", "lsht",
    "passage_count", "passage_retrieval_en", "passage_retrieval_zh",
    "lcc", "repobench-p",
]

LONGBENCH_CATEGORIES = {
    "single-doc-qa":  ["narrativeqa", "qasper", "multifieldqa_en", "multifieldqa_zh"],
    "multi-doc-qa":   ["hotpotqa", "2wikimqa", "musique", "dureader"],
    "summarization":  ["gov_report", "qmsum", "multi_news", "vcsum"],
    "few-shot":       ["trec", "triviaqa", "samsum", "lsht"],
    "synthetic":      ["passage_count", "passage_retrieval_en", "passage_retrieval_zh"],
    "code":           ["lcc", "repobench-p"],
}

TASK_MAX_NEW_TOKENS: dict = {
    "narrativeqa": 128, "qasper": 128, "multifieldqa_en": 64, "multifieldqa_zh": 64,
    "hotpotqa": 32, "2wikimqa": 32, "musique": 32, "dureader": 128,
    "gov_report": 512, "qmsum": 512, "multi_news": 512, "vcsum": 512,
    "trec": 64, "triviaqa": 32, "samsum": 128, "lsht": 64,
    "passage_count": 32, "passage_retrieval_en": 32, "passage_retrieval_zh": 32,
    "lcc": 64, "repobench-p": 64,
}

TASK_SCORER_MAP: dict = {
    "narrativeqa": "f1", "qasper": "f1", "multifieldqa_en": "f1",
    "multifieldqa_zh": "f1", "hotpotqa": "f1", "2wikimqa": "f1",
    "musique": "f1", "dureader": "rouge-l",
    "gov_report": "rouge-l", "qmsum": "rouge-l",
    "multi_news": "rouge-l", "vcsum": "rouge-l",
    "trec": "accuracy", "triviaqa": "f1", "samsum": "rouge-l", "lsht": "accuracy",
    "passage_count": "accuracy", "passage_retrieval_en": "accuracy",
    "passage_retrieval_zh": "accuracy",
    "lcc": "edit-distance", "repobench-p": "edit-distance",
}

VIZ_CONFIG = {
    "gap_vs_budget":   {"filename": "gap_vs_budget.png",   "figsize": (8, 5)},
    "spearman_bar":    {"filename": "spearman_bar.png",    "figsize": (7, 4)},
    "gap_heatmap":     {"filename": "gap_heatmap.png",     "figsize": (10, 6)},
    "absolute_curves": {"filename": "absolute_curves.png", "figsize": (12, 5)},
}

COLOR_MAP = {
    "eviction-aware": "#2196F3",
    "sequential":     "#FF5722",
}

LINE_STYLE_MAP = {
    "meta-llama/Llama-2-7b-hf":  "-",
    "mistralai/Mistral-7B-v0.1": "--",
    "gpt2": "-.",
}


@dataclass
class AdapterSpec:
    model_name: str
    adapter_path: str
    adapter_type: str  # "sequential" | "eviction-aware"


@dataclass
class BudgetSweepConfig:
    experiment_id: str = "h-m2"
    budget_ratios: List[float] = field(default_factory=lambda: list(BUDGET_RATIOS))
    adapters: List[AdapterSpec] = field(default_factory=list)
    longbench_tasks: List[str] = field(default_factory=lambda: list(LONGBENCH_TASKS))
    max_seq_length: int = 4096
    batch_size: int = 1
    seed: int = 1
    fp16: bool = True
    attn_implementation: str = "eager"
    figures_dir: str = "figures"
    results_dir: str = "outputs/h-m2"
    spearman_gate_threshold: float = -0.8


def get_default_config() -> BudgetSweepConfig:
    """Build BudgetSweepConfig with all 4 H-E1 adapter combinations.
    Falls back to GPT-2 proxy adapters for PoC smoke test when LLaMA/Mistral not available.
    """
    h_e1 = _H_E1_OUTPUTS
    # Check if full model adapters exist, else use GPT-2 proxy
    llama_baseline = os.path.join(h_e1, "llama2-7b-baseline")
    if not os.path.isdir(llama_baseline):
        # Use GPT-2 proxy adapters for PoC
        adapters = [
            AdapterSpec(
                model_name="gpt2",
                adapter_path=os.path.join(h_e1, "gpt2-baseline", "adapter"),
                adapter_type="sequential",
            ),
            AdapterSpec(
                model_name="gpt2",
                adapter_path=os.path.join(h_e1, "gpt2-eviction-aware", "adapter"),
                adapter_type="eviction-aware",
            ),
        ]
    else:
        adapters = [
            AdapterSpec(
                model_name="meta-llama/Llama-2-7b-hf",
                adapter_path=os.path.join(h_e1, "llama2-7b-baseline"),
                adapter_type="sequential",
            ),
            AdapterSpec(
                model_name="meta-llama/Llama-2-7b-hf",
                adapter_path=os.path.join(h_e1, "llama2-7b-eviction-aware"),
                adapter_type="eviction-aware",
            ),
            AdapterSpec(
                model_name="mistralai/Mistral-7B-v0.1",
                adapter_path=os.path.join(h_e1, "mistral-7b-baseline"),
                adapter_type="sequential",
            ),
            AdapterSpec(
                model_name="mistralai/Mistral-7B-v0.1",
                adapter_path=os.path.join(h_e1, "mistral-7b-eviction-aware"),
                adapter_type="eviction-aware",
            ),
        ]
    return BudgetSweepConfig(adapters=adapters)


def validate_config(cfg: BudgetSweepConfig) -> None:
    assert len(cfg.budget_ratios) > 0, "budget_ratios must not be empty"
    for r in cfg.budget_ratios:
        assert 0.0 < r < 1.0, f"budget_ratio must be in (0,1), got: {r}"
    assert len(cfg.adapters) > 0, "adapters must not be empty"
    for a in cfg.adapters:
        assert a.model_name != "", "AdapterSpec.model_name must be set"
        assert a.adapter_type in ("sequential", "eviction-aware"), \
            f"adapter_type must be 'sequential' or 'eviction-aware', got: {a.adapter_type}"
        if not os.path.isdir(a.adapter_path):
            raise ValueError(f"adapter_path not found: {a.adapter_path}")
    assert cfg.attn_implementation == "eager", \
        "attn_implementation must be 'eager' (H2O wrapper compatibility)"
    os.makedirs(cfg.figures_dir, exist_ok=True)
    os.makedirs(cfg.results_dir, exist_ok=True)
