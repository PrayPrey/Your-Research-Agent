# Architecture: H-E1 — Locality Score Oracle Existence Proof

**Generated:** 2026-05-20  
**Hypothesis:** h-e1 (EXISTENCE / MUST_WORK)  
**Tier:** LIGHT (single GPU, minimal infrastructure)

Applied: Green-field experiment — no matching Archon KB patterns for theorem proving DPO domain

---

## Codebase Analysis (Serena)

Green-field experiment — no existing local codebase to analyze.  
Serena analysis skipped. Architecture derived from Phase 2C experiment brief and reference repositories:
- ByteDance-Seed/BFS-Prover-V2 (BFS + DPO infrastructure)
- lean-dojo/LeanDojo-v2 (proof state extraction)
- eric-mitchell/direct-preference-optimization (DPO loss)

---

## File Structure

```
h-e1/
  code/
    data/
      load_datasets.py
      leandojo_tracing.py
    training/
      dpo_pairs.py
      dpo_trainer.py
    evaluation/
      locality_score.py
      statistical_tests.py
    visualization/
      plots.py
    run_experiment.py
    config.py
  figures/
  results/
```

---

## Module Definitions

### ExperimentConfig (`code/config.py`)

**Dependencies**: None

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class ExperimentConfig:
    # Model
    model_id: str = "ByteDance-Seed/BFS-Prover-V2-7B"
    dtype: str = "bfloat16"

    # Training
    beta: float = 10.0
    lr_start: float = 5e-6
    lr_end: float = 5e-7
    batch_size: int = 16
    grad_accum_steps: int = 1
    num_epochs: int = 1
    seed: int = 1
    weight_decay: float = 0.01
    adam_betas: tuple = (0.9, 0.999)

    # Hard subset threshold
    pass_at_1_threshold: float = 0.20
    cold_start_rollouts: int = 16

    # DPO conditions
    conditions: List[str] = field(default_factory=lambda: ["A", "B", "P"])

    # Gate
    gate_alpha: float = 0.05

    # Paths
    output_dir: str = "h-e1/results"
    figures_dir: str = "h-e1/figures"
    checkpoint_dir: str = "h-e1/checkpoints"
```

---

### DatasetLoader (`code/data/load_datasets.py`)

**Dependencies**: ExperimentConfig

```python
from datasets import Dataset
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Problem:
    name: str
    split: str
    formal_statement: str
    goal: str
    header: str
    dataset: str  # "minif2f" | "vericoding"

def load_minif2f() -> List[Problem]: ...
def load_vericoding(data_path: str) -> List[Problem]: ...
def run_cold_start_sft_evaluation(
    problems: List[Problem],
    model_id: str,
    rollouts: int = 16
) -> Dict[str, float]: ...   # problem_name -> pass@1
def construct_hard_subset(
    problems: List[Problem],
    pass_at_1_scores: Dict[str, float],
    threshold: float = 0.20
) -> List[Problem]: ...
```

---

### LeanDojoTracer (`code/data/leandojo_tracing.py`)

**Dependencies**: DatasetLoader

```python
from dataclasses import dataclass
from typing import List, Optional

TACTIC_TAXONOMY = {
    "type_error": ["type mismatch", "application type mismatch"],
    "undefined_name": ["unknown identifier", "unknown tactic"],
    "tactic_failure": ["tactic failed", "simp made no progress"],
}

@dataclass
class ProofStateTriple:
    state_id: str
    state: str
    tactic: str
    compiler_error: Optional[str]
    error_category: Optional[str]  # key from TACTIC_TAXONOMY
    problem_name: str

def trace_repository(repo_url: str, commit: str) -> None: ...
def extract_state_triples(
    problems: list,
    timeout: int = 60
) -> List[ProofStateTriple]: ...
def classify_lean4_error(error_msg: str) -> Optional[str]: ...
def get_premise_consistent_tokens(
    error_category: str,
    tokenizer
) -> List[int]: ...
```

---

### DPOPairBuilder (`code/training/dpo_pairs.py`)

**Dependencies**: LeanDojoTracer, ExperimentConfig

```python
from dataclasses import dataclass
from typing import List, Literal

Condition = Literal["A", "B", "P"]

@dataclass
class DPOPair:
    state_id_chosen: str
    state_id_rejected: str
    state: str
    chosen_tactic: str
    rejected_tactic: str
    error_msg: str
    error_category: str
    condition: Condition

def build_pairs_condition_A(triples: list) -> List[DPOPair]: ...
def build_pairs_condition_B(triples: list) -> List[DPOPair]: ...
def build_pairs_condition_P(triples: list) -> List[DPOPair]: ...
def validate_state_alignment(pairs: List[DPOPair]) -> None: ...
    # Asserts state_id_chosen == state_id_rejected for each pair; aborts on violation
def build_all_conditions(triples: list) -> dict[Condition, List[DPOPair]]: ...
```

---

### DPOTrainer (`code/training/dpo_trainer.py`)

**Dependencies**: DPOPairBuilder, ExperimentConfig

```python
import torch
import torch.nn.functional as F
from transformers import PreTrainedModel, PreTrainedTokenizer
from typing import List

def load_model_and_tokenizer(
    model_id: str,
    dtype: torch.dtype = torch.bfloat16
) -> tuple[PreTrainedModel, PreTrainedTokenizer]: ...

def get_batch_logps(
    logits: torch.Tensor,
    labels: torch.Tensor,
    average_log_prob: bool = False
) -> torch.Tensor: ...

def dpo_loss(
    policy_chosen_logps: torch.Tensor,
    policy_rejected_logps: torch.Tensor,
    ref_chosen_logps: torch.Tensor,
    ref_rejected_logps: torch.Tensor,
    beta: float = 10.0
) -> torch.Tensor: ...

def train_dpo_condition(
    condition: str,
    pairs: list,
    config: "ExperimentConfig",
    ref_model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer
) -> PreTrainedModel: ...
    # Saves checkpoint to config.checkpoint_dir / condition

def run_all_dpo_conditions(
    all_pairs: dict,
    config: "ExperimentConfig"
) -> dict[str, PreTrainedModel]: ...
    # Returns {"A": model_A, "B": model_B, "P": model_P}
```

---

### LocalityScoreEvaluator (`code/evaluation/locality_score.py`)

**Dependencies**: DPOTrainer, LeanDojoTracer, ExperimentConfig

```python
import torch
from typing import List

def compute_locality_score(
    model_pre,
    model_post,
    proof_states: List["ProofStateTriple"],
    tokenizer,
    premise_consistent_tokens: dict
) -> float: ...
    # Returns LS = sum_s[P_post(pc|s) - P_pre(pc|s)] / sum_s[sum_t|P_post(t|s) - P_pre(t|s)|]

def compute_all_locality_scores(
    ref_model,
    condition_models: dict,
    proof_states: list,
    tokenizer,
    taxonomy_tokens: dict
) -> dict[str, list[float]]: ...
    # Returns {"A": [ls_per_state...], "B": [...], "P": [...]} for each dataset
```

---

### StatisticalTests (`code/evaluation/statistical_tests.py`)

**Dependencies**: LocalityScoreEvaluator

```python
from dataclasses import dataclass
from typing import Optional
import numpy as np

@dataclass
class GateResult:
    condition_a_mean: float
    condition_b_mean: float
    condition_p_mean: float
    t_stat: float
    p_value: float
    gate_pass: bool  # LS_A > LS_P and p < 0.05
    secondary_pass: bool  # LS_A > LS_B

def one_sided_ttest_ls_a_gt_p(
    ls_scores_a: list,
    ls_scores_p: list,
    alpha: float = 0.05
) -> GateResult: ...

def evaluate_gate(
    ls_by_condition: dict,
    dataset_name: str
) -> GateResult: ...

def log_gate_result(result: GateResult, dataset_name: str) -> None: ...
    # Prints: [H-E1] Locality Score — Condition A: ... | ...
    # Prints: [H-E1] Gate Check: LS_A > LS_P = ... (p=...)

def write_results_json(
    results: dict,
    output_path: str
) -> None: ...
```

---

### Visualizer (`code/visualization/plots.py`)

**Dependencies**: StatisticalTests

```python
def plot_locality_score_comparison(
    ls_by_condition_minif2f: dict,
    ls_by_condition_vericoding: dict,
    output_path: str = "h-e1/figures/locality_score_comparison.png"
) -> None: ...
    # 2 datasets × 3 conditions = 6 bars

def plot_probability_mass_distribution(
    mass_shifts: dict,
    taxonomy: dict,
    output_path: str
) -> None: ...
    # Stacked bar: tactic category Δ per condition × dataset

def plot_error_category_breakdown(
    ls_per_category: dict,
    output_path: str
) -> None: ...

def plot_locality_score_per_state(
    ls_per_state: dict,
    proof_state_complexities: list,
    output_path: str
) -> None: ...
    # Scatter: x=proof state complexity, y=LS

def generate_all_figures(results: dict, config: "ExperimentConfig") -> None: ...
```

---

### ExperimentRunner (`code/run_experiment.py`)

**Dependencies**: All modules

```python
def main(config: "ExperimentConfig") -> None: ...
    # Step 1: load_minif2f() + load_vericoding()
    # Step 2: run_cold_start_sft_evaluation() → construct_hard_subset()
    # Step 3: trace_repository() + extract_state_triples()
    # Step 4: build_all_conditions() + validate_state_alignment()
    # Step 5: load_model_and_tokenizer() (ref + 3 DPO)
    # Step 6: run_all_dpo_conditions()
    # Step 7: compute_all_locality_scores()
    # Step 8: evaluate_gate() per dataset + log_gate_result()
    # Step 9: generate_all_figures()
    # Step 10: write_results_json() + write 04_validation.md

if __name__ == "__main__":
    import argparse
    # parse --config path
    ...
```

---

## Module Dependency Graph

- `config.py` → (no deps)
- `data/load_datasets.py` → `config.py`
- `data/leandojo_tracing.py` → `load_datasets.py`
- `training/dpo_pairs.py` → `leandojo_tracing.py`, `config.py`
- `training/dpo_trainer.py` → `dpo_pairs.py`, `config.py`
- `evaluation/locality_score.py` → `dpo_trainer.py`, `leandojo_tracing.py`
- `evaluation/statistical_tests.py` → `locality_score.py`
- `visualization/plots.py` → `statistical_tests.py`
- `run_experiment.py` → all modules

---

## Epic Tasks

| ID | Task | Description | Files | Complexity | Breakdown |
|----|------|-------------|-------|------------|-----------|
| E1 | Config & Data Pipeline | ExperimentConfig + miniF2F/Vericoding loading + cold-start SFT hard subset construction | `config.py`, `data/load_datasets.py` | 10/20 | Module_Size:3 + Dependencies:2 + Algorithm:3 + Integration:2 |
| E2 | LeanDojo Tracing | LeanGitRepo tracing, Dojo context manager, (state, tactic, compiler_error) triple extraction, error classification, taxonomy token mapping | `data/leandojo_tracing.py` | 15/20 | Module_Size:4 + Dependencies:3 + Algorithm:4 + Integration:4 |
| E3 | DPO Pair Construction | Build A/B/P condition pairs, state alignment assertion (100%), permutation logic for condition P | `training/dpo_pairs.py` | 12/20 | Module_Size:3 + Dependencies:3 + Algorithm:3 + Integration:3 |
| E4 | DPO Training Loop | Load BFS-Prover-V2-7B, DPO loss (β=10), 3 independent runs, checkpoint save, loss stability check | `training/dpo_trainer.py` | 16/20 | Module_Size:4 + Dependencies:4 + Algorithm:4 + Integration:4 |
| E5 | Locality Score Computation | Post-DPO logit diff per proof state, premise-consistent token mass, LS formula, all 3 conditions × 2 datasets | `evaluation/locality_score.py` | 14/20 | Module_Size:4 + Dependencies:3 + Algorithm:4 + Integration:3 |
| E6 | Statistical Testing & Gate | One-sided t-test LS_A > LS_P, secondary LS_A > LS_B, gate pass/fail, results JSON, 04_validation.md | `evaluation/statistical_tests.py` | 9/20 | Module_Size:2 + Dependencies:2 + Algorithm:3 + Integration:2 |
| E7 | Visualization & Experiment Runner | 4 figure types, main orchestration script tying all steps end-to-end | `visualization/plots.py`, `run_experiment.py` | 10/20 | Module_Size:3 + Dependencies:3 + Algorithm:2 + Integration:2 |

**Distribution**: VeryHigh(18-20): [] | High(14-17): [E4, E2, E5] | Medium(9-13): [E3, E1, E7, E6] | Low(4-8): []

---

## External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `torch` | >=2.0.0 | Model forward pass, logit computation |
| `transformers` | >=4.40.0 | Load BFS-Prover-V2-7B, tokenizer |
| `datasets` | >=2.18.0 | `load_dataset("Tonic/MiniF2F")` |
| `lean-dojo` | >=2.0.0 | LeanGitRepo, trace, Dojo context |
| `scipy` | >=1.11.0 | `ttest_1samp(..., alternative='greater')` |
| `numpy` | >=1.24.0 | Array operations for LS computation |
| `matplotlib` | >=3.7.0 | All 4 figure types |
| `accelerate` | >=0.27.0 | GPU training, bfloat16 |
| `pyyaml` | >=6.0 | Config loading |

---

## Notes for Phase 4 Coder

1. TACTIC_TAXONOMY must be defined in `leandojo_tracing.py` BEFORE any DPO training begins (NFR-4)
2. `validate_state_alignment()` must ABORT (not warn) on any state ID mismatch
3. Each DPO run loads a fresh copy of `ByteDance-Seed/BFS-Prover-V2-7B` as both policy init and frozen ref
4. `average_log_prob=False` in `get_batch_logps` — sum log-probs, not average
5. Set `CUDA_VISIBLE_DEVICES` before any Python invocation; single GPU only
6. Gate log format: `[H-E1] Locality Score — Condition A: {:.4f} | Condition B: {:.4f} | Condition P: {:.4f}`
