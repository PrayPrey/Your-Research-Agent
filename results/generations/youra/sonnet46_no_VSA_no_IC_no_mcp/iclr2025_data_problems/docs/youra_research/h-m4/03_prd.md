---
stepsCompleted: [1, 2, 3, 4, 5, 6]
hypothesis_id: h-m4
generated_at: "2026-08-25T00:00:00+00:00"
---

# Product Requirements Document: H-M4

## 1. Executive Summary

H-M4 is a robustness check extending H-M3 to compare two checkpoint-matching strategies for Pythia model evaluation: **token-count-matched** (H-M3 baseline, r=0.632) vs **step-matched** (H-M4 new condition). The experiment isolates whether the ~15% token volume reduction in dedup-Pile acts as a confound on the contamination-correction signature discovered in H-M3. The deliverable is a comparison of Pearson r values and uniform accuracy bias under both matching conditions across 4 benchmarks × 4 Pythia model sizes.

## 2. Problem Statement

H-M3 validated a contamination-correction signal (Pearson r=0.632) using token-count-matched checkpoint pairs. However, an alternative methodological choice — step-matching — would not control for the ~15% volume difference between Pile (~244B tokens) and dedup-Pile (~207B tokens). If volume matters, step-matched differentials will show a larger uniform negative bias and a weaker contamination-correlation. H-M4 tests this by adding step-matched pairs to the same experimental apparatus.

**Research Question:** Does the choice of checkpoint-matching method (token-count vs step) materially affect the contamination-performance correlation and the per-benchmark accuracy differential?

## 3. Scope

**In Scope:**
- Evaluate 4 Pythia model sizes (160M, 410M, 1B, 6.9B) × 4 benchmarks under step-matched condition
- Reuse H-M3 token-count-matched results as baseline (no re-evaluation needed)
- Compute and compare r_token_matched vs r_step_matched
- Compute uniform bias (mean differential) under each condition
- Generate required figures

**Out of Scope:**
- New model architectures
- New benchmarks
- Re-running H-M3 evaluations (results inherited)
- Full contamination re-estimation (uses H-M3 estimates)

## 4. Data Specification

### 4.1 Primary Data Source

| Field | Value |
|-------|-------|
| Source | HuggingFace Hub (EleutherAI/pythia, EleutherAI/pythia-{size}-deduped) |
| Access Method | Programmatic API — `AutoModelForCausalLM.from_pretrained(..., revision="step{N}")` |
| Download Required | YES — step-matched checkpoints (Pile step 143K for each size) |
| Sizes | 160M, 410M, 1B, 6.9B |
| Disk Estimate | ~0.4GB (160M) + ~1.0GB (410M) + ~1.5GB (1B) + ~13GB (6.9B) per checkpoint |

**Note:** Token-count-matched Pile checkpoints (step ~121K) may already be cached from H-M3. Step-matched Pile checkpoints (step 143K) are NEW downloads.

### 4.2 Checkpoint Pair Specification

| Condition | Pile step | dedup-Pile step | Pile tokens | dedup tokens | Volume ratio |
|-----------|-----------|-----------------|-------------|--------------|--------------|
| Token-count-matched (H-M3) | ~121K | 143K | ~207B | ~207B | ~1.00 |
| Step-matched (H-M4 NEW) | 143K | 143K | ~244B | ~207B | ~1.15 |

### 4.3 Benchmark Datasets

| Benchmark | Task | Few-shot | Data split | N examples |
|-----------|------|----------|------------|------------|
| MMLU | Knowledge QA | 5-shot | test | ~14,000 |
| HellaSwag | Sentence completion | 10-shot | validation | ~10,042 |
| ARC-Challenge | Science QA | 25-shot | test | ~1,172 |
| WinoGrande | Commonsense | 5-shot | validation | ~1,267 |

All benchmark data is auto-downloaded by lm-evaluation-harness — no manual download required.

### 4.4 Inherited Data (No Download)

| Data | Source | Location |
|------|--------|----------|
| Token-count-matched accuracy results | H-M3 | `docs/youra_research/h-m3/` results files |
| Contamination estimates | H-M3/literature | H-M3 analysis outputs |
| Contamination overlap per benchmark | H-M3 | H-M3 `analysis.py` output |

## 5. Functional Requirements

### FR-1: Checkpoint Selector Module

Implement `checkpoint_selector.py` providing:
- `compute_token_count_at_step(step, tokens_per_step) -> float`
- `find_token_matched_pile_step(dedup_step, dedup_tps, pile_tps, available_pile_steps) -> int`
- `get_step_matched_pair(dedup_step) -> tuple[int, int]`
- `get_token_count_matched_pair(dedup_step, pile_steps, pile_tps, dedup_tps) -> tuple[int, int]`
- `verify_checkpoint_matching_activated(pile_step, dedup_step, condition, pile_tps, dedup_tps) -> bool`

### FR-2: Evaluation Runner (Step-Matched Condition)

Run lm-evaluation-harness for Pile step-143K checkpoints for all 4 model sizes × 4 benchmarks. Token-count-matched results from H-M3 are inherited (not re-evaluated).

**Evaluation parameters (identical to H-M3):**
- Framework: lm-evaluation-harness (EleutherAI) — same pinned version as H-M3
- Device: CUDA, precision: float16
- Batch size: 1 (inference)
- Deterministic seed: 1

### FR-3: Results Aggregator

Load and merge:
1. Step-matched evaluation results (H-M4 new)
2. Token-count-matched results (H-M3 inherited)

Output unified DataFrame: `benchmark × model_size × condition → accuracy_differential`

### FR-4: Statistical Analysis Module

Compute for each condition (token_matched, step_matched):
- `accuracy_differential = acc_dedup - acc_pile` per benchmark × model size
- `Pearson r` between contamination_estimate and accuracy_differential (n=16 obs)
- `Spearman ρ` same
- `p-value` for each
- `Bootstrap 95% CI` (n=10,000 iterations)
- `uniform_bias = mean(accuracy_differential)` across all benchmarks
- `delta_r = r_token_matched - r_step_matched`
- `bias_delta = uniform_bias_step - uniform_bias_token`

### FR-5: Ablation — No H-M3 Baseline

Confirm results hold when NOT inheriting H-M3 token-count-matched results (i.e., re-computing from raw accuracy numbers if available). Document if H-M3 inheritance introduces any numerical discrepancy.

### FR-6: Visualization

Generate figures in `docs/youra_research/h-m4/figures/`:
1. **MANDATORY:** `fig_01_correlation_comparison.png` — Bar chart: r_token_matched vs r_step_matched with 95% CIs
2. `fig_02_scatter_comparison.png` — 2-panel scatter: contamination vs differential for each condition
3. `fig_03_differential_bars.png` — Per-benchmark differential comparison across conditions and model sizes
4. `fig_04_bias_decomposition.png` — Volume bias vs contamination component per model size
5. `fig_05_summary_table.png` — r, ρ, p-values, CIs for both conditions

### FR-7: Gate Evaluation

Evaluate and document:
- Primary gate: `r_token_matched >= r_step_matched`
- Secondary gate: `uniform_bias_step < uniform_bias_token`
- Gate fail condition: `|delta_r| < 0.05 AND |bias_delta| < 0.01` → document as robustness confirmation

## 6. Non-Functional Requirements

| Requirement | Value |
|-------------|-------|
| Reproducibility | Deterministic — seed=1, pinned lm-eval version |
| Compute | GPU required for 6.9B model (CUDA) |
| Disk space | ~15GB for new step-matched Pile checkpoints (6.9B dominates) |
| Runtime | ~4-8h for 6.9B inference; smaller models cached from H-M3 |
| Output format | JSON (raw results), CSV (aggregated), PNG (figures) |

## 7. Dependencies

### 7.1 Python Packages

```
transformers>=4.35.0
lm-eval==<same version as H-M3>
torch>=2.0.0
scipy>=1.10.0
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
huggingface_hub>=0.19.0
pyyaml>=6.0
```

### 7.2 External Repositories / Data

| Resource | URL | Purpose |
|----------|-----|---------|
| EleutherAI/pythia | https://github.com/EleutherAI/pythia | Model checkpoints |
| EleutherAI/lm-evaluation-harness | https://github.com/EleutherAI/lm-evaluation-harness | Evaluation framework |
| HuggingFace Hub | Programmatic | Checkpoint downloads |

### 7.3 Inherited Outputs (H-M3)

| File | Description |
|------|-------------|
| `docs/youra_research/h-m3/results/token_matched_results.json` | Token-count-matched accuracy per benchmark × model |
| `docs/youra_research/h-m3/results/contamination_estimates.csv` | Contamination overlap per benchmark |
| `docs/youra_research/h-m3/analysis.py` | Analysis scripts to inherit/adapt |

## 8. Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| Step-matched evaluations complete | All 4 sizes × 4 benchmarks = 16 evaluations done |
| Gate primary | r_token_matched ≥ r_step_matched (OR: document robustness confirmation) |
| Gate secondary | uniform_bias_step ≤ uniform_bias_token |
| Figures | All 5 figures generated |
| Statistical rigor | Bootstrap 95% CIs computed for both conditions |
| Reproducibility | Full results in JSON; scripts in code/ |

## 9. Experiment Context

**Hypothesis Type:** MECHANISM (robustness check)
**Gate Type:** SHOULD_WORK
**Prerequisites:** H-M3 (VALIDATED — Pearson r=0.632, p=0.0086)
**Expected runtime:** 1-2 days (dominated by 6.9B inference)
**Phase 4 reads:** `03_tasks.yaml` for task execution order
