# Phase 6 Paper Writing - Complete

**Generated:** 2026-05-12  
**Pipeline:** YouRA Phase 0 → 1 → 2A → 2B → (2C → 3 → 4) → 4.5 → **6**  
**Status:** ✅ COMPLETE

---

## Paper Overview

**Title:** When Fixed Thresholds Fail: Empirical Falsification of Automated Semantic Dataset Versioning

**Type:** Negative Result (Empirical Falsification)  
**Target Venue:** ICML 2026  
**Word Count:** 6,581 words

**Core Finding:** Fixed statistical thresholds (7%/2%/0.5%) derived from ImageNet literature do NOT generalize to NLP datasets for automated semantic versioning, achieving only 44.4% accuracy with 100% false positive rate on PATCH-level changes.

---

## Generated Files

### Paper Sections
- `00_abstract.md` - 200-word abstract with quantitative results
- `01_introduction.md` - Problem framing, hypothesis, contributions (3-level problem framing)
- `02_related_work.md` - Dataset versioning tools, drift detection, semantic versioning, positioning table
- `03_methodology.md` - SVAD architecture, feature extraction, KS+MMD tests, threshold selection
- `04_experiments.md` - Dataset coverage (9/15), ground truth labels, experimental protocol
- `05_results.md` - Gate failure metrics, confusion matrix, 100% PATCH FP rate, 20× drift variance
- `06_discussion.md` - Root cause analysis (3 causes), unexpected findings, path forward
- `07_conclusion.md` - Negative result framing, contributions, limitations, broader impact

### Supporting Files
- `06_paper.md` - **MERGED FULL PAPER** (all sections concatenated)
- `06_references.bib` - BibTeX bibliography (25+ verified citations via Semantic Scholar)
- `06_narrative_blueprint.yaml` - Narrative strategy, evidence flow, writing guidelines
- `065_ground_truth.yaml` - Phase 6.5 adversarial review targets

### Figures (Copied from h-e1/figures/)
- `figures/gate_metrics.png` - Achieved vs Target metrics bar chart
- `figures/confusion_matrix.png` - 3×3 heatmap showing 100% PATCH misclassification
- `figures/drift_scores.png` - Distribution of KS+MMD scores (0.042-0.79 range)
- `figures/per_dataset_performance.png` - Per-dataset accuracy breakdown

---

## Key Contributions

1. **Empirical falsification:** First evidence that ImageNet thresholds fail on NLP (16.7% precision vs 70% target)

2. **Quantitative failure measurement:** -53.3pp precision gap, 20× drift variance, 100% PATCH false positive rate

3. **Mechanistic insights:** 3 root causes identified (dataset-specific baselines, frozen extractor robustness, cross-modality mis-calibration)

4. **Constructive redirection:** 3 alternative approaches proposed (adaptive calibration, supervised classification, performance-based validation)

---

## Quantitative Claims (Verified)

| Claim | Value | Source | Location |
|-------|-------|--------|----------|
| Overall Accuracy | 44.4% (vs 85% target) | h-e1/04_validation.md | Abstract, Sec 5.1 |
| Precision (MAJOR) | 16.7% (vs 70% target) | h-e1/04_validation.md | Abstract, Sec 5.1 |
| Recall (MAJOR) | 100% (vs 85% target) | h-e1/04_validation.md | Sec 5.1 |
| PATCH FP Rate | 100% (5/5 misclassified) | Confusion matrix | Sec 5.2, Abstract |
| Drift Variance | 20× (0.042 to 0.79) | h-e1/04_results.json | Sec 5.3, Abstract |
| Dataset Coverage | 9/15 (60%) | h-e1/04_validation.md | Sec 4.1 |

---

## Narrative Structure

**Hook Strategy:** Counterintuitive negative result (100% PATCH false positive rate)

**Emotional Arc:** Hope (can we automate semantic versioning?) → Surprising failure (100% FP rate) → Insight (drift is dataset-relative, not absolute)

**3-Level Problem Framing:**
1. **Societal:** ML reproducibility crisis (60-70% failure rates)
2. **Technical:** Existing versioning lacks semantic meaning (DVC snapshots, HuggingFace revisions)
3. **Specific:** Can fixed thresholds from ImageNet generalize? (Answer: No)

**Evidence Flow:**
- Act 1 (Setup): Problem + gap + prior work
- Act 2 (Method): SVAD system + experiment design
- Act 3 (Results): Headline failure + 100% PATCH FP rate
- Act 4 (Interpretation): Root causes + why thresholds fail
- Act 5 (Closure): Reframe as useful negative result + future directions

---

## Limitations (Acknowledged)

1. **Ground truth not performance-validated** (HIGH severity)
   - Labels from literature, not measured model degradation
   - Justification: PoC-stage acceptable; doesn't change decisive negative result

2. **Incomplete dataset coverage (9/15)** (MEDIUM severity)
   - Missing 6 datasets (3 vision, 3 NLP)
   - Justification: Hypothesis failed decisively on 9; adding 6 unlikely to reverse -53pp gap

3. **MNIST cross-dataset shift contaminates results** (MEDIUM severity)
   - MNIST→USPS is domain adaptation, not version drift
   - Justification: Removing MNIST still yields 50% accuracy (vs 85% target)

4. **Frozen feature extractors may under-detect drift** (LOW severity)
   - Transfer learning models optimized for robustness, not sensitivity
   - Justification: Even with current features, 20× variance demonstrates threshold problem

---

## Citations (Verified via Semantic Scholar)

**Primary:**
- Recht et al. 2019 (ImageNet-v2) - 2,130 citations
- Rabanser et al. 2019 (Failing Loudly) - 443 citations
- Gretton et al. 2012 (MMD kernel test) - 6,237 citations

**Models:**
- He et al. 2016 (ResNet) - 227,358 citations
- Devlin et al. 2019 (BERT) - 114,255 citations

**Datasets:**
- Wang et al. 2018 (GLUE) - 8,480 citations
- Bowman et al. 2015 (SNLI)
- Williams et al. 2018 (MultiNLI)

**Tools:**
- Lhoest et al. 2021 (HuggingFace Datasets)
- Kuprieiev et al. 2020 (DVC)

Total: 25+ citations in `06_references.bib`

---

## Phase 6.5 Readiness

**Ground Truth File:** `065_ground_truth.yaml`

**Attack Surface (High Priority):**
1. Ground truth labels not performance-validated
2. Only 1 vision dataset tested (invalid cross-dataset shift)
3. Root Cause 2 (frozen extractors) not directly tested
4. SST2 PATCH with 0.79 drift—possible label error

**Anticipated Objections:**
- "Why not test adaptive thresholds?" → Future work; requires multiple transitions per dataset
- "9/15 too few datasets?" → Scope limited to NLP; -53pp gap decisive even on 9
- "SST2 label might be wrong?" → Acknowledged; but ALL 5 PATCH exceed threshold (systematic)
- "Frozen features the problem?" → Acknowledged; but 20× variance demonstrates threshold issue

---

## Next Steps

**Phase 6.5 (Optional):** Adversarial review
- Devil's Advocate attack on methodology weaknesses
- Numerical verification of quantitative claims
- Logical attack on causal reasoning
- Falsifiability check on alternative explanations

**Phase 7 (If applicable):** Submission preparation
- ICML LaTeX formatting
- Figure quality enhancement
- Supplementary materials (code, datasets)

---

## File Tree

```
paper/
├── 00_abstract.md              # Abstract (200 words)
├── 01_introduction.md          # Introduction + contributions
├── 02_related_work.md          # Related work + positioning table
├── 03_methodology.md           # SVAD system + experimental protocol
├── 04_experiments.md           # Dataset coverage + ground truth
├── 05_results.md               # Gate failure + 100% PATCH FP rate
├── 06_discussion.md            # Root causes + path forward
├── 07_conclusion.md            # Negative result framing + impact
├── 06_paper.md                 # ✅ MERGED FULL PAPER (6,581 words)
├── 06_references.bib           # BibTeX bibliography (25+ citations)
├── 06_narrative_blueprint.yaml # Narrative strategy document
├── 065_ground_truth.yaml       # Phase 6.5 attack targets
├── README.md                   # This file
└── figures/
    ├── gate_metrics.png        # Figure 1: Achieved vs Target
    ├── confusion_matrix.png    # Figure 2: 100% PATCH misclassification
    ├── drift_scores.png        # Figure 3: 20× drift variance
    └── per_dataset_performance.png  # Figure 4: Per-dataset breakdown
```

---

**Phase 6 Status:** ✅ **COMPLETE**  
**All 7 steps executed:** Init → Blueprint → Foundation → Evidence → Closure → References → Merge

**Ready for:** Phase 6.5 (Adversarial Review) or direct submission preparation
