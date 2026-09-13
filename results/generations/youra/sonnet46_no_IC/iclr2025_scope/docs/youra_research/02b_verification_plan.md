---
title: "Verification Plan: Effective Rank as Zero-Shot LoRA Rank Predictor"
hypothesis_id: "H-erank-v1"
date: "2026-08-05"
status: complete
completedAt: "2026-08-05T00:00:00"
stepsCompleted:
  - step-00-init-environment
  - step-01-init-parsing
  - step-02-input-hypothesis
  - step-03-hypothesis-generation
  - step-04-hypothesis-inventory
  - step-05-risk-analysis
  - step-06-dependency-graph
  - step-07-timeline-planning
  - step-08-dialectical-analysis
  - step-09-summary
  - step-10-finalize
---

# Verification Plan: Effective Rank as Zero-Shot LoRA Rank Predictor

**Date:** 2026-08-05
**Hypothesis ID:** H-erank-v1
**Confidence:** 0.72
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under pre-trained transformer models {BERT-base-uncased, DeBERTa-v3-base, ViT-base-patch16-224} with adequate fine-tuning (≥3 epochs NLP on full GLUE MNLI 392k samples; ≥5 epochs ViT on CIFAR-10 50k samples), if per-layer effective rank erank(W₀) = exp(H(σ/‖σ‖₁)) of each weight matrix W₀ is computed from pre-trained weights (fp32 precision, before any fine-tuning), then it demonstrates statistically significant positive Pearson correlation (r ≥ 0.65, one-tailed H₁: α > 0) with per-layer marginal PARA oracle ranks (argmax over r ∈ {4,8,16,32,64} of validation accuracy, all non-target layers frozen at baseline r=8) across ≥2 of the 3 model families, because effective rank captures the geometric complexity of each layer's pre-training representation — layers with spread-out singular spectra have more non-dominated directions and require higher-rank LoRA updates to capture task-relevant signal.

### 1.2 Alternative Hypothesis (H0)

There is no significant positive correlation between erank(W₀) and PARA oracle ranks (Pearson r ≤ 0 for ≥2/3 model families, or 0 < r < 0.65 for all 3 families).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | GLUE MNLI + SST-2 (NLP); CIFAR-10 (Vision) (standard) | MNLI (392k samples) provides sufficient training data for stable 3-epoch oracle runs. SST-2 enables task-agnosticity validation (second NLP task). CIFAR-10 (50k samples) provides cross-architecture validation with ViT-base. All are standard classification benchmarks with fixed train/validation splits. |
| **Model** | BERT-base-uncased, DeBERTa-v3-base, ViT-base-patch16-224 | Three architecturally distinct models: BERT (encoder, absolute position), DeBERTa (encoder, disentangled attention), ViT (vision encoder, patch attention). Testing ≥2/3 families validates cross-architecture generalization. All models are base-scale — SVD computation feasible in fp32 on CPU. |

**Dataset Details:**
- Source: HuggingFace datasets (glue, cifar10)
- Path: HuggingFace Hub — no local download required

**Model Details:**
- Type: pretrained_transformer
- Source: HuggingFace Hub (bert-base-uncased, microsoft/deberta-v3-base, google/vit-base-patch16-224)

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| Uniform LoRA r=8 (Hu et al. 2021) | MNLI 90.0 (DeBERTa-v3-base) | GLUE MNLI |
| AdaLoRA (Zhang et al. 2023) | MNLI 90.4 (DeBERTa-v3-base, 0.3M params) | GLUE MNLI |
| IFCLoRA (Zhang et al. 2026) | +1.2% over uniform LoRA on ARC-Challenge | ARC, BoolQ, HellaSwag |
| LAARA (Tripathi et al. 2026) | MMLU 67.2 vs LoRA 65.8 (+1.4%) | MMLU, GSM8K, HumanEval |
| PARA oracle (upper bound) | Per-layer marginal sweep — theoretical upper bound | All families |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | erank(W₀) shows sufficient variation across layers (CV > 0.05) within each model family | h-e1 data: ViT erank variation by depth confirmed; BERT attention vs FFN Levene p=0.0001 | Correlation undetectable; fallback to participation ratio PR(W₀) |
| A2 | Marginal PARA oracle produces stable rank assignments (consistent across 2 random seeds) | GLUE benchmarks have sufficient validation set size for stable accuracy estimates | Oracle ranks noisy; run each training with 2 seeds, use mean accuracy for argmax |
| A3 | Positive direction: erank(W₀) positively predicts oracle rank (not negatively) | High-erank → spread singular directions → more non-dominated signal → higher rank needed | Pearson r < 0 — direction inverted; hypothesis falsified in stated form |
| A4 | erank-oracle correlation generalizes across NLP tasks (task-agnosticity): MNLI and SST-2 oracle ranks agree at Spearman ρ ≥ 0.7 | IFCLoRA shows structural predictor generalizes across tasks; Aghajanyan 2021: intrinsic dim partially task-independent | erank is task-SPECIFIC predictor; scope must be reduced to per-task estimation |
| A5 | erank(W₀) captures relevant structural property better than spectral entropy H(W₀) (h-e1 failed metric) | erank = exp(H(normalized_singular_values)) uses normalized distribution; wider dynamic range than spectral entropy | erank shows same ceiling effect as spectral entropy; fallback to participation ratio PR(W₀) |

### 1.6 Research Gap & Novelty

**Research Gap:** No published study has measured Pearson/Spearman correlation between erank(W₀) and PARA oracle ranks per layer. No zero-data, task-agnostic, purely structural LoRA rank predictor exists.

**Key Innovation:** erank(W₀) provides zero-cost (single SVD, no training, no calibration data) per-layer rank prediction — qualitatively different from all prior work:
- AdaLoRA requires full training run for rank discovery
- IFCLoRA requires calibration set from target task (not fully task-agnostic)
- LAARA requires gradient computation in training warmup
- PiSSA/LoRA-XS use W₀ SVD for initialization only — rank still fixed

erank requires only pretrained weights — available at model load time before any task data.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: erank(W₀)–Oracle Rank Positive Correlation (Existence)**

**Statement**: Under pre-trained transformers {BERT-base-uncased, DeBERTa-v3-base, ViT-base-patch16-224}, if erank(W₀) = exp(H(σ/‖σ‖₁)) is computed fp32 before fine-tuning, then Pearson r(erank, oracle_rank) ≥ 0.65 (one-tailed p < 0.05) in ≥2/3 model families, because layers with spread-out singular spectra (high erank) have more non-dominated directions requiring higher-rank LoRA updates.

**Rationale**: This is the foundational existence proof. If erank does not correlate with oracle ranks, the entire hypothesis collapses. Pearson r ≥ 0.65 is the minimum threshold for the correlation to be practically meaningful as a rank predictor. Phase 2A h-e1 data provides preliminary evidence (ViT depth variation, BERT Levene p=0.0001).

**Variables** (from Phase 2A):
- Independent: erank(W₀) per weight matrix (continuous, [1, min(d_in,d_out)], fp32 SVD)
- Dependent: PARA oracle rank per layer (ordinal: {4,8,16,32,64}); Pearson r per model family
- Controlled: Baseline r=8 for non-target layers; training hyperparameters fixed; fp32 SVD precision

**Verification Protocol** (P1 from Phase 2A):
1. Compute erank(W₀) for all weight matrices (~72-80 per model) via torch.linalg.svdvals fp32
2. Run PARA oracle: for each layer, train LoRA r∈{4,8,16,32,64} on full GLUE MNLI (392k, ≥3 epochs) or CIFAR-10 (50k, ≥5 epochs), all other layers at r=8
3. Record oracle_rank = argmax_{r} validation_accuracy(r); run 2 seeds per oracle point, use mean accuracy
4. Compute Pearson r per model family with bootstrap 95% CI (n=1000); one-tailed test H₁: r > 0, α=0.05
5. Success: r ≥ 0.65 for ≥2/3 families (p < 0.05); also record participation ratio PR(W₀) as alternative metric

**Success Criteria** (PoC):
- Primary: Pearson r ≥ 0.65 (one-tailed p < 0.05) for ≥2/3 families
- Secondary: erank-proportional assignment (P2) within 1% of oracle accuracy AND above uniform r=8

**Failure Response**:
- IF r < 0 for ≥2/3 families: ABANDON (direction wrong — fundamental theoretical error)
- IF 0 < r < 0.65 for all 3 families: PIVOT to participation ratio PR(W₀) as alternative metric
- IF only 1 family passes: SCOPE (narrow claim to specific architecture family)

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Section 1.6 (P1, primary prediction) + Section 5 (sh1_existence)

---

**H-M1: Pre-Training Shapes Layer-Specific Singular Spectra (Mechanism Step 1)**

**Statement**: Under pre-trained transformers, if layers are grouped by erank tercile (bottom vs top 33%) or by layer type (attention vs FFN), then Levene test on PARA oracle ranks within groups is significant (p < 0.05) in ≥2/3 model families, because pre-training via gradient descent on large corpora shapes singular value distributions such that complex layers (deep FFN, cross-modal attention) develop spread-out spectra (high erank) while simpler layers develop concentrated spectra (low erank).

**Rationale**: This mechanism step validates that the pre-training process creates meaningful differentiation in erank across layers — a prerequisite for erank to predict oracle ranks. h-e1 ViT depth variation (entropy increases 4.27→6.44) and BERT Levene p=0.0001 provide preliminary evidence that this structure exists in pretrained models.

**Variables**:
- Independent: erank(W₀) tercile membership (bottom/top 33%); layer type (attention vs FFN)
- Dependent: PARA oracle rank distribution per group; Levene statistic p-value
- Controlled: Same oracle runs as H-E1 (shared compute); fixed training hyperparameters

**Verification Protocol** (P4 from Phase 2A):
1. Using oracle ranks from H-E1 runs (shared data), split layers by erank tercile per model family
2. Run Levene test on oracle rank distributions: bottom-33% erank group vs top-33% erank group
3. Also run Levene test with layer-type grouping (attention Q/K/V/O vs FFN intermediate/output)
4. Record p-values for both groupings per model family; success requires p < 0.05 in ≥2/3 families for either grouping
5. Secondary: compute erank CV per model family to confirm variation >0.05 (validates A1)

**Success Criteria** (PoC):
- Primary: Levene p < 0.05 in ≥2/3 families (tercile OR layer-type grouping)
- Secondary: erank CV > 0.05 within each model family (assumption A1 validated)

**Failure Response**:
- IF Levene p > 0.05 for all families in both groupings: PIVOT — erank lacks discriminative power; test participation ratio PR(W₀) grouping
- IF CV < 0.05 for any family: PIVOT — metric ceiling; switch to PR(W₀) for that family

**Dependencies**: H-E1 (requires oracle runs to provide oracle rank data)

**Source**: Phase 2A Section 1.3 (Causal Step 1) + Section 1.6 (P4)

---

**H-M2: High-erank Layers Exhibit Larger Relative Adaptation Magnitude (Mechanism Step 2)**

**Statement**: Under pre-trained transformers fine-tuned with LoRA at oracle rank per layer, if relative adaptation magnitude ‖ΔW_opt‖_F / ‖W₀‖_F is computed per layer after convergence, then it demonstrates Spearman ρ ≥ 0.5 with erank(W₀) in ≥2/3 model families, because high-erank matrices have singular mass spread across many orthogonal directions, requiring larger-magnitude LoRA updates to capture task-relevant signal distributed across non-dominated directions.

**Rationale**: This mechanism step tests whether high-erank layers actually undergo larger adaptation — the mechanistic link between erank (structural complexity) and oracle rank (optimization preference). If adaptation magnitude is decoupled from erank, the theoretical mechanism is incomplete even if the correlation (H-E1) holds empirically.

**Variables**:
- Independent: erank(W₀) per layer (from H-E1 computation)
- Dependent: ‖ΔW_opt‖_F / ‖W₀‖_F per layer at oracle rank (relative adaptation magnitude)
- Controlled: LoRA rank set to oracle rank per layer; same training hyperparameters as H-E1

**Verification Protocol** (P3 from Phase 2A):
1. After oracle training runs (H-E1), record learned LoRA adapters A, B per layer at oracle rank r_l
2. Compute ΔW = B×A (full update matrix); record ‖ΔW‖_F / ‖W₀‖_F per layer at convergence
3. Compute Spearman ρ(erank(W₀), ‖ΔW‖_F/‖W₀‖_F) per model family, two-tailed test α=0.05
4. Success: ρ ≥ 0.5 for ≥2/3 families; record result for paper mechanistic analysis section
5. Compare adaptation magnitude between attention and FFN layer types as secondary analysis

**Success Criteria** (PoC):
- Primary: Spearman ρ ≥ 0.5 in ≥2/3 model families (two-tailed p < 0.05)
- Secondary: Adaptation magnitude monotonically increases with erank tercile in ≥2/3 families

**Failure Response**:
- IF ρ < 0.2 for all families: EXPLORE — mechanism decoupled; investigate whether adaptation direction (not magnitude) correlates with erank
- IF ρ mixed (some positive, some negative): SCOPE — mechanism family-specific; document architectural dependency

**Dependencies**: H-M1 (requires oracle training completion; shares compute with H-E1)

**Source**: Phase 2A Section 1.3 (Causal Step 2) + Section 1.6 (P3)

---

**H-M3: PARA Oracle Assigns Higher Ranks to High-erank Layers (Mechanism Step 3 + Task-Agnosticity)**

**Statement**: Under DeBERTa-v3-base fine-tuned on GLUE MNLI and SST-2 independently, if PARA oracle ranks are determined per layer for both tasks, then Spearman ρ(oracle_rank_MNLI, oracle_rank_SST2) ≥ 0.7, validating that erank-oracle correlation is task-agnostic and that the oracle independently discovers the same layer-complexity structure encoded by erank(W₀).

**Rationale**: This mechanism step closes the causal loop: if the oracle assigns similar ranks regardless of task, it confirms that W₀ structure (captured by erank) is the primary determinant — not task-specific signal. This validates the zero-data, task-agnostic claim of erank as a rank predictor. IFCLoRA 2026 supports the structural-predictor premise; erank strengthens by removing calibration data requirement.

**Variables**:
- Independent: Task identity (MNLI vs SST-2 for DeBERTa; CIFAR-10 for ViT)
- Dependent: PARA oracle rank agreement: Spearman ρ(oracle_MNLI, oracle_SST2) per model
- Controlled: Same model weights (DeBERTa-v3-base pretrained), same oracle protocol (r∈{4,8,16,32,64}, r=8 baseline), fixed hyperparameters per task

**Verification Protocol** (P4/A4 from Phase 2A):
1. Run PARA oracle for DeBERTa-v3-base on full SST-2 (67k train, ≥3 epochs, AdamW lr=2e-5, batch=32) — same protocol as MNLI oracle
2. For each layer, record oracle_rank_SST2; compute Spearman ρ(oracle_rank_MNLI, oracle_rank_SST2) across all DeBERTa layers
3. Also compute erank-oracle Pearson r for SST-2 independently to verify P1 holds for second NLP task
4. Report: ρ ≥ 0.7 confirms task-agnosticity; also report erank-oracle r for SST-2 vs MNLI consistency
5. If ρ < 0.7: document as limitation — erank requires task-specific calibration (loses zero-data advantage)

**Success Criteria** (PoC):
- Primary: Spearman ρ(MNLI_oracle, SST2_oracle) ≥ 0.7 for DeBERTa-v3-base
- Secondary: Pearson r(erank, oracle_SST2) ≥ 0.65 for DeBERTa (P1 replicates on second task)

**Failure Response**:
- IF ρ < 0.5: SCOPE — task-agnosticity claim removed; erank becomes task-conditioned predictor (still useful but weaker than claimed)
- IF 0.5 ≤ ρ < 0.7: EXPLORE — partial task-agnosticity; investigate which layer types show agreement vs disagreement

**Dependencies**: H-M2 (logical: mechanism chain; practical: shares oracle infrastructure from H-E1/H-M1)

**Source**: Phase 2A Section 1.3 (Causal Step 3) + Section 1.4 (A4) + Phase 2B readiness sh3_comparison context

---

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Pearson r ≥ 0.65 in ≥2/3 families | STOP — reassess entire hypothesis |
| H-M1 | MUST_WORK | Levene p < 0.05 in ≥2/3 families (tercile or type) | PIVOT — try PR(W₀) grouping |
| H-M2 | SHOULD_WORK | Spearman ρ ≥ 0.5 in ≥2/3 families | EXPLORE — document as limitation |
| H-M3 | SHOULD_WORK | Spearman ρ(MNLI, SST2) ≥ 0.7 for DeBERTa | SCOPE — narrow to per-task claim |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanism (Step 1) | H-M1 | 1 week (shared oracle data from H-E1) |
| Phase 2: Mechanism (Step 2) | H-M2 | 1 week (shared oracle artifacts from H-M1) |
| Phase 2: Mechanism (Step 3) | H-M3 | 1 week (SST-2 oracle sweep for DeBERTa) |

**Total Duration:** 5 weeks (H-E1 oracle sweep dominates: ~15 days on 5×H100)

---

## 4. Risk Analysis

### 4.1 Risk Overview

5 risks identified from Phase 2A assumptions A1–A5. R1 (metric ceiling) and R3 (direction inversion) are the highest severity risks that would invalidate the hypothesis. R2 (oracle instability) is mitigable with 2-seed reproducibility. R4 (task-specificity) narrows but does not invalidate the claim. R5 (ceiling effect vs h-e1 metric) is pre-addressed by erank's normalized formulation.

### 4.2 Risk-Hypothesis Mapping

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RISK-HYPOTHESIS MAPPING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1 (Metric Ceiling) | A1 | H-E1, H-M1 (all) | High |
| R2 (Oracle Instability) | A2 | H-E1, H-M1, H-M2, H-M3 | Medium |
| R3 (Direction Inversion) | A3 | H-E1 (foundational) | Critical |
| R4 (Task Specificity) | A4 | H-M3 | Medium |
| R5 (erank vs entropy) | A5 | H-E1, H-M1 | Medium |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4.3 Mitigation Strategies

**Risk R1: erank Metric Ceiling (from A1)**

**Source Assumption:** A1 — erank(W₀) shows sufficient variation (CV > 0.05) across layers

**Description:** If erank shows the same ceiling effect as spectral entropy (CV < 0.05 across layers), the correlation signal will be undetectable regardless of whether the underlying mechanism is real.

**Affected Hypotheses:** H-E1, H-M1, H-M2, H-M3 (invalidates entire verification chain)

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Compute erank CV before running oracle sweep — if CV < 0.05 in any model family, switch to participation ratio PR(W₀) = (Σσᵢ)²/Σσᵢ² for that family (pre-validated: P5 checks erank-PR agreement at Spearman ρ ≥ 0.8)
2. **Detection:** Check erank CV per model family immediately after SVD computation (Stage 1, day 1)
3. **Response:**
   - PIVOT: Use PR(W₀) as primary metric if erank CV < 0.05 (P5 oracle-free fallback)
   - SCOPE: Narrow claim to model families where erank shows sufficient variation
   - ABORT: If both erank and PR show CV < 0.05 for all 3 families

**Early Warning Indicators:**
- erank range < 2× for any model family (e.g., all eranks between 8 and 10 for 10-dim subspace)
- erank does not differentiate attention vs FFN layers within BERT/DeBERTa

---

**Risk R2: Oracle Instability (from A2)**

**Source Assumption:** A2 — Marginal PARA oracle produces stable rank assignments across random seeds

**Description:** If oracle ranks are noisy (different ranks selected on two seeds), the correlation signal will be inflated or deflated by measurement error.

**Affected Hypotheses:** H-E1, H-M1, H-M2, H-M3 (oracle data quality)

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Run each oracle training with exactly 2 seeds; use mean validation accuracy for argmax; train for full ≥3 epochs MNLI (not early stopped) to reach convergence
2. **Detection:** After 2-seed runs, check if argmax agrees between seeds; if seed disagreement > 20% of layers, oracle is unstable
3. **Response:**
   - PIVOT: Increase to 3 seeds per oracle point; use validation loss instead of accuracy if accuracy is too noisy
   - SCOPE: Report correlation with oracle ranks only for layers where 2-seed agreement is confirmed
   - ABORT: If > 50% of oracle ranks disagree between seeds (oracle fundamentally invalid)

**Early Warning Indicators:**
- Validation accuracy difference between seeds > 0.5% for same (layer, rank) configuration
- Oracle rank differs between seeds for > 30% of layers in any model family

---

**Risk R3: Direction Inversion (from A3)**

**Source Assumption:** A3 — erank positively (not negatively) predicts oracle rank

**Description:** If the correlation is negative (concentrated-spectrum layers need higher rank), the hypothesis is falsified in its stated form. This is the most dangerous risk because it invalidates the theoretical mechanism.

**Affected Hypotheses:** H-E1 (foundational; cascades to all)

**Severity:** Critical

**Mitigation Strategy:**
1. **Prevention:** Pre-register one-tailed test (H₁: r > 0) before running experiments; document positive direction prediction in Phase 2B plan (this document)
2. **Detection:** Check direction of Pearson r after oracle sweep for DeBERTa (Stage 1 quick-check) before committing to full BERT + ViT sweeps
3. **Response:**
   - PIVOT: If r < 0, reinterpret as "concentrated layers need more rank to compensate for poor low-rank approximation" — run full analysis with |r| ≥ 0.65 threshold
   - EXPLORE: Investigate why direction inverted (low-rank approximation quality metric as alternative DV)
   - ABORT: If both positive and negative directions produce |r| < 0.65, hypothesis is fundamentally unsupported

**Early Warning Indicators:**
- Stage 1 quick-check (DeBERTa + AdaLoRA learned ranks) shows negative Spearman ρ
- Deep FFN layers (expected high-erank) receive low oracle ranks in preliminary runs

---

**Risk R4: Task Specificity (from A4)**

**Source Assumption:** A4 — Oracle ranks for MNLI and SST-2 agree at Spearman ρ ≥ 0.7 (task-agnosticity)

**Description:** If oracle ranks are task-specific, erank loses its zero-data advantage over IFCLoRA (which already uses calibration data).

**Affected Hypotheses:** H-M3 (task-agnosticity claim)

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Run SST-2 oracle for DeBERTa (120 additional runs ~3 GPU-days) before claiming task-agnosticity
2. **Detection:** Report ρ(MNLI_oracle, SST2_oracle) for DeBERTa as pre-specified threshold check
3. **Response:**
   - SCOPE: Reduce claim to "erank predicts per-task oracle rank with ρ ≥ 0.65" — still useful, less powerful
   - EXPLORE: Identify which layer types show task agreement vs disagreement

**Early Warning Indicators:**
- DeBERTa oracle ranks differ substantially between MNLI and SST-2 for attention layers
- erank-oracle r for SST-2 < 0.5 (much lower than MNLI r)

---

**Risk R5: erank Ceiling Effect vs Spectral Entropy (from A5)**

**Source Assumption:** A5 — erank captures relevant structure better than spectral entropy (h-e1 failed metric)

**Description:** If erank shows same ceiling effect as spectral entropy (prior h-e1 failure), the methodology redesign was insufficient.

**Affected Hypotheses:** H-E1, H-M1

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Validate erank implementation against reference (khanghy1000 gist): erank(random_matrix) ≈ min(d_in, d_out); erank(rank-1 matrix) = 1. This confirms dynamic range.
2. **Detection:** Compute erank alongside spectral entropy for all matrices; compare CV of both metrics per model family
3. **Response:**
   - PIVOT: If erank CV ≈ spectral entropy CV, switch to participation ratio PR(W₀) as primary metric
   - EXPLORE: Try log(erank) or erank-normalized-by-dimension as alternative formulations

**Early Warning Indicators:**
- erank values cluster within 10% range for most layers (same as h-e1 spectral entropy failure)
- erank correlation with spectral entropy > 0.95 (metrics effectively identical)

### 4.4 Risk Summary Table

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    RISK SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | erank metric ceiling | A1 | High | All | Switch to PR(W₀) |
| R2 | Oracle instability | A2 | Medium | All | 2-seed mean accuracy |
| R3 | Direction inversion | A3 | Critical | H-E1 | Stage 1 quick-check, pre-register |
| R4 | Task specificity | A4 | Medium | H-M3 | SST-2 oracle validation |
| R5 | erank vs entropy ceiling | A5 | Medium | H-E1, H-M1 | Reference impl validation |

Critical Risks: 1 (R3)
High Risks: 1 (R1)
Medium Risks: 3 (R2, R4, R5)
Low Risks: 0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Baseline Failure Pattern Analysis:**
| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| AdaLoRA requires full training | erank must match training-discovered ranks | Pre-register Stage 1 quick-check using AdaLoRA allocation as proxy oracle |
| IFCLoRA requires calibration data | Calibration-time predictor may outperform structural predictor | If H-E1 r ≥ 0.65 but erank-strategy < IFCLoRA-strategy: narrow claim to "training-free, calibration-free" advantage |
| LAARA uses gradient computation | Gradient info may capture more rank-relevant signal than pure structure | Report erank vs gradient-based predictor comparison in paper limitations |

---

## 5. Dependency & Timeline Visualization

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses (H-E1, H-M1, H-M2, H-M3)
═══════════════════════════════════════════════════════════

[Level 0 - Root / Foundation]
    H-E1: erank-Oracle Correlation Existence
    (EXISTENCE — no dependencies — MUST_WORK)
         │
         ▼ Gate 1: MUST PASS (r ≥ 0.65 in ≥2/3 families)
         │         FAIL → STOP entire hypothesis
         │
[Level 1 - Mechanism Step 1]
    H-M1: Pre-Training Shapes Layer Singular Spectra
    (MECHANISM — prerequisite: H-E1 — MUST_WORK)
         │
         ▼ Gate 2a: MUST PASS (Levene p < 0.05 in ≥2/3 families)
         │          FAIL → PIVOT to PR(W₀) grouping
         │
[Level 2 - Mechanism Step 2]
    H-M2: High-erank Layers Show Larger Adaptation Magnitude
    (MECHANISM — prerequisite: H-M1 — SHOULD_WORK)
         │
         ▼ Gate 2b: SHOULD PASS (Spearman ρ ≥ 0.5)
         │          FAIL → EXPLORE, document as limitation
         │
[Level 3 - Mechanism Step 3 + Task-Agnosticity]
    H-M3: Oracle Assigns High Ranks to High-erank Layers (Task-Agnostic)
    (MECHANISM — prerequisite: H-M2 — SHOULD_WORK)
         │
         ▼ Gate 2c: SHOULD PASS (ρ(MNLI,SST2) ≥ 0.7 for DeBERTa)
                    FAIL → SCOPE claim to per-task prediction

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Levels: 4 (Level 0–3)
Total Gates: 4 decision points
═══════════════════════════════════════════════════════════
```

**Verification Phases with Gate Conditions:**

**Phase 1 — Foundation**
| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | Pearson r(erank, oracle_rank) ≥ 0.65 in ≥2/3 families | MUST PASS |

→ **Gate 1**: If H-E1 fails → STOP, reassess entire hypothesis. No mechanism testing without existence.

**Phase 2 — Core Mechanisms** (3 hypotheses, sequential)
| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-M1 | H-E1 | MUST PASS (Levene p < 0.05) |
| H-M2 | H-M1 | SHOULD PASS (ρ ≥ 0.5) |
| H-M3 | H-M2 | SHOULD PASS (ρ(MNLI,SST2) ≥ 0.7) |

→ **Gate 2a**: H-M1 must pass (layer differentiation must be demonstrated). H-M2/H-M3 failures narrow scope but don't invalidate H-E1 correlation.

### 5.2 Dependency Hierarchy

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 DEPENDENCY HIERARCHY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Level | Hypothesis | Prerequisites | Gate Type    | Phase |
|-------|------------|---------------|--------------|-------|
| 0     | H-E1       | None          | MUST_WORK    | 1     |
| 1     | H-M1       | H-E1          | MUST_WORK    | 2     |
| 2     | H-M2       | H-M1          | SHOULD_WORK  | 2     |
| 3     | H-M3       | H-M2          | SHOULD_WORK  | 2     |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses (H-E1, H-M1, H-M2, H-M3)
═══════════════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2     │ W3      │ W4      │ W5      │
─────────────────┼──────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation
  H-E1           │ ████████ │         │         │         │
  [Gate 1]       │        ◆ │         │         │         │
─────────────────┼──────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms
  H-M1           │          │ ████████│         │         │
  [Gate 2a]      │          │        ◆│         │         │
  H-M2           │          │         │ ████████│         │
  [Gate 2b]      │          │         │        ◆│         │
  H-M3           │          │         │         │ ████████│
  [Gate 2c]      │          │         │         │        ◆│
═══════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
Note: H-E1 oracle sweep (~15 days on 5×H100) dominates total duration.
      H-M1 and H-M2 use oracle artifacts from H-E1 (no additional GPU runs).
      H-M3 requires ~120 additional runs for SST-2 oracle (DeBERTa only).
═══════════════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3

Total Duration: 5 weeks
  Formula: 2 weeks (H-E1 oracle) + 1 week (H-M1 Levene + erank CV)
           + 1 week (H-M2 adaptation magnitude) + 1 week (H-M3 SST-2 oracle)

Compute Budget Breakdown:
  H-E1: ~360 oracle runs for BERT-base (5 ranks × 72 matrices)
         ~400 oracle runs for DeBERTa-v3-base (5 ranks × 80 matrices)
         ~360 oracle runs for ViT-base (5 ranks × 72 matrices)
         ≈ 1,120 total oracle training runs for P1 on MNLI + CIFAR-10
  H-M3: ~400 additional oracle runs for DeBERTa SST-2 (task-agnosticity)
  H-M1/H-M2: No additional GPU runs — use oracle artifacts from H-E1

Stage 1 Quick-Check (RECOMMENDED before full sweep):
  DeBERTa + AdaLoRA learned ranks as proxy oracle
  ~2 days GPU time on 5×H100
  Go/No-Go decision before committing full 1,120 oracle runs

Slack Available: 0 weeks (all sequential)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 4
  - Existence: 1 (H-E1)
  - Mechanism: 3 (H-M1, H-M2, H-M3)
  - Condition: 0 (not needed)

Verification Phases: 2
  1. Foundation (H-E1) — Week 1-2
  2. Mechanisms (H-M1→H-M3) — Week 3-5

Total Duration: 5 weeks
Critical Path Length: 5 weeks
Execution Mode: Sequential chain

Compute Resources:
  - 5×H100 (confirmed from h-e1 infrastructure)
  - H-E1: ~1,120 oracle training runs (5 ranks × ~224 matrices across 3 models)
  - H-M3: ~400 additional SST-2 oracle runs for DeBERTa
  - H-M1/H-M2: Analysis only (shared oracle artifacts, no GPU runs)

Datasets Required (full standard splits):
  - GLUE MNLI: 392k train (NLP oracle) — HuggingFace Hub
  - GLUE SST-2: 67k train (H-M3 task-agnosticity) — HuggingFace Hub
  - CIFAR-10: 50k train (ViT oracle) — HuggingFace Hub

Models Required:
  - bert-base-uncased (110M params, HuggingFace)
  - microsoft/deberta-v3-base (86M params, HuggingFace)
  - google/vit-base-patch16-224 (86M params, HuggingFace)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

```
Step 1: Validate erank implementation (reference check) — Day 1
Step 2: Compute erank(W₀) and PR(W₀) for all 3 model families — Day 1 (30 min)
Step 3: Stage 1 quick-check: DeBERTa + AdaLoRA proxy oracle (Go/No-Go) — Days 2-3
Step 4: If Go → Run PARA oracle for all 3 models on MNLI+CIFAR-10 — Weeks 1-2
Step 5: Evaluate Gate 1 (H-E1): Pearson r ≥ 0.65 in ≥2/3 families
        → FAIL: STOP; PASS: continue
Step 6: Execute H-M1 analysis (Levene test on oracle data from Step 4) — Week 3
Step 7: Evaluate Gate 2a (H-M1): Levene p < 0.05 in ≥2/3 families
        → FAIL: PIVOT; PASS: continue
Step 8: Execute H-M2 analysis (adaptation magnitude from oracle artifacts) — Week 4
Step 9: Evaluate Gate 2b (H-M2): Spearman ρ ≥ 0.5 in ≥2/3 families
        → FAIL: document; PASS: continue
Step 10: Run SST-2 oracle for DeBERTa, execute H-M3 analysis — Week 5
Step 11: Evaluate Gate 2c (H-M3): ρ(MNLI,SST2) ≥ 0.7
Step 12: Train erank-proportional rank assignment, compare to uniform r=8 (P2) — parallel with Step 10
Step 13: Compile all results → Phase 2C experiment design
```

---

## 6. Dialectical Analysis

### 6.1 Full Analysis

Dialectical analysis conducted via MCP structuredargumentation (3 arguments: thesis, antithesis, synthesis). The central tension is between theoretical motivation (positive direction derived from information-theoretic analysis of singular spectra) and empirical precedent (h-e1 spectral entropy failure on same theoretical grounds). The synthesis resolves this through staged testing and pre-specified fallbacks. Overall robustness: **High** — verification plan addresses all antithesis concerns with concrete mitigations.

### 6.2 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: erank(W₀) is a statistically significant, positive,
zero-data predictor of per-layer optimal LoRA rank, with Pearson
r ≥ 0.65 in ≥2/3 transformer model families.

Supporting Evidence:
1. Pre-training shapes singular spectra by layer complexity (h-e1
   ViT depth variation 4.27→6.44; BERT attention vs FFN Levene p=0.0001)
2. High-erank matrices require higher-rank LoRA updates to span
   task-relevant signal in non-dominated directions (Exchange 7,
   theoretically derived)
3. PARA oracle independently discovers layer-complexity structure;
   IFCLoRA 2026 validates structural-predictor premise
4. LAARA 2026 proves uniform rank suboptimal — field needs per-layer
   differentiation; erank provides zero-cost solution

Strengths:
- Zero-data, zero-training — qualitatively better than AdaLoRA/IFCLoRA/LAARA
- Theoretically grounded positive direction (pre-registered)
- Cross-architecture (NLP + Vision) scope
- Both outcomes publishable (positive: new method; negative: bounds static predictors)

Expected Outcomes:
- Primary (P1): r ≥ 0.65 (one-tailed p < 0.05) in ≥2/3 families
- Secondary (P2): erank-strategy within 1% oracle, outperforms uniform r=8
- Tertiary (P3): Spearman ρ(adaptation_magnitude, erank) ≥ 0.5

Confidence: 0.72
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS (H0)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis: There is no significant positive correlation between
erank(W₀) and PARA oracle ranks (r ≤ 0 for ≥2/3 families, or
0 < r < 0.65 for all 3 families).

Counter-Arguments:
1. h-e1 precedent: spectral entropy failed on same theoretical motivation
   — structural predictors often collapse to ceiling effects in practice
2. Non-convex LoRA landscape: optimal rank may depend on training dynamics
   (task signal alignment), not W₀ geometry alone
3. Marginal oracle ≠ joint-optimal oracle: correlation with marginal proxy
   may not reflect globally optimal rank allocation
4. Task-specificity risk: if MNLI/SST-2 oracle ranks disagree (ρ < 0.7),
   erank loses its zero-data advantage over calibration-based IFCLoRA

Potential Failure Points:
- R3 (Critical): Direction inverted (r < 0 for ≥2/3 families)
- R1 (High): erank CV < 0.05 — same ceiling as spectral entropy
- R4 (Medium): Oracle ranks task-specific (ρ < 0.7 MNLI vs SST-2)

Conditions Supporting H0:
- Stage 1 quick-check shows Spearman ρ < 0 (DeBERTa + AdaLoRA proxy)
- Deep FFN layers get LOW oracle ranks despite expected high erank
- erank CV < 0.05 in any model family

Antithesis Confidence: 0.28 (thesis is more likely given indirect evidence)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:

H-erank-v1 presents a theoretically grounded, falsifiable claim with
zero prior direct empirical support. The antithesis raises valid
concerns from h-e1 precedent and LoRA optimization dynamics.

Resolution Path:

The verification plan addresses this dialectic through:
1. Stage 1 quick-check (DeBERTa + AdaLoRA proxy, 3 days): Go/No-Go
   before committing 15-day full oracle sweep — directly mitigates R3
2. Sequential H-E1→H-M1→H-M2→H-M3 chain: three independent lines of
   corroborating evidence beyond single-number correlation
3. Pre-specified fallbacks: PR(W₀) for R1; SST-2 oracle for R4;
   scope narrowing for direction/magnitude failures
4. Pre-registered positive direction: one-tailed test prevents
   post-hoc direction reversal (antithesis's core epistemic concern)

Conditions for Thesis Support:
- All MUST_WORK gates pass (H-E1 r≥0.65, H-M1 Levene p<0.05)
- P1 confirmed: Pearson r ≥ 0.65 (one-tailed p < 0.05) in ≥2/3 families
- Mechanism chain provides convergent validity (H-M2/H-M3 at least partial)

Conditions for Antithesis Support:
- H-E1 fails: r < 0 for ≥2/3 families (wrong direction) OR
  0 < r < 0.65 for all 3 families (signal too weak)
- erank CV < 0.05 in all families (ceiling effect — metric redesign needed)

Nuanced Outcome Possibilities:
1. Full Support: H-E1+H-M1 MUST_WORK pass + H-M2+H-M3 SHOULD_WORK pass
   → Thesis validated with mechanism; strongest possible result
2. Partial Support: H-E1 passes, H-M2 or H-M3 fails
   → Correlation established without full mechanism explanation; still publishable
3. No Support: H-E1 or H-M1 fail
   → Antithesis supported; paper documents bounds of static W₀ predictors

Synthesis Confidence: 0.82 (verification plan is epistemically sound)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.5 Robustness Assessment

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 ROBUSTNESS ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | r ≥ 0.65 in ≥2/3 families | May be < 0.65 or < 0 | H-E1 test with pre-registered direction |
| Mechanism | 3-step causal chain valid | Non-convex landscape overrides structure | H-M1–H-M3 independent tests |
| Metric | erank wider dynamic range than entropy | Same ceiling as h-e1 spectral entropy | CV check Day 1; PR(W₀) fallback |
| Task-agnosticity | Oracle ranks task-stable (ρ ≥ 0.7) | Task-specific — loses zero-data advantage | H-M3 SST-2 oracle for DeBERTa |
| Compute risk | 5-week staged plan | 15-day oracle wasted if H-E1 fails | Stage 1 quick-check Go/No-Go (Day 3) |

**Overall Robustness Score:** High
**Confidence in Verification Plan:** 0.82 (synthesis)
**Confidence in Hypothesis (H1):** 0.72 (Phase 2A consensus)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** erank(W₀) correlates with PARA oracle rank at Pearson r ≥ 0.65 in ≥2/3 of {BERT-base, DeBERTa-v3-base, ViT-base} families.
- ID: H-erank-v1 | Confidence: 0.72

**Verification Structure:**
- Mode: Incremental (Phase 2A data loaded; 60% scope reduction from established facts)
- Sub-Hypotheses: 4 total — H-E1 (Existence), H-M1, H-M2, H-M3 (Mechanism chain)
- Phases: 2 phases over 5 weeks | Critical Gates: 4 decision points
- Compute: ~1,120 oracle training runs + Stage 1 quick-check (3 days) before full commitment

**Risk Assessment:** Medium-High
- Critical risk: R3 direction inversion (mitigated by Stage 1 Go/No-Go)
- High risk: R1 metric ceiling (mitigated by erank CV check Day 1 + PR(W₀) fallback)

**Immediate Action:** Stage 1 quick-check — DeBERTa erank vs AdaLoRA learned ranks (Days 1-3)

### 7.2 Final Summary & Conclusions

**Key Achievements:**
- 4 sub-hypotheses (H-E1, H-M1, H-M2, H-M3) covering existence + full 3-step causal chain
- H0 addressed: No significant positive correlation (r ≤ 0 or 0 < r < 0.65 for all 3 families)
- 5 risks identified from A1–A5 with complete mitigation strategies and fallback metrics
- Staged verification with Go/No-Go gate before major compute commitment

**Verification Execution Order:**

**Phase 1: Foundation** (Weeks 1–2)
- Stage 1 quick-check: DeBERTa + AdaLoRA proxy (Days 1–3) — Go/No-Go
- H-E1: Compute erank, run PARA oracle full suite (MNLI 392k, CIFAR-10 50k, ≥3/5 epochs), Pearson r
- Gate 1: MUST PASS (r ≥ 0.65 in ≥2/3 families, one-tailed p < 0.05)

**Phase 2: Core Mechanisms** (Weeks 3–5)
- H-M1: Levene test on oracle rank distributions by erank tercile and layer type (Week 3)
- H-M2: Spearman ρ(erank, ‖ΔW_opt‖_F/‖W₀‖_F) from oracle training artifacts (Week 4)
- H-M3: SST-2 oracle for DeBERTa; ρ(MNLI_oracle, SST2_oracle) task-agnosticity check (Week 5)
- Parallel: Train erank-proportional assignment, compare to uniform r=8 (P2)

**Critical Decision Points:**

1. **Day 3 (Stage 1 Go/No-Go):** DeBERTa erank vs AdaLoRA proxy
   - Negative Spearman ρ → STOP full oracle commitment; investigate R3
   - Positive → Proceed to full H-E1 oracle sweep

2. **Gate 1 — Week 2 (H-E1 MUST_WORK):**
   - FAIL (r < 0 for ≥2/3): ABANDON thesis; write bounds-of-static-predictors paper
   - FAIL (0 < r < 0.65 for all 3): PIVOT to PR(W₀) as primary metric
   - PASS → Phase 2

3. **Gate 2a — Week 3 (H-M1 MUST_WORK):**
   - FAIL → PIVOT to PR(W₀) grouping; H-M2/H-M3 as exploratory

4. **Gates 2b/2c — Weeks 4–5 (H-M2/H-M3 SHOULD_WORK):**
   - Failures narrow scope but do not invalidate H-E1 correlation claim

**Open Questions:**
- Does erank generalize to decoder-only LLMs (GPT/LLaMA architecture)?
- Does the erank-truncation criterion (oracle-free alternative) correlate with PARA oracle at comparable r?
- What is the minimum training run count for a stable marginal oracle (2 seeds sufficient)?
- Is erank-oracle correlation consistent across MNLI and SST-2 (task-agnosticity confirmed)?

**Recommendations:**

1. **Immediate Actions:**
   - Implement erank computation + reference validation before any oracle training
   - Run Stage 1 quick-check (Days 1–3) as mandatory Go/No-Go
   - Pre-register positive direction at α=0.05 before oracle runs

2. **Resource Allocation:**
   - Weeks 1–2: 5×H100 for full oracle sweep (budget ~15 GPU-days)
   - Week 5: ~3 GPU-days additional for SST-2 oracle (H-M3 task-agnosticity)
   - H-M1/H-M2: Analysis only (no additional GPU runs needed)

3. **Failure Management:**
   - R3 (direction): Stage 1 early detection; PR(W₀) fallback ready
   - R1 (ceiling): CV check Day 1; switch metric before oracle commitment
   - Always document failures with interpretation for paper limitations section

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: `docs/youra_research/03_refinement.yaml` (ID: H-erank-v1)
- Schema version: 10.0.0 | Generated: 2026-08-05 | Convergence: 15 exchanges, 6 agents

**B. MCP Tool Usage Summary**
- Total MCP calls: 7 (4 scientificmethod + 3 structuredargumentation)
- Tools: scientificmethod ×4 (H-E1 hypothesis+experiment, H-M integrated hypothesis+experiment), structuredargumentation ×3 (thesis, antithesis, synthesis)
- Mode: Incremental (Phase 2A pre-structured; 4–6 calls target met)

---

## 8. Finalization Status

**Verification State:** COMPLETE — verification_state.yaml created with 4 sub-hypotheses (H-E1 READY, H-M1/H-M2/H-M3 NOT_STARTED)
**Pipeline Tasks Updated:** N/A — Archon pipeline project not found in unattended mode (Phase 0 brainstorm exists locally; re-run Phase 0 to create Archon project if needed)
**Hypothesis Tasks Created:** 4 hypotheses registered in verification_state.yaml; Archon tasks pending pipeline project creation
