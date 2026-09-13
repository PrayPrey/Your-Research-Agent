---
stepsCompleted: [step-00, step-01, step-02, step-03, step-04, step-05, step-06, step-07, step-08, step-09, step-10]
status: complete
completedAt: "2026-05-08T06:30:00Z"
hypothesis_id: H-SparsityLoRA-v1
research_mode: incremental
pipeline_project_id: 433e86d9-79bc-4277-b2d8-f422e0f4e65b
phase2b_task_id: 7dd0c52c-c1ed-4e5b-bf11-e9c3c53e33e5
---

# Verification Plan: SparsityLoRA — Activation Sparsity as a Pre-Training Structural Prior for LoRA Rank Allocation

**Date:** 2026-05-08
**Hypothesis ID:** H-SparsityLoRA-v1
**Confidence:** 0.72
**Total Hypotheses:** 5 (H-E1, H-M1, H-M2, H-M3, H-M4)

---

## 0. Established Facts & Scope Reduction

### 0.1 BUILD_ON (Do Not Re-Verify)

| Claim | Evidence |
|-------|----------|
| LoRA applies low-rank decomposition (rank r) to weight updates in pre-trained transformers | Hu et al. 2021 — 18,759 citations; HF PEFT production implementation |
| Pre-trained LLMs have low intrinsic dimension for fine-tuning (≥90% full performance in d << D subspace) | Aghajanyan et al. 2021 — MRPC: d=207 (SAID) |
| MLP activation sparsity varies significantly across transformer layers (layer-discriminating signal) | Li et al. 2022 (Lazy Neuron); Szatkowski et al. 2025; ReLU Strikes Back (Mirzadeh et al. 2023) |
| All existing adaptive rank methods (AdaLoRA, DyLoRA, ARD-LoRA, La-LoRA, Sensitivity-LoRA) require training-time signals | Literature review — AdaLoRA uses SVD importance during training |

### 0.2 PROVE_NEW (Phase 2B Targets)

| Claim | Evidence Gap |
|-------|-------------|
| Static activation sparsity as PRE-TRAINING predictor of LoRA rank has not been demonstrated | Act-LoRA (MDPI 2025) uses L2-norm for BINARY layer selection, not rank magnitude |
| Sparsity-guided rank allocation achieves ≥95% GLUE quality at ≤60% LoRA parameters | No prior work — core empirical contribution |

**Scope Reduction:** 67% (4/6 claims established → only 2 PROVE_NEW claims need verification)

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under LLaMA-3-8B inference on GLUE (SST-2 and MNLI), if layer-wise MLP activation sparsity (fraction of |activations| < 0.01, measured via forward hooks on 512 Alpaca calibration samples) is used to inversely allocate per-layer LoRA ranks under a fixed total parameter budget equal to 60% of uniform-r=16, then the sparsity-guided rank allocation achieves ≥95% of oracle joint allocation performance on both SST-2 and MNLI, because pre-training drives MLP layers toward low-dimensional activation attractors whose dimensionality is proxied by activation sparsity and determines the rank needed for quality fine-tuning.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in GLUE performance between sparsity-guided adaptive rank allocation and uniform LoRA rank at equivalent parameter count. Activation sparsity does not predict per-layer LoRA rank sensitivity (Pearson r > -0.2) and does not correlate with AdaLoRA's learned per-layer allocation (Kendall's tau < 0.2).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | GLUE (SST-2 + MNLI) (standard) | Direct evaluation benchmark used by LoRA, AdaLoRA, DyLoRA — enables apples-to-apples comparison. Two tasks with different supervision signals test cross-task transferability of sparsity-based rank allocation. |
| **Model** | LLaMA-3-8B | SiLU activations produce soft sparsity; 32 MLP layers provide sufficient per-layer diversity; commonly used in PEFT literature |

**Dataset Details:**
- Source: HuggingFace datasets (glue, sst2, mnli)
- Path: `datasets.load_dataset('glue', 'sst2')` / `datasets.load_dataset('glue', 'mnli')`
- Calibration: Alpaca (tatsu-lab/alpaca, 512 samples, primary) + WikiText-103 (stability check)

**Model Details:**
- Type: Decoder-only LLM with SiLU MLP gating
- Source: meta-llama/Meta-Llama-3-8B (HuggingFace)

### 1.4 Baseline Methods

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|-----------------|
| Uniform LoRA r=16 | SST-2: ~95%; MNLI: ~90.7% | GLUE SST-2, MNLI | Uniform rank ignores per-layer heterogeneity; uses maximum parameter budget |
| Uniform LoRA budget-matched (r=~10) | — | GLUE | Same rank everywhere under 60% budget; ignores layer heterogeneity |
| Random allocation (10 seeds) | — | GLUE | Random baseline; no structural prior |
| AdaLoRA (matched budget) | MNLI: 90.76% at 0.3M | GLUE MNLI | State-of-the-art adaptive but requires full training run — our approach achieves comparable with zero overhead |

**Best Baseline:** AdaLoRA MNLI 90.76% at 0.3M parameters

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Alpaca sparsity measurement transfers to GLUE task distributions | TEAL: stable sparsity across diverse inputs; PowerInfer: stable across LLaMA distributions | Narrows scope to task-specific calibration; reduces utility but doesn't kill hypothesis |
| A2 | SiLU near-zero activations (|a| < epsilon) correctly identify low-activation subspaces; epsilon=0.01 consistent | TEAL uses magnitude-based thresholding; PyTorch hook-based measurement well-established | Sparsity estimates are noisy; need to sweep epsilon and report sensitivity |
| A3 | Layer-wise sparsity is sufficient proxy for effective intrinsic dimensionality | Aghajanyan et al. 2021: intrinsic dimension is low; layer structure matters (SAID >> DID) | Sparsity insufficient; covariance-effective-rank or Jacobian spectral analysis needed |
| A4 | Marginal rank sensitivity correlates with joint rank sensitivity under shared budget | Computational necessity; common assumption in LoRA literature | Marginal doesn't predict joint optimum; need DyLoRA-style rank range training |
| A5 | Learned ΔW low-rank structure reflects intrinsic rank requirement, not rank constraint artifact | Hu et al. 2021: rank r=1 often sufficient; AdaLoRA finds low intrinsic rank in many layers | ΔW spectral decay is training-dynamics artifact; mechanistic claim collapses |

### 1.6 Research Gap & Novelty

**Gap:** No existing work uses static activation sparsity (measured in a single pre-training forward pass) as a continuous rank magnitude predictor for LoRA. Act-LoRA (MDPI 2025) is closest but performs binary layer selection using L2-norm, not sparsity-fraction-based rank magnitude allocation.

**Key Innovation:** "Sparsity as free approximation to AdaLoRA's learned allocation" — if Kendall's tau ≥ 0.4 between sparsity ranking and AdaLoRA's allocation, pre-training geometry encodes sufficient information for rank decisions without any training computation. Zero-gradient, zero-cost structural prior.

**Differentiation:**
- vs. AdaLoRA: training-time SVD (gradient-required) vs. one forward pass (zero overhead)
- vs. DyLoRA: trains across rank range (still gradient) vs. predicts rank BEFORE training
- vs. Act-LoRA: binary layer selection (L2-norm) vs. continuous rank magnitude (sparsity fraction)
- vs. Sensitivity-LoRA: second-order Hessian (gradient) vs. zero-order forward-pass statistics

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | BLOCKED |
| H-M2 | MECHANISM | MUST_WORK | H-E1 | BLOCKED |
| H-M3 | MECHANISM | MUST_WORK | H-M1, H-M2 | BLOCKED |
| H-M4 | MECHANISM | MUST_WORK | H-M3 | BLOCKED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Layer-wise MLP Activation Sparsity Existence and Stability**

**Statement**: Under LLaMA-3-8B in inference mode, if layer-wise MLP activation sparsity (fraction |a| < 0.01 via forward hooks on 512 Alpaca samples) is measured across all 32 MLP gate layers, then sparsity CV > 0.3 and Kendall's tau_calibration ≥ 0.6 (Alpaca vs. WikiText-103), because pre-training drives MLP layers toward differentiated sparse activation attractors (Lazy Neuron Phenomenon).

**Rationale**: This is the foundational existence check — without significant inter-layer sparsity variation and cross-distribution stability, the sparsity signal cannot serve as a discriminating rank allocation prior. H-E1 directly validates PROVE_NEW claim #1 and provides the input ranking for all H-M hypotheses.

**Variables**:
- Independent: Calibration dataset (Alpaca vs. WikiText-103), input length (128 vs. 512 tokens), epsilon threshold sweep {0.001, 0.01, 0.05, 0.1}
- Dependent: CV of per-layer sparsity across 32 layers; Kendall's tau (Alpaca vs. WikiText ranking); Kendall's tau (128-token vs. 512-token ranking)
- Controlled: LLaMA-3-8B model state (inference only, no gradient), same tokenizer and batch size

**Verification Protocol**:
1. Register register_forward_hook on all 32 MLP gate_proj output activations; process 512 Alpaca samples (batch=8, torch.no_grad()).
2. For each layer and epsilon, compute mean sparsity fraction; compute CV across 32 layers.
3. Repeat for WikiText-103 (512 samples) and both input lengths (128, 512 tokens); compute Kendall's tau for all pairs.
4. Sweep epsilon {0.001, 0.01, 0.05, 0.1}; check if CV > 0.3 and tau ≥ 0.6 hold across epsilon values.
5. Report: sparsity profile plot (32 layers), CV value, all pairwise Kendall's tau values, sensitivity table.

**Success Criteria**:
- Primary: CV > 0.3 AND Kendall's tau_calibration ≥ 0.6 at epsilon=0.01
- Secondary: Ranking stable across input lengths (tau_length ≥ 0.6); CV > 0.3 for at least 3 of 4 epsilon values

**Failure Response**:
- IF CV ≤ 0.3: PIVOT — sparsity not discriminating; explore gradient norm or activation magnitude as alternative signal
- IF tau < 0.6: EXPLORE — use task-specific calibration (GLUE validation sets); narrow hypothesis scope

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Section 1.6 (P1), Section 5 (sh1_existence)

---
**H-M1: Pre-training Drives Heterogeneous Sparse Activation Attractors**

**Statement**: Under LLaMA-3-8B, if layer-wise MLP activation sparsity profiles are measured across multiple calibration distributions (Alpaca, WikiText, SST-2, MNLI), then ICC > 0.75 and all pairwise Kendall's tau ≥ 0.6, because pre-training optimization pushes MLP layers toward fixed low-dimensional activation attractors that are intrinsic to the model architecture, not the input distribution.

**Rationale**: H-M1 tests the mechanistic claim that sparsity reflects architectural geometry rather than data statistics. High ICC across 4 diverse calibration sets would confirm that the sparsity pattern is a structural property of the pre-trained weights, providing theoretical grounding for using Alpaca as a task-agnostic calibration source.

**Variables**:
- Independent: Calibration distribution (Alpaca, WikiText-103, SST-2 val, MNLI val), each 512 samples
- Dependent: Per-layer mean sparsity vector (32-dim); pairwise Kendall's tau; ICC(2,1)
- Controlled: LLaMA-3-8B inference mode; epsilon=0.01; same hook pipeline as H-E1

**Verification Protocol**:
1. Run H-E1 measurement pipeline on 4 calibration datasets (Alpaca, WikiText, SST-2 val, MNLI val).
2. Compute all 6 pairwise Kendall's tau values between sparsity rankings.
3. Compute ICC(2,1) across 4 conditions using pingouin or scipy.
4. Compute Pearson r between sparsity ranking and ΔW spectral decay ratio from a reference SST-2 fine-tuned model (uniform r=16).
5. Report: heatmap of pairwise tau values; ICC with 95% CI; scatter plot of sparsity vs. ΔW spectral ratio.

**Success Criteria**:
- Primary: All 6 pairwise Kendall's tau ≥ 0.6 AND ICC > 0.75
- Secondary: Pearson r > 0.4 between sparsity ranking and ΔW spectral decay ratio

**Failure Response**:
- IF ICC ≤ 0.75 or some tau < 0.5: EXPLORE — characterize which distributions diverge; may require task-specific calibration

**Dependencies**: H-E1 (sparsity pipeline established, CV > 0.3 confirmed)

**Source**: Phase 2A Section 1.3 (Causal Step 1), Key Assumption A1

---
**H-M2: Layer-wise Sparsity Variation is Significant and Calibration-Stable**

**Statement**: Under LLaMA-3-8B with epsilon sensitivity sweep, if sparsity CV and inter-calibration Kendall's tau are computed for epsilon ∈ {0.001, 0.01, 0.05, 0.1}, then CV > 0.3 holds for at least 3 of 4 epsilon values and tau ≥ 0.6 holds for the best epsilon, because the layer-ordering of sparsity reflects architectural differences in MLP complexity that are robust to threshold choice.

**Rationale**: H-M2 directly addresses the SiLU soft-sparsity concern (Key Assumption A2) — if the sparsity signal is robust to epsilon, it demonstrates that the layer rank ordering is a stable structural property regardless of exact threshold. This de-risks the main objection from Prof. Rex regarding threshold sensitivity.

**Variables**:
- Independent: Epsilon threshold {0.001, 0.01, 0.05, 0.1}
- Dependent: CV per epsilon; Kendall's tau (Alpaca vs. WikiText) per epsilon; rank correlation between epsilon conditions
- Controlled: LLaMA-3-8B; Alpaca 512 samples; same hook pipeline

**Verification Protocol**:
1. From H-E1 data, extract per-layer sparsity for each epsilon value.
2. Compute CV for each epsilon; check if CV > 0.3 threshold holds.
3. Compute Kendall's tau (Alpaca vs. WikiText) for each epsilon; identify best epsilon.
4. Compute Kendall's tau between sparsity rankings at different epsilon values (rank stability across thresholds).
5. Report: sensitivity table (CV and tau per epsilon); select optimal epsilon for downstream use.

**Success Criteria**:
- Primary: CV > 0.3 for ≥ 3 of 4 epsilon values; Kendall's tau ≥ 0.6 for optimal epsilon
- Secondary: Kendall's tau ≥ 0.7 between epsilon=0.01 and epsilon=0.05 rankings (stable ordering)

**Failure Response**:
- IF CV collapses for most epsilon values: PIVOT — try activation magnitude (L1 norm per layer) as alternative proxy

**Dependencies**: H-E1 (raw sparsity data from hook pipeline)

**Source**: Phase 2A Section 1.3 (Causal Step 2), Key Assumption A2, open question on epsilon sensitivity

---
**H-M3: Activation Sparsity Negatively Predicts Per-Layer LoRA Rank Sensitivity**

**Statement**: Under LLaMA-3-8B fine-tuned on GLUE SST-2 and MNLI with uniform r=16, if per-layer joint rank sensitivity is measured (accuracy drop from budget-neutral rank reduction by Δr=2) and correlated with Alpaca sparsity rankings, then Pearson r ≤ -0.4 on sensitive layers (≥0.5% accuracy drop) for both tasks, Kendall's tau ≥ 0.4 between sparsity ranking and AdaLoRA's learned allocation, and sparsity explains ≥20% unique variance in ΔW spectral decay beyond gradient norm, because sparse layers operate in lower-dimensional subspaces requiring less rank for effective LoRA adaptation.

**Rationale**: H-M3 is the core mechanistic claim — the theoretical bridge between pre-training geometry and fine-tuning rank requirements. A negative correlation between sparsity and rank sensitivity, combined with alignment with AdaLoRA's learned allocation and ΔW spectral validation, would confirm that sparsity encodes the same structural information as gradient-based adaptive rank methods but at zero training cost.

**Variables**:
- Independent: Layer-wise activation sparsity (from H-E1); per-layer gradient Frobenius norm (from fine-tuned model)
- Dependent: Per-layer joint rank sensitivity (accuracy drop from Δr=2, budget-neutral); ΔW spectral decay ratio (top-4 SVs / Frobenius norm); AdaLoRA final per-layer rank allocation
- Controlled: LLaMA-3-8B; 60% parameter budget for sensitivity perturbation; 5 seeds for sensitivity measurement

**Verification Protocol**:
1. Fine-tune LLaMA-3-8B with uniform r=16 on SST-2 and MNLI (5 seeds each); record per-layer gradient Frobenius norms and compute ΔW = B×A post-training; run torch.linalg.svd to get spectral decay ratio.
2. For each of 32 layers: reduce rank by Δr=2 (redistribute Δr*cost to other layers proportionally); fine-tune and record accuracy drop; identify sensitive layers (≥0.5% drop).
3. Compute Pearson r between sparsity and joint sensitivity on sensitive layers (SST-2 and MNLI separately).
4. Run AdaLoRA at 60% budget on SST-2 and MNLI; extract final per-layer rank allocation; compute Kendall's tau vs. sparsity ranking.
5. Multiple regression: sparsity + gradient_norm + n_params → ΔW spectral decay; report sparsity beta coefficient, p-value, and unique variance (semipartial r²).

**Success Criteria**:
- Primary: Pearson r ≤ -0.4 on sensitive layers for BOTH SST-2 AND MNLI; Kendall's tau ≥ 0.4 vs. AdaLoRA
- Secondary: Sparsity beta significant (p < 0.05) with ≥20% unique variance in ΔW spectral decay beyond gradient norm

**Failure Response**:
- IF Pearson r > -0.2: PIVOT — mechanistic claim fails; explore gradient norm or covariance-effective-rank as alternative proxy
- IF tau < 0.2 vs. AdaLoRA: EXPLORE — task-conditioned rank sensitivity may require task-specific calibration

**Dependencies**: H-M1, H-M2 (stable sparsity profile confirmed; optimal epsilon selected)

**Source**: Phase 2A Section 1.3 (Causal Steps 3-4), Section 1.6 (P2), Key Assumptions A3, A4, A5

---
**H-M4: Sparsity-Guided Rank Allocation Achieves ≥95% Oracle Performance at 60% Parameter Budget**

**Statement**: Under LLaMA-3-8B fine-tuned on GLUE SST-2 and MNLI, if inverse-sparsity-proportional rank allocation is applied under a 60% parameter budget (vs. uniform r=16), then SparsityLoRA achieves ≥95% of oracle joint allocation performance (best of 20 random allocations) on both SST-2 and MNLI, and significantly outperforms uniform budget-matched (r=~10) and random allocation baselines (p < 0.05 over 5 seeds), because sparsity-guided allocation concentrates rank in low-sparsity (high-intrinsic-dimension) layers while reducing rank in high-sparsity layers.

**Rationale**: H-M4 is the core engineering claim — it validates that the mechanistic signal from H-M3 translates into an effective rank allocation strategy. Achieving ≥95% oracle at 60% parameter cost with no training overhead directly demonstrates the practical value of SparsityLoRA and enables the "free AdaLoRA approximation" narrative.

**Variables**:
- Independent: Rank allocation strategy (SparsityLoRA; uniform r=16; uniform budget-matched r=~10; random 10-seed; AdaLoRA 60% budget)
- Dependent: SST-2 accuracy; MNLI accuracy (matched + mismatched); % of oracle joint allocation; parameter count
- Controlled: LLaMA-3-8B; lr=2e-4, bs=16, epochs=3, warmup=0.03; 60% budget for all adaptive strategies; same 5 seeds

**Verification Protocol**:
1. Pre-compute oracle: run 20 random rank allocations under 60% budget; record best SST-2 and MNLI accuracy; define oracle as max for each task.
2. Fine-tune with 5 strategies (SparsityLoRA, uniform r=16, uniform r=~10, random 10-seed, AdaLoRA) under 60% budget; 5 seeds each; record SST-2 and MNLI accuracy.
3. Compute SparsityLoRA as % of oracle for SST-2 and MNLI; check ≥95% threshold on both.
4. t-test (or Mann-Whitney U if non-normal) between SparsityLoRA and uniform-matched, SparsityLoRA and random (using 5-seed results); report p-values and effect sizes (Cohen's d).
5. Report: table of all strategies × metrics; bar chart with error bars (5 seeds); oracle reference line.

**Success Criteria**:
- Primary: SparsityLoRA ≥ 95% oracle on BOTH SST-2 AND MNLI; p < 0.05 vs. uniform-matched and random on at least one metric
- Secondary: SparsityLoRA within 2% of AdaLoRA on both tasks (demonstrates "free approximation" quality)

**Failure Response**:
- IF ≥95% oracle fails on one task but not both: EXPLORE — report as task-specific finding; investigate if task-conditioned rank (DyLoRA) explains discrepancy
- IF fails both tasks: ABANDON SparsityLoRA as strategy; re-examine H-M3 correlation as fundamental prerequisite

**Dependencies**: H-M3 (sparsity-rank correlation confirmed; optimal epsilon selected for allocation)

**Source**: Phase 2A Section 1.3 (Causal Step 4), Section 1.6 (P3), Section 5 (sh3_comparison partially, core PoC verification)

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 ──┐
               ├──→ H-M3 → H-M4
H-E1 → H-M2 ──┘
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | CV > 0.3 AND tau_calibration ≥ 0.6 | PIVOT to alternative sparsity proxy |
| H-M1 | MUST_WORK | ICC > 0.75 AND all pairwise tau ≥ 0.6 | EXPLORE task-specific calibration |
| H-M2 | MUST_WORK | CV > 0.3 for ≥3 epsilon values; stable rankings | PIVOT to L1-norm alternative |
| H-M3 | MUST_WORK | Pearson r ≤ -0.4 (both tasks); tau ≥ 0.4 vs. AdaLoRA | PIVOT mechanism; explore alternatives |
| H-M4 | MUST_WORK | ≥95% oracle on BOTH SST-2 AND MNLI; p < 0.05 vs. baselines | EXPLORE task-specific; ABANDON if both fail |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1, H-M1, H-M2 (parallel) | ~3 days |
| Phase 2: Correlation | H-M3 (requires Phase 1 complete) | ~4 days |
| Phase 3: Allocation | H-M4 (requires H-M3 pass) | ~3 days |

**Total Duration:** ~10 days (sequential critical path)

---

## 4. Risk Analysis

### 4.1 Risk Register

| ID | Source | Description | Severity | Likelihood |
|----|--------|-------------|----------|------------|
| R1 | A1 | Alpaca sparsity does not transfer to GLUE task distributions (domain shift changes layer rankings) | MEDIUM | MEDIUM |
| R2 | A2 | SiLU epsilon threshold instability — soft-sparsity produces inconsistent layer rankings across epsilon values | HIGH | HIGH |
| R3 | A3 | Sparsity insufficient as dimensionality proxy — first-order statistic may not map to second-order geometric intrinsic dimension | HIGH | MEDIUM |
| R4 | A4 | Marginal vs. joint rank sensitivity divergence — marginal perturbation overestimates joint sensitivity for correlated layer groups | HIGH | MEDIUM |
| R5 | A5 | ΔW spectral decay as training-dynamics artifact — fast decay at r=16 may be universal (rank constraint) not layer-structural | MEDIUM | LOW |
| R6 | — | Task-conditioned rank sensitivity — SST-2 may be rank-insensitive (DyLoRA), providing insufficient DV variance for correlation analysis | HIGH | HIGH |

### 4.2 Risk-Hypothesis Mapping

| Risk | Source Assumption | Affected Hypotheses | Priority |
|------|------------------|---------------------|----------|
| R1 | A1: Alpaca→GLUE transfer | H-E1, H-M1, H-M3, H-M4 | MEDIUM |
| R2 | A2: Epsilon instability | H-E1, H-M2, H-M3 | HIGH |
| R3 | A3: Sparsity proxy | H-M3 (ΔW spectral claim) | HIGH |
| R4 | A4: Marginal≠joint sensitivity | H-M3 (correlation protocol) | HIGH |
| R5 | A5: ΔW artifact | H-M3 (spectral validation) | MEDIUM |
| R6 | — (task-conditioned) | H-M3, H-M4 | HIGH |

**Critical path risk:** R4 and R6 directly threaten H-M3, which is the prerequisite for H-M4. If both materialize, the core mechanistic claim is unverifiable.

### 4.3 Mitigation Strategies

**R1 — Alpaca Transfer Risk**
- Prevention: Include GLUE validation set (SST-2 val, MNLI val) as additional calibration sources in H-M1 cross-distribution analysis
- Detection: H-M1 Kendall's tau between Alpaca and SST-2/MNLI calibration rankings; alert if tau < 0.5
- Response: SCOPE — use task-specific calibration (GLUE val set) if Alpaca fails; reports utility reduction but does not invalidate hypothesis

**R2 — Epsilon Instability Risk**
- Prevention: Pre-register optimal epsilon = argmax CV(epsilon) on Alpaca before running any fine-tuning; commit before seeing downstream results
- Detection: H-M2 sensitivity table — if top-5 layer ranking changes > 3 positions between epsilon=0.01 and epsilon=0.05, flag R2
- Response: EXPLORE — report results for all epsilon values; if only one epsilon achieves CV > 0.3, narrow claim to that epsilon; add epsilon selection as hyperparameter

**R3 — Dimensionality Proxy Risk**
- Prevention: Include ΔW spectral decay ratio as concurrent mechanistic check in H-M3 (already in protocol)
- Detection: Pearson r between sparsity and ΔW spectral ratio < 0.3 on reference model (early warning before full correlation study)
- Response: PIVOT — if sparsity doesn't correlate with ΔW, try covariance-effective-rank (CER) or Jacobian spectral radius as alternative proxy

**R4 — Marginal/Joint Sensitivity Risk**
- Prevention: Protocol explicitly defines joint sensitivity (reduce layer rank, redistribute budget proportionally) not marginal (reduce only, no redistribution)
- Detection: Check if top-5 most sensitive layers cluster in same transformer block type (e.g., all attention projections) — indicates correlated sensitivity
- Response: EXPLORE — if marginal and joint disagree on top/bottom layers, run DyLoRA-style rank range sweep on top-10 layers to get empirical joint estimate

**R5 — ΔW Spectral Artifact Risk**
- Prevention: Train reference models at r=4, r=8, r=16; compare spectral decay ratio across ranks per layer
- Detection: If ΔW spectral decay ratios cluster near 0.9+ for all layers at r=16 (no inter-layer variance), flag R5
- Response: EXPLORE — use relative spectral decay (ratio across ranks) instead of absolute ratio; intrinsically controls for rank-constraint artifact

**R6 — Task-Conditioned Sensitivity Risk**
- Prevention: Analyze SST-2 and MNLI separately throughout; do not average; require both tasks to pass success criteria
- Detection: Count layers with ≥0.5% sensitivity drop on SST-2; if < 5 layers, SST-2 is rank-insensitive → flag R6
- Response: SCOPE — if SST-2 rank-insensitive, restrict H-M3 correlation claim to MNLI only; report SST-2 as negative result; H-M4 strategy comparison still valid for both tasks (performance doesn't require sensitivity correlation)

### 4.4 Risk Summary

| ID | Risk | Severity | Likelihood | Priority | Affected | Mitigation |
|----|------|----------|------------|----------|----------|------------|
| R1 | Alpaca→GLUE transfer | MEDIUM | MEDIUM | 3 | H-E1, H-M1, H-M3, H-M4 | Task-specific calibration fallback |
| R2 | SiLU epsilon instability | HIGH | HIGH | 1 | H-E1, H-M2, H-M3 | Pre-register epsilon via CV maximization |
| R3 | Sparsity dimensionality proxy | HIGH | MEDIUM | 2 | H-M3 | ΔW spectral concurrent check |
| R4 | Marginal≠joint sensitivity | HIGH | MEDIUM | 2 | H-M3 | Joint protocol + block clustering check |
| R5 | ΔW spectral artifact | MEDIUM | LOW | 4 | H-M3 | Multi-rank decay comparison |
| R6 | Task-conditioned sensitivity | HIGH | HIGH | 1 | H-M3, H-M4 | Separate task analysis; MNLI-only fallback |

**Critical (Priority 1): R2, R6** — Execute mitigation before any fine-tuning
**High (Priority 2): R3, R4** — Monitor during H-M3 execution
**Medium (Priority 3-4): R1, R5** — Track via H-M1 and spectral analysis

---

## 5. Execution Plan

### 5.1 Dependency Graph (DAG)
```
═══════════════════════════════════════════════════════════════
  DEPENDENCY GRAPH (DAG) — SparsityLoRA | 5 Hypotheses
═══════════════════════════════════════════════════════════════

[Level 0 — Foundation]
         H-E1
   (Existence: sparsity CV > 0.3, tau ≥ 0.6)
         │
    ┌────┴────┐
    ▼         ▼
[Level 1 — Parallel Mechanism Entry]
  H-M1      H-M2
(Arch.    (Epsilon
property)  stability)
    │         │
    └────┬────┘
         ▼
[Level 2 — Correlation]
        H-M3
  (Sparsity predicts
   rank sensitivity)
         │
         ▼
[Level 3 — Allocation Efficacy]
        H-M4
  (≥95% oracle at
   60% budget)
         │
         ▼
[Terminal — PoC Complete → Phase 5 Baseline Comparison]

═══════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M3 → H-M4  (or H-E1 → H-M2 → H-M3 → H-M4)
Parallelization: H-M1 ∥ H-M2 (both depend only on H-E1)
═══════════════════════════════════════════════════════════════

Gate Conditions:
  Gate 0 (H-E1): MUST_WORK — if fails, PIVOT entire approach
  Gate 1 (H-M1): MUST_WORK — if fails, EXPLORE task-specific calibration
  Gate 2 (H-M2): MUST_WORK — if fails, PIVOT to alternative sparsity proxy
  Gate 3 (H-M3): MUST_WORK — if fails, PIVOT mechanism; H-M4 blocked
  Gate 4 (H-M4): MUST_WORK — if fails, EXPLORE/ABANDON SparsityLoRA strategy
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Type | Prerequisites | Gate | Parallelizable |
|-------|-----------|------|---------------|------|----------------|
| 0 | H-E1 | EXISTENCE | None | MUST_WORK | — |
| 1 | H-M1 | MECHANISM | H-E1 | MUST_WORK | Yes (∥ H-M2) |
| 1 | H-M2 | MECHANISM | H-E1 | MUST_WORK | Yes (∥ H-M1) |
| 2 | H-M3 | MECHANISM | H-M1, H-M2 | MUST_WORK | No |
| 3 | H-M4 | MECHANISM | H-M3 | MUST_WORK | No |

**Key structural insight:** H-M1 and H-M2 share the same data from H-E1 (forward hook measurements). Both can be computed from the same hook run → zero additional GPU cost for parallelization. Only analysis code differs.

**Verification Phases:**
- Phase A (Foundation): H-E1 only → ~1 day (inference-only, no fine-tuning)
- Phase B (Structural Validation): H-M1 + H-M2 in parallel → ~2 days (inference-only)
- Phase C (Correlation): H-M3 → ~4 days (requires fine-tuning + sensitivity sweep)
- Phase D (Efficacy): H-M4 → ~3 days (requires fine-tuning with 5 strategies × 5 seeds)

### 5.3 Gantt Timeline
```
═══════════════════════════════════════════════════════════════════════════════════
  VERIFICATION TIMELINE — SparsityLoRA | 5 Hypotheses | 6 Weeks
═══════════════════════════════════════════════════════════════════════════════════

Phase / Hypothesis  │ W1-2      │ W3-4        │ W5          │ W6          │
────────────────────┼───────────┼─────────────┼─────────────┼─────────────┤
PHASE A: Foundation │           │             │             │             │
  H-E1 (Existence)  │ ██████████│             │             │             │
  [Gate A] ◆        │         ◆ │             │             │             │
────────────────────┼───────────┼─────────────┼─────────────┼─────────────┤
PHASE B: Structural │           │             │             │             │
  H-M1 (Arch.prop.) │           │ ██████████  │             │             │
  H-M2 (ε-stable)  │           │ ██████████  │             │             │
  [Gate B] ◆        │           │           ◆ │             │             │
────────────────────┼───────────┼─────────────┼─────────────┼─────────────┤
PHASE C: Correlation│           │             │             │             │
  H-M3 (Rank corr.) │           │             │ ██████████  │             │
  [Gate C] ◆        │           │             │           ◆ │             │
────────────────────┼───────────┼─────────────┼─────────────┼─────────────┤
PHASE D: Efficacy   │           │             │             │             │
  H-M4 (≥95% oracle)│           │             │             │ ██████████  │
  [Gate D] ◆        │           │             │             │           ◆ │
════════════════════╪═══════════╪═════════════╪═════════════╪═════════════╡
Legend: ██ = Active work  ◆ = Gate decision  [H-M1 ∥ H-M2 = parallel execution]
Total Duration: 6 weeks  |  Critical Path: H-E1 → H-M1 → H-M3 → H-M4
═══════════════════════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M3 → H-M4

| Node | Duration | Early Start | Early Finish | Float |
|------|----------|-------------|--------------|-------|
| H-E1 | 2 weeks | W1 | W2 | 0 (critical) |
| H-M1 | 2 weeks | W3 | W4 | 0 (critical) |
| H-M2 | 2 weeks | W3 | W4 | 0 (parallel with H-M1, no float) |
| H-M3 | 1 week | W5 | W5 | 0 (critical) |
| H-M4 | 1 week | W6 | W6 | 0 (critical) |

**Total Critical Path Duration: 6 weeks**

**Key Insights:**
- H-M1 and H-M2 run in parallel (both depend only on H-E1, share same sparsity hook data)
- No slack in the pipeline — any hypothesis delay directly extends total duration
- Gate A (end of H-E1) is the pivotal decision point: if H-E1 fails, all downstream work is blocked
- H-M3 is the most resource-intensive step (32-layer sensitivity sweep × 2 tasks × 5 seeds)

**Risk-adjusted duration (if R2 or R6 trigger EXPLORE):** +1–2 weeks for re-measurement or scope adjustment

### 5.5 Resource Summary

| Resource | Phases A-B | Phase C | Phase D | Total |
|----------|-----------|---------|---------|-------|
| GPU compute (A100 hrs) | ~8 hrs (inference only) | ~120 hrs (fine-tuning + sensitivity) | ~80 hrs (5 strategies × 5 seeds) | ~208 hrs |
| Researcher days | 4 days | 5 days | 3 days | ~12 days |
| GPU memory | 16 GB (A100 40GB, inference) | 40 GB (full fine-tuning) | 40 GB (full fine-tuning) | 40 GB peak |
| Storage | ~5 GB (hook data) | ~50 GB (checkpoints) | ~40 GB (checkpoints) | ~95 GB |

**Compute notes:**
- Phases A-B: inference-only (torch.no_grad()), minimal GPU hours
- Phase C: 32 layers × 2 tasks × sensitivity analysis = ~24 fine-tuning runs × 5 seeds = 240 runs total (major bottleneck)
- Phase D: 5 strategies × 2 tasks × 5 seeds = 50 fine-tuning runs + 20 oracle runs = 70 total
- Recommended: single A100 40GB; set CUDA_VISIBLE_DEVICES before each run

### 5.6 Execution Order

```
Step 1: Run H-E1 — measure layer-wise sparsity on Alpaca + WikiText-103 (W1-2)
        → Compute CV, Kendall's tau across epsilon sweep
        → [Gate A]: CV > 0.3 AND tau ≥ 0.6? → YES: proceed / NO: PIVOT

Step 2: Run H-M1 ∥ H-M2 (parallel) — structural validation + epsilon sensitivity (W3-4)
        → H-M1: add GLUE val calibration, compute ICC
        → H-M2: analyze epsilon sensitivity table, select optimal epsilon
        → [Gate B]: ICC > 0.75 AND CV stable for ≥3 epsilons? → YES: proceed / NO: PIVOT

Step 3: Run H-M3 — rank sensitivity correlation study (W5)
        → Fine-tune reference models (uniform r=16) on SST-2 + MNLI
        → Per-layer sensitivity sweep (32 layers × 2 tasks)
        → Compute Pearson r, Kendall's tau vs. AdaLoRA, multiple regression ΔW
        → [Gate C]: r ≤ -0.4 AND tau ≥ 0.4? → YES: proceed / NO: PIVOT mechanism

Step 4: Run H-M4 — allocation strategy comparison (W6)
        → Pre-compute oracle (20 random allocations)
        → Fine-tune 5 strategies under 60% budget (SparsityLoRA, uniform, budget-matched, random, AdaLoRA)
        → Compute % oracle, run statistical tests
        → [Gate D]: ≥95% oracle on BOTH tasks, p < 0.05 vs baselines? → YES: PoC COMPLETE / NO: EXPLORE/ABANDON

Final: PoC complete → proceed to Phase 5 Baseline Comparison
```

---

## 6. Dialectical Analysis

### 6.1 Analysis

The central dialectical tension in SparsityLoRA is between **structural determinism** (thesis: pre-training geometry encodes rank requirements) and **task-conditioned contingency** (antithesis: rank sensitivity depends on the fine-tuning task, making any task-agnostic prior insufficient). The verification plan resolves this tension through sequential gating: Phase A-B tests whether the structural premise holds at all before investing in Phase C-D correlation analysis. This is epistemically sound — neither commits resources based on theoretical assumption alone, nor dismisses the hypothesis without empirical test.

### 6.2 Thesis

**Core Claim:** Pre-training activation sparsity is a valid zero-cost structural prior for per-layer LoRA rank allocation in LLaMA-3-8B.

**Supporting Evidence:**
1. Lazy Neuron Phenomenon (Li et al. 2022; Szatkowski et al. 2025): pre-training creates heterogeneous sparse activation patterns across MLP layers — a structural property, not an input artifact
2. SAID theory (Aghajanyan et al. 2021): pre-trained models have low intrinsic fine-tuning dimension that is layer-structure-dependent — sparse layers have lower effective dimension
3. Existing PEFT infrastructure (HF PEFT rank_pattern, AdaLoRA reference): enables direct implementation and comparison at zero additional engineering cost

**Strengths:**
- Grounded in established theory with clear causal chain: pre-training geometry → sparse attractors → low intrinsic dimension → low rank requirement
- Zero training overhead: single inference pass vs. full fine-tuning run for AdaLoRA
- Directly falsifiable with pre-specified thresholds on public benchmark (GLUE)
- Opens "structural priors for PEFT" as a new research direction

**Expected Outcomes:**
- P1 (secondary): CV > 0.3, tau_calibration ≥ 0.6 — sparsity is a stable structural signal
- P2 (primary): Pearson r ≤ -0.4 on sensitive layers; Kendall's tau ≥ 0.4 vs. AdaLoRA; ≥20% unique variance in ΔW spectral decay
- P3: SparsityLoRA ≥ 95% oracle at 60% budget, p < 0.05 vs. uniform/random

### 6.3 Antithesis

**Null Hypothesis (H0):** There is no significant difference in GLUE performance between sparsity-guided adaptive rank allocation and uniform LoRA at equivalent parameter count. Activation sparsity does not predict per-layer LoRA rank sensitivity (Pearson r > -0.2) and does not correlate with AdaLoRA's learned per-layer allocation (Kendall's tau < 0.2).

**Counter-Arguments:**
1. **SiLU epsilon arbitrariness:** Unlike ReLU, SiLU has no natural zero — epsilon selection is arbitrary and could produce inconsistent layer rankings, inflating or deflating the apparent correlation
2. **Task-conditioned rank insensitivity:** DyLoRA shows SST-2 is rank-insensitive (r=1 to r=8 produce similar results) — if the DV (sensitivity) has near-zero variance, Pearson r is undefined, not evidence of mechanism failure
3. **First-order statistic vs. second-order geometry:** Sparsity fraction is a scalar statistic; intrinsic dimensionality is a geometric property of the weight Jacobian subspace — the theoretical mapping is indirect and potentially unreliable

**Conditions Under Which H0 Would Be Supported:**
- H-E1: CV ≤ 0.3 (sparsity not discriminating) or tau < 0.6 (not an architectural property)
- H-M3: Pearson r > -0.2 on both SST-2 and MNLI sensitive layers
- H-M3: Kendall's tau < 0.2 vs. AdaLoRA allocation (no relationship to learned optimal)
- H-M4: SparsityLoRA < 95% oracle on either task (allocation strategy ineffective)

### 6.4 Synthesis

**Resolution Path:** The verification plan addresses the dialectic through sequential hypothesis testing with pre-specified gates:

1. **Gate A (H-E1):** Directly tests whether sparsity is a discriminating architectural signal (antithesis challenge #1). If CV ≤ 0.3, the entire approach pivots before any fine-tuning.
2. **Gates B1/B2 (H-M1/M2):** Cross-distribution ICC test answers whether sparsity is distribution-specific artifact; epsilon sensitivity table addresses threshold arbitrariness.
3. **Gate C (H-M3):** Three-stream evidence (Pearson r + Kendall's tau vs. AdaLoRA + ΔW spectral regression) reduces single-measurement vulnerability. Separate SST-2/MNLI analysis directly handles task-conditioned sensitivity.
4. **Gate D (H-M4):** Performance outcome test independent of mechanistic correlation — practical value can be demonstrated even if theoretical mechanism is imprecise.

**Nuanced Outcome Possibilities:**
- **Full Support** (all gates pass): Thesis validated — sparsity as task-agnostic structural prior for rank allocation
- **Partial Support** (MNLI passes, SST-2 rank-insensitive): Refined thesis — "sparsity predicts rank in rank-sensitive tasks; SST-2 is rank-insensitive as DyLoRA predicted"
- **No Mechanistic but Performance Success** (H-M3 fails, H-M4 passes): "Sparsity-guided allocation works empirically even without correlation explanation" — practically useful, theoretically incomplete
- **Antithesis Supported** (H-E1 or H-M3 fails both tasks): Pivot to gradient-based proxy (gradient norm) or alternative structural prior (activation magnitude, covariance rank)

### 6.5 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Verification Resolution |
|--------|----------------|---------------------|------------------------|
| Existence | CV > 0.3, stable ranking across distributions | Artifact of epsilon threshold or input distribution | H-E1: direct CV test; H-M1: 4-dataset ICC |
| Mechanism | Sparsity → intrinsic dim → rank requirement | First-order ≠ second-order geometry; task-conditioned | H-M3: three-stream evidence + separate task analysis |
| Calibration transfer | Alpaca generalizes to GLUE | Domain-specific activation patterns | H-M1: GLUE val set included as calibration condition |
| Epsilon stability | Ranking robust to threshold | SiLU soft-sparsity makes ranking arbitrary | H-M2: epsilon sensitivity table; pre-register optimal epsilon |
| Allocation efficacy | ≥95% oracle at 60% budget | Marginal improvement indistinguishable from noise | H-M4: 5 seeds, statistical tests, oracle reference |
| Generalization | Structural prior for all PEFT | LLaMA-3-8B specific artifact | Acknowledged scope limitation; follow-up work |

**Overall Robustness Score: MEDIUM-HIGH**
- Strong theoretical grounding; well-specified falsification criteria
- Main risk: task-conditioned sensitivity limiting full-scope validation
- Mitigation: MNLI-only fallback preserves scientific contribution even under partial failure

**Confidence in Verification Plan:** 0.78 (synthesis confidence — higher than initial 0.72 due to gate structure addressing antithesis concerns)

---

## 7. Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** SparsityLoRA — layer-wise MLP activation sparsity as zero-cost pre-training structural prior for LoRA rank allocation in LLaMA-3-8B on GLUE (SST-2, MNLI).
- **ID:** H-SparsityLoRA-v1 | **Confidence:** 0.72 | **Mode:** Incremental (67% scope reduction)

**Verification Structure:**
- Sub-Hypotheses: 5 total — H-E1 (Existence), H-M1–H-M4 (Mechanism × 4 causal steps)
- Phases: 4 phases (A: Foundation, B: Structural, C: Correlation, D: Efficacy) over 6 weeks
- Critical Gates: 5 decision points (all MUST_WORK); H-M1 ∥ H-M2 parallelizable

**Risk Assessment:** MEDIUM-HIGH
- Priority 1 risks: R2 (SiLU epsilon instability), R6 (task-conditioned rank sensitivity — SST-2 may be rank-insensitive)
- Key mitigation: Pre-register epsilon via CV maximization; analyze SST-2 and MNLI separately throughout

**Immediate Action:** Begin Phase A — H-E1 sparsity measurement (inference-only, ~1 day GPU setup)

### 7.2 Final Summary

**What This Plan Achieves:**
- Decomposes H-SparsityLoRA-v1 into 5 falsifiable sub-hypotheses covering the full 4-step causal chain
- Provides early-exit gates preventing wasted compute if foundational assumptions fail
- Identifies 6 risks with concrete detection criteria and response strategies
- H-M1 ∥ H-M2 parallelization reduces Phase B from 4 to 2 weeks at zero extra GPU cost
- Three-stream mechanistic evidence in H-M3 (correlation + AdaLoRA comparison + ΔW spectral) ensures robustness

**What This Plan Does NOT Cover:**
- Cross-architecture generalization (Mistral, Gemma) — saved for follow-up work
- Full baseline comparison (Ours vs. baseline on all GLUE tasks) — deferred to Phase 5
- QLoRA/quantized base models — out of scope for this PoC

### 7.3 Conclusions

**Key Achievements:**
- 5 sub-hypotheses covering existence (H-E1) and full 4-step causal chain (H-M1–H-M4)
- H0 directly addressed: antithesis (task-conditioned sensitivity) drives MNLI fallback scope design
- Sequential gate structure: Phase A-B are inference-only, protecting ~200 GPU-hrs of Phase C-D investment

**Verification Execution Order:**
- Phase A (W1-2): H-E1 — sparsity CV + stability check [Gate A: CV > 0.3, tau ≥ 0.6]
- Phase B (W3-4): H-M1 ∥ H-M2 — ICC cross-distribution + epsilon sensitivity [Gate B: ICC > 0.75]
- Phase C (W5): H-M3 — rank sensitivity correlation + ΔW spectral regression [Gate C: r ≤ -0.4, tau ≥ 0.4]
- Phase D (W6): H-M4 — 5-strategy comparison + oracle benchmark [Gate D: ≥95% oracle, p < 0.05]

**Critical Decision Points:**
1. Gate A (H-E1 fail → PIVOT): reassess entire sparsity-as-proxy approach; try gradient norm
2. Gate B (H-M1 fail → EXPLORE): use GLUE-task-specific calibration; Gate B (H-M2 fail → PIVOT): try L1-norm
3. Gate C (H-M3 fail both tasks → PIVOT mechanism): try covariance effective-rank proxy
4. Gate D (H-M4 fail both → ABANDON SparsityLoRA strategy): document as negative result

**Open Questions (from Phase 2A):**
- Does epsilon threshold selection substantially affect sparsity rankings? (addressed by H-M2)
- Is marginal rank sensitivity a sufficient proxy for joint sensitivity? (addressed by H-M3 protocol)
- Does the sparsity–AdaLoRA allocation correlation hold when both evaluated on same task? (addressed by H-M3)
- Is ΔW spectral decay mechanistically distinguishable from gradient magnitude effects? (addressed by H-M3 multiple regression)

**Recommendations:**
1. **Immediate:** Set CUDA_VISIBLE_DEVICES to single empty GPU; pre-register epsilon selection criterion (CV maximization on Alpaca) before running any fine-tuning
2. **Phase B:** Run H-M1 and H-M2 from the same sparsity hook data collected in H-E1 — zero additional measurement cost
3. **Phase C:** If SST-2 has < 5 sensitive layers, immediately apply MNLI-only fallback scope for H-M3 (do not wait for end of phase)
4. **Phase D:** Pre-compute oracle (20 random allocations) before fine-tuning SparsityLoRA to avoid look-ahead bias

### 7.4 Appendices

**A. Phase 2A Source Reference**
- Source: `docs/youra_research/20260508_scope/03_refinement.yaml` (v10.0.0, H-SparsityLoRA-v1)
- Discussion: 15 exchanges, 6 agents, convergence at Exchange 15 (all 6 criteria met)
- Established facts reused (DO NOT re-verify): LoRA basics, intrinsic dimension (SAID), MLP sparsity literature, training-time adaptive rank methods

**B. MCP Tool Usage Summary**
- `mcp__clearThought__scientificmethod`: 4 inquiry flows (H-E1, H-M1/M2, H-M3/M4 — hypothesis + experiment stages)
- `mcp__clearThought__collaborativereasoning`: 1 session (6-risk expert panel)
- `mcp__clearThought__structuredargumentation`: 3 arguments (thesis, antithesis, synthesis)
- Total MCP calls: 10 | Mode: Incremental (Phase 2A pre-seeded)

**C. Hypothesis Count Rationale**
- causal_chain_count = 4 → H-M1, H-M2, H-M3, H-M4 (one per causal step)
- H-M1/H-M2 split: Steps 1-2 are both infrastructure/existence-type and parallelizable; Steps 3-4 require fine-tuning
- No H-C: condition_requires_verification = false (scope boundaries are descriptive, not requiring dedicated hypothesis testing)

---

## 8. State & Tasks

### 8.1 Verification State

✅ `verification_state.yaml` created at: `docs/youra_research/20260508_scope/verification_state.yaml`
- Schema version: 3.5
- Main hypothesis: H-SparsityLoRA-v1
- Sub-hypotheses: 5 (H-E1: READY; H-M1, H-M2, H-M3, H-M4: NOT_STARTED)
- Pipeline project ID: 433e86d9-79bc-4277-b2d8-f422e0f4e65b
- Hypothesis task mapping: populated (all 5 tasks created in Archon)
- Workflow status: ACTIVE → current_phase: Phase 2C
- Phase 5: skip_baseline_comparison = true (per module.yaml)

### 8.2 Pipeline Tasks

✅ Phase 2B task `7dd0c52c-c1ed-4e5b-bf11-e9c3c53e33e5` → status: **done**

No Phase 2C pipeline-level task existed to mark as doing (hypothesis-level tasks handle Phase 2C tracking per module task_management.archon_scope = "hypothesis_only").

### 8.3 Hypothesis Tasks

| Hypothesis | Archon Task ID | Status |
|-----------|---------------|--------|
| H-E1 | 723cd5b0-c0be-49fd-9e5a-79716304dd6e | todo |
| H-M1 | c202e016-70e5-443c-9bb0-dcdad5dbbb6c | todo |
| H-M2 | 7e5e5790-1d1f-4a49-9c18-21b08b43932c | todo |
| H-M3 | bacaf730-66a5-498f-876f-caef3dd871e9 | todo |
| H-M4 | 8f73882c-c46d-4dc3-8c9c-f30f9ecf123f | todo |

Feature label: `hypothesis-verification-sparsitylora-v1`
Project: Anonymous Pipeline: Dynamic LoRA Rank via Layer Activation Sparsity for Efficient Fine-Tuning

---

*Generated by YouRA Phase 2B (v6.0) | 2026-05-08*
