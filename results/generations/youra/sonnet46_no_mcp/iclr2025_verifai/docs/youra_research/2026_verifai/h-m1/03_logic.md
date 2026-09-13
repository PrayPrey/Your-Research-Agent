# Logic: h-m1 — Distinct Failure Channel Mechanism Verification

**Type:** MECHANISM (INCREMENTAL — extends h-e1)
**Applied**: incremental-experiment-extension-pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual h-e1 code (direct file reads)
**Analyzed Path**: `docs/youra_research/20260508_verifai/h-e1/code/`
**Relevant Symbols**: `BaselineGenerator`, `SyncodeGenerator` (lowercase c), `MetricsEvaluator` — verified from actual source.

---

## External Dependencies API

### API Signatures (From Actual h-e1 Code)

```python
# From: h-e1/code/baseline_generator.py (ACTUAL CODE)
class BaselineGenerator:
    def __init__(
        self,
        model_name: str = "codellama/CodeLlama-7b-hf",
        temperature: float = 0.8,
        max_new_tokens: int = 256,
        n_samples: int = 20,
    ) -> None: ...

    def load_model(self) -> None: ...

    def _generate_single(self, prompt: str, seed: int) -> str: ...

    def generate_pool(
        self,
        problems: Dict[str, dict],
        seeds: List[int],   # ← h-e1 uses seeds list, NOT problem_idx/sample_idx
        output_path: str,
    ) -> Dict[str, List[str]]:  # returns {task_id: [completion_str]} (NO ast_valid field!)
        ...

# From: h-e1/code/syncode_generator.py (ACTUAL CODE)
class SyncodeGenerator:   # lowercase 'c' — not SynCodeGenerator!
    def __init__(
        self,
        model_name: str = "codellama/CodeLlama-7b-hf",
        grammar: str = "python",
        mode: str = "grammar_mask",
        temperature: float = 0.8,
        max_new_tokens: int = 256,
        n_samples: int = 20,
    ) -> None: ...

    def _generate_single_constrained(
        self, prompt: str, seed: int
    ) -> Tuple[str, int]:  # returns (completion_str, filtered_token_count) — NOT (str, bool)!
        ...

    def generate_pool(
        self,
        problems: Dict[str, dict],
        seeds: List[int],   # ← h-e1 uses seeds list
        output_path: str,
    ) -> Dict[str, List[str]]:  # returns {task_id: [completion_str]} (NO constraint_active field!)
        ...

    def verify_constraint_active(
        self,
        pool: Dict[str, List[str]],
        filtered_counts: Dict[str, List[int]] = None,
    ) -> bool: ...

# From: h-e1/code/metrics.py (ACTUAL CODE)
class MetricsEvaluator:
    def compute_ast_failure_rate(self, pool: Dict[str, List[str]]) -> float: ...
    def compute_delta_ast(
        self,
        baseline_pool: Dict[str, List[str]],
        syncode_pool: Dict[str, List[str]],
    ) -> float: ...
```

**Key divergences from h-e1 spec:**
- h-e1 `generate_pool()` takes `seeds: List[int]`, h-m1 must use per-problem seed scheme internally
- h-e1 JSONL has NO `ast_valid`, `problem_idx`, `sample_idx` fields — h-m1 must compute/add these on load
- `_generate_single_constrained` returns `(str, int)` (filtered_count), NOT `(str, bool)`
- h-e1 seed scheme was `list(range(20))` — h-m1 introduces `problem_idx * 100 + sample_idx`

**Verified from**: `docs/youra_research/20260508_verifai/h-e1/code/` (actual implementation)

---

## A-3: SynCode Pool Extension [Complexity: 14, Budget: 4]

**Applied**: incremental-experiment-extension-pattern

### API Signatures

```python
# h-m1/code/syncode_generator.py
import ast as ast_module
import json
from typing import Dict, List, Optional, Set, Tuple

class ExtendedSyncodeGenerator:
    """Extends h-e1 SyncodeGenerator: 164 problems, constraint_active bool flag, resume."""

    def __init__(
        self,
        model_name: str = "codellama/CodeLlama-7b-hf",
        grammar: str = "python",
        mode: str = "grammar_mask",
        temperature: float = 0.8,
        max_new_tokens: int = 512,
        n_samples: int = 20,
    ) -> None:
        """Initialize; syn_model=None until load_model() called."""
        ...

    def load_model(self) -> None:
        """Load SYNCODE_CLASS(model, grammar, mode). Set self.syn_model."""
        ...

    def _compute_seed(self, problem_idx: int, sample_idx: int) -> int:
        """Returns problem_idx * 100 + sample_idx."""
        return problem_idx * 100 + sample_idx

    def _generate_single_constrained(
        self, prompt: str, seed: int
    ) -> Tuple[str, bool]:
        """Generate one constrained completion.
        Returns (completion_str, constraint_active_bool).
        constraint_active = filtered_token_count > 0 OR logits_processor present."""
        ...

    def load_progress(self, progress_path: str) -> Set[str]:
        """Load progress.json; return set of completed task_ids. Return empty set if missing."""
        ...

    def generate_pool(
        self,
        problems: Dict[str, dict],
        output_path: str,
        progress_path: str,
    ) -> Dict[str, List[dict]]:
        """Generate 164×20 constrained pool with resume support.
        Appends to existing JSONL; skips task_ids in progress set.
        Returns {task_id: [record_dict]}."""
        ...

    def compute_constraint_active_rate(
        self, pool: Dict[str, List[dict]]
    ) -> float:
        """Returns fraction of samples where constraint_active=True across all problems."""
        ...
```

### Pool Record Shape

```python
# Each record in syncode_pool.jsonl
{
    "task_id": str,          # e.g. "HumanEval/0"
    "problem_idx": int,      # 0-163
    "sample_idx": int,       # 0-19
    "seed": int,             # problem_idx * 100 + sample_idx
    "completion": str,       # generated code (new tokens only)
    "ast_valid": bool,       # ast.parse() succeeded
    "constraint_active": bool,  # grammar constraint was active during generation
}
```

### Pseudo-code: generate_pool

```
1. completed = load_progress(progress_path)
2. pool = {}; open output_path in append mode
3. for problem_idx, (task_id, problem) in enumerate(sorted(problems.items())):
4.     if task_id in completed: load records from existing JSONL; continue
5.     records = []
6.     for sample_idx in range(n_samples):
7.         seed = problem_idx * 100 + sample_idx
8.         completion, constraint_active = _generate_single_constrained(prompt, seed)
9.         ast_valid = try ast.parse(completion) -> True; except SyntaxError -> False
10.        record = {task_id, problem_idx, sample_idx, seed, completion, ast_valid, constraint_active}
11.        write record as JSONL line; records.append(record)
12.    pool[task_id] = records
13.    update progress.json with task_id; print progress
14. return pool
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | ExtendedSyncodeGenerator.__init__ + load_model | Init with SYNCODE_CLASS, handle import fallback |
| L-3-2 | _generate_single_constrained | filtered_token_count → constraint_active bool conversion |
| L-3-3 | generate_pool with resume | Append mode JSONL, progress tracking, ast_valid computation |
| L-3-4 | compute_constraint_active_rate | Aggregate bool flag across all pool records |

---

## A-9: Visualization [Complexity: 14, Budget: 4]

**Applied**: Standard matplotlib/seaborn plotting pattern

### API Signatures

```python
# h-m1/code/visualization.py
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List

class HM1Visualizer:
    def __init__(self, figures_dir: str) -> None:
        """Create figures_dir if not exists."""
        ...

    def plot_gate_metrics(
        self,
        baseline_mean: float,
        syncode_mean: float,
        ci_lower: float,
        ci_upper: float,
        delta_ast: float,
        gate_result: str,  # "PASS" | "PARTIAL" | "FAIL"
    ) -> None:
        """Bar chart: x=[Baseline, SynCode], y=ast_failure_rate.
        Error bars: (syncode_mean-ci_lower, ci_upper-syncode_mean).
        Saves: figures_dir/gate_metrics.{pdf,png}"""
        ...

    def plot_per_problem_scatter(
        self,
        baseline_rates: np.ndarray,  # [164]
        syncode_rates: np.ndarray,   # [164]
        task_ids: List[str],         # [164]
    ) -> None:
        """Scatter: x=baseline_rate, y=syncode_rate, diagonal=no-improvement line.
        Saves: figures_dir/per_problem_scatter.{pdf,png}"""
        ...

    def plot_fmd_comparison(
        self,
        baseline_dist: Dict[str, float],  # {category: proportion}
        syncode_dist: Dict[str, float],
    ) -> None:
        """Side-by-side bars for syntax/type/functional/success.
        Saves: figures_dir/fmd_comparison.{pdf,png}"""
        ...

    def plot_transition_heatmap(
        self,
        baseline_pool: Dict[str, List[dict]],
        syncode_pool: Dict[str, List[dict]],
        task_ids: List[str],   # ordered list, length 164
    ) -> None:
        """164×20 grid: 0=baseline_pass, 1=both_fail, 2=transition(b_fail+s_pass).
        Saves: figures_dir/transition_heatmap.{pdf,png}"""
        ...

    def save_all(
        self,
        ast_results: dict,
        bootstrap_results: dict,
        fmd_results: dict,
        baseline_pool: Dict[str, List[dict]],
        syncode_pool: Dict[str, List[dict]],
        baseline_rates: np.ndarray,  # [164]
        syncode_rates: np.ndarray,   # [164]
        task_ids: List[str],
    ) -> None:
        """Call all 4 plot_* methods."""
        ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | plot_gate_metrics | Bar + CI error bars + PASS/FAIL annotation |
| L-9-2 | plot_per_problem_scatter | x=baseline, y=syncode, diagonal, count annotation |
| L-9-3 | plot_fmd_comparison | Side-by-side bars for 4 categories |
| L-9-4 | plot_transition_heatmap | 164×20 grid heatmap with 3-color encoding |

---

## A-2: Baseline Pool Extension [Complexity: 13, Budget: 2]

**Applied**: incremental-experiment-extension-pattern

### API Signatures

```python
# h-m1/code/baseline_generator.py
import json
from typing import Dict, List, Optional, Set

class ExtendedBaselineGenerator:
    """Extends h-e1 BaselineGenerator: 164 problems, new seed scheme, resume, ast_valid field."""

    def __init__(
        self,
        model_name: str = "codellama/CodeLlama-7b-hf",
        temperature: float = 0.8,
        max_new_tokens: int = 512,
        n_samples: int = 20,
    ) -> None: ...

    def load_model(self) -> None: ...

    def _compute_seed(self, problem_idx: int, sample_idx: int) -> int:
        """Returns problem_idx * 100 + sample_idx."""
        ...

    def _generate_single(self, prompt: str, seed: int) -> str: ...

    def load_h_e1_pool(self, h_e1_path: str) -> Dict[str, List[dict]]:
        """Load h-e1 JSONL (fields: task_id, completion, seed, generation_time).
        Converts to h-m1 record format: adds ast_valid, problem_idx=None, sample_idx=None.
        Returns {task_id: [record_dict]}."""
        ...

    def load_progress(self, progress_path: str) -> Set[str]:
        """Return set of completed task_ids. Empty set if progress.json missing."""
        ...

    def generate_pool(
        self,
        problems: Dict[str, dict],
        output_path: str,
        progress_path: str,
        h_e1_pool_path: Optional[str] = None,
    ) -> Dict[str, List[dict]]:
        """Generate 164×20 baseline pool.
        If h_e1_pool_path provided: reuse first 20 problems from h-e1.
        Resume from progress_path. Append to existing JSONL.
        Returns {task_id: [record_dict]}."""
        ...
```

### Pool Record Shape

```python
# Each record in baseline_pool.jsonl
{
    "task_id": str,
    "problem_idx": int,
    "sample_idx": int,
    "seed": int,
    "completion": str,
    "ast_valid": bool,
}
```

### Pseudo-code: load_h_e1_pool

```
1. records = {}; open h_e1_path; for line in JSONL:
2.     rec = json.loads(line)
3.     task_id = rec["task_id"]
4.     ast_valid = try ast.parse(rec["completion"]) -> True; except -> False
5.     new_rec = {task_id, problem_idx: None, sample_idx: None,
6.                seed: rec["seed"], completion: rec["completion"], ast_valid}
7.     records.setdefault(task_id, []).append(new_rec)
8. return records
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | load_h_e1_pool | Parse h-e1 JSONL, compute ast_valid, return dict |
| L-2-2 | generate_pool with h_e1 reuse + resume | Ordered enumeration, seed scheme, append JSONL |

---

## A-10: Orchestrator & Tests [Complexity: 12, Budget: 2]

**Applied**: Standard PyTorch

### API Signatures

```python
# h-m1/code/run_experiment.py
import argparse
from typing import Dict, List

def get_paths(base_dir: str) -> dict:
    """Returns {data_dir, results_dir, figures_dir, baseline_pool, syncode_pool,
    progress_baseline, progress_syncode, ast_results, bootstrap_results,
    fmd_results, transitions, mechanism_verification, metrics}."""
    ...

def load_pool_from_jsonl(path: str) -> Dict[str, List[dict]]:
    """Load JSONL records. Handle missing fields gracefully (h-e1 compat).
    Returns {task_id: [record_dict]}."""
    ...

def main() -> int:
    """CLI orchestrator. Returns 0=PASS, 1=FAIL."""
    ...
```

### Pseudo-code: main() (Steps 0-9)

```
0. parse_args(); paths = get_paths(args.base_dir)
   if not args.skip_mechanism_check:
       verifier = MechanismVerifier()
       mech = verifier.verify(syn_gen, test_prompt, paths["mechanism_verification"])
       if not mech["pre_check_passed"]: print warning; proceed anyway

1. problems = get_human_eval_plus()  # 164 problems from evalplus

2. if args.load_pools:
       baseline_pool = load_pool_from_jsonl(paths["baseline_pool"])
   else:
       bgen = ExtendedBaselineGenerator(); bgen.load_model()
       baseline_pool = bgen.generate_pool(problems, paths["baseline_pool"],
                                          paths["progress_baseline"],
                                          h_e1_pool_path=paths.get("h_e1_baseline"))

3. if not args.skip_syncode:
       if args.load_pools:
           syncode_pool = load_pool_from_jsonl(paths["syncode_pool"])
       else:
           sgen = ExtendedSyncodeGenerator(); sgen.load_model()
           syncode_pool = sgen.generate_pool(problems, paths["syncode_pool"],
                                             paths["progress_syncode"])

4. computer = ASTFailureRateComputer()
   baseline_rates, syncode_rates, task_ids = computer.compute_arrays(baseline_pool, syncode_pool)
   delta_ast = computer.compute_delta_ast(baseline_rates, syncode_rates)
   ast_results = computer.save_results(baseline_rates, syncode_rates, task_ids, paths["ast_results"])

5. ci = BootstrapCI(n_bootstrap=10000, alpha=0.05)
   delta_mean, ci_lower, ci_upper, p_value = ci.compute(baseline_rates, syncode_rates)
   gate_result = ci.evaluate_gate(delta_mean, ci_lower)
   ci.save_results(delta_mean, ci_lower, ci_upper, p_value, gate_result, paths["bootstrap_results"])

6. fmd = FMDClassifier()
   baseline_cls = fmd.classify_pool(baseline_pool, problems)
   syncode_cls = fmd.classify_pool(syncode_pool, problems)
   baseline_dist = fmd.compute_distribution(baseline_cls)
   syncode_dist = fmd.compute_distribution(syncode_cls)
   fmd.save_results(baseline_dist, syncode_dist, fmd.compute_syntax_shift(...), paths["fmd_results"])

7. extractor = TransitionExtractor()
   transitions = extractor.extract(baseline_pool, syncode_pool)
   coverage = extractor.compute_coverage_by_problem(transitions)
   extractor.save_results(transitions, coverage, paths["transitions"])

8. save metrics.json: {gate_result, delta_ast, ci_lower, ci_upper, p_value,
                        constraint_active_rate, transition_count}

9. viz = HM1Visualizer(paths["figures_dir"])
   viz.save_all(ast_results, bootstrap_results, fmd_results, ...)

   return 0 if gate_result == "PASS" else 1
```

### Test Signatures

```python
# h-m1/code/tests/test_ast_metrics.py
class TestASTFailureRateComputer(unittest.TestCase):
    def test_all_valid_completions(self): ...       # failure_rate = 0.0
    def test_all_invalid_completions(self): ...     # failure_rate = 1.0
    def test_mixed_pool_compute_arrays(self): ...   # arrays aligned by task_id

# h-m1/code/tests/test_bootstrap_ci.py
class TestBootstrapCI(unittest.TestCase):
    def test_delta_zero_p_value_near_half(self): ... # equal pools -> p_value ~0.5
    def test_strong_signal_pass_gate(self): ...      # clear delta -> PASS
    def test_negative_delta_fail_gate(self): ...     # syncode worse -> FAIL
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-10-1 | main() orchestrator + get_paths + load_pool_from_jsonl | Steps 0-9 per pseudo-code |
| L-10-2 | Unit tests: ASTFailureRateComputer + BootstrapCI | 3 test methods each |

---

## A-5: Bootstrap CI [Complexity: 10, Budget: 2]

**Applied**: Standard numpy bootstrap pattern

### API Signatures

```python
# h-m1/code/bootstrap_ci.py
import numpy as np
from typing import Tuple

class BootstrapCI:
    def __init__(self, n_bootstrap: int = 10000, alpha: float = 0.05) -> None:
        self.n_bootstrap = n_bootstrap
        self.alpha = alpha

    def compute(
        self,
        baseline_rates: np.ndarray,  # [164] per-problem failure rates
        syncode_rates: np.ndarray,   # [164] per-problem failure rates
    ) -> Tuple[float, float, float, float]:
        """Paired problem-level bootstrap.
        Returns (delta_mean, ci_lower, ci_upper, p_value)."""
        ...

    def evaluate_gate(self, delta_mean: float, ci_lower: float) -> str:
        """Returns 'PASS' if delta_mean > 0 and ci_lower > 0, else 'PARTIAL' or 'FAIL'."""
        ...

    def save_results(
        self,
        delta_mean: float,
        ci_lower: float,
        ci_upper: float,
        p_value: float,
        gate_result: str,
        output_path: str,
    ) -> dict: ...
```

### Pseudo-code: compute (paired bootstrap)

```
1. diffs = baseline_rates - syncode_rates   # [164] per-problem deltas
2. delta_mean = np.mean(diffs)
3. bootstrap_deltas = np.zeros(n_bootstrap)
4. rng = np.random.default_rng(seed=42)
5. for i in range(n_bootstrap):
6.     indices = rng.integers(0, len(diffs), size=len(diffs))
7.     bootstrap_deltas[i] = np.mean(diffs[indices])
8. ci_lower = np.percentile(bootstrap_deltas, alpha/2 * 100)   # 2.5th
9. ci_upper = np.percentile(bootstrap_deltas, (1-alpha/2) * 100)  # 97.5th
10. p_value = np.mean(bootstrap_deltas <= 0)   # one-sided: fraction where delta <= 0
11. return (delta_mean, ci_lower, ci_upper, p_value)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | BootstrapCI.compute | Paired bootstrap 10,000 iter, percentile CI, one-sided p_value |
| L-5-2 | evaluate_gate + save_results | Gate logic: PASS/PARTIAL/FAIL; JSON serialization |

---

## A-8: Mechanism Verifier [Complexity: 9, Budget: 2]

**Applied**: Standard PyTorch

### API Signatures

```python
# h-m1/code/mechanism_verifier.py
import ast as ast_module
import json
from typing import Any

class MechanismVerifier:
    """Pre-experiment verification: GrammarAlignedLogitsProcessor presence + constraint_active_rate."""

    def check_logits_processor(self, syn_model: Any) -> bool:
        """Inspect syn_model for GrammarAlignedLogitsProcessor.
        Checks: syn_model.logits_processor, syn_model.grammar_decoder, model.logits_processor_list.
        Returns True if any grammar-constraining processor found."""
        ...

    def run_test_samples(
        self,
        syn_generator: Any,  # ExtendedSyncodeGenerator (already loaded)
        test_prompt: str,
        n_test: int = 5,
    ) -> dict:
        """Generate n_test samples via syn_generator._generate_single_constrained.
        Returns {constraint_active_rate: float, ast_valid_rate: float}."""
        ...

    def verify(
        self,
        syn_generator: Any,  # ExtendedSyncodeGenerator (already loaded)
        test_prompt: str,
        output_path: str,
    ) -> dict:
        """Run all pre-checks; save to mechanism_verification.json.
        Returns {grammar_lp_present: bool, constraint_active_rate: float, pre_check_passed: bool}."""
        ...
```

### Pseudo-code: verify

```
1. grammar_lp_present = check_logits_processor(syn_generator.syn_model)
2. test_results = run_test_samples(syn_generator, test_prompt, n_test=5)
3. constraint_active_rate = test_results["constraint_active_rate"]
4. pre_check_passed = grammar_lp_present AND constraint_active_rate >= 0.3
5. result = {grammar_lp_present, constraint_active_rate, ast_valid_rate, pre_check_passed}
6. save result to output_path as JSON
7. return result
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | check_logits_processor | Inspect syn_model attrs for grammar processor |
| L-8-2 | run_test_samples + verify | 5-sample test, threshold check, JSON save |

---

## Summary: Subtask Allocation

| Epic | Budget | Used | Subtask IDs |
|------|--------|------|-------------|
| A-3 | 4 | 4 | L-3-1, L-3-2, L-3-3, L-3-4 |
| A-9 | 4 | 4 | L-9-1, L-9-2, L-9-3, L-9-4 |
| A-2 | 2 | 2 | L-2-1, L-2-2 |
| A-10 | 2 | 2 | L-10-1, L-10-2 |
| A-5 | 2 | 2 | L-5-1, L-5-2 |
| A-8 | 2 | 2 | L-8-1, L-8-2 |
| **Total** | **16** | **16** | |
