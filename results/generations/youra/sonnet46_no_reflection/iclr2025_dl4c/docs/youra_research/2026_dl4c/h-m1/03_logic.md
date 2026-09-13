# Logic: H-M1 — AST Node Reallocation Mechanism

**Version:** 1.0
**Date:** 2026-05-19
**Budget:** 11 subtasks (high-complexity modules only)

Applied: Standard Python module design pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from H-E1 actual code via filesystem (Serena MCP returned "no active project" error)
**Analyzed Path**: `docs/youra_research/20260519_dl4c/h-e1/code/`
**Relevant Symbols**:
- `ZSSNode(label, children)` — `ast_metric.py`
- `extract_semantic_ast(code: str) -> ZSSNode` — `ast_metric.py`
- `compute_ast_semantic_edit_distance(code_a: str, code_b: str) -> float` — `ast_metric.py`
- `batch_ast_edit_distances(reference_codes: dict, candidate_codes: dict) -> dict` — `ast_metric.py`
- `match_checkpoints(grpo_kl_log: list, dpo_kl_log: list, tolerance: float = 0.05) -> list` — `kl_metric.py`
- `load_checkpoint_kl_log(checkpoint_dir: str) -> list` — `kl_metric.py`
- `generate_solutions(model_dir: str, problems: dict, cfg: ExperimentConfig, max_new_tokens: int = 512) -> dict` — `evaluate.py`
- `bootstrap_ci(values: list, n_samples: int = 10000, ci: float = 0.95, seed: int = 42) -> dict` — `evaluate.py`
- `SEMANTIC_NODE_TYPES: frozenset` — flat set in `ast_metric.py` (no CF/DF taxonomy split)

---

## External Dependencies API (Base Hypothesis H-E1)

Signatures verified from actual H-E1 code — NOT from specs.

```python
# From: h-e1/code/ast_metric.py
SEMANTIC_NODE_TYPES: frozenset  # {"If","For","While","Try","With","Assign","AugAssign","Call","Return"}

class ZSSNode:
    def __init__(self, label: str, children: list): ...

def extract_semantic_ast(code: str) -> ZSSNode:
    """Raises ValueError on SyntaxError."""

def compute_ast_semantic_edit_distance(code_a: str, code_b: str) -> float:
    """Returns float('inf') on parse failure."""

def batch_ast_edit_distances(
    reference_codes: dict,   # {task_id: str}
    candidate_codes: dict,   # {task_id: str}
) -> dict:                   # {task_id: float}
    ...

# From: h-e1/code/kl_metric.py
def load_checkpoint_kl_log(checkpoint_dir: str) -> list:
    """Returns [{step: int, kl_divergence: float}, ...] or [] if missing."""

def match_checkpoints(
    grpo_kl_log: list,
    dpo_kl_log: list,
    tolerance: float = 0.05,
) -> list:
    """Returns [{grpo_step, dpo_step, kl_grpo, kl_dpo}, ...]"""

# From: h-e1/code/evaluate.py
def generate_solutions(
    model_dir: str,
    problems: dict,
    cfg: ExperimentConfig,
    max_new_tokens: int = 512,
) -> dict:
    """Returns {task_id: completion_str}"""

def bootstrap_ci(
    values: list,
    n_samples: int = 10000,
    ci: float = 0.95,
    seed: int = 42,
) -> dict:
    """Returns {mean: float, lower: float, upper: float, n: int}"""
```

**Critical notes**:
- `generate_solutions` takes `cfg: ExperimentConfig` (H-E1 type), not `M1ExperimentConfig`. H-M1 must build a minimal `ExperimentConfig` shim or pass compatible dtype/device params.
- `match_checkpoints` default tolerance is `0.05`, but H-M1 uses `0.15` — always pass explicitly.
- `bootstrap_ci` has `seed=42` default; H-M1 uses `seed=1` — always pass explicitly.

---

## A-2: AST Decomposition Module [Complexity: 14, Budget: 3 subtasks]

**File**: `ast_decomposition.py`

### API Signatures

```python
import ast
import zss
from typing import Optional

# FA-AST taxonomy (arxiv:2002.08653)
CONTROL_FLOW_NODES: frozenset = frozenset({
    "If", "For", "While", "Try", "With", "ExceptHandler", "Break", "Continue",
})

DATA_FLOW_NODES: frozenset = frozenset({
    "Assign", "AugAssign", "AnnAssign", "Call", "Return", "Yield",
    "Import", "ImportFrom", "FunctionDef", "AsyncFunctionDef",
})

# Surface = everything else (ast.Constant, ast.Name, ast.Expr, ast.Pass, ast.Global, ...)


def classify_ast_node(node_type: str) -> str:
    """Classify AST node type into FA-AST category.
    Returns: "control_flow" | "data_flow" | "surface"
    """
    ...


def strip_docstrings_comments(code: str) -> str:
    """Normalize code: remove docstrings and comment lines.
    Returns normalized source string; returns original on parse failure.
    """
    ...


def _build_full_zss_tree(node: ast.AST) -> "ZSSNodeFull":
    """Recursively build full ZSS tree (all node types, not filtered)."""
    ...


def ast_to_zss_full(tree: ast.AST) -> "ZSSNodeFull":
    """Convert Python AST to full ZSS tree (includes all node types).
    Unlike H-E1 extract_semantic_ast, does NOT filter to SEMANTIC_NODE_TYPES.
    """
    ...


def extract_edit_operations(
    tree_base: "ZSSNodeFull",
    tree_new: "ZSSNodeFull",
) -> list[tuple[str, str]]:
    """Extract edit operations via ZSS.
    Returns list of (op_type, node_type_label) where op_type in {"insert","remove","update"}.
    Uses zss.simple_distance with operation capture.
    """
    ...


def compute_edit_distribution(
    code_base: str,
    code_new: str,
) -> Optional[dict]:
    """Compute per-category edit proportions between two code strings.

    Returns:
        {
          "control_flow": float,   # fraction of edits in CF nodes
          "data_flow": float,      # fraction of edits in DF nodes
          "surface": float,        # fraction of edits in surface nodes
          "semantic": float,       # control_flow + data_flow
          "total_edits": int,
        }
        None if either code fails to parse.
    """
    ...


def compute_sep(code_base: str, code_new: str) -> Optional[float]:
    """Semantic Edit Proportion = (CF_edits + DF_edits) / total_edits.
    Returns None on parse failure or zero total_edits.
    """
    ...


def compute_node_type_frequencies(
    codes: list[str],
    node_types: list[str],
) -> dict[str, int]:
    """Count occurrences of each node_type across all code strings.
    Skips unparseable codes. Used for heatmap data.
    Returns {node_type: count}.
    """
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Taxonomy + classify | Define CF/DF/surface frozensets; implement `classify_ast_node`; unit-testable boundary cases |
| L-2-2 | AST normalization + full ZSS tree | `strip_docstrings_comments` (ast.NodeTransformer removing Expr(Constant)); `ast_to_zss_full` building ZSSNodeFull for all nodes; `extract_edit_operations` using zss cost matrix |
| L-2-3 | Distribution + SEP + freq | `compute_edit_distribution`, `compute_sep`, `compute_node_type_frequencies`; handle None/inf/zero-edit edge cases |

### Pseudo-code for `extract_edit_operations`

```
1. ops = []
2. cost, operations = zss.distance_with_operations(
       tree_base, tree_new,
       get_children=lambda n: n.children,
       get_label=lambda n: n.label,
   )
3. for op in operations:
       if op.type == zss.Operation.insert:
           ops.append(("insert", op.arg2.label))
       elif op.type == zss.Operation.remove:
           ops.append(("remove", op.arg1.label))
       elif op.type == zss.Operation.update:
           ops.append(("update", op.arg1.label))
4. return ops
```

Note: `zss` exposes `simple_distance` but not `distance_with_operations` directly in all versions.
Fallback: use `zss.distance` with custom `update_cost_fn` that appends to a shared list during traversal.
If `zss` does not support operation extraction, implement Zhang-Shasha manually or use node-type frequency diff as approximation.

### Pseudo-code for `strip_docstrings_comments`

```
1. tree = ast.parse(code)
2. For each FunctionDef/AsyncFunctionDef/ClassDef/Module node:
       if first stmt is Expr(Constant(str)): remove it
3. return ast.unparse(tree)  # Python 3.9+
```

---

## A-4: SEP Analysis Module [Complexity: 15, Budget: 4 subtasks]

**File**: `sep_analysis.py`

### API Signatures

```python
import os
import json
import logging
import numpy as np
from typing import Optional
from config import M1ExperimentConfig

logger = logging.getLogger(__name__)


def load_checkpoint_solutions(
    checkpoint_path: str,
    problems: dict,              # {task_id: {prompt, ...}}
    cfg: M1ExperimentConfig,
    cache_dir: Optional[str] = None,
) -> dict:                       # {task_id: completion_str}
    """Load or generate solutions for a checkpoint.
    Cache: {cache_dir}/{checkpoint_basename}_solutions.json
    Uses H-E1 generate_solutions with ExperimentConfig shim.
    """
    ...


def _make_h_e1_config(cfg: M1ExperimentConfig) -> "ExperimentConfig":
    """Build minimal H-E1 ExperimentConfig from M1ExperimentConfig for generate_solutions."""
    ...


def compute_sep_for_checkpoint_pair(
    grpo_checkpoint: str,
    dpo_checkpoint: str,
    reference_solutions: dict,   # {task_id: str}
    problems: dict,
    cfg: M1ExperimentConfig,
) -> dict:
    """Compute per-problem SEP for one KL-matched checkpoint pair.

    Returns:
        {
          "sep_grpo": list[float],      # one per problem (None excluded)
          "sep_dpo": list[float],
          "edit_dist_grpo": dict,       # {task_id: edit_distribution_dict}
          "edit_dist_dpo": dict,
          "kl_grpo": float,
          "kl_dpo": float,
          "step_grpo": int,
          "step_dpo": int,
          "n_valid_grpo": int,
          "n_valid_dpo": int,
          "n_invalid_grpo": int,
          "n_invalid_dpo": int,
        }
    """
    ...


def aggregate_sep_across_pairs(
    grpo_checkpoint_dir: str,
    dpo_checkpoint_dir: str,
    reference_solutions: dict,
    problems: dict,
    cfg: M1ExperimentConfig,
    condition_label: str = "grpo_binary",
) -> dict:
    """Iterate all KL-matched pairs; collect SEP across problems × pairs.

    Returns:
        {
          "sep_grpo": list[float],      # all valid SEP values (problems × pairs)
          "sep_dpo": list[float],
          "pairs": list[dict],          # per-pair results from compute_sep_for_checkpoint_pair
          "pass_at_1_per_step": dict,   # {step: float} from checkpoint eval
          "condition": str,
          "n_pairs": int,
        }
    """
    ...


def compute_bootstrap_ci_sep(
    sep_values: list[float],
    cfg: M1ExperimentConfig,
) -> dict:
    """Bootstrap CI for mean SEP. Delegates to H-E1 bootstrap_ci.

    Returns: {mean: float, lower: float, upper: float, n: int}
    """
    ...


def collect_all_conditions(
    cfg: M1ExperimentConfig,
    problems: dict,
    reference_solutions: dict,
) -> dict:
    """Run aggregate_sep_across_pairs for all 3 conditions.

    Returns:
        {
          "grpo_binary":    aggregate_sep result dict,
          "grpo_errortype": aggregate_sep result dict,
          "dpo":            aggregate_sep result dict,
          "ci": {
              "grpo_binary":    bootstrap CI dict,
              "grpo_errortype": bootstrap CI dict,
              "dpo":            bootstrap CI dict,
          }
        }
    """
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Cache + solution loading | `load_checkpoint_solutions` with JSON cache; `_make_h_e1_config` shim translating M1 → H-E1 config fields |
| L-4-2 | Per-pair SEP computation | `compute_sep_for_checkpoint_pair`: load KL logs, load solutions, call `compute_sep` per problem, collect stats |
| L-4-3 | Cross-pair aggregation | `aggregate_sep_across_pairs`: discover checkpoint dirs, call `match_checkpoints(tolerance=cfg.kl_tolerance)`, loop 27 pairs, flatten SEP lists |
| L-4-4 | Bootstrap CI + all-conditions collector | `compute_bootstrap_ci_sep` wrapping H-E1 `bootstrap_ci(seed=cfg.seed)`; `collect_all_conditions` orchestrating 3 conditions |

### Pseudo-code for `aggregate_sep_across_pairs`

```
1. grpo_kl_log = load_checkpoint_kl_log(grpo_checkpoint_dir + "/kl_log.json")
2. dpo_kl_log  = load_checkpoint_kl_log(dpo_checkpoint_dir + "/kl_log.json")
3. pairs = match_checkpoints(grpo_kl_log, dpo_kl_log, tolerance=cfg.kl_tolerance)
   # Expected: ~27 pairs
4. all_sep_grpo, all_sep_dpo = [], []
5. pair_results = []
6. for pair in pairs:
       grpo_ckpt = f"{grpo_checkpoint_dir}/checkpoint-{pair['grpo_step']}"
       dpo_ckpt  = f"{dpo_checkpoint_dir}/checkpoint-{pair['dpo_step']}"
       result = compute_sep_for_checkpoint_pair(
           grpo_ckpt, dpo_ckpt, reference_solutions, problems, cfg
       )
       all_sep_grpo.extend(result["sep_grpo"])
       all_sep_dpo.extend(result["sep_dpo"])
       pair_results.append({**pair, **result})
7. return {
       "sep_grpo": all_sep_grpo,
       "sep_dpo": all_sep_dpo,
       "pairs": pair_results,
       "condition": condition_label,
       "n_pairs": len(pairs),
   }
```

### Data Shape Notes

| Variable | Shape / Type | Note |
|----------|-------------|-------|
| `sep_grpo` (per pair) | `list[float]`, len ≤ 542 | One per valid problem |
| `sep_grpo` (aggregated) | `list[float]`, len ≤ 542×27 = 14634 | All pairs flattened |
| `edit_dist_grpo` | `dict[task_id, dict]` | Per-problem edit distribution |

---

## A-7: Orchestrator [Complexity: 13, Budget: 2 subtasks]

**File**: `run_m1_analysis.py`

### API Signatures

```python
import sys
import os
import json
import logging
import argparse
from typing import Optional
from config import M1ExperimentConfig, get_config, load_config_from_yaml

logger = logging.getLogger(__name__)


def check_h_e1_checkpoints(cfg: M1ExperimentConfig) -> dict:
    """Verify H-E1 checkpoint directories and kl_log.json files exist.

    Returns:
        {
          "grpo_binary_available": bool,
          "grpo_errortype_available": bool,
          "dpo_available": bool,
          "checkpoint_paths": {
              "grpo_binary": str,
              "grpo_errortype": str,
              "dpo": str,
          },
          "all_available": bool,  # AND of all three
        }
    """
    ...


def load_problems(cfg: M1ExperimentConfig) -> dict:
    """Load HumanEval+ (164) + MBPP+ (378) via evalplus.

    Returns: {task_id: {prompt, canonical_solution, ...}}  # 542 total
    """
    ...


def load_reference_solutions(
    problems: dict,
    cfg: M1ExperimentConfig,
    cache_path: Optional[str] = None,
) -> dict:
    """Generate or load SFT-only reference solutions from base model.

    Cache: {cfg.output_dir}/reference_solutions.json
    Uses H-E1 generate_solutions with sft_model_id.
    Returns: {task_id: completion_str}
    """
    ...


def run_analysis(cfg: M1ExperimentConfig) -> dict:
    """Main pipeline. Returns full results dict.

    Steps:
        1. check_h_e1_checkpoints → if not all_available: trigger train_from_scratch
        2. load_problems + load_reference_solutions
        3. collect_all_conditions → sep_results
        4. run_all_statistical_tests
        5. verify_mechanism_activated
        6. save sep_results.json
        7. generate_all_figures
    Returns full results dict including gate_satisfied bool.
    """
    ...


def main() -> None:
    """Entry point. Exits 0 on success, 1 if gate fails."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Checkpoint discovery + data loading | `check_h_e1_checkpoints`, `load_problems`, `load_reference_solutions` with caching; argparse for `--config` and `--smoke-test` flags |
| L-7-2 | Full pipeline orchestration | `run_analysis`: wire all modules, structured logging, JSON output, figure trigger, gate check, `sys.exit(0/1)` |

### Pseudo-code for `run_analysis`

```
1. ckpt_status = check_h_e1_checkpoints(cfg)
2. if not ckpt_status["all_available"]:
       logger.warning("H-E1 checkpoints missing; triggering train_from_scratch")
       from train_from_scratch import train_grpo_binary, train_grpo_errortype, train_dpo
       # update cfg checkpoint dirs with returned paths
3. problems = load_problems(cfg)
4. reference_solutions = load_reference_solutions(problems, cfg)
5. sep_results = collect_all_conditions(cfg, problems, reference_solutions)
6. stat_results = run_all_statistical_tests(
       sep_grpo_binary=sep_results["grpo_binary"]["sep_grpo"],
       sep_grpo_errortype=sep_results["grpo_errortype"]["sep_grpo"],
       sep_dpo=sep_results["dpo"]["sep_dpo"],
       pass_at_1_grpo_binary=...,
       pass_at_1_grpo_errortype=...,
       reward_signals_binary=...,
       reward_signals_errortype=...,
       cfg=cfg,
   )
7. gate_ok, gate_detail, effect_size = verify_mechanism_activated(
       sep_results["grpo_binary"]["sep_grpo"],
       sep_results["dpo"]["sep_dpo"],
       stat_results,
   )
8. full_results = {
       "sep_results": sep_results,
       "stat_results": stat_results,
       "gate": {"satisfied": gate_ok, "detail": gate_detail, "effect_size": effect_size},
       "config": asdict(cfg),
   }
9. save full_results to {cfg.output_dir}/sep_results.json
10. generate_all_figures(full_results, cfg)
11. return full_results
```

---

## A-6: Visualization Module [Complexity: 12, Budget: 2 subtasks]

**File**: `visualize_m1.py`

### API Signatures

```python
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import M1ExperimentConfig


def plot_gate_sep_comparison(
    sep_results: dict,   # output of collect_all_conditions
    ci_results: dict,    # {"grpo_binary": CI_dict, "grpo_errortype": CI_dict, "dpo": CI_dict}
    output_path: str,
) -> None:
    """FR-7.1 MANDATORY: Bar chart — mean SEP per condition with 95% CI error bars.
    Conditions on x-axis: GRPO-binary, GRPO-error-type, DPO.
    Saves to output_path.
    """
    ...


def plot_ast_edit_distribution(
    edit_distributions: dict,   # {condition: {control_flow, data_flow, surface means}}
    output_path: str,
) -> None:
    """FR-7.2: Stacked horizontal bar — CF/DF/surface proportions per condition."""
    ...


def plot_reward_correctness_scatter(
    reward_signals: dict,    # {condition: list[float]} per checkpoint
    pass_at_1: dict,         # {condition: list[float]} per checkpoint
    spearman_results: dict,  # output of run_spearman_correlation
    output_path: str,
) -> None:
    """FR-7.3: Scatter — reward signal vs pass@1, annotated with Spearman rho."""
    ...


def plot_sep_vs_kl_trajectory(
    pairs_data: dict,   # {"grpo_binary": pairs list, "dpo": pairs list}
    output_path: str,
) -> None:
    """FR-7.4: Line plot — mean SEP vs KL divergence over training steps, GRPO vs DPO."""
    ...


def plot_ast_node_heatmap(
    node_freq_grpo: dict,   # {node_type: count}
    node_freq_dpo: dict,    # {node_type: count}
    node_types: list[str],  # ["If","For","While","Assign","Call","Return"]
    output_path: str,
) -> None:
    """FR-7.5: Seaborn heatmap — normalized AST node frequencies, GRPO vs DPO rows."""
    ...


def generate_all_figures(
    sep_results: dict,       # full results dict from run_analysis
    cfg: M1ExperimentConfig,
) -> None:
    """Call all 5 plot functions. Saves to cfg.figures_dir. Creates dir if missing."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Gate figure + edit distribution | `plot_gate_sep_comparison` (MANDATORY bar+CI), `plot_ast_edit_distribution` (stacked bar) |
| L-6-2 | Scatter + trajectory + heatmap + orchestrator | `plot_reward_correctness_scatter`, `plot_sep_vs_kl_trajectory`, `plot_ast_node_heatmap`, `generate_all_figures` |

### Data shape for heatmap

```
# Input matrix construction:
matrix = np.array([
    [node_freq_grpo[n] / total_grpo for n in node_types],   # row 0: GRPO
    [node_freq_dpo[n]  / total_dpo  for n in node_types],   # row 1: DPO
])  # shape: [2, 6]
# Seaborn: sns.heatmap(matrix, xticklabels=node_types, yticklabels=["GRPO","DPO"])
```

---

## Summary: Subtask Allocation

| Module | Subtasks | IDs |
|--------|----------|-----|
| A-2 AST Decomposition | 3 | L-2-1, L-2-2, L-2-3 |
| A-4 SEP Analysis | 4 | L-4-1, L-4-2, L-4-3, L-4-4 |
| A-7 Orchestrator | 2 | L-7-1, L-7-2 |
| A-6 Visualization | 2 | L-6-1, L-6-2 |
| **Total** | **11** | within budget |

---

## Key Implementation Notes for Phase 4 Coder

1. `generate_solutions` requires `ExperimentConfig` (H-E1 type). Use `_make_h_e1_config` shim in `sep_analysis.py` to adapt M1 config.
2. `match_checkpoints` default tolerance is `0.05`; always pass `tolerance=cfg.kl_tolerance` (default `0.15`).
3. `bootstrap_ci` seed default is `42`; pass `seed=cfg.seed` explicitly.
4. H-E1 `SEMANTIC_NODE_TYPES` is a flat frozenset — H-M1 adds full taxonomy. Do NOT import `SEMANTIC_NODE_TYPES` from H-E1; define own `CONTROL_FLOW_NODES` and `DATA_FLOW_NODES`.
5. `zss` operation extraction: if `zss.distance_with_operations` is unavailable, fall back to node-type frequency difference between `ast_to_zss_full` traversals as approximation for `extract_edit_operations`.
6. `strip_docstrings_comments` must use `ast.unparse` (Python ≥3.9). Pin requirement accordingly.
7. All figures must call `plt.tight_layout()` and `plt.savefig(output_path, dpi=150, bbox_inches="tight")` before `plt.close()`.
