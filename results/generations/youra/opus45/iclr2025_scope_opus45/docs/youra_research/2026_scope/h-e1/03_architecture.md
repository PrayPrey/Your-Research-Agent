# Architecture: H-E1 Spectral Memory Horizon Stability

**Hypothesis**: EXISTENCE PoC - CV(H_spec) < 0.3 across 1000 random sequences
**Type**: Measurement/Analysis (no training)
**Date**: 2026-03-27

Applied: EXISTENCE PoC minimal architecture pattern
Applied: PyTorch direct weight access pattern for fused-kernel models

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. H-E1 is the foundation hypothesis with no prior code base.

---

## File Structure

- `code/config.py` - fixed experiment configuration
- `code/model.py` - Mamba model loader + eigenvalue extractor
- `code/evaluate.py` - H_spec computation, CV calculation, visualization
- `code/run_experiment.py` - main entry point

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: none

```python
class ExperimentConfig:
    model_id: str = "state-spaces/mamba-1.4b"
    model_370m_id: str = "state-spaces/mamba-370m"
    tokenizer_id: str = "EleutherAI/gpt-neox-20b"
    num_samples: int = 1000
    seq_length: int = 512
    seed: int = 42
    cv_threshold: float = 0.3
    figures_dir: str = "figures"
    results_path: str = "results.yaml"
    device: str = "cuda"
    dtype: str = "float32"
```

---

### MambaProbe (`code/model.py`)

**Dependencies**: Config

```python
class MambaProbe:
    def __init__(self, config: ExperimentConfig): ...

    def load_model(self, model_id: str) -> None: ...
    # Loads MambaLMHeadModel.from_pretrained(model_id), moves to device

    def extract_layer_eigenvalues(self) -> list[torch.Tensor]: ...
    # Returns [A.abs() for each layer], A = exp(layer.mixer.A_log)

    def compute_h_spec(self, input_ids: torch.Tensor) -> float: ...
    # lambda_max = max over all layers; H_spec = -1/log(lambda_max)

    def unload(self) -> None: ...
```

---

### Evaluator (`code/evaluate.py`)

**Dependencies**: Config, MambaProbe

```python
def generate_random_sequences(config: ExperimentConfig) -> torch.Tensor: ...
# torch.randint(0, vocab_size, (num_samples, seq_length), generator=rng)

def measure_h_spec_distribution(
    probe: MambaProbe,
    sequences: torch.Tensor,
    config: ExperimentConfig,
) -> dict: ...
# Returns {h_spec_values, mean, std, cv, pass_gate}

def run_scale_crossvalidation(config: ExperimentConfig) -> dict: ...
# Loads mamba-370m, computes mean H_spec, returns {h_1.4b, h_370m}

def save_results(metrics: dict, config: ExperimentConfig) -> None: ...
# Writes results.yaml

def generate_figures(metrics: dict, config: ExperimentConfig) -> None: ...
# Saves: hspec_distribution.png, gate_metrics.png,
#        hspec_per_layer.png, eigenvalue_distribution.png,
#        scale_comparison.png (if crossval ran)
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: Config, MambaProbe, Evaluator

```python
def main() -> None: ...
# 1. Build ExperimentConfig
# 2. Generate random sequences
# 3. Load MambaProbe(mamba-1.4b)
# 4. measure_h_spec_distribution -> metrics
# 5. run_scale_crossvalidation (optional)
# 6. save_results, generate_figures
# 7. Print CV, PASS/FAIL gate verdict
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Config, dependencies, directory structure, figures/ dir | 5 | 1+1+1+2 |
| A-2 | Model Loader | MambaProbe: load Mamba-1.4B, expose A_log per layer, handle fused-kernel fallback | 12 | 3+2+4+3 |
| A-3 | Eigenvalue Extraction | extract_layer_eigenvalues, compute_h_spec: exp(A_log), lambda_max, H_spec formula | 10 | 2+2+4+2 |
| A-4 | CV Measurement Loop | generate_random_sequences, measure_h_spec_distribution over 1000 samples | 8 | 2+2+2+2 |
| A-5 | Visualization & Results | generate_figures (4-5 plots), save_results YAML, gate verdict reporting | 9 | 2+2+3+2 |
| A-6 | Cross-Validation | run_scale_crossvalidation on Mamba-370M, scale comparison figure | 7 | 2+2+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-5], Low(4-8): [A-1, A-4, A-6]

---

## Critical Implementation Notes

- A matrix access: `layer.mixer.A_log` - direct weight access (no hooks needed, A is input-independent)
- Fused kernel fallback: if attribute access fails, initialize with `use_fast_path=False`
- Numerical precision: cast A_log to float32 before exp() for stability
- H_spec guard: if lambda_max >= 1.0, log is non-negative, H_spec undefined - skip or clamp
- Memory: process sequences one-at-a-time in the CV loop to stay under 16GB
