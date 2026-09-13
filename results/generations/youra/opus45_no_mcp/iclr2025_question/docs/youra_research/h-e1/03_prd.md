# Product Requirements Document: H-E1

**Hypothesis:** H-E1 (EXISTENCE)
**Date:** 2026-08-19
**Author:** PrayPrey
**Version:** 1.0

---

## Executive Summary

This PRD defines requirements for validating H-E1: verifying that token entropy and semantic consistency metrics CAN be computed for LLM-generated responses under QA task conditions. This is a foundational existence test—no model training, just metric computation verification.

**Success Criteria:** >99% computation success rate across TriviaQA validation set (~11,313 questions).

---

## Problem Statement

Before building hallucination detection systems using entropy and consistency signals, we must verify these signals can be reliably computed at scale. H-E1 establishes this foundation.

**What we're testing:** Can we compute entropy from logits and semantic consistency from multiple responses for every question?

---

## Functional Requirements

### FR-1: Data Loading
- **FR-1.1:** Load TriviaQA `rc.nocontext` validation split (~11,313 questions)
- **FR-1.2:** Extract question text only (no context documents)
- **FR-1.3:** Support batch processing with progress tracking

### FR-2: Model Inference
- **FR-2.1:** Load Llama-2-7B-chat-hf in FP16 (~14GB VRAM)
- **FR-2.2:** Generate 10 responses per question with temperature=0.7
- **FR-2.3:** Return logits via `output_scores=True, return_dict_in_generate=True`
- **FR-2.4:** Max 128 new tokens per response
- **FR-2.5:** Use Llama-2 chat template: `[INST] {question} [/INST]`

### FR-3: Entropy Computation
- **FR-3.1:** Compute Shannon entropy from softmax(logits) per generated token
- **FR-3.2:** Aggregate as mean entropy across all generated tokens
- **FR-3.3:** Store per-sample entropy for each of 10 responses
- **FR-3.4:** Compute final mean entropy across 10 samples

### FR-4: Semantic Consistency Computation
- **FR-4.1:** Encode 10 responses using SentenceTransformer (all-MiniLM-L6-v2)
- **FR-4.2:** Compute pairwise cosine similarity (45 pairs for 10 responses)
- **FR-4.3:** Return mean pairwise similarity as consistency score

### FR-5: Output Storage
- **FR-5.1:** Store results in JSON format per question
- **FR-5.2:** Fields: question_id, entropy, consistency, success, responses (optional)
- **FR-5.3:** Support incremental checkpointing every 100 questions
- **FR-5.4:** Final output: `h-e1/results.json`

### FR-6: Evaluation
- **FR-6.1:** Compute success rate: % questions with valid entropy AND consistency
- **FR-6.2:** Compute entropy statistics: mean, std, min, max
- **FR-6.3:** Compute consistency statistics: mean, std, min, max
- **FR-6.4:** Verify non-zero variance in both metrics
- **FR-6.5:** Generate validation report: `h-e1/04_validation.md`

---

## Non-Functional Requirements

### NFR-1: Performance
- Target: Process full TriviaQA validation in <24 hours on single GPU
- Memory: Fit in 24GB VRAM (A10/A100)

### NFR-2: Reliability
- Checkpoint every 100 questions for crash recovery
- Graceful handling of OOM errors (skip question, log, continue)

### NFR-3: Reproducibility
- Fixed random seed (42) for generation
- Log all hyperparameters to config file

---

## Success Criteria

| Metric | Target | Rationale |
|--------|--------|-----------|
| Success Rate | >99% | Both metrics computed for nearly all questions |
| Entropy Variance | >0 | Entropy varies across questions |
| Consistency Variance | >0 | Consistency varies across questions |
| Runtime | <24h | Practical for iteration |

**Gate Decision:**
- PASS (≥99% success + variance >0) → Proceed to H-M1
- FAIL → STOP pipeline, cannot compute required signals

---

## Data Specifications

### Input
- **Dataset:** TriviaQA rc.nocontext validation (~11,313 questions)
- **Source:** HuggingFace `mandarjoshi/trivia_qa`

### Output
- `h-e1/results.json` - per-question metrics
- `h-e1/04_validation.md` - evaluation report
- `h-e1/figures/` - visualizations

---

## Dependencies

### Models
- `meta-llama/Llama-2-7b-chat-hf` - requires HuggingFace access token
- `sentence-transformers/all-MiniLM-L6-v2` - public

### Libraries
- transformers>=4.35.0
- sentence-transformers>=2.2.0
- torch>=2.0
- datasets>=2.14.0
- numpy, scipy

### Hardware
- GPU: 24GB VRAM minimum (A10, A100, RTX 3090/4090)
- Storage: ~5GB for model weights, ~500MB for results

---

## Appendix: Phase 2C Reference

This PRD implements the experiment design from `h-e1/02c_experiment_brief.md`:
- Metric computation patterns from Archon KB
- Code examples from semantic-uncertainty and selfcheckgpt repos
- HuggingFace API patterns for logit access
