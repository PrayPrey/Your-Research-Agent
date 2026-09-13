---
stepsCompleted:
  - executive-summary
  - problem-statement
  - functional-requirements
  - non-functional-requirements
  - data-specification
  - success-criteria
  - dependencies
hypothesis_id: H-M2
hypothesis_type: MECHANISM
date: 2026-08-20
author: yoon303b@gmail.com
---

# Product Requirements Document: H-M2
## Domain Exposure–Benchmark Correlation Analysis via Pythia Checkpoint Trajectory

---

## 1. Executive Summary

This experiment tests whether cumulative domain exposure during Pythia training correlates differentially with MMLU vs HellaSwag benchmark scores across 154 checkpoints × 3 representative model sizes (70M, 1B, 6.9B). Specifically, it computes Spearman ρ between cumulative Wikipedia exposure and MMLU scores, and between cumulative Books exposure and HellaSwag scores, then applies Fisher z-tests (one-tailed) to confirm directional superiority. The gate condition is P1: ρ(Wikipedia→MMLU) > ρ(Wikipedia→HellaSwag) for ≥2 of 3 model sizes.

**Key Deliverable:** A validated correlation analysis pipeline that demonstrates domain-specific exposure trajectories predict benchmark-specific learning patterns during Pythia training, providing the training-dynamics evidence for the YOURA hypothesis chain (H-E1 → H-M1 → H-M2 → H-M3).

**Reuse:** Domain exposure trajectories from H-E1 (154 checkpoints × 22 domains × 3 model sizes) are loaded directly — no recomputation. The content-level domain distinctions validated by H-M1 provide mechanistic grounding for the expected directional relationships.

---

## 2. Problem Statement

### 2.1 Background

H-E1 confirmed non-uniform domain exposure trajectories across Pythia checkpoints (std > 0.001 for ≥10 of 22 domains). H-M1 confirmed domain content differences are statistically significant (Wikipedia: higher factual-association density; Books: higher narrative-coherence features). H-M2 bridges these findings to training dynamics: if content differences drive benchmark alignment, then training exposure to Wikipedia should predict MMLU improvement more than HellaSwag improvement.

### 2.2 Problem

Without demonstrating that domain exposure trajectories during training predict benchmark-specific improvements, the correlation between corpus composition and downstream performance could be post-hoc and acausal. H-M2 provides time-series evidence by examining whether cumulative exposure at each of 154 training checkpoints tracks benchmark scores across model sizes.

### 2.3 Proposed Solution

Evaluate MMLU and HellaSwag for 3 Pythia model sizes at all 154 checkpoints using lm-evaluation-harness v0.4, load H-E1 domain exposure fractions, apply floor filtering (≥30% on all benchmarks), and compute Spearman ρ for each (domain, benchmark) pair. Apply Fisher z-test to confirm directional hypotheses P1 and P2 with Holm-Bonferroni correction.

---

## 3. Functional Requirements

### FR-1: Domain Exposure Data Loading (H-E1 Reuse)

**Description:** Load pre-computed domain exposure trajectories from H-E1 output.

**Requirements:**
- FR-1.1: Load `cumulative_domain_fraction[model_size][domain][checkpoint_t]` from H-E1 output files in `docs/youra_research/h-e1/` — shape per model: (154, 22)
- FR-1.2: Verify coverage: 154 checkpoints × 22 Pile domains × 3 model sizes (70M, 1B, 6.9B)
- FR-1.3: Align checkpoint step indices between H-E1 output and lm-eval-harness results (steps: 0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1000, 2000, …, 143000)
- FR-1.4: Verify domain names match Pile taxonomy (22 domains including "Wikipedia (en)", "Books3", "Github")
- FR-1.5: If H-E1 output format incompatible → raise explicit error with reformatting instructions

### FR-2: Checkpoint Benchmark Evaluation

**Description:** Evaluate MMLU and HellaSwag for all 154 checkpoints × 3 model sizes.

**Requirements:**
- FR-2.1: Evaluate Pythia-70m, Pythia-1b, Pythia-6.9b at all 154 checkpoint revisions (`revision=step{N}`)
- FR-2.2: MMLU evaluation: 5-shot, all 57 subjects, `cais/mmlu` dataset (post PR #497 fix); extract `acc,none` score averaged across subjects
- FR-2.3: HellaSwag evaluation: 10-shot, normalization scoring; extract `acc_norm,none` score
- FR-2.4: Use lm-evaluation-harness Python API (`lm_eval.simple_evaluate`) for batch processing
- FR-2.5: Batch size: `auto` for VRAM efficiency; dtype `float`
- FR-2.6: Save results per checkpoint per model size to `results/h-m2/eval_cache/{model_size}/step{N}.json`
- FR-2.7: Implement resume capability: skip checkpoint if cache file exists and is valid JSON
- FR-2.8: Fallback: if HF Hub unavailable, load pre-cached eval results from `EleutherAI/pythia` repo at `evals/pythia-v1/`
- FR-2.9: Total evaluations: 462 (154 × 3); parallelization across model sizes recommended

### FR-3: Floor Filtering

**Description:** Remove early training checkpoints where scores are below random chance.

**Requirements:**
- FR-3.1: Apply floor threshold ≥30% on both MMLU and HellaSwag simultaneously (per model size)
- FR-3.2: Mask: `valid_mask[t] = (mmlu[t] >= 0.30) AND (hellaswag[t] >= 0.30)`
- FR-3.3: Verify N_valid ≥ 100 checkpoints per model size after filtering; raise error if below
- FR-3.4: Log per model size: which checkpoints filtered, N_valid remaining
- FR-3.5: Apply same mask to domain exposure arrays (synchronized indexing)

### FR-4: Decontamination Audit

**Description:** 13-gram decontamination audit for MMLU and HellaSwag test sets vs training data.

**Requirements:**
- FR-4.1: Apply 13-gram overlap check comparing MMLU test questions against The Pile training documents seen by each checkpoint
- FR-4.2: Apply same to HellaSwag validation examples
- FR-4.3: Compute contamination-adjusted scores if overlap rate > 5% of any subject
- FR-4.4: Report both raw and adjusted correlations; use adjusted as primary if delta > 3pp for any benchmark
- FR-4.5: Save decontamination report to `results/h-m2/decontamination_report.json`

### FR-5: Spearman Correlation Analysis

**Description:** Compute Spearman ρ for all (domain, benchmark) pairs.

**Requirements:**
- FR-5.1: Compute `spearmanr(cumulative_exposure[domain, valid_mask], score[benchmark, valid_mask])` for all 22 domains × 2 benchmarks × 3 model sizes = 132 correlation coefficients
- FR-5.2: Use `scipy.stats.spearmanr` (nonparametric, handles monotonic relationships)
- FR-5.3: Store (ρ, p-value) for each (domain, benchmark, model_size) triple
- FR-5.4: Primary focus: (Wikipedia (en), mmlu), (Wikipedia (en), hellaswag), (Books3, hellaswag), (Books3, mmlu)
- FR-5.5: Compute 95% CI for each Spearman ρ: `ci = [tanh(atanh(rho) ± 1.96/sqrt(n-3))]`

### FR-6: Fisher Z-Test for Directional Comparison

**Description:** Test P1 and P2 hypotheses via one-tailed Fisher z-test.

**Requirements:**
- FR-6.1: P1 test per model size: `fisher_z_test(rho_wiki_mmlu, rho_wiki_hellaswag, n_valid)` — one-tailed H1: rho_wiki_mmlu > rho_wiki_hellaswag
- FR-6.2: P2 test per model size: `fisher_z_test(rho_books_hellaswag, rho_books_mmlu, n_valid)` — one-tailed H1: rho_books_hellaswag > rho_books_mmlu
- FR-6.3: Fisher z formula: `z = (atanh(rho1) - atanh(rho2)) / sqrt(2 / (n-3))`, p = `1 - norm.cdf(z)`
- FR-6.4: Apply Holm-Bonferroni correction across 4 tests (P1×3 sizes + P2×3 sizes → primary: P1 for 2 of 3 sizes)
- FR-6.5: Significance threshold: p < 0.10 (SHOULD_WORK gate — exploratory directional test)
- FR-6.6: Gate evaluation: P1 passed if `rho_wiki_mmlu > rho_wiki_hellaswag` for ≥2 of 3 model sizes (regardless of p-value — directional confirmation is primary)

### FR-7: Gate Verification

**Description:** Implement `verify_mechanism_activated()` as specified in 02c_experiment_brief.md.

**Requirements:**
- FR-7.1: Implement per spec: count model sizes where P1 and P2 directional conditions hold
- FR-7.2: Assert N_valid ≥ 100 per model size
- FR-7.3: Return `(mechanism_activated: bool, indicators: dict)` with p1_gate_passed, p2_gate_passed, counts
- FR-7.4: Log all intermediate values for reproducibility

### FR-8: Visualization

**Description:** Generate required and optional figures.

**Requirements:**
- FR-8.1 (MANDATORY): Bar chart of ρ(Wikipedia→MMLU) vs ρ(Wikipedia→HellaSwag) × 3 model sizes, with 95% CIs — save to `docs/youra_research/h-m2/figures/fig1_gate_metrics.png`
- FR-8.2: Full ρ matrix heatmap: top-8 Pile domains × 2 benchmarks × 3 model sizes (3 subplot panels) — `figures/fig2_domain_benchmark_heatmap.png`
- FR-8.3: Trajectory plots: Wikipedia exposure vs MMLU/HellaSwag over 154 checkpoints × 3 sizes (6 line plots, dual y-axis) — `figures/fig3_trajectories.png`
- FR-8.4: Fisher z-test forest plot: point estimates + 95% CIs for P1 and P2 comparisons — `figures/fig4_fisher_forest.png`
- FR-8.5: Floor filtering diagnostic: which checkpoints filtered, N_valid per model size — `figures/fig5_floor_filter.png`
- FR-8.6: All figures: 300 DPI, accessible color scheme (colorblind-safe palette)

### FR-9: Results Reporting

**Description:** Generate structured results output.

**Requirements:**
- FR-9.1: Save full correlation matrix to `results/h-m2/correlation_matrix.json` (all 132 ρ values + CIs + p-values)
- FR-9.2: Save gate evaluation summary to `results/h-m2/gate_summary.json`
- FR-9.3: Save Fisher z-test results to `results/h-m2/fisher_tests.json`
- FR-9.4: Save final summary report to `docs/youra_research/h-m2/04_results_summary.md`

---

## 4. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seed = 42 (no randomness in Spearman ρ — seed only for any sampling)
- All checkpoint step indices deterministic (Pythia training is deterministic)
- Decontamination audit results cached and versioned

### NFR-2: Performance
- Resume capability for checkpoint evaluation (skip completed evaluations)
- Estimated wall-clock: ~6–12 hours for full 462-checkpoint evaluation (GPU-dependent)
- Memory: ≥16GB VRAM for Pythia-6.9B; CPU-only fallback allowed for 70M
- Parallelization: run 3 model sizes concurrently on separate GPUs if available

### NFR-3: Fault Tolerance
- If HF Hub unavailable: fall back to pre-cached Pythia eval results
- If N_valid < 100 after floor filtering: raise error with diagnostic (do not silently proceed)
- Checkpoint resume: idempotent evaluation — re-running safe

### NFR-4: Modularity
- Separate modules: `data_loader.py`, `evaluator.py`, `correlation_analysis.py`, `statistical_test.py`, `visualization.py`, `reporter.py`
- Each module independently testable with minimal mock data

### NFR-5: Logging
- Log each checkpoint evaluation start/completion with timestamp
- Log N_valid checkpoints after floor filtering per model size
- Log all correlation coefficients computed
- Use Python `logging` module at INFO level by default

---

## 5. Data Specification

### 5.1 Input Data

| Dataset | Source | Access Method | Notes |
|---------|--------|---------------|-------|
| Domain exposure fractions | H-E1 output | Local file load | Shape: (154, 22) per model size |
| Pythia checkpoints | HuggingFace Hub | `revision=step{N}` | 70m, 1b, 6.9b |
| MMLU test set | `cais/mmlu` (HF) | lm-eval-harness auto | 14,042 questions, 57 subjects |
| HellaSwag validation | `Rowan/hellaswag` (HF) | lm-eval-harness auto | 10,042 examples |
| Pythia dataloader indices | `EleutherAI/pythia_deduped_pile_idxmaps` | numpy memmap | For decontamination |

### 5.2 Output Data

| Output | Path | Format | Size Estimate |
|--------|------|--------|---------------|
| Eval cache | `results/h-m2/eval_cache/` | JSON per checkpoint | ~462 files × 50KB = ~23MB |
| Correlation matrix | `results/h-m2/correlation_matrix.json` | JSON | ~100KB |
| Gate summary | `results/h-m2/gate_summary.json` | JSON | ~5KB |
| Fisher tests | `results/h-m2/fisher_tests.json` | JSON | ~10KB |
| Decontamination report | `results/h-m2/decontamination_report.json` | JSON | ~50KB |
| Figures | `docs/youra_research/h-m2/figures/` | PNG (300 DPI) | ~5 files |
| Results summary | `docs/youra_research/h-m2/04_results_summary.md` | Markdown | ~5KB |

### 5.3 Data Dependencies

- **H-E1 output (REQUIRED):** `cumulative_domain_fraction` arrays for 70M, 1B, 6.9B
- **H-M1 context (informational):** Domain content taxonomy (Wikipedia, Books3, Github focal domains)
- **No new training data downloads** beyond Pythia checkpoint weights (HF Hub streaming)

---

## 6. Success Criteria

### Primary Gate (SHOULD_WORK)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| P1 Directional | ρ(Wikipedia→MMLU) > ρ(Wikipedia→HellaSwag) for ≥2 of 3 model sizes | `p1_directional_count >= 2` |
| P2 Directional | ρ(Books3→HellaSwag) > ρ(Books3→MMLU) for ≥2 of 3 model sizes | `p2_directional_count >= 2` |
| Floor Filter Valid | N_valid ≥ 100 checkpoints per model size | `n_valid >= 100` for all 3 sizes |
| Gate Output | `verify_mechanism_activated()` returns True | mechanism_activated == True |

### Secondary Criteria

| Criterion | Target | Notes |
|-----------|--------|-------|
| Fisher z-test P1 | p < 0.10 (one-tailed) for ≥2 of 3 model sizes | Exploratory; directional count is primary |
| Correlation magnitude | rho_wiki_mmlu > 0.5 for ≥1 model size | Expected stronger at 6.9B |
| Decontamination delta | < 3pp shift | If > 3pp, use adjusted as primary |
| Reproducibility | Same ρ values on rerun | Deterministic pipeline |

### Failure Mode

Gate FAIL → EXPLORE: proceed to H-M3 with limitation documented ("Wikipedia-MMLU correlation not confirmed via training dynamics; scale effects may mask signal at Pythia scale")

---

## 7. Dependencies

### 7.1 Python Packages

```
# Core evaluation
lm_eval>=0.4.0            # lm-evaluation-harness
torch>=2.0                # PyTorch (GPU required for 6.9B)
transformers>=4.35        # HuggingFace model loading

# Statistical analysis
scipy>=1.7                # spearmanr, norm.cdf
numpy>=1.20               # arctanh, ndarray operations

# Data loading
datasets>=2.14            # HuggingFace datasets (MMLU, HellaSwag)
huggingface_hub>=0.17     # Checkpoint revision access

# Visualization
matplotlib>=3.7           # All figures
seaborn>=0.12             # Heatmap

# NLP (decontamination)
nltk>=3.8                 # 13-gram tokenization for decontamination

# Utilities
tqdm>=4.65                # Progress bars
pyyaml>=6.0               # Config files
```

### 7.2 External Repositories

| Repository | URL | Usage |
|-----------|-----|-------|
| EleutherAI/pythia | https://github.com/EleutherAI/pythia | Checkpoint access, fallback evals |
| EleutherAI/lm-evaluation-harness | https://github.com/EleutherAI/lm-evaluation-harness | Benchmark evaluation framework |
| EleutherAI/pythia_deduped_pile_idxmaps | HuggingFace | Pile dataloader indices (decontamination) |

### 7.3 Previous Hypothesis Outputs

| Hypothesis | Output Required | Path |
|-----------|-----------------|------|
| H-E1 | Domain exposure fractions (154×22×3 array) | `docs/youra_research/h-e1/` |
| H-M1 | Focal domain list (Wikipedia, Books3, Github) | Informational (taxonomy) |

### 7.4 Hardware Requirements

- GPU: ≥16GB VRAM for Pythia-6.9B evaluation; 8GB for 70M/1B
- Disk: ≥50GB for checkpoint cache + eval results
- CPU: Any modern multi-core (statistical analysis is CPU-only)
- Network: HuggingFace Hub access (or pre-cached checkpoints)
