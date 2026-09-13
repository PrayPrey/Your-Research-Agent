# Experiment Design: H-M2

**Date:** 2026-08-25
**Author:** Anonymous
**Hypothesis Statement:** If we embed benchmark design features using SentenceBERT and apply k-means clustering, then benchmarks will cluster into coverage families with ≥60% intra-family similarity on the feature space, because similar design constraints (task/metric/modality) create similar hypothesis coverage patterns.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** - Validates coverage family clustering.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M1 (VALIDATED - feature extraction protocol established, kappa=0.917)
**Gate Status:** MUST_WORK (failure triggers clustering method pivot)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (needs validated feature extraction)

### Gate Condition
MUST_WORK gate - Intra-family similarity must achieve ≥60%. If <60%, PIVOT to alternative clustering (hierarchical) or different embeddings (USE vs SentenceBERT).

---

## Continuation Context

Second hypothesis in verification plan. Builds on H-M1's validated feature extraction protocol (Cohen's kappa=0.917). This hypothesis validates that design features create meaningful groupings, not arbitrary clusters.

### Previous Hypothesis Results
**H-M1 (VALIDATED):**
- Cohen's kappa: 0.917 (task type), 1.0 (modality, metrics, dataset size)
- Dataset: 20 benchmarks stratified across vision/language/audio/multimodal
- Output: `experiments/h-m1/data/h-m1/sampled_benchmarks.csv` with validated features
- Key findings: Protocol achieves substantial agreement; disagreements limited to edge cases (COCO, OpenImages: detection vs segmentation)

---

## Implementation Research Summary

**MCP ABLATION MODE**: Archon, Exa, Serena MCPs unavailable. Experiment design based on Phase 2B protocol + standard clustering methodology (sentence-transformers + scikit-learn).

### Archon Knowledge Base Findings

*MCP unavailable - No historical implementation cases retrieved*

### Archon Code Examples

*MCP unavailable - No code examples retrieved*

### Exa Implementation Search

*MCP unavailable - No GitHub repositories retrieved*

**Fallback Implementation Strategy:**
- SentenceBERT: `sentence-transformers` library (HuggingFace), model='all-MiniLM-L6-v2'
- K-means: `scikit-learn.cluster.KMeans`
- Similarity: Cosine similarity via `sklearn.metrics.pairwise.cosine_similarity`
- Silhouette score: `sklearn.metrics.silhouette_score`

### Codebase Analysis (Serena)

*MCP unavailable - No existing embedding/clustering modules found*

**Reusable Components:**
- H-M1 feature extraction pipeline (`experiments/h-m1/src/h_m1/extractor.py`)
- H-M1 validated dataset (`experiments/h-m1/data/h-m1/sampled_benchmarks.csv`)

---

## Dataset Specification

### Type
**custom** (real data from H-M1 validation)

**Justification:** H-M2 operates on features extracted from 20 benchmarks validated in H-M1 (ImageNet, COCO, SQuAD, etc.). These are real benchmark design features, not synthetic data.

### Source
- **Primary Input:** `experiments/h-m1/data/h-m1/sampled_benchmarks.csv` (H-M1 output)
- **Features per Benchmark:**
  - `task`: PWC taxonomy category (e.g., image_classification, question_answering)
  - `modality`: {image, text, audio, multimodal}
  - `size`: Dataset size (samples)
  - Derived features: task-modality interaction, size category

### Sample Size
**20 benchmarks** (full H-M1 dataset)

**Stratification:**
- Vision: 8 (ImageNet, COCO, Cityscapes, MNIST, CIFAR-10, PASCAL VOC, OpenImages, ADE20K)
- Language: 7 (SQuAD, WMT14, GLUE, WikiText-103, Natural Questions, WMT16, BoolQ)
- Audio: 3 (LibriSpeech, Common Voice, TIMIT)
- Multimodal: 2 (VQA v2, MS-COCO Captions)

**Rationale for Size:**
20 is small for production clustering but sufficient for PoC validation. H-M3 will extend to 50-100 benchmarks for historical prediction. This experiment validates clustering methodology.

### Preparation Protocol
1. Load `sampled_benchmarks.csv` from H-M1
2. Construct feature strings: `"task: {task}, modality: {modality}, size: {size_category}"`
3. Encode via SentenceBERT (`all-MiniLM-L6-v2`) → 384-dim embeddings
4. Normalize embeddings (L2 norm)
5. Apply k-means for k ∈ {3, 5, 7, 10}

**No synthetic data generation.** All inputs are real benchmarks.

---

## Model Specification

### Architecture
**Clustering Pipeline:**
1. **Embedding:** SentenceBERT (`sentence-transformers/all-MiniLM-L6-v2`)
   - Input: Feature strings (task + modality + size category)
   - Output: 384-dim dense vectors
2. **Clustering:** Scikit-learn K-means
   - Distance metric: Euclidean (cosine similarity via normalized embeddings)
   - Initialization: k-means++ (10 random seeds)
3. **Evaluation:** Silhouette score + intra-family cosine similarity

### Hyperparameters
| Parameter | Value | Justification |
|-----------|-------|---------------|
| **k values** | {3, 5, 7, 10} | Sweep to find optimal family count. Expected 5-7 families (vision-classification, vision-detection, language-QA, language-generation, audio, multimodal). |
| **SentenceBERT model** | all-MiniLM-L6-v2 | Lightweight (22M params), SOTA on semantic similarity, pre-trained on 1B+ sentence pairs. |
| **K-means init** | k-means++ | Better initialization than random. |
| **K-means seeds** | 10 random seeds | Mitigate initialization sensitivity. Report median silhouette + similarity. |
| **Similarity metric** | Cosine similarity | Standard for high-dim embeddings. |

### Pretrained Models
- **SentenceBERT:** HuggingFace `sentence-transformers/all-MiniLM-L6-v2`
  - Download: `SentenceTransformer('all-MiniLM-L6-v2')` (auto-cached)
  - No fine-tuning (pre-trained embeddings sufficient for PoC)

---

## Baseline Methods

### Baseline 1: Random Clustering
**Description:** Assign benchmarks to k families uniformly at random.

**Expected Performance:**
- Intra-family similarity: ~33% (random chance with 20 benchmarks, k=5)
- Silhouette score: near 0 (no cluster structure)

**Purpose:** Lower bound. If SentenceBERT clustering ≤ random, features don't capture structure.

### Baseline 2: Manual Clustering (Ground Truth)
**Description:** Expert manually groups benchmarks by task type (e.g., all image_classification together).

**Expected Performance:**
- Intra-family similarity: ~80-90% (expert-defined families align closely)
- Silhouette score: >0.6 (clear separation)

**Purpose:** Upper bound. If SentenceBERT approaches manual clusters, validates embedding quality.

### Comparison Plan
1. Compute intra-family similarity for all 3 methods (random, SentenceBERT k-means, manual)
2. Plot k vs similarity curves (SentenceBERT should exceed random baseline)
3. Gate check: SentenceBERT ≥60% similarity (midpoint between random 33% and manual 80-90%)

---

## Experimental Design

### Independent Variables
- **Clustering method:** {Random baseline, SentenceBERT k-means, Manual ground truth}
- **k value:** {3, 5, 7, 10}

### Dependent Variables
- **Primary:** Intra-family cosine similarity (target ≥60%)
- **Secondary:** Silhouette score (target >0.4)

### Controlled Variables
- Feature extraction protocol (H-M1 validated)
- Benchmark sample (fixed 20 benchmarks from H-M1)
- Embedding model (SentenceBERT all-MiniLM-L6-v2)
- Distance metric (cosine via normalized embeddings)

### Procedure
```python
# Pseudo-code
for k in [3, 5, 7, 10]:
    embeddings = SentenceBERT.encode(feature_strings)  # 20 x 384
    embeddings = normalize(embeddings, axis=1)         # L2 norm
    
    # SentenceBERT k-means (median over 10 seeds)
    kmeans_results = []
    for seed in range(10):
        labels = KMeans(n_clusters=k, init='k-means++', random_state=seed).fit_predict(embeddings)
        silhouette = silhouette_score(embeddings, labels, metric='cosine')
        intra_sim = compute_intra_family_similarity(embeddings, labels)
        kmeans_results.append({'silhouette': silhouette, 'similarity': intra_sim})
    
    median_result = median(kmeans_results)
    
    # Random baseline (median over 10 trials)
    random_results = []
    for trial in range(10):
        random_labels = random_assignment(n=20, k=k)
        random_sim = compute_intra_family_similarity(embeddings, random_labels)
        random_results.append(random_sim)
    
    median_random = median(random_results)
    
    # Manual clustering (ground truth)
    manual_labels = manual_cluster_by_task_type(benchmarks)  # Expert grouping
    manual_sim = compute_intra_family_similarity(embeddings, manual_labels)
    
    # Log: k, median_silhouette, median_similarity, random_similarity, manual_similarity

# Select best k: highest silhouette while maintaining similarity ≥60%
```

### Success Criteria (Gate Check)
1. **Primary (Gate):** Best k achieves intra-family similarity ≥60%
2. **Secondary:** Silhouette score >0.4 for best k
3. **Validation:** SentenceBERT similarity significantly exceeds random baseline (t-test p<0.05)

### Failure Response
- **Similarity 55-60%:** SCOPE - accept with caveat, label families as "weak coverage patterns"
- **Similarity 50-55%:** PIVOT - try hierarchical clustering (agglomerative) or USE embeddings
- **Similarity <50%:** EXPLORE - feature engineering (weight task type higher, add task-modality interaction)

---

## Evaluation Metrics

### Primary Metric: Intra-Family Similarity
**Formula:**
```
For each family F:
  mean_similarity_F = mean(cosine_similarity(e_i, e_j) for all i,j in F where i≠j)

Overall intra-family similarity = mean(mean_similarity_F for all families)
```

**Threshold:** ≥60%
**Interpretation:** If ≥60%, clustering captures meaningful structure (design constraints create groupings).

### Secondary Metric: Silhouette Score
**Formula:** Sklearn `silhouette_score(embeddings, labels, metric='cosine')`

**Threshold:** >0.4
**Interpretation:** Measures cluster separation. >0.4 = reasonable structure.

### Diagnostics
1. **Silhouette plot:** Visualize per-sample silhouette coefficients
2. **Family interpretability:** Check if families align with task types (e.g., "vision-classification" cluster contains ImageNet, MNIST, CIFAR-10)
3. **Confusion matrix:** Compare SentenceBERT clusters to manual ground truth (adjusted Rand index)

---

## Computational Requirements

### Hardware
- **CPU:** 4 cores (k-means multi-threaded)
- **RAM:** 4 GB
- **GPU:** Optional (SentenceBERT encoding faster on GPU but not required for 20 samples)

### Runtime Estimate
- SentenceBERT encoding: <10 sec (20 samples)
- K-means (10 seeds × 4 k values): ~30 sec
- Total: **<5 minutes**

### Dependencies
```
sentence-transformers==2.2.0
scikit-learn==1.3.0
numpy==1.24.0
pandas==2.0.0
matplotlib==3.7.0
```

---

## Risk Mitigation

### Risk R4: Weak Clustering Signal (from Phase 2B)
**Mitigation:**
1. **Prevention:** Try multiple k values (3-10), select best via silhouette score
2. **Detection:** If all k produce similarity <55%, weak signal confirmed
3. **Response:**
   - PIVOT: Hierarchical clustering (agglomerative with cosine distance)
   - PIVOT: Alternative embeddings (USE, SciBERT)
   - EXPLORE: Feature engineering (add task-modality interaction, weight task higher)

### Additional Risks
**R-H2-1: SentenceBERT embeddings don't capture design constraint similarity**
- **Mitigation:** Compare to manual clustering (ground truth). If ARI >0.6, embeddings valid.
- **Response:** Try SciBERT (scientific text specialist) or USE (Universal Sentence Encoder)

**R-H2-2: 20 benchmarks too small for stable clustering**
- **Mitigation:** Use median over 10 k-means seeds (reduce initialization noise)
- **Response:** If silhouette variance >0.15, acknowledge instability but proceed (H-M3 extends to 50-100 benchmarks)

---

## Output Artifacts

### Figures (Required)
1. **k_selection_plot.png:** k vs intra-family similarity (with ≥60% threshold line)
2. **silhouette_plot.png:** Silhouette coefficients for best k
3. **cluster_visualization.png:** 2D PCA projection of embeddings colored by cluster
4. **baseline_comparison.png:** SentenceBERT vs random vs manual similarity

### Data Files
1. **embeddings.npy:** SentenceBERT embeddings (20 × 384)
2. **cluster_assignments.csv:** Benchmark ID, k={3,5,7,10} cluster labels, best_k label
3. **metrics.json:** Silhouette scores, intra-family similarities for all k values

### Report
- **04_validation.md:** Gate result (PASS/FAIL), intra-family similarity scores, family interpretability analysis

---

## Implementation Pseudo-Code

```python
# Step 1: Load H-M1 validated features
benchmarks = pd.read_csv('experiments/h-m1/data/h-m1/sampled_benchmarks.csv')
feature_strings = [f"task: {row.task}, modality: {row.modality}, size: {categorize_size(row.size)}" 
                   for _, row in benchmarks.iterrows()]

# Step 2: Encode with SentenceBERT
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(feature_strings)  # 20 x 384
embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)  # L2 normalize

# Step 3: K-means sweep
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

results = {}
for k in [3, 5, 7, 10]:
    # SentenceBERT k-means (10 seeds)
    kmeans_trials = []
    for seed in range(10):
        km = KMeans(n_clusters=k, init='k-means++', random_state=seed, n_init=10)
        labels = km.fit_predict(embeddings)
        sil = silhouette_score(embeddings, labels, metric='cosine')
        intra_sim = compute_intra_family_similarity(embeddings, labels)
        kmeans_trials.append({'silhouette': sil, 'similarity': intra_sim, 'labels': labels})
    
    # Median trial
    median_trial = sorted(kmeans_trials, key=lambda x: x['similarity'])[5]
    
    # Random baseline
    random_sims = [compute_intra_family_similarity(embeddings, np.random.randint(0, k, 20)) 
                   for _ in range(10)]
    median_random = np.median(random_sims)
    
    results[k] = {
        'kmeans_similarity': median_trial['similarity'],
        'kmeans_silhouette': median_trial['silhouette'],
        'random_similarity': median_random,
        'labels': median_trial['labels']
    }

# Step 4: Select best k (highest silhouette with similarity ≥60%)
best_k = max([k for k, v in results.items() if v['kmeans_similarity'] >= 0.60], 
             key=lambda k: results[k]['kmeans_silhouette'])

# Step 5: Gate check
gate_similarity = results[best_k]['kmeans_similarity']
gate_silhouette = results[best_k]['kmeans_silhouette']

if gate_similarity >= 0.60 and gate_silhouette > 0.40:
    print("GATE: PASS")
else:
    print("GATE: FAIL")

# Step 6: Family interpretability
cluster_labels = results[best_k]['labels']
for family_id in range(best_k):
    family_benchmarks = benchmarks[cluster_labels == family_id]
    print(f"Family {family_id}: {family_benchmarks['task'].value_counts().to_dict()}")
```

---

## Validation Checklist

- [ ] Intra-family similarity ≥60% for best k
- [ ] Silhouette score >0.40 for best k
- [ ] SentenceBERT similarity significantly exceeds random baseline (t-test p<0.05)
- [ ] Families interpretable (align with task types or modality groups)
- [ ] All 4 required figures generated
- [ ] 04_validation.md report written with gate decision

---

## Next Steps (if H-M2 PASS)

1. **Route to H-M3:** Historical prediction test (2022→2023-2024)
2. **Dataset Expansion:** Extend from 20 to 50-100 benchmarks for H-M3
3. **Family Refinement:** Label coverage families based on H-M2 clustering (e.g., "vision-classification", "language-QA")

---

**Generated:** 2026-08-25  
**Workflow:** Phase 2C (Experiment Design)  
**Status:** Complete  
**Next Phase:** Phase 3 (Implementation Planning)
