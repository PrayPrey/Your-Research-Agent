# Product Requirements Document: h-m-integrated

**Hypothesis:** Semantic Embeddings Encode Lifecycle Role via Distributional Signatures
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Date:** 2026-03-18
**Phase:** 3 - Implementation Planning

---

## Executive Summary

This PRD specifies the implementation requirements for validating the h-m-integrated hypothesis: semantic embeddings encode lifecycle role via distributional signatures, enabling unsupervised clustering to recover 2-tier lifecycle structure that exceeds baselines by ≥0.15 NMI.

**Core Mechanism:** Frozen sentence-transformer embeddings (all-MiniLM-L6-v2) capture semantic distributional signatures that enable K-means clustering to recover lifecycle structure unsupervised, outperforming permutation, LDA, and lexical baselines by at least 0.15 NMI.

**Success Criteria:**
- Primary: NMI(unsupervised) > 0.6 AND improvement over max(baselines) ≥ 0.15
- Secondary: Normalized NMI ≥ 0.6 (signal persists after controls), Probe variance < 0.1 (generalization)

---

## Problem Statement

### Research Question
Do semantic embeddings encode lifecycle role through distributional signatures that enable unsupervised recovery of lifecycle structure beyond baseline methods?

### Hypothesis Dependencies
**Prerequisites:** h-e1 (COMPLETED) - Lifecycle separability validated (κ ≥ 0.60, probe ≥ 0.75)

**Builds On:**
- h-e1 validated that lifecycle constructs are operationally stable and embeddings contain linear lifecycle signals
- This hypothesis tests whether distributional signatures enable full unsupervised recovery

### Gate Information
- **Type:** SHOULD_WORK
- **Failure Response:** EXPLORE alternative embeddings OR PIVOT to amplification framework OR SCOPE to repository-specific

---

## Functional Requirements

### FR1: Dataset Loading and Preprocessing
**Priority:** P0 (Blocker)
**Source:** Phase 2C Section "Dataset"

**Requirements:**
- Load Cross-Repository Metadata Sample from h-e1 (N=300)
  - Path: `data/metadata_sample/metadata_fields.csv`
  - Columns: repository, field_name, field_value, lifecycle_label
- Repository distribution: HuggingFace (150), OpenML (100), UCI (50)
- Lifecycle labels: General Information (275), Responsible AI (25)
- Scaffolding split: 75 scaffolded, 225 unscaffolded
- Text representation: Concatenate `field_name + ": " + field_value`
- Preprocessing: Remove excessive whitespace, normalize unicode
- NO additional preprocessing (preserve distributional signatures)

**Acceptance Criteria:**
- Dataset loads with 300 samples
- Text fields correctly concatenated
- Original distributions preserved (no sampling artifacts)

---

### FR2: Embedding Model Loading
**Priority:** P0 (Blocker)
**Source:** Phase 2C Section "Models - Baseline Model"

**Requirements:**
- Load sentence-transformers model: `all-MiniLM-L6-v2`
- Model parameters: 22.7M (6 layers, 384 hidden dim)
- Frozen weights (no fine-tuning)
- Encoding configuration:
  - Output: 384-dimensional embeddings (L2-normalized)
  - Context window: 256 tokens
  - Batch processing with progress bar

**Code Pattern:**
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(texts, show_progress_bar=True)
# Returns: numpy array of shape (n_samples, 384)
```

**Acceptance Criteria:**
- Model loads successfully from HuggingFace Hub
- Embeddings shape: (300, 384)
- No NaN values in embeddings

---

### FR3: Unsupervised Clustering Pipeline
**Priority:** P0 (Blocker)
**Source:** Phase 2C Section "Models - Proposed Model"

**Requirements:**
- Implement K-means clustering on semantic embeddings
- Configuration:
  - `n_clusters=2` (2-tier lifecycle structure)
  - `random_state=42` (reproducibility)
  - `init='k-means++'` (smart centroid initialization)
- Output: Cluster assignments {0, 1} for all 300 samples

**Code Pattern:**
```python
from sklearn.cluster import KMeans
clusterer = KMeans(n_clusters=2, random_state=42)
labels_pred = clusterer.fit_predict(embeddings)
```

**Acceptance Criteria:**
- K-means produces exactly 2 clusters
- All samples assigned to clusters
- Cluster assignments deterministic (fixed seed)

---

### FR4: Baseline Method 1 - Permutation
**Priority:** P0 (Blocker)
**Source:** Phase 2C Section "Training Protocol - Baseline Configurations"

**Requirements:**
- Implement random label shuffle baseline
- Method: `np.random.permutation(labels_true)`
- Expected NMI: ~0.0

**Acceptance Criteria:**
- Baseline produces valid cluster labels
- NMI computed successfully

---

### FR5: Baseline Method 2 - LDA Topic Modeling
**Priority:** P0 (Blocker)
**Source:** Phase 2C Section "Training Protocol - Baseline Configurations"

**Requirements:**
- Implement LDA 2-topic baseline
- Library: `sklearn.decomposition.LatentDirichletAllocation`
- Configuration:
  - `n_components=2` (2 topics matching 2-tier structure)
  - `max_iter=100`
  - `random_state=42`
- Expected NMI: 0.40-0.50

**Code Pattern:**
```python
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

vectorizer = CountVectorizer()
doc_term_matrix = vectorizer.fit_transform(texts)
lda = LatentDirichletAllocation(n_components=2, max_iter=100, random_state=42)
topic_distributions = lda.fit_transform(doc_term_matrix)
labels_lda = topic_distributions.argmax(axis=1)
```

**Acceptance Criteria:**
- LDA converges within 100 iterations
- Topic assignments mapped to binary labels
- NMI computed successfully

---

### FR6: Baseline Method 3 - Lexical Keyword Matching
**Priority:** P0 (Blocker)
**Source:** Phase 2C Section "Training Protocol - Baseline Configurations"

**Requirements:**
- Implement rule-based keyword clustering
- Method: Keyword matching (e.g., "bias", "ethics", "fairness" → RAI cluster)
- Keyword list: ["bias", "ethics", "fairness", "responsible", "accountability", "transparency"]
- Default cluster: General Information (no keyword match)
- Expected NMI: ~0.45

**Acceptance Criteria:**
- Keyword matching case-insensitive
- All samples assigned to clusters
- NMI computed successfully

---

### FR7: NMI Metric Computation
**Priority:** P0 (Blocker)
**Source:** Phase 2C Section "Evaluation - Primary Metrics"

**Requirements:**
- Compute Normalized Mutual Information (NMI)
- Library: `sklearn.metrics.normalized_mutual_info_score`
- Configuration: `average_method='arithmetic'`
- Range: [0, 1], 1.0 = perfect correspondence
- Formula: NMI(U, V) = 2 * MI(U, V) / (H(U) + H(V))

**Code Pattern:**
```python
from sklearn.metrics import normalized_mutual_info_score
nmi = normalized_mutual_info_score(labels_true, labels_pred,
                                     average_method='arithmetic')
```

**Acceptance Criteria:**
- NMI computed for all methods (semantic, permutation, LDA, lexical)
- Values in valid range [0, 1]
- Baseline gap computed: NMI(semantic) - max(NMI(baselines))

---

### FR8: Control Experiment - Length Normalization
**Priority:** P1 (High)
**Source:** Phase 2C Section "Training Protocol - Normalization Controls"

**Requirements:**
- Implement length normalization control
- Method: Truncate/pad text to fixed length (e.g., 100 tokens)
- Re-run semantic clustering on normalized text
- Compute NMI_normalized
- Test signal persistence after stylistic control

**Acceptance Criteria:**
- Length normalization applied consistently
- NMI_normalized computed
- Signal persistence verified: NMI_normalized ≥ 0.6

---

### FR9: Control Experiment - Modality Filtering
**Priority:** P1 (High)
**Source:** Phase 2C Section "Training Protocol - Normalization Controls"

**Requirements:**
- Implement modality filtering control
- Method: Remove deontic language markers (should, must, required, etc.)
- Re-run semantic clustering on filtered text
- Test signal persistence after artifact removal

**Acceptance Criteria:**
- Deontic markers removed from text
- NMI computed on filtered embeddings
- Control effectiveness documented

---

### FR10: Generalization Test - Repository Stratification
**Priority:** P1 (High)
**Source:** Phase 2C Section "Evaluation - Secondary Metrics"

**Requirements:**
- Train repository-specific linear probes (HF/OpenML/UCI separate)
- Measure accuracy variance to test generalization
- Expected: Probe variance < 0.1
- Compare NMI by repository

**Acceptance Criteria:**
- 3 separate probes trained (HF, OpenML, UCI)
- Accuracy variance computed
- Repository-specific NMI documented

---

### FR11: Scaffolding Effect Analysis
**Priority:** P2 (Medium)
**Source:** Phase 2C Section "Continuation Context"

**Requirements:**
- Compare NMI for scaffolded vs unscaffolded metadata
- Scaffolded: 75 samples (HF Open Datasheets)
- Unscaffolded: 225 samples
- Quantify interface amplification effect

**Acceptance Criteria:**
- NMI computed for both groups
- Gap quantified: NMI_gap = NMI(scaffolded) - NMI(unscaffolded)
- Interface effect documented

---

### FR12: Visualization - Gate Metrics Comparison
**Priority:** P1 (High)
**Source:** Phase 2C Section "Visualization Requirements - Required Figure"

**Requirements:**
- Generate bar chart: NMI scores for all methods
- Methods: Semantic, Permutation, LDA, Lexical
- Add horizontal line at 0.60 threshold
- Add vertical gap annotation (0.15 minimum)
- Save to: `h-m-integrated/figures/gate_metrics.png`

**Acceptance Criteria:**
- All 4 methods displayed
- Threshold line visible
- Baseline gap annotated
- Figure saved to correct path

---

### FR13: Visualization - Embedding Space (t-SNE/UMAP)
**Priority:** P2 (Medium)
**Source:** Phase 2C Section "Visualization Requirements - Additional Figures"

**Requirements:**
- Project 384-dim embeddings to 2D using t-SNE or UMAP
- Color points by true lifecycle labels
- Add cluster boundaries from K-means
- Save to: `h-m-integrated/figures/embedding_space.png`

**Acceptance Criteria:**
- 2D projection visualizes embedding structure
- True labels visible as colors
- Cluster separation visible

---

### FR14: Visualization - Confusion Matrix
**Priority:** P2 (Medium)
**Source:** Phase 2C Section "Visualization Requirements - Additional Figures"

**Requirements:**
- Generate confusion matrix: True lifecycle labels vs predicted clusters
- Show counts and percentages
- Save to: `h-m-integrated/figures/confusion_matrix.png`

**Acceptance Criteria:**
- Matrix shows cluster purity
- Both counts and percentages displayed
- Figure interpretable

---

### FR15: Validation Report Generation
**Priority:** P0 (Blocker)
**Source:** Phase 4 standard output

**Requirements:**
- Generate `04_validation.md` with:
  - Hypothesis statement
  - Gate criteria
  - All NMI scores (semantic + 3 baselines)
  - Baseline gap computation
  - Control experiment results
  - Generalization metrics
  - Figure references
  - PASS/PARTIAL/FAIL decision
  - Failure action if applicable

**Acceptance Criteria:**
- Report contains all required sections
- Gate decision clear (PASS/PARTIAL/FAIL)
- All metrics documented
- Figures referenced

---

## Non-Functional Requirements

### NFR1: Reproducibility
**Priority:** P0
- All random seeds fixed: `random_state=42`
- Deterministic clustering results
- Environment specification in requirements.txt

### NFR2: Performance
**Priority:** P1
- Embedding encoding: < 1 minute for 300 samples
- K-means clustering: < 10 seconds
- Total runtime: < 5 minutes

### NFR3: Code Quality
**Priority:** P1
- Modular pipeline design (encoding, clustering, evaluation separate)
- Clear function signatures with docstrings
- Type hints for key functions
- Assertion checks for intermediate results

### NFR4: Documentation
**Priority:** P1
- Inline comments for non-obvious operations
- README with usage instructions
- Requirements.txt with exact versions

---

## Data Specifications

### Input Data
**Source:** h-e1 validation dataset (reused)
**Format:** CSV file
**Location:** `data/metadata_sample/metadata_fields.csv`
**Schema:**
- `repository`: str (HuggingFace, OpenML, UCI)
- `field_name`: str (metadata field name)
- `field_value`: str (metadata field value)
- `lifecycle_label`: str (General Information, Responsible AI)

**Size:** 300 rows
**Missing Values:** None expected

### Output Data
**Validation Report:** `h-m-integrated/04_validation.md`
**Figures Directory:** `h-m-integrated/figures/`
**Intermediate Artifacts:**
- Embeddings: `(300, 384)` numpy array
- Cluster labels: `(300,)` numpy array
- NMI scores: dict with method names as keys

---

## Dependencies

### Python Packages
```
sentence-transformers==2.2.2
scikit-learn==1.3.0
numpy==1.24.3
pandas==2.0.3
matplotlib==3.7.2
seaborn==0.12.2
```

### Pre-trained Models
- `all-MiniLM-L6-v2` (HuggingFace Hub)

### Data Dependencies
- h-e1 dataset: `data/metadata_sample/metadata_fields.csv`

### Compute Requirements
- CPU: Any modern processor
- RAM: 4GB minimum
- GPU: Not required (frozen embeddings)
- Storage: < 100MB

---

## Success Criteria

### Primary Gate Criteria
1. **NMI(semantic) > 0.6** - Semantic clustering achieves target performance
2. **Baseline gap ≥ 0.15** - Semantic method exceeds best baseline by minimum margin

### Secondary Criteria
1. **Normalized NMI ≥ 0.6** - Signal persists after length/modality controls
2. **Probe variance < 0.1** - Generalization across repositories
3. **All baselines implemented** - Permutation, LDA, Lexical all functional

### Gate Decision Logic
```python
if NMI_semantic > 0.6 and baseline_gap >= 0.15:
    result = "PASS"
elif 0.5 <= NMI_semantic < 0.6 or 0.10 <= baseline_gap < 0.15:
    result = "PARTIAL"  # Signal exists but weak
else:
    result = "FAIL"  # No mechanism effect
```

### Failure Actions
- **If NMI < 0.6 OR baseline gap < 0.15:** EXPLORE alternative embeddings
- **If normalized NMI collapses:** PIVOT to amplification framework
- **If probe variance > 0.15:** SCOPE to repository-specific approach

---

## Risk Assessment

### Technical Risks
1. **Class imbalance** (8.3% RAI) may affect clustering
   - Mitigation: Document imbalance, consider stratified metrics
2. **Curse of dimensionality** (384-dim embeddings) may challenge K-means
   - Mitigation: Compare with MiniBatchKMeans if needed
3. **Lexical baseline** may be stronger than expected
   - Mitigation: Ensure gap criterion is met

### Dependency Risks
1. **HuggingFace Hub availability** for model download
   - Mitigation: Cache model locally after first download
2. **h-e1 dataset availability**
   - Mitigation: Dataset already collected and validated

---

## Implementation Notes

### Code Structure
```
h-m-integrated/
├── code/
│   ├── data_loader.py          # FR1: Dataset loading
│   ├── embedding_model.py      # FR2: Sentence-transformer loading
│   ├── clustering.py           # FR3: K-means clustering
│   ├── baselines.py            # FR4-6: Baseline methods
│   ├── evaluation.py           # FR7: NMI computation
│   ├── controls.py             # FR8-9: Normalization controls
│   ├── visualization.py        # FR12-14: Figure generation
│   ├── pipeline.py             # Main experiment pipeline
│   └── validation_report.py    # FR15: Report generation
├── figures/                    # Generated visualizations
├── 04_validation.md           # Final validation report
└── requirements.txt           # Python dependencies
```

### Execution Order
1. Load dataset (FR1)
2. Load embedding model (FR2)
3. Encode texts → embeddings
4. Run semantic clustering (FR3)
5. Run 3 baselines (FR4-6)
6. Compute NMI for all methods (FR7)
7. Run control experiments (FR8-9)
8. Run generalization tests (FR10-11)
9. Generate visualizations (FR12-14)
10. Generate validation report (FR15)

---

## Appendix: Phase 2C Traceability

| PRD Section | Phase 2C Source |
|-------------|-----------------|
| FR1 Dataset | Section "Dataset" + "Loading Information" |
| FR2 Model | Section "Models - Baseline Model" |
| FR3 Clustering | Section "Models - Proposed Model" + "Core Mechanism Implementation" |
| FR4-6 Baselines | Section "Training Protocol - Baseline Configurations" |
| FR7 NMI | Section "Evaluation - Primary Metrics" |
| FR8-9 Controls | Section "Training Protocol - Normalization Controls" |
| FR10 Generalization | Section "Evaluation - Expected Baseline Performance" |
| FR12-14 Figures | Section "Visualization Requirements" |
| Success Criteria | Section "Evaluation - Success Criteria" |

---

**Document Status:** Draft v1.0
**Next Step:** Architecture design (Step 3)
**Estimated Implementation Scope:** 10-15 implementation tasks
