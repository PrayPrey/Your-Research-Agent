from dataclasses import dataclass, field
import yaml


@dataclass
class GenerationConfig:
    model: str = "gpt-4o-mini"
    temperature: float = 0.2
    max_tokens: int = 512


@dataclass
class VerifierTimeouts:
    execution_timeout: float = 3.0
    static_timeout: float = 10.0
    type_timeout: float = 10.0
    smt_timeout: float = 10.0


@dataclass
class SmtPilotConfig:
    n_problems: int = 20
    seed: int = 1
    gate_threshold: float = 0.30


@dataclass
class PathsConfig:
    results_dir: str = "results"
    figures_dir: str = "figures"
    completions_checkpoint: str = "results/completions.jsonl"
    smt_pilot_results: str = "results/smt_pilot_results.json"
    verifier_results: str = "results/verifier_results.jsonl"
    activation_stats: str = "results/activation_stats.json"


@dataclass
class ExperimentConfig:
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    timeouts: VerifierTimeouts = field(default_factory=VerifierTimeouts)
    smt_pilot: SmtPilotConfig = field(default_factory=SmtPilotConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    activation_threshold: float = 0.10
    random_seed: int = 1


def load_config(path: str = "config/experiment.yaml") -> ExperimentConfig:
    with open(path) as f:
        data = yaml.safe_load(f)
    cfg = ExperimentConfig()
    if "generation" in data:
        cfg.generation = GenerationConfig(**data["generation"])
    if "timeouts" in data:
        cfg.timeouts = VerifierTimeouts(**data["timeouts"])
    if "smt_pilot" in data:
        cfg.smt_pilot = SmtPilotConfig(**data["smt_pilot"])
    if "paths" in data:
        cfg.paths = PathsConfig(**data["paths"])
    if "activation_threshold" in data:
        cfg.activation_threshold = data["activation_threshold"]
    if "random_seed" in data:
        cfg.random_seed = data["random_seed"]
    return cfg
