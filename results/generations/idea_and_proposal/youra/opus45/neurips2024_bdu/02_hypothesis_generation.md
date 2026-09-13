# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-PPN-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under moderate-to-high dimensional Bayesian optimization settings (50-500 dimensions), if foundation model surrogates are conditioned on LLM-extracted semantic priors through attention-based integration with adaptive weighting, then sample efficiency (measured by simple regret) will improve by at least 20% compared to unconditioned baselines, because hierarchical prior integration enables exploitation of domain knowledge while the adaptive mechanism prevents prior-data conflict.

**Alternative Hypothesis (H0):**
Conditioning foundation model surrogates on LLM-extracted priors provides no statistically significant improvement in sample efficiency compared to unconditioned baselines (GIT-BO), and any observed improvements are attributable to random variation or confounding factors rather than the proposed hierarchical prior integration mechanism.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| LLM prior conditioning strength | Independent | Attention weight magnitude (0-1 scale) applied to LLM prior embeddings in cross-attention layer | 0.0 (no prior), 0.3 (weak), 0.5 (moderate), 0.7 (strong), 1.0 (full) |
| Prompt template type | Independent | Three standardized templates: constraint elicitation, region suggestion, heuristic encoding | {constraint, region, heuristic} |
| Problem dimensionality | Independent | Number of input dimensions in optimization problem | 50, 100, 200, 500 dimensions |
| Simple regret | Dependent | f(x*) - f(x_best) at fixed evaluation budget | Lower is better; expect 20%+ reduction vs baseline |
| Prior-data agreement score | Dependent | Cosine similarity between LLM prior prediction and surrogate prediction | [-1, 1]; expect >0.5 for informative priors |
| Foundation model architecture | Controlled | TabPFN v2 with frozen base weights | Fixed |
| LLM choice | Controlled | Claude 3.5 Sonnet for prior elicitation | Fixed |
| Benchmark suite | Controlled | Synthetic (Hartmann, Rosenbrock) + Real (MOPTA08, Rover) | Fixed |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: LLM Prior Extraction → Semantic Prior Embedding
    ↓
Step 2: Semantic Prior Embedding → Conditioned Surrogate Predictions
    ↓
Step 3: Conditioned Surrogate + Adaptive Weighting → PEAF Acquisition
    ↓
Outcome: Improved Sample Efficiency (Lower Regret)
```

**Step 1: LLM Prior Extraction → Semantic Prior Embedding**
- Mechanism: LLM processes problem description via standardized prompt templates and generates structured prior information
- Evidence: LLM-BI (2025), Eliciting Priors (2024) demonstrate successful prior extraction

**Step 2: Semantic Prior Embedding → Conditioned Surrogate Predictions**
- Mechanism: Cross-attention integrates prior embeddings with TabPFN's context encoding
- Evidence: GIT-BO (2025) shows TabPFN accepts external conditioning signals

**Step 3: Conditioned Surrogate + Adaptive Weighting → PEAF Acquisition**
- Mechanism: Adaptive weight α balances prior exploitation vs surrogate exploration
- Evidence: Predictive coding literature (2024-2025) supports hierarchical Bayesian inference

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | LLM-BI (2025), Eliciting Priors (2024) | LLMs extract meaningful probabilistic priors | Strong |
| Step 2 → Step 3 | GIT-BO (2025) | TabPFN accepts conditioning while maintaining zero-shot capability | Strong |
| Step 3 → Outcome | Direct Regret Optimization (2025) | Acquisition design directly impacts regret | Medium |

**Key Tension:**
- **Tension:** GIT-BO achieves strong results using gradient-based active subspace *without* LLM priors. Do LLM priors add value beyond gradient information?
- **Resolution:** Test whether LLM priors provide *complementary* information, particularly in early iterations where gradient estimates are noisy.

### 1.4 Key Assumptions

1. **LLMs contain useful domain knowledge for optimization problems**
   - Evidence: LLM-BI (2025), Eliciting Priors (2024)
   - Consequence if Violated: Prior embeddings uninformative; adaptive weighting mitigates but doesn't eliminate risk

2. **TabPFN architecture can accept cross-attention conditioning**
   - Evidence: GIT-BO (2025), standard transformer practices
   - Consequence if Violated: Need alternative conditioning mechanism

3. **Prediction error provides meaningful acquisition signal**
   - Evidence: Predictive coding literature (2024-2025)
   - Consequence if Violated: PEAF underperforms standard acquisition functions

4. **Adaptive weighting correctly handles prior-data disagreement**
   - Evidence: Bayesian model averaging, CogLinks (2025)
   - Consequence if Violated: System follows incorrect priors despite contradicting data

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Moderate-to-high dimensional BO (50-500 dimensions)
- Domains where LLM has semantic knowledge (NAS, HPO, drug discovery)
- Settings where sample efficiency is critical

**Where Hypothesis Does NOT Apply:**
- Very low dimensional problems (d < 20)
- Very high dimensional problems (d > 500)
- Novel/random functions where LLM has no knowledge
- Real-time applications (<100ms latency required)

**Known Limitations:**
- LLM inference cost (~$0.01-0.10 per iteration)
- Requires prompt engineering for new domains
- Prior quality depends on LLM's domain knowledge

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Sample Efficiency vs GIT-BO Baseline)**:
PPN will achieve at least 20% lower simple regret than GIT-BO at 100 iterations on benchmarks where LLM has domain knowledge.

*Measurement*: Simple regret at t=100, paired t-test (n≥20 seeds), p < 0.05, Cohen's d > 0.5

*Success Criteria*: Regret reduction ≥ 20% (p < 0.05)
*Falsification*: Regret reduction < 5% OR performance degradation

**Secondary Predictions:**

**P2 (Early-Stage Advantage)**:
Performance advantage will be most pronounced in early iterations (t < 50), diminishing as data accumulates.

**P3 (Adaptive Weighting Robustness)**:
With misleading priors, adaptive weighting recovers to within 10% of baseline; fixed weighting shows >30% degradation.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if:
1. **Primary Failure**: Regret reduction < 5% vs GIT-BO (p > 0.05)
2. **Mechanism Failure**: Conditioned TabPFN shows >10% degradation on regression tasks
3. **Robustness Failure**: Adaptive weighting fails to recover with adversarial priors (>50% degradation)

### 1.8 Statistical Verification Design

**Sample Size**: n ≥ 20 random seeds per method per benchmark
**Statistical Test**: Paired t-test, α = 0.05 (one-tailed), Bonferroni correction
**Effect Size**: Cohen's d > 0.5 (medium)
**Report Format**: Mean ± Std Dev, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does LLM prior conditioning produce measurably different predictions compared to unconditioned baselines?"
- Verification type: Empirical
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is the proposed 3-step hierarchical mechanism the actual cause of improvement?"
- Decomposes to 3 sub-hypotheses (H-M1, H-M2, H-M3)
- Verification type: Causal/ablation analysis

**SH3 (Comparison):**
"Does PPN outperform GIT-BO, SAASBO, TuRBO on standard benchmarks?"
- Verification type: Comparative empirical

**Total sub-hypotheses in Phase 2B:** 5 (SH1 + H-M1 + H-M2 + H-M3 + SH3)

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-PPN-v1
- [x] Confidence level: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables operationalized
- [x] Causal mechanism with evidence (N=3 steps)
- [x] Key tension identified with resolution
- [x] Assumptions list consequences if violated
- [x] 3 testable predictions (P1 primary)
- [x] 3 falsification criteria defined
- [x] 5 baselines identified
- [x] SH1/SH2/SH3 ready for decomposition

### Open Questions

1. **Implementation:** Exact cross-attention conditioning architecture for TabPFN?
2. **Prompts:** Should templates be problem-specific or generic?
3. **Adaptive Weight:** Learned end-to-end or analytical computation?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (YOLO Mode)*
*2026-02-13*
