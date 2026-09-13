# Architecture: h-m2

**Hypothesis:** h-m2 — Mechanistic Complementarity of mypy/ast Repair vs. SynCode (MECHANISM / INCREMENTAL)
**Date:** 2026-05-10
**Gate:** SHOULD_WORK

Applied: iterative-feedback-repair-loop (Olausson 2023 / SELF-REFINE)
Applied: Jaccard-complement C_score independence null model

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1 code analyzed)
**Status**: Patterns found from base code
**Analyzed Path**: `docs/youra_research/20260508_verifai/h-m1/code/`
**Findings**: h-m1 uses flat module layout (no subpackages). All classes importable from top-level files. `FMDClassifier` uses temp-file mypy API; `BootstrapCI.compute()` takes numpy arrays of rates; `TransitionExtractor.extract()` operates on pool dicts. Import paths verified from actual `.py` files.

---

## File Organization

h-m2/code/
- config.py              (h-m2 config, extends h-m1 ExperimentConfig)
- mypy_feedback_repair.py  (NEW — core mechanism)
- c_score_calculator.py    (NEW — Jaccard complement + bootstrap)
- z3_eligibility_delta.py  (NEW — ΔP measurement)
- run_experiment.py        (NEW — orchestrator for all FRs)

Reused from h-m1/code/ (no copy — direct imports):
- baseline_generator.py
- fmd_classifier.py
- bootstrap_ci.py
- transition_extractor.py
- syncode_generator.py
- visualization.py

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ExtendedBaselineGenerator | `from baseline_generator import ExtendedBaselineGenerator` | `h-m1/code/baseline_generator.py` |
| FMDClassifier | `from fmd_classifier import FMDClassifier` | `h-m1/code/fmd_classifier.py` |
| BootstrapCI | `from bootstrap_ci import BootstrapCI` | `h-m1/code/bootstrap_ci.py` |
| TransitionExtractor | `from transition_extractor import TransitionExtractor` | `h-m1/code/transition_extractor.py` |
| ExtendedSyncodeGenerator | `from syncode_generator import ExtendedSyncodeGenerator` | `h-m1/code/syncode_generator.py` |
| ExperimentConfig | `from config import ExperimentConfig` | `h-m1/code/config.py` |

**Note**: run_experiment.py must set `sys.path.insert(0, "<abs_path>/h-m1/code")` before imports, or use a .pth / PYTHONPATH env var. Paths verified from actual h-m1/code/*.py files (flat module, no __init__.py subpackage).

---

## Module Definitions

### H2Config (`h-m2/code/config.py`)

**Dependencies**: h-m1 ExperimentConfig (dataclass extension)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class MypyRepairConfig:
    max_rounds: int = 3
    repair_temperature: float = 0.2
    max_new_tokens: int = 512
    mypy_flags: List[str] = field(default_factory=lambda: ["--ignore-missing-imports", "--no-error-summary"])
    mypy_timeout: int = 30
    mechanism_activated_threshold: float = 0.10

@dataclass
class CScoreConfig:
    n_bootstrap: int = 10000
    alpha: float = 0.0167  # Bonferroni: 0.05/3
    seed: int = 42
    min_stratum_size: int = 10

@dataclass
class Z3DeltaConfig:
    z3_timeout_seconds: int = 60
    arith_density_threshold: float = 0.1  # heuristic for z3_eligible

@dataclass
class H2OutputConfig:
    data_dir: str = "h-m2/data/"
    results_dir: str = "h-m2/results/"
    figures_dir: str = "h-m2/figures/"
    baseline_pool_file: str = "baseline_pool.jsonl"
    syncode_pool_file: str = "syncode_pool.jsonl"
    mypy_repair_pool_file: str = "mypy_repair_pool.jsonl"
    fmd_classification_file: str = "fmd_classification.jsonl"
    f_syncode_transitions_file: str = "f_syncode_transitions.json"
    f_mypy_transitions_file: str = "f_mypy_transitions.json"
    c_score_results_file: str = "c_score_results.json"
    z3_eligibility_delta_file: str = "z3_eligibility_delta.json"
    metrics_file: str = "metrics.json"
    progress_baseline_file: str = "progress_baseline.json"
    progress_syncode_file: str = "progress_syncode.json"
    progress_repair_file: str = "progress_repair.json"

@dataclass
class H2ExperimentConfig:
    hypothesis_id: str = "h-m2"
    n_problems: int = 164
    n_samples: int = 20
    h_m1_code_dir: str = ""       # abs path to h-m1/code/
    h_e1_baseline_pool: str = ""  # abs path to h-e1/data/baseline_pool.jsonl
    h_m1_syncode_pool: str = ""   # abs path to h-m1/data/syncode_pool.jsonl
    repair: MypyRepairConfig = field(default_factory=MypyRepairConfig)
    c_score: CScoreConfig = field(default_factory=CScoreConfig)
    z3: Z3DeltaConfig = field(default_factory=Z3DeltaConfig)
    output: H2OutputConfig = field(default_factory=H2OutputConfig)
```

---

### MypyFeedbackRepair (`h-m2/code/mypy_feedback_repair.py`)

**Dependencies**: config.H2ExperimentConfig, transformers (CodeLlama-7B)

```python
from typing import Dict, List, Optional, Tuple
from config import MypyRepairConfig

class MypyFeedbackRepair:
    def __init__(self, cfg: MypyRepairConfig, model=None, tokenizer=None) -> None: ...
    def load_model(self, model_name: str = "codellama/CodeLlama-7b-hf") -> None: ...

    def _parse_mypy_errors(self, stdout: str) -> List[Dict]: ...
    # Returns list of {line_num, error_type, message}

    def _format_structured_feedback(self, ast_valid: bool, ast_error: Optional[str],
                                     mypy_errors: List[Dict]) -> str: ...

    def _build_repair_prompt(self, original_prompt: str, current_code: str,
                              feedback: str) -> str: ...

    def _generate_repair(self, prompt: str) -> str: ...
    # Uses self.model/tokenizer at repair_temperature=0.2

    def repair_sample(self, baseline_code: str, problem: dict,
                       task_id: str, sample_idx: int) -> dict: ...
    # Returns: {task_id, problem_idx, sample_idx, rounds_used, final_code,
    #           success, feedback_history, ast_valid_final, mypy_exit_code_final}
    # Logs: "mypy_feedback_applied: round={r}, errors_before={n}, errors_after={m}"

    def repair_pool(self, baseline_pool: Dict[str, List[dict]],
                    problems: Dict[str, dict],
                    output_path: str, progress_path: str) -> Dict[str, List[dict]]: ...
    # Checkpoints every 10 problems; resumes from progress_path
    # Returns: {task_id: [repair_record, ...]}

    def compute_mechanism_activated_rate(self, repair_pool: Dict[str, List[dict]]) -> float: ...
    # fraction of samples where rounds_used > 0
```

---

### CScoreCalculator (`h-m2/code/c_score_calculator.py`)

**Dependencies**: config.CScoreConfig, numpy

```python
from typing import Dict, List, Set, Tuple
import numpy as np
from config import CScoreConfig

class CScoreCalculator:
    def __init__(self, cfg: CScoreConfig) -> None: ...

    def compute_c_score(self, set_a: Set[str], set_b: Set[str],
                         stratum: List[str]) -> Dict: ...
    # Returns: {j_obs, e_j, c_score, r1, r2, intersection_size, union_size}

    def bootstrap_c_score_ci(self, set_a: Set[str], set_b: Set[str],
                               stratum: List[str]) -> Dict: ...
    # 10000 problem-level resamples; seed=42
    # Returns: {mean, ci_lower, ci_upper, p_value}

    def define_eligibility_conditioned_stratum(
        self, fmd_classifications: Dict[str, List[str]],
        mypy_eligible_problems: Set[str]) -> List[str]: ...
    # Problems where >=1 sample FMD=type_structural AND mypy-eligible

    def compute_difficulty_quintiles(
        self, problems: List[str],
        baseline_pass_rates: Dict[str, float]) -> Dict[int, List[str]]: ...
    # Returns {quintile_idx: [task_ids]}

    def compute_c_score_by_quintile(
        self, set_a: Set[str], set_b: Set[str],
        quintiles: Dict[int, List[str]]) -> Dict[int, Dict]: ...

    def save_results(self, conditioned_result: Dict, raw_result: Dict,
                      quintile_results: Dict, output_path: str) -> dict: ...
```

---

### Z3EligibilityDelta (`h-m2/code/z3_eligibility_delta.py`)

**Dependencies**: config.Z3DeltaConfig, ast, z3

```python
from typing import Dict, List, Tuple
from config import Z3DeltaConfig

class Z3EligibilityDelta:
    def __init__(self, cfg: Z3DeltaConfig) -> None: ...

    def _compute_arith_density(self, code: str) -> float: ...
    # fraction of AST nodes that are arithmetic BinOp / Compare

    def _has_return_annotation(self, code: str) -> bool: ...

    def check_z3_eligible(self, code: str) -> bool: ...
    # heuristic: arith_density > threshold AND has_return_annotation
    # OR: attempt actual z3.Solver().check() with 60s timeout

    def compute_eligibility_rate(
        self, pool: Dict[str, List[dict]], use_best_of: bool = True) -> Dict[str, bool]: ...
    # {task_id: z3_eligible}; use best sample (pick first ast_valid if use_best_of)

    def compute_delta_p(
        self, baseline_eligible: Dict[str, bool],
        post_mypy_eligible: Dict[str, bool]) -> Tuple[float, float, float, float]: ...
    # Returns: (delta_p, ci_lower, ci_upper, p_value) via bootstrap (10000 iters, seed=42)

    def save_results(self, delta_p: float, ci_lower: float, ci_upper: float,
                      p_value: float, output_path: str) -> dict: ...
```

---

### RunExperiment (`h-m2/code/run_experiment.py`)

**Dependencies**: All above modules + h-m1 modules via sys.path

```python
import sys, os, json, logging
from typing import Dict, List

# sys.path.insert(0, cfg.h_m1_code_dir) — enables h-m1 imports

from config import H2ExperimentConfig
from mypy_feedback_repair import MypyFeedbackRepair
from c_score_calculator import CScoreCalculator
from z3_eligibility_delta import Z3EligibilityDelta

# h-m1 imports (after sys.path patch)
from baseline_generator import ExtendedBaselineGenerator
from fmd_classifier import FMDClassifier
from transition_extractor import TransitionExtractor
from syncode_generator import ExtendedSyncodeGenerator
from visualization import Visualizer   # if exists in h-m1

def setup_directories(cfg: H2ExperimentConfig) -> None: ...
def setup_logging(log_path: str) -> logging.Logger: ...

def run_phase_1_baseline_pool(cfg: H2ExperimentConfig,
                               problems: Dict) -> Dict[str, List[dict]]: ...
# FR-1: extend baseline to 164 problems; reuse h-e1 and h-m1 pools

def run_phase_2_fmd_classification(cfg: H2ExperimentConfig,
                                    baseline_pool: Dict,
                                    problems: Dict) -> Dict[str, List[str]]: ...
# FR-2: classify all 164×20 samples

def run_phase_3_mypy_repair(cfg: H2ExperimentConfig,
                              baseline_pool: Dict,
                              problems: Dict) -> Dict[str, List[dict]]: ...
# FR-3: apply MypyFeedbackRepair on all problems

def run_phase_4_syncode_pool(cfg: H2ExperimentConfig,
                               problems: Dict,
                               baseline_pool: Dict) -> Dict[str, List[dict]]: ...
# FR-4: extend h-m1 SynCode pool to full 164 problems

def run_phase_5_extract_transitions(cfg: H2ExperimentConfig,
                                     baseline_pool: Dict,
                                     syncode_pool: Dict,
                                     repair_pool: Dict,
                                     fmd_classifications: Dict,
                                     problems: Dict) -> Tuple: ...
# FR-5: returns (f_syncode_set, f_mypy_set, mypy_eligible_set)

def run_phase_6_c_score(cfg: H2ExperimentConfig,
                          f_syncode: set, f_mypy: set,
                          fmd_classifications: Dict,
                          mypy_eligible: set,
                          baseline_pass_rates: Dict) -> Dict: ...
# FR-6: conditioned C_score + quintile breakdown

def run_phase_7_z3_delta(cfg: H2ExperimentConfig,
                           baseline_pool: Dict,
                           repair_pool: Dict) -> Dict: ...
# FR-7: ΔP(Z3_eligible)

def run_phase_8_visualization(cfg: H2ExperimentConfig,
                                c_score_results: Dict,
                                z3_results: Dict,
                                fmd_classifications: Dict,
                                repair_pool: Dict) -> None: ...
# FR-8: 6 figures

def evaluate_gate(c_score_results: Dict, z3_results: Dict) -> str: ...
# Returns PASS / PARTIAL / FAIL

def save_metrics(cfg: H2ExperimentConfig, c_score_results: Dict,
                  z3_results: Dict, fmd_stats: Dict,
                  repair_stats: Dict, gate_result: str) -> None: ...
# FR-9: writes metrics.json

def main(cfg: H2ExperimentConfig) -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment & Config | Install deps, set CUDA, create dirs, verify h-m1 imports, write H2ExperimentConfig | 7 | 2+2+1+2 |
| A-2 | Baseline Pool (164 problems) | Extend h-e1/h-m1 pool to full 164 via ExtendedBaselineGenerator; checkpoint/resume | 10 | 3+3+1+3 |
| A-3 | FMD Classification | Run FMDClassifier on all 3280 samples; validate type_structural stratum ≥10; cross-check sequential vs. parallel | 11 | 3+3+2+3 |
| A-4 | mypy Feedback Repair | Implement MypyFeedbackRepair (3-round loop, structured feedback, T=0.2); checkpoint/resume; verify mechanism_activated > 0.10 | 16 | 4+4+4+4 |
| A-5 | SynCode Pool Extension | Extend h-m1 SynCode pool (20 problems) to full 164 via ExtendedSyncodeGenerator; extract F_SynCode at full N=164 | 12 | 3+3+3+3 |
| A-6 | F_mypy Transition Extraction | Extract F_mypy→✓ from repair_pool; validate non-empty; compute repair_success_rate and mechanism_activated_rate | 8 | 2+2+2+2 |
| A-7 | C_score Computation | Implement CScoreCalculator: eligibility-conditioned stratum, J_obs, E[J], C_score, bootstrap CI (Bonferroni α=0.0167), quintile breakdown | 17 | 4+4+5+4 |
| A-8 | Z3 Eligibility Delta | Implement Z3EligibilityDelta: heuristic z3_eligible check, ΔP, bootstrap CI; 60s timeout | 13 | 3+3+4+3 |
| A-9 | Visualization (6 figures) | gate_metrics.png, jaccard_heatmap.png, fmd_distribution.png, z3_eligibility_comparison.png, repair_convergence.png, quintile_c_score.png | 10 | 3+2+2+3 |
| A-10 | Gate Evaluation & Metrics JSON | Assemble metrics.json with full schema; PASS/PARTIAL/FAIL logic; null result protocol logging | 8 | 2+2+2+2 |
| A-11 | Integration & End-to-End Test | Wire run_experiment.py phases; dry-run on 5 problems; validate all output files produced | 11 | 3+3+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4, A-7], Medium(9-13): [A-3, A-5, A-8, A-11], Low(4-8): [A-1, A-2, A-6, A-9, A-10]

---

## Data Flow

- FR-1 → `baseline_pool.jsonl` (164×20 = 3280 records)
- FR-2 → `fmd_classification.jsonl` (per-sample stratum labels)
- FR-3 → `mypy_repair_pool.jsonl` (3280 repair records)
- FR-4 → `syncode_pool.jsonl` + `f_syncode_transitions.json`
- FR-5 → `f_mypy_transitions.json`
- FR-6 (needs FR-4, FR-5, FR-2) → `c_score_results.json`
- FR-7 (needs FR-3, FR-1) → `z3_eligibility_delta.json`
- FR-8 (needs FR-2 through FR-7) → `figures/*.png`
- FR-9 (needs FR-6, FR-7) → `metrics.json`

## Key Constraints

- All h-m1 modules imported via `sys.path.insert(0, cfg.h_m1_code_dir)` — no code copying
- `BootstrapCI` from h-m1 computes delta between two rate arrays; `CScoreCalculator` implements independent C_score bootstrap (different interface)
- `FMDClassifier` from h-m1 classifies to {syntax, type, functional, success}; h-m2 maps "type" → type_structural stratum
- Checkpoint files: `progress_baseline.json`, `progress_syncode.json`, `progress_repair.json` — all resume-capable
- `np.random.seed(42)` set before all bootstrap loops (NFR-1)
- Single GPU: `CUDA_VISIBLE_DEVICES` must be set before launching run_experiment.py
