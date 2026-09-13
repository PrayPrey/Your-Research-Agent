# Product Requirements Document: H-E1
## Token Entropy and N-Sample Consistency Predictive Validity

**Hypothesis ID:** h-e1
**Type:** EXISTENCE
**Gate:** MUST_WORK
**Generated:** 2026-08-28

---

## 1. Executive Summary

Validate that token entropy and N-sample consistency individually predict factual correctness above chance (AUROC > 0.55) on TruthfulQA using LLaMA-2-7B. This EXISTENCE hypothesis establishes foundational evidence that uncertainty signals carry predictive information about hallucination.

**Success Criteria:**
- entropy_AUROC > 0.55
- consistency_AUROC > 0.55
- Both CI lower bounds > 0.50

**Failure Response:** ABANDON entire hypothesis chain.

---

## 2. Problem Statement

LLMs produce confident-sounding but factually incorrect outputs. We need validated uncertainty metrics that predict these failures. This experiment tests whether basic uncertainty signals (token entropy, response consistency) predict factual correctness better than random guessing.

---

## 3. Functional Requirements

### FR-1: Data Pipeline
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Load TruthfulQA generation split (817 questions) from HuggingFace | P0 |
| FR-1.2 | Extract question, best_answer, incorrect_answers fields | P0 |
| FR-1.3 | Cache dataset locally after first download | P1 |

### FR-2: Model Loading
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | Load LLaMA-2-7B from meta-llama/Llama-2-7b-hf | P0 |
| FR-2.2 | Use fp16 precision with device_map="auto" | P0 |
| FR-2.3 | Verify HuggingFace token with Meta access | P0 |

### FR-3: Token Entropy Computation
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | Generate response with greedy decoding, return logits | P0 |
| FR-3.2 | Compute Shannon entropy per token: -sum(p * log(p)) | P0 |
| FR-3.3 | Aggregate as mean entropy over generated tokens | P0 |

### FR-4: N-Sample Consistency Computation
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | Generate N=5 responses per question (temperature=1.0) | P0 |
| FR-4.2 | Encode responses with sentence-transformers/all-MiniLM-L6-v2 | P0 |
| FR-4.3 | Compute mean pairwise cosine similarity | P0 |

### FR-5: Ground Truth Labeling
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.1 | Compute BERTScore F1 between response and best_answer | P0 |
| FR-5.2 | Compute max BERTScore F1 with incorrect_answers | P0 |
| FR-5.3 | Label correct (0) if best_score > worst_score AND best_score >= 0.5 | P0 |

### FR-6: Evaluation
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-6.1 | Compute AUROC for entropy scores vs labels | P0 |
| FR-6.2 | Compute AUROC for (negated) consistency scores vs labels | P0 |
| FR-6.3 | Bootstrap 95% CI (n=1000) for both AUROCs | P0 |
| FR-6.4 | Generate ROC curve plots | P1 |

### FR-7: Output Artifacts
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-7.1 | Save scores.csv: question_id, entropy, consistency, label | P0 |
| FR-7.2 | Save metrics.json: AUROC values, CIs, sample counts | P0 |
| FR-7.3 | Save roc_curves.png: ROC visualization | P1 |

---

## 4. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-1 | Performance | Process 817 questions in < 6 hours |
| NFR-2 | Memory | Fit in 16GB VRAM (fp16 LLaMA-2-7B) |
| NFR-3 | Reproducibility | Fixed random seed (42) for bootstrap |
| NFR-4 | Storage | < 5GB total disk usage |

---

## 5. Data Specifications

### Input Data
- **Source:** HuggingFace `truthfulqa/truthful_qa` (generation split)
- **Size:** 817 questions
- **Fields:** question, best_answer, incorrect_answers

### Output Data
- **scores.csv:** Per-question scores and labels
- **metrics.json:** Aggregate evaluation metrics
- **roc_curves.png:** Visualization

---

## 6. Dependencies

### Python Packages
```
transformers>=4.30.0
datasets>=2.14.0
torch>=2.0.0
sentence-transformers>=2.2.0
bert-score>=0.3.13
scikit-learn>=1.3.0
scipy>=1.11.0
numpy>=1.24.0
matplotlib>=3.7.0
```

### External
- HuggingFace token with Meta LLaMA-2 access
- GPU with >= 16GB VRAM

---

## 7. Success Criteria Verification

| Criterion | Threshold | Pass Condition |
|-----------|-----------|----------------|
| Entropy AUROC | > 0.55 | roc_auc_score(labels, entropy) > 0.55 |
| Consistency AUROC | > 0.55 | roc_auc_score(labels, -consistency) > 0.55 |
| Statistical significance | CI lower > 0.50 | Bootstrap 2.5th percentile > 0.50 |

**Gate Decision:**
- PASS: Both conditions met → proceed to dependent hypotheses
- FAIL: Either condition unmet → ABANDON hypothesis chain

---

## 8. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| LLaMA access denied | Have backup model (Mistral-7B) |
| OOM on GPU | Use gradient checkpointing or batch size 1 |
| BERTScore slow | Use rescale_with_baseline=True, batch |
| Low signal | Threshold set conservatively at 0.55 |

---

**Document Status:** COMPLETE
**Ready for:** Architecture Design (Step 3)
