# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-PACPA-v1
**Confidence Level:** 0.82 (High)

**Main Hypothesis:**
Under constrained autoregressive generation settings (extractive QA, code completion, entity extraction), if position-adaptive conformal prediction with entropy-weighted nonconformity scores is applied to LLM outputs, then the framework will achieve distribution-free coverage guarantees (≥90% for α=0.1) with smaller prediction sets than sampling-based approaches, because position stratification enables approximate exchangeability within strata while leveraging the informativeness of LLM logits for conformity scoring.

**Alternative Hypothesis (H0):**
Position-adaptive nonconformity scores provide no improvement over position-agnostic conformal prediction for autoregressive text generation—either coverage guarantees fail to hold empirically, or prediction set sizes are equivalent to or larger than sampling-based ensemble methods.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Nonconformity score function | Independent | Entropy-weighted logit-based scoring computed from LLM output distributions | Score types: entropy-weighted, raw logit, hidden-state based |
| Position adaptation mechanism | Independent | Position stratification with entropy-based reweighting across sequence positions | Stratification schemes: uniform bins (5-10), adaptive percentile-based |
| Calibration set design | Independent | Domain-specific labeled examples with position-stratified sampling | ~500 samples per stratum minimum |
| Coverage rate | Dependent | Proportion of test instances where ground truth falls within prediction set | Target: ≥90% for α=0.1 |
| Prediction set size | Dependent | Average number of candidate responses in prediction set | Target: <50% of pure sampling baseline |
| Computational overhead | Dependent | Additional inference time relative to standard generation | Target: ≤30% overhead |
| LLM access type | Controlled | Grey-box (logits) or white-box (hidden states) | Fixed per experiment |
| Task domain | Controlled | Constrained generation tasks only | SQuAD, HumanEval, CoNLL NER |
| Distribution shift | Confounding | Difference between calibration and test distributions | Monitored via calibration diagnostics |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Position Stratification → Approximate Exchangeability → Valid Coverage Guarantees → Smaller Prediction Sets
        ↓                         ↓                              ↓
   [Step 1]                  [Step 2]                       [Step 3]
```

**Step 1: Position Stratification → Approximate Exchangeability**
Tokens within the same position stratum share similar uncertainty characteristics due to autoregressive generation dynamics. Stratifying by position groups approximately exchangeable tokens together.

**Step 2: Approximate Exchangeability → Valid Coverage Guarantees**
Standard CP theory provides marginal coverage when data is approximately exchangeable within strata (ResCP precedent, Candès et al. 2025).

**Step 3: Entropy-Weighted Scoring → Smaller Prediction Sets**
Entropy captures token-level uncertainty; weighting by entropy focuses conformity on informative positions, reducing set size while maintaining coverage.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Neglia et al. 2025 (ResCP) | Position-adaptive reweighting achieves asymptotic conditional coverage | Strong |
| Step 1 → Step 2 | Candès et al. 2025 (Stanford) | Enhanced CP methods provide conditional validity for LLMs | Strong |
| Step 2 → Step 3 | ConU (EMNLP 2024) | Self-consistency + CP achieves strict coverage on 7 LLMs, 4 datasets | Strong |
| Full chain | Liu et al. 2025 Survey | Taxonomy validates prediction uncertainty measurable from outputs | Strong |

**Key Tension:**
- **Tension:** ConU achieves coverage without position adaptation, suggesting position may not be necessary.
- **Resolution:** This plan tests whether position adaptation provides conditional structure for more efficient coverage.

### 1.4 Key Assumptions

1. **Approximate exchangeability within position strata**
   - Consequence if violated: Coverage < 1-α empirically

2. **LLM logit distributions encode sufficient conformity information**
   - Consequence if violated: Prediction sets vacuously large

3. **Calibration set representative of test distribution**
   - Consequence if violated: Coverage degradation from distribution shift

4. **Grey-box/white-box access provides reliable logits**
   - Consequence if violated: Method restricted to white-box settings

5. **Position stratification captures uncertainty structure**
   - Consequence if violated: No benefit over position-agnostic CP

### 1.5 Scope & Boundaries

**Applies to:**
- Constrained generation: extractive QA, code completion, entity extraction
- Grey-box or white-box LLM access
- Tasks with well-defined ground truth
- Sequence lengths up to 512 tokens

**Does NOT apply to (Future Work):**
- Open-ended generation (creative writing, dialogue)
- Black-box LLMs without logit access
- Tasks without clear ground truth

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Coverage Rate)**:
Position-adaptive CP will achieve ≥90% coverage (α=0.1) on constrained generation benchmarks.

*Measurement*: Coverage ≥ 90% with p < 0.05; n ≥ 500 test instances
*Success Criteria*: Coverage ≥ 90% (p < 0.05)
*Falsification*: Coverage < 85% triggers rejection

**Secondary Predictions:**

**P2 (Set Efficiency)**: 20-50% smaller prediction sets than position-agnostic CP at same coverage.

**P3 (Computational Efficiency)**: ≤30% overhead vs standard sampling.

**Falsification Criteria:**

1. **Primary Failure**: Coverage < 85%
2. **Mechanism Failure**: Set size reduction < 10%
3. **Efficiency Failure**: Overhead > 50%

### 1.8 Statistical Verification Design

**Sample Size:**
- Test instances: n ≥ 500 (power = 0.8, α = 0.05)
- Calibration set: ~2500 total (500 per stratum × 5 strata)

**Tests:**
- P1: One-sample proportion test
- P2: Paired t-test
- P3: Descriptive statistics

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does position-adaptive CP achieve ≥90% coverage on constrained autoregressive generation?"
- Verification: Empirical on SQuAD, HumanEval, CoNLL NER
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is position stratification with entropy-weighted scoring the mechanism enabling valid coverage with smaller sets?"
- Decomposes to N=3 sub-hypotheses:
  - H-M1: Position stratification → Approximate exchangeability
  - H-M2: Approximate exchangeability → Valid coverage
  - H-M3: Entropy weighting → Smaller prediction sets
- Verification: Ablation studies

**SH3 (Comparison):**
"Does position-adaptive CP outperform baselines on coverage-efficiency trade-off?"
- Verification: Comparative evaluation
- Critical: Determines practical value

**Total Sub-Hypotheses:** 2 + 3 = 5

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-PACPA-v1
- [x] Confidence level: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] Variables operationalized
- [x] Causal mechanism (N=3) with evidence
- [x] Key tension + resolution
- [x] Assumptions with consequences
- [x] Testable predictions (P1 primary, P2/P3 secondary)
- [x] Falsification criteria (3 conditions)
- [x] Baselines identified (4)
- [x] SH1/SH2/SH3 defined

### Open Questions

1. **Calibration Set:** Optimal stratification scheme for different domains?
2. **Efficiency:** Can entropy-weighted scoring achieve <30% overhead?
3. **Priority:** Test SH1 first or run mechanism ablations in parallel?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
