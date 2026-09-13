# Logic: h-m3 — Within-Prompt Quality Probe via Chosen/Rejected Δ-Cosine Analysis

**Hypothesis**: h-m3 (MECHANISM, INCREMENTAL)
**Date**: 2026-03-15
**Base**: h-m2 (VALIDATED)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Serena project not activated (no active project context). API signatures verified via direct Read tool from h-m2/code/. All parameter names confirmed from actual implementation files.
**Analyzed Path**: `docs/youra_research/20260315_bi_align/h-m2/code/`
**Relevant Symbols**:
- `bootstrap_c_sem(cos_actual, cos_random, n_bootstrap=1000, seed=42)` — uses `rng.integers` (NOT rng.choice); h-m3 uses `rng.choice` per experiment brief
- `Embedder.encode(texts, cache_key)` — returns L2-normalized `[N, D]` float32
- `Embedder.encode_tier(texts, prefix, tier, n_pairs)` — cache key: `{prefix}_{model_slug}_{tier_slug}_{n_pairs}`
- `compute_cosine_similarities(h_next, a_actual, a_topic, a_random)` — elementwise dot product on L2-normalized vecs
- `check_model_consistency_m2(all_model_bidir_results, alpha)` — returns `{models_passing, passing_models, gate_passed}`

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual h-m2 Code)

```python
# From: h-m2/code/statistics.py
def bootstrap_c_sem(
    cos_actual: np.ndarray,   # shape (N,)
    cos_random: np.ndarray,   # shape (N,)
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> Tuple[float, np.ndarray]:  # (c_sem, ci_array[2])
    # Uses rng.integers — h-m3 bootstrap_delta_ci uses rng.choice instead

def check_model_consistency_m2(
    all_model_bidir_results: Dict,
    alpha: float = 0.05,
) -> Dict:  # {models_passing, passing_models, gate_passed}

# From: h-m2/code/embedder.py
class Embedder:
    def encode(self, texts: List[str], cache_key: str) -> np.ndarray:
        # Returns [N, D] L2-normalized float32

    def encode_tier(
        self,
        texts: List[str],
        prefix: str,   # e.g. "h", "a_chosen", "a_rejected", "h_prompt"
        tier: str,     # e.g. "helpful-base"
        n_pairs: int,
    ) -> np.ndarray:
        # cache_key = f"{prefix}_{model_slug}_{tier_slug}_{n_pairs}"

# From: h-m2/code/accommodation.py
def compute_cosine_similarities(
    h_next: np.ndarray,   # [N, D] L2-normalized
    a_actual: np.ndarray, # [N, D] L2-normalized
    a_topic: np.ndarray,  # [N, D]
    a_random: np.ndarray, # [N, D]
) -> Dict[str, np.ndarray]:  # {cos_actual, cos_topic, cos_random} each (N,)
```

**Verified from**: `docs/youra_research/20260315_bi_align/h-m2/code/` (actual implementation)

---

## A-4: delta_probe.py [Complexity: 16, Budget: 4 subtasks]

Applied: Standard NumPy normalized dot product pattern

### API Signatures

```python
# delta_probe.py
import numpy as np
from typing import Dict, List

OPERATIONALIZATIONS: List[str] = ["raw", "length_matched", "prompt_projected"]


def truncate_to_rejected_length(
    a_chosen_texts: List[str],
    a_chosen_token_lens: List[int],
    a_rejected_token_lens: List[int],
) -> List[str]:
    """Truncate A_chosen whitespace-tokens to len(A_rejected). Returns List[str]."""
    ...


def project_out(
    vecs: np.ndarray,       # [N, D] L2-normalized
    direction: np.ndarray,  # [N, D] L2-normalized per-pair directions
) -> np.ndarray:            # [N, D] projected (NOT re-normalized)
    """Per-pair projection: v - (v·d)*d."""
    ...


def compute_delta_raw(
    emb_h_next: np.ndarray,     # [N, D]
    emb_a_chosen: np.ndarray,   # [N, D]
    emb_a_rejected: np.ndarray, # [N, D]
) -> np.ndarray:                # [N,]
    """OP1: dot(H_next, A_chosen) - dot(H_next, A_rejected)."""
    ...


def compute_delta_length_matched(
    h_next_texts: List[str],           # unused (only for re-embed if needed)
    a_chosen_texts: List[str],
    a_rejected_texts: List[str],
    a_chosen_token_lens: List[int],
    a_rejected_token_lens: List[int],
    embedder,                          # Embedder instance
    tier: str,
) -> np.ndarray:                       # [N,]
    """OP2: Truncate A_chosen, re-embed, compute delta as OP1."""
    ...


def compute_delta_prompt_projected(
    emb_h_next: np.ndarray,     # [N, D]
    emb_a_chosen: np.ndarray,   # [N, D]
    emb_a_rejected: np.ndarray, # [N, D]
    emb_h_prompt: np.ndarray,   # [N, D] L2-normalized prompt embeddings
) -> np.ndarray:                # [N,]
    """OP3: Project out H_prompt direction, normalize, compute delta."""
    ...


def compute_all_deltas(
    tier_pairs: Dict,  # {h_next, a_chosen, a_rejected, h_prompt, a_chosen_token_len, a_rejected_token_len}
    embedder,          # Embedder instance
    tier: str,
) -> Dict[str, np.ndarray]:
    """Compute all 3 ops for one tier + model. Returns {"raw": [N,], "length_matched": [N,], "prompt_projected": [N,]}."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| emb_* | [N, D] | L2-normalized float32, D=384 (MiniLM) or 768 (mpnet) |
| delta | [N,] | Per-pair float32, signed |
| direction (project_out) | [N, D] | Row-wise per-pair prompt direction |

### Pseudo-code

```
compute_delta_raw:
  cos_chosen   = sum(emb_h_next * emb_a_chosen, axis=1)   # [N,]
  cos_rejected = sum(emb_h_next * emb_a_rejected, axis=1) # [N,]
  return cos_chosen - cos_rejected                          # [N,]

project_out(vecs, direction):
  proj_coeff = sum(vecs * direction, axis=1, keepdims=True) # [N,1]
  return vecs - proj_coeff * direction                       # [N,D]

compute_delta_prompt_projected:
  a_chosen_proj  = project_out(emb_a_chosen,   emb_h_prompt)  # [N,D]
  a_rejected_proj= project_out(emb_a_rejected, emb_h_prompt)  # [N,D]
  # normalize projected embeddings
  a_chosen_proj  = a_chosen_proj / (norm(a_chosen_proj) + 1e-8)
  a_rejected_proj= a_rejected_proj / (norm(a_rejected_proj) + 1e-8)
  return compute_delta_raw(emb_h_next, a_chosen_proj, a_rejected_proj)

compute_delta_length_matched:
  truncated = truncate_to_rejected_length(a_chosen_texts, a_chosen_token_lens, a_rejected_token_lens)
  emb_truncated = embedder.encode_tier(truncated, prefix="a_chosen_trunc", tier=tier, n_pairs=N)
  emb_h_next = embedder.encode_tier(tier_pairs["h_next"], prefix="h_next_cr", tier=tier, n_pairs=N)
  emb_a_rejected = embedder.encode_tier(tier_pairs["a_rejected"], prefix="a_rejected", tier=tier, n_pairs=N)
  return compute_delta_raw(emb_h_next, emb_truncated, emb_a_rejected)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | truncate_to_rejected_length | Whitespace-token truncation, edge cases (empty, shorter chosen) |
| L-4-2 | project_out + OP3 | Per-pair prompt projection, safe normalization (1e-8 guard) |
| L-4-3 | compute_delta_raw + OP1 | Dot-product delta with L2-normalized inputs |
| L-4-4 | compute_all_deltas + FR-M3 logging | Orchestrate 3 ops, log E[Δ] per op per tier |

---

## A-5: statistics.py extensions [Complexity: 14, Budget: 3 subtasks]

Applied: One-sample bootstrap CI with rng.choice (per experiment brief)

### API Signatures

```python
# statistics.py (new h-m3 section)
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple


def bootstrap_delta_ci(
    delta_values: np.ndarray,   # [N,] per-pair delta
    n_resamples: int = 1000,
    seed: int = 42,
) -> Tuple[float, float, float]:  # (mean_delta, ci_lower, ci_upper)
    """Bootstrap mean Δ with 95% CI using rng.choice (NOT rng.integers)."""
    ...


def ttest_delta(
    delta_values: np.ndarray,  # [N,]
) -> Dict:  # {t_stat, p_value, df, significant}
    """One-sample t-test H0: E[Δ] = 0."""
    ...


def cohens_d_onesample(
    delta_values: np.ndarray,  # [N,]
) -> float:
    """Cohen's d = mean(Δ) / std(Δ, ddof=1)."""
    ...


def gate_evaluation_m3(
    ops_results: Dict[str, Dict],
    # {op_name: {mean_delta, ci_lower, ci_upper, n_pairs}}
    min_n_pairs: int = 1000,
) -> Dict:
    # Returns {gate_passed, ops_passing, ops_passing_list, auto_demote, n_pairs_min, gate_result}
    ...


def check_model_consistency_m3(
    all_model_results: Dict,
    # {model_slug: {op_results: {op: {mean_delta, ...}}}}
    ops: List[str] = None,  # defaults to OPERATIONALIZATIONS
) -> Dict:
    # Returns {models_consistent, consistent_models, gate_passed}
    ...


def verify_mechanism_activated_m3(
    all_model_results: Dict,
    experiment_log: str,
) -> Tuple[bool, Dict]:
    # Indicators: n_pairs_sufficient, delta_positive, ci_lower_positive,
    #             operationalizations_pass, fr_m3_logs_found
    ...
```

### Pseudo-code

```
bootstrap_delta_ci(delta_values, n_resamples=1000, seed=42):
  rng = np.random.default_rng(seed)
  n = len(delta_values)
  boot_means = [np.mean(rng.choice(delta_values, size=n, replace=True))
                for _ in range(n_resamples)]
  ci_lower, ci_upper = np.percentile(boot_means, [2.5, 97.5])
  return float(np.mean(delta_values)), float(ci_lower), float(ci_upper)

gate_evaluation_m3(ops_results, min_n_pairs):
  ops_passing = [op for op, res in ops_results.items()
                 if res["mean_delta"] > 0 AND res["ci_lower"] > 0]
  n_pairs_min = min(res["n_pairs"] for res in ops_results.values())
  auto_demote = n_pairs_min < min_n_pairs
  gate_passed = len(ops_passing) >= 2 AND NOT auto_demote
  gate_result = "PASS" if gate_passed else "FAIL"
  return {gate_passed, ops_passing=len(ops_passing), ops_passing_list=ops_passing,
          auto_demote, n_pairs_min, gate_result}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | bootstrap_delta_ci + ttest_delta + cohens_d_onesample | Core one-sample statistics |
| L-5-2 | gate_evaluation_m3 | ops_passing >= 2, auto-demote logic |
| L-5-3 | check_model_consistency_m3 + verify_mechanism_activated_m3 | Cross-model gate + 5-indicator check |

---

## A-7: run_experiment.py [Complexity: 16, Budget: 3 subtasks]

Applied: Standard multi-model orchestrator loop

### API Signatures

```python
# run_experiment.py
import argparse
import json
import logging
from typing import Dict

from config import ExperimentConfig, load_config
from data_loader import split_chosen_rejected_by_tier
from embedder import Embedder
from delta_probe import compute_all_deltas
from statistics import (
    bootstrap_delta_ci, ttest_delta, cohens_d_onesample,
    gate_evaluation_m3, check_model_consistency_m3, verify_mechanism_activated_m3,
)
from visualize import (
    plot_delta_distributions, plot_bootstrap_ci_by_op_and_model,
    plot_n_pairs_bar, plot_delta_by_tier, plot_delta_raw_vs_length_scatter,
    plot_model_op_heatmap,
)


def parse_args() -> argparse.Namespace:
    """--config, --dry-run flags."""
    ...


def run_single_model(
    model_name: str,
    tier_cr_pairs: Dict,       # {tier: {h_next, a_chosen, a_rejected, h_prompt, ..., n_pairs}}
    config: ExperimentConfig,
) -> Dict:
    """Full pipeline for one SBERT model. Returns {tier_results, op_stats, gate_result}."""
    ...


def main() -> None:
    """3-model orchestrator: load → parse pairs → 3-model loop → gate → figures → save."""
    ...
```

### Pseudo-code

```
run_single_model(model_name, tier_cr_pairs, config):
  embedder = Embedder(model_name, cache_dir=config.cache.embeddings_dir)
  tier_results = {}
  for tier, pairs in tier_cr_pairs.items():
      deltas = compute_all_deltas(pairs, embedder, tier)
      # deltas = {"raw": [N,], "length_matched": [N,], "prompt_projected": [N,]}
      op_stats = {}
      for op, delta_arr in deltas.items():
          mean_d, ci_lo, ci_hi = bootstrap_delta_ci(delta_arr, config.stats.n_bootstrap, config.stats.seed)
          ttest = ttest_delta(delta_arr)
          d_eff = cohens_d_onesample(delta_arr)
          op_stats[op] = {mean_delta: mean_d, ci_lower: ci_lo, ci_upper: ci_hi,
                          ttest: ttest, cohen_d: d_eff, n_pairs: len(delta_arr)}
      gate = gate_evaluation_m3(op_stats, config.stats.min_n_pairs)
      tier_results[tier] = {delta_arrays: deltas, op_stats: op_stats, gate: gate}
  return {tier_results: tier_results, op_stats: op_stats, gate_result: gate}

main():
  config = load_config(args.config)
  tier_cr_pairs = split_chosen_rejected_by_tier(config.cache.cache_dir)
  # Auto-demote check logged inside split_chosen_rejected_by_tier
  all_model_results = {}
  log_buffer = []
  for model_name in config.cache.models:
      result = run_single_model(model_name, tier_cr_pairs, config)
      all_model_results[model_name] = result
  consistency = check_model_consistency_m3(all_model_results)
  activated, indicators = verify_mechanism_activated_m3(all_model_results, "\n".join(log_buffer))
  # Generate 6 figures
  # Save delta_results.json
  # Log gate: PASS/FAIL with ops_passing count
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | run_single_model | Embedder init, compute_all_deltas, per-op stats loop |
| L-7-2 | main orchestrator | 3-model loop, consistency check, mechanism verification |
| L-7-3 | figure generation + JSON save | 6 figures + delta_results.json |

---

## A-2: data_loader.py extension [Complexity: 12, Budget: 1 subtask]

Applied: Standard

### API Signatures

```python
def parse_chosen_rejected_pairs(
    records: List[dict],
) -> Tuple[Dict, int]:
    """NEW h-m3: parse chosen + rejected fields into aligned lists.

    Returns pairs_dict: {h_next: List[str], a_chosen: List[str], a_rejected: List[str],
                         h_prompt: List[str], a_chosen_token_len: List[int],
                         a_rejected_token_len: List[int]}, n_pairs: int
    """
    ...


def split_chosen_rejected_by_tier(cache_dir: str) -> Dict[str, Dict]:
    """NEW h-m3: per-tier parse_chosen_rejected_pairs. Auto-demote warning if n_pairs < 1000.

    Returns: {tier_name: {h_next, a_chosen, a_rejected, h_prompt,
                          a_chosen_token_len, a_rejected_token_len, n_pairs}}
    """
    ...
```

### Pseudo-code

```
parse_chosen_rejected_pairs(records):
  results = {h_next:[], a_chosen:[], a_rejected:[], h_prompt:[],
             a_chosen_token_len:[], a_rejected_token_len:[]}
  for rec in records:
      chosen_turns = parse_conversation(rec["chosen"])
      rejected_turns = parse_conversation(rec["rejected"])
      # Extract last Human + last AI from chosen side as H_next, A_chosen
      # Extract last AI from rejected side as A_rejected
      # Use chosen conversation up to last human turn as H_prompt
      if valid(H_next, A_chosen, A_rejected):
          results["h_next"].append(H_next)
          results["a_chosen"].append(A_chosen)
          results["a_rejected"].append(A_rejected)
          results["h_prompt"].append(H_prompt)
          results["a_chosen_token_len"].append(compute_token_count(A_chosen))
          results["a_rejected_token_len"].append(compute_token_count(A_rejected))
  return results, len(results["h_next"])
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | parse_chosen_rejected_pairs + split_chosen_rejected_by_tier | Pair parsing, filter logic, auto-demote warning |

---

## A-6: visualize.py extension [Complexity: 12, Budget: 1 subtask]

Applied: Standard matplotlib/seaborn

### API Signatures

```python
def plot_delta_distributions(
    delta_results_by_op: Dict[str, np.ndarray],  # {"raw": [N,], ...}
    save_path: str,
    config: Optional[VisualizationConfig] = None,
) -> None:
    """MANDATORY Fig 1: Violin per operationalization."""
    ...

def plot_bootstrap_ci_by_op_and_model(
    all_model_op_stats: Dict,  # {model: {op: {mean_delta, ci_lower, ci_upper}}}
    save_path: str,
    config: Optional[VisualizationConfig] = None,
) -> None:
    """MANDATORY Fig 2: E[Δ] ± CI grouped bars."""
    ...

def plot_n_pairs_bar(
    tier_n_pairs: Dict[str, int],
    min_threshold: int,
    save_path: str,
    config: Optional[VisualizationConfig] = None,
) -> None:
    """MANDATORY Fig 3: N_pairs per tier + threshold line."""
    ...

def plot_delta_by_tier(
    delta_results_by_tier_op: Dict,  # {tier: {op: [N,]}}
    tier_order: List[str],
    save_path: str,
    config: Optional[VisualizationConfig] = None,
) -> None:
    """AUTONOMOUS Fig 4: Δ by RLHF tier."""
    ...

def plot_delta_raw_vs_length_scatter(
    delta_raw: np.ndarray,     # [N,]
    delta_length: np.ndarray,  # [N,]
    save_path: str,
    config: Optional[VisualizationConfig] = None,
) -> None:
    """AUTONOMOUS Fig 5: Scatter OP1 vs OP2."""
    ...

def plot_model_op_heatmap(
    summary_matrix: Dict,      # {model: {op: mean_delta}}
    model_names: List[str],
    save_path: str,
    config: Optional[VisualizationConfig] = None,
) -> None:
    """AUTONOMOUS Fig 6: 3-model x 3-op heatmap."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | 6 h-m3 figure functions | 3 mandatory + 3 autonomous, seaborn violin/bar/scatter/heatmap |

---

## A-8: Embedding encode pass [Complexity: 11, Budget: 1 subtask]

Applied: Standard

### API Signatures

```python
# In run_experiment.py / embedder reuse pattern
# New h-m3 cache key prefixes (via encode_tier):
#   prefix="a_chosen"       → a_chosen_{model_slug}_{tier_slug}_{n_pairs}.npy
#   prefix="a_rejected"     → a_rejected_{model_slug}_{tier_slug}_{n_pairs}.npy
#   prefix="h_next_cr"      → h_next_cr_{model_slug}_{tier_slug}_{n_pairs}.npy
#   prefix="h_prompt"       → h_prompt_{model_slug}_{tier_slug}_{n_pairs}.npy
#   prefix="a_chosen_trunc" → a_chosen_trunc_{model_slug}_{tier_slug}_{n_pairs}.npy

# All use Embedder.encode_tier(texts, prefix, tier, n_pairs) from h-m2 (unchanged API)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | h-m3 cache key design | 5 new prefixes, reuse encode_tier API from h-m2 unchanged |

---

## Summary

| Task | Subtasks Used | Key API |
|------|--------------|---------|
| A-4 delta_probe | 4/4 | compute_all_deltas, project_out, truncate_to_rejected_length |
| A-5 statistics | 3/3 | bootstrap_delta_ci (rng.choice), gate_evaluation_m3 |
| A-7 run_experiment | 3/3 | run_single_model, main, 6 figures |
| A-2 data_loader | 1/1 | parse_chosen_rejected_pairs, split_chosen_rejected_by_tier |
| A-6 visualize | 1/1 | 6 plot functions |
| A-8 embeddings | 1/1 | 5 new cache key prefixes |
| **Total** | **13/13** | |

**Critical implementation notes**:
- `bootstrap_delta_ci` uses `rng.choice` (h-m2 `bootstrap_c_sem` uses `rng.integers` — do NOT copy)
- `project_out` requires safe normalization guard `1e-8` before computing OP3 delta
- `encode_tier` API unchanged from h-m2 — use new prefixes only
- `NearestNeighbors(n_jobs=1)` constraint inherited from h-m2 (not used in h-m3, but note for any KNN usage)
- Gate pass condition: `ops_passing >= 2 AND n_pairs_min >= 1000`
