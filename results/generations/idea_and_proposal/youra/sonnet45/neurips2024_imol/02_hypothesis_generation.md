# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-08
**Author:** Pray
**Source Round:** Round 2 (FEASIBLE)
**Hypothesis ID:** H-2.1
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-2.1
**Confidence Level:** 0.85 (High)

**Main Hypothesis:**
In intrinsically-motivated open-ended learning (IMOL) systems, an adaptive weighted ensemble combining multiple intrinsic motivation signals (RND for novelty detection, ICM for forward dynamics prediction, and Learning Progress for competence improvement) will achieve superior exploration efficiency and skill acquisition compared to single-signal approaches, where the superiority is measured by cumulative intrinsic reward, state coverage, and task completion rate across diverse environments.

**Alternative Hypothesis (H0):**
Single intrinsic motivation signals (RND-only, ICM-only, or Learning Progress-only) achieve equivalent or superior exploration efficiency and skill acquisition compared to adaptive weighted ensembles, or fixed equal-weight ensembles are sufficient without requiring adaptive weighting mechanisms.

### 1.2 Variables

| Variable Type | Variable Name | Measurement | Domain/Range |
|--------------|---------------|-------------|--------------|
| **Independent** | IM Signal Composition | Categorical: {RND-only, ICM-only, LP-only, Fixed-Ensemble, UCB-Adaptive, Meta-Adaptive} | 6 conditions |
| **Independent** | Environment Type | Categorical: {Sparse-Reward, Dense-Reward, Goal-Reaching, Procedural-Generation} | 4 environment classes |
| **Independent** | Adaptation Tier | Categorical: {Tier-1-Fixed, Tier-2-UCB, Tier-3-MetaLearning} | 3 tiers |
| **Dependent** | Exploration Efficiency | Continuous: State coverage rate (% unique states / timestep) | [0, 1] |
| **Dependent** | Skill Acquisition | Discrete: Number of distinct skills mastered (by threshold) | [0, ∞) |
| **Dependent** | Cumulative IM Reward | Continuous: ∫ r_intrinsic dt over episode | [0, ∞) |
| **Dependent** | Task Completion Rate | Continuous: Success % on held-out test tasks | [0, 1] |
| **Control** | RL Algorithm | Fixed: PPO with shared hyperparameters | - |
| **Control** | Network Architecture | Fixed: Shared feature extractor + policy/value heads | - |
| **Control** | Training Budget | Fixed: 10M environment steps per condition | - |
| **Moderating** | Signal Weight Distribution | Continuous: (w_RND, w_ICM, w_LP) where Σw=1 | Simplex in R³ |

### 1.3 Causal Mechanism

**Proposed Causal Chain:**

```
Multi-Signal IM Integration
    ↓
Diverse Exploration Strategies
    ↓
Complementary Coverage (RND=novelty, ICM=dynamics, LP=competence)
    ↓
Adaptive Weight Allocation (UCB bandit prioritizes effective signals)
    ↓
Environment-Specific Signal Relevance Matching
    ↓
Superior Exploration Efficiency + Skill Diversity
```

**Mechanism Explanation:**

1. **Multi-Signal Integration:** Three IM signals capture different exploration dimensions:
   - **RND** detects novel states (state-space coverage)
   - **ICM** rewards forward dynamics prediction errors (transition learning)
   - **Learning Progress** tracks competence improvement (mastery signals)

2. **Complementary Coverage:** Different environments favor different signals (sparse-reward → RND; dynamics-rich → ICM; skill-progression → LP). Ensemble coverage exceeds any single signal.

3. **Adaptive Weighting (UCB Bandit):** Treats each signal as a "bandit arm," allocating weights based on recent effectiveness (intrinsic reward magnitude), enabling environment-specific signal prioritization.

4. **Dynamic Adaptation:** UCB exploration-exploitation balance prevents premature signal commitment while exploiting currently effective signals.

**Evidence for Causal Links:**

- **Link 1-2 (Multi-Signal → Diversity):** CURIOUS (Colas et al. 2018) demonstrates modular IM signals enable diverse goal-directed behaviors
- **Link 2-3 (Diversity → Complementary Coverage):** Mirolli & Baldassarre (2013) taxonomy shows knowledge-based (RND) vs competence-based (LP) IM signals address distinct exploration failures
- **Link 3-4 (Complementary → Adaptive Allocation):** Prioritized Sampling (D'Eramo 2022) shows TD-error (a learning progress proxy) improves multi-task RL via adaptive task sampling
- **Link 4-6 (Adaptation → Superior Performance):** UCB bandit guarantees sublinear regret (Auer et al. 2002), ensuring near-optimal signal selection over time

**Key Tension:**

The hypothesis predicts adaptive weighting outperforms both single signals AND fixed ensembles. This requires:
1. **Sufficiently diverse environments** where no single signal dominates across all contexts
2. **Adaptation timescale** must match environment nonstationarity (too slow = ineffective; too fast = noise sensitivity)
3. **Signal complementarity** must exist (if signals are redundant, adaptation provides no benefit)

**Potential Confounds:**
- Computational overhead of UCB may offset benefits in simple environments
- Signal normalization/scaling affects effective weight ratios
- Exploration noise (ε-greedy) may dominate adaptive effects in early training

### 1.4 Key Assumptions

1. **Signal Independence Assumption:** RND, ICM, and LP provide sufficiently independent exploration signals (low correlation in state-action space)
   - **Justification:** Each signal uses distinct mechanisms (random features, forward model, progress tracking)
   - **Risk:** High correlation in simple environments may reduce complementarity

2. **Signal Comparability Assumption:** IM signals can be normalized to comparable reward scales for weighted summation
   - **Justification:** Z-score normalization with running statistics (standard in RL)
   - **Risk:** Extreme outliers or non-stationary distributions may violate comparability

3. **UCB Applicability Assumption:** Signal effectiveness can be measured via intrinsic reward magnitude for bandit feedback
   - **Justification:** Intrinsic rewards directly reflect signal utility
   - **Risk:** Delayed feedback (rewards manifest after exploration) may weaken UCB performance

4. **Stationarity Assumption (Moderate):** Signal effectiveness changes gradually enough for UCB to adapt
   - **Justification:** Environment dynamics typically stable within episodes
   - **Risk:** Sudden environment shifts may require faster adaptation (Tier 3 meta-learning addresses this)

5. **Skill Transfer Assumption:** Improved exploration translates to better skill acquisition and task performance
   - **Justification:** Exploration-exploitation balance is core RL principle
   - **Risk:** Chaotic exploration without goal structure may waste exploration

6. **Implementation Feasibility Assumption:** Each IM signal (RND, ICM, LP) can be implemented with comparable computational cost
   - **Justification:** All three are established methods with efficient implementations
   - **Risk:** ICM forward model may dominate compute in high-dimensional observations

### 1.5 Scope & Boundaries

**Included in Scope:**
- **Environments:** Continuous control (MuJoCo), discrete control (Atari sparse-reward subset), procedurally-generated (MiniGrid variants)
- **IM Signals:** RND, ICM, Learning Progress (absolute progress, not relative)
- **Adaptation Mechanisms:** Tier 1 (fixed weights), Tier 2 (UCB bandit), Tier 3 (meta-learning optional)
- **Evaluation:** Exploration metrics (state coverage, intrinsic rewards), task performance (success rate on downstream tasks)
- **Training Scale:** Up to 10M environment steps (standard RL research scale)

**Explicitly Excluded:**
- **Multi-Agent Settings:** Hypothesis focuses on single-agent IMOL (inter-agent IM signals require separate theory)
- **Extrinsic Reward Environments:** Testing sparse/zero-reward settings where IM dominates (dense extrinsic rewards may overshadow IM effects)
- **Lifelong/Continual Learning:** Catastrophic forgetting mitigation not addressed (future extension)
- **Real-World Robotics:** Simulated environments only (safety, cost, reproducibility)
- **Signal Design Space:** Limited to 3 established signals (not exploring novel IM signals)
- **Hierarchical RL:** Flat RL agents only (hierarchical goal generation out of scope)

**Boundary Conditions:**
- **Minimum Environment Complexity:** Requires sufficient state-space size for exploration to matter (excludes toy domains like CartPole)
- **Maximum Dimensionality:** Pixel-based observations up to 84×84×4 (Atari standard) due to RND/ICM compute constraints
- **Episode Length:** 100-1000 steps (short enough for UCB feedback, long enough for skill expression)

### 1.6 Testable Predictions

**Primary Prediction (P1):**
Tier 2 UCB-Adaptive ensemble will achieve **≥15% higher state coverage** and **≥20% higher task completion rate** compared to the best single-signal baseline (RND/ICM/LP-only) across at least 3 out of 4 environment types, measured at 10M training steps.

**Secondary Predictions:**

**P2 (Signal Complementarity):**
In sparse-reward environments, RND weights will dominate (w_RND > 0.5); in dynamics-rich environments (e.g., physics manipulation), ICM weights will dominate (w_ICM > 0.5); in skill-progression environments (curriculum), LP weights will dominate (w_LP > 0.5).

**P3 (Adaptation Benefit):**
UCB-Adaptive ensemble will outperform Fixed-Equal-Weight ensemble by **≥10% in cumulative intrinsic reward**, demonstrating the value of adaptive weighting beyond simple signal combination.

**P4 (Tier Comparison - Optional):**
If Tier 3 meta-learning is implemented, it will match or exceed Tier 2 UCB performance in non-stationary environments but show no significant gain in stationary environments (validating adaptation granularity).

**Falsification Criteria:**

The hypothesis is **FALSIFIED** if any of the following occur:

1. **No Ensemble Benefit:** UCB-Adaptive ensemble fails to outperform ALL single-signal baselines in ≥2 out of 4 environment types (suggests signals are redundant or harmful when combined)

2. **No Adaptation Benefit:** UCB-Adaptive shows no significant improvement over Fixed-Equal-Weight ensemble (p > 0.05 on cumulative IM reward), indicating adaptation overhead outweighs benefits

3. **Negative Transfer:** Ensemble performance is **worse** than the average of single-signal baselines (suggests destructive interference between signals)

4. **Signal Dominance Across All Environments:** One signal (e.g., RND) achieves >0.9 weight across all environments, showing no environment-specific adaptation

**Partial Support Criteria:**
- If ensemble benefits appear only in 1-2 environment types, hypothesis is **PARTIALLY SUPPORTED** (signal complementarity limited to specific contexts)

### 1.7 SOTA Baseline (Not Applicable - Novel Integration Hypothesis)

**Rationale for Omission:**
This hypothesis does not claim to surpass a specific state-of-the-art method but rather investigates whether adaptive multi-signal IM integration provides systematic benefits over single-signal approaches. The research question is about **signal composition strategy** (single vs. ensemble vs. adaptive ensemble) rather than competing with existing IMOL systems.

**Relevant Comparisons:**
- **CURIOUS (Colas 2018):** Uses modular architecture but fixed IM signal per module (no adaptive weighting)
- **Prioritized Sampling (D'Eramo 2022):** Uses adaptive task sampling (not signal weighting) in multi-task RL
- **RND (Burda 2019):** Single-signal SOTA for Atari sparse-reward exploration

Our hypothesis extends these by introducing **adaptive signal-level composition**, which is orthogonal to (and compatible with) existing IMOL architectures.

### 1.8 Statistical Verification Design

**Experimental Design:**
- **Type:** Factorial between-subjects design
- **Factors:**
  - Factor A: IM Condition (6 levels: RND-only, ICM-only, LP-only, Fixed-Ensemble, UCB-Adaptive, Meta-Adaptive*)
  - Factor B: Environment Type (4 levels: Sparse-Reward, Dense-Dynamics, Goal-Reaching, Procedural)
- **Replicates:** N=10 seeds per condition (standard RL practice)
- **Total Runs:** 6 × 4 × 10 = 240 runs (or 200 if Tier 3 excluded)

**Primary Statistical Tests:**

1. **Main Effect Test (P1 - Ensemble Superiority):**
   - **Method:** Two-way ANOVA with factors [IM Condition × Environment Type]
   - **Hypothesis:** Main effect of IM Condition on task completion rate (F-test, α=0.05)
   - **Post-hoc:** Tukey HSD to compare UCB-Adaptive vs. each single-signal baseline
   - **Effect Size:** Cohen's d ≥ 0.5 (medium effect) for practical significance

2. **Adaptation Benefit Test (P3 - UCB vs Fixed Ensemble):**
   - **Method:** Paired t-test comparing UCB-Adaptive vs. Fixed-Ensemble on cumulative IM reward
   - **Hypothesis:** μ_UCB > μ_Fixed (one-tailed test, α=0.05)
   - **Requirement:** p < 0.05 AND mean difference ≥10%

3. **Signal Weight Analysis (P2 - Environment-Specific Adaptation):**
   - **Method:** Multinomial logistic regression predicting dominant signal (w_max) from Environment Type
   - **Hypothesis:** Significant association (χ² test, α=0.05)
   - **Validation:** Inspect weight trajectories (w_RND, w_ICM, w_LP over time) per environment

**Metrics & Collection:**

| Metric | Collection Frequency | Aggregation |
|--------|---------------------|-------------|
| State Coverage | Every 100k steps | Cumulative unique states / total states |
| Task Completion Rate | End of training + evaluation | % success on 100 held-out test episodes |
| Cumulative IM Reward | Every episode | Sum over training |
| Signal Weights (w_RND, w_ICM, w_LP) | Every 10k steps | Mean & std over 10 seeds |
| Skill Count | End of training | Threshold-based (success on N distinct task variants) |

**Sample Size Justification:**
- N=10 seeds balances statistical power (detect d=0.5 with 80% power) and computational cost (240 runs = ~2-3 GPU-weeks)
- ANOVA power analysis: With α=0.05, N=10, d=0.5 → Power ≈ 0.85 (adequate)

**Confound Controls:**
- **Hyperparameters:** Shared PPO hyperparameters across all conditions (lr=3e-4, γ=0.99, λ=0.95)
- **Architecture:** Identical feature extractors, policy/value heads
- **Random Seeds:** Stratified across conditions to balance environment initialization variance
- **Compute Resources:** Equivalent GPU-hours per run (no speed-biased comparisons)

---

## 2. Contribution Summary

**Primary Contribution:**
First systematic investigation of **adaptive multi-signal intrinsic motivation integration** in open-ended RL, demonstrating that UCB bandit-based signal weighting enables environment-specific exploration strategy adaptation without manual signal design per domain.

**Secondary Contributions:**

1. **Tiered Adaptation Framework:** Establishes practical progression path (Fixed → UCB → Meta-learning) for IM signal composition, providing fallback strategies for different research/deployment contexts

2. **Signal Complementarity Analysis:** Quantifies when and why RND (novelty), ICM (dynamics), and LP (competence) signals provide complementary exploration benefits, informing future IM signal design

3. **Negative Results Value:** Even if hypothesis is falsified, results clarify whether multi-signal IM benefits exist, guiding future IMOL system design toward single-signal optimization vs. ensemble approaches

**Theoretical Impact:**
Extends Mirolli & Baldassarre (2013) IM taxonomy from classification framework to actionable integration strategy, bridging theoretical motivation types (knowledge vs. competence) with practical multi-signal engineering.

**Practical Impact:**
Tier 2 UCB approach requires minimal implementation overhead (~50 lines of code) compared to single-signal baselines, making it immediately deployable in existing IMOL codebases (e.g., RLlib, Stable-Baselines3).

**Differentiation from Prior Work:**
- **vs. CURIOUS (2018):** Fixed modular signals → Adaptive signal weighting
- **vs. Prioritized Sampling (2022):** Task-level adaptation → Signal-level adaptation
- **vs. RND/ICM/LP individually:** Single-signal → Principled multi-signal integration

---

## 3. Key Related Work

### Direct Precedents

1. **CURIOUS: Intrinsically Motivated Modular Multi-Goal RL (Colas et al., 2018)**
   - **Contribution:** Modular architecture with separate IM modules, absolute learning progress for curriculum
   - **Relation:** Provides architectural blueprint for modular IM signals; our work adds adaptive weighting
   - **Citation:** Semantic Scholar 3f56ac0e4b881d25268e83961b93ee95f2807bfb

2. **Prioritized Sampling with Intrinsic Motivation in Multi-Task RL (D'Eramo & Chalvatzaki, 2022)**
   - **Contribution:** TD-error (learning progress proxy) for adaptive task sampling
   - **Relation:** Demonstrates adaptive prioritization benefits; we apply to signal-level composition
   - **Citation:** Semantic Scholar 384d05141cf79d24bbf53df9334bb474928b4a93

3. **Random Network Distillation (Burda et al., 2019)**
   - **Contribution:** RND for novelty detection via prediction error on fixed random network
   - **Relation:** One of three IM signals in our ensemble; SOTA for Atari sparse-reward exploration
   - **Citation:** arXiv:1810.12894

### Foundational Theory

4. **Intrinsic Motivations and Open-Ended Development (Mirolli & Baldassarre, 2013)**
   - **Contribution:** Taxonomy of knowledge-based vs. competence-based IM signals
   - **Relation:** Theoretical foundation for signal complementarity hypothesis
   - **Citation:** Reference paper

5. **Intrinsic Curiosity Module (Pathak et al., 2017)**
   - **Contribution:** ICM using forward dynamics prediction error as intrinsic reward
   - **Relation:** One of three IM signals; demonstrates deep RL scalability
   - **Citation:** arXiv:1705.05363

### Methodological Parallels

6. **UCB Algorithm for Multi-Armed Bandits (Auer et al., 2002)**
   - **Contribution:** Upper confidence bound algorithm with sublinear regret guarantees
   - **Relation:** Adaptation mechanism for Tier 2; provides theoretical foundation for signal selection
   - **Citation:** Machine Learning Journal

7. **Unsupervised Skill Discovery via Skill Regions Differentiation (Xiao et al., 2025)**
   - **Contribution:** Balancing inter-skill diversity and intra-skill exploration
   - **Relation:** Addresses similar multi-objective balancing problem (diversity vs. exploitation)
   - **Citation:** Semantic Scholar 5c460d8e8e4e6304f2ee82ebae621c0c2f0aaa9e

### Contrasting Approaches

8. **DIAYN: Diversity is All You Need (Eysenbach et al., 2019)**
   - **Contribution:** Unsupervised skill discovery via mutual information maximization
   - **Relation:** Single-signal approach (empowerment-based); our work compares multi-signal vs. single-signal
   - **Citation:** arXiv:1802.06070

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence - Signal Complementarity):**
Do RND, ICM, and Learning Progress signals provide sufficiently independent exploration coverage such that their combination improves state-space exploration compared to any single signal?

**Experiment:** Fixed equal-weight ensemble vs. best single-signal baseline across 4 environments. Measure state coverage overlap (Jaccard index) between signals.

**Success Criterion:** Fixed ensemble achieves ≥10% higher state coverage than best single signal in ≥2 environments, AND signal overlap (Jaccard) < 0.7 (demonstrating independence).

---

**SH2 (Mechanism - Adaptation Benefit):**
Does UCB bandit-based adaptive weighting improve exploration efficiency beyond fixed ensemble weighting by dynamically allocating weight to environment-appropriate signals?

**Experiment:** UCB-Adaptive vs. Fixed-Ensemble in 4 environment types. Track signal weight trajectories and correlate with environment characteristics.

**Success Criterion:** UCB-Adaptive achieves ≥10% higher cumulative IM reward than Fixed-Ensemble (p < 0.05), AND weight distributions show environment-specific patterns (e.g., RND dominant in sparse-reward).

---

**SH3 (Comparison - SOTA Baseline):**
Does the adaptive ensemble approach achieve competitive performance with single-signal SOTA methods (RND for Atari sparse-reward) while providing superior generalization across diverse environments?

**Experiment:** UCB-Adaptive vs. RND-only (SOTA for sparse-reward exploration) across all 4 environments.

**Success Criterion:** UCB-Adaptive matches RND in sparse-reward environments (±5% task completion rate) AND outperforms RND in ≥2 other environment types by ≥15%.

---

### Readiness Checklist

**Hypothesis Clarity:**
- [✓] Core hypothesis stated in falsifiable form
- [✓] Variables (IV, DV, controls) clearly defined and measurable
- [✓] Causal mechanism articulated with evidence links
- [✓] Assumptions explicitly listed with risk assessment

**Experimental Design:**
- [✓] Test environments specified (MuJoCo, Atari sparse-reward, MiniGrid)
- [✓] Baseline conditions defined (6 IM conditions × 4 environments)
- [✓] Evaluation metrics operationalized (state coverage, task completion, IM reward)
- [✓] Statistical tests pre-specified (ANOVA, t-tests, effect sizes)

**Feasibility:**
- [✓] Tier 2 UCB uses only established components (RND, ICM, LP, UCB bandit)
- [✓] Computational budget realistic (240 runs = 2-3 GPU-weeks)
- [✓] Implementation complexity low (Tier 2 adds ~50 LOC to standard RL)
- [✓] Fallback strategy available (Tier 1 fixed ensemble if UCB fails)

**Phase 2B Readiness:**
- [✓] Sub-hypotheses (SH1-SH3) preview Phase 2B decomposition
- [✓] Each SH has clear experiment design and success criteria
- [✓] Hypothesis narrow enough for Phase 2B breakdown (focused on signal composition)

**Missing Elements:**
- [ ] Specific environment instances not yet chosen (e.g., which MuJoCo tasks, which Atari games)
- [ ] Exact UCB hyperparameters (exploration parameter c, update frequency) to be determined in Phase 2B

**Overall Status:** ✅ **READY FOR PHASE 2B**

---

### Open Questions for Phase 2B

1. **Environment Selection:** Which specific environments within each type (Sparse-Reward, Dense-Dynamics, Goal-Reaching, Procedural) best test signal complementarity?
   - Candidate Sparse-Reward: Montezuma's Revenge, Venture, PrivateEye
   - Candidate Dense-Dynamics: HalfCheetah, Ant (with reward shaping removed)
   - Candidate Goal-Reaching: FetchReach, FetchPush (with sparse rewards)
   - Candidate Procedural: MiniGrid-MultiRoom, MiniGrid-KeyCorridorS3R3

2. **UCB Hyperparameters:** What exploration-exploitation trade-off (c parameter in UCB formula) balances responsiveness vs. stability?
   - Suggest: c ∈ {0.1, 1.0, 2.0} ablation study
   - Update frequency: Every 10k steps (balancing feedback delay vs. adaptation speed)

3. **Signal Normalization:** How to ensure RND, ICM, LP rewards are on comparable scales for weighted summation?
   - Propose: Z-score normalization with running mean/std per signal (window size: 100 episodes)
   - Alternative: Rank-based normalization (less sensitive to outliers)

4. **Learning Progress Operationalization:** Absolute learning progress vs. relative progress? Window size for progress calculation?
   - Recommend: Absolute LP (prediction error delta over fixed window)
   - Window size: 100 episodes (following CURIOUS 2018)

5. **Baseline Strength:** Should single-signal baselines be tuned individually, or use shared hyperparameters for fair comparison?
   - Propose: Shared hyperparameters for unbiased comparison (favors strong single-signal performance, conservative test of ensemble benefit)

6. **Tier 3 Inclusion:** Is meta-learning Tier 3 necessary for hypothesis validation, or optional extension?
   - Recommendation: Optional - Tier 2 UCB sufficient for core hypothesis test
   - Include only if computational budget allows (adds 40 runs)

---

**Phase 2B Input Summary:**
- **Main Hypothesis:** Adaptive multi-signal IM ensemble (UCB-based) improves exploration efficiency and skill acquisition across diverse environments compared to single-signal and fixed-ensemble baselines
- **Key Sub-Hypotheses:** SH1 (Signal Complementarity), SH2 (Adaptation Benefit), SH3 (SOTA Comparison)
- **Critical Design Questions:** Environment selection, UCB hyperparameters, signal normalization, Learning Progress operationalization

---

*Generated using YouRA Phase 2A Extended Workflow*
*Hypothesis ID: H-2.1*
*FEASIBLE Confidence: 0.85*
*Ready for Phase 2B Verification Planning*
