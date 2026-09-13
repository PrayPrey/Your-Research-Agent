# Architecture: h-m1 — Distinct Failure Channel: SynCode Eliminates Syntactic Invalidity

**Type:** MECHANISM (INCREMENTAL — extends h-e1)
**Gate:** MUST_WORK
**Applied:** incremental-experiment-extension-pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code (h-e1/code/ — direct file reads performed)
**Analyzed Path**: `docs/youra_research/20260508_verifai/h-e1/code/`
**Findings**: Flat module layout; `BaselineGenerator`/`SyncodeGenerator`/`MetricsEvaluator`/`Visualizer` are standalone classes; `run_experiment.py` orchestrates via `sys.path.insert`. h-e1 seed scheme is `list(range(20))` — h-m1 must replace with `problem_idx × 100 + sample_idx`. `SyncodeGenerator` class name uses lowercase-c spelling; import is `from syncode_generator import SyncodeGenerator`.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| BaselineGenerator | `from baseline_generator import BaselineGenerator` | `h-e1/code/baseline_generator.py` |
| SyncodeGenerator | `from syncode_generator import SyncodeGenerator` | `h-e1/code/syncode_generator.py` |
| MetricsEvaluator | `from metrics import MetricsEvaluator` | `h-e1/code/metrics.py` |
| Visualizer | `from visualization import Visualizer` | `h-e1/code/visualization.py` |
| load_humaneval_plus | `from data_loader import load_humaneval_plus` | `h-e1/code/data_loader.py` |
| ExperimentConfig | `from config import ExperimentConfig` | `h-e1/code/config.py` |

**Verified from**: `docs/youra_research/20260508_verifai/h-e1/code/` (actual implementation)

**Key divergence from h-e1 spec**: `SyncodeGenerator` (lowercase c) not `SynCodeGenerator`; seed scheme in h-e1 is `list(range(20))`, not problem-indexed — h-m1 introduces correct scheme `seed = problem_idx × 100 + sample_idx`.

---

## File Organization

h-m1/code/
- `config.py` — ExperimentConfig (h-m1 version, extends h-e1 dataclasses)
- `baseline_generator.py` — ExtendedBaselineGenerator (164 problems, h-e1 reuse + resume)
- `syncode_generator.py` — ExtendedSyncodeGenerator (164 problems, constraint_active logging)
- `ast_metrics.py` — ASTFailureRateComputer (per-problem arrays, delta_ast)
- `bootstrap_ci.py` — BootstrapCI (10,000 iterations, paired problem-level)
- `fmd_classifier.py` — FMDClassifier (multi-label: syntax/type/functional/success)
- `transition_extractor.py` — TransitionExtractor (F_SynCode→✓ set, serialization)
- `mechanism_verifier.py` — MechanismVerifier (GrammarAlignedLogitsProcessor check)
- `visualization.py` — HM1Visualizer (4 figures)
- `run_experiment.py` — main orchestrator with progress checkpointing
- tests/
  - `test_ast_metrics.py`
  - `test_bootstrap_ci.py`
  - `test_fmd_classifier.py`
  - `test_transition_extractor.py`

---

## Module Definitions

### config (`h-m1/code/config.py`)

**Dependencies**: stdlib dataclasses only

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class ModelConfig:
    model_name: str = "codellama/CodeLlama-7b-hf"
    device_map: str = "auto"
    torch_dtype: str = "float16"

@dataclass
class GenerationConfig:
    temperature: float = 0.8
    max_new_tokens: int = 512
    n_samples: int = 20
    top_p: float = 0.95
    do_sample: bool = True

@dataclass
class BootstrapConfig:
    n_bootstrap: int = 10000
    alpha: float = 0.05

@dataclass
class ThresholdConfig:
    delta_ast_min: float = 0.0
    ci_lower_min: float = 0.0
    constraint_active_rate_min: float = 0.3

@dataclass
class OutputConfig:
    data_dir: str = "h-m1/data/"
    results_dir: str = "h-m1/results/"
    figures_dir: str = "h-m1/figures/"
    baseline_pool_file: str = "baseline_pool.jsonl"
    syncode_pool_file: str = "syncode_pool.jsonl"
    progress_file: str = "progress.json"
    h_e1_baseline_pool: str = "h-e1/data/baseline_pool.jsonl"

@dataclass
class ExperimentConfig:
    hypothesis_id: str = "h-m1"
    n_problems: int = 164
    model: ModelConfig = field(default_factory=ModelConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    bootstrap: BootstrapConfig = field(default_factory=BootstrapConfig)
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
```

---

### baseline_generator (`h-m1/code/baseline_generator.py`)

**Dependencies**: config, transformers, torch, evalplus, json

```python
import json
from typing import Dict, List, Optional, Set

class ExtendedBaselineGenerator:
    """Extends h-e1 BaselineGenerator to 164 problems with correct seed scheme."""

    def __init__(
        self,
        model_name: str = "codellama/CodeLlama-7b-hf",
        temperature: float = 0.8,
        max_new_tokens: int = 512,
        n_samples: int = 20,
    ) -> None: ...

    def load_model(self) -> None:
        """Load CodeLlama-7B via AutoModelForCausalLM, device_map='auto'."""
        ...

    def _compute_seed(self, problem_idx: int, sample_idx: int) -> int:
        """seed = problem_idx * 100 + sample_idx"""
        ...

    def _generate_single(self, prompt: str, seed: int) -> str: ...

    def load_h_e1_pool(self, h_e1_path: str) -> Dict[str, List[dict]]:
        """Load first-20-problem pool from h-e1/data/baseline_pool.jsonl.
        Returns {task_id: [record_dicts]} for reuse."""
        ...

    def load_progress(self, progress_path: str) -> Set[str]:
        """Return set of completed task_ids for resume support."""
        ...

    def generate_pool(
        self,
        problems: Dict[str, dict],
        output_path: str,
        progress_path: str,
        h_e1_pool_path: Optional[str] = None,
    ) -> Dict[str, List[dict]]:
        """Generate 164×20 pool; reuse h-e1 first 20 if available; resume from progress.
        Record format: {task_id, problem_idx, sample_idx, seed, completion, ast_valid}
        Returns {task_id: [record_dicts]}"""
        ...
```

---

### syncode_generator (`h-m1/code/syncode_generator.py`)

**Dependencies**: config, syncode, transformers, torch, evalplus, json

```python
from typing import Dict, List, Optional, Set, Tuple

class ExtendedSyncodeGenerator:
    """Extends h-e1 SyncodeGenerator to 164 problems with constraint_active logging."""

    def __init__(
        self,
        model_name: str = "codellama/CodeLlama-7b-hf",
        grammar: str = "python",
        mode: str = "grammar_mask",
        temperature: float = 0.8,
        max_new_tokens: int = 512,
        n_samples: int = 20,
    ) -> None: ...

    def load_model(self) -> None: ...

    def _compute_seed(self, problem_idx: int, sample_idx: int) -> int:
        """seed = problem_idx * 100 + sample_idx"""
        ...

    def _generate_single_constrained(
        self, prompt: str, seed: int
    ) -> Tuple[str, bool]:
        """Returns (completion, constraint_active_flag)."""
        ...

    def load_progress(self, progress_path: str) -> Set[str]:
        """Return set of completed task_ids for resume support."""
        ...

    def generate_pool(
        self,
        problems: Dict[str, dict],
        output_path: str,
        progress_path: str,
    ) -> Dict[str, List[dict]]:
        """Generate 164×20 constrained pool; resume from progress.
        Record format: {task_id, problem_idx, sample_idx, seed, completion, ast_valid, constraint_active}
        Returns {task_id: [record_dicts]}"""
        ...

    def compute_constraint_active_rate(
        self, pool: Dict[str, List[dict]]
    ) -> float:
        """Fraction of samples where constraint_active=True across all problems."""
        ...
```

---

### ast_metrics (`h-m1/code/ast_metrics.py`)

**Dependencies**: stdlib (ast, json), numpy

```python
import numpy as np
from typing import Dict, List, Tuple

class ASTFailureRateComputer:

    def compute_per_problem_rates(
        self,
        pool: Dict[str, List[dict]],
    ) -> Dict[str, float]:
        """Returns {task_id: failure_rate} for all 164 problems."""
        ...

    def compute_arrays(
        self,
        baseline_pool: Dict[str, List[dict]],
        syncode_pool: Dict[str, List[dict]],
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Returns (baseline_rates[164], syncode_rates[164], ordered_task_ids).
        Arrays aligned by task_id order."""
        ...

    def compute_delta_ast(
        self,
        baseline_rates: np.ndarray,
        syncode_rates: np.ndarray,
    ) -> float:
        """delta_ast = mean(baseline_rates) - mean(syncode_rates)"""
        ...

    def save_results(
        self,
        baseline_rates: np.ndarray,
        syncode_rates: np.ndarray,
        task_ids: List[str],
        output_path: str,
    ) -> dict:
        """Serialize per_problem + aggregate to ast_failure_rates.json. Returns result dict."""
        ...
```

---

### bootstrap_ci (`h-m1/code/bootstrap_ci.py`)

**Dependencies**: numpy, json

```python
import numpy as np
from typing import Tuple

class BootstrapCI:

    def __init__(self, n_bootstrap: int = 10000, alpha: float = 0.05) -> None: ...

    def compute(
        self,
        baseline_rates: np.ndarray,
        syncode_rates: np.ndarray,
    ) -> Tuple[float, float, float, float]:
        """Paired problem-level bootstrap.
        Returns (delta_mean, ci_lower, ci_upper, p_value).
        p_value = fraction of bootstrap deltas <= 0 (one-sided)."""
        ...

    def evaluate_gate(
        self,
        delta_mean: float,
        ci_lower: float,
    ) -> str:
        """Returns 'PASS', 'PARTIAL', or 'FAIL'."""
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

---

### fmd_classifier (`h-m1/code/fmd_classifier.py`)

**Dependencies**: stdlib (ast), mypy.api, evalplus, json

```python
from typing import Dict, List

class FMDClassifier:
    """Multi-label failure mode distribution classifier.
    Categories: syntax | type | functional | success
    """

    def classify_completion(
        self,
        completion: str,
        task_id: str,
        problem: dict,
    ) -> str:
        """Returns category: 'syntax' | 'type' | 'functional' | 'success'."""
        ...

    def classify_pool(
        self,
        pool: Dict[str, List[dict]],
        problems: Dict[str, dict],
    ) -> Dict[str, List[str]]:
        """Returns {task_id: [category_per_sample]} for all pool records."""
        ...

    def compute_distribution(
        self,
        classifications: Dict[str, List[str]],
    ) -> Dict[str, float]:
        """Returns {category: proportion} across all samples."""
        ...

    def compute_syntax_shift(
        self,
        baseline_dist: Dict[str, float],
        syncode_dist: Dict[str, float],
    ) -> float:
        """syntax_rate_baseline - syntax_rate_syncode (directional check)."""
        ...

    def save_results(
        self,
        baseline_dist: Dict[str, float],
        syncode_dist: Dict[str, float],
        syntax_shift: float,
        output_path: str,
    ) -> dict: ...
```

---

### transition_extractor (`h-m1/code/transition_extractor.py`)

**Dependencies**: stdlib (json)

```python
from typing import Dict, List

class TransitionExtractor:
    """Extracts F_SynCode→✓ set: baseline fails ast, SynCode succeeds."""

    def extract(
        self,
        baseline_pool: Dict[str, List[dict]],
        syncode_pool: Dict[str, List[dict]],
    ) -> List[dict]:
        """Returns list of {problem_idx, sample_idx, task_id} transition records.
        Condition: baseline record ast_valid=False AND syncode record ast_valid=True,
        matched by (task_id, sample_idx)."""
        ...

    def compute_coverage_by_problem(
        self,
        transitions: List[dict],
        n_problems: int = 164,
    ) -> List[dict]:
        """Returns [{problem_idx, task_id, transitions_count}] per problem."""
        ...

    def save_results(
        self,
        transitions: List[dict],
        coverage: List[dict],
        output_path: str,
    ) -> dict:
        """Serialize to F_SynCode_success_transitions.json with transition_count + transition_rate."""
        ...
```

---

### mechanism_verifier (`h-m1/code/mechanism_verifier.py`)

**Dependencies**: syncode, torch, json

```python
from typing import Any

class MechanismVerifier:
    """Pre-experiment verification: GrammarAlignedLogitsProcessor presence + constraint_active_rate."""

    def check_logits_processor(self, syn_model: Any) -> bool:
        """Return True if GrammarAlignedLogitsProcessor in syn_model logits_processor list."""
        ...

    def run_test_samples(
        self,
        syn_generator,
        test_prompt: str,
        n_test: int = 5,
    ) -> dict:
        """Generate n_test samples; return {constraint_active_rate, ast_valid_rate}."""
        ...

    def verify(
        self,
        syn_generator,
        test_prompt: str,
        output_path: str,
    ) -> dict:
        """Run all pre-checks; save to mechanism_verification.json.
        Returns {grammar_lp_present, constraint_active_rate, pre_check_passed}."""
        ...
```

---

### visualization (`h-m1/code/visualization.py`)

**Dependencies**: matplotlib, seaborn, numpy, json

```python
import numpy as np
from typing import Dict, List

class HM1Visualizer:

    def __init__(self, figures_dir: str) -> None: ...

    def plot_gate_metrics(
        self,
        baseline_mean: float,
        syncode_mean: float,
        ci_lower: float,
        ci_upper: float,
        delta_ast: float,
        gate_result: str,
    ) -> None:
        """Bar chart with 95% CI error bars; PASS/FAIL annotation.
        Saves: gate_metrics.pdf + gate_metrics.png"""
        ...

    def plot_per_problem_scatter(
        self,
        baseline_rates: np.ndarray,
        syncode_rates: np.ndarray,
        task_ids: List[str],
    ) -> None:
        """Scatter: baseline_rate (x) vs syncode_rate (y); diagonal = no improvement.
        Saves: per_problem_scatter.pdf + per_problem_scatter.png"""
        ...

    def plot_fmd_comparison(
        self,
        baseline_dist: Dict[str, float],
        syncode_dist: Dict[str, float],
    ) -> None:
        """Side-by-side bar chart for syntax/type/functional/success proportions.
        Saves: fmd_comparison.pdf + fmd_comparison.png"""
        ...

    def plot_transition_heatmap(
        self,
        baseline_pool: Dict[str, List[dict]],
        syncode_pool: Dict[str, List[dict]],
        task_ids: List[str],
    ) -> None:
        """164×20 grid heatmap: transition / no-gain / already-correct.
        Saves: transition_heatmap.pdf + transition_heatmap.png"""
        ...

    def save_all(
        self,
        ast_results: dict,
        bootstrap_results: dict,
        fmd_results: dict,
        baseline_pool: Dict[str, List[dict]],
        syncode_pool: Dict[str, List[dict]],
        baseline_rates: np.ndarray,
        syncode_rates: np.ndarray,
        task_ids: List[str],
    ) -> None:
        """Generate all 4 required figures."""
        ...
```

---

### run_experiment (`h-m1/code/run_experiment.py`)

**Dependencies**: all h-m1 modules, argparse, json, os

```python
def get_paths(base_dir: str) -> dict:
    """Returns all data/results/figures path dict for h-m1."""
    ...

def load_pool_from_jsonl(path: str) -> Dict[str, List[dict]]:
    """Load JSONL pool records with full fields (ast_valid, constraint_active, etc.)."""
    ...

def main() -> int:
    """CLI orchestrator. Steps:
    0. Mechanism pre-verification
    1. Load datasets (164 HumanEval+ problems)
    2. Generate/load baseline pool (164 problems, reuse h-e1 first 20)
    3. Generate/load SynCode pool (164 problems, constraint_active logging)
    4. Compute per-problem AST failure rates
    5. Bootstrap CI statistical test → gate evaluation
    6. FMD classification
    7. F_SynCode→✓ transition extraction
    8. Compute consolidated metrics → metrics.json
    9. Generate 4 figures
    Returns 0 if gate PASS, 1 if gate FAIL."""
    ...
```

**CLI Args**:
- `--load_pools` — skip generation, load from disk
- `--skip_syncode` — baseline only (for testing)
- `--base_dir` — output root (default: h-m1 directory)
- `--num_problems` — limit problems (default: 164)
- `--skip_mechanism_check` — skip pre-verification

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config & Scaffold | config.py, directory structure, progress.json schema | 6 | 2+1+1+2 |
| A-2 | Baseline Pool Extension | ExtendedBaselineGenerator: h-e1 reuse, correct seed scheme, resume, 164 problems | 13 | 3+3+3+4 |
| A-3 | SynCode Pool Extension | ExtendedSyncodeGenerator: constraint_active logging, resume, 164 problems | 14 | 3+3+4+4 |
| A-4 | AST Failure Rate Computation | ASTFailureRateComputer: per-problem arrays, delta_ast, ast_failure_rates.json | 8 | 2+2+2+2 |
| A-5 | Bootstrap CI | BootstrapCI: 10,000-iter paired bootstrap, gate logic, bootstrap_ci.json | 10 | 2+2+4+2 |
| A-6 | FMD Classifier | FMDClassifier: ast/mypy/evalplus multi-label, distribution, fmd_results.json | 13 | 3+3+4+3 |
| A-7 | Transition Extractor | TransitionExtractor: F_SynCode→✓ set, coverage_by_problem, serialization | 8 | 2+2+2+2 |
| A-8 | Mechanism Verifier | MechanismVerifier: LogitsProcessor check, 5-sample test, mechanism_verification.json | 9 | 2+3+2+2 |
| A-9 | Visualization | HM1Visualizer: 4 figures (gate_metrics, scatter, fmd, heatmap) PDF+PNG | 14 | 3+2+4+5 |
| A-10 | Orchestrator & Tests | run_experiment.py main pipeline + unit tests for A-4/A-5/A-6/A-7 | 12 | 3+3+3+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3, A-9], Medium(9-13): [A-2, A-5, A-6, A-8, A-10], Low(4-8): [A-1, A-4, A-7]

---

## Data Flow

- `run_experiment.py` calls `MechanismVerifier.verify()` → `mechanism_verification.json`
- `ExtendedBaselineGenerator.generate_pool()` → `baseline_pool.jsonl` (records with `ast_valid`)
- `ExtendedSyncodeGenerator.generate_pool()` → `syncode_pool.jsonl` (records with `ast_valid`, `constraint_active`)
- `ASTFailureRateComputer.compute_arrays()` → `(baseline_rates[164], syncode_rates[164])` → `ast_failure_rates.json`
- `BootstrapCI.compute()` → `(delta_mean, ci_lower, ci_upper, p_value)` → `bootstrap_ci.json`
- `FMDClassifier.classify_pool()` → distributions → `fmd_results.json`
- `TransitionExtractor.extract()` → transitions → `F_SynCode_success_transitions.json`
- `HM1Visualizer.save_all()` → 4 figures in `h-m1/figures/`
- consolidated gate result → `metrics.json`

## Key Implementation Notes

- **Seed scheme change from h-e1**: h-e1 used `list(range(20))` for all problems; h-m1 uses `problem_idx * 100 + sample_idx` — controlled reproduction requires regenerating h-e1 problems with new seeds OR documenting the discrepancy
- **Pool record format change**: h-e1 JSONL lacks `ast_valid`, `problem_idx`, `sample_idx` fields; h-m1 adds these at write time; `load_pool_from_jsonl` must handle both formats
- **Resume support**: track completed `task_id` set in `progress.json`; both generators append to existing JSONL and skip completed tasks
- **h-e1 baseline reuse**: `load_h_e1_pool()` reads h-e1/data/baseline_pool.jsonl; since seed scheme differs, reused records still have correct `completion` strings but seeds will not match — acceptable for pool extension, note in results
