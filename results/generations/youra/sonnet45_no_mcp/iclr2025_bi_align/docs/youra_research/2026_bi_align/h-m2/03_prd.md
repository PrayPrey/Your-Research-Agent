# Product Requirements Document (PRD)
# Hypothesis: H-M2 - Embedding Space Clustering Analysis

**Version:** 1.0  
**Date:** 2026-04-19  
**Hypothesis ID:** h-m2  
**Hypothesis Type:** MECHANISM  
**Gate Type:** SHOULD_WORK

---

## 1. Executive Summary

### 1.1 Product Vision
Validate geometric structure in RLHF preference data by demonstrating that rejected responses form distinct clusters in semantic embedding space with statistically significant separation from chosen responses.

### 1.2 Success Criteria
- **Primary Gate:** MANOVA effect size (Cohen's d) ≥ 0.5 (medium-to-large clustering effect)
- **Secondary:** Visual confirmation of non-random clustering in PCA 2D projection
- **Baseline Comparison:** Cohen's d > 0.3 (exceeds random distribution threshold)

### 1.3 Core Hypothesis
Under semantic embedding space representation, if we extract embeddings from 160K+ HH-RLHF chosen/rejected pairs using pretrained encoders (RoBERTa-base), then rejected responses will form distinct clusters (not random distribution) with MANOVA effect size d ≥ 0.5, because aggregated human judgments create high-density sampling of alignment failure space.

---

## 2. Problem Statement

### 2.1 Research Question
Do rejected responses in HH-RLHF exhibit geometric structure (non-random clustering) when represented in pretrained semantic embedding space?

### 2.2 Current Gap
Prior hypothesis (h-m1) validated annotation consistency (κ=0.724), but did not test whether this consistency translates to geometric structure in embedding space.

### 2.3 Impact
This validation determines whether geometric manifold framing is viable for downstream multi-dimensional analysis (H-M3, H-M4). Failure would necessitate alternative approaches or hypothesis abandonment.

---

## 3. Target Users & Stakeholders

### 3.1 Primary Users
- Research team conducting geometric alignment failure analysis

### 3.2 Stakeholders
- Prerequisite: h-m1 (annotation consistency validation - COMPLETED, κ=0.724)
- Downstream hypotheses: h-m3 (multi-dimensional structure), h-m4 (encoder invariance)

---

## 4. Data Specification

### 4.1 Primary Dataset

**Dataset:** HH-RLHF harmless subset  
**Source:** Hugging Face Datasets (Anthropic/hh-rlhf)  
**URL:** https://huggingface.co/datasets/Anthropic/hh-rlhf  
**Size:** 160K+ chosen/rejected response pairs  
**Splits:** Full dataset (no train/test split needed for embedding analysis)

**Loading Method:**
```python
from datasets import load_dataset
dataset = load_dataset("Anthropic/hh-rlhf", split="train")
harmless_data = dataset.filter(lambda x: 'harmless' in x.get('source', ''))
```

### 4.2 Preprocessing Requirements

1. Extract text from chosen/rejected pairs
2. Tokenize using RoBERTa tokenizer (max_length=512, truncation=True)
3. No data augmentation (preserve original semantic content)

**Statistics:**
- Total pairs: ~160K (harmless subset)
- Average response length: ~100-200 tokens
- Label distribution: 50% chosen, 50% rejected

### 4.3 Data Outputs

- Embedding matrices: chosen_embeddings.npy (N×768), rejected_embeddings.npy (N×768)
- PCA projections: pca_2d_projection.npy
- Statistical test results: manova_results.json
- Visualization artifacts: See Section 8 (Visualization Requirements)

---

## 5. Functional Requirements

### FR-1: Dataset Loading and Preprocessing
**Priority:** High  
**Description:** Load HH-RLHF harmless subset and prepare text for embedding extraction  
**Acceptance Criteria:**
- Successfully load 160K+ pairs from HuggingFace
- Filter for harmless subset
- Validate data integrity (no missing fields)

### FR-2: RoBERTa Embedding Extraction
**Priority:** High  
**Description:** Extract CLS token embeddings using pretrained RoBERTa-base model  
**Acceptance Criteria:**
- Load RoBERTa-base from HuggingFace Transformers
- Extract CLS embeddings (768-dimensional) for all responses
- Batch processing for memory efficiency (batch_size=32)
- Reproducible with fixed random seed (seed=42)

### FR-3: MANOVA Statistical Analysis
**Priority:** High  
**Description:** Compute multivariate analysis of variance to test group separation  
**Acceptance Criteria:**
- Calculate Cohen's d effect size for chosen vs rejected groups
- Compute F-statistic and p-value
- Output: effect size d, confidence interval, statistical significance

### FR-4: PCA Dimensionality Reduction
**Priority:** High  
**Description:** Apply PCA for 2D visualization of embedding space structure  
**Acceptance Criteria:**
- Reduce 768D embeddings to 2D projection
- Preserve variance information (report % variance explained)
- Generate scatter plot with chosen (blue) vs rejected (red) color coding

### FR-5: Baseline Comparison (Random Distribution)
**Priority:** Medium  
**Description:** Establish null hypothesis baseline using random label assignment  
**Acceptance Criteria:**
- Generate random binary labels with 50/50 distribution
- Compute Cohen's d for random baseline (expected ≈ 0.0)
- Compare proposed method against random baseline

---

## 6. Non-Functional Requirements

### NFR-1: Performance
- Embedding extraction: Complete in ≤3 hours for full 160K dataset
- GPU memory: ≤4GB (single GPU, RoBERTa-base)
- Batch processing to handle large dataset

### NFR-2: Reproducibility
- Fixed random seeds (seed=42)
- Version pinning: transformers==4.x, torch==2.x, scikit-learn==1.x
- Deterministic computation modes where applicable

### NFR-3: Scalability
- Support batch processing for memory-constrained environments
- Checkpoint intermediate results (embeddings saved to disk)

### NFR-4: Maintainability
- Modular code structure (separate modules for loading, embedding, analysis)
- Clear variable naming and function documentation
- Configuration file for hyperparameters

---

## 7. Evaluation Metrics

### 7.1 Primary Metric

**MANOVA Effect Size (Cohen's d)**
- **Calculation:** Mean difference between group centroids / pooled standard deviation
- **Threshold:** d ≥ 0.5 (medium-to-large effect)
- **Interpretation:**
  - d < 0.3: Small/negligible effect (random-like)
  - 0.3 ≤ d < 0.5: Small-to-medium effect
  - d ≥ 0.5: Medium-to-large effect (gate satisfied)

### 7.2 Secondary Metrics

**Visual Clustering Confirmation**
- PCA 2D scatter plot shows distinct chosen/rejected clusters
- Visual inspection confirms non-overlapping distributions

**F-statistic (MANOVA)**
- Statistical significance test (p-value < 0.05)
- Measures group separation in multivariate space

### 7.3 Baseline Comparison

**Random Classifier**
- Expected Cohen's d ≈ 0.0
- AUROC = 0.5 (random chance)
- Purpose: Demonstrate proposed method exceeds random baseline

---

## 8. Visualization Requirements

### 8.1 Mandatory Figure (Gate Evaluation)

**Gate Metrics Comparison Bar Chart**
- X-axis: Method (Random Baseline, RoBERTa Embeddings)
- Y-axis: Cohen's d effect size
- Threshold line at d = 0.5 (gate condition)
- Actual values displayed on bars

### 8.2 Additional Figures (Autonomous Generation)

**Figure 1: PCA 2D Scatter Plot**
- Chosen responses (blue points)
- Rejected responses (red points)
- First 2 principal components as axes
- Variance explained percentages on axis labels

**Figure 2: Effect Size Distribution**
- Histogram of per-dimension Cohen's d values across 768 embedding dimensions
- Shows distribution of separation strength

**Figure 3: Cumulative Variance Explained**
- PCA scree plot
- X-axis: Principal component number
- Y-axis: Cumulative variance explained (%)

**Figure 4: Embedding Space Heatmap**
- Distance matrix visualization for sample pairs
- Color intensity represents Euclidean distance

All figures saved to: `{hypothesis_folder}/figures/`

---

## 9. Model/Architecture Specification

### 9.1 Baseline Model

**Architecture:** Random Classifier  
**Type:** Statistical baseline  
**Purpose:** Null hypothesis (no structure)

**Configuration:**
- Random binary label assignment
- No trainable parameters
- Expected AUROC = 0.5, Cohen's d ≈ 0.0

### 9.2 Proposed Model

**Architecture:** RoBERTa-base Embedding Extractor  
**Type:** Pretrained encoder (no fine-tuning)  
**Source:** HuggingFace Transformers (`roberta-base`)

**Configuration:**
- Model: `RobertaModel.from_pretrained("roberta-base")`
- Tokenizer: `RobertaTokenizer.from_pretrained("roberta-base")`
- Embedding method: CLS token pooling (first token of last hidden state)
- Max sequence length: 512 tokens
- Batch size: 32

**Pseudo-code:**
```python
import torch
from transformers import RobertaTokenizer, RobertaModel

class EmbeddingClusteringAnalyzer:
    def __init__(self, model_name="roberta-base"):
        self.tokenizer = RobertaTokenizer.from_pretrained(model_name)
        self.model = RobertaModel.from_pretrained(model_name)
        self.model.eval()
    
    def extract_embeddings(self, texts):
        """Extract CLS token embeddings"""
        embeddings = []
        with torch.no_grad():
            for text in texts:
                inputs = self.tokenizer(text, return_tensors="pt", 
                                       max_length=512, truncation=True)
                outputs = self.model(**inputs)
                cls_embedding = outputs.last_hidden_state[:, 0, :].squeeze()
                embeddings.append(cls_embedding.numpy())
        return np.array(embeddings)
    
    def compute_manova_effect_size(self, chosen_emb, rejected_emb):
        """Compute Cohen's d for group separation"""
        mean_diff = np.mean(chosen_emb, axis=0) - np.mean(rejected_emb, axis=0)
        pooled_std = np.sqrt((np.var(chosen_emb, axis=0) + np.var(rejected_emb, axis=0)) / 2)
        cohens_d = np.mean(mean_diff / (pooled_std + 1e-8))
        return cohens_d
```

---

## 10. Training Protocol

**No Training Required** - This is an embedding extraction and statistical analysis experiment.

### 10.1 Embedding Extraction Protocol

1. Load RoBERTa-base pretrained model (frozen weights)
2. Extract CLS embeddings for all 160K+ chosen/rejected pairs
3. Save embeddings to disk (checkpoint)
4. Apply PCA dimensionality reduction for visualization
5. Compute MANOVA test statistics

### 10.2 Computational Requirements

- **Device:** Single GPU (CUDA)
- **GPU Memory:** ~4GB (RoBERTa-base)
- **Batch Size:** 32 (embedding extraction)
- **Estimated Time:** 2-3 hours for full dataset
- **Seeds:** Fixed seed=42 for reproducibility

---

## 11. Dependencies and Environment

### 11.1 Python Dependencies

```
torch>=2.0.0
transformers>=4.30.0
scikit-learn>=1.3.0
numpy>=1.24.0
scipy>=1.10.0
matplotlib>=3.7.0
seaborn>=0.12.0
datasets>=2.13.0
```

### 11.2 Hardware Requirements

- GPU: NVIDIA GPU with ≥4GB VRAM (Tesla T4, RTX 3060, or better)
- RAM: ≥16GB system memory
- Storage: ≥10GB free space (dataset + embeddings)

### 11.3 Environment Setup

- Python 3.10+
- CUDA 11.8+ (for GPU acceleration)
- Virtual environment (venv or conda)

---

## 12. Success Criteria Summary

| Criterion | Threshold | Type |
|-----------|-----------|------|
| MANOVA Effect Size (Cohen's d) | ≥ 0.5 | PRIMARY (Gate) |
| Visual Clustering | Distinct clusters in PCA | SECONDARY |
| Baseline Comparison | d > 0.3 | SECONDARY |
| Statistical Significance | p-value < 0.05 | SECONDARY |

**Gate Decision:**
- **PASS:** Cohen's d ≥ 0.5 → Proceed to h-m3 (multi-dimensional structure analysis)
- **FAIL (d < 0.3):** EXPLORE alternative encoders or ABANDON geometric framing

---

## 13. Risks and Mitigation

### Risk 1: Surface Pattern Dominance
**Description:** Embeddings may capture only lexical patterns, not semantic structure  
**Mitigation:** Compare against TF-IDF baseline (referenced in Phase 2C)  
**Owner:** Research team

### Risk 2: Encoder-Specific Artifacts
**Description:** Clustering may be RoBERTa-specific, not data-intrinsic  
**Mitigation:** Deferred to h-m4 (multi-encoder validation)  
**Owner:** Downstream hypothesis

### Risk 3: Computational Constraints
**Description:** 160K samples may exceed available GPU memory  
**Mitigation:** Batch processing with checkpointing  
**Owner:** Implementation team

---

## 14. Timeline and Milestones

**Note:** YouRA pipeline avoids time estimates per workflow principles. Focus on WHAT, not WHEN.

**Milestones:**
1. ✓ Phase 2C completed (experiment design)
2. → Phase 3 in progress (implementation planning)
3. → Phase 4 (coding and validation)
4. → Gate evaluation (MANOVA d ≥ 0.5)

---

## 15. Appendix

### 15.1 Related Hypotheses

**Prerequisites:**
- h-e1: Base-rate validation (COMPLETED, p=0.456)
- h-m1: Annotation consistency (COMPLETED, κ=0.724)

**Dependents:**
- h-m3: Multi-dimensional structure (pending h-m2 completion)
- h-m4: Encoder invariance (pending h-m3 completion)

### 15.2 References

- Phase 2C Experiment Brief: `02c_experiment_brief.md`
- Phase 2B Verification Plan: `02b_verification_plan.md` (Section 2.2, H-M2)
- Phase 2B Context: `02b_context.md`

---

*Generated by Phase 3 Implementation Planning (Step 2)*  
*Next: Architecture Design (Step 3)*
