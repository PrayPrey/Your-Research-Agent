---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Spurious Correlation Detection"
---

# Research Brainstorm Session Results

**Session Date:** 2026-03-19
**Facilitator:** Research Question Architect
**Participant:** Anonymous
---

## Executive Summary

**Initial Interest:** Spurious correlation detection and shortcut learning mitigation in deep learning models

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode)

**Session Duration:** < 1 minute (automated extraction with failure context integration)

---

## Starting Context

This research direction emerges from multiple failed attempts to address spurious correlations in deep learning. Previous approaches focused on gradient-based minority detection and optimizer-based robust learning, which proved either computationally infeasible or scientifically invalid for automated pipeline execution.

**Source Type:** ROUTE_TO_0 - Reflection after hypothesis failures
**Recovery Mode:** Learning from 11 failure records to identify viable research direction

---

## Lessons from Previous Attempts

### Failed Approach 1: SAM Optimizer for Group Robustness (h-e1-wga)
**What was tried:** Using Sharpness-Aware Minimization (SAM) to improve worst-group accuracy on Waterbirds dataset
**Why it failed:**
- Flat minima ≠ group-robust minima
- SAM's isotropic flatness doesn't discriminate spurious vs core features
- Best result: +0.90pp (threshold: ≥10pp) - 10x below target
- Larger perturbation radius (rho) monotonically hurt WGA

**Root cause:** Flatness regularization alone cannot substitute for group supervision in spurious correlation settings

### Failed Approach 2: Gradient Norm-Based Minority Detection (h-e1_run3)
**What was tried:** Using per-sample gradient norms as minority group predictors
**Why it failed:**
- ΔAUC: 0.0242 on Waterbirds (target: ≥0.05)
- Statistical significance: p=0.589 (threshold: p<0.01)
- Negative ΔAUC on CelebA (-0.0205)
- Implementation error on text dataset (CivilComments)

**Root cause:** Gradient norms do not reliably encode minority group information across spurious correlation scenarios without additional signals

### Failed Approach 3: Human Annotation Study (superseded_h-e1)
**What was tried:** Multi-week human annotation study with expert reviewers
**Why it failed:** Methodology requires 3-4 weeks of manual coordination, external participants, and web interface development - incompatible with automated pipeline execution

**Root cause:** Phase 4 designed for automated ML experiments, not multi-week human subject research

### Validated Infrastructure (Reusable Components)
From h-e1 attempts:
- WaterbirdsDataset implementation with group metadata
- ResNet-50 backbone (ImageNet pretrained)
- GroupDRO implementation: +10.9pp WGA confirmed
- Full evaluation framework: compute_wga, statistical testing
- Conda env setup, dataset caching pipeline

### Key Insights for New Direction
1. **Automated execution requirement:** Must avoid human studies, multi-week protocols
2. **Avoid isotropic regularization:** Generic flatness/sharpness methods don't target spurious correlations
3. **Need explicit minority awareness:** Some form of proxy or signal required (not just gradient magnitude)
4. **Proven baseline exists:** GroupDRO works but requires group labels
5. **Strong signal validation:** +0.9pp improvements are noise; need ≥5pp minimum for PARTIAL

---

## Session Plan

Generate research direction that:
1. Avoids failed approaches (SAM, raw gradient norms, human studies)
2. Leverages validated infrastructure (Waterbirds, ResNet-50, evaluation framework)
3. Targets automated execution within Phase 4 pipeline constraints
4. Addresses core challenge: minority group identification without explicit labels

---

## Technique Sessions

ROUTE_TO_0 Auto-Fill Mode - Synthesis from failure analysis and lessons learned

---

## Research Question Development

### Initial Question

How can we automatically identify and mitigate spurious correlations in deep learning models without requiring group labels or multi-week human annotation studies?

### Refined Question

Can self-supervised contrastive learning embeddings reveal spurious correlation structure in training data, enabling automated minority group discovery and robust model training without explicit group labels?

### Detailed Sub-Questions

1. Do self-supervised embeddings (SimCLR, MoCo) cluster samples by spurious features vs core features in Waterbirds/CelebA datasets?
2. Can clustering on frozen SSL embeddings identify minority groups with ≥80% precision/recall compared to ground truth?
3. Does retraining with cluster-balanced sampling improve worst-group accuracy by ≥5pp over ERM baseline?
4. Is the SSL-based minority discovery transferable across datasets (Waterbirds → CelebA → CivilComments)?
5. What is the computational overhead of SSL embedding extraction vs end-to-end GroupDRO training?

---

## Reference Papers

Will discover in Phase 1 - Targeted search for:
- Self-supervised learning for spurious correlation detection
- Unsupervised minority group discovery methods
- Contrastive learning bias mitigation approaches
- Cluster-based rebalancing techniques (JTT, DFR variants)

---

## Validation Results

### So What Test

**Significance:** Addresses critical limitation in robust ML - most methods require explicit group labels which are expensive to obtain. Automated minority discovery enables practical deployment of robust training at scale.

**Impact:** If successful, provides drop-in replacement for GroupDRO that doesn't require group annotation, making robust ML accessible to practitioners without labeled spurious features.

**Novelty check:** Phase 1 will validate whether SSL-embedding-based minority discovery has been explored (expected gap: most SSL work focuses on representation quality, not spurious correlation structure)

### Feasibility Check

**Automated execution:** ✅ SSL embedding extraction, clustering, retraining - all scriptable within Phase 4
**Dataset availability:** ✅ Waterbirds, CelebA, CivilComments with ground truth groups for validation
**Computational cost:** ✅ Frozen SSL encoder + k-means = O(N) single pass, not iterative optimization
**Evaluation metrics:** ✅ Existing compute_wga framework, cluster precision/recall vs ground truth
**Infrastructure reuse:** ✅ Leverages validated WaterbirdsDataset, ResNet-50 pipeline, evaluation code

**Risk mitigation:**
- If SSL embeddings don't cluster by spurious features → FAIL caught at MUST_WORK gate (Phase 4)
- If clustering precision <80% → PARTIAL, route to self-modify or redesign
- No multi-week dependencies, no human annotation required

---

## Phase 1 Input Package

<phase1-input>

### research_question
Can self-supervised contrastive learning embeddings reveal spurious correlation structure in training data, enabling automated minority group discovery and robust model training without explicit group labels?

### detailed_question
1. Do self-supervised embeddings (SimCLR, MoCo) cluster samples by spurious features vs core features in Waterbirds/CelebA datasets?
2. Can clustering on frozen SSL embeddings identify minority groups with ≥80% precision/recall compared to ground truth?
3. Does retraining with cluster-balanced sampling improve worst-group accuracy by ≥5pp over ERM baseline?
4. Is the SSL-based minority discovery transferable across datasets (Waterbirds → CelebA → CivilComments)?
5. What is the computational overhead of SSL embedding extraction vs end-to-end GroupDRO training?

### reference_papers
Not provided - will discover in Phase 1 (targeted search for SSL spurious correlation detection, unsupervised minority discovery, contrastive learning bias mitigation)

</phase1-input>

---

## Session Insights

### Key Discoveries

**Core insight from failures:** All previous attempts failed because they either:
1. Used isotropic signals (SAM flatness, raw gradient norms) that don't discriminate spurious features
2. Required human intervention incompatible with automated pipelines

**Promising direction:** Self-supervised learning may capture spurious correlation structure in learned representations because:
- SSL trained on augmentations might preserve spurious feature clusters
- Contrastive objectives don't explicitly target class labels, so background/texture correlations may emerge in embedding space
- Frozen embeddings enable single-pass minority discovery (not iterative optimization)

**Why this avoids past failures:**
- No isotropic regularization (SAM, L2)
- No raw gradient magnitude assumptions
- No human annotation required
- Scriptable within Phase 4 constraints
- Clear MUST_WORK criteria: cluster precision ≥80%, WGA improvement ≥5pp

### Techniques Used

ROUTE_TO_0 Failure Analysis (structured synthesis from 11 Serena Memory records)

### Areas for Further Exploration

- Alternative SSL architectures (DINO, SwAV, BarlowTwins)
- Clustering algorithms beyond k-means (HDBSCAN, spectral)
- Hybrid approaches: SSL embeddings + loss signals
- Active learning for minimal group label feedback
- Extension to language models (spurious word correlations)

---

## Next Steps

Proceed to Phase 1 - Targeted Research
- Search for SSL-based spurious correlation detection papers
- Identify minority discovery clustering methods
- Find bias mitigation with contrastive learning
- Validate novelty and feasibility before Phase 2A hypothesis generation

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
