"""Configuration for H-E1 ContractEval contract-strength gap experiment."""
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    # Data paths
    contracteval_jsonl: str = ""  # set at runtime
    samples_dir: str = "data/samples"
    results_dir: str = "results"
    figures_dir: str = "figures"
    outputs_dir: str = "outputs"

    # Models evaluated (closed + open)
    models: list = field(default_factory=lambda: [
        "gpt-4o-mini",
        "claude-3-haiku-20240307",
        "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct",
        "codellama/CodeLlama-13b-Instruct-hf",
        "codellama/CodeLlama-34b-Instruct-hf",
    ])

    # PBT config
    oracle_budget: int = 100_000
    pbt_budget: int = 5_000
    pbt_seed: int = 42
    pbt_timeout: int = 60  # seconds per check
    n_samples: int = 10
    temperature: float = 0.8
    n_bootstrap: int = 10_000
    gate_threshold: float = 0.01  # CI_lower > 0.01

    # Experiment scale
    max_tasks: int = 364  # all tasks


def default_config() -> Config:
    base = Path(__file__).parent
    cfg = Config()
    # ContractEval JSONL from archive (already downloaded)
    # h-e1/code/ -> h-e1/ -> youra_research/ -> docs/ -> TEST_verifai/
    archive_path = (
        base.parent.parent
        / "_archive/20260803T121822_routing_recovery"
        / ".data_cache/datasets/ContractEval/data/ContractEval/ContractEval.jsonl"
    )
    cfg.contracteval_jsonl = str(archive_path)
    cfg.samples_dir = str(base / "data/samples")
    cfg.results_dir = str(base / "results")
    cfg.figures_dir = str(base.parent / "figures")
    cfg.outputs_dir = str(base / "outputs")
    return cfg
