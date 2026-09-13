# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-CAVD-v1
**Confidence Level:** 0.78

**Main Hypothesis:**
Under the condition of standard pairwise preference data with implicit annotator disagreement, if we apply variational inference to discover K latent value clusters and aggregate rewards via transparent social choice voting (Borda/Condorcet with Gumbel-Softmax relaxation), then we can preserve pluralistic value representation while enabling governance-auditable AI decisions, because disagreement patterns in preference data encode latent value structure that can be decomposed into interpretable clusters reflecting distinct moral frameworks.

**Alternative Hypothesis (H0):**
Preference disagreements in annotation data are primarily noise or idiosyncratic individual variation rather than reflections of coherent value systems; therefore, attempting to discover latent value clusters will produce arbitrary groupings with no meaningful correspondence to moral frameworks, and voting-based aggregation will not improve transparency or governance auditability compared to standard weighted averaging.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| K (number of value clusters) | Independent | Hyperparameter K∈{3,5,7,10} selected via BIC or silhouette score on validation set | K=5 expected optimal based on Moral Foundations Theory (5 foundations) |
| Voting rule | Independent | Choice of Borda count or Condorcet method for reward aggregation | Borda (smoother gradients) vs Condorcet (stronger theoretical guarantees) |
| Per-cluster preference accuracy | Dependent | Accuracy of predicting held-out preferences within each discovered cluster, measured on PERSONA benchmark | >90% of MODPO with explicit labels |
| Governance Transparency Score | Dependent | Human evaluator agreement on identifying which clusters influenced model decisions (inter-rater reliability κ) | κ > 0.6 (substantial agreement) |
| MFQ correlation | Dependent | Pearson correlation between cluster assignments and Moral Foundations Questionnaire dimensions | r > 0.3 (medium effect size) |
| Value Inequity Index | Dependent | Variance in per-cluster accuracy across discovered value groups | Lower is better; target < 0.05 |
| Base LLM architecture | Controlled | Fixed to Llama-3-8B or equivalent across all experiments | Constant |
| Training data | Controlled | PERSONA benchmark: 1,586 personas, 317,200 preference pairs | Constant |

### 1.3 Causal Mechanism

```
Step 1: Pairwise Preferences → VAE Encoder → Soft Cluster Assignments
    ↓
Step 2: Soft Cluster Assignments → K Specialized Reward Heads → Per-Cluster Rewards
    ↓
Step 3: Per-Cluster Rewards → Gumbel-Softmax Voting → Differentiable Aggregated Reward
    ↓
Step 4: Aggregated Reward + Audit Trail → Policy Training → Governance-Auditable Decisions
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | VPL (Poddar et al., NeurIPS 2024) | VAE successfully learns latent preference structure from pairwise data | Strong |
| Step 1 → Step 2 | EM-DPO (Chidambaram et al., 2024) | Latent annotator types are discoverable via expectation-maximization | Strong |
| Step 2 → Step 3 | ArmoRM (Wang et al., 2024) | Multi-head reward modeling achieves SOTA on RewardBench with interpretability | Strong |
| Step 3 → Step 4 | Gumbel-Softmax (Jang et al., 2016) | Continuous relaxation enables end-to-end training with discrete decisions | Strong |
| Step 4 → Outcome | Policy Aggregation (Alamdari et al., 2024) | Social choice methods applicable to RL policy aggregation | Medium |

**Key Tension:**
- **Tension:** VPL focuses on user-centric personalization (individual preferences), while CAVD targets value-system-centric discovery (shared moral frameworks). The same VAE architecture may optimize for different latent structures depending on the objective.
- **Resolution:** CAVD uses MFQ correlation as an explicit training signal or post-hoc validation to ensure discovered clusters align with moral frameworks rather than idiosyncratic user preferences. Ablation study will compare user-centric vs value-centric objectives.

### 1.4 Key Assumptions

1. **Preference disagreements reflect genuine value diversity rather than noise**
   - Supporting evidence: Braun (2023) shows legal ML datasets systematically remove disagreement traces, implying signal is lost
   - Consequence if violated: VAE will discover noise clusters; MFQ correlation will be near zero

2. **K=3-10 clusters are sufficient to capture meaningful value diversity**
   - Supporting evidence: Moral Foundations Theory posits 5 core moral foundations; Schwartz Value Survey identifies 10 value types
   - Consequence if violated: Underfitting loses nuance; overfitting creates uninterpretable micro-clusters

3. **Moral Foundations Theory provides valid external validation framework**
   - Supporting evidence: MFQ validated across 30+ cultures with consistent factor structure
   - Consequence if violated: Discovered clusters may be valid but unmappable to known frameworks

4. **Gumbel-Softmax relaxation preserves voting semantics during optimization**
   - Supporting evidence: Gumbel-Softmax widely used in neural architecture search and discrete VAEs
   - Consequence if violated: Inference-time hard voting may diverge from training behavior

### 1.5 Scope & Boundaries

**Where hypothesis applies:**
- Preference data with implicit annotator disagreement (content moderation, ethical judgments, subjective quality)
- Domains requiring transparent value trade-offs (medical AI, policy-relevant AI)
- Settings where governance oversight is required (EU AI Act compliance)

**Where it does NOT apply:**
- Objective tasks with ground truth answers (math, factual QA)
- Individual personalization scenarios
- Low-resource settings (<10K preference pairs)

**Known limitations:**
- Cluster interpretability depends on post-hoc MFQ correlation
- Voting mechanism adds ~5% inference latency
- Requires diverse annotator pool

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Cluster Interpretability):**
If CAVD discovers K latent value clusters from PERSONA preference data, then discovered clusters will correlate with Moral Foundations Questionnaire dimensions with r > 0.3 for at least 3 of 5 MFQ foundations.

*Measurement:* Pearson correlation with Bonferroni correction (5 tests, α' = 0.01)
*Success criterion:* r > 0.3 for ≥3/5 foundations with p < 0.05

**Secondary Predictions:**

**P2 (Preference Preservation):**
CAVD will achieve per-cluster preference accuracy ≥90% of MODPO (with explicit labels) while using only standard unlabeled preference data.

**P3 (Governance Auditability):**
Human evaluators will achieve substantial agreement (κ > 0.6) when identifying which value clusters influenced CAVD model decisions from audit trail outputs.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure:** MFQ correlation r < 0.15 for all 5 foundations
2. **Mechanism Failure:** Per-cluster accuracy < 75% of single-reward baseline
3. **Transparency Failure:** Human evaluator agreement κ < 0.4
4. **Degenerate Clustering:** >80% of samples assigned to single cluster OR entropy < 0.5

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- For detecting r = 0.3 with power = 0.8 and α = 0.05: n ≥ 84 personas
- PERSONA provides 1,586 personas - sufficient

**Test Specification:**
- P1: Pearson r with Bonferroni correction
- P2: Paired t-test, 15 random seeds
- P3: Fleiss' kappa, 5 raters, 50 samples

**Required Experimental Runs:**
- Training: 5 seeds × 4 K values × 2 voting rules = 40 configurations
- Human study: 50 samples × 5 raters = 250 human judgments

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does latent value structure exist in standard preference data, discoverable via variational inference, that correlates with established moral frameworks (MFQ)?"
- Maps to: P1 (Cluster Interpretability)
- Verification type: Empirical correlation analysis
- Critical: MUST PASS - if no structure exists, entire hypothesis fails

**SH2 (Mechanism):**
"Is the proposed 4-step mechanism the actual cause of governance-auditable pluralistic alignment?"

Will decompose into 4 sub-hypotheses in Phase 2B:
- **H-M1:** VAE encoder discovers meaningful (non-degenerate) clusters
- **H-M2:** K reward heads learn specialized preference functions
- **H-M3:** Gumbel-Softmax voting produces interpretable aggregation
- **H-M4:** Audit trail enables human identification of value contributions

**SH3 (Comparison):**
"Does CAVD provide advantages over baselines (VPL, MODPO) in governance transparency while maintaining competitive preference accuracy?"
- Maps to: P2 and P3
- Verification type: Comparative empirical

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-CAVD-v1
- [x] Confidence level specified: 0.78
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=4 steps)
- [x] Causal chain length determined: N=4
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 defined)
- [x] Falsification criteria are defined (4 conditions)
- [x] Baselines are identified for comparison
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:**
   - GPU: Single 80GB A100 sufficient for 40 configurations?
   - Time: Estimated 2-3 months - realistic?

2. **Data Availability:**
   - PERSONA benchmark: Confirmed available
   - MFQ scores: Verify if PERSONA personas have MFQ annotations

3. **K Selection Priority:**
   - Start with K=5 (theory-motivated) and expand if needed?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
