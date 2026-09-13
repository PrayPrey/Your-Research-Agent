# Product Requirements Document: H-M1 ProvenanceCache Implementation

**Date:** 2026-08-20  
**Hypothesis:** H-M1 (Provenance-Aware Tiered Eviction)  
**Target:** ≥5% accuracy gain vs H2O baseline at 25% cache budget on single-hop QA  
**Budget:** 2.5 implementation tiers (Tier 2 complexity)

---

## Executive Summary

Implement provenance-aware tiered KV cache eviction policy for Llama-2-7B on LongBench single-hop QA. Compare against H2O baseline to validate whether retrieval metadata (query/passage types + relevance scores) predicts cache utility better than accumulated attention scores.

**Core Value Proposition:**  
If retrieval relevance correlates with attention (H-E1 validated: ρ=0.612 for Contriever), then cache eviction can exploit provenance metadata to outperform attention-based baselines without overhead of attention tracking.

---

## Success Criteria

### Primary Gate (MUST_WORK)
- ProvenanceCache F1 ≥ H2O F1 × 1.05 at 25% cache budget
- Statistical significance: p < 0.05 (two-tailed t-test, n=200 per task)
- Failure → Phase 2A modification (adjust tiering policy or metadata)

### Secondary Metrics
- Cache composition analysis (% query / high-rel / low-rel tokens)
- Inference latency comparable to H2O (no >20% slowdown)
- Memory footprint ≤ H2O (no additional overhead)

### PoC Success
1. Code runs without error on 10-sample subset
2. ProvenanceCache F1 > Random eviction F1 (sanity check)

---

## Functional Requirements

### FR1: Baseline Implementation (H2O)
**Priority:** P0 (blocker)  
**Description:** Integrate H2O KV cache eviction from FMInference/H2O repository

**Acceptance Criteria:**
- Clone and adapt h2o_hf/ implementation for LongBench evaluation
- Support `heavy_ratio=0.125, recent_ratio=0.125` for 25% cache budget
- Enable `output_attentions=True` for attention score accumulation
- Verify eviction logic matches paper specification (sink + heavy-hitter + recent tiers)

**Implementation Notes:**
- Use FMInference/H2O as primary reference (official NeurIPS 2023 code)
- Modify `run_lm_eval_harness.py` for LongBench dataset integration
- Extract attention weights after each forward pass for heavy-hitter tracking

---

### FR2: ProvenanceCache Eviction Policy
**Priority:** P0 (blocker)  
**Description:** Implement three-tier eviction using retrieval provenance metadata

**Acceptance Criteria:**
- Tier 0: Query tokens (always retained)
- Tier 1: High-relevance passages (top-K by Contriever retrieval score)
- Tier 2: Low-relevance passages (diverse subset for contrastive evidence)
- Total budget: 25% of context length
- Eviction decisions use only provenance metadata (no attention tracking)

**Implementation Notes:**
- Provenance registration: Map token positions to (type, relevance_score) tuples
- Token types: {"query", "high_rel_passage", "low_rel_passage"}
- Relevance scores: Contriever similarity scores normalized to [0,1]
- Budget allocation: 50% high-rel, 50% low-rel (after query tokens)

---

### FR3: LongBench Dataset Integration
**Priority:** P0 (blocker)  
**Description:** Load and preprocess LongBench single-hop QA tasks

**Acceptance Criteria:**
- Load 4 tasks: narrativeqa, qasper, triviaqa, multifieldqa_en (200 samples each)
- Tokenize with Llama-2 tokenizer (left-padding for batch generation)
- Truncate contexts to 4096 tokens (Llama-2-7B max context length)
- Format as {"input": question, "context": document, "answers": [list]}

**Implementation Notes:**
- Use HuggingFace `datasets` library: `load_dataset('THUDM/LongBench', task_name, split='test')`
- Single-hop filtering: Use inherently single-hop tasks (narrativeqa, triviaqa) without additional filtering
- Preprocessing: Normalize whitespace, lowercase for F1 computation

---

### FR4: Contriever Retrieval Integration
**Priority:** P0 (blocker)  
**Description:** Generate provenance metadata using Contriever retrieval model

**Acceptance Criteria:**
- Load facebook/contriever model from HuggingFace
- For each question: retrieve top-K passages with relevance scores
- Tokenize retrieved passages and track token position → passage mapping
- Register provenance metadata before generation (query tokens + passage tokens with scores)

**Implementation Notes:**
- Contriever model: `facebook/contriever` or `facebook/contriever-msmarco`
- Passage chunking: Split long documents into 512-token passages with 128-token overlap
- Top-K retrieval: K=5 passages (top-3 as high-rel, bottom-2 as low-rel)
- Score normalization: Min-max scaling to [0,1] per query

---

### FR5: Evaluation Harness
**Priority:** P0 (blocker)  
**Description:** Compute F1 scores and comparison metrics across all conditions

**Acceptance Criteria:**
- Conditions: FullKV, H2O, ProvenanceCache, Random (4 total)
- Metrics: F1 score, Exact Match, cache compression ratio, latency, memory
- Statistical testing: Two-tailed t-test for F1 comparison (ProvenanceCache vs H2O)
- Result format: CSV with per-question scores + aggregated statistics

**Implementation Notes:**
- F1 computation: Token-level overlap with normalization (remove articles, punctuation)
- Greedy generation: temperature=0.0, max_new_tokens=100, seed=42
- Evaluation loop: Iterate over all 800 samples (4 tasks × 200 samples) for each condition
- Cache metrics: Track retained tokens, eviction counts, cache hit rate

---

### FR6: Visualization and Reporting
**Priority:** P1 (important)  
**Description:** Generate figures and validation report (04_validation.md)

**Acceptance Criteria:**
- **Required:** Gate metrics bar chart (ProvenanceCache vs H2O F1 scores with ±5% threshold line)
- **Optional:** Cache budget curve, per-task breakdown, cache composition, latency boxplot, memory usage
- Save figures to `h-m1/figures/` with descriptive filenames
- Generate 04_validation.md with PASS/FAIL verdict, key findings, and figure references

**Implementation Notes:**
- Use matplotlib for all visualizations (no external dependencies)
- Figure format: PNG at 300 DPI
- Validation report template: Include gate status, statistical tests, ablation insights
- Key findings format: Bullet list with quantitative comparisons

---

## Non-Functional Requirements

### NFR1: Reproducibility
- Fixed random seed (42) for all stochastic operations
- Deterministic tokenization (sorted vocabulary, no random truncation)
- Version pinning: torch==2.0.1, transformers==4.31.0, datasets==2.14.0

### NFR2: Performance
- Total runtime: ≤8 GPU-hours (800 samples × 4 conditions × ~30 sec/sample)
- GPU memory: ≤16 GB VRAM (FP16 precision for Llama-2-7B)
- CPU fallback: Support CPU-only execution (slower but functional)

### NFR3: Error Handling
- Graceful degradation: Continue evaluation if single sample fails
- Checkpoint support: Save intermediate results every 50 samples
- Logging: Detailed logs for debugging (attention shapes, cache sizes, eviction counts)

---

## Out of Scope

- Multi-hop QA evaluation (deferred to H-M4)
- Diversity-aware scoring (deferred to H-M2)
- Query complexity stratification (deferred to H-M3)
- Model fine-tuning or training (inference-only experiment)
- Cache eviction on encoder models (decoder-only scope)

---

## Technical Stack

### Models
- Llama-2-7B (`meta-llama/Llama-2-7b-hf`)
- Contriever (`facebook/contriever-msmarco`)

### Datasets
- LongBench (`THUDM/LongBench`)

### Libraries
- PyTorch 2.0.1
- HuggingFace Transformers 4.31.0
- HuggingFace Datasets 2.14.0
- NumPy, SciPy (statistical tests)
- Matplotlib (visualization)

### Baseline Code
- FMInference/H2O (official repository)

---

## Implementation Phases (Archon Task Breakdown)

### Epic 1: Environment Setup
- Clone H2O repository
- Install dependencies (torch, transformers, datasets)
- Download Llama-2-7B and Contriever models
- Verify GPU availability (fallback to CPU if needed)

### Epic 2: Baseline Implementation
- Adapt H2O code for LongBench dataset
- Implement FullKV and Random eviction baselines
- Verify H2O eviction logic against paper specification
- Run PoC on 10-sample subset

### Epic 3: ProvenanceCache Implementation
- Implement Contriever retrieval pipeline
- Register provenance metadata (token types + relevance scores)
- Implement tiered eviction logic (query > high-rel > low-rel)
- Test on PoC subset

### Epic 4: Full Evaluation
- Run all 4 conditions on 800 samples
- Compute F1 scores and statistical tests
- Generate cache composition and latency metrics
- Save results to CSV

### Epic 5: Visualization and Reporting
- Generate required gate metrics chart
- Generate optional figures (cache budget curve, per-task breakdown, etc.)
- Write 04_validation.md with PASS/FAIL verdict
- Archive code and results

---

## Risk Analysis

### High Risk
- **H2O integration complexity**: Official repo may have compatibility issues with latest transformers
  - Mitigation: Use KVCache-Factory as fallback if H2O fails
- **CUDA availability**: GPU may not be available (as in H-E1)
  - Mitigation: Design CPU-compatible evaluation (slower but functional)

### Medium Risk
- **Contriever retrieval overhead**: Passage chunking may dominate runtime
  - Mitigation: Cache retrieval results, run retrieval once per question
- **LongBench single-hop filtering**: Some tasks may have multi-hop questions
  - Mitigation: Use inherently single-hop tasks (narrativeqa, triviaqa)

### Low Risk
- **Statistical power**: 200 samples per task may be insufficient for significance
  - Mitigation: Pool samples across tasks if needed (800 total samples)

---

## Acceptance Checklist

- [ ] H2O baseline achieves ~60-70% F1 on LongBench (matches paper ballpark)
- [ ] ProvenanceCache F1 ≥ H2O F1 × 1.05 (primary gate)
- [ ] Statistical significance: p < 0.05 (two-tailed t-test)
- [ ] PoC runs without error on 10-sample subset
- [ ] All 4 conditions evaluated on 800 samples
- [ ] Gate metrics chart generated
- [ ] 04_validation.md written with PASS/FAIL verdict
- [ ] Code archived in `h-m1/code/` directory

---

*Budget Tier: 2.5 (moderate complexity with external baseline integration)*  
*Estimated Duration: 6-8 GPU-hours + 2-3 implementation hours*
