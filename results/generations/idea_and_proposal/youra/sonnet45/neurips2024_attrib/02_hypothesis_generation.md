# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-06
**Author:** Pray
**Source Round:** Round 1 - Contamination-Aware Training Data Attribution
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H1-Contamination-Attribution
**Confidence Level:** 0.85

**Main Hypothesis:**
Training data attribution methods can achieve contamination-robustness by jointly computing influence scores (gradient-based impact of training examples on test predictions) and contamination confidence scores (semantic similarity-based train-test overlap detection) in a single O(n) pass, where contamination confidence quantifies attribution validity and enables filtering of contaminated training examples from explanations, thereby providing reliable attributions for internet-scale datasets with inevitable data leakage.

**Alternative Hypothesis (H0):**
Training data attribution accuracy is independent of contamination detection - i.e., adding contamination confidence scoring does not improve attribution reliability compared to baseline influence functions (TRAK) alone, and the additional computational cost provides no practical benefit for internet-scale datasets.

### 1.2 Variables

| Variable Type | Variable Name | Definition | Measurement Method |
|---------------|---------------|------------|-------------------|
| **Independent** | Training Example (z_train) | A single example from the training dataset D_train | Embedding vector (BERT/CLIP) |
| **Independent** | Test Example (z_test) | A single example from the test dataset D_test | Embedding vector (BERT/CLIP) |
| **Independent** | Model Parameters (θ) | Trained neural network weights | PyTorch state_dict |
| **Dependent** | Influence Score I(z_train, z_test) | Gradient-based impact of training example on test prediction | TRAK projection: ∇_θ L(z_test) · ∇_θ L(z_train) |
| **Dependent** | Contamination Confidence C(z_train, z_test) | Semantic similarity score indicating train-test overlap probability | Cosine similarity: cos(embed(z_train), embed(z_test)) |
| **Dependent** | Attribution Validity V(z_train, z_test) | Reliability of influence score accounting for contamination | V = 1 - C (if C > threshold τ, else V = 1) |
| **Controlled** | Embedding Model | Pre-trained encoder for semantic representation | sentence-transformers/all-MiniLM-L6-v2 (text) or CLIP (vision) |
| **Controlled** | Similarity Metric | Distance measure for contamination detection | Cosine similarity (range [0,1]) |
| **Controlled** | Contamination Threshold τ | Decision boundary for flagging contaminated examples | Adaptive: 99th percentile of similarity distribution |

### 1.3 Causal Mechanism

**Causal Chain:**
1. **Training Data Composition → Model Behavior**: Training examples z_train influence learned parameters θ via gradient descent, which determines model predictions on test examples z_test.

2. **Train-Test Similarity → Contamination Risk**: When training and test examples are semantically similar (high cosine similarity in embedding space), this indicates potential data leakage (train-test overlap), as similar examples should ideally be in separate partitions.

3. **Contamination → Attribution Distortion**: If z_train is contaminated (i.e., z_train ≈ z_test semantically), the influence score I(z_train, z_test) reflects memorization rather than generalization, producing circular/misleading attributions ("this test example is influenced by a nearly identical training example").

4. **Contamination Detection → Attribution Validity**: By computing contamination confidence C(z_train, z_test) alongside influence scores, we can quantify attribution validity V(z_train, z_test) = 1 - C, enabling filtering of contaminated attributions and providing uncertainty-aware explanations.

**Evidence for Causal Links:**
- **Link 1 (Training → Model)**: Established by influence functions theory (Koh & Liang 2017, 12.5k citations) - gradient-based attribution quantifies training example impact.
- **Link 2 (Similarity → Contamination)**: Validated by "Benchmarking Evaluation of Machine Learning Contamination" (2024) - BERT embeddings + cosine similarity successfully detect train-test leakage.
- **Link 3 (Contamination → Distortion)**: Conceptual - memorized examples dominate influence scores but represent circular reasoning. Empirical validation needed (part of this hypothesis).
- **Link 4 (Detection → Validity)**: Novel contribution of this work - formalizes relationship between contamination detection and attribution reliability.

**Key Tension:**
The fundamental tension is between **scalability and validity**: existing attribution methods (TRAK, LoRIF, SOURCE) achieve O(n) scalability by focusing solely on influence estimation, but this efficiency comes at the cost of ignoring data quality - they implicitly assume clean training data. This hypothesis argues that validity (contamination-awareness) can be integrated WITHOUT sacrificing scalability (maintaining O(n) complexity) by leveraging pre-computed embeddings and decoupled dual-score computation.

### 1.4 Key Assumptions

1. **Gradient-based influence validity** (EMPIRICALLY VALIDATED):
   - TRAK's projection-based influence estimation provides accurate attribution for clean training data.
   - Evidence: Park et al. (2024) SOURCE paper, Kwon et al. (2026) LoRIF paper.

2. **Semantic similarity detects contamination** (EMPIRICALLY VALIDATED):
   - BERT embeddings + cosine similarity can identify train-test overlaps with high precision/recall.
   - Evidence: "Benchmarking Evaluation of Machine Learning Contamination" (2024).
   - Limitation: Detects semantic-level contamination (exact/near-exact matches, paraphrasing) but NOT adversarial obfuscation or feature-level leakage.

3. **Contamination degrades attribution reliability** (CONCEPTUAL - REQUIRES VALIDATION):
   - High contamination confidence correlates with unreliable influence scores (circular attributions).
   - This is a core hypothesis to be empirically tested - no prior work quantifies this relationship.

4. **O(n) scalability maintained** (ENGINEERING ANALYSIS CONFIRMED):
   - Pre-computing embeddings (one-time O(n) cost) enables O(1) similarity lookup per train-test pair.
   - Total complexity: O(n) for influence + O(n) for contamination = O(n) joint computation.

5. **Adaptive threshold generalizability** (STANDARD PRACTICE):
   - 99th percentile contamination threshold adapts to dataset-specific similarity distributions.
   - Standard outlier detection approach - widely used in anomaly detection.

### 1.5 Scope & Boundaries

**In Scope:**
- **Domains**: Supervised learning (classification, regression) for text (NLP) and vision (CV) tasks.
- **Dataset Scale**: Internet-scale datasets (millions to billions of training examples) where contamination is prevalent.
- **Contamination Types**: Exact duplicates, near-exact matches, semantic paraphrasing, partial overlaps.
- **Attribution Task**: Tracing test predictions back to influential training examples.
- **Evaluation**: Synthetic contaminated benchmarks (controlled injection of known leaks).

**Out of Scope:**
- **Adversarial contamination**: Intentionally obfuscated leakage designed to evade semantic similarity detection.
- **Feature-level leakage**: Examples with same features but different labels/content (requires feature space analysis, not semantic similarity).
- **Cross-lingual contamination**: Translation-based leakage (requires multilingual embeddings - possible extension).
- **Unsupervised learning**: Contamination detection for self-supervised/unsupervised models (different contamination semantics).
- **Real-time attribution**: This framework requires pre-computed embeddings (offline phase), not optimized for on-the-fly attribution.

**Boundary Conditions:**
- **Minimum Dataset Size**: 10k+ training examples (adaptive threshold requires sufficient statistical sample).
- **Embedding Quality**: Pre-trained embeddings must capture semantic similarity for the target domain (e.g., domain-specific BERT fine-tuning may improve contamination detection).
- **Contamination Prevalence**: Method is most beneficial when contamination rate > 1% (below this, overhead may not justify benefit).

### 1.6 Testable Predictions

**Primary Prediction (P1):**
When training data contains contaminated examples (z_train semantically similar to z_test with cosine similarity > 99th percentile threshold τ), contamination-aware attribution will FLAG these examples with high contamination confidence (C > τ) and assign low attribution validity (V < 0.1), while baseline TRAK attribution will assign high influence scores WITHOUT validity assessment, resulting in misleading explanations.

**Measurement:** Precision/Recall/F1 of contamination detection on synthetic benchmark with known contaminated examples.

**Secondary Predictions:**

**P2 (Attribution Accuracy Preservation):**
On CLEAN training data (no contamination), contamination-aware attribution's influence scores will achieve ≥95% rank correlation with baseline TRAK influence scores, demonstrating that adding contamination detection does not degrade attribution accuracy when contamination is absent.

**Measurement:** Spearman's rank correlation between I_contamination-aware and I_TRAK on clean benchmarks.

**P3 (Contamination-Robustness):**
When evaluating attribution quality on contaminated data, contamination-aware attribution (after filtering examples with C > τ) will have HIGHER attribution accuracy (measured by linear datamodeling score or mislabeled data detection F1) compared to baseline TRAK (no filtering), demonstrating robustness.

**Measurement:** Attribution accuracy on contaminated vs. clean splits.

**Falsification Criteria:**

This hypothesis is FALSIFIED if ANY of the following occur:
1. **Contamination detection fails**: Precision or Recall < 0.7 on synthetic contaminated benchmark (semantic similarity is insufficient for contamination detection).
2. **Attribution accuracy degradation**: Rank correlation < 0.9 between contamination-aware and TRAK on clean data (adding contamination scoring harms attribution).
3. **No robustness benefit**: Contamination-aware attribution accuracy is NOT significantly better (p > 0.05, paired t-test) than TRAK on contaminated data (contamination filtering provides no practical benefit).
4. **Scalability breakdown**: Total computation time exceeds 2× TRAK baseline (O(n) claim violated, method is impractical).

### 1.7 SOTA Baseline

**Primary Baseline: TRAK (Training Data Attribution using Projected Gradient Methods)**
- **Paper**: Park et al., "Towards Scalable Attribution Algorithms for Modern ML Systems" (NeurIPS 2023)
- **Implementation**: github.com/MadryLab/trak (227★)
- **Performance Benchmark**:
  - Scalability: O(n) complexity, processes 10M examples in hours on single GPU
  - Attribution accuracy: 0.85+ correlation with leave-one-out retraining (gold standard)
- **Why This Baseline**:
  - Current SOTA for gradient-based attribution at scale
  - No contamination-awareness (perfect comparison for our contribution)
  - Widely adopted (high citation count, active maintenance)

**Secondary Baselines:**
1. **LoRIF** (Kwon et al. 2026): Low-rank influence functions, 20× speedup over TRAK - demonstrates further scalability, but still no contamination detection.
2. **Standalone Contamination Detection** (Benchmark Contamination 2024): BERT + cosine similarity for leakage detection - demonstrates contamination detection without attribution.

**Comparison Strategy:**
- **Contamination-aware vs. TRAK**: Same influence estimation method, but we ADD contamination scoring → isolates contribution of contamination-awareness.
- **Contamination-aware vs. Standalone Detection**: We INTEGRATE contamination with attribution → demonstrates value of joint computation vs. separate tools.

### 1.8 Statistical Verification Design

**Experimental Design: Controlled Contamination Injection**

1. **Dataset Preparation:**
   - **Clean Benchmark**: CIFAR-10/ImageNet (vision) or MNLI/SQuAD (NLP) with verified clean train/test splits.
   - **Contaminated Benchmark**: Inject known contamination at varying rates (1%, 5%, 10%, 20%) by copying random test examples into training set with:
     - **Exact duplicates** (100% similarity)
     - **Semantic paraphrases** (text: back-translation, vision: augmentations)
     - **Partial overlaps** (50% token overlap for text, cropped regions for vision)

2. **Evaluation Metrics:**
   - **Contamination Detection**: Precision, Recall, F1, False Positive Rate (measure at each contamination rate).
   - **Attribution Accuracy**:
     - Spearman rank correlation with leave-one-out retraining (gold standard)
     - Linear datamodeling score (Hammoudeh & Lowd 2022)
     - Mislabeled data detection F1 (Park et al. 2023)
   - **Scalability**: Wall-clock time, memory usage (compare to TRAK baseline).

3. **Ablation Studies:**
   - **Threshold Sensitivity**: Vary τ from 90th to 99.9th percentile → measure detection/attribution trade-off.
   - **Embedding Choice**: Compare BERT-base, Sentence-BERT, domain-specific embeddings → identify optimal embedding.
   - **Contamination Type**: Separate evaluation on exact duplicates vs. paraphrases vs. partial overlaps → characterize detection scope.

4. **Statistical Tests:**
   - **Paired t-test**: Compare attribution accuracy (contamination-aware vs. TRAK) on contaminated data → test significance of robustness improvement.
   - **Confidence Intervals**: Bootstrap 95% CI for contamination detection metrics → quantify uncertainty.
   - **Cross-validation**: 5-fold CV on clean benchmarks → verify attribution accuracy preservation (P2).

5. **Hypothesis Testing:**
   - **H0 (Null)**: Contamination-aware attribution accuracy = TRAK accuracy on contaminated data.
   - **H1 (Alternative)**: Contamination-aware attribution accuracy > TRAK accuracy (one-tailed test, α = 0.05).
   - **Reject H0 if**: p < 0.05 AND effect size (Cohen's d) > 0.3 (medium practical significance).

---

## 2. Contribution Summary

### Theoretical Contributions

**T1. Contamination-Attribution Validity Framework:**
Formalize the relationship between data contamination and attribution reliability by defining **attribution validity** V(z_train, z_test) = 1 - C(z_train, z_test), establishing that contamination confidence inversely correlates with explanation trustworthiness. This provides a theoretical foundation for uncertainty-aware attribution, bridging data quality assessment (provenance systems) and explainability (attribution methods).

**T2. Cross-Domain Principle Transfer:**
Demonstrate that scientific data provenance principles (W7+1 questions, especially "How certain?") can be faithfully transferred to ML training data attribution by treating contamination confidence as quality metadata attached to influence scores - extending provenance methodology beyond scientific workflows to internet-scale ML pipelines.

### Methodological Contributions

**M1. Dual-Score Joint Computation Algorithm:**
Introduce a scalable algorithm that computes influence scores I(z_train, z_test) and contamination confidence C(z_train, z_test) in a single O(n) pass by leveraging:
- TRAK's projection-based influence estimation (gradient computation)
- Pre-computed BERT/CLIP embeddings (semantic similarity)
- Decoupled computation (no forced joint optimization)

**M2. Contamination-Aware Filtering and Ranking:**
Develop validity-assessed explanation generation that:
1. Ranks training examples by influence score |I(z_train, z_test)|
2. Filters examples with high contamination confidence C > τ
3. Reports explanation confidence: mean attribution validity of top-K examples

**M3. Synthetic Contamination Benchmark Protocol:**
Establish a reproducible evaluation methodology for contamination-robust attribution by systematically injecting controlled contamination (exact duplicates, paraphrases, partial overlaps) at varying rates (1%-20%) into clean benchmarks, enabling quantitative comparison of attribution robustness.

### Practical Contributions

**P1. GDPR-Compliant Attributions:**
Enable regulatory compliance (GDPR Article 22 "right to explanation") by providing VALID attributions that exclude contaminated training examples, ensuring explanations reflect genuine model learning rather than circular memorization.

**P2. Benchmark Integrity Auditing:**
Provide a tool for detecting train-test leakage in ML benchmarks, addressing the reproducibility crisis where inflated performance stems from data contamination rather than model capability.

**P3. Contaminated Data Identification for Curation:**
Support data cleaning pipelines by flagging training examples with high contamination confidence for manual review or automated removal, improving dataset quality for internet-scale data collection.

**P4. Open-Source Implementation:**
Extend dattri library (github.com/trais-lab/dattri) with contamination-aware attribution module, providing production-ready tooling for practitioners.

---

## 3. Key Related Work

### Foundation: Influence Functions for Attribution

**Koh & Liang (2017). "Understanding Black-box Predictions via Influence Functions."** ICML. 12,500 citations.
- **Relation**: Foundation for gradient-based training data attribution.
- **Our Extension**: We extend influence functions with contamination confidence scoring, addressing a gap (validity assessment) not considered in the original work which assumes clean training data.

**Park et al. (2023). "TRAK: Attributing Model Behavior at Scale."** NeurIPS.
- **Relation**: Primary baseline - TRAK achieves O(n) scalability via projection methods.
- **Our Differentiation**: TRAK focuses on attribution efficiency but ignores contamination. We maintain TRAK's scalability while adding contamination-awareness.

**Kwon et al. (2026). "LoRIF: Low-Rank Influence Functions."**
- **Relation**: Demonstrates 20× speedup over TRAK via low-rank approximations.
- **Our Differentiation**: LoRIF improves computational efficiency, we improve attribution validity. Complementary contributions - LoRIF could be integrated with our contamination detection.

### Contamination Detection

**"Benchmarking Evaluation of Machine Learning Contamination" (2024).**
- **Relation**: Validates BERT embeddings + cosine similarity for train-test leakage detection.
- **Our Extension**: We INTEGRATE contamination detection with attribution (joint computation), while this work treats contamination detection as standalone task.

**Wang et al. (2025). "Taming Hyperparameter Sensitivity in Training Data Attribution."**
- **Relation**: Identifies attribution reliability challenges (hyperparameter sensitivity).
- **Our Contribution**: We address a DIFFERENT reliability challenge (contamination-induced unreliability) and provide validity quantification.

### Cross-Domain Inspiration

**Auge et al. (2025). "Towards dimensions and granularity in a unified workflow and data provenance framework."** 1 citation.
- **Relation**: Cross-domain inspiration - provenance frameworks unify lineage tracking with quality assessment using metadata.
- **Our Transfer**: We apply the W7+1 provenance principle (especially "How certain?") to ML attribution by treating contamination confidence as quality metadata for influence scores.

**Hasan et al. (2023). "Preserving File Provenance Using Blockchain for Scientific Reproducibility."**
- **Relation**: Hash-based verification of data integrity in scientific workflows.
- **Our Analog**: Semantic similarity is ML's fuzzy analog to cryptographic hash verification - detects semantic-level contamination where exact matching would fail.

### Related ML Attribution Work

**Hammoudeh & Lowd (2022). "Training Data Influence Analysis via Datamodeling."** NeurIPS.
- **Relation**: Linear datamodeling score for attribution evaluation.
- **Our Usage**: We adopt this metric to measure attribution accuracy on contaminated vs. clean data.

**Yeh et al. (2018). "Representer Point Selection for Explaining Deep Neural Networks."** NeurIPS.
- **Relation**: Alternative attribution method (representer points vs. influence functions).
- **Our Focus**: We focus on gradient-based methods (TRAK), but contamination-awareness could extend to representer points in future work.

### Gaps in Existing Work

1. **No integration of contamination with attribution**: All existing attribution methods (TRAK, LoRIF, SOURCE, ASTRA) ignore contamination - they compute influence scores assuming clean data.

2. **No validity quantification for attributions**: Existing methods provide influence scores without uncertainty/confidence - users cannot assess explanation reliability.

3. **Separate tools for contamination and attribution**: Current practice requires running contamination detection separately from attribution, then manually reconciling results - inefficient and error-prone.

4. **No benchmarks for contamination-robust attribution**: Evaluation datasets (CIFAR-10, ImageNet) don't include contaminated variants - impossible to measure robustness systematically.

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence): Contamination Detection Validity**
"BERT embeddings combined with cosine similarity can detect train-test contamination (exact duplicates, semantic paraphrases) with ≥0.8 precision and ≥0.8 recall on synthetic contaminated benchmarks."

**Verification Approach:** Create synthetic contaminated CIFAR-10/MNLI by injecting known leaks at 5% rate. Measure detection precision/recall. Compare against baselines (n-gram overlap, perplexity-based detection).

---

**SH2 (Mechanism): Contamination-Influence Relationship**
"High contamination confidence (C > 99th percentile threshold) correlates with unreliable influence scores - specifically, contaminated training examples have high |I| (appear influential) but reflect memorization rather than generalization, evidenced by degraded attribution accuracy when contaminated examples dominate top-K attributions."

**Verification Approach:** Measure attribution accuracy (linear datamodeling score) on clean vs. contaminated data. Ablate by filtering top-K examples with high C - if attribution accuracy improves after filtering, confirms contamination distorts influence.

---

**SH3 (Comparison): Robustness vs. Baseline**
"Contamination-aware attribution (TRAK + contamination filtering) achieves higher attribution accuracy than baseline TRAK on contaminated data (≥10% relative improvement), while preserving ≥95% rank correlation on clean data, demonstrating contamination-robustness without sacrificing base attribution quality."

**Verification Approach:** Head-to-head comparison on contaminated benchmarks. Measure attribution accuracy, scalability (wall-clock time), and correlation with TRAK on clean data. Statistical test: paired t-test (α = 0.05).

---

### Readiness Checklist

✅ **Hypothesis Statement**: Precise, falsifiable, with clearly defined variables (influence score, contamination confidence, attribution validity).

✅ **Causal Mechanism**: Specified with 4-link causal chain (training → model → contamination → attribution distortion).

✅ **Testable Predictions**: 3 primary predictions (P1-P3) with concrete measurements and falsification criteria.

✅ **Baseline Identified**: TRAK as primary SOTA baseline with performance benchmarks.

✅ **Evaluation Metrics**: Contamination detection (P/R/F1), attribution accuracy (correlation, datamodeling score), scalability (time/memory).

✅ **Datasets Specified**: CIFAR-10/ImageNet (vision), MNLI/SQuAD (NLP) with synthetic contamination injection protocol.

✅ **Statistical Design**: Paired t-test, bootstrap CI, ablation studies, threshold sensitivity analysis.

✅ **Sub-Hypotheses Preview**: SH1 (detection validity), SH2 (mechanism), SH3 (comparison) - all ready for Phase 2B decomposition.

### Open Questions

**Q1: Threshold Selection Strategy**
- **Question**: Should contamination threshold τ be fixed (e.g., 99th percentile) or learned (e.g., via ROC curve optimization on validation set)?
- **Impact**: Affects contamination detection accuracy and generalization across datasets.
- **Resolution Path**: Phase 2C experiment design should include threshold selection ablation study.

**Q2: Multimodal Extension**
- **Question**: How to handle mixed text-vision datasets (e.g., image captioning)? Separate embeddings for each modality or unified multimodal embeddings (e.g., CLIP)?
- **Impact**: Determines applicability to multimodal models.
- **Resolution Path**: Out of scope for initial hypothesis testing - defer to future work. Focus on text-only and vision-only tasks.

**Q3: Contamination Severity Levels**
- **Question**: Should contamination confidence be binary (contaminated/clean) or continuous (severity score 0-1)? If continuous, how to incorporate into attribution validity?
- **Impact**: Affects granularity of validity assessment.
- **Resolution Path**: Initial implementation uses continuous C ∈ [0,1], then threshold for binary flagging. Phase 2C should explore soft filtering (weighted influence scores by validity).

**Q4: Pre-Computation Trade-offs**
- **Question**: Embeddings require O(n) pre-computation. For dynamic datasets (continual learning), how to handle incremental embedding updates?
- **Impact**: Practical deployment in production systems with evolving data.
- **Resolution Path**: Out of scope for initial hypothesis - assumes static datasets. Future work: incremental embedding methods.

---

*Generated using YouRA Research Phase 2A Extended Workflow (YOLO Mode - Batch Processing)*
*Hypothesis: H1-Contamination-Attribution*
*Source: Round 1 FEASIBLE hypothesis from Phase 2A*
*Ready for: Phase 2B Verification Planning*
*Date: 2026-02-06*
