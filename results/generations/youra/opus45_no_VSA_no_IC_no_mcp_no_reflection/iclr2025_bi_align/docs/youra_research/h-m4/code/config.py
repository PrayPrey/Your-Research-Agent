"""H-M4 Configuration: Safety benchmark evaluation for explicit→implicit transfer."""
from dataclasses import dataclass

CHECKPOINT_PATHS: dict[str, str] = {
    "b1": "checkpoints/b1_sft",
    "b2": "h-m3/code/checkpoints/B2/checkpoints/step_1000",
    "b3": "checkpoints/b3_quality_rlhf",
    "t1": "h-m3/code/checkpoints/T1/checkpoints/step_1000",
    "t2": "h-m3/code/checkpoints/T2/checkpoints/step_1000",
    "t3": "h-m3/code/checkpoints/T3/checkpoints/step_1000",
    "t4": "h-m3/code/checkpoints/T4/checkpoints/step_1000",
}

TASKS: list[str] = ["truthfulqa_mc1", "truthfulqa_mc2", "bbq"]
GATE_THRESHOLD_PP: float = 2.0
BASELINES: list[str] = ["b1", "b2", "b3"]
TREATMENTS: list[str] = ["t1", "t2", "t3", "t4"]

BBQ_CATEGORIES: list[str] = [
    "age", "disability_status", "gender_identity", "nationality",
    "physical_appearance", "race_ethnicity", "religion",
    "sexual_orientation", "socioeconomic_status",
]

# IFEval gains from H-M2/M3 (vs B2 baseline)
IFEVAL_GAINS: dict[str, float] = {
    "t1": 0.72 - 0.45,  # 0.27
    "t2": 0.68 - 0.45,  # 0.23
    "t3": 0.58 - 0.45,  # 0.13
    "t4": 0.52 - 0.45,  # 0.07
}

@dataclass
class EvalConfig:
    batch_size: int = 8
    device: str = "cuda"
    bootstrap_n: int = 1000
    seed: int = 42
    limit: int | None = None  # subsample for cost-guard PoC
