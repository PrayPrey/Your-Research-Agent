# Product Requirements Document (PRD)

**Date:** 2026-08-25  
**Hypothesis:** H-M1 - Feature Extraction Protocol Inter-Rater Agreement  
**Type:** MECHANISM  
**Status:** Implementation Planning

---

## Executive Summary

### Purpose
Validate that a standardized feature extraction protocol (Papers with Code taxonomy for task types, regex patterns for metrics, category tags for modality, table parsing for dataset size) achieves >0.80 inter-rater agreement (Cohen's kappa), proving the protocol is objective enough for scaled deployment.

### Success Criteria
- Cohen's kappa >0.80 for task type, modality, and metric extraction
- ICC >0.80 for dataset size extraction
- Inter-rater study completed with 20 diverse benchmarks
- Protocol refinement process documented if kappa [0.70, 0.80]

### Scope
**In Scope:**
- Feature extraction protocol implementation
- Papers with Code API integration
- Inter-rater agreement calculation (Cohen's kappa, ICC)
- Benchmark diversity sampling (vision, language, audio, multimodal)
- Protocol documentation and calibration workflow

**Out of Scope:**
- Model training (this is annotation study, not ML)
- Large-scale benchmark collection (>20 samples)
- Citation network analysis
- Coverage prediction (deferred to H-M2)

---

## Problem Statement

### Context
Manual benchmark review requires weeks of expert time. Without objective feature extraction achieving >0.80 inter-rater agreement, automated approaches cannot scale to 100+ benchmarks.

### Current State
Researchers manually review benchmarks to extract task types, metrics, modalities, and dataset sizes - subjective and time-consuming.

### Desired State
Standardized protocol enables independent annotators to achieve substantial agreement (kappa >0.80), validating objectivity for automation.

### Gap Analysis
Protocol objectivity unproven. Need empirical validation with diverse benchmarks before scaling.

---

## Functional Requirements

### FR1: Benchmark Sample Collection
**Description:** Collect 20 diverse DL benchmarks from Papers with Code API spanning task types, modalities, and dataset sizes.

**Acceptance Criteria:**
- 20 benchmarks selected via stratified sampling
- Coverage: Vision (8), language (7), audio (3), multimodal (2)
- Dataset sizes: Small (<10K), medium (10K-100K), large (>100K), very large (>1M)
- Publication years: 2015-2024 span
- Each benchmark has accessible paper and extractable features

**Dependencies:** Papers with Code API access

### FR2: Feature Extraction Protocol Implementation
**Description:** Implement standardized protocol with PWC taxonomy mapper, regex patterns, modality decision tree, and table parser.

**Acceptance Criteria:**
- PWC taxonomy mapping function for task types
- Regex patterns for common metrics (accuracy, F1, mAP, BLEU, perplexity, etc.)
- Modality classification decision tree (image/text/audio/video/multimodal)
- Table parsing logic for dataset size extraction
- Protocol documentation with decision rules

**Dependencies:** FR1 (benchmarks)

### FR3: Independent Annotation Workflow
**Description:** Two annotators independently extract features from 20 benchmarks following protocol.

**Acceptance Criteria:**
- Pre-study calibration on 3 practice benchmarks
- Independent annotation (no communication during study)
- Time limit: 2 hours per annotator
- Uncertainty flags recorded for ambiguous cases
- Protocol version number tracked

**Dependencies:** FR2 (protocol)

### FR4: Inter-Rater Agreement Calculation
**Description:** Calculate Cohen's kappa for categorical features (task type, modality, metrics) and ICC for continuous features (dataset size).

**Acceptance Criteria:**
- Cohen's kappa computed for each categorical feature
- ICC computed for dataset size
- 95% confidence intervals reported
- Disagreement patterns identified
- Results stored in structured format

**Dependencies:** FR3 (annotations)

**Implementation Notes:**
```python
from sklearn.metrics import cohen_kappa_score
from scipy.stats import pearsonr
import numpy as np

# Cohen's kappa for categorical
kappa = cohen_kappa_score(annotator1_labels, annotator2_labels)

# ICC for continuous (dataset size)
def calculate_icc(ratings):
    n, k = ratings.shape
    mean_ratings = np.mean(ratings, axis=1)
    ss_between = k * np.sum((mean_ratings - np.mean(ratings))**2)
    ss_within = np.sum((ratings - mean_ratings[:, None])**2)
    ms_between = ss_between / (n - 1)
    ms_within = ss_within / (n * (k - 1))
    icc = (ms_between - ms_within) / (ms_between + (k - 1) * ms_within)
    return icc
```

### FR5: Protocol Refinement (Conditional)
**Description:** If any kappa in [0.70, 0.80], refine protocol and re-test on 10 new benchmarks.

**Acceptance Criteria:**
- Disagreement cases analyzed
- Decision rules added to protocol
- Protocol version incremented
- Re-test with 10 new benchmarks
- Updated kappa scores computed

**Dependencies:** FR4 (kappa <0.80 detected)

### FR6: Visualization Generation
**Description:** Generate required gate metrics chart and optional analysis figures.

**Acceptance Criteria:**
- **Gate Metrics Chart (mandatory):** Kappa scores vs 0.80 threshold bar chart
- Confusion matrix heatmap for task type annotations
- Feature distribution histogram (task/modality coverage)
- Disagreement case scatter plot with error bars
- All figures saved to `figures/` subfolder

**Dependencies:** FR4 (agreement scores)

---

## Data Requirements

### Input Data

#### Dataset 1: Papers with Code Benchmark List
- **Source:** Papers with Code API (https://paperswithcode.com/api/v1/datasets/)
- **Format:** JSON API response
- **Size:** 20 benchmarks
- **Access:** Public API
- **Preprocessing:** Stratified sampling by task type and modality

#### Dataset 2: Benchmark Papers (PDFs)
- **Source:** arXiv, ACL Anthology, conference proceedings
- **Format:** PDF
- **Size:** 20 papers
- **Access:** Public via DOI/arXiv links
- **Preprocessing:** Text extraction, table parsing

### Output Data

#### Annotation Records
- **Format:** CSV or JSON
- **Schema:**
  ```python
  {
    "benchmark_id": str,
    "annotator_id": str,
    "task_type": str,  # PWC taxonomy category
    "metrics": List[str],  # extracted metric names
    "modality": str,  # image/text/audio/video/multimodal
    "dataset_size": int,  # number of samples
    "uncertainty_flag": bool
  }
  ```

#### Agreement Scores
- **Format:** JSON
- **Schema:**
  ```python
  {
    "task_type_kappa": float,
    "modality_kappa": float,
    "metrics_kappa": float,
    "dataset_size_icc": float,
    "confidence_intervals": Dict[str, Tuple[float, float]]
  }
  ```

---

## Non-Functional Requirements

### NFR1: Reproducibility
- Protocol versioning tracked in documentation
- Random seed for benchmark sampling
- Annotation timestamps recorded

### NFR2: Objectivity
- Decision rules explicit and testable
- Minimizes annotator judgment calls
- Disagreement cases analyzed systematically

### NFR3: Scalability Readiness
- Protocol format supports automation (regex, taxonomy mapping)
- Extensible to new task types and modalities
- Refinement process documented for future updates

---

## Dependencies

### External Libraries
- `scikit-learn` (Cohen's kappa)
- `scipy` (ICC calculation)
- `requests` (Papers with Code API)
- `matplotlib` / `seaborn` (visualization)
- `pandas` (data handling)

### Data Sources
- Papers with Code API
- arXiv papers
- Conference proceedings (ACL, NeurIPS, CVPR, etc.)

### MCP Services
- None (annotation study, not code implementation)

---

## Success Metrics

### Primary Metrics
1. **Task Type Kappa:** >0.80 (MUST_WORK gate)
2. **Modality Kappa:** >0.80 (MUST_WORK gate)
3. **Metrics Kappa:** >0.80 (MUST_WORK gate)
4. **Dataset Size ICC:** >0.80 (MUST_WORK gate)

### Secondary Metrics
- Annotation time per benchmark (<6 minutes average)
- Uncertainty flag rate (<15% of annotations)
- Protocol refinement rounds (0-1 expected)

### Gate Logic
- ✅ **PASS:** All kappa/ICC >0.80
- ⚠️ **PARTIAL:** Any kappa [0.70, 0.80] → Protocol refinement
- ❌ **FAIL:** Any kappa <0.70 → MUST_WORK gate fails, workflow STOPS

---

## Risk Assessment

### Technical Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| PWC taxonomy incomplete for edge-case tasks | Medium | Medium | Document taxonomy gaps, use "other" category |
| Regex patterns miss domain-specific metrics | Medium | High | Manual review of unmatched metrics, pattern expansion |
| Table parsing fails on non-standard formats | High | Medium | Fallback to manual extraction with note |

### Data Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Papers unavailable for selected benchmarks | Low | Low | Substitute with next stratified sample |
| Inconsistent reporting across papers | High | Medium | Protocol includes handling rules for missing data |

---

## Open Questions
1. Should we use 2 or 3 annotators for stronger reliability?
   - **Decision:** Start with 2 (standard), add 3rd if kappa borderline [0.75, 0.80]

2. How to handle benchmarks with multiple task types?
   - **Decision:** Extract primary task type based on paper abstract emphasis

3. Dataset size: report train set only or train+val+test?
   - **Decision:** Total dataset size (all splits), note in protocol

---

## Appendix

### Protocol Document Outline
1. Feature Extraction Rules
   - PWC Taxonomy Mapping Table
   - Regex Patterns for Metrics
   - Modality Decision Tree
   - Table Parsing Guidelines
2. Calibration Procedure
3. Disagreement Resolution Process
4. Version History

### Related Hypotheses
- **H-M2:** Feature clustering reveals coverage families (depends on H-M1 protocol)
- **H-M3:** Coverage prediction from features (depends on H-M1 and H-M2)

---

**Document Status:** COMPLETE  
**Next Phase:** Phase 3 Step 3 - Architecture Design
