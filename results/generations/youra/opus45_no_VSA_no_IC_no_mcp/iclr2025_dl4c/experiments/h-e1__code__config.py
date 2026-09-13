from dataclasses import dataclass, field

@dataclass
class ExperimentConfig:
    seed: int = 42
    model_id: str = "codellama/CodeLlama-7b-Instruct-hf"
    max_iterations: int = 3
    temperature: float = 0.2
    max_tokens: int = 512
    top_p: float = 0.95
    timeout_sec: int = 10
    mem_limit_mb: int = 512
    datasets: list[str] = field(default_factory=lambda: ["humaneval", "mbpp"])
    feedback_types: list[str] = field(default_factory=lambda: ["execution", "random"])
    results_path: str = "results.json"
    figures_dir: str = "../figures/"

CONFIG = ExperimentConfig()
