"""HC1V2Config — extends HC1Config from h-c1."""
import sys, os
_HC1_CODE = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../h-c1/code"))
if _HC1_CODE not in sys.path:
    sys.path.append(_HC1_CODE)  # append so h-c1-v2/code stays at front

import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("hc1_config", os.path.join(_HC1_CODE, "config.py"))
_hc1_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_hc1_mod)
HC1Config = _hc1_mod.HC1Config
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class HC1V2Config(HC1Config):
    models: List[str] = field(default_factory=lambda: [
        "meta-llama/Llama-2-7b-hf",
        "meta-llama/Llama-2-7b-chat-hf",
        "meta-llama/Llama-2-13b-chat-hf",
    ])

    anli_cells: List[str] = field(default_factory=lambda: [
        "NLI-ANLI-R1", "NLI-ANLI-R2", "NLI-ANLI-R3"
    ])
    advglue_cells: List[str] = field(default_factory=lambda: ["NLI-AdvGLUE"])

    model_pairs: List[Tuple[str, str]] = field(default_factory=lambda: [
        ("meta-llama/Llama-2-7b-hf", "meta-llama/Llama-2-7b-chat-hf"),
        ("meta-llama/Llama-2-7b-hf", "meta-llama/Llama-2-13b-chat-hf"),
    ])

    h_c1_results_file: str = "docs/youra_research/h-c1/results/hc1_results.json"
    h_m1_label_mask_path: str = "docs/youra_research/h-m1/results/label_preservation_mask.npy"

    moderation_rate_threshold: float = 0.60
    ddece_threshold: float = 0.01

    results_dir: str = "docs/youra_research/h-c1-v2/results"
    figures_dir: str = "docs/youra_research/h-c1-v2/figures"
    results_file: str = "docs/youra_research/h-c1-v2/results/hc1v2_results.json"
    validation_report: str = "docs/youra_research/h-c1-v2/04_validation.md"
    errors_log: str = "docs/youra_research/h-c1-v2/results/errors.log"
    new_inference_output: str = "docs/youra_research/h-c1-v2/results/13b_chat"

    seed: int = 1
    subsample_clean: int = 1000
    n_bins: int = 15
