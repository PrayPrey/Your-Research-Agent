# Verification Plan: Duality-Guided Cross-Architecture Distillation (DG-CAD)

**Date:** 2026-08-29
**Hypothesis ID:** H-DG-CAD-v1
**Confidence:** 0.80
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under standard NLP tasks (classification, QA, summarization), if Transformer attention layers are converted to SSM layers using Mamba-2 duality-inspired closed-form initialization followed by layer-wise optimization, then the resulting sub-quadratic model achieves performance within 1.5x the degradation of same-architecture distillation, because the duality-preserving initialization provides a strong starting point that reduces optimization difficulty and preserves long-context reasoning structure.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in downstream task performance between duality-guided cross-architecture distillation and naive output-matching knowledge distillation (p > 0.05).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | LongBench (standard) | Provides 4K-128K context evaluation across multiple task types; directly tests long-context preservation |
| **Model** | BERT-base → Mamba-12 | Standard sizes (12 layers, 768 dim) enable fair comparison; public implementations available |

**Dataset Details:**
- Source: THUDM/LongBench on GitHub
- Path: github.com/THUDM/LongBench

**Model Details:**
- Type: Transformer (teacher) to SSM (student)
- Source: HuggingFace Transformers (BERT), state-spaces/mamba (Mamba)

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| DistilBERT | 97% of BERT on GLUE | GLUE |
| Mamba (from scratch) | Competitive with Transformers | Various NLP |
| Naive KD | TBD (baseline) | LongBench |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Mamba-2 duality conditions approximately hold for pretrained Transformer attention patterns | Mamba-2 shows equivalence for attention with specific structure | Closed-form initialization produces poor starting point |
| A2 | Layer-wise conversion preserves gradient flow better than end-to-end | Layer-wise distillation used successfully in DistilBERT | May need alternative conversion order |
| A3 | Calibration on 512-4096 token sequences generalizes to 8K+ contexts | SSM recurrence is position-agnostic | Must include longer sequences in calibration |
| A4 | 768-dim SSM state is sufficient to represent 768-dim Transformer hidden states | Mamba-2 uses matching dimensions | May need state expansion factor (2x) |
| A5 | Attention head entropy correlates with conversion difficulty | High-entropy attention spreads information widely | Need alternative metrics for conversion quality |

### 1.6 Research Gap & Novelty

**Gap:** No existing method operationalizes Mamba-2 attention-SSM duality for practical knowledge distillation from Transformers to SSMs.

**Novelty:** First closed-form SSM parameter initialization from attention weights using duality equations, enabling structure-preserving cross-architecture distillation.

**Differentiation:**
- vs. DistilBERT: Same-architecture only; we enable Transformer→SSM
- vs. Mamba-2: Proves duality theoretically; we operationalize for transfer
- vs. Naive KD: Black-box output matching; we preserve internal structure

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| h-e1 | EXISTENCE | MUST_WORK | None | READY |
| h-m1 | MECHANISM | MUST_WORK | h-e1 | READY |
| h-m2 | MECHANISM | MUST_WORK | h-m1 | READY |
| h-m3 | MECHANISM | MUST_WORK | h-m2 | READY |

---

### 2.2 Hypothesis Specifications

#### h-e1: Duality Initialization Validity

**Type:** EXISTENCE
**Statement:** Under Mamba-2 duality equations, if attention weights from a pretrained Transformer are converted to SSM parameters (A, B, C, Δ), then the resulting SSM produces non-divergent outputs during forward pass, because the duality mapping preserves core computational structure.

**Variables:**
- IV: Conversion method (duality equations vs random init)
- DV: SSM output stability (non-divergent forward pass)
- CV: Model architecture (12 layers, 768 dim), input sequences

**Success Criteria:**
- SSM forward pass completes without NaN/Inf for 100% of calibration samples
- Output magnitude within 10x of Transformer output magnitude

**Gate:**
- Type: MUST_WORK
- If Fail: Duality equations are incorrectly implemented or fundamentally incompatible

**Prerequisites:** None

**Verification Protocol:**
1. Implement closed-form SSM parameter derivation from attention weights
2. Initialize Mamba-12 using duality equations on BERT-base layer 1
3. Run forward pass on 100 calibration samples (512-2048 tokens)
4. Check for NaN/Inf in outputs; measure output magnitude ratio
5. Pass if all outputs valid and magnitude ratio < 10x

---

#### h-m1: Closed-Form Initialization Quality

**Type:** MECHANISM
**Statement:** Under layer-wise conversion, if SSM parameters are initialized via duality equations (vs random), then initial reconstruction error is lower, because duality provides structurally-aligned starting point.

**Variables:**
- IV: Initialization method (duality vs random)
- DV: Initial reconstruction MSE (before optimization)
- CV: Layer index, calibration data

**Success Criteria:**
- Duality init achieves ≥30% lower initial reconstruction error than random init
- Statistical significance p < 0.05 (paired t-test across layers)

**Gate:**
- Type: MUST_WORK
- If Fail: Duality equations do not provide meaningful advantage; reconsider approach

**Prerequisites:** h-e1

**Verification Protocol:**
1. For each Transformer layer, initialize SSM via duality and random
2. Measure reconstruction MSE on calibration set (no optimization yet)
3. Compare initial error between methods across all 12 layers
4. Compute paired t-test; report mean improvement percentage

---

#### h-m2: Layer-Wise Optimization Convergence

**Type:** MECHANISM
**Statement:** Under layer-wise optimization with duality-initialized parameters, if 100 optimization steps are applied per layer, then reconstruction error decreases monotonically, because well-initialized parameters lead to stable optimization landscape.

**Variables:**
- IV: Optimization steps (0, 25, 50, 75, 100)
- DV: Reconstruction MSE trajectory
- CV: Learning rate, optimizer, calibration data

**Success Criteria:**
- Reconstruction error decreases by ≥50% from step 0 to step 100
- No divergence (error increase >10%) in any 25-step window

**Gate:**
- Type: MUST_WORK
- If Fail: Optimization landscape is ill-posed; need different objective or initialization

**Prerequisites:** h-m1

**Verification Protocol:**
1. Initialize all layers via duality equations
2. Apply layer-wise optimization with logging every 25 steps
3. Plot reconstruction error trajectory for each layer
4. Verify monotonic decrease and compute total reduction percentage

---

#### h-m3: Fine-Tuning Task Alignment

**Type:** MECHANISM
**Statement:** Under downstream task fine-tuning, if the converted SSM is fine-tuned on task data, then task accuracy improves while calibration performance is preserved, because fine-tuning adapts to task distribution without catastrophic forgetting.

**Variables:**
- IV: Fine-tuning epochs (0, 1, 3, 5)
- DV: Task accuracy, calibration reconstruction error
- CV: Task type, learning rate, batch size

**Success Criteria:**
- Task accuracy improves ≥5% from epoch 0 to epoch 5
- Calibration reconstruction error increases <20% (no catastrophic forgetting)

**Gate:**
- Type: MUST_WORK
- If Fail: Fine-tuning causes catastrophic forgetting; need regularization

**Prerequisites:** h-m2

**Verification Protocol:**
1. Take fully-converted SSM from h-m2
2. Fine-tune on GLUE subset (MNLI or QQP)
3. Evaluate task accuracy at each epoch checkpoint
4. Also evaluate reconstruction error on calibration set
5. Verify accuracy gain and bounded reconstruction degradation

---

## 3. Execution

### 3.1 Dependency Chain
```
h-e1 → h-m1 → h-m2 → h-m3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| h-e1 | MUST_WORK | Non-divergent SSM outputs | STOP: Fix duality equations |
| h-m1 | MUST_WORK | ≥30% lower initial error | STOP: Reconsider initialization approach |
| h-m2 | MUST_WORK | ≥50% error reduction, monotonic | STOP: Fix optimization objective |
| h-m3 | MUST_WORK | ≥5% accuracy gain, <20% calibration degradation | STOP: Add regularization |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Existence | h-e1 | 1-2 days |
| Phase 2: Mechanism | h-m1, h-m2, h-m3 | 3-5 days |

**Total Duration:** 4-7 days (PoC verification)

---

## 4. Risk Analysis

### 4.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Duality equations don't hold for real attention | Medium | High | Test on single layer first; have fallback approximation |
| Optimization diverges | Low | High | Use conservative learning rate; add gradient clipping |
| Catastrophic forgetting during fine-tuning | Medium | Medium | Add calibration loss regularization |
| Insufficient long-context generalization | Medium | Medium | Include longer sequences in calibration |

### 4.2 Risk-Hypothesis Mapping

- A1 violation → h-e1 fails
- A2 violation → h-m2 fails (try alternative conversion order)
- A3 violation → h-m3 long-context eval fails (expand calibration)
- A4 violation → h-e1/h-m1 fails (try state expansion)
- A5 violation → h-m1 shows no entropy correlation (find alternative metric)

---

## 5. Dialectical Analysis

### 5.1 Thesis
Duality-guided initialization provides superior starting point for cross-architecture distillation by preserving the computational structure of attention in SSM form, leading to faster convergence and better final performance.

### 5.2 Antithesis (H0 Perspective)
Attention and SSM are fundamentally different computational primitives. Any theoretical "duality" breaks down in practice due to:
- Pretrained attention patterns deviating from duality conditions
- Optimization landscape being equally difficult regardless of initialization
- SSM unable to truly replicate attention's parallel-in-time computation

### 5.3 Synthesis
The truth likely lies between: duality provides a meaningful advantage for attention patterns that approximately satisfy duality conditions, but benefit varies by layer and attention head. The verification plan tests this by measuring layer-by-layer reconstruction improvement and identifying which attention characteristics predict conversion quality.

### 5.4 Robustness Assessment
- **Strong if:** h-e1 passes easily, h-m1 shows consistent 30%+ improvement across layers
- **Moderate if:** h-e1 passes with some layers, h-m1 shows 15-30% improvement
- **Weak if:** h-e1 barely passes, h-m1 shows <15% improvement

---

## 6. Summary

**Executive Summary:**
This verification plan decomposes DG-CAD validation into 4 sub-hypotheses following the 3-step causal chain from Phase 2A. Each hypothesis has MUST_WORK gates ensuring early failure detection. The plan focuses on PoC verification (does the methodology work?) rather than full baseline comparison (how much better?), which is deferred to Phase 5.

**Key Decision Points:**
1. h-e1: If duality equations produce divergent outputs → fundamental rethink needed
2. h-m1: If initial error reduction <30% → duality advantage is marginal
3. h-m2: If optimization diverges → objective/initialization incompatible
4. h-m3: If catastrophic forgetting → regularization strategy required

**Next Steps:**
→ Phase 2C: Design detailed experiment for h-e1
→ Phase 3: Implementation planning for duality equation code
→ Phase 4: Execute verification loop

---

*Generated by Phase 2B Planning Workflow*
*stepsCompleted: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]*
