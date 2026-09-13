from dataclasses import dataclass, field


@dataclass
class ExperimentConfig:
    # Model
    model_name: str = "meta-llama/Llama-2-7b-chat-hf"
    torch_dtype: str = "float16"
    device_map: str = "auto"
    max_context_length: int = 4096

    # Dataset
    dataset_name: str = "THUDM/LongBench"
    tasks: list = field(default_factory=lambda: ["narrativeqa", "hotpotqa", "2wikimqa", "musique"])
    examples_per_task: int = 100
    seed: int = 42

    # KV Eviction
    methods: list = field(default_factory=lambda: ["M0", "M1", "M2", "M6"])
    retention_ratio: float = 0.5
    observation_window: int = 16
    streaming_sink_size: int = 4

    # Generation
    max_new_tokens: int = 50

    # Evaluation
    n_bootstrap: int = 1000
    bootstrap_seed: int = 42
    gate_threshold: float = 2.0

    # Output
    output_dir: str = "h-e1"
    results_file: str = "results.json"
    figures_dir: str = "figures"

    # Logging
    log_level: str = "INFO"
    log_eviction_details: bool = True


def validate_config(cfg: ExperimentConfig) -> None:
    import torch
    assert torch.cuda.is_available(), "CUDA GPU required"
    assert 0.0 < cfg.retention_ratio < 1.0
    assert cfg.observation_window > 0
    assert cfg.examples_per_task > 0
    assert cfg.n_bootstrap >= 100
    assert cfg.gate_threshold > 0.0
