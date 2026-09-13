from dataclasses import dataclass

@dataclass
class AnalysisConfig:
    logs_path: str = "results/mock_iteration_logs.jsonl"
    results_dir: str = "results/"
    figures_dir: str = "figures/"
    conditions: tuple[str, str] = ("A", "B")  # A=static_first, B=exec_first per h-e1
    iterations: tuple[int, ...] = (1, 2, 3)
    alpha: float = 0.05
    required_fields: tuple[str, ...] = ("problem_id", "condition", "iteration", "passed")
