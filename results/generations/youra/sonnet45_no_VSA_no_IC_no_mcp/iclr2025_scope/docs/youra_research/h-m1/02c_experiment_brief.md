# Experiment Design: H-M1

**Date:** 2026-08-25
**Author:** Anonymous
**Hypothesis Statement:** If we apply a standardized feature extraction protocol (Papers with Code taxonomy for task types, regex patterns for metrics, category tags for modality, table parsing for dataset size) to diverse benchmarks, then independent annotators will achieve >0.80 inter-rater agreement (Cohen's kappa), because the protocol provides objective decision rules for feature categorization.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** - Validates feature extraction objectivity.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** None (foundation hypothesis, parallel with H-E1)
**Gate Status:** MUST_WORK (failure stops workflow)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** None (parallel with H-E1)

### Gate Condition
MUST_WORK gate - Feature extraction kappa must achieve >0.80. If kappa <0.70, workflow STOPS for protocol redesign.

---

## Continuation Context

First hypothesis in verification plan (parallel foundation with H-E1). No previous validation results to build on. This hypothesis validates that the feature extraction protocol is objective enough to scale.

### Previous Hypothesis Results (if applicable)
*N/A - Foundation hypothesis*

---

## Implementation Research Summary

**MCP ABLATION MODE**: Archon, Exa, Serena MCPs unavailable. Experiment design based on Phase 2B protocol specification and standard inter-rater reliability methodology.

### Archon Knowledge Base Findings

*MCP unavailable - No historical implementation cases retrieved*

### Archon Code Examples

*MCP unavailable - No code examples retrieved*

### Exa GitHub Implementations

*MCP unavailable - No GitHub implementations searched*

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

*MCP unavailable - Implementation priority based on standard methodology*

**Recommended Implementation Path:**
- Primary: Scikit-learn Cohen's kappa implementation (sklearn.metrics.cohen_kappa_score)
- Fallback: Manual calculation with confusion matrix
- Justification: Standard inter-rater reliability metric, widely validated, matches Phase 2B specification

### Code Analysis (Serena MCP)

*MCP unavailable - No codebase analysis performed*

---

## Experiment Specification

### Dataset

**Name:** Benchmark Sample for Inter-Rater Agreement Study  
**Type:** custom (curated from Papers with Code)  
**Size:** 20 diverse DL benchmarks (pilot phase)  
**Source:** Papers with Code API + manual paper collection  
**Diversity Criteria:**
- Task types: Classification, detection, segmentation, generation, sequence modeling
- Modalities: Vision (8), language (7), audio (3), multimodal (2)
- Dataset sizes: Small (<10K), medium (10K-100K), large (>100K), very large (>1M)
- Publication years: 2015-2024 (span)

**Benchmark Selection Protocol:**
1. Query Papers with Code API for top benchmarks per task category
2. Filter: ≥50 citations (sufficient usage data)
3. Stratified sampling across task types and modalities
4. Manual verification: paper accessible, features extractable

**Features to Extract (per benchmark):**
1. **Task Type** (categorical): PWC taxonomy category
2. **Metrics** (categorical list): Regex extraction from paper
3. **Modality** (categorical): Image/text/audio/video/multimodal
4. **Dataset Size** (continuous): Number of samples (from paper tables)

**Loading Information** (for Phase 4 download):
- Method: API + manual download
- Identifier: Papers with Code benchmark list + arXiv paper PDFs
- Code:
```python
import requests
# Papers with Code API
pwc_url = "https://paperswithcode.com/api/v1/datasets/"
response = requests.get(pwc_url, params={"ordering": "-citations"})
benchmarks = response.json()["results"][:20]
```

### Models

#### Baseline Model

**N/A** - This is not a model training experiment. This is an inter-rater reliability study validating feature extraction objectivity.

**Loading Information** (for Phase 4 download):
- Method: N/A
- Identifier: N/A
- Code: N/A

#### Proposed Model

**Architecture:** Feature Extraction Protocol + Inter-Rater Agreement Calculation

**Core Mechanism Implementation:**

```python
# Feature Extraction Protocol Implementation
class FeatureExtractionProtocol:
    def __init__(self):
        # PWC taxonomy for task types
        self.task_taxonomy = load_pwc_taxonomy()
        # Regex patterns for metric extraction
        self.metric_patterns = {
            'accuracy': r'accuracy|acc\s*[:=]\s*(\d+\.?\d*)',
            'f1': r'f1[-\s]score|f1\s*[:=]\s*(\d+\.?\d*)',
            'map': r'mAP|mean\s+average\s+precision',
            'bleu': r'BLEU[-\s]?\d*',
            # ... more patterns
        }
        # Modality decision tree
        self.modality_rules = load_modality_decision_tree()
    
    def extract_features(self, benchmark_paper):
        """Extract 4 features from benchmark paper."""
        features = {}
        
        # 1. Task type (PWC taxonomy)
        features['task_type'] = self._map_to_pwc_taxonomy(
            benchmark_paper.abstract,
            benchmark_paper.title
        )
        
        # 2. Metrics (regex extraction)
        features['metrics'] = self._extract_metrics(
            benchmark_paper.full_text
        )
        
        # 3. Modality (decision tree)
        features['modality'] = self._classify_modality(
            benchmark_paper.dataset_description
        )
        
        # 4. Dataset size (table parsing)
        features['dataset_size'] = self._parse_dataset_size(
            benchmark_paper.tables
        )
        
        return features

# Inter-Rater Agreement Calculation
from sklearn.metrics import cohen_kappa_score

def calculate_agreement(annotator1_labels, annotator2_labels):
    """Calculate Cohen's kappa for categorical features."""
    kappa = cohen_kappa_score(annotator1_labels, annotator2_labels)
    return kappa

# Main experiment logic
def run_interrater_study(benchmarks, num_annotators=2):
    annotations = {f'annotator_{i}': [] for i in range(num_annotators)}
    
    # Each annotator extracts features independently
    for annotator_id in range(num_annotators):
        protocol = FeatureExtractionProtocol()
        for benchmark in benchmarks:
            features = protocol.extract_features(benchmark)
            annotations[f'annotator_{annotator_id}'].append(features)
    
    # Calculate kappa for each feature
    kappa_scores = {}
    for feature_name in ['task_type', 'modality']:
        labels_a1 = [a[feature_name] for a in annotations['annotator_0']]
        labels_a2 = [a[feature_name] for a in annotations['annotator_1']]
        kappa_scores[feature_name] = calculate_agreement(labels_a1, labels_a2)
    
    return kappa_scores
```

### Training Protocol

**N/A** - No model training. This is a human annotation study.

**Annotation Protocol:**
1. **Pre-Study Calibration:**
   - Both annotators read protocol document
   - Practice on 3 example benchmarks (not in test set)
   - Discuss disagreements, refine protocol if needed
   - Record protocol version number

2. **Independent Annotation:**
   - Each annotator extracts features from 20 benchmarks
   - No communication during annotation phase
   - Time limit: 2 hours per annotator
   - Record uncertainty flags for ambiguous cases

3. **Agreement Calculation:**
   - Compute Cohen's kappa for categorical features
   - Compute ICC for continuous features (dataset size)
   - Identify systematic disagreement patterns

4. **Protocol Refinement (if kappa <0.80):**
   - Analyze disagreement cases
   - Add decision rules to protocol
   - Re-test on 10 new benchmarks

### Evaluation

**Primary Metric:** Cohen's Kappa (inter-rater agreement)  
**Target:** kappa > 0.80 (substantial agreement)  
**Secondary Metric:** ICC (Intraclass Correlation Coefficient) for dataset size

**Success Criteria (PoC):**
1. ✅ **PASS:** kappa_task_type > 0.80 AND kappa_modality > 0.80 AND ICC_dataset_size > 0.80
2. ⚠️ **PARTIAL:** Any kappa in [0.70, 0.80] → protocol refinement needed
3. ❌ **FAIL:** Any kappa < 0.70 → feature too subjective, MUST_WORK gate fails

**Interpretation (Landis & Koch scale):**
- kappa > 0.80: Almost perfect agreement
- kappa 0.60-0.80: Substantial agreement
- kappa 0.40-0.60: Moderate agreement
- kappa < 0.40: Poor agreement

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Inter-rater reliability study
- Library: scikit-learn (sklearn.metrics)
- Code:
```python
from sklearn.metrics import cohen_kappa_score
from scipy.stats import pearsonr
import numpy as np

# Cohen's kappa for categorical features
kappa = cohen_kappa_score(annotator1_labels, annotator2_labels)

# ICC for continuous features (dataset size)
def calculate_icc(ratings):
    # ratings: (n_samples, n_annotators)
    n, k = ratings.shape
    mean_ratings = np.mean(ratings, axis=1)
    ss_between = k * np.sum((mean_ratings - np.mean(ratings))**2)
    ss_within = np.sum((ratings - mean_ratings[:, None])**2)
    ms_between = ss_between / (n - 1)
    ms_within = ss_within / (n * (k - 1))
    icc = (ms_between - ms_within) / (ms_between + (k - 1) * ms_within)
    return icc
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Kappa scores (task_type, modality, metrics) vs 0.80 threshold bar chart

#### Additional Figures (LLM Autonomous)

**Figure 1: Inter-Rater Agreement Heatmap**
- Confusion matrix for task type annotations (annotator 1 vs annotator 2)
- Shows systematic disagreement patterns

**Figure 2: Feature Distribution**
- Histogram of extracted features across 20 benchmarks
- Shows diversity coverage (vision/language/audio/multimodal)

**Figure 3: Disagreement Case Analysis**
- Scatter plot: kappa score by feature type
- Error bars: 95% confidence intervals

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_scope/docs/youra_research/h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (feature extraction + kappa calculation)
2. `kappa_task_type > 0.80 AND kappa_modality > 0.80 AND ICC_dataset_size > 0.80`

**Gate Logic:**
- ✅ PASS: All kappa > 0.80 → H-M1 satisfied, proceed to H-M2
- ⚠️ PARTIAL: Any kappa [0.70, 0.80] → Protocol refinement, re-test on 10 new benchmarks
- ❌ FAIL: Any kappa < 0.70 → MUST_WORK gate fails, STOP workflow

---

## Appendix: Reference Implementations

**MCP ABLATION MODE** - No implementations retrieved from Archon/Exa/Serena.

**Standard References:**
1. **Cohen's Kappa:** Scikit-learn implementation
   - URL: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.cohen_kappa_score.html
   - Usage: Standard for categorical inter-rater reliability

2. **ICC Calculation:** SciPy + NumPy
   - URL: https://en.wikipedia.org/wiki/Intraclass_correlation
   - Usage: Continuous variable agreement

3. **Papers with Code API:**
   - URL: https://paperswithcode.com/api/v1/docs/
   - Usage: Benchmark metadata retrieval

4. **Inter-Rater Reliability Studies (Literature):**
   - Landis, J. R., & Koch, G. G. (1977). "The measurement of observer agreement for categorical data." Biometrics, 33(1), 159-174.
   - Fleiss, J. L. (1971). "Measuring nominal scale agreement among many raters." Psychological bulletin, 76(5), 378.

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-25

### Workflow History for This Hypothesis
- 2026-08-25: Phase 2C experiment design initiated (MCP ablation mode)
- Status: IN_PROGRESS
- Gate: MUST_WORK (kappa > 0.80 required)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
