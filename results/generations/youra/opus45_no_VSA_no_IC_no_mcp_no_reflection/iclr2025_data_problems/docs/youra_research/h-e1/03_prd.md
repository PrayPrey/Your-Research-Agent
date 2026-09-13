# Product Requirements Document: h-e1

**Hypothesis:** h-e1 - E5-large Embedding Similarity Computation
**Type:** EXISTENCE
**Gate:** MUST_WORK
**Date:** 2026-08-28

---

## 1. Executive Summary

Validate that E5-large embedding model can compute reliable cosine similarity scores between domain samples (The Pile) and task exemplars (MMLU), producing non-trivial variance across domains (std > 0.05).

---

## 2. Problem Statement

### 2.1 Context
The YouRA pipeline requires domain-task similarity scores as input features. Before building complex mechanisms, we must verify the foundational capability: can E5-large embeddings reliably differentiate domains based on task relevance?

### 2.2 Success Definition
- All 8 Pile domains produce valid similarity scores
- Cross-domain standard deviation > 0.05
- Reproducible across runs (variance < 5%)
- Statistically significant domain differences (ANOVA p < 0.05)

---

## 3. Functional Requirements

### FR-1: Data Loading
| ID | Requirement |
|----|-------------|
| FR-1.1 | Load The Pile subset: 8 domains, 1000 samples each |
| FR-1.2 | Load MMLU validation set as task exemplars |
| FR-1.3 | Cache processed data to `./data/h-e1/` |

### FR-2: Embedding Computation
| ID | Requirement |
|----|-------------|
| FR-2.1 | Load E5-large-v2 model from `intfloat/e5-large-v2` |
| FR-2.2 | Embed domain samples with "passage: " prefix |
| FR-2.3 | Embed task exemplars with "query: " prefix |
| FR-2.4 | Normalize all embeddings to unit vectors |

### FR-3: Similarity Computation
| ID | Requirement |
|----|-------------|
| FR-3.1 | Compute cosine similarity matrix [N_domain × N_task] |
| FR-3.2 | Aggregate mean similarity per sample |
| FR-3.3 | Compute per-domain mean scores |
| FR-3.4 | Calculate cross-domain standard deviation |

### FR-4: Baseline Comparisons
| ID | Requirement |
|----|-------------|
| FR-4.1 | Random embeddings baseline (replace E5 with random vectors) |
| FR-4.2 | Uniform sampling baseline (equal samples from all domains) |

### FR-5: Statistical Analysis
| ID | Requirement |
|----|-------------|
| FR-5.1 | Descriptive statistics: mean, std, min, max |
| FR-5.2 | ANOVA F-test across domains |
| FR-5.3 | Reproducibility check: 3 runs with different seeds |
| FR-5.4 | Generate visualization: domain similarity bar chart |

---

## 4. Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | GPU Memory | < 4 GB |
| NFR-2 | Execution Time | < 30 minutes |
| NFR-3 | Storage | < 2 GB |
| NFR-4 | Reproducibility | Variance < 5% |

---

## 5. Data Specifications

### 5.1 Input Data
| Dataset | Source | Size |
|---------|--------|------|
| The Pile | `monology/pile-uncopyrighted` | 8 domains × 1000 samples |
| MMLU | `cais/mmlu` validation | ~1500 questions |

### 5.2 Output Artifacts
| Artifact | Path | Format |
|----------|------|--------|
| Domain embeddings | `embeddings/domain_emb.pt` | PyTorch |
| Task embeddings | `embeddings/task_emb.pt` | PyTorch |
| Similarity matrix | `results/similarities.csv` | CSV |
| Domain scores | `results/domain_scores.json` | JSON |
| Analysis report | `results/h-e1_analysis.md` | Markdown |
| Bar chart | `figures/domain_similarity_bar.png` | PNG |

---

## 6. Success Criteria

| Criterion | Threshold | Priority |
|-----------|-----------|----------|
| Score computability | All 8 domains valid | P0 |
| Non-trivial variance | std > 0.05 | P0 |
| Reproducibility | Variance < 5% | P0 |
| Statistical significance | ANOVA p < 0.05 | P1 |

---

## 7. Dependencies

- Python 3.8+
- PyTorch with CUDA
- sentence-transformers
- HuggingFace datasets
- numpy, scipy, matplotlib

---

## 8. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| OOM | Batch size = 32 |
| HuggingFace download fail | Use cached datasets |
| Low variance | Fallback to BGE-large |
| MMLU format issues | Validate on 10 samples first |

---

## Document Status

**Status:** COMPLETE
**Phase 2C Reference:** 02c_experiment_brief.md
