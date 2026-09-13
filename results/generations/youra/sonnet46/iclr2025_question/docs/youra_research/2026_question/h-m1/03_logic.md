# Logic: H-M1 Statistical Analysis

**Hypothesis:** H-M1 (MECHANISM PoC)
**Type:** Pure statistical analysis — numpy arrays, scipy.stats

Applied: Standard scipy.stats statistical analysis pipeline

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: API signatures verified from base code via direct file reads (Serena project activation unavailable; files read directly)
**Analyzed Path**: `docs/youra_research/20260315_question/h-e1/code/`
**Relevant Symbols**:
- `cohen_d(group1, group2)` in `evaluate.py` — pooled std variant (note: uses `(var1+var2)/2`, NOT `(n1-1)*v1+(n2-1)*v2`)
- `load_task(task_name, config)` in `data.py` — interleaving logic verified
- `ExperimentConfig` in `config.py` — flat dataclass, `get_config()` factory, `load_config()` NOT present in h-e1
- `verify_mechanism_activated(scores, labels, task_name)` in `evaluate.py` — returns `(bool, Dict[str, bool])`

---

## External Dependencies API

### API Signatures (From Actual h-e1 Code)

```python
# From: h-e1/code/evaluate.py (ACTUAL CODE)
def cohen_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """group1=hallucinated scores, group2=non-hallucinated scores. Returns float."""
    # Uses pooled_std = sqrt((var1 + var2) / 2)  ← simple average, NOT weighted
    ...

# From: h-e1/code/data.py (ACTUAL CODE)
def load_task(task_name: str, config: ExperimentConfig) -> TaskData:
    """Interleaves right(label=0) and hallucinated(label=1) per raw example."""
    # ds = load_dataset(config.halueval_hf_id, hf_config, split="data")
    # Returns TaskData with labels shape (N,), balanced 50/50
    ...

# From: h-e1/code/config.py (ACTUAL CODE)
def get_config() -> ExperimentConfig:
    """Factory — NOT load_config(). H-M1 must define its own load_config()."""
    ...
```

**CRITICAL**: h-e1 `config.py` has `get_config()`, NOT `load_config()`. H-M1 defines its own `load_config(path)`.
**CRITICAL**: h-e1 `cohen_d` uses `pooled_std = sqrt((var1+var2)/2)`, not the weighted formula in PRD. Copy the actual formula.

---

## A-3: Statistical Analysis Core [Complexity: 3, Budget: 3]

Applied: Standard scipy.stats statistical analysis pipeline

### API Signatures

```python
# analyze.py
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np
from scipy.stats import entropy, ranksums

@dataclass
class TaskAnalysisResult:
    task_name: str
    kl_divergence_from_uniform: float   # nats
    kl_passes: bool                      # kl > 0.05
    wilcoxon_pvalue: float
    wilcoxon_statistic: float
    wilcoxon_passes: bool                # pvalue < 0.05
    p_near_uniform: float                # proportion shape (scalar)
    class_means: List[float]             # [P(contra), P(neutral), P(entail)] means
    cohens_d: float
    not_near_uniform: bool               # p_near_uniform < 0.10

@dataclass
class GateResult:
    gate_pass: bool
    kl_all_pass: bool
    wilcoxon_pass_count: int             # 0-3
    mechanism_activated: bool


def compute_cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Cohen's d; group1=hallucinated, group2=non-hallucinated. Returns float."""
    # Mirrors h-e1 cohen_d: pooled_std = sqrt((var1+var2)/2)


def analyze_nli_distribution(
    scores_nxt3: np.ndarray,   # shape (N, 3): [P(contra), P(neutral), P(entail)]
    labels_n: np.ndarray,      # shape (N,), binary {0,1}
    task_name: str,
    config: "ExperimentConfig",
) -> TaskAnalysisResult:
    """KL divergence + Wilcoxon + near-uniform + Cohen's d for one task."""
    ...


def evaluate_gate(
    results: List[TaskAnalysisResult],
    config: "ExperimentConfig",
) -> GateResult:
    """MUST_WORK gate: KL>0.05 on all 3 AND Wilcoxon p<0.05 on >=2/3."""
    ...


def verify_mechanism_activated(
    results: List[TaskAnalysisResult],
    config: "ExperimentConfig",
) -> Tuple[bool, Dict[str, Dict[str, bool]]]:
    """Per-task indicators: kl_passes, wilcoxon_passes, not_near_uniform.
    Returns (all_pass, {task_name: {indicator: bool}})."""
    ...
```

### Pseudo-code: analyze_nli_distribution

```
1. class_means = scores_nxt3.mean(axis=0)           # shape (3,)
2. uniform = np.array([1/3, 1/3, 1/3])
3. kl = entropy(class_means + 1e-10, uniform + 1e-10)  # scipy.stats.entropy(pk, qk)
4. kl_passes = kl > config.kl_threshold             # 0.05
5. contra_scores = scores_nxt3[:, 0]                # P(contradiction) column
6. hal_scores = contra_scores[labels_n == 1]        # shape (N_hal,)
7. corr_scores = contra_scores[labels_n == 0]       # shape (N_corr,)
8. stat, pvalue = ranksums(hal_scores, corr_scores)
9. wilcoxon_passes = pvalue < config.wilcoxon_alpha  # 0.05
10. near_uniform_mask = np.all(np.abs(scores_nxt3 - 1/3) < 0.05, axis=1)
11. p_near_uniform = near_uniform_mask.mean()
12. not_near_uniform = p_near_uniform < 0.10
13. d = compute_cohens_d(hal_scores, corr_scores)
14. return TaskAnalysisResult(...)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | compute_cohens_d | Implement pooled-std Cohen's d matching h-e1 formula |
| L-3-2 | analyze_nli_distribution | KL + Wilcoxon + near-uniform + class means |
| L-3-3 | evaluate_gate + verify_mechanism_activated | Gate logic + mechanism indicator logging |

---

## A-2: Data Loading [Complexity: 2, Budget: 2]

Applied: Standard scipy.stats statistical analysis pipeline

### API Signatures

```python
# data.py
from dataclasses import dataclass
from typing import Dict, List
import numpy as np

@dataclass
class TaskScores:
    task_name: str
    scores_nxt3: np.ndarray   # shape (N, 3): [P(contra), P(neutral), P(entail)]
    labels_n: np.ndarray      # shape (N,), binary {0,1}
    n_examples: int            # expected 20000


def load_h_e1_scores(results_path: str) -> Dict[str, np.ndarray]:
    """Load (N,3) score matrices from h-e1_results.json.
    Returns: {task_name: np.ndarray shape (N,3)}. Raises FileNotFoundError if missing."""
    ...


def load_halueval_labels(task_name: str, config: "ExperimentConfig") -> np.ndarray:
    """Reload HaluEval labels using same interleaving as h-e1/data.py:load_task().
    Returns: np.ndarray shape (N,), binary, balanced 50/50."""
    # Uses: load_dataset(config.halueval_hf_id, config.hf_config_names[task_name], split="data")
    # Interleaves right_response(0) and hallucinated_response(1) per raw example
    ...


def load_task_data(
    task_name: str,
    scores_dict: Dict[str, np.ndarray],
    config: "ExperimentConfig",
) -> TaskScores:
    """Combine scores + labels for one task. Verifies N matches."""
    ...


def load_all_tasks(config: "ExperimentConfig") -> List[TaskScores]:
    """Load all 3 tasks. Verifies shapes (20000, 3) per task."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | load_h_e1_scores | JSON load + shape verification + FileNotFoundError with message |
| L-2-2 | load_halueval_labels + load_task_data + load_all_tasks | Label interleaving (mirrors h-e1 load_task logic) |

---

## A-9: Main Orchestration [Complexity: 2, Budget: 2]

Applied: Standard scipy.stats statistical analysis pipeline

### API Signatures

```python
# run_experiment.py
import logging
from pathlib import Path
from typing import List

def setup_logging() -> None:
    """Configure root logger: INFO level, timestamped format."""
    ...

def load_config(path: str = "config.yaml") -> "ExperimentConfig":
    """Load YAML config into ExperimentConfig dataclass."""
    ...

def save_results(
    results: List["TaskAnalysisResult"],
    gate: "GateResult",
    config: "ExperimentConfig",
) -> None:
    """Save h_m1_results.json (full) and h_m1_summary.json (gate fields)."""
    ...

def main() -> None:
    """Full pipeline. Exits with sys.exit(1) if h-e1 results missing."""
    ...

if __name__ == "__main__":
    main()
```

### Pseudo-code: main()

```
1. setup_logging()
2. config = load_config("config.yaml")
3. Verify h_e1_results_path exists → sys.exit(1) if not
4. task_data_list = load_all_tasks(config)
5. results = [analyze_nli_distribution(td.scores_nxt3, td.labels_n, td.task_name, config)
              for td in task_data_list]
6. gate = evaluate_gate(results, config)
7. _, indicators = verify_mechanism_activated(results, config)
8. save_results(results, gate, config)
9. generate_all_figures(task_data_list, results, config.figures_dir)
10. log "GATE: PASS/FAIL (KL_all={}, Wilcoxon_count={}/3)"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | load_config + setup_logging + save_results | YAML load, logging setup, JSON persistence |
| L-9-2 | main() | Full pipeline orchestration with precondition check |

---

## A-10: Unit Tests [Complexity: 3, Budget: 3]

Applied: Standard scipy.stats statistical analysis pipeline

### API Signatures

```python
# tests/test_config.py
def test_load_config_defaults() -> None: ...
def test_load_config_from_yaml(tmp_path) -> None: ...

# tests/test_data.py
def test_load_h_e1_scores_missing_file(tmp_path) -> None: ...
def test_load_h_e1_scores_shape(tmp_path) -> None: ...
def test_load_task_data_n_mismatch() -> None: ...

# tests/test_analyze.py
def test_compute_cohens_d_known_values() -> None: ...
def test_analyze_nli_distribution_uniform_input() -> None: ...
def test_analyze_nli_distribution_nonuniform_input() -> None: ...
def test_evaluate_gate_pass() -> None: ...
def test_evaluate_gate_fail_kl() -> None: ...
def test_evaluate_gate_fail_wilcoxon() -> None: ...

# tests/test_run_experiment.py
def test_main_missing_h_e1_results(tmp_path, monkeypatch) -> None: ...
def test_save_results_creates_files(tmp_path) -> None: ...
```

### Pseudo-code: key test cases

```
test_analyze_nli_distribution_uniform_input:
    scores = np.tile([1/3, 1/3, 1/3], (200, 1))  # all uniform → KL near 0
    labels = np.array([0,1]*100)
    result = analyze_nli_distribution(scores, labels, "test", cfg)
    assert result.kl_passes == False
    assert result.p_near_uniform > 0.95

test_analyze_nli_distribution_nonuniform_input:
    # Hallucinated: high P(contra); correct: low P(contra)
    scores_hal = np.column_stack([np.random.uniform(0.6,0.9,100), ...])
    scores_cor = np.column_stack([np.random.uniform(0.0,0.2,100), ...])
    scores = np.vstack([scores_cor, scores_hal])
    labels = np.array([0]*100 + [1]*100)
    result = analyze_nli_distribution(scores, labels, "test", cfg)
    assert result.kl_passes == True
    assert result.wilcoxon_passes == True

test_evaluate_gate_pass:
    results = [make_task_result(kl_passes=True, wilcoxon_passes=True) for _ in range(3)]
    gate = evaluate_gate(results, cfg)
    assert gate.gate_pass == True
    assert gate.kl_all_pass == True
    assert gate.wilcoxon_pass_count == 3

test_main_missing_h_e1_results:
    monkeypatch cfg.h_e1_results_path = "/nonexistent/path.json"
    with pytest.raises(SystemExit):
        main()
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-10-1 | test_config + test_data | Config load tests; data loading with FileNotFoundError and shape checks |
| L-10-2 | test_analyze | Cohen's d known values; uniform/nonuniform distribution inputs; gate pass/fail cases |
| L-10-3 | test_run_experiment | main() missing file exit; save_results file creation |

---

## Array Shape Reference

| Variable | Shape | Note |
|----------|-------|------|
| scores_nxt3 | (N, 3) | N=20000, [P(contra), P(neutral), P(entail)] |
| labels_n | (N,) | binary {0,1}, balanced 50/50 |
| class_means | (3,) | per-class mean across N |
| uniform | (3,) | [1/3, 1/3, 1/3] |
| contra_scores | (N,) | scores_nxt3[:, 0] |
| hal_scores | (~N/2,) | contra_scores[labels==1] |
| near_uniform_mask | (N,) | bool array |
