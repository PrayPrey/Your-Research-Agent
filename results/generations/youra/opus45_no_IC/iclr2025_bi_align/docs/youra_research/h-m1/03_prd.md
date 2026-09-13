# Product Requirements Document: H-M1

**Hypothesis:** User Adaptation to AI Patterns
**Date:** 2026-08-10
**Author:** Anonymous
**Phase 2C Source:** 02c_experiment_brief.md
**Type:** MECHANISM

---

## Executive Summary

This PRD specifies requirements for testing whether users adapt their communication complexity based on AI response patterns. The experiment analyzes lagged cross-correlation between AI complexity at turn t and user complexity at turn t+1 to detect temporal dependency indicating user adaptation behavior.

**Success Gate:** User-AI lagged correlation p < 0.05 with positive mean correlation.

---

## Problem Statement

### Background
H-E1 established that BCS (Bidirectional Communication Synchrony) is computable with meaningful variance (SD=0.569, n=26,395). The next question: does this synchrony emerge from actual adaptation behavior?

### Hypothesis
Users adapt communication complexity based on AI response patterns, detectable via significant lagged correlation (AI leads, User follows).

### Core Question
Is there a temporal dependency where AI complexity at turn t predicts user complexity at turn t+1?

---

## Functional Requirements

### FR-1: Data Loading and Reuse
**Priority:** P0 (Critical)

1.1. Load H-E1 checkpoint with precomputed complexity values
- Source: `h-e1/results/bcs_checkpoint.pkl`
- Fallback: Reload from `Anthropic/hh-rlhf` and recompute

1.2. Extract per-turn complexity trajectories
- User complexity: `user_complexity[t]` for each turn
- AI complexity: `ai_complexity[t]` for each turn

1.3. Organize as conversation-level time series
- Minimum 4 aligned turn pairs per conversation
- Expected: 26,395 conversations (matching H-E1)

### FR-2: Lagged Cross-Correlation Analysis
**Priority:** P0 (Critical)

2.1. Implement lagged correlation function
```python
def compute_lagged_correlation(user, ai, lag=1):
    # AI[t] correlates with User[t+lag]
    aligned_ai = ai[:-lag]
    aligned_user = user[lag:]
    return pearsonr(aligned_ai, aligned_user)
```

2.2. Compute lag-1 correlation per conversation
- Positive lag = AI leads User
- Handle edge cases: zero variance, insufficient length

2.3. Support lag range [-3, +3] for full analysis
- Primary focus: lag=1 (AI → User adaptation)

### FR-3: Statistical Hypothesis Testing
**Priority:** P0 (Critical)

3.1. One-sample t-test on lag-1 correlations
- H0: mean lag-1 correlation = 0
- H1: mean lag-1 correlation ≠ 0 (two-tailed)
- Gate criterion: p < 0.05

3.2. Compute effect size (Cohen's d)
- d = mean / std

3.3. Report confidence intervals
- 95% CI for mean lag-1 correlation

### FR-4: Baseline Validation (Shuffled Turns)
**Priority:** P0 (Critical)

4.1. Implement shuffled baseline
```python
def shuffle_baseline(ai_complexity):
    shuffled = ai_complexity.copy()
    np.random.shuffle(shuffled)
    return shuffled
```

4.2. Compute lag-1 correlation on shuffled data
- Expected: correlation ~ 0, p > 0.10

4.3. Run 1000 permutation shuffles
- Build null distribution for comparison

### FR-5: Multi-Lag Analysis
**Priority:** P1 (Important)

5.1. Compute correlations for lags -3 to +3
- Negative lag: User leads AI
- Positive lag: AI leads User

5.2. Identify peak lag
- Expected: peak at lag=1 if user adaptation exists

5.3. Compare lag-1 vs lag-2 vs lag-3 effect sizes
- Verify immediacy of adaptation

### FR-6: Conversation Length Analysis
**Priority:** P2 (Nice-to-have)

6.1. Stratify by conversation length bins
- Short: 4-6 turns
- Medium: 7-10 turns
- Long: 11+ turns

6.2. Test if longer conversations show stronger adaptation
- Hypothesis: more turns = more adaptation opportunity

---

## Non-Functional Requirements

### NFR-1: Performance
- Process 26,395 conversations in < 60 minutes
- Parallelize per-conversation analysis (multiprocessing)

### NFR-2: Reproducibility
- Fixed random seed for shuffling (seed=42)
- Save all intermediate results to checkpoint

### NFR-3: Memory
- Maximum 8GB RAM usage
- Stream processing for large conversation sets

### NFR-4: Robustness
- Handle zero-variance edge cases gracefully
- Filter conversations with < 3 aligned turn pairs

---

## Success Criteria

### Primary Gate (MUST_WORK)
| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Lag-1 p-value | p < 0.05 | One-sample t-test |
| Lag-1 direction | positive | Mean correlation > 0 |
| Shuffled baseline | p > 0.10 | Null validation |

### Secondary Criteria
| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Effect size | d > 0.1 | Cohen's d |
| Lag immediacy | lag-1 > lag-2 | Effect comparison |
| Sample size | n > 10,000 | Valid correlations |

---

## Dependencies

### Input Dependencies
| Dependency | Source | Status |
|------------|--------|--------|
| H-E1 checkpoint | `h-e1/results/bcs_checkpoint.pkl` | Required |
| Complexity metric | Validated in H-E1 | Reuse |
| HH-RLHF dataset | HuggingFace | Fallback |

### Output Artifacts
| Artifact | Path | Description |
|----------|------|-------------|
| Results checkpoint | `h-m1/results/lag_analysis.pkl` | All correlations |
| Gate report | `h-m1/04_validation.md` | Pass/fail analysis |
| Figures | `h-m1/figures/` | Visualizations |

---

## Evaluation Metrics

### Primary Metrics
1. **Mean lag-1 correlation** - Central measure of adaptation strength
2. **P-value** - Statistical significance (gate criterion)
3. **Cohen's d** - Effect size for practical significance

### Secondary Metrics
4. **Median lag-1 correlation** - Robust central tendency
5. **Lag profile** - Correlations across lag range
6. **Length-stratified correlations** - Adaptation vs conversation length

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| R1: Metric noise | Medium | Use robust median alongside mean |
| R2: Insufficient long conversations | Low | Already filtered in H-E1 |
| R3: Spurious correlation | High | Shuffled baseline validation |

---

## Appendix: Phase 2C Traceability

| Phase 2C Item | PRD Section |
|---------------|-------------|
| Dataset: Anthropic/hh-rlhf | FR-1 |
| Baseline: Shuffled turns | FR-4 |
| Proposed: Lagged correlation | FR-2 |
| Primary metric: t-test p-value | FR-3 |
| Gate: p < 0.05 | Success Criteria |
| Ablation: Multi-lag analysis | FR-5 |
| Ablation: Length stratification | FR-6 |

---

*Generated for Phase 3 Implementation Planning*
*Next: Architecture Document (03_architecture.md)*
