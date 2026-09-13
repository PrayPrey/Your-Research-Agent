# H-M2 Architecture: Corpus Entropy → Model Logit Margin Internalization

Applied: dataclass-config-pattern, spearman-gate-pattern, verify-mechanism-activated-pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from base code (h-m1/code/)
**Analyzed Path**: `docs/youra_research/20260315_data_problems/h-m1/code/`
**Findings**: HM1Config dataclass with load_config(), StatisticalTests.run_all_tests() with spearman_correlation/ols_regression/evaluate_gate, verify_mechanism_activated() top-level function, Visualizer class pattern, 15-step main() pipeline in run_experiment.py.

---

## File Organization

- `h-m2/code/`
  - `config.py` — HM2Config dataclass, load_config()
  - `data_prep.py` — C7 negative control generation, tokenization orchestration
  - `train.py` — gpt-neox config generation, training launch orchestration
  - `probe.py` — logit margin computation (Gupta 2023 methodology)
  - `statistical_tests.py` — Spearman gate, log-linear OLS, negative control delta
  - `visualize.py` — 5 figures
  - `run_experiment.py` — top-level pipeline orchestrator
  - `tests/`
    - `test_probe.py`
    - `test_statistical_tests.py`
    - `conftest.py`
- `h-m2/configs/` — gpt-neox YAML files (pythia-1b-hm2-C{N}.yml, N=0..7)
- `h-m2/data/`
  - `tokenized/config_C{N}/` — .bin/.idx tokenized corpora
  - `probe_templates.json` — 50+ templates per demographic axis
- `h-m2/checkpoints/config_C{N}/` — Pythia-1B final checkpoints
- `h-m2/results/` — JSON results per config + aggregate
- `h-m2/figures/` — scatter, bar, heatmap, control, winobias plots

---

## Module Definitions

### HM2Config (`code/config.py`)

**Dependencies**: None (stdlib only)

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

HM1_CODE_DIR: str  # path to h-m1/code/
HE1_DATA_DIR: str  # path to h-e1/code/data/filtered/
HM2_BASE_DIR: str  # path to h-m2/

ALL_CONFIGS: List[str] = ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7"]
CORPUS_H_ENTROPY: Dict[str, float] = {
    "C0": 3.2662, "C1": 3.2702, "C2": 3.2528, "C3": 3.2275,
    "C4": 3.1106, "C5": 2.5374, "C6": 3.2209, "C7": 3.2275,
}

@dataclass
class HM2Config:
    # Paths
    hm1_code_dir: str = HM1_CODE_DIR
    he1_data_dir: str = HE1_DATA_DIR
    hm2_base_dir: str = HM2_BASE_DIR
    tokenized_dir: str  # h-m2/data/tokenized/
    checkpoints_dir: str  # h-m2/checkpoints/
    configs_dir: str  # h-m2/configs/
    results_dir: str  # h-m2/results/
    figures_dir: str  # h-m2/figures/
    probe_templates_path: str  # h-m2/data/probe_templates.json
    results_path: str  # h-m2/results/results.json
    validation_path: str  # h-m2/04_validation.md

    # Training hyperparameters
    hidden_size: int = 2048
    num_layers: int = 16
    num_attention_heads: int = 8
    vocab_size: int = 50304
    max_seq_len: int = 2048
    global_batch_size: int = 256
    lr: float = 2e-5
    train_iters_full: int = 190735   # 100B tokens
    train_iters_quick: int = 95368   # 50B tokens (PoC)
    seed: int = 42

    # Probe configuration
    n_probe_templates: int = 50      # min templates per demographic axis
    n_occupation_pairs: int = 20     # WinoBias occupation categories
    logit_margin_sanity_bound: float = 10.0  # |margin| < 10 sanity check

    # Statistical
    alpha_level: float = 0.01       # Spearman gate threshold
    negative_control_delta_threshold: float = 0.01  # |C7 - C0| ≤ 0.01
    n_bootstrap: int = 1000

    # Visualization
    dpi: int = 150
    figure_size: tuple = (10, 6)
    figure_size_heatmap: tuple = (14, 10)

    # Scale robustness (Pythia-160M)
    scale_check_configs: List[str] = field(
        default_factory=lambda: ["C1", "C3", "C5"]
    )

def load_config(yaml_path: Optional[str] = None) -> HM2Config: ...
```

---

### DataPrep (`code/data_prep.py`)

**Dependencies**: HM2Config

```python
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np

class DataPrep:
    def __init__(self, config: HM2Config): ...

    def generate_c7_negative_control(
        self,
        c3_tokenized_dir: str,
        output_dir: str,
        demographic_token_ids: List[int],
        seed: int = 42,
    ) -> None:
        """
        Load C3 .bin/.idx, collect demographic token positions,
        globally permute demographic tokens across all documents,
        write permuted corpus to output_dir as .bin/.idx.
        """
        ...

    def build_gptneox_yaml_config(
        self,
        config_id: str,
        train_data_path: str,
        output_yaml_path: str,
        train_iters: int,
    ) -> str:
        """
        Write gpt-neox YAML config for config_id (C0-C7).
        Sets: train-data-paths, global-batch-size, lr, train-iters,
              gradient-checkpointing, bf16/fp16, seed.
        Returns: path to written YAML.
        """
        ...

    def build_all_yaml_configs(
        self,
        quick: bool = False,
    ) -> Dict[str, str]:
        """
        Generate gpt-neox YAML configs for all 8 configurations.
        Returns: {config_id: yaml_path}
        """
        ...

    def load_probe_templates(self) -> Dict[str, List[str]]:
        """
        Load probe_templates.json.
        Returns: {"gender": [...50+ templates...], "occupation": [...]}
        """
        ...

    def get_demographic_token_ids(self, tokenizer) -> List[int]:
        """
        Return token IDs for demographic tokens (pronouns, gendered names, markers).
        Used for C7 generation.
        """
        ...
```

---

### TrainingOrchestrator (`code/train.py`)

**Dependencies**: HM2Config, DataPrep

```python
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

class TrainingOrchestrator:
    def __init__(self, config: HM2Config): ...

    def build_launch_command(
        self,
        yaml_config_path: str,
        cuda_device: int,
    ) -> List[str]:
        """
        Build gpt-neox deepy.py launch command.
        Returns: ['python', 'deepy.py', 'train.py', yaml_config_path]
        with CUDA_VISIBLE_DEVICES set.
        """
        ...

    def run_training(
        self,
        config_id: str,
        yaml_config_path: str,
        cuda_device: int,
        dry_run: bool = False,
    ) -> bool:
        """
        Launch training for config_id via subprocess.
        Blocks until completion. Returns True on success.
        """
        ...

    def checkpoint_exists(self, config_id: str) -> bool:
        """Check if final checkpoint dir exists for config_id."""
        ...

    def get_missing_checkpoints(self) -> List[str]:
        """Return list of config_ids missing final checkpoints."""
        ...
```

---

### LogitProbe (`code/probe.py`)

**Dependencies**: HM2Config

```python
import torch
from typing import Dict, List, Optional, Tuple
import numpy as np
from transformers import GPTNeoXForCausalLM, AutoTokenizer

OCCUPATION_PAIRS: List[Tuple[str, str]]  # (congruent, incongruent) pairs, 20+ WinoBias

class LogitProbe:
    def __init__(
        self,
        config: HM2Config,
        device: str = "cuda",
    ): ...

    def load_model(
        self,
        checkpoint_path: str,
        dtype: torch.dtype = torch.bfloat16,
    ) -> Tuple[GPTNeoXForCausalLM, AutoTokenizer]:
        """
        Load GPTNeoXForCausalLM from checkpoint_path.
        Tokenizer loaded from 'EleutherAI/pythia-1b'.
        Returns (model, tokenizer).
        """
        ...

    def compute_logit_margin(
        self,
        model: GPTNeoXForCausalLM,
        tokenizer: AutoTokenizer,
        prompt: str,
        congruent_word: str,
        incongruent_word: str,
    ) -> float:
        """
        Compute logit(congruent_word) - logit(incongruent_word) at last prompt position.
        Uses model(**inputs).logits[0, -1, :] (vocab_size,).
        """
        ...

    def compute_mean_logit_margin(
        self,
        model: GPTNeoXForCausalLM,
        tokenizer: AutoTokenizer,
        templates: List[str],
        occ_pairs: List[Tuple[str, str]],
    ) -> float:
        """
        Average logit margin over templates × occupation pairs (50+ × 20+).
        Returns scalar float.
        """
        ...

    def run_probe_for_config(
        self,
        config_id: str,
        probe_templates: Dict[str, List[str]],
    ) -> Dict[str, float]:
        """
        Load checkpoint for config_id, run probe on gender demographic axis.
        Returns: {"mean_logit_margin": float, "per_axis": {...}}
        """
        ...

    def run_all_configs(
        self,
        probe_templates: Dict[str, List[str]],
        config_ids: Optional[List[str]] = None,
    ) -> Dict[str, Dict[str, float]]:
        """
        Run probe pipeline for all config_ids (default: C0-C7).
        Returns: {config_id: {"mean_logit_margin": float, ...}}
        """
        ...

    def run_winobias_eval(
        self,
        config_id: str,
        cuda_device: int = 0,
    ) -> Dict[str, float]:
        """
        Launch lm_eval with --tasks winobias via subprocess for config_id.
        Parses output JSON. Returns {"pro_acc": float, "anti_acc": float, "gap": float}.
        """
        ...
```

---

### StatisticalTests (`code/statistical_tests.py`)

**Dependencies**: HM2Config; reuses patterns from `h-m1/code/statistical_tests.py`

```python
from typing import Any, Dict, List, Tuple
import numpy as np

class StatisticalTests:
    def __init__(
        self,
        n_bootstrap: int = 1000,
        seed: int = 42,
        alpha_level: float = 0.01,
        negative_control_threshold: float = 0.01,
    ): ...

    def spearman_correlation(
        self,
        corpus_entropy_values: List[float],
        model_logit_margins: List[float],
    ) -> Dict[str, float]:
        """
        Spearman ρ between H(occ|demo) and logit margins.
        Returns: {"rho": float, "pvalue": float}
        """
        ...

    def bootstrap_spearman_ci(
        self,
        corpus_entropy_values: List[float],
        model_logit_margins: List[float],
    ) -> Tuple[float, float]:
        """Bootstrap 95% CI for Spearman ρ. Returns (ci_low, ci_high)."""
        ...

    def log_linear_ols(
        self,
        corpus_entropy_values: List[float],
        model_logit_margins: List[float],
    ) -> Dict[str, float]:
        """
        Fit OLS: logit_margin ~ log(H_entropy).
        Returns: {"coef": float, "intercept": float, "r_squared": float, "pvalue": float}
        """
        ...

    def negative_control_delta(
        self,
        margin_c7: float,
        margin_c0: float,
    ) -> Dict[str, float]:
        """
        Compute |margin(C7) - margin(C0)|.
        Returns: {"delta": float, "passes_threshold": bool}
        """
        ...

    def winobias_spearman(
        self,
        corpus_entropy_values: List[float],
        winobias_gaps: List[float],
    ) -> Dict[str, float]:
        """
        Spearman ρ between H(occ|demo) and WinoBias accuracy gaps (secondary).
        Returns: {"rho": float, "pvalue": float}
        """
        ...

    def evaluate_gate(
        self,
        spearman_result: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Gate: rho > 0 AND pvalue < alpha_level (SHOULD_WORK).
        Returns: {"gate_passed": bool, "rho": float, "pvalue": float, "gate_type": str}
        """
        ...

    def run_all_tests(
        self,
        corpus_entropy_values: List[float],
        model_logit_margins: Dict[str, float],
        winobias_gaps: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Orchestrate: spearman, bootstrap_ci, log_linear_ols,
        negative_control_delta, winobias_spearman, gate.
        Returns: unified results dict.
        """
        ...
```

---

### Visualizer (`code/visualize.py`)

**Dependencies**: HM2Config

```python
from pathlib import Path
from typing import Dict, List, Any
import matplotlib.pyplot as plt

class Visualizer:
    def __init__(self, figures_dir: str, dpi: int = 150): ...

    def plot_scatter_entropy_vs_margin(
        self,
        corpus_entropy: Dict[str, float],
        logit_margins: Dict[str, float],
        spearman_rho: float,
        log_linear_fit: Dict[str, float],
    ) -> str:
        """Scatter: H(occ|demo) vs. logit margin, 8 labeled points + fit line. Returns path."""
        ...

    def plot_bar_margin_per_config(
        self,
        logit_margins: Dict[str, float],
        corpus_entropy: Dict[str, float],
    ) -> str:
        """Bar chart: mean logit margin C0-C7 sorted by H(occ|demo). Returns path."""
        ...

    def plot_negative_control_comparison(
        self,
        logit_margins: Dict[str, float],
        delta: float,
    ) -> str:
        """Grouped bar: C3 vs C7 vs C0 with delta annotation. Returns path."""
        ...

    def plot_per_axis_heatmap(
        self,
        per_axis_margins: Dict[str, Dict[str, float]],
    ) -> str:
        """Heatmap: logit margins × (demographic_axis × config). Returns path."""
        ...

    def plot_winobias_accuracy_gap(
        self,
        winobias_gaps: Dict[str, float],
    ) -> str:
        """Line chart: WinoBias anti-stereotypical accuracy gap across C0-C6. Returns path."""
        ...

    def generate_all(
        self,
        corpus_entropy: Dict[str, float],
        logit_margins: Dict[str, float],
        stats_results: Dict[str, Any],
        per_axis_margins: Dict[str, Dict[str, float]],
        winobias_gaps: Dict[str, float],
    ) -> Dict[str, str]:
        """Generate all 5 figures. Returns {figure_name: file_path}."""
        ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: HM2Config, DataPrep, TrainingOrchestrator, LogitProbe, StatisticalTests, Visualizer

```python
import argparse
import json
import logging
from pathlib import Path
from typing import Any, Dict

def parse_args() -> argparse.Namespace:
    """--quick, --skip-training, --skip-probe, --cuda-device, --config, --output-dir"""
    ...

def verify_mechanism_activated(
    logit_margins: Dict[str, float],
    stats_results: Dict[str, Any],
    config: HM2Config,
) -> Dict[str, bool]:
    """
    Returns: {
        "checkpoints_exist": bool,
        "logit_margins_computed": bool,     # all 8, |margin| < 10
        "ordering_matches_hm1": bool,       # margin(C5) > margin(C1)
        "spearman_positive": bool,
        "spearman_significant": bool,
        "negative_control_ok": bool,        # |C7-C0| <= 0.01
        "mechanism_activated": bool,        # all above AND gate_passed
    }
    """
    ...

def write_results_json(results: Dict[str, Any], path: str) -> None: ...

def write_validation_md(
    results: Dict[str, Any],
    mechanism_check: Dict[str, bool],
    path: str,
) -> None: ...

def main() -> None:
    """
    12-step H-M2 pipeline:
      1.  parse_args
      2.  load_config
      3.  mkdir dirs
      4.  data_prep: build_all_yaml_configs + generate_c7_negative_control
      5.  training: run 8 Pythia-1B configs (skip if --skip-training or checkpoints exist)
      6.  data_prep: load_probe_templates
      7.  probe: run_all_configs → logit_margins dict (skip if --skip-probe)
      8.  probe: run_winobias_eval for all configs → winobias_gaps dict
      9.  stats: run_all_tests
     10.  visualize: generate_all
     11.  verify_mechanism_activated
     12.  write_results_json + write_validation_md
    """
    ...
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| StatisticalTests | `from h_m1.statistical_tests import StatisticalTests` (pattern reuse, not direct import) | `h-m1/code/statistical_tests.py` |
| HM1Config/load_config | Pattern reference only | `h-m1/code/config.py` |
| verify_mechanism_activated | Pattern reference only | `h-m1/code/run_experiment.py` |
| CorpusFilter (h-e1) | Accessed via h-m1 pattern: `sys.path.insert(0, he1_code_dir)` | `h-e1/code/corpus_filter.py` |

**Note**: H-M2 does NOT directly import h-m1 modules at runtime. Statistical pipeline is reimplemented with H-M2-specific signatures (corpus_entropy inputs instead of filtering_intensities). Patterns are structural references.

**Verified from**: `h-m1/code/` (actual implementation)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup & Config | HM2Config dataclass, directory layout, probe_templates.json (50+ templates, 20 occ pairs) | 6 | 2+1+1+2 |
| A-2 | C7 Negative Control Generation | Load C3 .bin/.idx, identify demographic token IDs, globally permute, write new .bin/.idx | 14 | 3+2+4+5 |
| A-3 | gpt-neox YAML Config Generation | Write 8 YAML configs (C0-C7) with correct train-data-paths, lr, batch, iters, bf16 | 8 | 2+2+2+2 |
| A-4 | Training Orchestration | TrainingOrchestrator: build launch commands, subprocess execution, checkpoint verification | 10 | 2+2+3+3 |
| A-5 | Logit Margin Probe Pipeline | LogitProbe: GPTNeoXForCausalLM loading, compute_logit_margin (Gupta 2023), aggregate over 50+ templates × 20 pairs, run all 8 configs | 17 | 4+3+5+5 |
| A-6 | WinoBias Evaluation | lm_eval subprocess for all 8 configs, parse JSON results, compute accuracy gaps | 10 | 2+2+3+3 |
| A-7 | Statistical Tests | Spearman gate (rho>0, p<0.01), log-linear OLS (R²), negative control delta, WinoBias Spearman | 13 | 3+3+4+3 |
| A-8 | Pythia-160M Scale Check | Train 160M on C1/C3/C5, run probe, verify directional consistency margin(C5)>margin(C3)>margin(C1) | 14 | 3+3+4+4 |
| A-9 | Visualization | 5 figures: scatter+fit, bar-margin, negative-control grouped bar, per-axis heatmap, WinoBias line chart | 9 | 2+2+2+3 |
| A-10 | Mechanism Verification & Reporting | verify_mechanism_activated (7 checks), write_results_json, write_validation_md | 8 | 2+2+2+2 |
| A-11 | Unit & Integration Tests | test_probe (logit margin correctness, dtype, edge cases), test_statistical_tests (gate logic, OLS), integration smoke test | 10 | 2+3+3+2 |

**Distribution**:
- VeryHigh (18-20): []
- High (14-17): [A-5, A-2, A-8]
- Medium (9-13): [A-4, A-6, A-7, A-9, A-11]
- Low (4-8): [A-1, A-3, A-10]
