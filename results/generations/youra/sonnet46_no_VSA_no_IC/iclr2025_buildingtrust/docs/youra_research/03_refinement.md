# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-20T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent-Controller Ablation)
- **Gap ID**: gap1
- **Gap Title**: No Cross-Split Predictive Validity Analysis of Trustworthiness Benchmarks
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7
- **Hypothesis ID**: H-TrustPredVal-v1

---

## Research Dialogue Context

**Participants**: Dr. Nova (🔭), Prof. Vera (🔬), Dr. Sage (🎯), Prof. Pax (⚙️), Dr. Ally (🛡️), Prof. Rex (🔍)

**Total Exchanges**: 7

**Convergence Reason**: All 6 criteria met after 7 exchanges. Key evolution: Exchange 1 (Dr. Nova) introduced predictive validity framing and dimension-specific asymmetry hypothesis. Exchange 2-4 established methodological rigor (shift type heterogeneity, common model set, policy significance, feasibility). Exchange 5 (Dr. Ally) synthesized the refined hypothesis (robustness < fairness predictive validity). Exchange 6 (Prof. Rex) identified three critical issues: capability confound, protocol mismatch, directionality grounding. Exchange 7 (Dr. Nova) resolved all three: partial Spearman ρ addresses confound, TrustLLM substitutes for HaluEval, theoretical mechanism grounds directionality.

### Key Insights
1. The capability confound (general NLU quality explains both ID and OOD scores) is the central methodological threat — resolved by partial Spearman ρ controlling for MMLU
2. Evaluation protocol compatibility is a hard constraint — TruthfulQA→HaluEval excluded due to format mismatch
3. The latent-bias-stability vs. adversarial-design distinction provides theoretical mechanism explaining dimension-specific ρ differences
4. Partial ρ framing strengthens novelty: testing whether trustworthiness generalizes *independently of* general capability is a stronger claim than testing whether it generalizes at all

### Breakthrough Moments
- **Exchange 6**: Prof. Rex's capability confound critique → reframed from limitation to core methodological innovation (partial Spearman ρ)
- **Exchange 7**: Dr. Nova's synthesis showing that fixing each critique strengthens the paper → the final hypothesis is stronger than the initial proposal

---

## Final Hypothesis

### Title
Trustworthiness Generalization Predictive Validity: Fairness vs. Adversarial Robustness

### Core Claim (Under-If-Then-Because)
Under evaluation of 15+ publicly available LLMs on matched in-distribution/OOD trustworthiness benchmark pairs, **if** we compute partial Spearman ρ between in-distribution and OOD model rankings (controlling for general capability via MMLU), **then** the fairness dimension (BBQ-Disambig → BBQ-Ambig) shows significantly positive partial ρ (> 0.4, p < 0.05) while the adversarial robustness dimension (GLUE → AdvGLUE, ANLI R1 → R3) shows lower partial ρ, **because** fairness failures reflect stable latent statistical biases in model representations that manifest consistently across distribution shifts, while adversarial robustness benchmarks are specifically designed to overcome models' current capabilities and therefore do not track stable generalizable trustworthiness properties.

### Null Hypothesis
There is no significant difference in partial Spearman ρ (MMLU-controlled) between the fairness dimension (BBQ) and the adversarial robustness dimension (GLUE/ANLI) for in-distribution to OOD model rank prediction (Δρ = 0, Fisher z-test p ≥ 0.05).

### Mechanism
Two competing mechanisms:
1. **Stable Latent Bias** (Fairness): Statistical co-occurrences in pretraining data encoded as stable model weights produce stereotype reliance that manifests in both informative (disambig) and underspecified (ambig) contexts → high rank correlation across splits
2. **Adversarial Disruption** (Robustness): AdvGLUE (14 attack methods) and ANLI R3 (iterative human-model-in-the-loop) are designed to defeat models that pass easier versions → rank reversal by design, low rank correlation across splits

---

## Predictions

| ID | Type | Statement | Success Criterion |
|----|------|-----------|-------------------|
| P1 | Confirmatory | Partial Spearman ρ_fairness (BBQ-Disambig→BBQ-Ambig) is significantly positive after MMLU control | ρ > 0.4 AND p < 0.05 (Fisher z-test, N ≥ 10) |
| P2 | Exploratory/Directional | ρ_fairness exceeds ρ_robustness | Δρ ≥ 0.2 (directional threshold) |
| P3 | Exploratory | Instruction-tuned models show smaller fairness generalization gap than base models | Directional: median fairness TGG_IT < TGG_base |

---

## Novelty

**What's New**: First study to treat cross-split predictive validity as a primary research question for trustworthiness benchmarks. First to apply partial Spearman ρ with capability control to test whether trustworthiness generalizes *independently of* general capability.

**Differentiation**:
- vs. DecodingTrust (Wang 2023): N=2 GPT models, no cross-split ρ as primary question
- vs. TrustLLM (Huang ICML 2024): 16 models, 6 dimensions but no ID→OOD rank correlation as primary metric
- vs. Gevers & Daelemans (2026): Same methodology, applied to trustworthiness (higher stakes) with mechanistic explanation for dimension-specific ρ
- vs. GLUE-X (Yang ACL 2023): Measures accuracy gap, not model rank stability (Spearman ρ)

---

## Experimental Design

**Data Sources**:
- TrustLLM (Huang et al., ICML 2024) — BBQ-Disambig/Ambig scores for 16 models
- GLUE-X (Yang et al., ACL 2023) — GLUE/AdvGLUE scores for 21 models
- OOD_NLP (Yuan et al., NeurIPS 2023) — ANLI R1/R3 scores
- Open LLM Leaderboard / MMLU papers — MMLU capability control scores

**Model Set**: LLaMA-2 (base + Chat), Mistral (base + Instruct), Falcon, GPT-3.5/4, Vicuna, Alpaca (~15+ overlapping)

**Analysis**:
1. Build model × benchmark score matrix
2. Compute raw and partial Spearman ρ per dimension
3. Fisher z-test for P1 (confirmatory) and P2 (exploratory)
4. RLHF pair analysis for P3 (Wilcoxon signed-rank)
5. Sensitivity analysis: MMLU → Winogrande capability proxy

**Baselines**: Random rank (ρ=0), raw Spearman ρ (no MMLU control), Gevers & Daelemans (2026) commonsense ρ reference values

---

## Limitations

- **Reliability dimension excluded**: TruthfulQA→HaluEval protocol mismatch; substitute with TrustLLM consistent hallucination OOD task if reliability coverage needed
- **Common model set N varies**: Report N per analysis cell; flag N < 10 as underpowered
- **MMLU control imperfect**: Sensitivity analysis with Winogrande/ARC required
- **Score aggregation risk**: Cross-paper aggregation may introduce protocol variation; acknowledge as limitation
- **English only**: Results may not generalize to non-English fairness/robustness benchmarks
- **Temporal scope**: Models available 2023-2025; newer models may shift ρ landscape

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-TrustPredVal-v1 |
| **Discussion Convergence** | 7 exchanges, all 6 criteria met |
| **Clarity Verified** | Yes |
| **Phase 2B Ready** | Yes |
| **Remaining Objections** | 3 documented (N reporting, MMLU sensitivity, P2 labeling) — all mitigated |

---

*Phase 2A Complete — Generated by Self-Contained Tikitaka Loop (Independent-Controller Ablation)*
*2026-08-20*
