# Validation Report: h-m-integrated

**Date:** 2026-03-18
**Hypothesis ID:** H-M-INTEGRATED
**Hypothesis Type:** MECHANISM
**Gate Type:** SHOULD_WORK
**Experiment ID:** h-m-integrated

---

## Hypothesis Statement

Semantic embeddings encode lifecycle role via distributional signatures, enabling unsupervised clustering to recover 2-tier lifecycle structure that exceeds baselines by ≥0.15 NMI.

---

## Gate Criteria

### Primary Criteria
- **NMI(semantic) > 0.6**: Semantic clustering achieves target performance
- **Baseline gap ≥ 0.15**: Semantic method exceeds best baseline by minimum margin

### Secondary Criteria
- **Normalized NMI ≥ 0.6**: Signal persists after length/modality controls
- **Probe variance < 0.1**: Generalization across repositories

---

## Experimental Results

### Dataset
- **Source**: Cross-Repository Metadata Sample (reused from h-e1)
- **Total Samples**: 300
- **Repository Distribution**: HuggingFace (150), OpenML (100), UCI (50)
- **Lifecycle Labels**: General Information (275), Responsible AI (25)
- **Scaffolding**: Scaffolded (75), Unscaffolded (225)
- **Class Imbalance**: 8.3% RAI (severe imbalance)

### NMI Scores (All Methods)

| Method | NMI Score | Notes |
|--------|-----------|-------|
| **Semantic** | **0.0229** | K-means clustering on all-MiniLM-L6-v2 embeddings |
| Permutation | 0.0101 | Random label shuffle baseline |
| LDA | 0.0049 | 2-topic model baseline |
| Lexical | 0.0000 | Keyword matching baseline (no matches) |

**Baseline Gap**: 0.0129 (semantic - max(baselines))

### Control Experiments

| Control Type | NMI Score | Signal Persistence |
|--------------|-----------|-------------------|
| Original | 0.0229 | Baseline |
| Length Normalized | 0.0229 | Identical (no stylistic artifact) |
| Modality Filtered | 0.0229 | Identical (no deontic marker effect) |

**Interpretation**: Signal is consistent across controls, suggesting it is not driven by length or modality artifacts. However, the signal is extremely weak.

### Generalization Tests

#### Repository-Specific Probes
| Repository | Probe Accuracy (3-fold CV) | Notes |
|------------|----------------------------|-------|
| HuggingFace | 0.9733 ± 0.0094 | Strong linear signal |
| OpenML | Skipped | Only one class present (severe imbalance) |
| UCI | 1.0000 ± 0.0000 | Perfect separation |

**Probe Variance**: 0.0002 (< 0.1 threshold) ✅

**Interpretation**: Despite low clustering NMI, **linear probes achieve near-perfect accuracy** (97-100%), confirming that embeddings contain strong supervised signals. The issue is with **unsupervised recovery**, not embedding quality.

#### Repository-Specific NMI
| Repository | NMI Score | Notes |
|------------|-----------|-------|
| HuggingFace | 0.0254 | Very low (consistent with overall) |
| OpenML | Skipped | Insufficient diversity |
| UCI | 0.3914 | **Moderate signal** (unexpected) |

**Interpretation**: UCI shows substantially higher NMI (0.39), suggesting repository-specific effects. This contradicts the low overall NMI and warrants further investigation.

### Scaffolding Effect
| Condition | NMI Score | Notes |
|-----------|-----------|-------|
| Scaffolded | 0.0471 | HF Open Datasheets (N=75) |
| Unscaffolded | 0.0591 | No structured interface (N=225) |
| **Gap** | **-0.0120** | **Negative** (unexpected) |

**Interpretation**: Scaffolding shows **negative gap** (unscaffolded > scaffolded), contradicting the interface amplification hypothesis. This suggests scaffolded metadata may be more homogeneous.

---

## Gate Evaluation

### Primary Criteria Results

| Criterion | Threshold | Actual | Met? |
|-----------|-----------|--------|------|
| NMI(semantic) > 0.6 | 0.6 | 0.0229 | ❌ **FAIL** |
| Baseline gap ≥ 0.15 | 0.15 | 0.0129 | ❌ **FAIL** |

### Secondary Criteria Results

| Criterion | Threshold | Actual | Met? |
|-----------|-----------|--------|------|
| Normalized NMI ≥ 0.6 | 0.6 | 0.0229 | ❌ **FAIL** |
| Probe variance < 0.1 | 0.1 | 0.0002 | ✅ **PASS** |

### Overall Gate Status

**Status**: **FAIL** ❌

Both primary criteria failed. Semantic NMI (0.0229) is **96% below threshold** (0.6), and baseline gap (0.0129) is **91% below threshold** (0.15).

---

## Failure Analysis

### Root Cause: Class Imbalance & Unsupervised Recovery Failure

The experiment reveals a critical failure in **unsupervised lifecycle recovery**, despite strong supervised signals:

1. **Severe Class Imbalance**: 8.3% RAI (25/300 samples) creates statistical challenge for unsupervised clustering
2. **K-means Distribution**: Produced 230/70 split instead of 275/25 true distribution
3. **Supervised vs Unsupervised Gap**: Linear probes achieve 97-100% accuracy, but K-means NMI is only 0.02
4. **Mechanism Failure**: Distributional signatures exist (proven by probes) but are **not cluster-inducing**

### Why Linear Probes Succeed but K-means Fails

- **Linear Probes (Supervised)**: Use label information to find optimal decision boundary → 97-100% accuracy
- **K-means (Unsupervised)**: Finds natural clusters based on distance → fails to recover rare class
- **Interpretation**: Embeddings capture lifecycle **semantically** but RAI class is too sparse and distributed to form natural clusters

### Lexical Baseline Anomaly

Lexical baseline achieved **NMI=0.0** (no keywords matched), indicating:
- RAI keywords ("bias", "ethics", "fairness", etc.) are **absent** from metadata fields
- This contradicts typical Responsible AI documentation, suggesting:
  - Dataset collection issue (fields may not contain RAI-specific language)
  - Lifecycle labels may be **structural** (field position/schema) rather than **content-based**

---

## Failure Action

**Recommendation**: **EXPLORE - Alternative representations and methods**

### Specific Actions

1. **Address Class Imbalance**:
   - Re-sample dataset with balanced RAI/General ratio (e.g., 50/50)
   - Use stratified sampling to ensure sufficient RAI representation
   - Consider SMOTE or other oversampling techniques

2. **Alternative Clustering Methods**:
   - Replace K-means with **density-based clustering** (HDBSCAN) to handle imbalanced clusters
   - Test **Gaussian Mixture Models** with class priors
   - Consider **semi-supervised clustering** with partial labels

3. **Alternative Embeddings**:
   - Test **domain-specific embeddings** (e.g., SciBERT for research metadata)
   - Try **larger models** (all-mpnet-base-v2, instructor-large)
   - Consider **contrastive learning** to enhance RAI class separation

4. **Re-evaluate Hypothesis**:
   - Pivot to **supervised** lifecycle detection (matches probe success)
   - Reframe as **few-shot learning** problem (given RAI scarcity)
   - Drop "unsupervised recovery" requirement, focus on "semantic separability"

---

## Figures

### Figure 1: Gate Metrics Comparison
![Gate Metrics](figures/gate_metrics.png)

**Interpretation**: All methods perform poorly (NMI < 0.03). Semantic clustering barely exceeds baselines. Gap (0.013) is far below threshold (0.15).

### Figure 2: Embedding Space (t-SNE)
![Embedding Space](figures/embedding_space.png)

**Interpretation**: t-SNE projection shows RAI samples (orange) are **scattered** throughout General Information samples (blue), with no clear cluster structure. This visualizes why K-means fails.

### Figure 3: Confusion Matrix
![Confusion Matrix](figures/confusion_matrix.png)

**Interpretation**: K-means assigns most samples to Cluster 0 (230/300). Cluster 1 captures only 28% of samples but includes some RAI cases. High misclassification rate.

### Figure 4: Repository Stratification
![Repository Stratification](figures/repository_stratification.png)

**Interpretation**: UCI shows substantially higher NMI (0.39) than HuggingFace (0.03), suggesting repository-specific effects. This heterogeneity contradicts the generalizable mechanism hypothesis.

### Figure 5: Scaffolding Effect
![Scaffolding Effect](figures/scaffolding_effect.png)

**Interpretation**: Scaffolded samples show **lower** NMI than unscaffolded (negative gap), contradicting interface amplification hypothesis. Scaffolded metadata may be more homogeneous.

---

## Conclusion

### Hypothesis Verdict

**FAIL** - The hypothesis that semantic embeddings enable unsupervised clustering to recover lifecycle structure is **rejected**.

### Key Findings

1. ✅ **Embeddings Capture Lifecycle Signals**: Linear probes achieve 97-100% accuracy
2. ❌ **Unsupervised Recovery Fails**: K-means NMI = 0.02 (far below threshold)
3. ❌ **Baseline Gap Insufficient**: Gap = 0.013 (91% below threshold)
4. ⚠️ **Repository Heterogeneity**: UCI shows 15x higher NMI than HuggingFace
5. ⚠️ **Class Imbalance Critical**: 8.3% RAI prevents natural clustering

### Methodological Issues

1. **Dataset Limitation**: Severe class imbalance (8.3% RAI) makes unsupervised clustering infeasible
2. **Keyword Mismatch**: Lexical baseline found **zero** RAI keywords, suggesting lifecycle is schema-based not content-based
3. **Repository Specificity**: Large NMI variance across repositories (0.03 to 0.39) contradicts generalizable mechanism

### Path Forward

This hypothesis should be **ABANDONED** in its current form. However, the strong supervised probe results (97-100%) suggest a **pivot** to supervised lifecycle detection is viable:

**Recommended Pivot**: H-M-SUPERVISED - "Semantic embeddings enable supervised lifecycle classification with ≥90% accuracy under cross-repository conditions"

This reformulation:
- Leverages proven embedding quality (probe success)
- Acknowledges class imbalance reality (supervised methods handle this)
- Drops failed unsupervised requirement
- Maintains scientific value (cross-repository generalization)

---

## Appendix: Experiment Metadata

- **Experiment Runtime**: ~60 seconds
- **Model**: sentence-transformers/all-MiniLM-L6-v2 (22.7M parameters)
- **Clustering**: K-means (k=2, random_state=42)
- **Baseline Methods**: Permutation, LDA (2-topic), Lexical (10 keywords)
- **Control Experiments**: Length normalization (100 tokens), Modality filtering (8 markers)
- **Generalization Tests**: Repository-specific probes (3-fold CV), Scaffolding effect
- **Figures Generated**: 5 (gate_metrics, embedding_space, confusion_matrix, repository_stratification, scaffolding_effect)
- **Results File**: `results/gate_evaluation.json`

---

**Report Generated**: 2026-03-18
**Validation Status**: FAIL
**Failure Action**: EXPLORE - Alternative representations and methods
**Next Phase**: N/A (hypothesis rejected, recommend pivot)
