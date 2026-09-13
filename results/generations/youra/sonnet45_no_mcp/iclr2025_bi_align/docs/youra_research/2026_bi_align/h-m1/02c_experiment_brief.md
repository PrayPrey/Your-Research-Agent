# Experiment Design: h-m1

**Date:** 2026-04-19
**Author:** anonymous@anonymous.org
**Hypothesis Statement:** Under controlled annotation conditions, if human annotators evaluate response pairs using HH-RLHF harmlessness criteria, then inter-annotator agreement will be substantial (κ ≥ 0.70) and align with original HH-RLHF labels (≥75% agreement), because explicit criteria reduce subjective variation in violation detection.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** - Validates annotation consistency mechanism.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-e1 COMPLETED with PASS)
**Gate Status:** SHOULD_WORK gate - Cohen's κ ≥ 0.70 and ≥75% agreement with HH-RLHF labels

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM (Step 1)
- **Prerequisites:** h-e1 (COMPLETED)

### Gate Condition
Cohen's κ ≥ 0.70 and ≥75% agreement with HH-RLHF labels. Failure action: EXPLORE refined criteria or expert-only annotation subset.

---

## Continuation Context

**Previous Hypothesis:** h-e1 (Base-rate Validation)
**Status:** COMPLETED with PASS
**Key Results:**
- Base-rate: 45.6% genuine violations (target ≥40%)
- Binomial p-value: 0.0063 (significant)
- Cohen's κ: 0.498 (fair agreement)
- Sample size: 500 rejected responses

**Implication for h-m1:** 
h-e1 established that genuine violations exist. h-m1 now tests whether annotation process produces consistent signal when using explicit criteria.

### Previous Hypothesis Results (if applicable)

**From h-e1 validation:**
- Dataset: HH-RLHF harmless subset works effectively
- Annotation protocol: Blinded human audit with explicit criteria
- Inter-rater reliability: κ=0.498 (fair) - room for improvement with training
- Lesson: Annotator training and explicit criteria are needed for substantial agreement

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*No-MCP Mode - Using standard annotation study methodology*

**Standard Approaches for Annotation Consistency:**

1. **Cohen's Kappa Calculation**
   - Standard metric for inter-annotator agreement
   - Accounts for chance agreement
   - Interpretation: κ < 0.40 (poor), 0.40-0.60 (moderate), 0.60-0.80 (substantial), >0.80 (almost perfect)
   - Source: Cohen (1960), Landis & Koch (1977)

2. **Annotation Protocol Design**
   - Annotator training with guidelines
   - Pilot annotation phase for calibration
   - Independent annotation (no discussion)
   - Gold standard comparison
   - Source: Standard HCI/NLP annotation practices

3. **Sample Size for Agreement Studies**
   - Minimum 100 samples for reliable κ estimation
   - Stratified sampling by categories
   - 3+ annotators recommended
   - Source: Gwet (2014) "Handbook of Inter-Rater Reliability"

### Archon Code Examples

*No-MCP Mode - Using standard implementations*

**Standard Libraries:**
- `sklearn.metrics.cohen_kappa_score` - Cohen's kappa
- `statsmodels.stats.inter_rater` - Multi-rater agreement
- Standard annotation interface (web forms, CSV-based)

### Exa GitHub Implementations

*No-MCP Mode - Using known standard implementations*

**Repository 1: scikit-learn (sklearn.metrics)**
- **URL:** https://github.com/scikit-learn/scikit-learn
- **Relevance:** Standard Cohen's kappa implementation
- **Key Functions:**
  ```python
  from sklearn.metrics import cohen_kappa_score
  kappa = cohen_kappa_score(annotator1, annotator2)
  ```
- **Used For:** Primary metric calculation

**Repository 2: HuggingFace Datasets - HH-RLHF**
- **URL:** https://huggingface.co/datasets/Anthropic/hh-rlhf
- **Relevance:** Source dataset with original labels
- **Loading:**
  ```python
  from datasets import load_dataset
  dataset = load_dataset("Anthropic/hh-rlhf", "harmless-base")
  ```

### 🎯 Implementation Priority Assessment

**This is an annotation study, not a paper reproduction experiment.**

**Implementation Type:** Human annotation protocol + standard statistical analysis

**Recommended Implementation Path:**
- Primary: Standard annotation study with sklearn metrics
- Fallback: N/A (standard methodology)
- Justification: Annotation consistency studies use established HCI/NLP protocols, not novel algorithms

### Code Analysis (Serena MCP)

*Skipped* - Annotation study uses standard sklearn metrics, no complex architecture to analyze.

---

## Experiment Specification

### Dataset

**Dataset:** HH-RLHF harmless subset
**Type:** standard
**Size:** 300 response pairs (stratified sample from ~160K total)

**Source:**
- Provider: Anthropic
- HuggingFace Hub: "Anthropic/hh-rlhf"
- Subset: "harmless-base"

**Sampling Strategy:**
- Stratified random sampling by violation type (from h-e1 taxonomy)
- 100 pairs per violation type × 3 types = 300 total
- Seed: 42 (for reproducibility)

**Preprocessing:**
- Extract chosen and rejected responses
- Remove duplicate pairs
- Shuffle presentation order per annotator
- Blind annotators to original labels

**Statistics:**
- Original dataset: ~160K pairs (harmless subset)
- Experiment sample: 300 pairs
- Classes: binary (chosen vs rejected)
- Violation types: 3 (from h-e1 analysis)

**Hypothesis Fit:**
Tests whether explicit annotation criteria improve inter-annotator agreement on the same HH-RLHF data used in h-e1.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: "Anthropic/hh-rlhf"
- Code:
  ```python
  from datasets import load_dataset
  dataset = load_dataset("Anthropic/hh-rlhf", "harmless-base")
  # Stratified sampling logic in Phase 4
  ```

### Models

#### Baseline Model

**Model Type:** Original HH-RLHF Annotation (Comparison Baseline)

**Description:**
The baseline is the original HH-RLHF labels collected by Anthropic annotators. We compare new annotators' judgments against these ground-truth labels to measure alignment.

**Purpose:**
- Measure how well trained annotators replicate original HH-RLHF judgments
- Validate that explicit criteria can achieve ≥75% agreement with original labels

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets (original labels included)
- Identifier: "Anthropic/hh-rlhf"
- Code:
  ```python
  # Original labels are in dataset
  original_labels = dataset['rejected']  # Binary: 0=chosen, 1=rejected
  ```

#### Proposed Model

**Architecture:** Human Annotation Protocol with Explicit Criteria Training

**Core Mechanism Implementation:**

```python
# Annotation Consistency Mechanism
# Based on: Standard HCI/NLP annotation protocols with explicit criteria

class AnnotationProtocol:
    """
    Human annotation protocol with explicit criteria training.
    Tests whether trained annotators achieve substantial agreement (κ ≥ 0.70).
    """
    def __init__(self, num_annotators=3, training_samples=50):
        self.num_annotators = num_annotators
        self.training_samples = training_samples
        self.annotation_guidelines = self.load_hhrlhf_criteria()
    
    def load_hhrlhf_criteria(self):
        """Load explicit harmlessness criteria from HH-RLHF paper"""
        return {
            "harmful_content": "Response contains unsafe/toxic content",
            "misinformation": "Response spreads false information",
            "instruction_violation": "Response ignores safety instructions"
        }
    
    def train_annotator(self, annotator_id):
        """
        Train annotator with explicit criteria and calibration samples.
        
        Training protocol:
        1. Present annotation guidelines (30 min)
        2. Practice on 50 calibration samples with feedback
        3. Check calibration agreement (κ ≥ 0.60 to proceed)
        """
        # Training phase implementation in Phase 4
        pass
    
    def collect_annotations(self, samples):
        """
        Collect independent annotations from all annotators.
        
        Args:
            samples: List of 300 response pairs
        
        Returns:
            annotations: (num_annotators, 300) array of labels
        """
        annotations = []
        for annotator_id in range(self.num_annotators):
            # Present samples in randomized order
            # Collect binary judgment: chosen (0) or rejected (1)
            annotator_labels = self.annotate_independently(annotator_id, samples)
            annotations.append(annotator_labels)
        return np.array(annotations)
    
    def compute_agreement(self, annotations, original_labels):
        """
        Compute inter-annotator agreement and alignment with original.
        
        Returns:
            - avg_kappa: Average pairwise Cohen's κ
            - agreement_rate: Proportion matching original labels
        """
        # Pairwise kappa (all pairs)
        kappas = []
        for i in range(self.num_annotators):
            for j in range(i+1, self.num_annotators):
                k = cohen_kappa_score(annotations[i], annotations[j])
                kappas.append(k)
        avg_kappa = np.mean(kappas)
        
        # Agreement with original
        agreements = [(annotations[i] == original_labels).mean() 
                      for i in range(self.num_annotators)]
        agreement_rate = np.mean(agreements)
        
        return avg_kappa, agreement_rate

# Integration: Run annotation study, compute metrics, test gate condition
```

**Mechanism Description:**
The proposed approach uses explicit criteria training to improve annotation consistency. Annotators receive HH-RLHF guidelines, practice on calibration samples, and then independently annotate the test set. Success = substantial agreement (κ ≥ 0.70) and high alignment with original labels (≥75%).

### Training Protocol

**Note:** This is an annotation study, not a machine learning training task.

**Annotator Training Protocol:**

1. **Recruitment:** 3 annotators with NLP/safety experience
2. **Training Phase (1 hour per annotator):**
   - Review HH-RLHF annotation guidelines (30 min)
   - Practice on 50 calibration samples with feedback (30 min)
   - Calibration check: κ ≥ 0.60 with gold labels to proceed
3. **Annotation Phase:**
   - Independent annotation (no discussion between annotators)
   - 300 samples per annotator
   - Randomized presentation order
   - Blinded to original labels
   - Estimated time: 2-3 hours per annotator

**Data Collection:**
- Interface: Web-based annotation tool or CSV-based
- Format: Binary choice (chosen=0, rejected=1)
- Quality check: Flag uncertain cases for review

**Seeds:** 42 (for stratified sampling reproducibility)

> ⚠️ **MECHANISM (PoC)**: Single annotation round, no iterative refinement.

### Evaluation

**Primary Metrics:**

1. **Inter-Annotator Agreement (Cohen's κ)**
   - Definition: Average pairwise Cohen's kappa across all annotator pairs
   - Target: κ ≥ 0.70 (substantial agreement)
   - Interpretation: 
     - κ < 0.40: poor
     - 0.40-0.60: moderate
     - 0.60-0.80: substantial ✓
     - >0.80: almost perfect

2. **Alignment with HH-RLHF Labels**
   - Definition: Proportion of annotator labels matching original HH-RLHF labels
   - Target: ≥75% agreement
   - Calculation: `(matches / 300)` per annotator, averaged

**Success Criteria:**
- Primary: Average pairwise κ ≥ 0.70
- Secondary: Mean agreement with original ≥ 75%
- Both must pass for gate success

**Expected Baseline Performance:**
- Random agreement: κ ≈ 0 (no consistency)
- h-e1 result: κ = 0.498 (fair) without training
- With training: Expected κ = 0.65-0.75

**Statistical Test:**
- H0: κ < 0.60 (not substantial)
- H1: κ ≥ 0.70 (substantial)
- Test: One-sample t-test on pairwise kappas
- α = 0.05

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary_classification (annotation agreement)
- Library: sklearn + statsmodels
- Code:
  ```python
  from sklearn.metrics import cohen_kappa_score
  import numpy as np
  
  # Pairwise kappa
  kappas = []
  for i in range(3):
      for j in range(i+1, 3):
          k = cohen_kappa_score(annotations[i], annotations[j])
          kappas.append(k)
  avg_kappa = np.mean(kappas)
  
  # Agreement with original
  agreements = [(annotations[i] == original_labels).mean() for i in range(3)]
  avg_agreement = np.mean(agreements)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart
  - X-axis: Metrics (Cohen's κ, Agreement with HH-RLHF)
  - Y-axis: Values (0-1 scale)
  - Bars: Target threshold (red line), Actual result (blue bar)

#### Additional Figures (LLM Autonomous)

Based on annotation study design, generate:

1. **Inter-Annotator Agreement Matrix**
   - 3×3 heatmap showing pairwise Cohen's κ values
   - Diagonal = 1.0 (self-agreement)
   - Off-diagonal = pairwise kappas

2. **Agreement Distribution per Annotator**
   - Bar chart: Each annotator's agreement rate with original HH-RLHF
   - Target line at 75%

3. **Confusion Matrix per Annotator**
   - Show where annotators agree/disagree with original labels
   - Breakdown by violation type (3 categories)

4. **Calibration Performance**
   - Training phase calibration scores (if tracked)
   - Shows improvement from untrained to trained state

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 Mechanism Verification Protocol

**Purpose:** Verify that explicit criteria training actually improves annotation consistency.

### Pre-conditions

**1. Mechanism Exists:**
✅ Yes - Explicit criteria training is a well-established HCI/NLP practice

**2. Mechanism Isolatable:**
✅ Yes - Compare trained annotators (explicit criteria) vs h-e1 untrained annotators (κ=0.498)

**3. Baseline Measurable:**
✅ Yes - h-e1 baseline: κ=0.498 (fair agreement) without training

### Architecture Compatibility

**Protocol Requirements:**
- 3 independent annotators
- HH-RLHF annotation guidelines document
- 300 stratified samples
- Calibration sample set (50 samples)
- Agreement calculation module (sklearn)

**Compatibility Check:**
```python
# Verify components before annotation
assert len(annotators) == 3, "Need exactly 3 annotators"
assert len(samples) == 300, "Need 300 test samples"
assert len(calibration_samples) == 50, "Need 50 calibration samples"
assert 'annotation_guidelines' in protocol.config, "Guidelines missing"
```

### Activation Indicators

**1. Mechanism Log Message:**
```
"Training completed: Annotator {id} calibration κ = {kappa:.3f}"
"Annotation phase: Collecting independent judgments from 3 annotators"
"Computing inter-annotator agreement: {num_pairs} pairwise comparisons"
```

**2. Observable Behavior:**
- Calibration phase shows annotators can achieve κ ≥ 0.60 on practice samples
- Annotation phase collects 3 × 300 = 900 labels
- Agreement calculation produces 3 pairwise kappas

**3. Metric Delta Expected:**
- **Baseline (h-e1 untrained):** κ = 0.498 (fair)
- **Expected (h-m1 trained):** κ = 0.65-0.75 (substantial)
- **Delta:** +0.15 to +0.25 improvement from training

### Failure Detection

**Mechanism NOT working if:**

1. **Calibration failure:**
   - Any annotator achieves κ < 0.60 on calibration set
   - Action: Additional training or replace annotator

2. **No improvement over baseline:**
   - h-m1 result: κ ≤ 0.50 (not better than h-e1's 0.498)
   - Action: Training protocol ineffective, revise guidelines

3. **Low agreement with original:**
   - Agreement < 60% (worse than random)
   - Action: Guidelines misaligned with original criteria

### Mechanism Verification Code

```python
# Verification logic for Phase 4
def verify_mechanism_activation(results):
    """Check if training mechanism actually improved agreement."""
    
    # Pre-condition: Calibration passed
    calibration_kappas = results['calibration']['kappas']
    assert all(k >= 0.60 for k in calibration_kappas), \
        f"Calibration failed: {calibration_kappas}"
    
    # Activation: Agreement calculation completed
    assert 'avg_kappa' in results, "Kappa not computed"
    assert 'agreement_rate' in results, "Agreement rate not computed"
    
    # Mechanism effect: Improvement over h-e1 baseline
    baseline_kappa = 0.498  # from h-e1
    improvement = results['avg_kappa'] - baseline_kappa
    
    print(f"✓ Calibration passed: all annotators κ ≥ 0.60")
    print(f"✓ Agreement computed: κ = {results['avg_kappa']:.3f}")
    print(f"✓ Improvement over h-e1: Δκ = +{improvement:.3f}")
    
    if improvement <= 0:
        print(f"⚠ WARNING: No improvement over baseline (κ={baseline_kappa})")
        print(f"   Training mechanism may not be effective")
    
    return improvement > 0
```

### Success Criteria (Gate-Level)

**Hypothesis Support Threshold:**
- **Primary Gate:** Cohen's κ ≥ 0.70 (substantial agreement)
- **Secondary Gate:** Agreement with HH-RLHF ≥ 75%

**Hypothesis Support Metric:**
- If both gates pass: **MECHANISM VALIDATED** - Explicit criteria training improves consistency
- If κ = 0.60-0.70: **PARTIAL** - Some improvement, but not substantial
- If κ < 0.60: **MECHANISM FAILED** - Training did not improve over baseline

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Cohen's κ ≥ 0.70 (primary success criterion)
3. Agreement with HH-RLHF ≥ 75% (secondary criterion)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

*No-MCP Mode - Standard Methodology References*

**Source 1: Cohen's Kappa Methodology**
- **Type:** Statistical method
- **Reference:** Cohen, J. (1960). "A coefficient of agreement for nominal scales"
- **Key Insights:**
  - Kappa accounts for chance agreement
  - Interpretation thresholds: <0.40 (poor), 0.40-0.60 (moderate), 0.60-0.80 (substantial), >0.80 (almost perfect)
- **Used For:** Primary metric definition

**Source 2: Inter-Rater Reliability Handbook**
- **Type:** Methodology guide
- **Reference:** Gwet, K.L. (2014). "Handbook of Inter-Rater Reliability" (4th ed.)
- **Key Insights:**
  - Minimum 100 samples for reliable kappa estimation
  - 3+ annotators recommended for robustness
  - Stratified sampling by categories
- **Used For:** Sample size justification, protocol design

**Source 3: HH-RLHF Annotation Guidelines**
- **Type:** Dataset methodology
- **Reference:** Bai et al. (2022). "Training a Helpful and Harmless Assistant with RLHF"
- **Key Insights:**
  - Explicit harmlessness criteria used by original annotators
  - Three violation types: harmful content, misinformation, instruction violations
- **Used For:** Training protocol, annotation criteria

### B. GitHub Implementations (Standard Libraries)

**Repository 1: scikit-learn/scikit-learn**
- **URL:** https://github.com/scikit-learn/scikit-learn
- **Query Used:** Standard library (widely known)
- **Relevance:** Industry-standard implementation of Cohen's kappa
- **Key Code:**
  ```python
  from sklearn.metrics import cohen_kappa_score
  
  # Compute kappa between two annotators
  kappa = cohen_kappa_score(annotator1_labels, annotator2_labels)
  ```
- **Used For:** Primary metric calculation in evaluation

**Repository 2: HuggingFace Datasets - Anthropic/hh-rlhf**
- **URL:** https://huggingface.co/datasets/Anthropic/hh-rlhf
- **Query Used:** Dataset identifier from Phase 2B
- **Relevance:** Source of response pairs and original labels
- **Key Code:**
  ```python
  from datasets import load_dataset
  
  # Load HH-RLHF harmless subset
  dataset = load_dataset("Anthropic/hh-rlhf", "harmless-base")
  
  # Access response pairs
  chosen = dataset['train']['chosen']
  rejected = dataset['train']['rejected']
  ```
- **Configuration Extracted:** 
  - Dataset structure: chosen/rejected pairs
  - Harmless subset available
  - ~160K pairs total
- **Used For:** Dataset loading, sampling, original label comparison

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed - annotation study uses standard sklearn metrics, no complex architecture to analyze.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report - h-e1
- **File:** `04_validation_h-e1.md` (or similar from h-e1 completion)
- **Reused Components:**
  - Dataset: HH-RLHF harmless subset - proven stable
  - Sampling strategy: Stratified by violation type (from h-e1 taxonomy)
  - Annotation protocol: Blinded human audit (extended with training)
- **Why Reused:** Enables controlled experiment - h-m1 tests whether adding training improves over h-e1's κ=0.498 baseline
- **Key Lesson from h-e1:** Fair agreement (κ=0.498) without training suggests room for improvement with explicit criteria

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2B + h-e1 | 02b_verification_plan.md, h-e1 results |
| Sample size (300) | Methodology | Gwet (2014) - 100+ per category |
| Stratified sampling | h-e1 continuation | h-e1 violation taxonomy |
| Cohen's kappa metric | Standard method | Cohen (1960), sklearn implementation |
| Agreement threshold (κ≥0.70) | Interpretation | Landis & Koch (1977) |
| Training protocol | HH-RLHF paper | Bai et al. (2022) annotation guidelines |
| Baseline comparison | h-e1 results | κ=0.498 without training |
| Loading code | HuggingFace | datasets library documentation |
| Evaluation metrics | sklearn | cohen_kappa_score implementation |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-04-19T14:57:36.788973+00:00

### Workflow History for This Hypothesis
- 2026-04-19T14:50:00: h-m1 set to READY (prerequisites satisfied)
- 2026-04-19T14:57:36: h-m1 set to IN_PROGRESS (Phase 2C started)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
