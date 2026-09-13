# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-OSLO-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under fixed parameter budget constraints, if layer-wise sparse and low-rank allocation is optimized using reconstruction error minimization via alternating minimization, then fine-tuning perplexity will decrease by 15-30% compared to uniform allocation, because layers with higher reconstruction error sensitivity receive more budget and achieve better task-specific adaptation.

**Alternative Hypothesis (H0):**
Uniform allocation of sparse and low-rank capacity across layers is equally effective as sensitivity-based allocation, and any observed differences are due to random variation or confounding factors rather than the allocation strategy.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Layer-wise sparsity budget (k_l) | Independent | Number of non-zero parameters per layer, varied via allocation algorithm | 0 to d² (layer dimension squared) |
| Layer-wise rank budget (r_l) | Independent | Rank of low-rank decomposition per layer, varied via allocation algorithm | 1 to 64 (typical range) |
| Total parameter budget (P) | Controlled | Fixed sum constraint: Σ(k_l + 2*d_l*r_l) ≤ P | Fixed at 1-5% of total parameters |
| Fine-tuning perplexity | Dependent | WikiText-2 test perplexity after fine-tuning | 5.0-20.0 (lower is better) |
| Reconstruction error | Dependent | Layer-wise Frobenius norm \|\|W_l + ΔW_l - W*_l\|\|²_F | 0.0-1.0 (normalized) |
| Model architecture | Controlled | Fixed to LLaMA-7B/13B transformer | LLaMA-7B primary, 13B secondary |
| Training data | Controlled | Alpaca instruction-tuning dataset | 52K examples |
| Optimization hyperparameters | Controlled | Learning rate=1e-4, batch size=16, epochs=3 | Fixed values |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Sensitivity Estimation
    ↓ (gradient-based ∂E_l/∂budget)
Step 2: Layer Importance Ranking
    ↓ (proportional allocation)
Step 3: Budget Allocation
    ↓ (alternating minimization)
Step 4: Per-layer Optimization
    ↓ (reconstruction error minimization)
Outcome: Reduced Perplexity
```

**Step 1 → Step 2:** Reconstruction error sensitivity estimation → Layer importance ranking
- Each layer's sensitivity ∂E_l/∂budget is computed via gradient
- Layers are ranked by their potential benefit from additional parameters
- Evidence: LoSA (2025) uses RMI for similar purpose; OSLO replaces heuristic with gradient-based estimation

**Step 2 → Step 3:** Layer importance ranking → Budget allocation
- Budget is allocated proportionally to sensitivity
- High-sensitivity layers receive more sparse/low-rank capacity
- Evidence: Bertsimas et al. (2023) alternating minimization scales to n=10000 in minutes

**Step 3 → Step 4:** Budget allocation → Per-layer alternating minimization
- Each layer optimizes its allocated sparse (S_l) and low-rank (L_l*R_l) components
- Alternating updates: sparse step → low-rank step → repeat until convergence
- Evidence: Bernoulli-LoRA (2025) proves convergence for similar low-rank updates

**Step 4 → Outcome:** Per-layer optimization → Reduced perplexity
- Converged allocation minimizes global reconstruction error
- Reconstruction error correlates with downstream perplexity
- Evidence: HASSLE-free (2025) achieves 12% perplexity reduction via reconstruction error

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | LoSA (Huang 2025) | RMI-based importance works; gradient is more principled | Medium |
| Step2 → Step3 | Bertsimas et al. (JMLR 2023) | Alternating minimization scales efficiently | Strong |
| Step3 → Step4 | Bernoulli-LoRA (Sokolov 2025) | Convergence guarantees for low-rank updates | Strong |
| Step4 → Outcome | HASSLE-free (Makni 2025) | 12% perplexity reduction via reconstruction error | Strong |

**Key Tension:**
- **Tension:** HASSLE-free demonstrates reconstruction error works for within-layer decomposition, but OSLO extends this to across-layer allocation. The assumption that layer-wise independence holds may not be valid for highly coupled transformer layers.
- **Resolution:** This verification plan tests layer independence assumption explicitly by comparing OSLO's layer-wise approach with a joint optimization baseline.

### 1.4 Key Assumptions

1. **Reconstruction error correlates with downstream task performance**
   - Evidence: HASSLE-free (2025) achieves 12% perplexity reduction; LoSA achieves 68.73 perplexity reduction
   - Consequence if violated: Optimizing reconstruction error may not improve actual task metrics; need to switch to direct task loss optimization

2. **Layer-wise optimization is sufficient vs. joint optimization**
   - Evidence: LoSA demonstrates effective layer-wise rank adjustment; avoids computational cost of joint optimization
   - Consequence if violated: Need to develop joint optimization algorithm, increasing computational cost significantly (potentially 10-100x)

3. **Alternating minimization converges for transformer weight matrices**
   - Evidence: Bernoulli-LoRA proves convergence for low-rank updates on linear layers; attention layers are conjectured
   - Consequence if violated: OSLO may produce unstable or suboptimal allocations; need to add convergence regularization or use convex relaxation

### 1.5 Scope & Boundaries

**Where hypothesis applies:**
- Transformer architectures: GPT, LLaMA, Mistral, and similar decoder-only models
- Fine-tuning scenarios: Instruction tuning, domain adaptation, task-specific fine-tuning
- Parameter budgets: 1-5% of total model parameters (typical PEFT range)

**Where hypothesis does NOT apply:**
- Non-transformer architectures: CNNs, RNNs, MLPs without attention
- Pre-training from scratch: Only fine-tuning is considered
- Extreme sparsity regimes: >95% sparsity may require different approaches

**Known limitations:**
- Convergence proof limited to linear/MLP layers; attention layers rely on empirical validation
- Computational overhead of sensitivity estimation may not scale to 100B+ models
- Current formulation assumes fixed architecture; dynamic architectures require extension

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Perplexity vs OSLO Allocation):**
OSLO allocation will achieve WikiText-2 perplexity reduction of ≥15% compared to uniform allocation under the same parameter budget.

*Measurement*:
- Perplexity reduction ≥15% with p < 0.05
- Statistical test: Paired t-test, n ≥ 25 runs (5 seeds × 5 parameter budget levels)

*Basis*:
- HASSLE-free achieves 12% perplexity reduction via reconstruction error
- LoSA achieves 68.73 absolute perplexity reduction
- OSLO's principled allocation should match or exceed these

*Success Criteria for Phase 2B*:
- Primary: Perplexity reduction ≥15% (p < 0.05)
- Falsification: Perplexity reduction <5% triggers hypothesis rejection

**Secondary Predictions:**

**P2 (Mechanism Validation):**
Layers with higher reconstruction error sensitivity (measured via gradient ∂E_l/∂budget) will receive more budget under OSLO allocation, and this correlation will be statistically significant (r > 0.7, p < 0.01).

**P3 (Comparative Advantage):**
OSLO will outperform LoSA (RMI heuristic) by at least 5% perplexity reduction on LLaMA-7B with 2% parameter budget.

**Falsification Criteria:**
The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: Perplexity reduction <5% compared to uniform allocation
   (Statistically indistinguishable from baseline)

2. **Mechanism Failure**: No correlation between sensitivity and allocation (r < 0.3)
   (Core mechanism does not operate as proposed)

3. **Comparative Failure**: OSLO performs worse than LoSA on any benchmark
   (No advantage over existing heuristic methods)

### 1.7 SOTA Baseline (SOTA Comparison Mode)

**Comparison Methods from Literature:**

| Method | Dataset | Performance | Std Dev | Year |
|--------|---------|-------------|---------|------|
| HASSLE-free | WikiText-2 | 12% perplexity reduction | N/A | 2025 |
| LoSA | WikiText-2 | 68.73 perplexity reduction | N/A | 2025 |
| RoseLoRA | Multiple | Enables knowledge editing | N/A | 2024 |
| SaRA | Multiple | Nuclear-norm low-rank | N/A | 2024-2025 |

**OSLO Target:**
- Primary: 15-30% perplexity reduction (exceeds HASSLE-free's 12%)
- Comparative: Outperform LoSA by 5% additional reduction

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): ~0.6 (medium-large effect)
- Required runs: n ≥ 25
- Statistical power: 0.8

**Test Specification:**
- Method: Paired t-test (same random seeds across conditions)
- Significance level: α = 0.05 (one-tailed)
- Report format: Mean difference, 95% CI, Cohen's d, p-value

**Experimental Configuration:**
- Seeds: 5 independent random seeds
- Budget levels: 5 levels (1%, 2%, 3%, 4%, 5% of parameters)
- Total runs: 25 per method (5 seeds × 5 budgets)

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does OSLO allocation achieve measurably lower perplexity than uniform allocation under fixed parameter budget?"
- Maps to: Primary prediction P1
- Verification type: Empirical comparison
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the reconstruction error sensitivity → proportional allocation → alternating minimization → perplexity reduction causal pathway operating as proposed?"
- Maps to: Causal mechanism (4 steps)
- Will decompose into: H-M1, H-M2, H-M3, H-M4 (one per causal link)
- Verification type: Causal analysis with ablations
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does OSLO outperform LoSA, RoseLoRA, and SaRA on standard benchmarks?"
- Maps to: Secondary prediction P3
- Verification type: Comparative empirical
- Critical: Determines practical value

**Total sub-hypotheses in Phase 2B:** 2 + 4 = 6

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-OSLO-v1
- [x] Confidence level specified: 0.85
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (4 steps, evidence table provided)
- [x] Causal chain length (N=4) determined and stored
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 predictions, primary marked)
- [x] Falsification criteria are defined
- [x] Baselines are identified for comparison (LoSA, RoseLoRA, SaRA)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:** How many GPU hours for sensitivity estimation on LLaMA-70B? Initial estimate: 2-4 hours on 8xA100 for full sensitivity computation.

2. **Data Availability:** Is Alpaca dataset (52K examples) sufficient for fine-tuning validation, or need additional datasets (Dolly, FLAN)?

3. **Priority Verification Order:** Should verify SH1 (existence) first to establish baseline, then SH2 (mechanism) for understanding, finally SH3 (comparison) for positioning?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (v2.0)*
*2026-02-13*
