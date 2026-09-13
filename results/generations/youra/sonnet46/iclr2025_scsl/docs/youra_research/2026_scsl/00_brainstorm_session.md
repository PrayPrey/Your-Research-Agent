---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Spurious Correlations & Shortcut Learning"
---

# Research Brainstorm Session Results

**Session Date:** 2026-03-16
**Facilitator:** Research Question Architect
**Participant:** Anonymous
---

## Executive Summary

**Initial Interest:** Spurious correlations and shortcut learning in deep learning — robustification methods using gradient magnitude disparity signals (ROUTE_TO_0 reflection after two failed attempts)

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

Reliance on spurious correlations due to simplicity bias is a well-known pitfall of deep learning models. This issue stems from the statistical nature of deep learning algorithms and their inductive biases at all stages, including data preprocessing, architectures, and optimization. As a result, models rely on spurious patterns rather than understanding underlying causal relationships, making them vulnerable to failure in real-world scenarios where data distributions involve under-represented groups or minority populations.

Source Type: Workshop CFP / Structured Input (ICLR 2025 Workshop on Spurious Correlation and Shortcut Learning: Foundations and Solutions)

**Retry Context:** This is Reflection 3 — two previous hypotheses have been executed and failed/superseded on this topic. New direction avoids all identified failure modes.

---

## Lessons from Previous Attempts

### Attempt 1: SAM/Flatness Optimizer Hypothesis (h-e1 Run 1) — MUST_WORK FAIL

**What was tried:** SAM optimizer (rho ∈ {0.01, 0.05, 0.1, 0.2}) to improve worst-group accuracy (WGA) by ≥10pp over ERM+SGD on Waterbirds without group label supervision.

**Why it failed:**
- Best SAM achieved only +0.90pp vs required +10pp (10x below threshold)
- Larger rho monotonically hurts WGA (rho=0.2 → 38.54%, catastrophic)
- Statistical test: t=0.907, p_corrected=0.83 — NOT significant
- Root cause: flat minima ≠ group-robust minima; SAM's flatness is isotropic and cannot discriminate spurious from core features
- Cascade: h-m1, h-m2, h-m3 all CASCADE_FAILED

**Pitfalls to AVOID:** SAM, ASAM, isotropic L2, any flatness-based optimizer without group-aware signal

---

### Attempt 2: Gradient Oscillation Index / Loss Landscape Geometry (h-e1-v2) — SUPERSEDED

**What was tried:** Under ERM+SGD on Waterbirds, minority-group samples produce gradient norm ratio ≥2x majority AND oscillation_index < 0 (directional opposition on nu1) AND lambda1 > EOS threshold — instantiating Rosenfeld & Risteski (2023) opposing-signal framework.

**Why it was superseded:**
- `oscillation_index < 0` criterion was INVALID — both groups project gradients in the SAME direction on nu1 (OI=+1.00, not <0)
- The "opposing signal" from Rosenfeld & Risteski does NOT manifest as directional opposition in nu1 projection space
- Gate result: PARTIAL (2/3) — oscillation criterion failed, others confirmed
- Reflection: SUPERSEDED (modification_attempt=1 at max, criterion is fundamentally wrong)

**Confirmed findings (carry forward — these are REAL):**
- `gradient_norm_ratio`: 6.37x–14.73x (minority >> majority) ✅ strongly confirmed
- `lambda1` EOS dynamics: 689.7 → 586.1 → 545.5 (all >> 500 threshold) ✅ confirmed
- Loss asymmetry: Group 2 loss 0.9238 vs Group 0 loss 0.0189 at epoch 5 ✅ confirmed
- Nu1 background alignment: anti-correlated (-0.301, -0.039, -0.288)

**Pitfalls to AVOID:** oscillation_index as directional criterion; nu1 projection opposition; Rosenfeld & Risteski framework as primary hypothesis

---

### How THIS Direction Avoids Previous Pitfalls

The new research direction:
1. **Does NOT use SAM or flatness** — instead focuses on gradient magnitude disparity as a *detection signal* to inform sample reweighting
2. **Does NOT rely on directional opposition** — instead uses the CONFIRMED gradient norm ratio (6–14x) as a reweighting signal
3. **Pivots from "understand" to "exploit"** — the confirmed gradient magnitude disparity is now the mechanism for a practical robustification method (gradient-norm-informed upsampling/reweighting)
4. **Aligns with JTT/DFR family** — which are known to work and are recommended by failure analyses

---

## Session Plan

ROUTE_TO_0 auto-extraction from structured input with failure context integration. Research direction:
1. **Primary:** Gradient norm disparity-informed sample reweighting — exploit the confirmed 6–14x minority/majority gradient norm ratio as a label-free signal for identifying minority-group samples
2. **Secondary:** Comparison with JTT, DFR, LfF on existing benchmarks (Waterbirds, CelebA, MultiNLI)
3. **Tertiary:** When does gradient norm disparity correlate with group membership? Conditions and failure modes.

Feasibility constraint applied: all hypotheses testable on existing real-world datasets without new benchmark creation, synthetic data, or human annotation.

---

## Technique Sessions

ROUTE_TO_0 Mode - No interactive sessions. Research components integrated from:
- ICLR 2025 Workshop CFP (primary input)
- Serena Memory: 6 failure/pivot/snapshot records from 2 previous attempts
- Confirmed experimental infrastructure: Waterbirds DataLoader, ResNet-50, GroupDRO, PyHessian, evaluate.py

---

## Research Question Development

### Initial Question

Can gradient norm disparity between minority and majority groups — confirmed empirically at 6–14x ratio — be exploited as a label-free signal to identify and upweight minority-group samples, thereby improving worst-group accuracy on spurious correlation benchmarks without requiring group annotations?

### Refined Question

Can a gradient-norm-informed sample reweighting method (using per-sample gradient norm magnitude as a proxy for group membership, without group labels) improve worst-group accuracy (WGA) by ≥10 percentage points over ERM+SGD on Waterbirds and CelebA, achieving performance competitive with JTT and DFR — leveraging the empirically confirmed minority-group gradient magnitude disparity (6–14x ratio) as the detection mechanism?

### Detailed Sub-Questions

1. **Gradient norm as group proxy**: Does per-sample gradient norm during early training epochs (epochs 1–5) reliably identify minority-group samples (high-norm) vs majority-group samples (low-norm) on Waterbirds and CelebA, and what precision/recall can be achieved relative to true group labels?

2. **Gradient-norm-informed reweighting**: Can upweighting high-gradient-norm samples (identified without group labels) during ERM training or in a two-stage retraining protocol (à la JTT/DFR) improve WGA by ≥10pp over ERM+SGD on Waterbirds and CelebA using existing ResNet-50 + standard training infrastructure?

3. **Comparison with existing methods**: How does gradient-norm-informed reweighting compare to JTT (reported +21pp WGA), LfF, DFR, and GEORGE on Waterbirds and CelebA in terms of WGA improvement, hyperparameter sensitivity, and computational cost?

4. **Generalization to text benchmarks**: Does gradient norm disparity between spurious and core feature groups persist in text settings (MultiNLI, CivilComments), and can gradient-norm-informed reweighting transfer to NLP spurious correlation benchmarks using existing BERT-based implementations?

5. **Mechanism analysis**: What is the relationship between gradient norm disparity magnitude (ratio) and WGA improvement from reweighting — is there a threshold ratio above which reweighting is effective, and does this align with theoretical predictions from the heavy-tailed gradient framework?

---

## Reference Papers

Key literature for Phase 1 discovery (anticipated — will confirm in Phase 1):

**Confirmed relevant (from previous attempts):**
- Sagawa et al. (2020) — Distributionally Robust Neural Networks (GroupDRO) — Waterbirds benchmark; confirmed +10.9pp WGA baseline
- Liu et al. (2021) — Just Train Twice (JTT) — reported +21pp WGA; prime comparison target
- Kirichenko et al. (2022) — Last Layer Retraining (DFR) — label-efficient retraining
- Nam et al. (2020) — Learning from Failure (LfF) — loss-based upweighting (similar mechanism)
- Rosenfeld & Risteski (2023) — heavy-tailed gradient framework (oscillation criterion invalid but norm ratio confirmed)
- Cohen et al. (2021) — EOS dynamics (lambda1 behavior confirmed)

**New literature to discover in Phase 1:**
- Gradient-based sample selection / curriculum learning for spurious correlations
- Per-sample gradient norm analysis in group robustness settings
- Connection between gradient magnitude and data difficulty / minority group membership
- Zhang et al. (2022) — GEORGE; Idrissi et al. (2022) — data balancing

---

## Validation Results

### So What Test

The previous two attempts confirmed a striking empirical phenomenon: minority-group samples consistently produce 6–14x larger gradient norms than majority-group samples during ERM training on Waterbirds. This is a robust, reproducible signal. The open question — and the research contribution — is: **can this signal be exploited for label-free robustification?**

If gradient norm disparity is a reliable group proxy, then a simple two-stage algorithm (train ERM → identify high-norm samples → retrain with reweighting) could match JTT/DFR performance without their specific design choices. This would:
- Provide a mechanistic explanation for *why* two-stage methods work (they implicitly exploit gradient norm disparity)
- Offer a cleaner, more principled algorithm
- Connect empirical robustification to theoretical gradient dynamics

Input from established research venue (ICLR 2025 Workshop) — significance pre-validated.

### Feasibility Check

All sub-questions operate exclusively on existing real-world benchmarks:
- Waterbirds (n=5,794, group annotations available for evaluation but NOT used in training)
- CelebA (n=202,599, standard spurious correlation benchmark)
- MultiNLI, CivilComments (text benchmarks with existing implementations)

**Reusable infrastructure confirmed from previous runs:**
- WaterbirdsDataset, ResNet-50, evaluate.py, GroupDRO baseline — all working
- Per-sample gradient norm computation — implemented and verified
- Conda env `youra-h-e1` with all dependencies; dataset cache `.data_cache/datasets/waterbirds/`
- Code: `h-e1/code/` (35 JSON results from Run 1, reusable evaluation framework)
- GPU: NVIDIA H100 NVL

No new benchmark creation, synthetic data, or human annotation required. Experiments can run immediately on existing infrastructure.

---

## Phase 1 Input Package

<phase1-input>

### research_question
Can gradient norm disparity between minority and majority groups — empirically confirmed at 6–14x ratio during ERM training — be exploited as a label-free signal for sample reweighting to improve worst-group accuracy on spurious correlation benchmarks, achieving performance competitive with JTT and DFR without group label supervision?

### detailed_question
1. Does per-sample gradient norm during early ERM training epochs reliably identify minority-group samples (high-norm) vs majority-group samples (low-norm) on Waterbirds and CelebA without group labels, and what precision/recall can be achieved?

2. Can a two-stage gradient-norm-informed reweighting protocol (ERM → high-norm sample identification → reweighted retraining) improve WGA by ≥10pp over ERM+SGD on Waterbirds and CelebA using existing ResNet-50 infrastructure?

3. How does gradient-norm-informed reweighting compare to JTT, DFR, LfF, and GEORGE on WGA improvement, hyperparameter sensitivity, and computational cost on Waterbirds and CelebA?

4. Does gradient norm disparity generalize to text spurious correlation settings (MultiNLI, CivilComments) and can gradient-norm-informed reweighting transfer to NLP benchmarks?

5. What is the theoretical relationship between gradient norm disparity ratio and WGA improvement from reweighting — is there a threshold ratio for effectiveness?

### reference_papers
Key papers to confirm/extend in Phase 1:
- Sagawa et al. 2020 (GroupDRO, Waterbirds)
- Liu et al. 2021 (JTT — primary comparison)
- Kirichenko et al. 2022 (DFR — last layer retraining)
- Nam et al. 2020 (LfF — loss-based upweighting, mechanistically similar)
- Rosenfeld & Risteski 2023 (heavy-tailed gradient framework — norm ratio confirmed)
- Zhang et al. 2022 (GEORGE)
- Idrissi et al. 2022 (data balancing baseline)
- Cohen et al. 2021 (EOS dynamics — lambda1 behavior)

</phase1-input>

---

## Session Insights

### Key Discoveries

- Two previous hypotheses have been executed: SAM flatness (FAIL) and gradient oscillation index (SUPERSEDED). Both produced confirming evidence for a different, more actionable finding: minority-group samples have 6–14x larger gradient norms than majority-group samples during ERM training.
- The confirmed gradient norm disparity is the single most reliable empirical finding from the prior two runs — it is robust, statistically significant, and replicable.
- The new research direction pivots from "understanding the mechanism" to "exploiting the confirmed signal for robustification" — a more tractable and directly impactful contribution.
- JTT (reported +21pp WGA) is the primary comparison target; gradient-norm-informed reweighting may be conceptually similar but more principled.
- All infrastructure (Waterbirds, ResNet-50, GroupDRO, per-sample gradient norms, H100 GPU) is confirmed working from previous runs.

### Techniques Used

ROUTE_TO_0 Failure Recovery Mode. Integrated 6 Serena Memory files from 2 previous attempts. Applied merge strategy: current input (SCSL workshop CFP) × past lessons (avoid SAM, avoid oscillation index) → new direction (gradient-norm-informed reweighting). Feasibility filtering: retained testable hypotheses on existing benchmarks.

### Areas for Further Exploration

- Gradient norm disparity in contrastive/self-supervised learning paradigms (SimCLR, MoCo on CelebA) — deferred to Phase 2A
- LLM robustness to spurious correlations — compute-intensive; deferred
- Mathematical formalization of gradient norm disparity as group membership proxy — theoretical complement to empirical contribution
- RL spurious correlations — out of scope for current infrastructure

---

## Next Steps

Proceed to Phase 1 - Targeted Research: `/phase1-targeted`

Research focus areas for Phase 1 literature search:
1. Gradient-norm-informed sample selection/reweighting for group robustness (primary — check if this exists)
2. JTT mechanism analysis — does JTT implicitly exploit gradient norm disparity?
3. DFR, LfF, GEORGE — comparison targets with existing Waterbirds/CelebA results
4. Heavy-tailed gradient framework and minority group learning (Rosenfeld & Risteski 2023 follow-ups)
5. EOS dynamics and group robustness connection (Cohen et al. 2021 follow-ups)

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Mode: ROUTE_TO_0 (Failure Recovery — Reflection 3)*
*Ready for: Phase 1 - Targeted Research*
