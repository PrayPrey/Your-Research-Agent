"""Configuration schema for h-e1 experiment."""
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class AnalyzerType(str, Enum):
    BANDIT = "bandit"
    CODEQL = "codeql"


@dataclass
class DataConfig:
    """Task stratification and dataset loading."""
    swebench_dataset: str = "princeton-nlp/SWE-bench"
    swebench_split: str = "test"
    target_sample_size: int = 10  # Small size for PoC validation
    min_samples_per_cwe: int = 1
    seed: int = 42
    cache_dir: Optional[str] = "/workspace/TEST_dl4c/data/h-e1/cache"
    purplelama_cwe_dist_path: str = "/workspace/TEST_dl4c/data/h-e1/purplelama_cwe_distribution.json"


@dataclass
class ModelConfig:
    """CodeLlama-7B-Instruct inference settings."""
    model_id: str = "meta-llama/CodeLlama-7b-Instruct-hf"
    torch_dtype: str = "auto"
    device_map: str = "auto"
    max_new_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.95
    do_sample: bool = True
    load_in_8bit: bool = False
    use_flash_attention_2: bool = False


@dataclass
class AgentMeshConfig:
    """Multi-agent system parameters."""
    max_debugger_iterations: int = 3  # Reduced for faster execution
    max_coder_attempts: int = 2
    timeout_per_task: int = 120  # 2 minutes per task
    use_reviewer: bool = True
    agents: list = None

    def __post_init__(self):
        if self.agents is None:
            self.agents = ["planner", "coder", "debugger", "reviewer"]


@dataclass
class AnalyzerConfig:
    """Security static analyzer settings."""
    primary_analyzer: AnalyzerType = AnalyzerType.BANDIT
    secondary_analyzer: AnalyzerType = AnalyzerType.CODEQL
    bandit_severity_threshold: str = "LOW"
    bandit_confidence_threshold: str = "LOW"
    bandit_output_format: str = "json"
    codeql_database_path: Optional[str] = "data/h-e1/codeql_db"
    codeql_query_suite: str = "python-security-extended.qls"
    instrument_debugger: bool = True
    log_all_revisions: bool = True


@dataclass
class TraceConfig:
    """Revision trace logging settings."""
    trace_output_dir: str = "/workspace/TEST_dl4c/data/h-e1/traces"
    trace_format: str = "jsonl"
    log_fields: list = None
    checkpoint_interval: int = 10
    checkpoint_dir: str = "/workspace/TEST_dl4c/data/h-e1/checkpoints"

    def __post_init__(self):
        if self.log_fields is None:
            self.log_fields = [
                "task_id", "iteration", "vulnerable_code", "fixed_code",
                "cwe_types", "analyzer_triggered", "analyzer_name", "severity"
            ]


@dataclass
class MetricsConfig:
    """Gate metric computation settings."""
    target_security_percentage: float = 30.0
    target_kl_divergence: float = 0.5
    target_jaccard_agreement: float = 0.4
    kl_divergence_epsilon: float = 1e-10
    cwe_histogram_bins: Optional[list] = None
    metrics_output_path: str = "/workspace/TEST_dl4c/data/h-e1/results/metrics.json"
    gate_decision_path: str = "/workspace/TEST_dl4c/data/h-e1/results/gate_decision.json"


@dataclass
class VisualizationConfig:
    """Figure generation settings."""
    output_dir: str = "/workspace/TEST_dl4c/docs/youra_research/h-e1/figures"
    dpi: int = 300
    format: str = "png"
    style: str = "seaborn-v0_8-darkgrid"
    bar_width: float = 0.6
    scatter_alpha: float = 0.7
    color_security: str = "#e74c3c"
    color_runtime: str = "#3498db"
    color_target: str = "#2ecc71"
    color_actual: str = "#95a5a6"


@dataclass
class ExperimentConfig:
    """Master configuration for h-e1."""
    hypothesis_id: str = "h-e1"
    experiment_name: str = "security_instrumented_multi_agent_traces"
    seed: int = 42
    data: DataConfig = None
    model: ModelConfig = None
    agentmesh: AgentMeshConfig = None
    analyzer: AnalyzerConfig = None
    trace: TraceConfig = None
    metrics: MetricsConfig = None
    visualization: VisualizationConfig = None
    verbose: bool = True
    save_intermediate: bool = True
    resume_from_checkpoint: bool = True

    def __post_init__(self):
        if self.data is None:
            self.data = DataConfig()
        if self.model is None:
            self.model = ModelConfig()
        if self.agentmesh is None:
            self.agentmesh = AgentMeshConfig()
        if self.analyzer is None:
            self.analyzer = AnalyzerConfig()
        if self.trace is None:
            self.trace = TraceConfig()
        if self.metrics is None:
            self.metrics = MetricsConfig()
        if self.visualization is None:
            self.visualization = VisualizationConfig()


def validate_config(config: ExperimentConfig) -> None:
    """Validate configuration constraints."""
    assert config.data.target_sample_size > 0
    assert config.data.min_samples_per_cwe > 0
    assert config.data.seed >= 0
    assert 0 < config.model.temperature <= 2.0
    assert 0 < config.model.top_p <= 1.0
    assert config.model.max_new_tokens > 0
    assert config.agentmesh.max_debugger_iterations > 0
    assert config.agentmesh.timeout_per_task > 0
    assert 0 <= config.metrics.target_security_percentage <= 100
    assert config.metrics.target_kl_divergence >= 0
    assert 0 <= config.metrics.target_jaccard_agreement <= 1.0
    print("Configuration validation passed.")


CONFIG = ExperimentConfig()
