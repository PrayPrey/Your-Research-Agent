---
paper_id: "2212.04629"
title: "Post hoc Explanations may be Ineffective for Detecting Unknown Spurious Correlation"
authors: "Adebayo, Muelly, Abelson, Kim"
year: 2022
arxiv_id: "2212.04629"
venue: "ICLR 2022"
citations: 109
---

# Paper Summary: Post hoc Explanations May Be Ineffective for Detecting Unknown Spurious Correlation

## Key Contributions

**Core Finding:** Feature attribution methods (Grad-CAM, Integrated Gradients, Guided Backprop) FAIL to reliably detect unknown spurious correlations, especially non-visible artifacts like background blur.

**Critical Limitation Identified:**
- When spurious signal is **KNOWN** at test-time → attribution methods can confirm reliance on VISIBLE signals (text tags, stripe patterns)
- When spurious signal is **UNKNOWN** → methods fail to detect reliance, even for visible signals
- For **NON-VISIBLE** artifacts (background blur) → methods fail even when signal is known

**Three Performance Metrics Introduced:**
1. **K-SSD** (Known Spurious Signal Detection): Can method detect reliance when spurious signal is explicitly tested?
2. **CCM** (Cause-for-Concern): Can method distinguish spurious vs normal models when signal unknown?
3. **FAM** (False Alarm): Does method erroneously indicate spurious reliance in normal models?

**User Study Result:** When practitioners were **blinded** (spurious signal unknown), NONE of the methods tested were effective for detecting spurious reliance. Only TCAV (concept activation) showed effectiveness when practitioners were NOT blinded and signal was visible.

## Methodology

**Experimental Design:**
- Semi-synthetic datasets with controlled spurious artifacts:
  - Medical imaging (bone age detection) with visible TAG, visible STRIPE pattern, non-visible BLUR
  - Dog species classification with spurious backgrounds
- Train "spurious models" that verifiably rely on injected artifacts vs "normal models" that don't
- Test 3 explanation classes: feature attribution (IG, SmoothGrad, GradCAM, GBP), concept activation (TCAV), training point ranking (influence functions)

**Key Experimental Conditions:**
- **Known Setting:** Practitioner explicitly tests for hypothesized spurious signal
- **Unknown Setting:** Practitioner analyzes explanations without knowing what to look for
- **Blinded User Study:** 200 participants randomly assigned to blinded/not-blinded groups

## Experiments & Results

**Feature Attribution Results:**
- **K-SSD metric** (known signal): Methods CAN detect visible TAG and STRIPE when explicitly tested, but FAIL for BLUR
- **CCM metric** (unknown signal): Methods CANNOT distinguish spurious vs normal models when signal unknown
- **FAM metric** (false alarms): Feature attribution methods show HIGHER false alarm rates than true detection — erroneously indicate spurious reliance in normal models

**Specific Numbers (Table 1 excerpt):**
- Tag signal detection (known): IG 0.87±0.01, SmoothGrad 0.77±0.024 (successful)
- Blur signal detection (known): IG 0.50±0.016, SmoothGrad 0.64±0.015 (near-random)
- CCM scores universally low across all methods and signals

**TCAV (Concept Activation) Results:**
- Can detect TAG and STRIPE when known (KS-test rejects null hypothesis)
- FAILS for BLUR even when known
- Less susceptible to false positives than feature attribution
- When unknown: CCM metric shows high similarity between spurious/normal model concept rankings (cannot distinguish)

**User Study Results (Table 4):**
- Median Likert scores (1-5, higher = more likely to recommend model):
- Blinded spurious models: 3-3∗ across all methods (participants did NOT reject spurious models)
- Not-blinded spurious models: Only TCAV showed rejection (median 2∗), others failed
- Implication: Even with explanations, practitioners struggle to identify spurious models without prior knowledge

## Related Work & Baselines

**Methods Tested:**
- **Feature Attribution:** Integrated Gradients, SmoothGrad, Grad-CAM, Guided Backprop
- **Concept Activation:** TCAV (Testing with Concept Activation Vectors)
- **Training Point Ranking:** Influence Functions

**Comparison Context:**
- Previous work (Ribeiro et al. 2016 LIME, Lapuschkin et al. 2019) showed attribution can detect spurious when signal is known and visible
- This work shows fundamental limitation: effectiveness breaks down when signal unknown or non-visible

## Theoretical Framework

**Spurious Score Definition:**
Mathematical measure of model's reliance on spurious signal based on prediction accuracy difference between spurious-present vs spurious-absent inputs.

**Why Attribution Fails for Unknown Spurious:**
1. Practitioner doesn't know what to test for → cannot select right test inputs
2. Attribution maps require knowing target class aligned with spurious signal
3. Non-visible artifacts (blur) don't produce localized high-attribution regions

**Pearl Quote (paper epigraph):** "It is hard to find a needle in a haystack, it is much harder if you haven't seen a needle before."

## Implications for Research

**Direct Challenge to Proposed Hypothesis:**
If we propose gradient-based attribution (Grad-CAM, IG) for spurious correlation detection, this paper shows it will FAIL when spurious features are unknown. This is EXACTLY the scenario we face in real-world deployment.

**Potential Solutions Suggested by Paper:**
- TCAV (concept-based) shows promise for visible signals when concepts predefined
- Need fundamentally different detection paradigm for unknown signals
- Post hoc explanations require prior knowledge to be effective

**Gap This Creates:**
- Cannot use direct gradient attribution for unknown spurious detection
- Need alternative: gradient **abnormality** detection (e.g., GAIA 2023) instead of direct attribution
- Or: automated spurious concept discovery before applying TCAV

## Relevance to Selected Research Gap

**Gap 3 (P0): Attribution effectiveness for unknown spurious features**

This is the FOUNDATIONAL paper documenting the core limitation. Key takeaways:
1. Gradient attribution (Grad-CAM, IG) works ONLY when spurious signal is known and visible
2. For unknown spurious: methods fail at CCM metric (cannot distinguish spurious vs normal models)
3. Non-visible artifacts: even knowing signal doesn't help
4. False alarm rates HIGH: methods indicate spurious reliance in normal models

**Action Items for Hypothesis Design:**
- ❌ Do NOT propose Grad-CAM/IG for unknown spurious detection (proven ineffective)
- ✅ Propose gradient abnormality detection (deviation from expected patterns) instead
- ✅ Consider TCAV-style concept activation IF we can automate concept discovery
- ✅ Focus on visible spurious signals OR develop detection for non-visible signals
- ✅ Design experiments that test UNKNOWN signal scenario (the realistic use case)
