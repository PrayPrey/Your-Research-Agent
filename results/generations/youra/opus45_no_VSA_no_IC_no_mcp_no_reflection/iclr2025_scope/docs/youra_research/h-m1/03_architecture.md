# Architecture Design: h-m1

**Version:** 1.0
**Date:** 2026-08-30
**Hypothesis:** h-m1 (MECHANISM)

Applied: Modular DL Experiment Pattern (Archon KB)
Applied: MOHAWK Stage-1 Matrix Alignment Pattern (Archon KB)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from base code (h-e1)
**Analyzed Path**: `h-e1/code/`
**Findings**: `duality_init_ssm_from_attention` (h-e1/code/duality_conversion.py) uses SVD-based conversion returning `(A, B, C, D, dt)` with shapes `A/C: [d_model, d_state]`, `B: [d_state, d_model]`, `D/dt: [d_model]` — this differs from the simplified pseudo-code in the PRD/brief. `selective_scan_ref` (h-e1/code/selective_scan.py) takes these exact shapes. Trust actual code: reuse both functions unmodified.

---

## Module Structure

```
h-m1/
├── code/
│   ├── __init__.py
│   ├── random_init.py           # NEW: random SSM baseline init
│   ├── reconstruction_error.py  # NEW: Frobenius norm metric + stats
│   ├── data_loader.py           # COPY from h-e1 (unchanged)
│   ├── run_experiment.py        # NEW: orchestration + figures
│   └── (import duality_conversion.py, selective_scan.py from h-e1)
├── configs/
│   └── experiment_config.yaml
├── figures/
└── results/
    └── comparison_results.json
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| duality_init_ssm_from_attention | `from duality_conversion import duality_init_ssm_from_attention` | `h-e1/code/duality_conversion.py` |
| selective_scan_ref | `from selective_scan import selective_scan_ref` | `h-e1/code/selective_scan.py` |
| load_wikitext_samples | `from data_loader import load_wikitext_samples` | `h-e1/code/data_loader.py` |

**Verified from**: `h-e1/code/` (actual implementation)

**Note**: Copy `duality_conversion.py`, `selective_scan.py`, `data_loader.py` into `h-m1/code/` unmodified (flat layout, matches h-e1 import style — no package relative imports used in base code).

---

## Module Definitions (New)

### random_init.py (`h-m1/code/random_init.py`)

**Dependencies**: torch

```python
def random_init_ssm(d_model: int, d_state: int = 64, seed: int = 42) -> Tuple[Tensor, Tensor, Tensor, Tensor, Tensor]:
    """Random SSM params matching duality_init_ssm_from_attention shapes.
    A: [d_model, d_state] ~ N(0,1)/sqrt(d_state)
    B: [d_state, d_model] Xavier uniform
    C: [d_model, d_state] Xavier uniform
    D: [d_model] zeros
    dt: [d_model] ones * 0.1
    """
```

### reconstruction_error.py (`h-m1/code/reconstruction_error.py`)

**Dependencies**: torch, scipy.stats

```python
def compute_reconstruction_error(ssm_output: Tensor, attn_output: Tensor) -> float:
    """torch.linalg.matrix_norm(ssm_output - attn_output, ord="fro").mean()"""

def paired_stats(duality_errors: List[float], random_errors: List[float]) -> dict:
    """Returns {mean_duality, mean_random, reduction_pct, p_value, cohens_d}"""
```

### run_experiment.py (`h-m1/code/run_experiment.py`)

**Dependencies**: duality_conversion, selective_scan, random_init, reconstruction_error, data_loader

```python
def run_comparison(num_samples: int = 500, d_state: int = 64, device: str = "cuda") -> Dict[str, Any]:
    """
    For each BERT layer (12) x each sample:
      attn_out = bert layer forward (reference)
      duality params = duality_init_ssm_from_attention(layer.attention.self, d_state)
      random params  = random_init_ssm(d_model, d_state, seed=42)
      duality_out = selective_scan_ref(embeddings, *duality_params)
      random_out  = selective_scan_ref(embeddings, *random_params)
      err_d = compute_reconstruction_error(duality_out, attn_out)
      err_r = compute_reconstruction_error(random_out, attn_out)
    Returns paired_stats + per-layer breakdown + gate pass/fail.
    """

def generate_figures(results: Dict[str, Any], output_dir: str = "figures/") -> List[str]:
    """Bar chart, box plot, per-layer comparison, histogram overlay."""

def main() -> Dict[str, Any]: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Reuse Setup | Copy h-e1 code (duality_conversion, selective_scan, data_loader) into h-m1, verify imports | 5 | 1+2+1+1 |
| M-2 | Random Init Baseline | Implement `random_init_ssm` matching duality output shapes | 7 | 2+1+2+2 |
| M-3 | Reconstruction Error Metric | Frobenius norm function + paired t-test + Cohen's d | 8 | 2+2+2+2 |
| M-4 | Per-Layer Attention Reference | Extract per-layer BERT attention output as ground truth | 9 | 2+2+2+3 |
| M-5 | Comparative Evaluation Loop | Run duality vs random across 12 layers x 500 samples | 15 | 3+4+4+4 |
| M-6 | Statistical Analysis Aggregation | Aggregate paired results, compute significance across full set | 10 | 2+3+3+2 |
| M-7 | Visualization Suite | Bar chart, box plot, per-layer chart, histogram | 8 | 2+2+2+2 |
| M-8 | Full Pipeline Orchestration | Wire together loader, models, eval, stats, figures; results JSON | 11 | 3+3+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [M-5], Medium(9-13): [M-4, M-6, M-8], Low(4-8): [M-1, M-2, M-3, M-7]

---

## Dependencies

```
torch>=2.0.0
transformers>=4.30.0
datasets>=2.0.0
matplotlib>=3.7.0
scipy>=1.10.0
pyyaml>=6.0
```

## Integration Points

1. BERT layer attention (per-layer) → duality_conversion (h-e1) / random_init (new)
2. SSM params → selective_scan_ref (h-e1) → SSM output
3. BERT layer forward → attention reference output
4. (SSM output, attention output) → reconstruction_error
5. Paired errors (all layers x samples) → statistical analysis → visualization

---

*Architecture designed for MECHANISM hypothesis validation*
*Next: Logic Design (Step 5)*
