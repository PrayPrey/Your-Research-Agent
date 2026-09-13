---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Loss Trajectory Analysis for Spurious Correlation"
---

# Research Brainstorm Session Results

**Session Date:** 2026-04-14
**Facilitator:** Research Question Architect
**Participant:** Anonymous
---

## Executive Summary

**Initial Interest:** Understanding and mitigating spurious correlations in deep learning through novel detection and robustification methods, focusing on foundations and testable mechanisms using existing benchmarks.

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode)

**Session Duration:** < 1 minute (automated extraction with failure context integration)

---

## Starting Context

Spurious correlations and shortcut learning represent fundamental challenges in deep learning robustness. Models rely on spurious patterns rather than causal relationships, failing on under-represented groups. This workshop CFP targets three key areas: (i) evaluation benchmarks, (ii) robustification methods, and (iii) foundations of spurious correlations.

Source: ICLR 2025 Workshop on Spurious Correlation and Shortcut Learning CFP
Retrying after 7+ previous failed attempts with comprehensive lessons learned.

**MANDATORY FEASIBILITY CONSTRAINTS:**
- Must use EXISTING real datasets and benchmarks (Waterbirds, CelebA, etc.)
- NO new benchmarks, rubrics, or scoring frameworks
- NO synthetic/generated data
- NO human evaluation or subjective scoring

---

## Lessons from Previous Attempts

### Summary of ALL Failed Approaches (7+ Runs)

**Run 1: GNGR (Gradient-Norm Guided Reweighting)**
- What was tried: Use gradient norms to identify minority samples, then upweight them
- Why it failed: Detection worked (AUC=0.914) but intervention achieved only +1.14% WGA (needed ≥3%)
- Key insight: **Detection ≠ Intervention success**

**Run 2: LC-GNR Layer Localization**
- What was tried: Hypothesis that gradient divergence localizes to classifier layers
- Why it failed: Direction REVERSED - encoder divergence > classifier divergence
- Key insight: **Spurious feature encoding happens in ENCODER, not classifier**

**Run 3: CISR/CMGR (SAM-based Curvature Interventions)**
- What was tried: SAM training to reduce spurious features via flat minima
- Why it failed: SAM INCREASED spurious probe accuracy; feature collapse (effective rank 125→14.7)
- Key insight: **SAM causes feature collapse and amplifies spurious features**

**Run 4: VGCS (Velocity-Gated Channel Suppression)**
- What was tried: Use learning velocity at epoch T=3 to separate groups
- Why it failed: AUC=0.5146 (random chance); p-value=0.6976
- Key insight: **Velocity does NOT separate groups; margin confounds everything**

**Run 5: Cluster-Based SSL Fairness Diagnostics**
- What was tried: Use clusterability (AMI) as geometric fairness diagnostic
- Why it failed: AMI=0.28 < 0.40; spurious features don't form discrete clusters
- Key insight: **Spurious correlations are linearly separable, not clustered**

**Run 6: Adaptive Margin Regularization**
- What was tried: Encoder representation constraints for low-margin samples
- Why it failed: Margin-based encoder regularization insufficient
- Key insight: **Margin-based approaches don't target spurious features**

**Run 7: Attribution Divergence Existence (MOST RECENT)**
- What was tried: Test if minority/majority groups show different attribution patterns (IoU < 0.3)
- Why it failed: **IoU = 0.6477** (expected < 0.3), P-value = 1.0
- Key insight: **Attribution patterns are SIMILAR between groups, NOT different**
- Critical finding: Despite 25% WGA gap (70% vs 95%), minority and majority groups rely on the SAME input features
- Alternative explanation: The difficulty may be in **feature extraction quality**, not feature selection

### What Run 7 Taught Us

The attribution divergence failure reveals a fundamental insight:

**The WGA gap is NOT caused by different feature reliance.**

Both minority (waterbird-on-land) and majority (waterbird-on-water) samples show similar top-10% attribution regions (IoU = 0.6477). This means:
- The model is NOT looking at different parts of the image
- The model IS looking at similar regions but extracting features DIFFERENTLY
- The challenge is **feature extraction under domain shift**, not feature selection

This suggests:
1. **Input masking won't help** - groups use similar input regions
2. **Attention mechanisms won't help** - attention is already similar
3. **The problem is in HOW features are processed**, not WHERE the model looks

### Critical Constraints for This Run

1. **NO attribution-based methods** - Attribution is similar between groups (IoU > 0.6)
2. **NO input masking/attention** - Groups use similar input regions
3. **NO velocity/learning-speed detection** - Empirically random chance
4. **NO SAM/flat-minima interventions** - Causes feature collapse
5. **NO cluster-based diagnostics** - Spurious features are linear, not clustered
6. **NO margin-based encoder regularization** - Already failed
7. **NO classifier-layer-only interventions** - Encoder divergence is greater

### Validated Findings to Preserve

1. **Gradient norm detection works** (AUC=0.914, 8.8x minority/majority ratio)
2. **Encoder representations diverge** (CKA=0.115 between groups)
3. **Linear separability exists** in embeddings
4. **Attribution patterns are SIMILAR** between groups (IoU=0.6477) - groups look at same regions
5. **20-epoch POC validation** identifies failures early
6. **Detection succeeds, intervention fails** - The core pattern

---

## Session Plan

Auto-extracted from structured input with comprehensive failure context integration.

**New Strategy - Loss Trajectory Divergence Analysis:**

Given that:
- Attribution is SIMILAR between groups (same input regions attended)
- Representations DIVERGE (CKA=0.115)
- Feature extraction quality differs, not feature selection

The NEW hypothesis focuses on **WHEN and HOW** representations diverge during training:

**Loss Trajectory Divergence:** Do minority and majority samples show divergent loss trajectories during training, and can early-epoch trajectory characteristics predict group membership before accuracy gaps emerge?

This is fundamentally different because:
1. **Temporal analysis** - Focus on training dynamics, not static attributions
2. **Per-sample tracking** - Individual loss curves, not group-averaged attributions
3. **Early-epoch signals** - Predict before spurious reliance is entrenched
4. **No intervention required for existence test** - Pure analysis hypothesis

**Why this might work:**
- Gradient norms detect minorities (AUC=0.914) → gradients carry group information
- But static gradients don't translate to successful intervention
- Loss TRAJECTORIES capture how the model learns each sample over time
- Minority samples may have distinctive loss curves (slower convergence, higher variance)
- Early trajectory divergence could enable pre-emptive intervention

---

## Technique Sessions

Auto-Fill Mode - No interactive sessions (ROUTE_TO_0 with comprehensive failure context from 7+ previous runs)

---

## Research Question Development

### Initial Question

Given that attribution patterns are similar between groups but representations diverge, can we use per-sample loss trajectories during training to identify when and how minority/majority samples begin to diverge, enabling early detection of spurious correlation susceptibility?

### Refined Question

**Do per-sample loss trajectories exhibit statistically significant divergence between minority and majority group samples during the first N epochs of training, and can trajectory-based features (convergence rate, variance, inflection points) predict group membership with AUC > 0.75 on existing spurious correlation benchmarks (Waterbirds, CelebA)?**

This question addresses:
- **Temporal dynamics:** When does the divergence emerge during training?
- **Per-sample granularity:** Individual loss curves, not group aggregates
- **Trajectory features:** Multiple signals - rate, variance, shape characteristics
- **Purely analytical:** No intervention required - tests an existence hypothesis
- **Clear metric:** AUC for group prediction from trajectory features
- **Uses existing benchmarks:** Waterbirds, CelebA

### Detailed Sub-Questions

1. **Loss Trajectory Divergence Existence:** Do minority samples exhibit statistically distinct loss trajectory patterns (e.g., slower initial descent, higher epoch-to-epoch variance) compared to majority samples during the first 10 epochs, measurable as trajectory distance > threshold with p < 0.05?

2. **Temporal Emergence:** At what epoch T do loss trajectories begin to diverge significantly between groups, and does this precede the emergence of the worst-group accuracy gap?

3. **Trajectory Feature Predictiveness:** Can simple trajectory features (mean loss slope epochs 1-5, loss variance epochs 1-10, convergence epoch) predict minority group membership with AUC > 0.75, outperforming random chance (0.5)?

4. **Cross-Benchmark Consistency:** Does loss trajectory divergence generalize from Waterbirds to CelebA with consistent divergence patterns, validating that this is a general phenomenon of spurious correlation rather than dataset-specific?

5. **Relationship to Gradient Norms:** Given that gradient norms achieve AUC=0.914 for minority detection at a single epoch, does trajectory-based prediction achieve comparable or better AUC by capturing temporal patterns?

---

## Reference Papers

**Key References (to discover in Phase 1):**
1. **Loss landscape dynamics** - How loss evolves during training for different samples
2. **Example difficulty/forgetting** - Papers on sample-level training dynamics
3. **Curriculum learning** - Literature on sample ordering based on difficulty
4. **Deep learning dynamics** - Temporal patterns in neural network training
5. **Spurious correlation detection** - Methods for identifying affected samples

**Methodological References:**
- Arpit et al. "A Closer Look at Memorization in Deep Networks" (per-sample dynamics)
- Toneva et al. "An Empirical Study of Example Forgetting during Deep Neural Network Learning"
- Papers on loss curve analysis and training dynamics
- Literature on early stopping and convergence patterns

**Note:** Specific paper discovery will occur in Phase 1 - Targeted Research.

---

## Validation Results

### So What Test

**Significance:** This research addresses a fundamental gap: despite successful detection (gradient norms AUC=0.914), no intervention has succeeded. The loss trajectory approach is FUNDAMENTALLY DIFFERENT because:

1. **Temporal analysis:** All previous methods analyzed static snapshots (gradients at epoch T, attributions post-training). Loss trajectories capture the DYNAMIC process of learning.

2. **Explains the attribution paradox:** Attribution similarity (IoU=0.6477) suggests groups use similar features, but representations diverge. Loss trajectories may reveal WHEN this divergence emerges during training.

3. **Connects detection to intervention timing:** If trajectory divergence predicts group membership AND occurs early (epoch < 5), this suggests a window for early intervention before spurious reliance is entrenched.

4. **No intervention required for validation:** This is a pure EXISTENCE hypothesis - we're testing whether trajectory divergence exists. This avoids the "detection works but intervention fails" trap.

**Impact if successful:**
- First temporal characterization of spurious correlation emergence
- Identifies optimal timing window for intervention
- Provides interpretable per-sample difficulty measure
- Foundation for trajectory-aware training algorithms

### Feasibility Check

**Feasibility Assessment: HIGH**

1. **Uses EXISTING benchmarks:**
   - Waterbirds: Standard benchmark, group labels available
   - CelebA: Standard benchmark, attribute labels available
   - No new data collection required

2. **Simple methodology:**
   - Train ERM model with per-sample loss logging (standard PyTorch)
   - Compute trajectory features (mean, variance, slope - basic statistics)
   - Predict group membership from features (logistic regression/RF)
   - No novel algorithm development required

3. **Builds on validated infrastructure:**
   - ERM training pipeline (validated in 7 runs)
   - Group stratification methodology (validated)
   - 20-epoch POC validation approach (validated)
   - Gradient computation (validated - for comparison)

4. **Clear success criteria:**
   - Primary: Trajectory features predict minority membership with AUC > 0.75
   - Secondary: Trajectory divergence emerges before accuracy gap (epoch T_divergence < T_gap)
   - Tertiary: Divergence generalizes to CelebA

5. **NO violations of feasibility constraints:**
   - Uses existing datasets (Waterbirds, CelebA)
   - No new benchmarks or rubrics
   - No synthetic data
   - No human evaluation (trajectory comparison is automated)

6. **Low implementation risk:**
   - Loss logging is trivial (already done in most training loops)
   - Trajectory features are simple statistics
   - Classification is standard ML pipeline

---

## Phase 1 Input Package

<phase1-input>

### research_question
Do per-sample loss trajectories exhibit statistically significant divergence between minority and majority group samples during the first N epochs of training, and can trajectory-based features (convergence rate, variance, inflection points) predict group membership with AUC > 0.75 on existing spurious correlation benchmarks (Waterbirds, CelebA)?

### detailed_question
1. Do minority samples exhibit statistically distinct loss trajectory patterns (slower descent, higher variance) compared to majority samples during the first 10 epochs, with trajectory distance > threshold and p < 0.05?
2. At what epoch T do loss trajectories begin to diverge significantly, and does this precede the worst-group accuracy gap emergence?
3. Can simple trajectory features (loss slope, variance, convergence epoch) predict minority group membership with AUC > 0.75?
4. Does loss trajectory divergence generalize from Waterbirds to CelebA with consistent patterns?
5. How does trajectory-based prediction compare to gradient norm detection (AUC=0.914)?

### reference_papers
Not provided - will discover in Phase 1. Priority search areas:
- Per-sample loss dynamics and training curves
- Example difficulty and forgetting in deep learning
- Curriculum learning and sample difficulty measures
- Training dynamics in neural networks
- Spurious correlation detection via training signals
- Loss landscape analysis methods

</phase1-input>

---

## Session Insights

### Key Discoveries

1. **Attribution similarity paradox:** Despite 25% WGA gap, attribution patterns are similar (IoU=0.6477). The problem is NOT where the model looks, but HOW it processes what it sees.

2. **Detection works, intervention fails:** 7 runs confirm this pattern. Need to understand WHEN divergence emerges, not just THAT it exists.

3. **Temporal analysis is unexplored:** All previous methods analyzed static snapshots. Loss trajectories capture the dynamic learning process.

4. **Loss curves are per-sample:** Unlike group-averaged attributions, loss trajectories provide individual sample characterization throughout training.

5. **Early detection window:** If trajectory divergence emerges early, it suggests a window for intervention before spurious reliance is entrenched.

### Techniques Used

Auto-Fill Mode (ROUTE_TO_0 with comprehensive failure context integration from Serena Memory - 7+ previous runs analyzed, including attribution divergence failure)

### Areas for Further Exploration

1. **Trajectory feature engineering:** Which loss curve characteristics best predict group membership
2. **Temporal granularity:** Per-epoch vs. per-batch loss tracking
3. **Multi-scale analysis:** Early epochs (1-5), mid epochs (5-10), late epochs (10-20)
4. **Comparison to gradient norms:** Does trajectory analysis outperform or complement gradient-based detection
5. **Intervention implications:** If trajectory divergence is early, can we design trajectory-aware training

---

## Next Steps

**Proceed to Phase 1 - Targeted Research**

Focus areas for literature review:
1. Per-sample loss dynamics during neural network training
2. Example difficulty, forgetting, and memorization studies
3. Curriculum learning and self-paced learning methods
4. Training dynamics and convergence analysis
5. Spurious correlation detection via training signals
6. Loss landscape geometry and its evolution

Command: `/phase1-targeted`

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
