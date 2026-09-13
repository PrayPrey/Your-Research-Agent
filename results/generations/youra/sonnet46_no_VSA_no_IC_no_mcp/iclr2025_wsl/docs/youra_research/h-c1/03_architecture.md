# Architecture: H-C1 — Sign-Flip Canonicalization Uniqueness Audit

**Hypothesis:** H-C1  
**Type:** CONDITION  
**Date:** 2026-08-27  
**Tier:** FULL (30 tasks max)  
**Epic Range:** 6–12  

---

## Codebase Analysis (Serena)

*Serena MCP not available (no-MCP session). Codebase analysis performed via direct inspection of prior hypothesis context.*

**Prior codebase reference (H-M3):**
- Sign-flip canonicalization implemented as ~30 lines PyTorch (`canonicalize.py`)
- Pattern: `exact_majority_sign` via `torch.sign(W1).sum(dim=1)` → `torch.sign(...)`
- Tie-breaking: `signs[signs == 0] = 1`
- No complex module hierarchy — single-file audit script pattern confirmed

**Green-field for H-C1:**
- No existing `h-c1/code/` directory
- Module structure designed from scratch, informed by H-M3 patterns

Applied: single-script-audit-pattern (H-M3 prior)  
Applied: data-load-then-audit pipeline structure  
Applied: failsafe-self-check-first pattern (idempotency assert before full loop)

---

## Module Structure

```
h-c1/
├── code/
│   ├── canonicalize.py       # sign-flip canonicalization (reused/adapted from H-M3)
│   ├── data_loader.py        # Schürholt zoo loading, sampling, weight extraction
│   ├── audit.py              # uniqueness audit loop, idempotency check, degeneracy stats
│   ├── visualize.py          # figures: bar chart (gate metric), histograms (conditional)
│   └── run_experiment.py     # entry point: orchestrate load → audit → visualize → report
├── figures/                  # output figures saved here
└── results/
    └── audit_results.json    # structured output: per-model flags + summary stats
```

---

## File Organization

| File | Responsibility | Imports |
|------|---------------|---------|
| `canonicalize.py` | `exact_majority_sign`, `canonicalize_sign_flip_m2` | torch |
| `data_loader.py` | `load_zoo_sample(n=500, seed=1)` → list of (W1, W2) | datasets, torch |
| `audit.py` | `run_audit(models)` → results list, summary dict | torch, canonicalize |
| `visualize.py` | `plot_gate_metric`, `plot_tied_neuron_hist` | matplotlib |
| `run_experiment.py` | End-to-end: load → audit → visualize → report → gate verdict | all above |

---

## Epic Tasks

### Epic E1: Data Loading and Sampling
**Description:** Implement `data_loader.py` — load Schürholt MNIST zoo via HuggingFace `datasets`, sample N=500 models with seed=1, extract W1 (64,784) and W2 (10,64) tensors, validate shapes.  
**Module:** data  
**Complexity Score:** 7 (Low-Medium)  
**Breakdown:** Module_Size(2) + Dependencies(2) + Algorithm(1) + Integration(2)  
**Complexity Level:** Medium  

### Epic E2: Sign-Flip Canonicalization Module
**Description:** Implement `canonicalize.py` with `exact_majority_sign(weights)` and `canonicalize_sign_flip_m2(W1, W2)` per 02c_experiment_brief.md spec. Reuse H-M3 implementation where possible. Include tie-breaking (+1 default) and return `is_degenerate` flag.  
**Module:** model  
**Complexity Score:** 9 (Medium)  
**Breakdown:** Module_Size(2) + Dependencies(1) + Algorithm(4) + Integration(2)  
**Complexity Level:** Medium  

### Epic E3: Uniqueness and Idempotency Audit Loop
**Description:** Implement `audit.py` — `run_audit(models, n=500)`: for each model apply canonicalization, record `is_degenerate` and `idempotent` flags. Compute `fraction_unique`, `fraction_idempotent`. Run idempotency self-check assert on first model before full loop.  
**Module:** evaluation  
**Complexity Score:** 10 (Medium)  
**Breakdown:** Module_Size(3) + Dependencies(2) + Algorithm(3) + Integration(2)  
**Complexity Level:** Medium  

### Epic E4: Degeneracy Characterization
**Description:** If any degenerate models: compute `mean_tied_neurons_per_degenerate_model`, `weight_norm_of_tied_neurons`, cluster by accuracy bin. Export to `results/audit_results.json`.  
**Module:** evaluation  
**Complexity Score:** 8 (Medium)  
**Breakdown:** Module_Size(2) + Dependencies(2) + Algorithm(2) + Integration(2)  
**Complexity Level:** Medium  

### Epic E5: Visualization
**Description:** Implement `visualize.py` — mandatory bar chart (`fraction_unique` vs 0.99 threshold), conditional histogram of tied neuron counts per degenerate model, conditional scatter (weight L1-norm vs tied fraction). Save all to `docs/youra_research/h-c1/figures/`.  
**Module:** evaluation  
**Complexity Score:** 7 (Low-Medium)  
**Breakdown:** Module_Size(2) + Dependencies(2) + Algorithm(1) + Integration(2)  
**Complexity Level:** Medium  

### Epic E6: Experiment Entry Point and Gate Verdict
**Description:** Implement `run_experiment.py` — orchestrate full pipeline: load → self-check → audit → characterization → visualize → print structured summary → render gate verdict (PASS/FAIL/SCOPE) against thresholds from PRD.  
**Module:** experiment  
**Complexity Score:** 8 (Medium)  
**Breakdown:** Module_Size(2) + Dependencies(1) + Algorithm(2) + Integration(3)  
**Complexity Level:** Medium  

---

## Task Budget Summary

| Category | Count |
|----------|-------|
| Epic Tasks | 6 |
| Subtasks (from Logic/Config) | TBD (Step 4) |
| Total Epics | 6 (within 6–12 range ✓) |

---

## External Dependencies

Base hypothesis H-M3 provides:
- Sign-flip canonicalization algorithm (reference implementation)
- Schürholt zoo loading pattern (confirmed working in H-E1, H-M3)
- Weight extraction format: W1 (64,784), W2 (10,64)

No import path dependencies from H-M3 codebase required — H-C1 reimplements the ~30-line canonicalization from spec (or copies the file if present).
