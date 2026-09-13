"""HC1Config: RLHF Calibration Moderation Experiment configuration."""
import sys, os
import importlib.util

_HE1_CODE = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../h-e1/code"))

def _import_he1_config():
    spec = importlib.util.spec_from_file_location("he1_config", os.path.join(_HE1_CODE, "config.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.ExperimentConfig

ExperimentConfig = _import_he1_config()

# Add h-e1 to sys.path for other modules (append so h-c1 stays at front)
if _HE1_CODE not in sys.path:
    sys.path.append(_HE1_CODE)

from dataclasses import dataclass, field
from typing import List, Dict, Tuple


@dataclass
class HC1Config(ExperimentConfig):
    # Models: base first, chat second
    models: List[str] = field(default_factory=lambda: [
        "meta-llama/Llama-2-7b-hf",
        "meta-llama/Llama-2-7b-chat-hf",
    ])

    # Subsample sizes
    subsample_clean: int = 1000
    subsample_adv: int = 1000
    n_bins: int = 15

    # Eval cells: cell_id -> (clean_key, adv_key)
    eval_cells: Dict[str, Tuple[str, str]] = field(default_factory=lambda: {
        "NLI-AdvGLUE":  ("mnli",      "advglue_mnli"),
        "NLI-ANLI-R1":  ("multi_nli", "anli_r1"),
        "NLI-ANLI-R2":  ("multi_nli", "anli_r2"),
        "NLI-ANLI-R3":  ("multi_nli", "anli_r3"),
    })

    # Gate thresholds
    moderation_rate_threshold: float = 0.60
    ddece_nli_threshold: float = 0.01

    # H-E1 baseline for consistency check
    he1_base_ece_clean_nli: float = 0.279
    he1_base_delta_ece_nli: float = 0.071
    consistency_tolerance: float = 0.005
    consistency_failure_mode: str = "warn"

    # Paths
    results_dir: str = "docs/youra_research/h-c1/results"
    figures_dir: str = "docs/youra_research/h-c1/figures"
    errors_log: str = "docs/youra_research/h-c1/results/errors.log"
    results_file: str = "docs/youra_research/h-c1/results/hc1_results.json"
    validation_report: str = "docs/youra_research/h-c1/04_validation.md"
