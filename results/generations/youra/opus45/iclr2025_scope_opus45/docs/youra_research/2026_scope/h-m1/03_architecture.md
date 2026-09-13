# Architecture: H-M1 — SSM Eigenvalue Memory Horizon Empirical Validation

**Applied**: single-file PoC experiment pattern (no training, inference-only validation)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending H-E1)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/20260327_scope/h-e1/code/`
**Findings**: H-E1 has 4 files — `model.py` (MambaProbe class with load_model, extract_layer_A_log, compute_h_spec, get_per_layer_h_spec), `evaluate.py` (5 standalone functions), `config.py` (ExperimentConfig dataclass), `run_experiment.py` (entry point). MambaProbe handles all model/eigenvalue logic.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| MambaProbe | `from h_e1.model import MambaProbe` | `h-e1/code/model.py` (lines 21-129) |
| ExperimentConfig | `from h_e1.config import ExperimentConfig` | `h-e1/code/config.py` (lines 5-28) |

**Verified from**: `docs/youra_research/20260327_scope/h-e1/code/` (actual implementation)

**Note**: H-M1 will copy/extend MambaProbe rather than import cross-hypothesis. MambaProbe.compute_h_spec and MambaProbe.extract_layer_A_log are the key reused methods.

---

## File Structure

- `code/`
  - `config.py` — experiment configuration
  - `model.py` — MambaProbe (from H-E1) + PerplexityEvaluator
  - `evaluate.py` — WikiText-103 data loading + context-length sweep
  - `run_experiment.py` — entry point, orchestrates full pipeline
  - `figures/` — output figures directory

---

## Module Definitions

### ExperimentConfig (`code/config.py`)

**Dependencies**: none

```python
@dataclass
class ExperimentConfig:
    # Model
    model_id: str = "state-spaces/mamba-1.4b"
    tokenizer_id: str = "state-spaces/mamba-1.4b-hf"
    # Dataset
    dataset_name: str = "wikitext"
    dataset_config: str = "wikitext-103-raw-v1"
    num_eval_sequences: int = 1000
    max_seq_length: int = 1024
    seed: int = 42
    # H_spec (from H-E1 validated result)
    h_spec_known: float = 256.18
    context_length_multipliers: list = (0.1, 0.25, 0.5, 1.0, 2.0, 4.0)
    # Gate
    degradation_ratio_threshold: float = 1.1
    baseline_ppl_expected: float = 16.3
    baseline_ppl_tolerance: float = 0.2
    # Hardware
    device: str = "cuda"
    dtype: str = "float32"
    # Output
    figures_dir: str = "figures"
    results_path: str = "results.yaml"
```

---

### MambaProbe + PerplexityEvaluator (`code/model.py`)

**Dependencies**: ExperimentConfig, torch, mamba_ssm

```python
class MambaProbe:
    """Reused from H-E1. Eigenvalue extraction from Mamba-1.4B."""
    def __init__(self, config: ExperimentConfig): ...
    def load_model(self) -> None: ...
    def extract_layer_A_log(self) -> dict[str, Tensor]: ...
    def compute_h_spec(self) -> dict[str, float]: ...
    def get_per_layer_h_spec(self) -> list[float]: ...
    def get_per_layer_lambda_max(self) -> list[float]: ...
    def unload(self) -> None: ...

class PerplexityEvaluator:
    """Measures perplexity at varying context lengths using a loaded Mamba model."""
    def __init__(self, model, tokenizer, device: str, dtype: str): ...
    def compute_perplexity(self, input_ids: Tensor) -> float: ...
    def evaluate_at_context_length(
        self, sequences: Tensor, context_length: int
    ) -> float: ...
    def run_context_sweep(
        self, sequences: Tensor, context_lengths: list[int]
    ) -> dict[int, float]: ...
    def compute_degradation_ratio(
        self, ppl_curve: dict[int, float], h_spec: float
    ) -> float: ...
```

---

### Data and Evaluation Functions (`code/evaluate.py`)

**Dependencies**: ExperimentConfig, torch, datasets, transformers

```python
def load_wikitext103(config: ExperimentConfig) -> Dataset: ...

def prepare_eval_sequences(
    dataset: Dataset,
    tokenizer,
    config: ExperimentConfig
) -> Tensor:
    """Returns Tensor of shape [num_eval_sequences, max_seq_length]."""
    ...

def compute_context_lengths(h_spec: float, multipliers: tuple, min_tokens: int = 16) -> list[int]: ...

def save_results(results: dict, path: str) -> None: ...

def generate_figures(
    ppl_curve: dict[int, float],
    h_spec: float,
    degradation_ratio: float,
    per_layer_h_specs: list[float],
    output_dir: str
) -> None:
    """Generates: (1) PPL vs context length curve, (2) gate metrics bar chart.
    Optional: (3) per-layer eigenvalue distribution, (4) decay rate profile."""
    ...
```

---

### Experiment Entry Point (`code/run_experiment.py`)

**Dependencies**: ExperimentConfig, MambaProbe, PerplexityEvaluator, evaluate.py functions

```python
def main(config: ExperimentConfig) -> dict: ...

if __name__ == "__main__":
    config = ExperimentConfig()
    results = main(config)
```

**Execution flow**:
1. Load WikiText-103 validation set, prepare 1000 eval sequences
2. Load Mamba-1.4B via MambaProbe; compute H_spec (verify ~256.18)
3. Run context sweep: PPL at [0.1×, 0.25×, 0.5×, 1×, 2×, 4×] H_spec
4. Compute degradation ratio; check gate (ratio > 1.1)
5. Save results YAML + generate figures

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup project structure | Create file skeleton, config.py with all params | 5 | 1+1+1+2 |
| A-2 | Dataset loading | Load WikiText-103, tokenize, chunk to 1000×1024 sequences | 8 | 2+2+2+2 |
| A-3 | Port MambaProbe from H-E1 | Copy and adapt MambaProbe class; verify H_spec ≈ 256.18 | 7 | 2+2+2+1 |
| A-4 | Implement PerplexityEvaluator | compute_perplexity, evaluate_at_context_length, run_context_sweep | 10 | 3+2+3+2 |
| A-5 | Implement degradation ratio | compute_degradation_ratio, gate check logic (ratio > 1.1) | 6 | 2+1+2+1 |
| A-6 | Run context sweep experiment | Wire full pipeline; run 6 context lengths × 1000 sequences | 10 | 2+3+3+2 |
| A-7 | Visualization | PPL vs context curve (H_spec line), gate metrics bar chart, optional per-layer plots | 9 | 2+1+3+3 |
| A-8 | Results saving and gate evaluation | YAML output with all metrics, PASS/FAIL determination | 6 | 1+1+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-6, A-7], Low(4-8): [A-1, A-2, A-3, A-5, A-8]
