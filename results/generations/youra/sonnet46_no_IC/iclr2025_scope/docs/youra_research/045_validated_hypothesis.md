# Validated Hypothesis Synthesis

**Generated:** 2026-08-05
**Workflow:** Phase 4.5 Hypothesis Synthesis
**Pipeline Position:** Phase 4 (Hypothesis Loop) → [Phase 4.5] → Phase 5/6

> ⚠️ **PIPELINE STATE NOTE:** Phase 4 (coding + experiment execution) was not completed for h-e1.
> All 15 implementation tasks remain in `todo` status. No experimental data was produced.
> This document reflects the planned experimental design and provides INCONCLUSIVE status
> for all predictions pending Phase 4 execution. **This document must be regenerated after
> Phase 4 completes.**

---

## 1. Executive Summary

Phase 4.5 was invoked after Phase 3 (implementation planning) completed for sub-hypothesis h-e1,
but before Phase 4 (experiment execution) ran. The PARA oracle sweep — requiring ~2,160 training
runs across 3 model families — was fully designed and planned but not executed. Consequently,
no empirical data exists to confirm or refute the core prediction (P1: Pearson r ≥ 0.65 between
erank(W₀) and PARA oracle ranks).

The original hypothesis remains in its Phase 2A form. No overclaims can be removed (no evidence
to contradict them) and no claims can be strengthened. All predictions are INCONCLUSIVE pending
Phase 4 execution.

| Metric | Value |
|--------|-------|
| **Original Core Statement** | erank(W₀) correlates with PARA oracle ranks (r ≥ 0.65) in ≥2/3 model families |
| **Refined Core Statement** | UNCHANGED — no experimental data to drive refinement |
| **Predictions Supported** | 0 / 5 (no data) |
| **Overall Pass Rate** | N/A (Phase 4 not executed) |
| **Hypotheses Validated** | 0 / 1 (h-e1 IN_PROGRESS) |

---

## 2. Prediction-Result Matrix

| Prediction | Original Statement | Tested By | Key Metric | Result | Status | Confidence | Evidence Summary |
|------------|-------------------|-----------|------------|--------|--------|------------|------------------|
| **P1** | Pearson r(erank(W₀), oracle_rank) ≥ 0.65 for ≥2/3 model families (one-tailed p < 0.05) | h-e1 PARA oracle sweep | Pearson r per model family | NOT MEASURED | INCONCLUSIVE | 0.00 | No 04_validation.md — Phase 4 not executed |
| **P2** | erank-proportional rank assignment within 1% of oracle, beats uniform r=8 | h-e1 erank strategy eval | Val accuracy gap to oracle | NOT MEASURED | INCONCLUSIVE | 0.00 | No 04_validation.md — Phase 4 not executed |
| **P3** | ‖ΔW_opt‖_F/‖W₀‖_F correlates with erank(W₀) at Spearman ρ ≥ 0.5 | h-e1 adaptation magnitude analysis | Spearman ρ per family | NOT MEASURED | INCONCLUSIVE | 0.00 | No 04_validation.md — Phase 4 not executed |
| **P4** | Levene test on oracle ranks by erank tercile significant (p < 0.05) for ≥2/3 families | h-e1 distribution analysis | Levene p-value | NOT MEASURED | INCONCLUSIVE | 0.00 | No 04_validation.md — Phase 4 not executed |
| **P5** | PR(W₀) and erank(W₀) agree in layer ranking at Spearman ρ ≥ 0.8 | h-e1 metric comparison | Spearman ρ(erank, PR) | NOT MEASURED | INCONCLUSIVE | 0.00 | No 04_validation.md — Phase 4 not executed |

**Status Legend:** SUPPORTED | PARTIALLY_SUPPORTED | REFUTED | INCONCLUSIVE

### Causal Mechanism Verification

| Mechanism Step | Description | Falsifier | Evidence | Verification Status |
|----------------|-------------|-----------|----------|---------------------|
| Step 1 | Pre-training shapes singular value distributions; complex layers develop spread-out spectra (high erank) | Levene p > 0.05, CV < 0.02 across all layers | Theoretical (Aghajanyan 2021, h-e1 prior ViT depth variation) | UNVERIFIED — awaiting Phase 4 |
| Step 2 | High-erank matrices have non-dominated singular directions requiring higher-rank LoRA updates | LoRA update directions show no relationship to W₀ singular spread (Spearman ρ < 0.1) | Theoretical (Dr. Nova direction argument; AdaLoRA layer allocations consistent) | UNVERIFIED — awaiting Phase 4 |
| Step 3 | PARA oracle assigns higher ranks to high-erank layers, creating measurable Pearson correlation | Pearson r < 0.65 for all 3 model families | None — primary empirical test of P1 | UNVERIFIED — awaiting Phase 4 |

---

## 3. Hypothesis Refinement

### 3.1 Original Core Statement (Phase 2A)

> Under pre-trained transformer models {BERT-base-uncased, DeBERTa-v3-base, ViT-base-patch16-224}
> with adequate fine-tuning (≥3 epochs NLP on full GLUE MNLI 392k samples; ≥5 epochs ViT on
> CIFAR-10 50k samples), if per-layer effective rank erank(W₀) = exp(H(σ/‖σ‖₁)) of each
> weight matrix W₀ is computed from pre-trained weights (fp32 precision, before any fine-tuning),
> then it demonstrates statistically significant positive Pearson correlation (r ≥ 0.65,
> one-tailed H₁: α > 0) with per-layer marginal PARA oracle ranks (argmax over r ∈ {4,8,16,32,64}
> of validation accuracy, all non-target layers frozen at baseline r=8) across ≥2 of the 3
> model families, because effective rank captures the geometric complexity of each layer's
> pre-training representation.

### 3.2 Refined Core Statement (Phase 4.5)

> IDENTICAL TO ORIGINAL — no experimental data available to drive refinement.
> This statement must be revised after Phase 4 execution based on actual Pearson r values,
> direction of correlation, and which model families satisfy the threshold.

**Key Changes:**
- None. No experimental evidence to support any modification.

### 3.3 Causal Mechanism — Verified Chain

```
UNVERIFIED — All three mechanism steps remain at theoretical/indirect-evidence level.
Phase 4 execution required to verify or falsify.

Step 1 [UNVERIFIED]: Pre-training → layer-specific singular spectra spread → erank variation
Step 2 [UNVERIFIED]: High erank → non-dominated directions → higher rank needed for LoRA
Step 3 [UNVERIFIED]: PARA oracle independently discovers same high-erank = high-rank structure
```

**Removed/Modified Steps:**
- None. No steps removed — no experimental data to justify removal.

### 3.4 Claims Removed or Weakened

| Original Claim | Action | Reason | Evidence |
|----------------|--------|--------|----------|
| r ≥ 0.65 threshold achievable | PENDING | No data | Phase 4 not executed |
| ≥2/3 model families satisfy threshold | PENDING | No data | Phase 4 not executed |
| erank-proportional strategy within 1% of oracle | PENDING | No data | Phase 4 not executed |

### 3.5 Assumptions Status

| Assumption | Original Status | Verification Status | Evidence | Impact if Violated |
|------------|----------------|---------------------|----------|-------------------|
| A1: erank shows sufficient variation (CV > 0.05) across layers | Supporting evidence (ViT depth variation, BERT Levene p=0.0001) | PARTIALLY_SUPPORTED (indirect) | 03_refinement.yaml: ViT entropy 4.27→6.44 by depth; BERT Levene p=0.0001 | Correlation undetectable; fallback to PR(W₀) |
| A2: PARA oracle produces stable rank assignments (2 seeds sufficient) | Supporting evidence (MNLI 392k sufficient size) | UNVERIFIED | Statistical argument only | Oracle ranks noisy; Pearson r unreliable |
| A3: Positive direction holds (erank positively predicts oracle rank) | Theoretical derivation + AdaLoRA consistency | UNVERIFIED | Dr. Nova direction argument; AdaLoRA allocates higher rank to FFN/deep layers | Hypothesis falsified in stated form if r < 0 |
| A4: Task-agnosticity (MNLI vs SST-2 oracle agreement ρ ≥ 0.7) | IFCLoRA structural predictor generalizes | UNVERIFIED | Theoretical analogy only | erank becomes task-specific predictor |
| A5: erank better than spectral entropy (wider dynamic range) | erank uses normalized distribution | UNVERIFIED | Theoretical: normalization avoids scale sensitivity | Same ceiling effect as spectral entropy; fallback to PR(W₀) |

---

## 4. Theoretical Interpretation

### 4.1 Mechanistic Explanation (Experiment-Verified)

No experiment-verified mechanistic explanation is available. Phase 4 was not executed.

The theoretical mechanism (pre-training shapes singular spectra → erank captures layer complexity
→ high-erank layers require higher-rank LoRA updates → PARA oracle discovers same structure)
remains at the level of theoretical motivation and indirect evidence from prior literature
(Aghajanyan 2021, AdaLoRA learned allocations, IFCLoRA structural predictor premise).

### 4.2 Unexpected Findings Analysis

No unexpected findings — no experimental data collected.

### 4.3 Connection to Existing Literature

| Our Finding | Related Work | Relationship | Citation |
|-------------|-------------|--------------|----------|
| PLANNED: erank(W₀) correlates with PARA oracle ranks | IFCLoRA (Zhang et al. 2026) | Extension: IFCLoRA uses activation-based IFC; erank is purely structural (zero calibration) | Zhang et al. 2026, arXiv |
| PLANNED: Layer-type (attention vs FFN) shows different optimal ranks | AdaLoRA (Zhang et al. 2023) | Consistent: AdaLoRA empirically assigns higher rank to FFN/deep layers | Zhang et al. 2023, arXiv:2303.10512 |
| PLANNED: Pre-training structure predicts adaptation rank | Aghajanyan et al. 2021 | Extension: d_90 per-layer variation establishes structural predictor premise | Aghajanyan et al. 2021 |
| PLANNED: erank provides zero-cost rank prediction | LAARA (Tripathi et al. 2026) | Differentiator: LAARA requires gradient warmup; erank requires only W₀ | Tripathi et al. 2026 |

### 4.4 Theoretical Contributions

1. **Zero-shot structural rank predictor hypothesis:** erank(W₀), computed from pretrained weights alone with no training/calibration, may provide a principled, task-agnostic per-layer LoRA rank predictor. If P1 is confirmed, this would be the first empirical validation of a purely structural (pre-training geometry) rank predictor.

2. **Cross-architecture generalization hypothesis:** Testing on BERT, DeBERTa, and ViT simultaneously addresses whether the erank-oracle correlation holds across attention mechanisms (absolute vs. disentangled) and modalities (NLP vs. vision). Pending Phase 4 results.

---

## 5. Experiment Results (Phase 6 Evidence)

### 5.1 Per-Hypothesis Results

| Hypothesis | Title | Gate | Result | Pass Rate | Key Insight |
|------------|-------|------|--------|-----------|-------------|
| **h-e1** | erank(W₀) correlation with PARA oracle ranks (existence proof) | MUST_WORK | NOT EVALUATED | N/A | Phase 4 not executed — no results |

### 5.2 Aggregate Metrics

| Metric | Value |
|--------|-------|
| **Total Hypotheses** | 1 (h-e1 only; h-m1, h-m2, h-m3 blocked on h-e1) |
| **Fully Validated** | 0 |
| **Partially Validated** | 0 |
| **Failed** | 0 |
| **Total Tasks Completed** | 0 / 15 |
| **SDD Compliance Rate** | N/A |

### 5.3 Optimal Hyperparameters

```yaml
# Planned hyperparameters (from 03_tasks.yaml / 02c_experiment_brief.md)
# NOT validated — Phase 4 not executed
planned:
  optimizer: AdamW
  lr_nlp: 2.0e-5
  lr_vit: 1.0e-4
  weight_decay: 0.01
  warmup_ratio: 0.06
  batch_size_nlp: 32
  batch_size_vit: 128
  epochs_nlp: 3
  epochs_vit: 5
  oracle_ranks: [4, 8, 16, 32, 64]
  baseline_rank: 8
  oracle_seeds: [42, 137]
  svd_precision: fp32
  erank_eps: 1.0e-10
```

### 5.4 Proven Components

| Component | Source Hypothesis | File | Reusable |
|-----------|-------------------|------|----------|
| erank formula (khanghy1000 gist pattern) | h-e1 (planned) | 02c_experiment_brief.md | YES — formula is task-agnostic |
| PARA oracle sweep design | h-e1 (planned) | 02c_experiment_brief.md | YES — reusable for h-m1/h-m2/h-m3 |
| PEFT dual-adapter oracle pattern | h-e1 (planned) | 03_architecture.md | YES — reusable across hypotheses |

### 5.5 Planned-vs-Actual Comparison

| Hypothesis | Planned Metric (03_tasks) | Planned Target | Actual Result (04_validation) | Deviation Type | Notes |
|------------|--------------------------|----------------|-------------------------------|----------------|-------|
| **h-e1** | Pearson r(erank, oracle_rank) | r ≥ 0.65, p < 0.05, ≥2/3 families | NOT MEASURED | IMPLEMENTATION_GAP | All 15 tasks in todo; experiment never started |

### 5.6 Key Figures Reference

| Figure | Source | Description | Suggested Paper Section |
|--------|--------|-------------|------------------------|
| erank vs oracle_rank scatter (BERT) | h-e1/figures/ (PLANNED) | Per-layer scatter with Pearson r annotation | Results §4.1 |
| erank vs oracle_rank scatter (DeBERTa) | h-e1/figures/ (PLANNED) | Per-layer scatter with Pearson r annotation | Results §4.1 |
| erank vs oracle_rank scatter (ViT) | h-e1/figures/ (PLANNED) | Per-layer scatter with Pearson r annotation | Results §4.1 |
| Layer-depth heatmaps (erank by depth) | h-e1/figures/ (PLANNED) | erank variation by layer index | Results §4.2 |

---

## 6. Limitations & Scope Boundaries

### 6.1 Principled Limitations

#### L1: Marginal Oracle ≠ Joint-Optimal Oracle

- **What:** PARA oracle optimizes rank per layer independently (all others frozen at r=8). This is not the globally optimal joint rank allocation.
- **Why This Matters:** Even if erank correlates with marginal oracle ranks, correlation with the true joint-optimal allocation may differ.
- **Root Cause:** Joint optimization over all layers simultaneously is computationally infeasible (5^72 combinations).
- **Impact on Claims:** P1 measures marginal oracle correlation only. P2 utility claim depends on whether erank-proportional allocation performs well end-to-end.
- **Why Acceptable:** Marginal oracle is the established proxy for optimal rank in prior work (AdaLoRA uses similar sweep logic). Any positive marginal correlation still provides actionable rank guidance.

#### L2: Experiment Scale and Duration

- **What:** Full oracle sweep requires ~2,160 training runs (~15 days on 5×H100 per Phase 3 estimate).
- **Why This Matters:** This is an unusually expensive experiment that may be subject to resource constraints or early stopping.
- **Root Cause:** Exhaustive per-layer oracle sweep is inherently O(n_layers × n_ranks × n_seeds × n_models).
- **Impact on Claims:** If experiment is abbreviated (fewer seeds, fewer models), statistical power for P1 is reduced.
- **Why Acceptable:** Phase 3 planning includes checkpoint-resume mechanism to handle interruption gracefully.

#### L3: erank Captures Spectrum Summary Only

- **What:** erank is a scalar summary of the full singular value distribution. The full spectrum contains more information.
- **Why This Matters:** Two layers with identical erank but different spectrum shapes may have different optimal LoRA ranks.
- **Root Cause:** erank = exp(Shannon entropy of normalized singular values) — collapses full distribution to one number.
- **Impact on Claims:** Upper bound on correlation r is constrained by information loss from scalar summary.
- **Why Acceptable:** Scalar summary is necessary for a zero-cost zero-data predictor. Full spectrum analysis would require task-specific oracle anyway.

### 6.2 Scope Conditions

| Condition | Results Hold | Results May Not Hold | Evidence |
|-----------|-------------|---------------------|----------|
| Encoder-only transformers (BERT, DeBERTa, ViT) | Within scope of h-e1 | Decoder-only LLMs (GPT, LLaMA) — not tested | Architectural differences in causal attention |
| Base-scale models (~86M–440M params) | BERT-base, DeBERTa-v3-base, ViT-base tested | Very large models (>7B) — SVD feasibility different | Computational constraints for fp32 SVD |
| Classification tasks (GLUE MNLI, CIFAR-10) | Tested in h-e1 | Generation tasks (translation, summarization) — PARA oracle requires classification metric | Oracle definition requires scalar accuracy metric |
| Pre-trained weights (before fine-tuning) | erank computed from W₀ only | Already fine-tuned models — erank of adapted weights different | erank must be from W₀, not ΔW |

### 6.3 Assumption Violation Impact

- **A3 (direction violated):** If Pearson r < 0 for ≥2/3 families, the hypothesis is falsified. Concentrated layers would need more rank to compensate — opposite mechanism. Requires complete reinterpretation.
- **A1 (erank CV < 0.05):** If erank shows same ceiling as spectral entropy, correlation is undetectable. Fallback to participation ratio PR(W₀) per Phase 2B A5 specification.
- **A5 (erank = spectral entropy effectively):** fp32 precision requirement and normalized formula should prevent this; confirmed by theory but not yet by experiment.

---

## 7. Future Work

### 7.1 From Untested Alternative Explanations

- **Alternative:** Concentrated-spectrum (low-erank) layers need MORE rank because dominant singular direction does not align with task-relevant signal.
  - **Why Not Yet Tested:** P1 tests positive direction only; falsification condition covers this but no experiment run.
  - **Proposed Experiment:** Run P1 and examine sign of r per model family; if r < 0, test this alternative via alignment study between LoRA update directions and W₀ singular directions.
  - **Expected Outcome:** If A3 is violated, this alternative explains the data better.

- **Alternative:** Oracle rank is primarily determined by layer depth (deep layers always get higher rank) independent of erank.
  - **Why Not Yet Tested:** Depth confound in P1 correlation — erank and layer depth both increase for FFN/deep layers.
  - **Proposed Experiment:** Partial correlation: r(erank, oracle_rank | layer_depth) controlling for depth.
  - **Expected Outcome:** Partial r should remain significant if erank provides information beyond depth.

### 7.2 From Unverified Assumptions

- **Assumption A2 (oracle stability):**
  - **Current Status:** UNVERIFIED
  - **Proposed Test:** Run 4 seeds per oracle point (not 2) for 10% of layers; measure variance in argmax rank.
  - **If Violated:** Use mode instead of argmax; increase to 4 seeds for full sweep.

- **Assumption A4 (task-agnosticity):**
  - **Current Status:** UNVERIFIED
  - **Proposed Test:** Run h-m3 (DeBERTa oracle for MNLI vs SST-2 comparison, Spearman ρ ≥ 0.7) — already planned.
  - **If Violated:** erank becomes task-specific predictor; zero-data advantage lost.

### 7.3 From Scope Extension Opportunities

- **Extension:** Decoder-only LLMs (LLaMA-3, Mistral-7B)
  - **Current Evidence Suggesting Feasibility:** IFCLoRA shows structural predictor generalizes across LLM architectures. Jonathan Chang's blog shows erank analysis on Llama-3-8B K/V matrices is feasible.
  - **Required Resources:** PARA oracle sweep for LLaMA is significantly more expensive (~70 layers × 5 ranks × 2 seeds × 3 tasks); would require multi-week GPU allocation.

- **Extension:** Quantized models (4-bit, 8-bit)
  - **Current Evidence Suggesting Feasibility:** QLoRA fine-tuning is increasingly common; whether erank of quantized W₀ correlates with oracle ranks is an open question.
  - **Required Resources:** Additional oracle sweep with quantized base models; fp32 SVD would need to be on dequantized weights.

---

## 8. Implications for Phase 6 (Paper Writing)

> ⚠️ **NOTE:** These implications are based on the PLANNED experiment design only.
> All claims below are CONDITIONAL on Phase 4 producing positive P1 results (r ≥ 0.65).
> Phase 6 MUST NOT use this document as-is — regenerate Phase 4.5 after Phase 4 completes.

### 8.1 Recommended Narrative Hook

**IF P1 SUPPORTED:** "We show that the effective rank of pretrained weight matrices — computed
in a single SVD pass with no training data — predicts per-layer optimal LoRA ranks with
Pearson r ≥ 0.65 across transformer architectures. This enables zero-cost, zero-data rank
allocation before any fine-tuning begins."

**Hook Strategy:** Zero-data contrast — every prior rank selection method (AdaLoRA, IFCLoRA,
LAARA) requires some form of training or calibration. erank requires only the pretrained weights.

**Why This Hook:** The practical value (no calibration overhead) is immediately comprehensible;
the empirical correlation claim is specific and falsifiable; cross-architecture generalization
(NLP + ViT) strengthens scope.

### 8.2 Key Insight (Experiment-Verified)

> PENDING — conditional on Phase 4. Expected insight if P1 confirmed:
> "Pre-training geometry, as captured by effective rank, encodes the same layer-complexity
> structure that the PARA oracle independently discovers through exhaustive rank sweep."

**Verification Evidence:** Pending Phase 4 execution (h-e1/04_validation.md).

### 8.3 Strongest Claims (Paper-Ready)

1. **[CONDITIONAL] erank(W₀) positively predicts PARA oracle ranks (P1)**
   - Evidence: Pearson r ≥ 0.65 for ≥2/3 families (pending Phase 4)
   - Confidence: 0.72 (pre-experiment estimate from Phase 2A)
   - Suggested Section: Results §4.1 — Primary correlation analysis

2. **[CONDITIONAL] Cross-architecture generalization: NLP encoders + ViT (P1)**
   - Evidence: BERT + DeBERTa + ViT all satisfy threshold (pending Phase 4)
   - Confidence: 0.60 (lower confidence for ViT cross-modal claim)
   - Suggested Section: Results §4.3 — Cross-architecture analysis

3. **[UNCONDITIONAL] Zero-cost structural predictor: single SVD pass, no calibration**
   - Evidence: erank formula definition — no training/data required by construction
   - Confidence: 1.00 (definitional property)
   - Suggested Section: Method §3.1 — erank computation

### 8.4 Honest Limitations (Must Include in Paper)

1. **Marginal oracle ≠ joint-optimal oracle**
   - Why Acceptable: Marginal oracle is computationally tractable and established proxy
   - Suggested Framing: "We validate against marginal per-layer oracle; joint allocation optimality is a stronger claim we leave to future work"

2. **Encoder-only models tested; decoder-only LLMs not evaluated**
   - Why Acceptable: Representative cross-architecture (NLP + Vision encoders) coverage
   - Suggested Framing: "Results hold for BERT-family and ViT-family models; generalization to autoregressive LLMs (LLaMA, GPT) is an important open question"

3. **erank is a scalar summary; full spectrum may provide more signal**
   - Why Acceptable: Scalar is necessary for zero-cost property; tradeoff is explicit
   - Suggested Framing: "erank trades full-spectrum information for a single closed-form scalar; this enables zero-data application but may reduce prediction precision"

### 8.5 Evidence Highlights (Most Persuasive)

1. **[PLANNED] Primary scatter plots: erank vs oracle_rank per model family**
   - Data: Pearson r with 95% bootstrap CI for BERT, DeBERTa, ViT
   - "So What": One figure shows the core claim across 3 architecturally distinct models
   - Suggested Figure/Table: Figure 1 (3-panel scatter, color-coded by layer type)

2. **[PLANNED] Oracle rank distribution by layer type (attention vs FFN)**
   - Data: Box plots of oracle ranks for attention Q/K/V/O vs FFN intermediate/output
   - "So What": Shows that erank-predicted layer hierarchy matches oracle-discovered hierarchy
   - Suggested Figure/Table: Figure 2 (box plots with Levene test p-values)

3. **[PLANNED] erank-proportional strategy vs baselines (P2)**
   - Data: Accuracy on MNLI/SST-2/CIFAR-10 for erank-strategy vs uniform-r8 vs oracle
   - "So What": Shows that the correlation translates to practical performance improvement
   - Suggested Figure/Table: Table 2 (performance comparison across datasets and models)

---

## Source Files Reference

| File | Hypothesis | Purpose |
|------|------------|---------|
| `h-e1/02c_experiment_brief.md` | h-e1 | Experiment design, variables, evaluation protocol |
| `h-e1/03_tasks.yaml` | h-e1 | Implementation tasks, planned metrics, SDD structure |
| `h-e1/04_checkpoint.yaml` | h-e1 | Phase 4 state (0/15 tasks completed — not executed) |
| `03_refinement.yaml` | main | Original hypothesis (P1–P5, mechanism, assumptions) |
| `verification_state.yaml` | pipeline | Sub-hypothesis statuses and pipeline routing |

**Input files per hypothesis:**
- `h-{id}/04_validation.md` — Experiment results, gate outcomes, lessons learned **[MISSING for h-e1]**
- `h-{id}/04_checkpoint.yaml` — Pass rate, failed checks, SDD metrics
- `h-{id}/03_tasks.yaml` — Planned tasks, expected metrics, success criteria
- `h-{id}/02c_experiment_brief.md` — Experiment design, variables, evaluation protocol

---

*Anonymous Research Pipeline — Evidence-refined hypothesis with theoretical interpretation*
*⚠️ REGENERATE THIS DOCUMENT after Phase 4 (h-e1) completes with actual experimental results.*
