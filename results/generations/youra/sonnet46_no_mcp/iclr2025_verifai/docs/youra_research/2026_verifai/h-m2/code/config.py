from dataclasses import dataclass, field
from typing import List, Optional
import os


@dataclass
class MypyRepairConfig:
    max_rounds: int = 3
    repair_temperature: float = 0.2
    max_new_tokens: int = 512
    mypy_flags: List[str] = field(default_factory=lambda: ["--ignore-missing-imports", "--no-error-summary"])
    mypy_timeout: int = 30
    mechanism_activated_threshold: float = 0.10


@dataclass
class CScoreConfig:
    n_bootstrap: int = 10000
    alpha: float = 0.0167  # Bonferroni: 0.05/3
    seed: int = 42
    min_stratum_size: int = 10


@dataclass
class Z3DeltaConfig:
    z3_timeout_seconds: int = 60
    arith_density_threshold: float = 0.1


@dataclass
class H2OutputConfig:
    data_dir: str = "h-m2/data/"
    results_dir: str = "h-m2/results/"
    figures_dir: str = "h-m2/figures/"
    baseline_pool_file: str = "baseline_pool.jsonl"
    syncode_pool_file: str = "syncode_pool.jsonl"
    mypy_repair_pool_file: str = "mypy_repair_pool.jsonl"
    fmd_classification_file: str = "fmd_classification.jsonl"
    f_syncode_transitions_file: str = "f_syncode_transitions.json"
    f_mypy_transitions_file: str = "f_mypy_transitions.json"
    c_score_results_file: str = "c_score_results.json"
    z3_eligibility_delta_file: str = "z3_eligibility_delta.json"
    metrics_file: str = "metrics.json"
    progress_baseline_file: str = "progress_baseline.json"
    progress_syncode_file: str = "progress_syncode.json"
    progress_repair_file: str = "progress_repair.json"


@dataclass
class H2BaselinePoolConfig:
    n_problems: int = 164
    n_samples_per_problem: int = 20
    seed_formula: str = "problem_idx * 100 + sample_idx"
    reuse_h_e1_pool: bool = True
    h_e1_pool_path: str = ""
    h_m1_syncode_pool_path: str = ""
    checkpoint_interval: int = 10


@dataclass
class H2FMDConfig:
    cross_validate_n: int = 10
    # FMDClassifier returns "type" — map to "type_structural" for display only
    stratum_label_map: dict = field(default_factory=lambda: {
        "syntax": "syntax",
        "type": "type_structural",
        "functional": "functional",
        "success": "success",
    })


@dataclass
class H2CScoreCalculatorConfig:
    n_bootstrap: int = 10000
    alpha: float = 0.0167
    seed: int = 42
    min_stratum_size: int = 10


@dataclass
class H2Z3EligibilityConfig:
    z3_timeout_seconds: int = 60
    arith_density_threshold: float = 0.1
    n_bootstrap: int = 10000


@dataclass
class H2IntegrationConfig:
    dry_run: bool = False
    dry_run_n_problems: int = 5
    phases: List[str] = field(default_factory=lambda: [
        "baseline_pool",
        "fmd_classification",
        "syncode_pool",
        "mypy_repair",
        "f_syncode_extraction",
        "f_mypy_extraction",
        "c_score",
        "z3_eligibility",
    ])
    required_output_files: List[str] = field(default_factory=lambda: [
        "baseline_pool.jsonl",
        "fmd_classification.jsonl",
        "mypy_repair_pool.jsonl",
        "syncode_pool.jsonl",
        "f_syncode_transitions.json",
        "f_mypy_transitions.json",
        "c_score_results.json",
        "z3_eligibility_delta.json",
        "metrics.json",
    ])


@dataclass
class H2VisualizationConfig:
    dpi: int = 150
    fig_width: float = 8.0
    fig_height: float = 6.0
    colors: dict = field(default_factory=lambda: {
        "syncode": "#2196F3",
        "mypy": "#FF5722",
        "baseline": "#9E9E9E",
        "pass_color": "#4CAF50",
        "fail_color": "#F44336",
    })
    figures: dict = field(default_factory=lambda: {
        "gate_metrics": "gate_metrics.png",
        "jaccard_heatmap": "jaccard_heatmap.png",
        "fmd_distribution": "fmd_distribution.png",
        "z3_eligibility_comparison": "z3_eligibility_comparison.png",
        "repair_convergence": "repair_convergence.png",
        "quintile_c_score": "quintile_c_score.png",
    })


@dataclass
class H2ExperimentConfig:
    hypothesis_id: str = "h-m2"
    n_problems: int = 164
    h_m1_code_dir: str = ""  # set at runtime: abs path to h-m1/code/
    h_e1_baseline_pool: str = ""  # abs path to h-e1/data/baseline_pool.jsonl
    h_m1_baseline_pool: str = ""  # abs path to h-m1/data/baseline_pool.jsonl
    h_m1_syncode_pool: str = ""   # abs path to h-m1/data/syncode_pool.jsonl
    output: H2OutputConfig = field(default_factory=H2OutputConfig)
    baseline_pool: H2BaselinePoolConfig = field(default_factory=H2BaselinePoolConfig)
    fmd: H2FMDConfig = field(default_factory=H2FMDConfig)
    mypy_repair: MypyRepairConfig = field(default_factory=MypyRepairConfig)
    c_score: CScoreConfig = field(default_factory=CScoreConfig)
    z3_delta: Z3DeltaConfig = field(default_factory=Z3DeltaConfig)
    c_score_calc: H2CScoreCalculatorConfig = field(default_factory=H2CScoreCalculatorConfig)
    z3_eligibility: H2Z3EligibilityConfig = field(default_factory=H2Z3EligibilityConfig)
    integration: H2IntegrationConfig = field(default_factory=H2IntegrationConfig)
    visualization: H2VisualizationConfig = field(default_factory=H2VisualizationConfig)
