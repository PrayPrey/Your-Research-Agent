# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-RA-DP-FL-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under heterogeneous federated LoRA fine-tuning conditions with varying client resources, if privacy budget is allocated proportionally to LoRA rank (ε_i = ε_total × r_i / Σr_j), then task accuracy will improve over uniform budget allocation at the same total ε, because higher-rank adapters (more expressive) receive tighter budgets while lower-rank adapters can tolerate more noise, creating equitable information leakage per unit capacity.

**Alternative Hypothesis (H0):**
Rank-proportional privacy budget allocation does not improve task accuracy compared to uniform allocation; the relationship between adapter rank and optimal privacy budget is either non-existent or non-linear, making uniform ε allocation equally effective or superior.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| LoRA rank (r_i) | Independent | Integer rank value per client determined by device memory/compute resources | 4-64 (typical range) |
| Total privacy budget (ε_total) | Independent | Real-valued epsilon for (ε,δ)-DP | 1-10 (practical range) |
| Task accuracy | Dependent | Downstream NLP task accuracy measured on held-out test set | 60-95% depending on task |
| Privacy guarantee (ε,δ) | Dependent | Differential privacy parameters where δ=1/n for n training samples | ε: per-client, δ: 10^-5 to 10^-6 |
| Communication cost | Dependent | Bytes transmitted per round per client | Reduced by ~95% vs full model |
| Model architecture | Controlled | Fixed LLM backbone (e.g., Llama-7B) with LoRA applied to attention layers | Fixed across experiments |
| Number of clients | Controlled | Total participating clients in federation | 20-100 clients |
| Aggregation frequency | Controlled | Rounds between global aggregation | Every 5 local epochs |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Resource-based rank selection
    ↓ (clients select rank r_i based on device memory/compute, NOT data)
Step 2: Heterogeneous client ranks established
    ↓ (ranks vary: r_i ∈ {4, 8, 16, 32, 64} across clients)
Step 3: Rank-proportional privacy budget allocation
    ↓ (ε_i = ε_total × r_i / Σr_j for each client)
Step 4: Rank-aware noise calibration
    ↓ (σ_i calibrated per client's rank-specific sensitivity)
Outcome: Improved privacy-utility tradeoff → Higher task accuracy
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | FlexLoRA (Bai 2024) | SVD-based rank adjustment for heterogeneous clients; ranks determined by device capability | Strong |
| Step 2 → Step 3 | Rate-distortion theory | Information-theoretic justification: allocate "bits" (privacy budget) proportionally to "complexity" (rank) | Medium |
| Step 3 → Step 4 | DP Survey (El Ouadrhiri 2022) | Gaussian mechanism: σ = Δf × √(2ln(1.25/δ)) / ε; sensitivity Δ scales with √r | Strong |
| Step 4 → Outcome | DP-FedLoRA (2025), Streaming DP (Dvijotham 2024) | Near-optimal noise allocation achieves competitive accuracy under strict privacy budgets | Strong |

**Key Tension:**
- **Tension:** FlexLoRA demonstrates accuracy benefits from heterogeneous ranks, but DP-FedLoRA shows that adding noise uniformly across LoRA matrices can negate these benefits. Uniform ε allocation ignores rank heterogeneity.
- **Resolution:** This verification plan tests whether rank-proportional budget allocation bridges this gap by matching privacy noise to adapter capacity, preserving FlexLoRA's benefits under DP constraints.

### 1.4 Key Assumptions

1. **Resource-based rank selection independence:**
   - Statement: Client ranks are determined by device resources (memory, compute), NOT by data characteristics
   - Evidence: FlexLoRA already implements resource-based rank selection
   - **Consequence if violated:** Privacy leaks through rank selection; adversary could infer data properties from observed ranks

2. **Moments accountant heterogeneous composition:**
   - Statement: Privacy loss can be accurately tracked across clients with different ε_i values
   - Evidence: Standard moments accountant (Abadi et al.) supports per-sample privacy budgets
   - **Consequence if violated:** Total privacy guarantee (ε_total, δ) becomes invalid; privacy claims unsupportable

3. **SVD aggregation privacy preservation:**
   - Statement: SVD truncation during aggregation does not introduce significant additional privacy loss
   - Evidence: Post-processing theorem in DP (deterministic operations on DP outputs remain DP)
   - **Consequence if violated:** Additional privacy loss accumulates; need separate privacy accounting for aggregation

4. **Linear rank-expressiveness relationship:**
   - Statement: LoRA adapter expressiveness scales approximately linearly with rank in range 4-64
   - Evidence: FlexLoRA experiments show consistent capacity-performance relationship
   - **Consequence if violated:** Budget allocation formula needs non-linear adjustment; suboptimal noise distribution

### 1.5 Scope & Boundaries

**Where this hypothesis applies:**
- Federated LoRA fine-tuning scenarios with heterogeneous client resources
- Parameter-efficient fine-tuning of foundation models (LLMs, LVMs)
- Privacy-sensitive domains requiring formal DP guarantees (healthcare, finance, legal)
- Client populations with diverse computational capabilities (edge to server)

**Where it does NOT apply:**
- Full model fine-tuning (non-adapter methods)
- Homogeneous client settings where uniform allocation is naturally optimal
- Scenarios where rank must be data-dependent (e.g., complexity-adaptive methods)
- Very small client populations (< 10) where privacy amplification is limited

**Known limitations:**
- Requires rank diversity across clients for budget heterogeneity to matter
- May need minimum number of clients for meaningful privacy amplification
- Implementation complexity in privacy accounting for heterogeneous ε
- Potential interaction effects with secure aggregation not fully characterized

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Task Accuracy vs Uniform Baseline)**:
Under the same total privacy budget ε_total, our rank-proportional allocation will achieve higher task accuracy than uniform allocation.

*Measurement*:
- Task accuracy improvement > 2-5% with p < 0.05
- Statistical test: Paired t-test across 5+ random seeds
- Minimum n ≥ 25 experimental runs

*Success Criteria for Phase 2B*:
- Primary: Accuracy improvement > 2% at ε_total=3 (p < 0.05)
- Falsification: Accuracy improvement < 0.5% OR negative improvement triggers rejection

**Secondary Predictions:**

**P2 (Mechanism Validation - Noise Distribution)**:
Higher-rank clients will receive proportionally tighter effective privacy budgets, and this allocation will not degrade their individual performance below baseline.

**P3 (Robustness Across Privacy Budgets)**:
Accuracy advantage of rank-proportional allocation will be consistent across ε_total ∈ {1, 3, 5, 8} with larger advantages at stricter budgets.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure**: Task accuracy with RA-DP-FL ≤ uniform allocation accuracy
2. **Mechanism Failure**: No correlation between rank and effective privacy budget
3. **Privacy Failure**: Total privacy guarantee cannot be maintained under heterogeneous ε composition
4. **Scalability Failure**: Benefits disappear with increasing client count (> 50 clients)

### 1.7 SOTA Baseline

**Mode:** Absolute Performance (No SOTA comparison target)

Comparison baselines:
- Uniform ε allocation with DP-SGD on LoRA
- FedASK double-sketching approach (complementary method)
- Non-private FlexLoRA (upper bound on accuracy)

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Expected effect size (Cohen's d): 0.5-0.8 (medium to large)
- Required experimental runs: n ≥ 25 (5 seeds × 5 ε values)
- Statistical power: 0.8

**Test Specification:**
- Method: Paired t-test (same random seeds, same data splits)
- Significance level: α = 0.05 (one-tailed, testing improvement)
- Report format: Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does rank-proportional privacy budget allocation improve task accuracy over uniform allocation under heterogeneous federated LoRA fine-tuning?"
- Maps to: Primary prediction P1
- Verification type: Empirical (comparative experiment)
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the proposed 4-step causal mechanism the actual cause of the accuracy improvement?"
- Maps to: Causal mechanism (N=4 steps)
- Will decompose into 4 sub-hypotheses in Phase 2B:
  - H-M1: Resource-based rank selection prevents privacy leakage
  - H-M2: Rank-proportional budget allocation follows information-theoretic principles
  - H-M3: Rank-aware noise calibration achieves tighter bounds than uniform
  - H-M4: Optimal noise distribution yields better accuracy at same total ε
- Verification type: Causal analysis (ablation studies)

**SH3 (Comparison):**
"Does RA-DP-FL provide complementary benefits to existing approaches (FedASK) and outperform naive baselines?"
- Maps to: Secondary predictions P2, P3
- Verification type: Comparative empirical
- Critical: Determines practical value and positioning

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-RA-DP-FL-v1
- [x] Confidence level specified: 0.85
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=4 steps, evidence table complete)
- [x] Causal chain length (N=4) determined and stored
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 predictions with primary marked)
- [x] Falsification criteria are defined (4 failure modes)
- [x] Baselines are identified for comparison (Uniform DP, FedASK, Non-private FlexLoRA)
- [x] SH1, SH2, SH3 are clear starting points for Phase 2B

### Open Questions

1. **Resource Requirements:**
   - What GPU memory is needed for Llama-7B + LoRA fine-tuning with DP?
   - Can experiments be run on consumer GPUs (RTX 3090/4090) or require A100?

2. **Data Availability:**
   - Are GLUE/SuperGLUE datasets with appropriate splits available?
   - Do we need domain-specific datasets (healthcare/finance) for practical validation?

3. **Implementation Complexity:**
   - How to integrate moments accountant for heterogeneous ε across clients?
   - Is Opacus compatible with PEFT/LoRA out-of-box or needs modification?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
