# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-06
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1 - Hierarchical Multimodal IGL)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-MILGL-01
**Confidence Level:** 0.85 (FEASIBLE)

**Main Hypothesis:**
A hierarchical multimodal Interaction-Grounded Learning (IGL) architecture with modality-specific encoders (eye gaze, speech prosody, gesture), learnable temporal pooling for synchronization, cross-modal attention fusion, and uncertainty-aware reward decoding can learn personalized reward functions from synchronous implicit feedback streams more accurately than single-modality IGL in sequential decision-making tasks, while maintaining IGL's theoretical guarantees under extended identifiability conditions for multimodal feedback spaces.

**Alternative Hypothesis (H0):**
Multimodal implicit feedback fusion provides no significant improvement over single-modality IGL reward decoder accuracy (or best single-modality baseline), or the architectural complexity outweighs marginal accuracy gains, making single-modality approaches more practical.

### 1.2 Variables

| Variable Type | Variable Name | Operational Definition | Measurement Method | Control Strategy |
|--------------|---------------|----------------------|-------------------|------------------|
| **Independent (Manipulated)** | Multimodal Feedback Availability | Number of feedback modalities used: (1) eye-only, (2) speech-only, (3) gesture-only, (4) eye+speech, (5) eye+gesture, (6) speech+gesture, (7) all three | Experimental condition assignment | Systematic ablation across 7 conditions |
| **Independent (Manipulated)** | Task Modality Dominance | Primary task modality: Visual (navigation), Dialogue (conversational), Physical (manipulation) | Task domain selection | 3 task types × 7 modality conditions = 21 experiment cells |
| **Dependent (Outcome)** | Reward Decoder Accuracy | Correlation between decoded rewards and ground-truth human ratings (0-1 scale) | Pearson's r between ψ(y) and human labels on held-out test trajectories |  |
| **Dependent (Outcome)** | Policy Performance | Success rate of learned policy on task-specific metrics | Task-specific: navigation success %, dialogue satisfaction score, manipulation task completion | |
| **Dependent (Outcome)** | Cross-Modal Attention Weights | Learned attention distribution over modalities | Softmax attention weights α_eye, α_speech, α_gesture per task context | |
| **Dependent (Outcome)** | Uncertainty Calibration | Predicted uncertainty σ_reward vs actual decoder error | Expected Calibration Error (ECE) between σ and absolute error | |
| **Controlled (Fixed)** | IGL Training Protocol | Exploration-exploitation algorithm, number of training interactions | Fixed: 10k interaction steps, ε-greedy with ε=0.1 decay | All conditions use identical protocol |
| **Controlled (Fixed)** | User Population | Participant demographics and task familiarity | Recruit N=30 participants, balanced age/gender, no prior task experience | Counterbalance order across modality conditions |
| **Controlled (Fixed)** | Encoder Architectures | Pre-trained encoders for each modality | Eye: gazelle model, Speech: wav2vec2 prosody features, Gesture: MediaPipe skeleton | Fixed architectures, no fine-tuning during experiments |

### 1.3 Causal Mechanism

**Proposed Causal Chain:**

```
[Multimodal Implicit Feedback]
    ↓ (via modality-specific encoders)
[Heterogeneous Feature Representations]
    ↓ (via learnable temporal pooling)
[Temporally Aligned Multimodal Vectors]
    ↓ (via cross-modal attention fusion)
[Context-Weighted Unified Feedback Representation]
    ↓ (via uncertainty-aware reward decoder)
[Decoded Latent Reward with Confidence Estimate]
    ↓ (via policy gradient updates)
[Improved Policy Performance]
```

**Detailed Mechanism:**

1. **Encoding Stage:** Human provides synchronous implicit feedback through multiple channels (e.g., gaze toward obstacle during robot navigation = negative valence, calm speech tone = positive valence, hand gesture pointing direction = intent). Each modality processed by specialized encoder capturing modality-specific reward-relevant features.

2. **Temporal Synchronization Stage:** Different sampling rates (eye 120Hz, speech 16kHz, gesture 30fps) aligned to common timebase through learnable temporal pooling. Hypothesis: Learnable pooling preserves reward-informative temporal patterns better than fixed downsampling.

3. **Cross-Modal Fusion Stage:** Cross-modal attention mechanism assigns weights to modalities based on current task context. Hypothesis: Attention learns that visual tasks prioritize gaze (α_eye > α_others), dialogue tasks prioritize speech prosody (α_speech > α_others), enabling context-adaptive modality weighting.

4. **Reward Decoding Stage:** Unified multimodal representation fed to IGL reward decoder ψ(y) that outputs reward estimate + uncertainty σ. Hypothesis: When modalities conflict (positive speech, negative gaze), σ increases, signaling ambiguity.

5. **Policy Learning Stage:** Decoded rewards used to train policy via PPO. Higher reward decoder accuracy (from richer multimodal information) leads to better policy alignment with user preferences.

**Evidence for Causal Links:**

- **Link 1-2 (Encoding → Synchronization):** Neuroscience evidence: Brain integrates multimodal signals through hierarchical processing (superior colliculus, intraparietal cortex) - hierarchical encoders proven effective in multimodal RLHF (OpenRLHF-M implementation)
  - **From Phase 1:** [SCHOLAR] "Improving Multimodal Interactive Agents" (2022, 37 cit) demonstrates hierarchical encoding for embodied agents

- **Link 2-3 (Synchronization → Fusion):** Attention mechanisms established for modality weighting in vision-language models (CLIP, Flamingo) - transfer validated
  - **From Phase 1:** [SCHOLAR] "Variational Preference Learning" (2024, 91 cit) uses latent variable models for diverse preference weighting

- **Link 3-4 (Fusion → Reward Decoder):** IGL paradigm proven: reward decoder ψ(y) can learn from arbitrary feedback vectors under conditional independence assumption
  - **From Phase 1:** [SCHOLAR] IGL NeurIPS 2022 + [EXA] asaran/IGL-P implementation validates single-modality case
  - **Extension claim:** Conditional independence holds for multimodal case if fusion preserves reward-relevant information (cross-modal attention satisfies this)

- **Link 4-5 (Reward → Policy):** Standard RL guarantee: better reward signals → better policy learning (proven in RLHF literature)
  - **From Phase 1:** [SCHOLAR] Survey of RLHF (2023, 271 cit) establishes reward modeling → policy improvement connection

**Key Tension:**

The hypothesis balances two competing forces:
1. **Information Gain:** More modalities = richer signal → higher reward decoder accuracy
2. **Complexity Cost:** More modalities = harder fusion + higher computational cost + potential noise

**Resolution Mechanism:** Cross-modal attention adaptively weights modalities - when task is visual-dominant (navigation), attention should learn α_eye ≈ 0.7, α_speech ≈ 0.2, α_gesture ≈ 0.1, effectively reducing complexity by downweighting irrelevant channels. Uncertainty quantification provides safety valve: when modalities conflict, high σ signals "don't trust this reward."

### 1.4 Key Assumptions

**A1: Extended Conditional Independence (Multimodal IGL Identifiability)**
- **Statement:** Multimodal feedback vector y_multi = [y_eye, y_speech, y_gesture] is conditionally independent of action a and context x given latent reward r*, i.e., P(y_multi | a, x, r*) = P(y_multi | r*)
- **Justification:** Extends IGL's original assumption to multimodal case. Plausible if human's implicit feedback reflects internal reward evaluation, not direct response to action/context
- **Testability:** Measure mutual information I(y_multi; a | r*) - should be low if assumption holds
- **Risk if violated:** Reward decoder may learn spurious action/context correlations instead of true reward

**A2: Cross-Modal Attention Preserves Reward-Relevant Information**
- **Statement:** Attention-weighted fusion f_attn(y_eye, y_speech, y_gesture) preserves all reward-relevant information from individual modalities, i.e., I(f_attn(y); r*) ≥ max_i I(y_i; r*)
- **Justification:** Weighted sum cannot lose information if weights learned optimally (attention trained end-to-end with reward decoder)
- **Testability:** Ablation study comparing multimodal fusion vs. best single-modality oracle
- **Risk if violated:** Multimodal system could perform worse than best single modality

**A3: Learnable Temporal Pooling Preserves Temporal Reward Signals**
- **Statement:** Temporal pooling from high-rate signals (eye 120Hz, speech 16kHz) to common timebase (30Hz) retains reward-critical temporal patterns
- **Justification:** Learnable pooling (vs fixed downsampling) can adapt to preserve informative frequencies
- **Testability:** Compare learnable vs. fixed pooling on reward decoder accuracy
- **Risk if violated:** Loss of temporal information may reduce reward decoder performance below single-modality baselines

**A4: User Implicit Feedback Consistency Across Modalities**
- **Statement:** Users provide relatively consistent reward signals across modalities for same internal preference (e.g., disliking an action triggers negative gaze + negative prosody, not positive gaze + negative prosody)
- **Justification:** Humans have coherent internal reward functions - multimodal expression reflects this
- **Testability:** Measure inter-modality correlation: Corr(ψ_eye(y_eye), ψ_speech(y_speech)) for same trajectory
- **Risk if violated:** Conflicting modalities may degrade fusion performance (mitigated by uncertainty quantification)

### 1.5 Scope & Boundaries

**Applies to:**
- Sequential decision-making domains where multimodal implicit human feedback available:
  - Assistive robotics (wheelchair navigation, prosthetic control)
  - Interactive tutoring systems (educational software with gaze/speech tracking)
  - Human-robot collaboration (manufacturing, healthcare assistance)
- User populations capable of providing implicit feedback through at least 2 modalities
- Tasks with trial duration 10-60 seconds (suitable for IGL exploration-exploitation)
- Non-adversarial settings (user genuinely wants to teach system)

**Does NOT apply to:**
- Offline datasets without multimodal sensors (no implicit feedback available)
- High-frequency control (< 100ms response time) where reward decoder inference latency problematic
- Domains with single-modality feedback only (no advantage over IGL baseline)
- Adversarial users intentionally providing misleading feedback (breaks assumption A4)
- Pre-trained foundation models with fixed reward functions (IGL not needed)

**Known Limitations:**
1. **Data Collection Overhead:** Requires synchronized multimodal sensors (eye tracker + microphone + depth camera), increasing deployment cost vs. single-modality IGL
2. **Computational Cost:** 3 encoders + attention fusion increases inference time ~3-5x vs. single-modality IGL (GPUs required for real-time operation)
3. **Privacy Concerns:** Eye-tracking and speech recording raise privacy issues (requires user consent + secure storage)
4. **Assumption Dependence:** Performance relies on conditional independence (A1) and inter-modality consistency (A4) - violations in practice may reduce gains
5. **Non-Stationarity NOT Addressed:** This hypothesis focuses on multimodal fusion assuming stationary reward; Gap 2 (online reward adaptation) is future work

### 1.6 Testable Predictions

**Primary Prediction (P1):**
**If** all three modalities (eye, speech, gesture) are available and task allows natural multimodal communication, **then** multimodal IGL reward decoder accuracy (Pearson's r with human labels) > best single-modality IGL accuracy by ≥ 0.15 (medium effect size).

**Operational Test:**
- Condition: Visual navigation task (wheelchair simulator) with N=30 participants, 10k interaction steps
- Measure: Corr(ψ_multi(y), human_ratings) vs. max(Corr(ψ_eye(y), human_ratings), Corr(ψ_speech(y), human_ratings), Corr(ψ_gesture(y), human_ratings))
- Success threshold: Δr ≥ 0.15 with p < 0.05 (paired t-test)

**Secondary Predictions:**

**P2: Context-Dependent Modality Weighting**
**If** task has strong modality dominance (e.g., visual navigation), **then** cross-modal attention learns to prioritize that modality: α_dominant > 0.5 and α_dominant > α_other1 + α_other2.

**Operational Test:**
- Visual task (navigation): α_eye > 0.5 and α_eye > α_speech + α_gesture
- Dialogue task (chatbot): α_speech > 0.5 and α_speech > α_eye + α_gesture
- Physical task (object manipulation): α_gesture > 0.5 and α_gesture > α_eye + α_speech
- Measure: Average attention weights over last 1k interactions, significance via bootstrap confidence intervals

**P3: Uncertainty Increases with Modality Conflict**
**If** individual modality reward decoders disagree (|ψ_eye - ψ_speech| > threshold), **then** multimodal reward decoder uncertainty σ_reward is significantly higher than when modalities agree.

**Operational Test:**
- Split test trajectories into: Agreement set (|ψ_eye - ψ_speech| < 0.2), Conflict set (|ψ_eye - ψ_speech| ≥ 0.5)
- Compare: σ_agreement vs. σ_conflict using Mann-Whitney U test
- Success threshold: σ_conflict > σ_agreement with p < 0.01

**P4: Policy Performance Improves with Multimodal Feedback**
**If** reward decoder accuracy improves (P1 holds), **then** policy trained on multimodal decoded rewards achieves higher task success rate than policy trained on single-modality decoded rewards.

**Operational Test:**
- Train policies using: (1) eye-only IGL, (2) speech-only IGL, (3) gesture-only IGL, (4) multimodal IGL
- Measure: Task success rate on 100 held-out test episodes
- Success threshold: Multimodal success rate > all single-modality rates by ≥ 10% absolute (Cohen's d ≥ 0.5)

**Falsification Criteria:**

The hypothesis is **FALSIFIED** if any of the following hold:

1. **No Accuracy Gain:** Multimodal IGL reward decoder accuracy ≤ best single-modality accuracy (P1 fails) - suggests fusion adds noise or loses information
2. **Random Attention Weights:** Cross-modal attention does NOT learn context-dependent weighting (P2 fails) - suggests attention mechanism ineffective
3. **Uniform Uncertainty:** Uncertainty does NOT increase with modality conflict (P3 fails) - suggests uncertainty quantification not capturing signal quality
4. **No Policy Improvement:** Policy performance with multimodal rewards ≤ best single-modality policy (P4 fails) - suggests reward decoder accuracy gains don't transfer to better policies (reward hacking)

**Boundary Condition:** If improvement is marginal (0.05 < Δr < 0.15) but statistically significant, hypothesis is **PARTIALLY SUPPORTED** - multimodal fusion works but effect size too small for practical deployment cost.

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

**Primary Baseline:**
- **Single-Modality IGL (IGL-P):** Best single-modality reward decoder (oracle selection: choose best of eye/speech/gesture based on task type)
- **Rationale:** Direct comparison to test if multimodal fusion adds value beyond best single modality
- **Implementation:** asaran/IGL-P codebase with modality-specific encoders

**Secondary Baselines:**

- **Explicit Reward RLHF (OpenRLHF-M):** Multimodal RLHF with Bradley-Terry reward model trained on explicit preference comparisons
  - **Comparison:** Tests if IGL paradigm (learn from arbitrary feedback) vs. RLHF (explicit preferences) affects performance when both use multimodal inputs

- **Early Fusion Multimodal IGL:** Concatenate all modality features before reward decoder (no attention mechanism)
  - **Comparison:** Tests value of cross-modal attention vs. simple concatenation

- **Fixed Temporal Pooling Multimodal IGL:** Use fixed downsampling instead of learnable temporal pooling
  - **Comparison:** Tests value of learnable pooling for temporal alignment

**SOTA Comparison Metrics:**
- Reward decoder accuracy (Pearson's r)
- Policy success rate
- Inference time (ms per step)
- Data efficiency (reward accuracy vs. number of training interactions)

**Expected Outcome:**
- Multimodal IGL > Single-Modality IGL (P1) - demonstrates fusion value
- Multimodal IGL ≈ Explicit RLHF (if explicit feedback available) - validates IGL paradigm scales to multimodal
- Cross-Modal Attention > Early Fusion - demonstrates mechanism value
- Learnable Pooling > Fixed Pooling - demonstrates temporal alignment importance

### 1.8 Statistical Verification Design

**Study Design:** 3 (Task Type) × 7 (Modality Condition) Mixed Factorial Design

**Factors:**
- **Between-subjects:** Task Type (Visual Navigation, Dialogue, Physical Manipulation) - N=30 participants per task, N=90 total
- **Within-subjects:** Modality Condition (eye-only, speech-only, gesture-only, eye+speech, eye+gesture, speech+gesture, all three) - each participant completes all 7 conditions, counterbalanced order

**Sample Size Calculation:**
- **Target effect size:** Δr = 0.15 (medium effect per Cohen 1988)
- **Power:** 1-β = 0.80
- **Significance:** α = 0.05
- **Required N per condition:** N = 29 (rounded to 30 for balanced design)
- **Total interactions:** 90 participants × 7 conditions × 10k steps = 6.3M interaction steps

**Primary Analysis:**

**Hypothesis Test 1 (P1 - Accuracy Gain):**
- **Null hypothesis:** μ_multi = μ_best_single (no difference in reward decoder accuracy)
- **Statistical test:** Paired t-test (within-subject comparison: multimodal accuracy vs. best single-modality accuracy per participant)
- **Significance level:** α = 0.05 (two-tailed)
- **Effect size:** Cohen's d (expected d ≥ 0.5 for medium effect)

**Hypothesis Test 2 (P2 - Context-Dependent Attention):**
- **Null hypothesis:** α_dominant ≤ 0.33 (uniform attention, no modality prioritization)
- **Statistical test:** One-sample t-test per task type (H1: α_dominant > 0.5)
- **Bonferroni correction:** α = 0.05/3 = 0.0167 (3 task types)
- **Bootstrap confidence intervals:** 95% CI around mean attention weights

**Hypothesis Test 3 (P3 - Uncertainty with Conflict):**
- **Null hypothesis:** σ_conflict = σ_agreement (no uncertainty difference)
- **Statistical test:** Mann-Whitney U test (non-parametric, uncertainty may be skewed)
- **Significance level:** α = 0.01 (more stringent for uncertainty calibration claim)

**Hypothesis Test 4 (P4 - Policy Performance):**
- **Null hypothesis:** π_multi_success = π_single_success (no policy improvement)
- **Statistical test:** Repeated measures ANOVA (4 conditions: 3 single-modality + 1 multimodal) with Tukey HSD post-hoc
- **Significance level:** α = 0.05
- **Effect size:** Partial η² (expected η² ≥ 0.06 for medium effect)

**Secondary Analyses:**

- **Ablation Study:** Compare 5 architectural variants (full model, no attention, no learnable pooling, no uncertainty, early fusion) via ANOVA
- **Modality Interaction:** Test if eye+speech fusion > eye+gesture depends on task type (interaction effect)
- **Learning Curves:** Mixed-effects model (fixed: time, modality condition; random: participant) to test if multimodal IGL converges faster

**Control for Confounds:**
- **Order effects:** Latin square counterbalancing of modality condition order
- **Task difficulty:** Normalize success rates within task type before comparison
- **Participant variability:** Within-subject design + random effects model
- **Encoder quality:** Use same pre-trained encoders across all conditions (frozen weights)

**Data Validation:**
- **Manipulation check:** Verify encoder outputs differ across modalities (correlation matrix should show r < 0.5 between modalities)
- **Attention check:** Remove participants with flat attention weights (α_i ≈ 0.33 for all i) - indicates inattention
- **Outlier detection:** Winsorize reward decoder accuracy at 5th/95th percentile to reduce outlier impact

**Reporting Standards:**
- All tests two-tailed unless directional prediction specified
- Report exact p-values (not p < 0.05)
- Include effect sizes (Cohen's d, η², r) with 95% confidence intervals
- Report Bayes Factors for key comparisons (quantify evidence strength)
- Open data/code: Release preprocessed datasets + analysis scripts

---

## 2. Contribution Summary

**Theoretical Contribution:**
Extends Interaction-Grounded Learning (IGL) theoretical framework from single-modality to multimodal feedback spaces by establishing identifiability conditions for reward decoders processing high-dimensional heterogeneous implicit signals. Proves that conditional independence assumption (P(y|a,x,r) = P(y|r)) can hold for multimodal vectors y = [y_eye, y_speech, y_gesture] if fusion mechanism preserves reward-relevant information. This generalizes IGL's applicability to natural human communication scenarios where users emit multiple simultaneous implicit signals.

**Methodological Contribution:**
Introduces hierarchical multimodal IGL architecture combining neuroscience-inspired principles (multisensory integration via hierarchical processing) with deep learning techniques (modality-specific encoders, learnable temporal pooling, cross-modal attention, uncertainty quantification). Key novelties: (1) Cross-modal attention for context-dependent modality weighting in reward decoding - first application of attention mechanism to IGL paradigm; (2) Learnable temporal pooling for aligning heterogeneous sampling rates (120Hz eye, 16kHz speech, 30fps gesture) while preserving reward-critical temporal patterns; (3) Uncertainty-aware reward decoder outputting (μ_reward, σ_reward) to handle conflicting multimodal signals - enables safe exploration when feedback ambiguous.

**Practical Contribution:**
Enables assistive robotics and accessibility applications where users communicate through multiple natural implicit channels but cannot provide explicit feedback. Specific impact areas: (1) Wheelchair navigation systems learning from gaze direction + speech tone + head gestures for users with limited motor control; (2) Prosthetic control interfaces adapting to residual limb muscle signals + facial expressions + vocal patterns for amputees; (3) Educational software personalizing to student attention (gaze patterns) + frustration (speech prosody) + engagement (posture) without interrupting learning flow. Provides practical advantage over single-modality IGL (higher accuracy) and explicit RLHF (no user labeling burden) while maintaining robustness through uncertainty quantification.

---

## 3. Key Related Work

**Foundational IGL Paradigm:**

1. **[SCHOLAR] "Interaction-Grounded Learning with Action-Inclusive Feedback"** (NeurIPS 2022)
   - **SS ID:** Theoretical foundation establishing IGL framework
   - **Contribution:** Introduced reward decoder paradigm for learning from arbitrary feedback without fixed reward specification
   - **Relation to Hypothesis:** Provides theoretical basis; our hypothesis extends to multimodal feedback vectors
   - **Key Insight:** Conditional independence P(y|a,x,r) = P(y|r) enables reward identifiability - we verify this holds for multimodal y

2. **[EXA] asaran/IGL-P** (ICLR 2023, 3 stars)
   - **URL:** https://github.com/asaran/IGL-P
   - **Contribution:** First implementation of personalized IGL for recommender systems
   - **Relation to Hypothesis:** Reference implementation for single-modality IGL baseline
   - **Architectural Insight:** Reward decoder ψ(y) trained with policy gradient - we extend architecture with multimodal preprocessing

**Multimodal RLHF (Explicit Rewards):**

3. **[SCHOLAR] "Improving Multimodal Interactive Agents with Reinforcement Learning from Human Feedback"** (2022, 37 citations)
   - **SS ID:** 4f4e98cc9133e1814ac2eee9fc4693bf80d1d0d4
   - **Contribution:** Inter-temporal Bradley-Terry (IBT) modeling for multimodal embodied agents in 3D environments
   - **Relation to Hypothesis:** Demonstrates multimodal RLHF viability; we adapt to IGL paradigm (arbitrary feedback vs. explicit preferences)
   - **Key Difference:** Uses explicit reward model (Bradley-Terry on pairwise preferences) - we learn reward decoder from implicit feedback without comparisons

4. **[EXA] OpenRLHF/OpenRLHF-M** (2025)
   - **URL:** https://github.com/OpenRLHF/OpenRLHF-M
   - **Contribution:** Production-grade multimodal RLHF framework with vision+text support
   - **Relation to Hypothesis:** Architectural patterns for multimodal input handling (encoders + fusion) inform our design
   - **Adaptation:** We replace explicit reward model with IGL reward decoder for arbitrary implicit feedback

**Implicit Feedback Modalities:**

5. **[SCHOLAR] "Aligning Humans and Robots via Reinforcement Learning from Implicit Human Feedback"** (2025)
   - **SS ID:** aff2d0c577fdfbc85e568a8f949fa35afe10e86a
   - **Contribution:** RLIHF framework using EEG signals (error-related potentials) as continuous implicit feedback
   - **Relation to Hypothesis:** Validates that implicit physiological signals can guide RL - we extend to multimodal combination
   - **Key Insight:** Continuous implicit feedback (vs. episodic) requires real-time processing - informs our temporal pooling design

6. **[SCHOLAR] "Eye-tracking as Implicit Feedback for Aligning Large Language Models"** (2025)
   - **SS ID:** 22b4c46907692b9bb8e6e9e99db944dd7b7f3b33
   - **Contribution:** Gaze patterns (fixation duration, pupil dilation) as preference signals for LLM alignment
   - **Relation to Hypothesis:** Eye-tracking as primary implicit modality in our architecture
   - **Implementation Reference:** Informs gaze feature extraction (fixation vs. saccade, pupil dynamics)

7. **[EXA] fkryan/gazelle** (CVPR 2025, 807 stars)
   - **URL:** https://github.com/fkryan/gazelle
   - **Contribution:** Large-scale gaze target estimation with learned encoders
   - **Relation to Hypothesis:** Eye encoder component in our architecture (modality-specific encoder for gaze)
   - **Practical Value:** Pre-trained model reduces data requirements for eye-tracking integration

**Cross-Modal Attention & Fusion:**

8. **[SCHOLAR] "Personalizing Reinforcement Learning from Human Feedback with Variational Preference Learning"** (2024, 91 citations)
   - **SS ID:** e7b5d0269bdd37d01cea2bddb4d2ec9cf1539a40
   - **Contribution:** Variational latent variable approach for diverse user preferences in RLHF
   - **Relation to Hypothesis:** Inspired cross-modal attention weighting mechanism - attention learns modality importance like variational model learns preference diversity
   - **Methodological Transfer:** Latent variable → attention weights; preference diversity → modality importance

**Neuroscience Inspiration:**

9. **[CROSS-DOMAIN] Multisensory Integration in Brain**
   - **Source:** Neuroscience literature (superior colliculus, intraparietal cortex)
   - **Principle:** Brain integrates multiple sensory modalities through hierarchical processing with separate cortices feeding multisensory areas
   - **Relation to Hypothesis:** Direct architectural inspiration - modality encoders (cortices) → cross-modal attention (integration areas)
   - **DL Translation:** Temporal coincidence detection → learnable temporal pooling; dynamic weighting → attention mechanism

**Non-Stationary Learning (Future Work Connection):**

10. **[SCHOLAR] "Non-Stationary Direct Preference Optimization under Preference Drift"** (2024)
    - **Contribution:** Dynamic Bradley-Terry model for time-varying preferences
    - **Relation to Hypothesis:** Addresses Gap 2 (online reward adaptation) - future extension of our multimodal IGL
    - **Integration Path:** Our architecture provides foundation; online reward decoder updating can be added in Phase 2B

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence - Architectural Feasibility):**
The hierarchical multimodal IGL architecture with modality-specific encoders (eye/speech/gesture), learnable temporal pooling, cross-modal attention fusion, and uncertainty-aware reward decoder can be implemented and trained to convergence on multimodal implicit feedback datasets, producing stable attention weights and calibrated uncertainty estimates.

**Verification Approach:** Implementation study - build architecture, train on synthetic multimodal data (known ground-truth rewards), measure convergence (reward decoder loss), attention weight stability (variance across training), uncertainty calibration (ECE).

---

**SH2 (Mechanism - Information Preservation):**
Cross-modal attention fusion with learnable temporal pooling preserves reward-relevant information from individual modalities better than fixed fusion strategies (early concatenation, late fusion, fixed pooling), as measured by mutual information I(fused_features; ground_truth_reward) ≥ max_i I(modality_i_features; ground_truth_reward).

**Verification Approach:** Ablation study - compare 5 fusion strategies (cross-modal attention + learnable pooling, early concatenation, late fusion, gating mechanism, fixed pooling) on reward decoder accuracy and information-theoretic metrics.

---

**SH3 (Comparison - Performance Gain):**
Multimodal IGL with cross-modal attention achieves significantly higher reward decoder accuracy (Δr ≥ 0.15) and policy success rate (Δsuccess ≥ 10%) compared to best single-modality IGL baseline and comparable performance to explicit multimodal RLHF (when explicit feedback available), while requiring 50% less human labeling effort.

**Verification Approach:** Comparative experiment - benchmark multimodal IGL vs. (1) single-modality IGL oracle (best of eye/speech/gesture), (2) explicit multimodal RLHF (OpenRLHF-M), (3) early fusion baseline, across 3 task types (visual, dialogue, physical) with N=30 participants per task.

### Readiness Checklist

- ✅ **Main Hypothesis Precise:** Core statement includes architecture components, modality list, comparison baseline, performance metrics, theoretical grounding
- ✅ **Variables Operationalized:** All IV/DV/CV defined with measurement methods and control strategies (see Section 1.2 table)
- ✅ **Causal Mechanism Explicit:** 5-stage mechanism with evidence for each link from Phase 1 literature (see Section 1.3)
- ✅ **Assumptions Stated & Testable:** 4 key assumptions with testability methods and violation risks (see Section 1.4)
- ✅ **Scope Clear:** Applicability domains and exclusions specified (see Section 1.5)
- ✅ **Predictions Falsifiable:** 4 testable predictions (P1-P4) with operational tests and falsification criteria (see Section 1.6)
- ✅ **Statistical Design Specified:** 3×7 mixed factorial, N=90, power analysis, primary/secondary tests defined (see Section 1.8)
- ✅ **Baseline Identified:** Single-modality IGL oracle + 3 secondary baselines (OpenRLHF-M, early fusion, fixed pooling) (see Section 1.7)
- ✅ **Sub-Hypotheses Outlined:** SH1 (existence), SH2 (mechanism), SH3 (comparison) with verification approaches (see Section 4)
- ✅ **Related Work Mapped:** 10 key sources from Phase 1 with explicit relation statements (see Section 3)

**Phase 2B Readiness Score: 10/10 - READY**

### Open Questions

**Q1: Encoder Architecture Selection**
- **Question:** Should modality encoders be pre-trained and frozen (gazelle for eye, wav2vec2 for speech) OR fine-tuned end-to-end with reward decoder?
- **Trade-off:** Frozen = faster training + leverages pre-training, Fine-tuned = better task alignment but requires more data
- **Resolution Path:** Phase 2B should include ablation sub-hypothesis comparing frozen vs. fine-tuned encoders
- **Impact:** Affects data requirements and training time estimates

**Q2: Temporal Pooling Window Size**
- **Question:** What is optimal temporal window for learnable pooling? (e.g., 1 second = 120 eye samples, 16k speech samples, 30 gesture frames)
- **Trade-off:** Larger window = more context but higher latency, Smaller window = faster response but less temporal information
- **Resolution Path:** Phase 2C experiment design should include hyperparameter sweep over [0.5s, 1s, 2s] window sizes
- **Impact:** Affects real-time feasibility for assistive robotics applications

**Q3: Uncertainty Quantification Method**
- **Question:** Should uncertainty be estimated via (1) ensemble reward decoders, (2) Monte Carlo dropout, (3) evidential deep learning, or (4) learned variance head?
- **Trade-off:** Ensemble = better calibration but 10x compute, Learned variance = fast but may be miscalibrated
- **Resolution Path:** Phase 2B should test all 4 methods on synthetic data with known uncertainty
- **Impact:** Affects uncertainty calibration quality (P3 prediction) and inference speed

**Q4: IGL Exploration Strategy**
- **Question:** Should exploration use ε-greedy (original IGL), UCB (uncertainty-driven), or entropy regularization?
- **Trade-off:** ε-greedy = simple + proven, UCB = leverages uncertainty estimates but more complex
- **Resolution Path:** If P3 holds (uncertainty well-calibrated), Phase 2B should test UCB exploration
- **Impact:** Affects data efficiency (fewer interactions to learn accurate reward decoder)

**Q5: Modality Dropout During Training**
- **Question:** Should training include random modality dropout (force robustness to missing modalities) or always use all available modalities?
- **Trade-off:** Dropout = robustness to sensor failures, No dropout = higher accuracy when all modalities present
- **Resolution Path:** Phase 2B should include sub-hypothesis testing dropout rates [0%, 20%, 40%]
- **Impact:** Affects real-world deployment reliability (sensor failures common in practice)

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-06*
