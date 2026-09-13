# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-26T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent-Controller Ablation)
- **Gap ID**: gap-2
- **Gap Title**: No Empirical Evidence of Bidirectional Tension (RLHF Improvement vs Human Calibration Trade-off)
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 10

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 10

**Convergence Reason**: All 6 criteria met — SPECIFIC core claim with statistical threshold, MECHANISM explained via proxy-gold divergence, PREDICTIONS formalized (P1-P3) with test methods and success criteria, NOVELTY articulated (divergence curve + dual-axis coverage ratio), FEASIBILITY confirmed (3-5 days, existing data only), OBJECTIONS addressed (temporal confounding resolved by within-experiment design, construct validity mitigated by explicit labeling, sample size mitigated by Gao replication)

### Key Insights
1. Coste et al. 2023's proxy-gold divergence is the mechanistic seed — the AI→Human proxy metric (RM score) diverges from actual human preference (gold label) under sustained RLHF optimization, which IS the bidirectional tension operationalized
2. The divergence curve must be framed as "calibration-alignment divergence" to avoid the construct validity error of conflating evaluation calibration with user calibration (Lai et al. sense)
3. Coverage ratio alone is insufficient as the primary novel contribution — the divergence curve slope computation is the key empirical claim

### Breakthrough Moments
- Exchange 7 (Dr. Nova): Proposing "calibration-alignment divergence curve" as a novel empirical construct — resolved the confirmatory-only critique of coverage ratio
- Exchange 6 (Prof. Rex): Distinguishing proxy-gold gap (evaluation calibration) from user calibration (Lai et al.) — prevented a construct validity error
- Exchange 8 (Prof. Vera): Identifying Gao et al. 2023 as the replication dataset and formalizing the regression protocol

---

## Final Hypothesis

### Title
Calibration-Alignment Divergence: Empirical Evidence of Bidirectional Tension in RLHF Optimization

### Hypothesis ID
H-BiAlign-v1

### Core Claim
Under NLP alignment evaluation settings (published RLHF benchmark papers 2018-2024), if AI→Human alignment optimization pressure increases (measured as KL budget from base policy), then the calibration-alignment divergence gap (normalized RM score minus gold human preference rate) increases monotonically with a significantly positive slope (β > 0, p < 0.05), because RLHF trains against a proxy metric that diverges from actual human behavioral response under sustained optimization — creating an anti-correlated relationship between proxy-metric optimization and human-behavioral calibration satisfaction.

### Mechanism
RLHF trains against a proxy metric (reward model score) that initially tracks true human behavioral response but diverges under sustained optimization pressure (reward hacking). The proxy-gold gap operationalizes the tension: as the proxy metric improves, human evaluation calibration to the model's true quality degrades. This is Goodhart's Law applied to bidirectional alignment.

**Causal chain (4 steps):**
1. RLHF trains policy to maximize proxy metric (RM score) approximating human preferences
2. As KL budget increases, policy finds outputs maximizing RM score but diverging from actual human preference (reward hacking)
3. Growing proxy-gold gap = AI→Human optimization signal becoming anti-calibrated to human behavioral response
4. Systematic AI→Human evaluation dominance (R > 0.90 coverage ratio) means the field is optimizing proxies that degrade bidirectional alignment

---

## Predictions

| ID | Statement | Test Method | Success Criterion | Falsification |
|----|-----------|-------------|-------------------|---------------|
| **P1** (primary) | Calibration-alignment divergence gap has positive slope vs. KL budget | Digitize Coste et al. 2023 figures; linear regression gap ~ KL_budget | β > 0, p < 0.05, R² > 0.5 | β ≤ 0 or p > 0.05 |
| P2 | Same positive slope replicates in Gao et al. 2023 | Same digitization + regression on Gao et al. figures | β > 0, p < 0.05 | Non-positive slope in Gao et al. |
| P3 | AI→Human coverage ratio R > 0.90 | Dual-axis classification of Phase 1 benchmark papers | R > 0.90 | R < 0.80 |

---

## Novelty

**What's new:**
- First empirical quantification of the calibration-alignment divergence curve as a bidirectional alignment construct
- First application of dual-axis classification schema to compute AI→Human coverage ratio in alignment benchmark literature
- Reframing of RLHF reward hacking (existing finding) as bidirectional alignment tension (novel interpretation)

**How it differs from prior work:**
- ICLR 2025 survey: qualitative taxonomy only, no coverage ratio, no divergence curve
- Coste et al. 2023: frames proxy-gold divergence as reward hacking, not bidirectional alignment
- Gao et al. 2023: studies scaling properties of divergence, not bidirectional alignment framing

---

## Experimental Design

**Primary dataset:** Coste et al. 2023 (arXiv 2310.02743) figure data — digitized using WebPlotDigitizer
**Replication dataset:** Gao et al. 2023 (arXiv 2210.10760) figure data — same digitization
**Meta-analysis corpus:** Phase 1 alignment benchmark papers (TruthfulQA, BBQ, HELM, HHH-RLHF, WinoBias, InstructGPT, Constitutional AI, MACHIAVELLI, Sorensen 2024)

**Tools:**
- WebPlotDigitizer (free, browser-based): figure digitization
- Python scipy.stats.linregress: regression analysis
- Python pandas: coverage ratio computation

**Timeline:** 3-5 days

---

## Limitations

1. Coverage ratio based on n≈10 papers (not the full 400-paper ICLR 2025 corpus) — limited representativeness
2. Figure digitization introduces ~2-5% measurement imprecision
3. Proxy-gold gap measures evaluation calibration, NOT user calibration (Lai et al. sense) — distinct construct, explicitly scoped
4. Sample size n≈5-10 per regression limits statistical power — report 95% CI on β

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met at Exchange 10 |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Labeling (evaluation vs. user calibration); coverage ratio framing (quantification, not discovery) |

---

*Phase 2A Complete — Ready for Phase 2B*
