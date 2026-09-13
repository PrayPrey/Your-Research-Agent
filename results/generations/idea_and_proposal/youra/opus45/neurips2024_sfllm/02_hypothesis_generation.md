# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-CAC-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under the condition that multiple LLM audits (uncertainty, fairness, privacy, provenance) are required simultaneously, if we standardize each audit output into a certificate format with explicit validity conditions and apply composition operators (Conservative Šidák or Adaptive correlation-aware), then the joint guarantee will be provably valid and tighter than naive Bonferroni correction because certificate abstraction enables formal composition rules that exploit shared sample structure and non-negative correlations between audit outcomes.

**Alternative Hypothesis (H0):**
There is no systematic advantage to composing audit certificates over naive Bonferroni correction; the joint guarantee α_joint ≈ k × α_i (Bonferroni bound) cannot be improved without making strong assumptions about correlation structure that are difficult to verify in practice.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Number of audit dimensions (k) | Independent | Count of distinct audit types applied simultaneously | k ∈ {2, 3, 4} |
| Individual confidence levels (α_i) | Independent | Per-certificate Type I error rate | α_i ∈ [0.01, 0.10] |
| Sample size (n) | Independent | Number of LLM outputs sampled for auditing | n ∈ [100, 10000] |
| Joint confidence level (α_joint) | Dependent | Probability that all k certificates hold simultaneously | α_joint ∈ [0, 1] |
| Composition tightness ratio | Dependent | α_joint(CAC) / α_joint(Bonferroni), lower indicates better composition | Expected: 0.6-0.9 |
| LLM model | Controlled | Fixed model for all experiments | GPT-4, Llama-3-70B |
| Task distribution | Controlled | Fixed task type and prompt distribution | Standardized benchmark tasks |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
[Certificate Abstraction] → [Validity Hierarchy] → [Composition Operators] → [Provable Joint Guarantees]
```

**Step 1: Certificate Abstraction → Standardized Interface**
By defining AuditCertificate(S, θ, α, C) with sample set, statistic, confidence level, and validity conditions, we create a uniform interface that enables formal reasoning about composition.

**Step 2: Validity Hierarchy → Condition Compatibility**
The shared interface allows us to define validity levels (L1: output sampling, L2: i.i.d., L3: exchangeable). Composition operates at min(Level(C1), Level(C2)).

**Step 3: Composition Operators → Joint Guarantees**
Conservative Mode: Šidák correction α_joint = 1 - (1-α)^k. Adaptive Mode: Empirical correlation yields tighter bounds when n > n_min.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Cederbladh et al. 2023 | Compositional V&V works with well-defined interfaces | Strong |
| Step 2 → Step 3 | Simes 1986, Šidák 1967 | Šidák less conservative than Bonferroni for correlated tests | Strong |
| Step 3 → Outcome | UCF Framework | Parsimony principle validated for multi-aspect controls | Medium |

**Key Tension:**
- **Tension:** Šidák assumes non-negative correlation, but audit correlation structures may be complex.
- **Resolution:** Two-tier design: Conservative mode valid under non-negative correlation, Adaptive requires n > 1000. Graceful degradation to Bonferroni ensures validity.

### 1.4 Key Assumptions

1. **A1: I.I.D. Output Sampling** - LLM outputs can be sampled i.i.d. from deployment distribution
   - Consequence if violated: CP coverage guarantees break; must use conditional CP methods

2. **A2: Valid Audit Primitives** - Individual audit methods satisfy their stated guarantees
   - Consequence if violated: Composition of invalid guarantees remains invalid

3. **A3: Non-negative Correlation** - Audit dimensions have ρ ≥ 0
   - Consequence if violated: Šidák becomes anti-conservative; fall back to Bonferroni

### 1.5 Scope & Boundaries

**Applies to:** Black-box LLM auditing, multi-aspect scenarios (≥2 dimensions), regulated deployment settings
**Does NOT apply to:** White-box audits, single-point queries, real-time auditing, strong negative correlations
**Limitations:** Conservative mode may over-correct by ~35%; Adaptive requires n > 1000

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Composition Tightness):** When k=4 certificates are composed using CAC Conservative mode, α_joint(CAC) / α_joint(Bonferroni) < 0.9 with p < 0.05.

**Secondary Predictions:**
**P2 (Validity Preservation):** Actual joint failure rate ≤ α_joint with 95% confidence when validity hierarchy respected.
**P3 (Adaptive Improvement):** When n > 1000 and ρ > 0.1, Adaptive mode ≥10% tighter than Conservative.

**Falsification Criteria:**
1. **Primary Failure:** Composition ratio ≥ 1.0 (no improvement over Bonferroni)
2. **Validity Failure:** Empirical failure rate > 1.2 × α_joint (anti-conservative)
3. **Integration Failure:** Cannot integrate ≥3 audit implementations into certificate format

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

*Not applicable - novel framework contribution. Baseline: Bonferroni correction.*

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 30 independent LLM output batches
**Test:** Paired comparison (CAC vs Bonferroni), α = 0.05 (two-tailed)
**Report:** Mean ratio, 95% CI, Cohen's d, p-value
**Validity:** Bootstrap simulation (1000 replicates)

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does the certificate abstraction successfully standardize outputs from heterogeneous audit methods (CP, BAFA, Unigram-WM, canary) while preserving their validity conditions?"

**SH2 (Mechanism):**
"Is the certificate composition mechanism (validity hierarchy + composition operators) the actual enabler of tighter-than-Bonferroni joint guarantees?"
- Decomposes into N=3 sub-hypotheses:
  - H-M1: Certificate abstraction creates composable units
  - H-M2: Validity hierarchy correctly identifies compatible conditions
  - H-M3: Šidák composition achieves tighter bounds for correlated audits

**SH3 (Comparison):**
"Does CAC composition provide practically meaningful improvement over naive Bonferroni correction across diverse LLM auditing scenarios?"

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-CAC-v1
- [x] Confidence level: 0.85
- [x] Alternative hypothesis (H0) defined
- [x] All variables operationalized
- [x] Causal mechanism with N=3 steps, evidence table
- [x] Key tension + resolution
- [x] Key assumptions with consequences
- [x] 3 testable predictions (P1 primary)
- [x] Falsification criteria defined
- [x] Baselines: Bonferroni, individual audits
- [x] SH1/SH2/SH3 clear

### Open Questions

1. **Resource Requirements:** Computational overhead of correlation estimation for k=4, n=10000?
2. **Data Availability:** Access to CivilComments, Bias-in-Bios, and watermarking test sets?
3. **Technical Feasibility:** Unified sampling protocol for audit methods with different requirements?
4. **Priority:** SH1 (foundation) → SH2 (mechanism) → SH3 (comparison)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
