# Logic: H-E1 — Locality Score Oracle Existence Proof

**Generated:** 2026-05-20
**Hypothesis:** h-e1 (EXISTENCE / PoC)
**Phase:** 3 - Logic Design

Applied: Standard PyTorch (no domain-specific DPO / theorem-proving patterns found in Archon KB)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field experiment — no local codebase. Serena analysis skipped.
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation. Architecture derived from Phase 2C experiment brief and reference repositories: ByteDance-Seed/BFS-Prover-V2, lean-dojo/LeanDojo-v2, eric-mitchell/direct-preference-optimization.

---

## A-1: Config & Data Pipeline [Complexity: 10, Budget: 1]

Applied: Standard PyTorch dataclass pattern

### API Signatures

```python
# config.py
from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class ExperimentConfig:
    """Experiment-wide configuration for H-E1."""
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
    adam_betas: Tuple[float, float] = (0.9, 0.999)

    # Hard subset
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

```python
# data/load_datasets.py
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Problem:
    """Single theorem-proving problem."""
    name: str
    split: str
    formal_statement: str
    goal: str
    header: str
    dataset: str  # "minif2f" | "vericoding"

def load_minif2f() -> List[Problem]:
    """Load all miniF2F problems from HuggingFace Tonic/MiniF2F."""
    ...

def load_vericoding(data_path: str) -> List[Problem]:
    """Load Lean4-compatible Vericoding problems from local path."""
    ...

def run_cold_start_sft_evaluation(
    problems: List[Problem],
    model_id: str,
    rollouts: int = 16
) -> Dict[str, float]:
    """Run BFS-Prover SFT in inference mode; returns problem_name -> pass@1.
    # pass@1 scores: Dict values in [0.0, 1.0], len == len(problems)
    """
    ...

def construct_hard_subset(
    problems: List[Problem],
    pass_at_1_scores: Dict[str, float],
    threshold: float = 0.20
) -> List[Problem]:
    """Return problems where pass@1 < threshold."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| pass@1 array (if batched) | `[N_problems]` | float32, values in [0,1] |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Config + DataLoader | ExperimentConfig dataclass + 4 load/eval functions |

---

## A-2: LeanDojo Tracing [Complexity: 15, Budget: 1]

Applied: Standard Python dataclass + dictionary pattern

### API Signatures

```python
# data/leandojo_tracing.py
from dataclasses import dataclass
from typing import List, Optional, Dict

# Pre-specified before any training — IMMUTABLE (NFR-4)
TACTIC_TAXONOMY: Dict[str, List[str]] = {
    "type_error": ["type mismatch", "application type mismatch"],
    "undefined_name": ["unknown identifier", "unknown tactic"],
    "tactic_failure": ["tactic failed", "simp made no progress"],
}

@dataclass
class ProofStateTriple:
    """LeanDojo (state, tactic, compiler_error) triple with alignment ID."""
    state_id: str          # LeanDojo state ID for alignment verification
    state: str             # Proof state string
    tactic: str            # Attempted tactic
    compiler_error: Optional[str]    # Raw Lean4 error message, or None if tactic succeeded
    error_category: Optional[str]    # Key from TACTIC_TAXONOMY, or None
    problem_name: str

def trace_repository(repo_url: str, commit: str) -> None:
    """Trace Lean4 repo using LeanGitRepo + trace(); cache results to disk."""
    ...

def extract_state_triples(
    problems: List[Problem],
    timeout: int = 60
) -> List[ProofStateTriple]:
    """Run Dojo context manager per problem; extract all (state, tactic, error) triples."""
    ...

def classify_lean4_error(error_msg: str) -> Optional[str]:
    """Match error_msg against TACTIC_TAXONOMY entries; return category key or None."""
    ...

def get_premise_consistent_tokens(
    error_category: str,
    tokenizer  # PreTrainedTokenizer
) -> List[int]:
    """Return token IDs for tactics addressing the given error_category."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | LeanDojo Tracing | trace_repository + extract_state_triples + classify + token mapping |

---

## A-3: DPO Pair Construction [Complexity: 12, Budget: 1]

Applied: Standard Python dataclass with permutation logic

### API Signatures

```python
# training/dpo_pairs.py
from dataclasses import dataclass
from typing import List, Dict, Literal

Condition = Literal["A", "B", "P"]

@dataclass
class DPOPair:
    """Single DPO training pair with full metadata."""
    state_id_chosen: str       # Must equal state_id_rejected (NFR-3)
    state_id_rejected: str
    state: str
    chosen_tactic: str
    rejected_tactic: str
    error_msg: str             # Raw Lean4 error (permuted for Condition P)
    error_category: str        # From TACTIC_TAXONOMY
    condition: Condition

def build_pairs_condition_A(
    triples: List[ProofStateTriple]
) -> List[DPOPair]:
    """Build pairs: rejected=error-triggering tactic, chosen=correct advancing tactic.
    Same proof state s for both; error_msg from LeanDojo compiler output.
    """
    ...

def build_pairs_condition_B(
    triples: List[ProofStateTriple]
) -> List[DPOPair]:
    """Build pairs: rejected=failed-branch tactic (no error info), chosen=correct tactic.
    Same proof state s; error_msg field left as empty string.
    """
    ...

def build_pairs_condition_P(
    triples: List[ProofStateTriple]
) -> List[DPOPair]:
    """Build pairs: rejected tactic with shuffled/permuted error message tokens.
    Same proof state s; error_msg is a random permutation within the batch.
    """
    ...

def validate_state_alignment(pairs: List[DPOPair]) -> None:
    """Assert state_id_chosen == state_id_rejected for all pairs.
    Raises ValueError immediately on first violation (NFR-3 — abort, not warn).
    """
    ...

def build_all_conditions(
    triples: List[ProofStateTriple]
) -> Dict[Condition, List[DPOPair]]:
    """Build and validate all three condition pair sets."""
    ...
```

### Pseudo-code: Condition P Permutation Logic

```
def build_pairs_condition_P(triples):
    # 1. Build base pairs same as Condition A (same state, chosen, rejected)
    base_pairs = build_pairs_condition_A(triples)
    # 2. Collect all error_msg strings in batch
    all_error_msgs = [p.error_msg for p in base_pairs]
    # 3. Random shuffle of error_msgs across batch (fixed seed for reproducibility)
    shuffled_msgs = random.sample(all_error_msgs, len(all_error_msgs))
    # 4. Assign shuffled error_msg to each pair (ensures mismatch between
    #    the actual error and the error message used as DPO negative signal)
    for pair, shuffled_msg in zip(base_pairs, shuffled_msgs):
        pair.error_msg = shuffled_msg
        pair.condition = "P"
    return base_pairs
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | DPO Pairs | 3 build functions + validate + build_all_conditions |

---

## A-4: DPO Training Loop [Complexity: 16, Budget: 2]

Applied: Standard PyTorch DPO loss (eric-mitchell/direct-preference-optimization pattern)

### API Signatures

```python
# training/dpo_trainer.py
import torch
import torch.nn.functional as F
from transformers import PreTrainedModel, PreTrainedTokenizer
from typing import Tuple, Dict

def load_model_and_tokenizer(
    model_id: str,
    dtype: torch.dtype = torch.bfloat16
) -> Tuple[PreTrainedModel, PreTrainedTokenizer]:
    """Load BFS-Prover-V2-7B with device_map='auto' and bfloat16."""
    ...

def get_batch_logps(
    logits: torch.Tensor,   # [B, T, V]
    labels: torch.Tensor,   # [B, T]
    average_log_prob: bool = False
) -> torch.Tensor:          # [B]
    """Compute per-sequence log-probabilities by summing (not averaging) token log-probs.
    Masks padding tokens (label == -100). average_log_prob=False per FR-4.2.
    # logits: [B, T, V], log_softmax -> [B, T, V]
    # gathered: [B, T], masked sum -> [B]
    """
    ...

def dpo_loss(
    policy_chosen_logps: torch.Tensor,    # [B]
    policy_rejected_logps: torch.Tensor,  # [B]
    ref_chosen_logps: torch.Tensor,       # [B]
    ref_rejected_logps: torch.Tensor,     # [B]
    beta: float = 10.0
) -> torch.Tensor:  # scalar
    """DPO loss: -logsigmoid(beta * (pi_logratios - ref_logratios)).mean()
    pi_logratios  = policy_chosen_logps - policy_rejected_logps   # [B]
    ref_logratios = ref_chosen_logps - ref_rejected_logps          # [B]
    loss = -F.logsigmoid(beta * (pi_logratios - ref_logratios)).mean()  # scalar
    """
    ...

def train_dpo_condition(
    condition: str,
    pairs: List[DPOPair],
    config: "ExperimentConfig",
    ref_model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer
) -> PreTrainedModel:
    """Train 1-epoch DPO from BFS-Prover-V2-7B; save checkpoint to config.checkpoint_dir/condition.
    Monitors loss stability: if final_loss > 2 * initial_loss, reduces LR/beta and retries.
    """
    ...

def run_all_dpo_conditions(
    all_pairs: Dict[str, List[DPOPair]],
    config: "ExperimentConfig"
) -> Dict[str, PreTrainedModel]:
    """Train conditions A, B, P sequentially; returns {"A": model_A, "B": model_B, "P": model_P}."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| logits | `[B, T, V]` | B=batch, T=seq_len, V=vocab_size (~32000) |
| labels | `[B, T]` | -100 for padding/prompt tokens |
| log_probs | `[B, T, V]` | F.log_softmax(logits, dim=-1) |
| gathered | `[B, T]` | log_probs at label positions |
| logps | `[B]` | sum over T dimension |
| pi_logratios | `[B]` | chosen_logps - rejected_logps |
| loss | scalar | mean over batch |

### Pseudo-code: get_batch_logps

```
def get_batch_logps(logits, labels, average_log_prob=False):
    # logits: [B, T, V], labels: [B, T]
    log_probs = F.log_softmax(logits[:, :-1, :], dim=-1)  # [B, T-1, V]
    labels = labels[:, 1:].clone()                         # [B, T-1], shift right
    mask = (labels != -100)                                # [B, T-1]
    labels[~mask] = 0                                      # avoid index error
    per_token_logps = log_probs.gather(2, labels.unsqueeze(2)).squeeze(2)  # [B, T-1]
    per_token_logps = per_token_logps * mask               # zero out padding
    if average_log_prob:
        return per_token_logps.sum(-1) / mask.sum(-1)      # [B]
    return per_token_logps.sum(-1)                         # [B]
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | DPO Loss Core | load_model_and_tokenizer + get_batch_logps + dpo_loss |
| L-4-2 | DPO Training | train_dpo_condition + run_all_dpo_conditions + stability check |

---

## A-5: Locality Score Computation [Complexity: 14, Budget: 1]

Applied: Standard PyTorch inference pattern

### API Signatures

```python
# evaluation/locality_score.py
import torch
from typing import List, Dict

def compute_locality_score(
    model_pre: "PreTrainedModel",
    model_post: "PreTrainedModel",
    proof_states: List[ProofStateTriple],
    tokenizer: "PreTrainedTokenizer",
    premise_consistent_tokens: Dict[str, List[int]]  # category -> token IDs
) -> float:
    """Compute LS = numerator / denominator over all proof states.
    # logits_pre:  [1, T, V] per state
    # logits_post: [1, T, V] per state
    # probs_pre:   [1, T, V] — softmax(logits_pre)
    # probs_post:  [1, T, V] — softmax(logits_post)
    # delta:       [1, T, V] — probs_post - probs_pre
    Returns single LS float.
    """
    ...

def compute_all_locality_scores(
    ref_model: "PreTrainedModel",
    condition_models: Dict[str, "PreTrainedModel"],  # {"A": ..., "B": ..., "P": ...}
    proof_states: List[ProofStateTriple],
    tokenizer: "PreTrainedTokenizer",
    taxonomy_tokens: Dict[str, List[int]]            # category -> token IDs
) -> Dict[str, List[float]]:
    """Compute LS per state for each condition. Returns {"A": [ls_s0, ls_s1, ...], ...}."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| logits_pre / logits_post | `[1, T, V]` | single state, T=state token length |
| probs_pre / probs_post | `[1, T, V]` | softmax over V |
| delta | `[1, T, V]` | element-wise difference |
| pc_mass_pre/post | scalar | sum of probs over premise_consistent_tokens at next-token position |
| total_mass_shift | scalar | sum of abs(delta) over all tokens at next-token position |

### Pseudo-code: Locality Score Formula

```
def compute_locality_score(model_pre, model_post, proof_states, tokenizer, pc_tokens):
    numerator = 0.0
    denominator = 0.0

    for state_triple in proof_states:
        # tokenize state context
        inputs = tokenizer(state_triple.state, return_tensors="pt").to(device)

        with torch.no_grad():
            logits_pre  = model_pre(**inputs).logits    # [1, T, V]
            logits_post = model_post(**inputs).logits   # [1, T, V]

        # next-token prediction position (last token)
        probs_pre  = softmax(logits_pre[:, -1, :],  dim=-1)  # [1, V]
        probs_post = softmax(logits_post[:, -1, :], dim=-1)  # [1, V]
        delta      = probs_post - probs_pre                   # [1, V]

        # premise-consistent token indices for this state's error_category
        pc_idx = pc_tokens.get(state_triple.error_category, [])

        # numerator: mass shift onto premise-consistent tokens
        numerator   += delta[:, pc_idx].sum().item()

        # denominator: total absolute mass shift over all tokens
        denominator += delta.abs().sum().item()

    return numerator / (denominator + 1e-9)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Locality Score | compute_locality_score + compute_all_locality_scores |

---

## A-6: Statistical Testing & Gate [Complexity: 9, Budget: 1]

Applied: Standard scipy.stats pattern

### API Signatures

```python
# evaluation/statistical_tests.py
from dataclasses import dataclass
from typing import Dict, List
import numpy as np
from scipy import stats

@dataclass
class GateResult:
    """Gate evaluation output for H-E1."""
    condition_a_mean: float
    condition_b_mean: float
    condition_p_mean: float
    t_stat: float
    p_value: float
    gate_pass: bool        # LS_A > LS_P AND p < 0.05
    secondary_pass: bool   # LS_A > LS_B (informational)

def one_sided_ttest_ls_a_gt_p(
    ls_scores_a: List[float],
    ls_scores_p: List[float],
    alpha: float = 0.05
) -> GateResult:
    """One-sided t-test H0: LS_A - LS_P <= 0.
    Uses scipy.stats.ttest_1samp(np.array(ls_a) - np.array(ls_p), 0, alternative='greater').
    """
    ...

def evaluate_gate(
    ls_by_condition: Dict[str, List[float]],  # {"A": [...], "B": [...], "P": [...]}
    dataset_name: str
) -> GateResult:
    """Compute GateResult for a given dataset's LS scores."""
    ...

def log_gate_result(result: GateResult, dataset_name: str) -> None:
    """Print gate results in required format.
    Format:
      [H-E1] Locality Score — Condition A: {:.4f} | Condition B: {:.4f} | Condition P: {:.4f}
      [H-E1] Gate Check: LS_A > LS_P = {bool} (p={:.4f})
    """
    ...

def write_results_json(
    results: dict,
    output_path: str
) -> None:
    """Serialize all LS scores, gate results, and metadata to JSON."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Stats + Gate | GateResult dataclass + ttest + evaluate_gate + log + write_json |

---

## A-7: Visualizer + ExperimentRunner [Complexity: 10, Budget: 1]

Applied: Standard matplotlib + orchestration pattern

### API Signatures

```python
# visualization/plots.py
from typing import Dict, List

def plot_locality_score_comparison(
    ls_by_condition_minif2f: Dict[str, List[float]],    # {"A": [...], "B": [...], "P": [...]}
    ls_by_condition_vericoding: Dict[str, List[float]],
    output_path: str = "h-e1/figures/locality_score_comparison.png"
) -> None:
    """Bar chart: 2 datasets x 3 conditions = 6 bars. Primary required figure."""
    ...

def plot_probability_mass_distribution(
    mass_shifts: Dict[str, Dict[str, float]],  # condition -> category -> delta_mass
    taxonomy: Dict[str, List[str]],
    output_path: str
) -> None:
    """Stacked bar: tactic category delta (P_post - P_pre) per condition x dataset."""
    ...

def plot_error_category_breakdown(
    ls_per_category: Dict[str, Dict[str, float]],  # condition -> category -> mean_LS
    output_path: str
) -> None:
    """Grouped bar chart: LS per TACTIC_TAXONOMY category per condition."""
    ...

def plot_locality_score_per_state(
    ls_per_state: Dict[str, List[float]],   # condition -> [ls per state]
    proof_state_complexities: List[float],  # complexity proxy (e.g., state string length)
    output_path: str
) -> None:
    """Scatter: x=proof state complexity, y=LS per state, color-coded by condition."""
    ...

def generate_all_figures(
    results: dict,
    config: "ExperimentConfig"
) -> None:
    """Call all 4 plot functions; save to config.figures_dir."""
    ...
```

```python
# run_experiment.py
def main(config: "ExperimentConfig") -> None:
    """Full H-E1 experiment orchestration."""
    ...
```

### Pseudo-code: main() 10-step orchestration

```
def main(config):
    set_seed(config.seed)
    set CUDA_VISIBLE_DEVICES to selected GPU

    # Step 1: Load datasets
    minif2f_problems   = load_minif2f()
    vericoding_problems = load_vericoding(data_path=config.vericoding_path)

    # Step 2: Hard subset selection
    minif2f_scores   = run_cold_start_sft_evaluation(minif2f_problems,   config.model_id, config.cold_start_rollouts)
    vericoding_scores = run_cold_start_sft_evaluation(vericoding_problems, config.model_id, config.cold_start_rollouts)
    minif2f_hard   = construct_hard_subset(minif2f_problems,   minif2f_scores,   config.pass_at_1_threshold)
    vericoding_hard = construct_hard_subset(vericoding_problems, vericoding_scores, config.pass_at_1_threshold)

    # Step 3: LeanDojo tracing
    trace_repository(repo_url=LEAN4_REPO_URL, commit=LEAN4_COMMIT)
    triples_minif2f   = extract_state_triples(minif2f_hard)
    triples_vericoding = extract_state_triples(vericoding_hard)

    # Step 4: DPO pair construction + validation
    all_pairs_minif2f   = build_all_conditions(triples_minif2f)
    all_pairs_vericoding = build_all_conditions(triples_vericoding)
    for cond_pairs in all_pairs_minif2f.values():
        validate_state_alignment(cond_pairs)
    for cond_pairs in all_pairs_vericoding.values():
        validate_state_alignment(cond_pairs)

    # Step 5: Load reference model + tokenizer
    ref_model, tokenizer = load_model_and_tokenizer(config.model_id, torch.bfloat16)
    ref_model.eval()
    for param in ref_model.parameters(): param.requires_grad = False

    # Step 6: Train 3 DPO conditions (on combined pairs from both datasets)
    all_pairs_combined = merge_pairs(all_pairs_minif2f, all_pairs_vericoding)
    condition_models = run_all_dpo_conditions(all_pairs_combined, config)

    # Step 7: Compute locality scores per dataset
    taxonomy_tokens = {cat: get_premise_consistent_tokens(cat, tokenizer) for cat in TACTIC_TAXONOMY}
    ls_minif2f   = compute_all_locality_scores(ref_model, condition_models, triples_minif2f,   tokenizer, taxonomy_tokens)
    ls_vericoding = compute_all_locality_scores(ref_model, condition_models, triples_vericoding, tokenizer, taxonomy_tokens)

    # Step 8: Gate evaluation + logging
    gate_minif2f   = evaluate_gate(ls_minif2f,   "miniF2F")
    gate_vericoding = evaluate_gate(ls_vericoding, "Vericoding")
    log_gate_result(gate_minif2f,   "miniF2F")
    log_gate_result(gate_vericoding, "Vericoding")

    # Step 9: Generate figures
    results = {"ls_minif2f": ls_minif2f, "ls_vericoding": ls_vericoding,
               "gate_minif2f": gate_minif2f, "gate_vericoding": gate_vericoding}
    generate_all_figures(results, config)

    # Step 10: Write results JSON + 04_validation.md
    write_results_json(results, os.path.join(config.output_dir, "results.json"))
    write_validation_md(gate_minif2f, gate_vericoding, config.output_dir)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Viz + Runner | 4 plot functions + generate_all_figures + main() orchestration |

---

## Summary: Subtask Budget

| Task | Budget Used | Subtasks |
|------|-------------|----------|
| A-1: Config & Data | 1 | L-1-1 |
| A-2: LeanDojo Tracing | 1 | L-2-1 |
| A-3: DPO Pairs | 1 | L-3-1 |
| A-4: DPO Training | 2 | L-4-1, L-4-2 |
| A-5: Locality Score | 1 | L-5-1 |
| A-6: Statistical Tests | 1 | L-6-1 |
| A-7: Viz + Runner | 1 | L-7-1 |
| **Total** | **8/8** | |

---

## Critical Notes for Phase 4 Coder

1. `TACTIC_TAXONOMY` defined in `leandojo_tracing.py` BEFORE any training — never modify after definition (NFR-4)
2. `validate_state_alignment()` calls `raise ValueError(...)` — never `warnings.warn()`
3. Each DPO run loads a fresh BFS-Prover-V2-7B as both policy init and frozen ref
4. `average_log_prob=False` in `get_batch_logps` — sum, not average log-probs
5. `set CUDA_VISIBLE_DEVICES` before any Python invocation; single GPU only
6. Gate log format (exact):
   ```
   [H-E1] Locality Score — Condition A: {:.4f} | Condition B: {:.4f} | Condition P: {:.4f}
   [H-E1] Gate Check: LS_A > LS_P = {bool} (p={:.4f})
   ```
7. DPO loss stability check: if `final_loss > 2 * initial_loss` at epoch end, reduce LR/beta and retry
8. LS denominator guarded with `+ 1e-9` to prevent division by zero
