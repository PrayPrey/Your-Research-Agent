# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-CTM-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under conditions of sustained human-AI interaction, if we project AI representation drift (measured via CKA similarity) and human behavioral adaptation patterns (multi-proxy feature vectors) into a shared embedding space using temporal contrastive learning, then we can quantify bidirectional coevolution by measuring trajectory alignment and coupling strength between these signals, because contrastive learning creates a unified metric space where heterogeneous signals become comparable through temporal pairing.

**Alternative Hypothesis (H0):**
There is no measurable relationship between AI representation drift and human behavioral adaptation patterns, and projecting these signals into a shared embedding space does not produce meaningful coevolution trajectory metrics that correlate with actual bidirectional adaptation.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| AI Representation Drift | Independent | CKA similarity between AI hidden states across interaction sessions | 0.0-1.0 (lower = more drift) |
| Human Behavioral Adaptation | Independent | Multi-proxy feature vector: query complexity (ASL 5-25 words), response latency (500-5000ms), correction frequency (0-50%), trust calibration actions (0-20 per session) | Normalized feature vector in R^4 |
| Coevolution Trajectory Metric (CTM) | Dependent | Trajectory alignment score (cosine similarity) + coupling coefficient (cross-correlation of adaptation rates) | CTM ∈ [0, 1], where 0 = no coevolution, 1 = perfect coupled adaptation |
| Interaction History Length | Controlled | Number of interaction sessions per user | Fixed at 10, 50, or 100 interactions |
| Task Domain | Controlled | Type of task performed | Creative writing, coding assistance, or Q&A |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: AI Hidden States → CKA Similarity Scores
        ↓
Step 2: CKA Scores + Behavioral Features → Shared Embedding Space (via Temporal Contrastive Learning)
        ↓
Step 3: Shared Embeddings → CTM Computation (Trajectory Alignment + Coupling Coefficient)
        ↓
      OUTCOME: Quantified Bidirectional Coevolution Metric
```

**Step 1 - AI Representation Tracking:**
AI hidden layer activations are extracted before and after user-specific interaction sessions. CKA (Centered Kernel Alignment) computes the similarity between these representation matrices, producing a continuous measure of how much the model's internal representations have adapted to the specific user.

**Step 2 - Contrastive Alignment:**
The CKA-based AI adaptation signal and the multi-proxy human behavioral feature vector are projected into a shared embedding space using temporal contrastive learning. Session timestamps provide natural positive pairs (same-session AI states paired with same-session behaviors), while different sessions serve as negative pairs. InfoNCE loss optimizes the alignment.

**Step 3 - CTM Computation:**
In the shared embedding space, two metrics are computed:
- **Trajectory Alignment Score**: Cosine similarity between the temporal trajectory of AI embeddings and human embeddings
- **Coupling Coefficient**: Cross-correlation between the rates of change in AI and human adaptation signals

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Kornblith et al. 2019 (CKA) | CKA reliably identifies correspondences between neural representations across different initializations | Strong |
| Step 1 → Step 2 | ICLR 2024 CKA paper | CKA achieves state-of-the-art performance in measuring neural network representation differences | Strong |
| Step 2 → Step 3 | CLIP (Radford et al. 2021) | Contrastive learning successfully aligns heterogeneous modalities (vision-language) | Strong |
| Step 2 → Step 3 | Pedreschi et al. 2024 (Human-AI Coevolution) | Human-AI feedback loops can be modeled as coupled dynamical systems | Medium |
| Step 3 → Outcome | Fer et al. 2025 (F-DTM) | Longitudinal trust evolution is measurable and predictable | Medium |

**Key Tension:**
- **Tension:** CKA literature (Kornblith et al.) focuses on comparing representations across models trained differently, while our application requires tracking within-model drift during fine-tuning/adaptation. Additionally, behavioral proxies may not perfectly capture cognitive changes (indirect measurement).
- **Resolution:** This verification plan tests whether CKA variance is sufficient to detect meaningful adaptation within a single model across sessions (Link 1 falsification test), and validates behavioral proxies against self-reported cognitive assessments (assumption validation in Phase 2B).

### 1.4 Key Assumptions

1. **Human behavioral changes are measurable through interaction logs**
   - Supporting evidence: HCI literature demonstrates query patterns, latency, and correction behaviors correlate with cognitive states
   - Consequence if violated: CTM human-side signal becomes noise; would need direct cognitive measurement (surveys, physiological sensors)

2. **AI representation drift captures meaningful user-specific adaptation**
   - Supporting evidence: RLHF literature shows model updates from preference learning alter hidden representations
   - Consequence if violated: CKA variance would be near-zero; would need model with explicit user adaptation mechanisms

3. **Contrastive learning can align behavioral and neural signals**
   - Supporting evidence: Multimodal contrastive learning (CLIP, ImageBind) successfully aligns fundamentally different modalities
   - Consequence if violated: Embedding space would show no temporal coherence; would need alternative alignment methods (e.g., CCA, mutual information)

4. **Longitudinal interaction data is available or can be generated**
   - Supporting evidence: LMSYS-Chat-1M, ShareGPT contain multi-turn conversations; synthetic generation feasible
   - Consequence if violated: Would limit validation to synthetic data only; external validity concerns

### 1.5 Scope & Boundaries

**Where hypothesis applies:**
- Interactive AI systems with observable user behavior (chatbots, coding assistants, creative tools)
- Systems that maintain session context and can be fine-tuned or adapted
- Domains where sustained interaction (10+ sessions) is common

**Where hypothesis does NOT apply:**
- One-shot AI interactions (no longitudinal signal)
- Systems without user behavioral logging
- Fully frozen models with no adaptation mechanism
- Domains where behavioral proxies are unreliable (e.g., high-stakes medical decisions)

**Known limitations:**
- Proxy validity requires ongoing validation against ground-truth cognitive assessments
- Causal attribution needs controlled experiments (randomized response manipulation)
- Results may not generalize across all task domains without domain-specific calibration

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (CTM Validity):** If CTM captures genuine coevolution, then higher CTM scores should positively correlate with improved task performance over time.

*Measurement:*
- CTM scores computed for user-AI pairs across 50+ interaction sessions
- Task performance measured via domain-specific metrics (helpfulness rating, task completion accuracy)
- Correlation analysis: Pearson r > 0.4 with p < 0.05

*Basis:*
If bidirectional adaptation is real and CTM measures it, users with stronger coevolution (higher CTM) should show better outcomes.

*Success Criteria for Phase 2B:*
- Primary: r(CTM, task_performance) > 0.4, p < 0.05
- Falsification: r < 0.2 or p > 0.10 triggers hypothesis revision

**Secondary Predictions:**

**P2 (Proxy Validity):** Human behavioral proxy signals should correlate with self-reported cognitive change assessments.
- Measurement: Correlation between behavioral features and post-session cognitive adaptation surveys
- Success: r > 0.3, p < 0.05

**P3 (Contrastive Alignment Quality):** The trained embedding space should show temporal coherence with clustering by interaction quality.
- Measurement: Silhouette score of temporal embeddings clustered by session quality
- Success: Silhouette score > 0.3

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure:** CTM scores show no correlation with task performance improvement (r < 0.2, p > 0.10)

2. **Mechanism Failure - Link 1:** CKA variance across sessions < 0.01 (AI representations too stable to track adaptation)

3. **Mechanism Failure - Link 2:** Embedding space silhouette score < 0.3 (contrastive alignment failed)

4. **Mechanism Failure - Link 3:** Coupling coefficient shows no relationship with observed mutual adaptation patterns

### 1.7 SOTA Baseline (Optional - Not SOTA Comparison Mode)

*Not applicable - This hypothesis targets absolute performance validation of a novel metric framework, not performance improvement over existing SOTA methods.*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): Medium (0.5) expected for correlation effects
- Required sample: n ≥ 30 user-AI pairs with 50+ sessions each
- Statistical power: 0.8

**Test Specification:**
- Primary analysis: Pearson correlation with bootstrapped confidence intervals
- Secondary: Mixed-effects regression controlling for user and task domain
- Significance level: α = 0.05 (two-tailed)
- Report format: Correlation coefficient, 95% CI, p-value, effect size

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does measurable bidirectional adaptation exist in sustained human-AI interaction, as captured by changes in both AI representations (CKA drift) and human behavioral patterns?"
- Maps to: Primary prediction P1
- Verification type: Empirical observation
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is temporal contrastive learning the effective mechanism for aligning heterogeneous adaptation signals (AI neural + human behavioral) into a unified measurement space?"
- Maps to: Causal mechanism (3 steps → will decompose into H-M1, H-M2, H-M3)
  - H-M1: CKA captures meaningful within-model adaptation
  - H-M2: Contrastive learning aligns heterogeneous signals
  - H-M3: Trajectory alignment + coupling coefficient form valid coevolution metric
- Verification type: Ablation studies
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does CTM provide information beyond existing unidirectional metrics (reward accuracy, user satisfaction) for predicting human-AI collaboration outcomes?"
- Maps to: Secondary predictions
- Verification type: Comparative empirical
- Critical: Determines practical value

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned (H-CTM-v1)
- [x] Confidence level specified (0.82)
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps, evidence table provided)
- [x] Causal chain length (N=3) determined and stored
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (P1 primary, P2, P3 secondary)
- [x] Falsification criteria are defined (4 conditions)
- [x] Baselines are identified for comparison
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Data Availability:** Can we obtain longitudinal interaction data with sufficient session depth (50+ per user)? LMSYS-Chat-1M may have limited per-user sessions. Alternative: synthetic data generation with ground-truth coevolution signals.

2. **Proxy Validation Study:** Should we conduct a preliminary study to validate behavioral proxies against cognitive assessments before full CTM validation? This adds scope but strengthens methodology.

3. **Computational Resources:** CKA computation on large model hidden states and contrastive training require moderate GPU resources. Verify single A100 is sufficient for proposed experiments.

4. **Priority Order:** Recommend starting with SH1 (existence) → SH2-M1 (CKA validation) → SH2-M2 (contrastive alignment) → SH2-M3 (CTM computation) → SH3 (comparison)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
