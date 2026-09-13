# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1 - FEASIBLE)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-LEC-v1
**Confidence Level:** 0.78

**Main Hypothesis:**
Under conditions of diverse MDP-algorithm training pairs across multiple domains (Atari, MuJoCo, Procgen, BRIDGE), if a neural network predictor is meta-trained to predict algorithm-specific RL performance from MDP structural features and early training signals, then it will achieve significantly higher correlation with final algorithm performance (Pearson r > 0.7) than hand-crafted complexity measures (e.g., Effective Horizon r ≈ 0.5) because algorithm-specific complexity patterns can be learned from data rather than manually designed, capturing the algorithm-environment interaction that static measures miss.

**Alternative Hypothesis (H0):**
Hand-crafted complexity measures based on MDP structural properties alone (without algorithm-specific learning) achieve equivalent or higher correlation with final RL algorithm performance compared to meta-learned predictors, indicating that algorithm-environment interaction patterns are not learnable or do not provide additional predictive value.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| MDP structural features | Independent | State-action space size (log scale), reward sparsity (% non-zero), transition entropy (bits), episode length statistics (mean, std) | Continuous; extracted from environment spec |
| Algorithm identity | Independent | One-hot encoding of algorithm type | {PPO, DQN, SAC, TD3, A2C} |
| Early training signals | Independent | First 10% of training: return trajectory (5 points), gradient norm (mean, std), policy entropy (initial, final, slope) | 11-dimensional vector per run |
| Predicted final performance | Dependent | Correlation (Pearson r) between predicted and actual normalized final return | Target: r > 0.7 |
| MDP distribution | Controlled | Same procedural generators with different random seeds; stratified sampling | Atari (50), MuJoCo (8), Procgen (16), BRIDGE (155) |
| Algorithm implementations | Controlled | CleanRL standardized implementations with default hyperparameters | Fixed per algorithm |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: MDP features + Algorithm identity → Latent complexity representation
        ↓
Step 2: Latent complexity + Early training signals → Performance prediction
        ↓
Step 3: Meta-training across diverse MDPs → Generalizable predictor
        ↓
     [Outcome]: Superior correlation with actual algorithm performance
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Effective Horizon (Laidlaw 2023) | Q-value alignment under random policy predicts PPO/DQN success | Strong |
| Step 1 → Step 2 | Deadly Triad (van Hasselt 2018) | Same MDP produces different outcomes for different algorithms | Strong |
| Step 2 → Step 3 | Neural Complexity (NeurIPS 2020) | Meta-learned complexity outperforms manual design | Strong |
| Step 3 → Outcome | Meta-RL literature (2025) | Cross-domain meta-learning transfers patterns | Medium |

**Key Tension:**
- **Tension:** Effective Horizon (2023) shows hand-crafted measures *can* predict deep RL performance, but Neural Complexity (2020) shows meta-learned measures outperform hand-crafted ones in supervised learning.
- **Resolution:** This hypothesis directly tests whether the meta-learning advantage transfers to RL via head-to-head comparison on BRIDGE benchmark.

### 1.4 Key Assumptions

1. **MDP-algorithm performance relationships are learnable from finite training data**
   - Consequence if violated: Predictor achieves only random correlation; fundamental approach fails

2. **Early training signals (first 10%) contain sufficient information about final performance**
   - Consequence if violated: Must use larger training fraction (higher cost)

3. **Structural MDP features can be extracted efficiently from environment specifications**
   - Consequence if violated: Feature extraction becomes bottleneck

4. **Performance patterns transfer across different MDP distributions**
   - Consequence if violated: Predictor overfits to training domains

### 1.5 Scope & Boundaries

**Applies to:** Standard RL benchmarks (Atari, MuJoCo, Procgen), model-free algorithms (PPO, DQN, SAC, TD3, A2C), single-agent settings

**Does NOT apply to:** Model-based RL, real-world robotics without simulation, multi-agent RL, continuous learning

**Limitations:** Requires 10% training for early signals; no theoretical guarantees; meta-training cost ~100-500 GPU-hours

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Correlation vs Baselines):** LEC achieves Pearson r > 0.70 on held-out test MDPs, exceeding Effective Horizon baseline (r ≈ 0.50).

*Measurement:* Fisher z-transformation for correlation comparison, p < 0.05, n ≥ 150 predictions
*Success Criteria:* r > 0.70 (p < 0.05)
*Falsification:* r ≤ 0.55

**Secondary Predictions:**
**P2 (Algorithm Selection):** Correctly identify best-performing algorithm with accuracy > 70%
**P3 (Cross-Domain Transfer):** Multi-domain training exceeds single-domain correlation

**Falsification Criteria:**
1. **Primary Failure:** r ≤ 0.55 on held-out test MDPs
2. **Mechanism Failure:** Early signals provide no improvement over static-only baseline
3. **Transfer Failure:** Cross-domain training performs worse than single-domain

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 30 MDPs per domain × 4 domains = 120 MDPs minimum
**Test:** Fisher z-transformation, α = 0.05 (one-tailed)
**Report:** r ± 95% CI, Δr (LEC - baseline), Cohen's q

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does the meta-learned LEC predictor achieve statistically significant correlation (r > 0.55, p < 0.05) with final RL algorithm performance on held-out MDPs?"
- Maps to: Primary prediction P1
- Verification: Empirical correlation analysis
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is the proposed 3-step causal mechanism responsible for LEC's predictive performance?"
- Decomposes into N=3 sub-hypotheses:
  - **H-M1:** Static MDP+algorithm encoding contributes to prediction
  - **H-M2:** Early training signals improve over static-only baseline
  - **H-M3:** Multi-domain training improves over single-domain
- Verification: Ablation studies

**SH3 (Comparison):**
"Does LEC outperform Effective Horizon baseline and enable practical algorithm selection?"
- Maps to: P2, P3
- Verification: Comparative empirical

**Total Sub-Hypotheses:** 5 (SH1, H-M1, H-M2, H-M3, SH3)

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-LEC-v1
- [x] Confidence: 0.78
- [x] H0 defined
- [x] Variables operationalized
- [x] Causal mechanism with evidence (N=3)
- [x] Key tension + resolution
- [x] Assumptions with consequences
- [x] Testable predictions (3)
- [x] Falsification criteria (3)
- [x] Baselines identified
- [x] SH1/SH2/SH3 ready

### Open Questions

1. **Resources:** Exact GPU-hour cost for meta-training? Start with smaller-scale validation?
2. **Data:** Access to all benchmarks (Atari, MuJoCo, Procgen, BRIDGE)?
3. **Architecture:** Optimal predictor design (transformer vs RNN/CNN)?
4. **Priority:** Verify SH1 first or run ablations in parallel?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work (8 sources with full citations)

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
