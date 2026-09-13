# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-04T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Loop (Claude-only, IC-ablation)
- **Gap ID**: gap_1
- **Gap Title**: No Systematic Cross-Benchmark Trustworthiness Trade-off Correlation Study
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 16

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 16 (min_exchanges=15 met at Exchange 15; Under-If-Then-Because finalized in Exchange 16)

**Convergence Reason**: All 6 convergence criteria PASS at Exchange 15. All 6 personas participated with genuine disagreement and challenge across exchanges.

### Key Insights
1. The RLHF-cluster mechanism provides a theoretically motivated prediction of 2-cluster trustworthiness dimension structure — the paper makes specific structural predictions before analyzing data (genuinely predictive, not post-hoc).
2. Scale and alignment confounds (identified by Prof. Rex in Exchange 8) are the central methodological challenge; partial Spearman controlling for log(params) and is_RLHF is the correct response.
3. The MST prescriptive application (Dr. Nova, Exchange 11) elevates the contribution from a descriptive correlation matrix to an actionable minimum evaluation set — the key differentiation from simply "computing ρ on existing data."
4. Both outcome directions are publishable: if trade-off structure is found, it reshapes deployment evaluation practice; if independence is confirmed, it equally reshapes practice by showing no evaluation shortcuts are possible.

### Breakthrough Moments
- **Exchange 5**: Dr. Nova refines from "compute correlation matrix" to "RLHF-cluster 2-block structure hypothesis" — the key theoretical contribution.
- **Exchange 8**: Prof. Rex identifies scale and alignment confounds — forces the methodological upgrade to partial Spearman and Pythia experiment.
- **Exchange 11**: Dr. Nova proposes MST-derived minimum evaluation set — the prescriptive application that makes the paper actionable.
- **Exchange 12**: Prof. Vera adds bootstrap MST stability test — rigorizes the prescriptive claim.

---

## Final Hypothesis

### Title
**Cross-Dimension Trustworthiness Correlation Structure (CDTCS)**

### Hypothesis ID
H-CDTCS-v1

### Core Claim
Under the setting of existing LLM evaluation frameworks (TrustLLM 16-model × 6-dimension scores, HELM 30-model × 7-metric scores, and Pythia-family benchmark evaluations via lm-eval-harness), if we compute partial Spearman rank correlation matrices across trustworthiness dimensions controlling for model scale (log parameter count) and alignment status (RLHF fine-tuning yes/no), then we will observe a 2-cluster correlation structure separating RLHF-sensitive dimensions (safety, ethics) from RLHF-insensitive dimensions (adversarial robustness, calibration/privacy), with a derivable minimum spanning evaluation set of ≤4 dimensions and replication of key cluster signs in HELM data, because RLHF optimization creates a systematic split in how trustworthiness dimensions respond to preference-based training.

### Mechanism
RLHF reward signals directly optimize safety and ethics behavior (making these dimensions co-move: positive partial ρ). Adversarial robustness and calibration/privacy are orthogonal to human preference signals and may degrade when RLHF creates conservative, refusal-prone representations — producing negative cross-cluster partial correlations. The Pythia scaling series (fixed architecture, no RLHF, only scale varies) provides a clean natural experiment isolating scale effects from alignment effects.

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 (primary) | ρ_partial(safety, ethics) > 0.5, TrustLLM n=16 | ρ_partial > 0.5 AND p < 0.0033 | ρ_partial < 0.3 OR p > 0.05 |
| P2 | ρ_partial(safety, robustness) < -0.4, TrustLLM n=16 | ρ_partial < -0.4 AND p < 0.0033 | ρ_partial > 0 OR sign reversal in HELM |
| P3 | 2-cluster hierarchical solution, silhouette > 0.3 | Silhouette > 0.3, clusters align with RLHF-sensitive/insensitive grouping | Silhouette < 0.1 for all k≥2, or k≠2 optimal |
| P4 | MST minimum evaluation set ≤4 dims, ≥90% bootstrap stable | MST set ≤4 dims AND bootstrap stability ≥0.90 | MST requires all 6 dims OR stability < 0.70 |

**Null hypothesis**: All |ρ_partial| < 0.3 across 15 pairwise combinations after Bonferroni correction (α=0.0033); silhouette < 0.1 for all k≥2. Trustworthiness dimensions are statistically independent.

---

## Novelty

**Key Innovation**: Reframes trustworthiness evaluation from "measure all 6 dimensions independently" to "measure the minimum spanning set derived from correlation geometry" — prescriptive output with immediate practical value.

**What's new vs prior work**:
- TrustLLM [Sun et al., 2024]: reports dimension scores but not pairwise Spearman correlation matrix or partial correlation controls
- HELM [Liang et al., 2022]: reports 7-metric scores with qualitative "important trade-offs" finding, no quantified correlation analysis
- Liu et al. [2023] survey (575 citations): explicitly identifies cross-dimension correlation analysis as future work — this paper executes it
- Epoch AI: computes ρ for capability benchmarks (median=0.73) but not trustworthiness dimensions
- MST minimum evaluation set: no prior trustworthiness paper applies MST to identify minimum sufficient evaluation set

---

## Experimental Design

**Primary Data**: TrustLLM published score tables (HowieHwong/TrustLLM GitHub, results/*.json) — 16 models × 6 dimensions, pre-computed.

**Replication Data**: HELM leaderboard data (stanford-crfm/helm) — 30 models × 7 metrics.

**Natural Experiment**: Pythia family (pythia-70m through pythia-12b, 8 checkpoints) via lm-eval-harness — controlled scale experiment with fixed architecture and no RLHF.

**Analysis Pipeline**:
1. Load TrustLLM JSON → 16×6 score matrix + model metadata (log_params, is_RLHF)
2. Partial Spearman ρ for all 15 dimension pairs (control: log_params + is_RLHF)
3. Bonferroni correction (α_corrected = 0.0033)
4. Hierarchical clustering (Ward linkage, silhouette for k=2)
5. MST on (1-|ρ_partial|) distance matrix + 1000-iteration bootstrap stability
6. HELM replication (steps 2-3 with HELM data)
7. Pythia within-family analysis (scale-only correlation structure)

**Tools**: scipy.stats.spearmanr (partial), sklearn.cluster.AgglomerativeClustering, networkx MST, 1000-iteration bootstrap via scipy.

---

## Limitations

1. **Statistical power**: n=16 (TrustLLM) is underpowered for moderate effects; requires |ρ_partial| > 0.55 for Bonferroni-corrected significance. Mitigated by Pythia expansion (n≈24) and HELM replication (n=30).
2. **Convenience sample**: TrustLLM 16 models are not random sample; findings generalize to frontier-model population, not all LLMs.
3. **RLHF mechanism**: Proposed theoretical framework, not directly tested causal claim. The paper tests structural predictions; mechanism is the explanatory account.
4. **Construct sensitivity**: TrustLLM and HELM use different operationalizations of "safety" and "robustness"; cross-framework replication may reflect construct variation.
5. **Temporal scope**: 2024-era model landscape; correlation structure may shift with new training techniques (DPO, RLHF variants).

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-CDTCS-v1 |
| **Discussion Convergence** | CONVERGED at Exchange 15 (all 6 criteria PASS) |
| **Clarity Verified** | Yes |
| **All Personas Participated** | Yes (Dr. Nova ×3, Prof. Vera ×3, Dr. Sage ×3, Prof. Pax ×2, Dr. Ally ×3, Prof. Rex ×2) |
| **Feasibility Constraints** | SATISFIED (existing data, existing benchmarks, no human annotation) |
| **Remaining Objections** | Acknowledged limitations: n=16 power, RLHF mechanism qualification |
| **Next Phase** | Phase 2B — decompose CDTCS into sub-hypotheses (H-E1: cluster structure, H-E2: MST evaluation set) |
