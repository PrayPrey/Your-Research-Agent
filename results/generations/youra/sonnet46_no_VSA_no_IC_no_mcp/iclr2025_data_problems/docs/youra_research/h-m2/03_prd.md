# Product Requirements Document: H-M2
# Min-k% Memorization Signal — Pile vs Dedup-Pile Mechanism Verification

**Hypothesis:** H-M2 (MECHANISM / SHOULD_WORK)
**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Phase 2C Source:** docs/youra_research/h-m2/02c_experiment_brief.md
**Tier:** FULL (≤30 tasks)
**Base Hypothesis:** H-M1 (VALIDATED — PASS)

---

## 1. Executive Summary

H-M2 tests whether the document-level contamination signal confirmed in H-M1 translates into a detectable model-level memorization signal. Specifically: do Pythia models trained on Pile show higher min-k% probability scores on benchmark test items compared to token-count-matched Pythia models trained on dedup-Pile?

This is a measurement study — no model training required. The experiment applies the min-k% probe (Shi et al. 2023) to frozen Pythia checkpoints across 4 benchmarks and 2 model sizes. Gate: SHOULD_WORK — failure is informative (documents limitation) but does not block downstream hypotheses.

---

## 2. Problem Statement

**Research Question:** Do Pythia-Pile models show detectably higher min-k% probability scores on benchmark test items (MMLU, HellaSwag, ARC-Challenge, WinoGrande) compared to token-count-matched Pythia-dedup-Pile models, as measured by paired t-test with Bonferroni correction?

**Null Hypothesis (H0):** Pile and dedup-Pile Pythia models show equal min-k% probability distributions on benchmark test items (no benchmark achieves p < 0.0125).

**Alternative Hypothesis (H1):** Pile-trained models show significantly higher min-k% scores (paired t-test, one-tailed, p < 0.0125 Bonferroni-corrected) for ≥2 benchmarks.

**Failure Consequence:** If H0 is supported → document as limitation: min-k% may not capture near-memorization from near-duplicate (vs verbatim) content. SHOULD_WORK gate — does not block H-M3/H-M4. Explore alternative metrics (zlib ratio, lowercase perplexity).

---

## 3. Goals and Non-Goals

### Goals
- Load token-count-matched Pythia checkpoint pairs (Pile step ~98,000 vs dedup-Pile step 143,000) for 1B and 6.9B model sizes
- Compute min-k% probability scores (k=20% primary; k=10%, 40% secondary) for all benchmark test items (≥500 per benchmark; full sets preferred: 26,523 total)
- Apply paired t-test (Pile vs dedup-Pile per-item scores) with Bonferroni correction across 4 benchmarks
- Compute memorization differential per benchmark (mean_pile − mean_deduped) and correlate with H-M1 contamination rankings (secondary)
- Produce mandatory figure (bar chart) and 3 additional figures
- Run k-sensitivity analysis (k ∈ {5%, 10%, 20%, 40%, 60%}) on MMLU as robustness check
- Generate validation report confirming/refuting H1

### Non-Goals
- Training or fine-tuning any model
- Binary membership inference (AUC computation) — H-M2 uses paired comparison, not classification
- Re-implementing lm-evaluation-harness internals
- Analyzing Pythia models beyond 1B and 6.9B for primary results

---

## 4. Functional Requirements

### FR-1: Token-Count-Matched Model Loading
- Load 4 model × checkpoint pairs:
  - `EleutherAI/pythia-1b` at `revision="step98000"` (~205.7B tokens)
  - `EleutherAI/pythia-1b-deduped` at `revision="step143000"` (~207B tokens)
  - `EleutherAI/pythia-6.9b` at `revision="step98000"`
  - `EleutherAI/pythia-6.9b-deduped` at `revision="step143000"`
- Use `AutoModelForCausalLM.from_pretrained` with `revision=` parameter and `cache_dir="./model_cache"`
- Load in `float16` (fp16) for memory efficiency on 6.9B model
- Verify checkpoint step matches target: log `"Loaded checkpoint at step {step}, token_count={tokens}"`
- If revision not found → try adjacent step (±1000 steps); if still not found → FAIL with specific error

### FR-2: Benchmark Item Loading
- Load full test sets via HuggingFace datasets:
  - MMLU: `load_dataset("cais/mmlu", "all", split="test")` — 14,042 items
  - HellaSwag: `load_dataset("Rowan/hellaswag", split="validation")` — 10,042 items
  - ARC-Challenge: `load_dataset("allenai/ai2_arc", "ARC-Challenge", split="test")` — 1,172 items
  - WinoGrande: `load_dataset("winogrande", "winogrande_xl", split="test")` — 1,267 items
- Format each item as: question text + answer text concatenated (same format as training data / lm-eval convention)
- Exclude items with tokenized length < 32 tokens (too short for reliable min-k% scoring)

### FR-3: Min-k% Score Computation
- Implement `compute_mink_prob(text, model, tokenizer, k=20, device)` per Shi et al. 2023:
  - Tokenize with `max_length=512`, `truncation=True`
  - Forward pass: compute per-token log-probabilities via log_softmax of shifted logits
  - Sort token log-probs ascending; return mean of lowest k% (min-k% score)
  - Return `None` for items with < 32 tokens after tokenization
- Compute scores for k ∈ {10, 20, 40} (primary: k=20)
- Score all 26,523 benchmark items for all 4 model × checkpoint combinations
- Batch size: 1 (sequential) or 8 with padding for efficiency
- Save scores per model-benchmark combination to checkpoint files

### FR-4: Ablation — k-Sensitivity Analysis
- For MMLU (largest benchmark), compute scores at k ∈ {5, 10, 20, 40, 60}
- Report mean min-k% differential (Pile − deduped) at each k value
- Visualize as line plot (k-sensitivity plot)

### FR-5: Statistical Testing
- Primary: Paired t-test (`scipy.stats.ttest_rel`) per benchmark:
  - Paired on per-item scores: `pile_scores[i]` vs `deduped_scores[i]` for same item
  - One-tailed (alternative='greater'): Pile > deduped-Pile
  - Bonferroni correction: α_corrected = 0.05 / 4 = 0.0125
- Secondary: Wilcoxon signed-rank test (non-parametric robustness)
- Effect size: Cohen's d for paired comparison
- Compute memorization differential: `mean_pile[benchmark] − mean_deduped[benchmark]`
- Spearman correlation between H-M1 contamination rankings and H-M2 memorization differentials

### FR-6: Mechanism Activation Verification
- Assert all 4 model checkpoints loaded at correct steps
- Assert scoring completed for ≥500 items per benchmark (full sets preferred)
- Log `pile_mean > deduped_mean` direction per benchmark
- `verify_mechanism_activated(results)` function per 02c spec

### FR-7: Visualization
- **Mandatory (gate metrics):** Bar chart — mean min-k% score (Pile vs dedup-Pile) per benchmark × model size; 95% CI error bars; significance stars; saved as `figures/fig_mink_comparison.png`
- **Memorization differential heatmap:** 4 benchmarks × 2 model sizes; color = (Pile − dedup-Pile) differential; saved as `figures/fig_mink_heatmap.png`
- **Violin plot:** Per-benchmark distribution of item-level min-k% scores (Pile vs dedup-Pile) for Pythia-6.9B; saved as `figures/fig_mink_violin.png`
- **k-sensitivity plot:** Mean min-k% differential vs k ∈ {5,10,20,40,60} for MMLU; saved as `figures/fig_k_sensitivity.png`
- **Cross-hypothesis scatter (bonus):** X = H-M1 contamination differential, Y = H-M2 memorization differential; 4 benchmark points; saved as `figures/fig_cross_hypothesis.png`

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Pythia-1B scoring: ~7 GPU-hours (A100) for all items and k values
- Pythia-6.9B scoring: ~29 GPU-hours at batch_size=1; ~10 hours with batch_size=8 and padding
- Checkpoint/resume after each model-benchmark combination to avoid restart waste

### NFR-2: Reproducibility
- Inference is deterministic with fp16 (no dropout, no sampling)
- Random seed: 1 (no randomness in scoring — seed for any future sampling)
- All intermediate scores saved to checkpoint files (JSON/NPZ)

### NFR-3: Memory
- Pythia-1B fp16: ~2GB GPU VRAM
- Pythia-6.9B fp16: ~14GB GPU VRAM (A100 40GB sufficient)
- CPU RAM: ≤8GB (benchmark texts + score arrays fit comfortably)

### NFR-4: Correctness
- Min-k% uses MINIMUM k% of per-token log-probs (ascending sort, take first k_count)
- Paired scoring: same item order for Pile and dedup-Pile models (items loaded once, scores computed per model)
- One-tailed test (H1: Pile > deduped); Bonferroni applied before declaring significance

---

## 6. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Primary: ≥2 benchmarks significant | p < 0.0125 (paired t-test, one-tailed, Bonferroni) | `statistical_results_hm2.json` |
| SHOULD_WORK gate pass | ≥1 benchmark p < 0.0125 (relaxed gate) | gate_decision field |
| Effect direction | pile_mean > deduped_mean for significant benchmarks | memorization_differential field |
| Cross-hypothesis correlation | Spearman ρ > 0 (memorization differential vs H-M1 contamination) | spearman_result field |
| Mechanism activated | All 4 checkpoints loaded; ≥500 items scored per benchmark | verify_mechanism_activated() |
| k-sensitivity | Effect direction (Pile > deduped) holds for k ∈ {10, 20, 40} on MMLU | k_sensitivity_results field |

---

## 7. Data Specification

### 7.1 Models
| Model ID | HuggingFace ID | Checkpoint Step | Token Count |
|----------|----------------|-----------------|-------------|
| pile_1b | `EleutherAI/pythia-1b` | step98000 | ~205.7B |
| deduped_1b | `EleutherAI/pythia-1b-deduped` | step143000 | ~207B |
| pile_6.9b | `EleutherAI/pythia-6.9b` | step98000 | ~205.7B |
| deduped_6.9b | `EleutherAI/pythia-6.9b-deduped` | step143000 | ~207B |

### 7.2 Benchmark Test Sets
| Benchmark | Source | Test Items | HuggingFace ID |
|-----------|--------|-----------|----------------|
| MMLU | cais/mmlu | 14,042 | `cais/mmlu`, config="all", split="test" |
| HellaSwag | Rowan/hellaswag | 10,042 | `Rowan/hellaswag`, split="validation" |
| ARC-Challenge | allenai/ai2_arc | 1,172 | `allenai/ai2_arc`, "ARC-Challenge", split="test" |
| WinoGrande | winogrande | 1,267 | `winogrande`, "winogrande_xl", split="test" |

### 7.3 Outputs
| File | Location | Format | Contents |
|------|----------|--------|----------|
| mink_scores_pile_1b.json | h-m2/checkpoints/ | JSON | {benchmark: [per-item min-k% scores]} for pile_1b |
| mink_scores_deduped_1b.json | h-m2/checkpoints/ | JSON | Same for deduped_1b |
| mink_scores_pile_6.9b.json | h-m2/checkpoints/ | JSON | Same for pile_6.9b |
| mink_scores_deduped_6.9b.json | h-m2/checkpoints/ | JSON | Same for deduped_6.9b |
| statistical_results_hm2.json | h-m2/ | JSON | Per-benchmark stats, gate decision |
| figures/ | h-m2/figures/ | PNG | All 4-5 figures |

---

## 8. Dependencies

### 8.1 Python Packages
```
transformers>=4.35.0      # AutoModelForCausalLM, AutoTokenizer, revision= loading
datasets>=2.14.0          # Benchmark loading
torch>=2.0.0              # Forward pass, log_softmax
scipy>=1.10.0             # ttest_rel, wilcoxon, spearmanr
numpy>=1.24.0             # Array operations
matplotlib>=3.7.0         # Figures
seaborn>=0.12.0           # Violin plots
tqdm>=4.65.0              # Progress bars
```

### 8.2 External Repositories
- `EleutherAI/pythia` — checkpoint structure documentation (revision="step{N}" loading)
- `swj0419/detect-pretrain-code` — reference implementation of min-k% probe (Shi et al. 2023)
- `EleutherAI/lm-evaluation-harness` — benchmark text formatting convention

### 8.3 Hardware
- GPU: Required for 6.9B model (≥14GB VRAM; A100 40GB recommended)
- GPU optional for 1B model (can run on CPU with 16GB RAM, but slow)
- Storage: ~5GB for model caches (downloaded on first run); ~500MB for score checkpoints

### 8.4 Base Hypothesis Dependencies (H-M1)
- Same 4 benchmarks (MMLU, HellaSwag, ARC-Challenge, WinoGrande) — enables cross-hypothesis correlation
- Same Pythia model suite (same HuggingFace IDs, same revision loading pattern)
- H-M1 contamination rankings (`statistical_results_hm1.json`) used for secondary Spearman analysis
- Reused code patterns: `sig_stars()`, matplotlib Agg backend, JSON checkpoint pattern, flat code directory

---

## 9. Validation Report Requirements

`04_validation.md` must include:
- Per-benchmark × model-size results table: {benchmark, model, mean_pile, mean_deduped, differential, t_stat, p_value, p_corrected, significant}
- Gate decision: PASS (≥2 significant) / SHOULD_WORK_PASS (≥1 significant) / FAIL (0 significant) with next-steps
- k-sensitivity table: {k, MMLU_differential, MMLU_p_value, MMLU_significant}
- Cross-hypothesis correlation: Spearman ρ between H-M1 contamination and H-M2 memorization differentials
- Mechanism activation log: all 4 checkpoints loaded at correct steps
- Figures: all 4-5 figure paths confirmed

---

*stepsCompleted: PRD*
