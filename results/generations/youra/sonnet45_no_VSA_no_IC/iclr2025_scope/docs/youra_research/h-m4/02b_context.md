# Phase 2B Context: h-m4

**Generated:** 2026-08-20 (JIT generation for Phase 2C)
**Source:** verification_state.yaml via Phase 2C step-01

---

## Hypothesis Information

**ID:** h-m4
**Type:** MECHANISM
**Statement:** Adaptive cache (grow/shrink based on retrieval density) matches static 25% cache accuracy while using ≤20% budget on average

**Prerequisites:** h-m3
**Gate Type:** SHOULD_WORK
**Gate Condition:** Experiment should demonstrate adaptive cache matching static 25% accuracy at ≤20% average budget. Non-critical optimization — failure documented as limitation.

---

## Experimental Setup

### Dataset Selection (from Phase 2A)

**Dataset:** LongBench (single-hop QA subset)
**Specific Task:** TriviaQA
**Type:** standard
**Source:** THUDM/LongBench (HuggingFace Datasets)
**Path:** Auto-download via HuggingFace

**Hypothesis Fit:**
- Tests retrieval-augmented QA with variable context length
- Enables measurement of cache sizing impact on accuracy
- Continuation from h-m1/h-m2/h-m3 for controlled comparison

**Statistics:**
- Test samples: ~200 per task
- Average context length: 8,209 tokens (TriviaQA)
- Evaluation metric: F1 score (token overlap)

### Model Selection (from Phase 2A)

**Model:** Llama-2-7B
**Type:** Autoregressive causal language model
**Source:** Meta (HuggingFace Transformers)
**Pretrained:** Yes (meta-llama/Llama-2-7b-hf)

**Hypothesis Fit:**
- Proven long-context capabilities
- Standard baseline for KV cache research
- Continuation from h-m1/h-m2/h-m3 for fair comparison

**Configuration:**
- Parameters: ~7B
- Context window: Extended for long-context evaluation
- Precision: FP16

---

## Continuation Context

**Previous Hypothesis:** h-m3 (Query Complexity Attention)
**Result:** FAILED (p=0.9537, no significance)
**Implication:** Query complexity does not predict attention concentration
**Fallback:** Uniform tiering (all retrieval passages treated equally)

**Reuse Strategy:**
- Same dataset (LongBench TriviaQA) for controlled comparison
- Same baseline model (Llama-2-7B)
- Only independent variable changes: cache sizing policy (static → adaptive)

---

## Baseline & Comparison Targets

**Baseline:** H2O (Heavy-Hitter Oracle)
- Static 25% cache budget (0.125 heavy_ratio + 0.125 recent_ratio)
- Accumulated attention-based eviction
- Proven ~95% FullKV accuracy at 20% retention (from literature)

**Comparison Target:**
- Adaptive cache should match static 25% accuracy
- While using ≤20% budget on average (resource efficiency gain)

---

## Dependencies

**Technical:**
- Retrieval density tracking infrastructure
- Sliding window passage access monitoring
- Dynamic budget adjustment mechanism

**From Previous Hypotheses:**
- h-m1: Provenance-aware tiering pattern (validated)
- h-m2: Diversity-aware scoring pattern (validated)
- h-m3: Query complexity tiering (failed → uniform fallback)

---

*This context file enables Phase 2C experiment design without referencing the full 02b_verification_plan.md.*
