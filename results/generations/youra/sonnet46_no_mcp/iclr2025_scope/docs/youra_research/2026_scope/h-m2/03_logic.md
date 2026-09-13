# Logic: H-M2 — Budget-Ratio Dose-Response Analysis

Applied: budget-sweep-evaluation pattern (knowledge-grounded)
Applied: spearman-monotonicity-gate pattern (knowledge-grounded)
Applied: incremental-experiment-reuse pattern (knowledge-grounded)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-M1, which extends H-E1)
**Status**: API signatures verified from actual base code (direct file reads; Serena MCP unavailable)
**Analyzed Path**: `h-m1/code/model.py`, `h-m1/code/data.py`, `h-m1/code/evaluate.py`
**Relevant Symbols**:
- `load_adapter_model(model_name, adapter_checkpoint, condition, kv_budget_ratio=0.5, fp16=True)` — h-m1/code/model.py line 37
- `set_h2o_training_mode(model, train_mode)` — h-m1/code/model.py line 80
- `H2OEvictionAwareAttention` — loaded via importlib from h-e1/code/model.py
- `inject_h2o_wrappers` — loaded via importlib from h-e1/code/model.py
- `load_base_model` — loaded via importlib from h-e1/code/model.py
- `LongBenchDataLoader(tokenizer, max_seq_length=4096, tasks=None)` — h-m1/code/data.py line 42
- `LONGBENCH_TASKS` — List[str] of 21 task names — h-m1/code/data.py line 17
- `LONGBENCH_CATEGORIES` — Dict with hyphenated keys: "single-doc-qa", "multi-doc-qa", "few-shot", "summarization", "synthetic", "code"
- `run_inference_condition(extractor, dataloader, aggregator, condition, device, min_samples_per_category=500)` — h-m1/code/evaluate.py line 30
- `collect_layer_metrics(baseline_cfg, proposed_cfg, experiment_cfg, device)` — h-m1/code/evaluate.py line 73

---

## External Dependencies API

### API Signatures (From Actual H-M1 Code)

```python
# From: h-m1/code/model.py (ACTUAL CODE — verified)

def load_adapter_model(
    model_name: str,
    adapter_checkpoint: str,
    condition: str,           # "eviction-aware" | "baseline"
    kv_budget_ratio: float = 0.5,
    fp16: bool = True,        # unused — dtype determined by load_base_model
) -> nn.Module:
    """Load base model + PEFT adapter; inject H2O wrappers for eviction condition."""
    ...

def set_h2o_training_mode(model: nn.Module, train_mode: bool) -> None:
    """Toggle H2OEvictionAwareAttention wrappers to train/eval for eviction activation."""
    for module in model.modules():
        if isinstance(module, H2OEvictionAwareAttention):
            module.train() if train_mode else module.eval()

# H2OEvictionAwareAttention — loaded via importlib from h-e1/code/model.py
class H2OEvictionAwareAttention(nn.Module):
    kv_budget_ratio: float    # direct attribute — set via module.kv_budget_ratio = r
    def forward(self, hidden_states, attention_mask=None, **kwargs):
        # CRITICAL: eviction only applied when self.training=True
        ...

# From: h-m1/code/data.py (ACTUAL CODE — verified)
class LongBenchDataLoader:
    def __init__(self, tokenizer, max_seq_length: int = 4096, tasks=None): ...
    def iter_all_samples(self) -> Iterator[dict]: ...
    def load_task(self, task_name: str): ...
    def tokenize_sample(self, sample: dict, task_name: str) -> dict: ...
    # Returns: {input_ids: Tensor[S], attention_mask: Tensor[S], task, category, sample_id}

LONGBENCH_TASKS: List[str]   # 21 task names
LONGBENCH_CATEGORIES: Dict[str, List[str]]  # keys use hyphens: "single-doc-qa" etc.
```

**Importlib pattern** (same as H-M1, verified from actual code):
```python
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("h_e1_model", os.path.join(_H_E1_CODE, "model.py"))
_mod = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_mod)
H2OEvictionAwareAttention = _mod.H2OEvictionAwareAttention
inject_h2o_wrappers = _mod.inject_h2o_wrappers
load_base_model = _mod.load_base_model
```

**Verified from**: `h-m1/code/model.py` lines 19-32, 37-77, 80-92 (actual implementation)

---

## A-2: Dataset Module [Complexity: 10, Budget: 2 subtasks]

Applied: longbench-evaluation-protocol pattern (knowledge-grounded)

### API Signatures

```python
# h-m2/code/dataset.py

import importlib.util as _ilu, os
# Dynamic import of h-m1/code/data.py
_H_M1_CODE = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../h-m1/code"))
_spec = _ilu.spec_from_file_location("h_m1_data", os.path.join(_H_M1_CODE, "data.py"))
_data_mod = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_data_mod)

LongBenchDataLoader = _data_mod.LongBenchDataLoader    # re-exported
LONGBENCH_TASKS = _data_mod.LONGBENCH_TASKS            # List[str], 21 tasks
LONGBENCH_CATEGORIES = _data_mod.LONGBENCH_CATEGORIES  # Dict[str, List[str]], hyphenated keys

# Task scoring map: task_name -> scorer_fn
TASK_SCORER_MAP: Dict[str, Callable[[str, List[str]], float]]
# Scorers: F1 (qa tasks), ROUGE-L (summarization), accuracy (few-shot/synthetic), edit-distance (code)

def score_prediction(task_name: str, prediction: str, answers: List[str]) -> float:
    """Route to appropriate scorer via TASK_SCORER_MAP. Returns score in [0, 1]."""
    ...

def run_task_evaluation(
    model: nn.Module,
    tokenizer,
    task_name: str,
    max_seq_length: int = 4096,
    device: str = "cuda",
) -> float:
    """Run full test split for one task; generate predictions; return mean score.
    batch_size=1; uses greedy decoding (do_sample=False).
    """
    ...

def compute_category_accuracies(per_task_scores: Dict[str, float]) -> Dict[str, float]:
    """Aggregate per-task scores into 6-category means.
    Returns: {"single-doc-qa": float, "multi-doc-qa": float, ...}  # 6 keys
    """
    ...
```

### Subtasks [2/2 used]

### Subtask L-2-1: Importlib re-export and TASK_SCORER_MAP
Parent: A-2
Description: Dynamic-import h-m1/code/data.py via importlib; re-export LongBenchDataLoader, LONGBENCH_TASKS, LONGBENCH_CATEGORIES; build TASK_SCORER_MAP with F1/ROUGE-L/accuracy/edit-distance scorers per task.

### Subtask L-2-2: run_task_evaluation and compute_category_accuracies
Parent: A-2
Description: Implement run_task_evaluation (load dataset, generate, score, return mean); implement compute_category_accuracies using LONGBENCH_CATEGORIES hyphenated keys to map tasks to categories.

---

## A-3: Model Module [Complexity: 11, Budget: 4 subtasks]

Applied: importlib-dynamic-loading pattern (knowledge-grounded)

### API Signatures

```python
# h-m2/code/model.py

import os, importlib.util as _ilu
from typing import Optional
import torch.nn as nn

_H_E1_CODE = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../h-e1/code"))
_H_M1_CODE = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../h-m1/code"))

# Dynamic imports (same pattern as h-m1/code/model.py)
H2OEvictionAwareAttention  # from h-e1/code/model.py
inject_h2o_wrappers        # from h-e1/code/model.py
load_base_model            # from h-e1/code/model.py
load_adapter_model         # from h-m1/code/model.py
set_h2o_training_mode      # from h-m1/code/model.py

def set_h2o_budget(model: nn.Module, kv_budget_ratio: float) -> None:
    """Set kv_budget_ratio on all H2OEvictionAwareAttention instances.
    Raises ValueError if no H2O wrappers found.
    """
    ...

def verify_budget_applied(model: nn.Module, expected_ratio: float) -> bool:
    """Return True if all H2OEvictionAwareAttention instances have expected_ratio."""
    ...

def load_model_for_sweep(
    model_name: str,
    adapter_path: str,
    adapter_type: str,        # "sequential" | "eviction-aware"
    initial_budget: float = 0.5,
) -> tuple[nn.Module, object]:
    """Load base model + PEFT adapter; inject H2O for eviction-aware; set eager attn.
    Returns: (model_in_eval_mode, tokenizer)
    """
    ...
```

### Pseudo-code

```
set_h2o_budget(model, kv_budget_ratio):
    count = 0
    for module in model.modules():
        if isinstance(module, H2OEvictionAwareAttention):
            module.kv_budget_ratio = kv_budget_ratio
            count += 1
    if count == 0:
        raise ValueError("No H2OEvictionAwareAttention wrappers found — budget not applied")

verify_budget_applied(model, expected_ratio):
    for module in model.modules():
        if isinstance(module, H2OEvictionAwareAttention):
            if abs(module.kv_budget_ratio - expected_ratio) > 1e-6:
                return False
    return True

load_model_for_sweep(model_name, adapter_path, adapter_type, initial_budget):
    # adapter_type "sequential" maps to condition "baseline" in H-M1's load_adapter_model
    condition = "eviction-aware" if adapter_type == "eviction-aware" else "baseline"
    model = load_adapter_model(model_name, adapter_path, condition, initial_budget)
    # load_adapter_model already sets attn_implementation="eager"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()
    return model, tokenizer
```

### Subtasks [4/4 used]

### Subtask L-3-1: Importlib dynamic loading
Parent: A-3
Description: Load H2OEvictionAwareAttention, inject_h2o_wrappers, load_base_model from h-e1/code/model.py; load load_adapter_model, set_h2o_training_mode from h-m1/code/model.py using same importlib pattern as h-m1.

### Subtask L-3-2: set_h2o_budget
Parent: A-3
Description: Iterate model.modules(), find H2OEvictionAwareAttention instances, set kv_budget_ratio attribute directly; raise ValueError if none found.

### Subtask L-3-3: verify_budget_applied
Parent: A-3
Description: Iterate H2OEvictionAwareAttention instances, check kv_budget_ratio == expected; return False on first mismatch, True if all match.

### Subtask L-3-4: load_model_for_sweep
Parent: A-3
Description: Delegate to h-m1's load_adapter_model with condition mapping ("sequential"->"baseline"); load tokenizer; handle pad_token; return (model, tokenizer).

---

## A-4: BudgetSweepEvaluator [Complexity: 13, Budget: 4 subtasks]

Applied: gpu-memory-managed-evaluation-loop pattern (knowledge-grounded)

### API Signatures

```python
# h-m2/code/evaluate.py

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import torch.nn as nn
from config import BudgetSweepConfig
from dataset import run_task_evaluation, compute_category_accuracies, LONGBENCH_TASKS

@dataclass
class RunResult:
    model_name: str
    adapter_type: str           # "sequential" | "eviction-aware"
    budget_ratio: float
    per_task_scores: Dict[str, float]   # task_name -> score in [0,1]
    category_scores: Dict[str, float]   # 6 hyphenated category keys -> mean score

class BudgetSweepEvaluator:
    def __init__(self, cfg: BudgetSweepConfig): ...

    def evaluate_single_run(
        self,
        model: nn.Module,
        tokenizer,
        adapter_type: str,
        budget_ratio: float,
        model_name: str,
        device: str,
    ) -> RunResult:
        """Set budget, activate eviction (H2O train mode), run all 21 tasks, return RunResult."""
        ...

    def run_all(self, device: str = "cuda") -> List[RunResult]:
        """12-run sweep: 2 adapter_types × 3 budget_ratios × 2 models.
        Loads/unloads models between adapter groups to manage GPU memory.
        Returns List[RunResult] length 12.
        """
        ...

def verify_mechanism_activated(
    model: nn.Module,
    budget_ratio: float,
    results_by_r: Dict[float, float],
) -> Tuple[bool, dict]:
    """Check budget correctly set + gap variance non-zero.
    Returns: (all_pass: bool, indicators: dict)
    """
    ...

def save_run_results(results: List[RunResult], output_dir: str) -> str:
    """Save per-run results as CSV (rows: model_name, adapter_type, budget_ratio, per-category scores).
    Returns CSV file path.
    """
    ...
```

### Pseudo-code

```
evaluate_single_run(model, tokenizer, adapter_type, budget_ratio, model_name, device):
    if adapter_type == "eviction-aware":
        set_h2o_budget(model, budget_ratio)
        assert verify_budget_applied(model, budget_ratio)
    set_h2o_training_mode(model, True)   # activate eviction for inference
    per_task_scores = {}
    for task in LONGBENCH_TASKS:
        score = run_task_evaluation(model, tokenizer, task, cfg.max_seq_length, device)
        per_task_scores[task] = score
    set_h2o_training_mode(model, False)
    category_scores = compute_category_accuracies(per_task_scores)
    return RunResult(model_name, adapter_type, budget_ratio, per_task_scores, category_scores)

run_all(device):
    results = []
    for adapter_spec in cfg.adapters:  # 2 adapters per model (sequential + eviction-aware)
        model, tokenizer = load_model_for_sweep(
            adapter_spec.model_name, adapter_spec.adapter_path,
            adapter_spec.adapter_type, initial_budget=cfg.budget_ratios[0]
        )
        model = model.to(device)
        for r in cfg.budget_ratios:   # [0.25, 0.50, 0.75]
            result = evaluate_single_run(model, tokenizer,
                                         adapter_spec.adapter_type, r,
                                         adapter_spec.model_name, device)
            results.append(result)
        del model
        torch.cuda.empty_cache()
    return results  # len == 12: 4 adapters × 3 ratios
```

### Subtasks [4/4 used]

### Subtask L-4-1: RunResult dataclass
Parent: A-4
Description: Define RunResult with model_name, adapter_type, budget_ratio, per_task_scores Dict[str,float], category_scores Dict[str,float]; add to_dict() helper for CSV serialization.

### Subtask L-4-2: evaluate_single_run
Parent: A-4
Description: Set budget (eviction-aware only), toggle H2O train mode, iterate 21 tasks via run_task_evaluation, restore eval mode, return RunResult.

### Subtask L-4-3: run_all orchestration
Parent: A-4
Description: Outer loop over adapters; inner loop over budget_ratios; load model once per adapter; del + empty_cache between adapters; collect 12 RunResults.

### Subtask L-4-4: save_run_results + verify_mechanism_activated
Parent: A-4
Description: save_run_results writes CSV with pandas (columns: model_name, adapter_type, budget_ratio + 6 category columns). verify_mechanism_activated checks verify_budget_applied and that np.var(list(results_by_r.values())) > 0.

---

## A-5: SpearmanAnalyzer [Complexity: 12, Budget: 4 subtasks]

Applied: spearman-correlation-gate pattern (knowledge-grounded)

### API Signatures

```python
# h-m2/code/analyze.py

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import numpy as np
from scipy import stats

@dataclass
class GapMatrix:
    """Per-model accuracy gap: eviction-aware minus sequential per (budget_ratio, category)."""
    model_name: str
    gaps: Dict[float, Dict[str, float]]   # gaps[r][category] = float
    mean_gaps: Dict[float, float]          # mean over 6 categories per r

@dataclass
class SpearmanResult:
    model_name: str
    rho: float
    pval: float
    gate_passed: bool   # rho < -0.8

@dataclass
class MonotonicityResult:
    model_name: str
    per_category: Dict[str, bool]   # True if gap(0.25) > gap(0.50) > gap(0.75)
    fraction_monotone: float         # count(True) / 6

class SpearmanAnalyzer:
    def compute_gap_matrix(
        self,
        results: List[RunResult],
    ) -> Dict[str, GapMatrix]:
        """Build GapMatrix per model_name from list of RunResults.
        Returns: {model_name: GapMatrix}
        """
        ...

    def compute_spearman(
        self,
        gap_matrix: GapMatrix,
    ) -> SpearmanResult:
        """scipy.stats.spearmanr([0.25, 0.50, 0.75], [mean_gap_25, mean_gap_50, mean_gap_75]).
        gate_passed = rho < -0.8
        """
        ...

    def check_monotonicity(self, gap_matrix: GapMatrix) -> MonotonicityResult:
        """Per category: True if gaps strictly decrease as budget_ratio increases."""
        ...

    def run_full_analysis(
        self,
        results: List[RunResult],
    ) -> dict:
        """Returns: {gap_matrices, spearman_results, monotonicity, gate_passed}
        gate_passed = True if any SpearmanResult.gate_passed
        """
        ...

    def save_summary(self, analysis: dict, output_path: str) -> None:
        """Serialize analysis to JSON (dataclasses -> dicts). Write to output_path."""
        ...
```

### Pseudo-code

```
compute_gap_matrix(results):
    # Group results by model_name and adapter_type
    by_model = defaultdict(lambda: {"sequential": {}, "eviction-aware": {}})
    for r in results:
        by_model[r.model_name][r.adapter_type][r.budget_ratio] = r.category_scores
    gap_matrices = {}
    for model_name, adapter_data in by_model.items():
        seq = adapter_data["sequential"]      # {r: {cat: score}}
        evict = adapter_data["eviction-aware"]
        gaps = {}
        for r in [0.25, 0.50, 0.75]:
            gaps[r] = {}
            for cat in LONGBENCH_CATEGORIES:
                gaps[r][cat] = evict[r][cat] - seq[r][cat]
        mean_gaps = {r: np.mean(list(gaps[r].values())) for r in gaps}
        gap_matrices[model_name] = GapMatrix(model_name, gaps, mean_gaps)
    return gap_matrices

compute_spearman(gap_matrix):
    ratios = [0.25, 0.50, 0.75]
    mean_gap_vals = [gap_matrix.mean_gaps[r] for r in ratios]
    rho, pval = scipy.stats.spearmanr(ratios, mean_gap_vals)
    return SpearmanResult(gap_matrix.model_name, rho, pval, gate_passed=(rho < -0.8))

run_full_analysis(results):
    gap_matrices = compute_gap_matrix(results)
    spearman_results = {m: compute_spearman(gm) for m, gm in gap_matrices.items()}
    monotonicity = {m: check_monotonicity(gm) for m, gm in gap_matrices.items()}
    gate_passed = any(sr.gate_passed for sr in spearman_results.values())
    return {
        "gap_matrices": gap_matrices,
        "spearman_results": spearman_results,
        "monotonicity": monotonicity,
        "gate_passed": gate_passed,
    }
```

### Subtasks [4/4 used]

### Subtask L-5-1: GapMatrix, SpearmanResult, MonotonicityResult dataclasses
Parent: A-5
Description: Define three dataclasses with correct field types; add to_dict() methods for JSON serialization.

### Subtask L-5-2: compute_gap_matrix
Parent: A-5
Description: Group RunResults by model_name and adapter_type; compute per-category and mean gaps for each budget_ratio; return Dict[str, GapMatrix].

### Subtask L-5-3: compute_spearman and check_monotonicity
Parent: A-5
Description: compute_spearman calls scipy.stats.spearmanr on [0.25,0.50,0.75] vs mean_gaps; gate = rho < -0.8. check_monotonicity checks strict decrease per category over 3 ratios.

### Subtask L-5-4: run_full_analysis and save_summary
Parent: A-5
Description: run_full_analysis orchestrates gap->spearman->monotonicity->gate. save_summary converts dataclass fields to dicts and writes JSON via json.dump.

---

## A-7: Mechanism Verification [Complexity: 8, Budget: 1 subtask]

Applied: sanity-check-gate pattern (knowledge-grounded)

### API Signatures

```python
# h-m2/code/evaluate.py (continuation)

def verify_mechanism_activated(
    model: nn.Module,
    budget_ratio: float,
    results_by_r: Dict[float, float],   # {r: mean_category_score}
) -> Tuple[bool, dict]:
    """Verify H2O budget mechanism is correctly applied and produces variance.

    Checks:
    1. verify_budget_applied(model, budget_ratio) — all H2O wrappers have correct ratio
    2. np.var(list(results_by_r.values())) > 0 — scores vary across budget ratios
    3. len(results_by_r) == 3 — all 3 budget ratios evaluated

    Returns: (all_pass: bool, indicators: dict with check details)
    """
    indicators = {}
    budget_ok = verify_budget_applied(model, budget_ratio)
    indicators["budget_set_correctly"] = budget_ok
    variance = float(np.var(list(results_by_r.values()))) if results_by_r else 0.0
    indicators["gap_variance"] = variance
    indicators["gap_variance_nonzero"] = variance > 1e-8
    indicators["n_ratios_evaluated"] = len(results_by_r)
    all_pass = budget_ok and variance > 1e-8 and len(results_by_r) == 3
    indicators["all_pass"] = all_pass
    return all_pass, indicators
```

### Subtask L-7-1: verify_mechanism_activated implementation
Parent: A-7
Description: Implement three-check verification (budget_set, gap_variance>0, n_ratios==3); log indicators; return (bool, dict). Called from BudgetSweepEvaluator.run_all() after completing all budget ratios for an adapter pair.

---

## Subtask Budget Summary

| Task | Allocated | Used |
|------|-----------|------|
| A-2 | 2 | 2 |
| A-3 | 4 | 4 |
| A-4 | 4 | 4 |
| A-5 | 4 | 4 |
| A-7 | 1 | 1 |
| **Total** | **15** | **15** |
