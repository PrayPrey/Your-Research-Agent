# Product Requirements Document: H-M2

**Hypothesis:** Routing is robust to paraphrase (cosine ≥0.90) and keyword masking (<10% absolute drop)
**Type:** MECHANISM
**Date:** 2026-08-09
**Author:** Anonymous

---

## 1. Executive Summary

This PRD defines requirements for testing the robustness of the linear probe routing system validated in H-E1. The experiment evaluates whether instruction embeddings maintain routing consistency under perturbations (paraphrases and keyword masking).

**Key Deliverables:**
- Paraphrase generation pipeline using TextAttack/nlpaug
- Keyword masking with TF-IDF importance scoring
- Robustness evaluation metrics (cosine similarity, accuracy drop, routing consistency)

---

## 2. Problem Statement

H-E1 demonstrated that linear probes achieve 72.67% top-1 accuracy for adapter selection. However, robustness to input variations is unknown. Real-world instructions vary in wording while preserving intent. This experiment tests whether the routing remains stable under:
1. **Paraphrase variations** - same instruction, different wording
2. **Keyword masking** - removing task-indicative keywords

---

## 3. Goals and Objectives

### Primary Goals
1. Validate paraphrase cosine similarity ≥ 0.90
2. Validate keyword masking accuracy drop < 10%
3. Measure routing consistency across perturbations

### Success Criteria
| Metric | Threshold | Falsification |
|--------|-----------|---------------|
| Paraphrase Cosine | ≥ 0.90 | < 0.80 |
| Accuracy Drop | < 10% | > 20% |
| Routing Consistency | ≥ 85% | < 70% |

---

## 4. Data Specification

### 4.1 Primary Dataset
- **Name:** Open-Orca/FLAN
- **Source:** HuggingFace Datasets (streaming)
- **Test Set:** 450 samples from H-E1 validation split
- **Download:** Auto-download via HuggingFace (NO manual task needed)

### 4.2 Perturbation Types
| Type | Tool | Parameters |
|------|------|------------|
| WordNet Paraphrase | TextAttack WordNetAugmenter | pct_words_to_swap=0.3, n=5 |
| Embedding Paraphrase | TextAttack EmbeddingAugmenter | cosine≥0.8 |
| Keyword Masking (20%) | nlpaug TfIdfAug | aug_p=0.2 |
| Keyword Masking (50%) | nlpaug TfIdfAug | aug_p=0.5 |

---

## 5. Functional Requirements

### FR-1: Load H-E1 Artifacts
- Load trained linear probe from h-e1/probe_model.pkl
- Load MiniLM-L6-v2 encoder
- Load test dataset (450 samples)

### FR-2: Paraphrase Generation
- Generate 5 WordNet paraphrases per test sample
- Generate 3 embedding-based paraphrases per sample
- Store original-paraphrase pairs

### FR-3: Keyword Masking
- Implement TF-IDF keyword identification
- Mask 20% and 50% keyword ratios
- Preserve sentence structure

### FR-4: Embedding Comparison
- Compute cosine similarity between original and perturbed embeddings
- Track per-sample and aggregate statistics

### FR-5: Routing Evaluation
- Predict class for original and perturbed samples
- Calculate routing consistency (% same prediction)
- Calculate accuracy drop

### FR-6: Ablation Variants
| Variant | What It Tests |
|---------|---------------|
| WordNet Paraphrases | Synonym substitution robustness |
| Embedding Paraphrases | Counter-fitted neighbor robustness |
| Keyword Masking (20%) | Partial keyword removal |
| Keyword Masking (50%) | Aggressive keyword removal |
| Random Word Masking | Control baseline |

### FR-7: Visualization
- Gate metrics bar chart (cosine vs target, drop vs target)
- Cosine similarity distribution histogram
- Per-class robustness heatmap
- Failure case examples

---

## 6. Non-Functional Requirements

### NFR-1: Performance
- Process 450 samples × 5 paraphrases in < 10 minutes
- Memory usage < 8GB

### NFR-2: Reproducibility
- Fixed random seed (same as H-E1)
- Deterministic augmentation where possible

---

## 7. Dependencies

### 7.1 Python Packages
```
sentence-transformers>=2.2.0
textattack>=0.3.8
nlpaug>=1.1.11
scikit-learn>=1.0.0
joblib>=1.0.0
numpy>=1.21.0
matplotlib>=3.5.0
seaborn>=0.12.0
```

### 7.2 H-E1 Artifacts (Required)
- `h-e1/probe_model.pkl` - Trained LogisticRegression
- `h-e1/label_encoder.pkl` - Label mapping (optional)

### 7.3 External References
- TextAttack: https://github.com/QData/TextAttack
- nlpaug: https://github.com/makcedward/nlpaug
- ALIGN-Sim: https://huggingface.co/BridgeAI-Lab/ALIGN-Sim

---

## 8. Constraints and Assumptions

### Constraints
- Reuse H-E1 probe (no retraining)
- Test on same 450 samples for consistency

### Assumptions
- H-E1 artifacts are available and loadable
- TextAttack/nlpaug produce valid augmentations

---

## 9. Timeline and Milestones

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Setup | 0.5 day | Environment, artifact loading |
| Implementation | 1 day | Perturbation + evaluation code |
| Execution | 0.5 day | Run experiments, collect metrics |
| Analysis | 0.5 day | Figures, validation report |

---

*Generated for Phase 3 Implementation Planning*
