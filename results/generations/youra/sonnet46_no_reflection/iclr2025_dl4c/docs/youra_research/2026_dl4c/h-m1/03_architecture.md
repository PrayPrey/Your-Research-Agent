# Architecture: H-M1 — AST Node Reallocation Mechanism

**Version:** 1.0
**Date:** 2026-05-19
**Hypothesis Type:** MECHANISM (INCREMENTAL on H-E1)
**Infrastructure Tier:** FULL (YAML + dataclass config, structured logging, unit tests)

Applied: incremental-analysis-layer pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code (H-E1 actual implementation read via filesystem)
**Analyzed Path**: `docs/youra_research/20260519_dl4c/h-e1/code/`
**Findings**: H-E1 has 15 Python files. Key verified APIs: `ZSSNode`, `compute_ast_semantic_edit_distance`, `batch_ast_edit_distances` in `ast_metric.py`; `compute_kl_divergence`, `match_checkpoints`, `load_checkpoint_kl_log` in `kl_metric.py`; `generate_solutions`, `bootstrap_ci`, `compute_semantic_edit_per_kl`, `run_full_evaluation` in `evaluate.py`; `ExperimentConfig`, `get_config`, `make_grpo_config`, `make_dpo_config` in `config.py`.

Note: Serena MCP returned "no active project" error; H-E1 code was read directly via filesystem Read tool as fallback.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual H-E1 Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ZSSNode | `sys.path.insert(0, h_e1_code_path); from ast_metric import ZSSNode` | `h-e1/code/ast_metric.py` |
| compute_ast_semantic_edit_distance | `from ast_metric import compute_ast_semantic_edit_distance` | `h-e1/code/ast_metric.py` |
| batch_ast_edit_distances | `from ast_metric import batch_ast_edit_distances` | `h-e1/code/ast_metric.py` |
| match_checkpoints | `from kl_metric import match_checkpoints` | `h-e1/code/kl_metric.py` |
| load_checkpoint_kl_log | `from kl_metric import load_checkpoint_kl_log` | `h-e1/code/kl_metric.py` |
| generate_solutions | `from evaluate import generate_solutions` | `h-e1/code/evaluate.py` |
| bootstrap_ci | `from evaluate import bootstrap_ci` | `h-e1/code/evaluate.py` |
| ExperimentConfig | `from config import ExperimentConfig` | `h-e1/code/config.py` |

**Verified from**: `docs/youra_research/20260519_dl4c/h-e1/code/` (actual implementation)

**Note**: H-E1 `SEMANTIC_NODE_TYPES` in `ast_metric.py` is a flat frozenset without control-flow/data-flow taxonomy split — H-M1 extends this with the full FA-AST 3-category taxonomy.

---

## File Organization

H-M1 code lives at: `docs/youra_research/20260519_dl4c/h-m1/code/`

- `config.py` — M1ExperimentConfig dataclass
- `ast_decomposition.py` — FA-AST taxonomy, edit distribution computation
- `sep_analysis.py` — SEP aggregation across problems and checkpoint pairs
- `statistical_tests.py` — Mann-Whitney U, Spearman rho, mechanism verification
- `visualize_m1.py` — 5 required figures
- `run_m1_analysis.py` — top-level orchestrator
- `train_from_scratch.py` — re-training fallback (if H-E1 checkpoints absent)
- `tests/test_ast_decomposition.py` — unit tests for taxonomy
- `tests/test_sep_analysis.py` — unit tests for SEP computation
- `tests/test_statistical_tests.py` — unit tests for stat tests

Output paths:
- `h-m1/outputs/sep_results.json`
- `h-m1/figures/gate_sep_comparison.png`
- `h-m1/figures/ast_edit_distribution.png`
- `h-m1/figures/reward_correctness_scatter.png`
- `h-m1/figures/sep_vs_kl_trajectory.png`
- `h-m1/figures/ast_node_heatmap.png`

---

## Module Definitions

### M1ExperimentConfig (`config.py`)

**Dependencies**: dataclasses, yaml, H-E1 ExperimentConfig (reference)

```python
from dataclasses import dataclass, field

@dataclass
class M1ExperimentConfig:
    # Paths
    h_e1_code_path: str = "../../h-e1/code"
    h_e1_checkpoint_base: str = "../../h-e1/checkpoints"
    grpo_binary_checkpoint_dir: str = "../../h-e1/checkpoints/grpo_binary"
    grpo_errortype_checkpoint_dir: str = "../../h-e1/checkpoints/grpo_errortype"
    dpo_checkpoint_dir: str = "../../h-e1/checkpoints/dpo"
    sft_model_id: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
    output_dir: str = "../outputs"
    figures_dir: str = "../figures"

    # Experiment
    seed: int = 1
    kl_tolerance: float = 0.15
    bootstrap_samples: int = 10000
    bootstrap_ci: float = 0.95
    dtype: str = "bfloat16"
    max_new_tokens: int = 512

    # Gate
    mann_whitney_alpha: float = 0.05
    spearman_rho_threshold: float = 0.5

def get_config() -> M1ExperimentConfig: ...
def load_config_from_yaml(path: str) -> M1ExperimentConfig: ...
def save_config_to_yaml(cfg: M1ExperimentConfig, path: str) -> None: ...
```

---

### ASTDecomposition (`ast_decomposition.py`)

**Dependencies**: ast (stdlib), zss, H-E1 ZSSNode (ast_metric.py)

```python
import ast
from typing import Optional

CONTROL_FLOW_NODES: frozenset  # {ast.If, ast.For, ast.While, ast.Try, ...}
DATA_FLOW_NODES: frozenset     # {ast.Assign, ast.Call, ast.Return, ...}
SURFACE_NODES: frozenset       # {ast.Constant, ast.Name, ast.Expr, ...}

def classify_ast_node(node_type: str) -> str: ...
# Returns: "control_flow" | "data_flow" | "surface"

def strip_docstrings_comments(code: str) -> str: ...
# Normalize AST: remove docstrings and comments

def ast_to_zss_full(tree: ast.AST) -> object: ...
# Full AST to zss.Node (unlike H-E1 which filters to SEMANTIC_NODE_TYPES only)

def extract_edit_operations(tree_base: object, tree_new: object) -> list[tuple[str, str]]: ...
# Returns list of (operation_type, node_type_label)

def compute_edit_distribution(
    code_base: str,
    code_new: str
) -> Optional[dict]: ...
# Returns {"control_flow": float, "data_flow": float, "surface": float,
#          "semantic": float, "total_edits": int}
# Returns None on parse failure; logs invalid rate

def compute_sep(code_base: str, code_new: str) -> Optional[float]: ...
# SEP = (control_flow_edits + data_flow_edits) / total_edits

def compute_node_type_frequencies(
    codes: list[str],
    node_types: list[str]
) -> dict[str, int]: ...
# Count occurrences of specific node types (for heatmap)
```

---

### SEPAnalysis (`sep_analysis.py`)

**Dependencies**: ast_decomposition, kl_metric (H-E1), evaluate (H-E1), config, numpy

```python
import sys
import numpy as np
from typing import Optional
from config import M1ExperimentConfig

def load_checkpoint_solutions(
    checkpoint_path: str,
    problems: dict,
    cfg: M1ExperimentConfig,
    cache_dir: Optional[str] = None,
) -> dict: ...
# Loads or generates {task_id: completion} for a checkpoint
# Uses H-E1 generate_solutions; caches to avoid re-generation

def compute_sep_for_checkpoint_pair(
    grpo_checkpoint: str,
    dpo_checkpoint: str,
    reference_solutions: dict,
    problems: dict,
    cfg: M1ExperimentConfig,
) -> dict: ...
# Returns {"sep_grpo": list[float], "sep_dpo": list[float],
#          "kl_grpo": float, "kl_dpo": float, "step_grpo": int, "step_dpo": int}

def aggregate_sep_across_pairs(
    grpo_checkpoint_dir: str,
    dpo_checkpoint_dir: str,
    reference_solutions: dict,
    problems: dict,
    cfg: M1ExperimentConfig,
    condition_label: str = "grpo_binary",
) -> dict: ...
# Iterates all 27 KL-matched pairs, collects SEP values
# Returns {"sep_grpo": list[float], "sep_dpo": list[float],
#          "pairs": list[dict], "pass_at_1_per_step": dict}

def compute_bootstrap_ci_sep(
    sep_values: list[float],
    cfg: M1ExperimentConfig,
) -> dict: ...
# Returns {"mean": float, "lower": float, "upper": float, "n": int}

def collect_all_conditions(
    cfg: M1ExperimentConfig,
    problems: dict,
    reference_solutions: dict,
) -> dict: ...
# Runs aggregate_sep_across_pairs for binary, errortype, dpo
# Returns {"grpo_binary": {...}, "grpo_errortype": {...}, "dpo": {...}}
```

---

### StatisticalTests (`statistical_tests.py`)

**Dependencies**: scipy.stats, numpy, config

```python
from scipy.stats import mannwhitneyu, spearmanr
import numpy as np
from config import M1ExperimentConfig

def run_mann_whitney_test(
    sep_grpo: list[float],
    sep_dpo: list[float],
) -> dict: ...
# Returns {"u_statistic": float, "p_value": float,
#          "effect_size": float, "significant": bool}
# Calls mannwhitneyu(sep_grpo, sep_dpo, alternative='greater')

def run_spearman_correlation(
    reward_signals: list[float],
    pass_at_1: list[float],
) -> dict: ...
# Returns {"rho": float, "p_value": float, "above_threshold": bool}

def run_all_statistical_tests(
    sep_grpo_binary: list[float],
    sep_grpo_errortype: list[float],
    sep_dpo: list[float],
    pass_at_1_grpo_binary: list[float],
    pass_at_1_grpo_errortype: list[float],
    reward_signals_binary: list[float],
    reward_signals_errortype: list[float],
    cfg: M1ExperimentConfig,
) -> dict: ...
# Returns full stats summary for both conditions

def verify_mechanism_activated(
    sep_grpo: list[float],
    sep_dpo: list[float],
    results: dict,
) -> tuple[bool, dict, float]: ...
# Checks: decomposition_working, semantic_proportion_valid,
#         grpo_higher (>50% pairs), statistically_significant (p<0.05)
```

---

### VisualizeM1 (`visualize_m1.py`)

**Dependencies**: matplotlib, seaborn, numpy, sep_analysis, statistical_tests, config

```python
from config import M1ExperimentConfig

def plot_gate_sep_comparison(
    sep_results: dict,
    ci_results: dict,
    output_path: str,
) -> None: ...
# FR-7.1 (MANDATORY): Bar chart: mean SEP per condition with 95% CI error bars
# Saves to h-m1/figures/gate_sep_comparison.png

def plot_ast_edit_distribution(
    edit_distributions: dict,
    output_path: str,
) -> None: ...
# FR-7.2: Stacked bar: control_flow/data_flow/surface proportions per condition

def plot_reward_correctness_scatter(
    reward_signals: dict,
    pass_at_1: dict,
    spearman_results: dict,
    output_path: str,
) -> None: ...
# FR-7.3: Scatter: reward signal vs pass@1 per checkpoint

def plot_sep_vs_kl_trajectory(
    pairs_data: dict,
    output_path: str,
) -> None: ...
# FR-7.4: Line: SEP vs KL divergence over training steps

def plot_ast_node_heatmap(
    node_freq_grpo: dict,
    node_freq_dpo: dict,
    node_types: list[str],
    output_path: str,
) -> None: ...
# FR-7.5: Heatmap: AST node type frequencies for GRPO vs DPO

def generate_all_figures(
    sep_results: dict,
    cfg: M1ExperimentConfig,
) -> None: ...
# Calls all 5 plot functions; saves to cfg.figures_dir
```

---

### RunM1Analysis (`run_m1_analysis.py`)

**Dependencies**: config, sep_analysis, statistical_tests, visualize_m1, H-E1 evaluate/kl_metric/data

```python
import sys
import os
import json
import logging
from config import M1ExperimentConfig, get_config

def check_h_e1_checkpoints(cfg: M1ExperimentConfig) -> dict: ...
# Returns {"grpo_binary_available": bool, "grpo_errortype_available": bool,
#          "dpo_available": bool, "checkpoint_paths": dict}

def load_problems(cfg: M1ExperimentConfig) -> dict: ...
# Loads HumanEval+ (164) + MBPP+ (378) via evalplus

def load_reference_solutions(
    problems: dict,
    cfg: M1ExperimentConfig,
) -> dict: ...
# Generates or loads SFT-only reference solutions from base model

def run_analysis(cfg: M1ExperimentConfig) -> dict: ...
# Main pipeline:
#   1. check_h_e1_checkpoints
#   2. load_problems + load_reference_solutions
#   3. collect_all_conditions (sep_analysis)
#   4. run_all_statistical_tests
#   5. verify_mechanism_activated
#   6. save sep_results.json
#   7. generate_all_figures
# Returns full results dict

def main() -> None: ...
# Entry point: parse args, load config, run_analysis, exit 0/1

if __name__ == "__main__":
    main()
```

---

### TrainFromScratch (`train_from_scratch.py`)

**Dependencies**: H-E1 train_grpo.py, train_dpo.py, config (H-E1 ExperimentConfig)

```python
def train_grpo_binary(cfg_path: str) -> str: ...
# Re-trains GRPO with binary reward using H-E1 train_grpo.py
# Returns checkpoint directory path

def train_grpo_errortype(cfg_path: str) -> str: ...
# Re-trains GRPO with error-type reward
# Returns checkpoint directory path

def train_dpo(cfg_path: str) -> str: ...
# Re-trains DPO using H-E1 train_dpo.py
# Returns checkpoint directory path

def main() -> None: ...
# Fallback only: called if check_h_e1_checkpoints returns False
```

---

## Module Dependencies

```
run_m1_analysis.py
  -> config.py
  -> sep_analysis.py
       -> ast_decomposition.py
       -> [H-E1] evaluate.py (generate_solutions)
       -> [H-E1] kl_metric.py (match_checkpoints, load_checkpoint_kl_log)
       -> [H-E1] data.py (load_humaneval_plus, load_mbpp_plus)
  -> statistical_tests.py
       -> config.py
  -> visualize_m1.py
       -> sep_analysis.py (result dicts)
       -> statistical_tests.py (result dicts)
  -> [H-E1] evaluate.py (bootstrap_ci)
train_from_scratch.py
  -> [H-E1] train_grpo.py
  -> [H-E1] train_dpo.py
  -> [H-E1] config.py
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create h-m1/code/ structure, config.py with M1ExperimentConfig, YAML support, requirements.txt with new deps (zss, scipy, seaborn) | 7 | 2+1+1+3 |
| A-2 | AST Decomposition Module | Implement ast_decomposition.py: FA-AST taxonomy, strip_docstrings_comments, ast_to_zss_full, extract_edit_operations, compute_edit_distribution, compute_sep, compute_node_type_frequencies | 14 | 4+2+5+3 |
| A-3 | Unit Tests for AST Decomposition | tests/test_ast_decomposition.py: taxonomy classification, edit op extraction, SEP computation, invalid code handling, normalization | 8 | 2+1+3+2 |
| A-4 | SEP Analysis Module | Implement sep_analysis.py: checkpoint solution loading/caching, per-pair SEP, aggregate across 27 pairs for 3 conditions, bootstrap CI | 15 | 4+4+4+3 |
| A-5 | Statistical Tests Module | Implement statistical_tests.py: Mann-Whitney U (both GRPO conditions vs DPO), Spearman rho, verify_mechanism_activated | 10 | 3+2+4+1 |
| A-6 | Visualization Module | Implement visualize_m1.py: 5 figures (gate bar, stacked bar, scatter, trajectory line, node heatmap) | 12 | 3+3+4+2 |
| A-7 | Orchestrator | Implement run_m1_analysis.py: checkpoint discovery, problem loading, reference solution generation, full pipeline, JSON output, figure trigger | 13 | 3+4+3+3 |
| A-8 | Train-from-Scratch Fallback | Implement train_from_scratch.py wrapping H-E1 trainers; triggered only if checkpoints missing | 9 | 2+4+2+1 |
| A-9 | Integration Test | Smoke test on 10 problems × 3 checkpoint pairs; validate sep_results.json schema and gate metric output | 10 | 2+3+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2, A-4, A-7], Medium(9-13): [A-5, A-6, A-8, A-9], Low(4-8): [A-1, A-3]
