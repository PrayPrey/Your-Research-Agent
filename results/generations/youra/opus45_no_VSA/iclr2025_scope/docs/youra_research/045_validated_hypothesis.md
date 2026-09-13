# Validated Hypothesis: IPCR Zero-Shot Adapter Routing

**Date:** 2026-08-09  
**Pipeline Project:** 07144d4f-0a39-4d5e-b837-021dae2229a7  
**Synthesis Phase:** 4.5

---

## Executive Summary

IPCR (Instruction-Prefix-Conditioned Routing) achieves **95% of oracle adapter selection performance** using frozen MiniLM embeddings + linear probe on FLAN task families. All MUST_WORK gates passed (h-e0, h-e1, h-m1). The SHOULD_WORK robustness hypothesis (h-m2) failed, revealing lexical dependence as a key limitation.

**Core Validated Claim:** Zero-shot adapter routing via instruction embeddings is effective but fragile—routing relies on surface lexical patterns rather than deep semantic invariants.

| Sub-Hypothesis | Gate | Result | Key Metric |
|----------------|------|--------|------------|
| h-e0 (Task separability) | MUST_WORK | ✅ PASS | F1=0.995 |
| h-e1 (Adapter selection) | MUST_WORK | ✅ PASS | Top-1: 72.67%, Top-3: 95.78% |
| h-m1 (Oracle performance) | MUST_WORK | ✅ PASS | 95% of oracle |
| h-m2 (Robustness) | SHOULD_WORK | ❌ FAIL | Cosine 0.78, drop 44% |

---

## Prediction-Result Matrix

| Prediction | Expected | Actual | Status |
|------------|----------|--------|--------|
| **P1**: Instruction prefixes linearly separable by task family | macro-F1 ≥0.75 | macro-F1 = 0.995 | **CONFIRMED** |
| **P2**: Linear probe achieves ≥70% oracle adapter selection | top-1 ≥70% OR top-3 ≥85% | top-1: 72.67%, top-3: 95.78% | **CONFIRMED** |
| **P3**: Zero-shot IPCR achieves ≥90% of oracle performance | ≥90% | 95.00% | **CONFIRMED** |
| **P4**: Routing robust to paraphrase | cosine ≥0.90 | cosine = 0.782 | **REFUTED** |
| **P5**: Routing tolerates keyword masking | drop <10% | drop = 44.4% | **REFUTED** |

**Alignment Assessment:** 3/5 predictions confirmed. Core mechanism validated; robustness properties refuted.

---

## Hypothesis Refinement

### Original Statement (from 03_refinement.yaml)
> Under the FLAN instruction-tuning task taxonomy, if instruction prefixes are embedded using a frozen sentence encoder (MiniLM) and mapped via learned linear projection to adapter weights, then zero-shot adapter routing achieves ≥90% of oracle task-specific LoRA performance on held-out tasks, because instruction semantics and adapter specializations share geometric structure inherited from the base model's learned task representations.

### Refined Statement (Post-Validation)

> **Zero-shot instruction-prefix routing via frozen MiniLM embeddings achieves near-oracle adapter selection accuracy (95% of oracle) on FLAN task families when instruction wording closely matches the training distribution. The routing mechanism relies substantially on task-indicative keywords and surface lexical features rather than deep semantic invariants, making it fragile to paraphrase and keyword perturbations.**

### Overclaims Removed
1. ~~"Routing is robust to paraphrase variations"~~ — Refuted: cosine 0.78 < 0.90
2. ~~"Routing tolerates keyword masking"~~ — Refuted: 44% accuracy drop >> 10%
3. ~~"Deep semantic structure drives routing"~~ — Undermined: lexical dependence evident

### Validated Mechanism Chain
1. MiniLM encodes instruction prefixes → 384-dim embeddings
2. Embeddings cluster by task family (h-e0: F1=0.995)
3. Linear probe predicts optimal adapter (h-e1: 72.67% top-1)
4. Selected adapter achieves near-oracle performance (h-m1: 95%)

---

## Theoretical Interpretation

### Why IPCR Works
1. **Lexical Anchoring:** FLAN instructions contain task-indicative keywords ("calculate", "translate", "explain") that MiniLM embeddings preserve. Linear separability (F1=0.995) emerges from these keyword clusters.
2. **Distribution Match:** Training and test instructions share vocabulary and phrasing patterns from the FLAN template structure.
3. **Adapter Specialization:** Task-specific LoRAs capture distinct computation patterns that align with instruction semantics.

### Why Robustness Fails
1. **Embedding Drift:** WordNet synonyms ("provide"→"allow", "capital"→"Washington") shift embeddings beyond routing tolerance (cosine 0.72).
2. **Keyword Dependence:** 20% keyword masking causes 26% accuracy drop—routing relies on surface tokens, not deep semantics.
3. **MiniLM Limitation:** Mean-pooling dilutes positional structure; task discrimination comes from token presence, not compositional meaning.

### Competing Explanations
- **Lexical Anchoring Hypothesis:** Success reflects keyword preservation in FLAN instructions, not semantic understanding.
- **Distribution Match Hypothesis:** High performance indicates training-test distribution overlap, not generalizable routing.

---

## Experiment Results

### H-E0: Task Family Separability

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Macro-F1 | 0.995 | ≥0.75 | ✅ PASS |
| Accuracy | 0.998 | - | - |
| Baseline F1 | 0.115 | - | - |

**Configuration:** MiniLM-L6-v2 encoder, LogisticRegression classifier, 50K FLAN samples, 9 task families.

### H-E1: Adapter Selection Accuracy

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Top-1 Accuracy | 72.67% | ≥70% | ✅ PASS |
| Top-3 Accuracy | 95.78% | ≥85% | ✅ PASS |
| vs Random | 14.8x | >1x | ✅ PASS |

**Configuration:** 3000 FLAN samples, 18 task subtypes, 70/15/15 split.

### H-M1: Oracle Performance

| Strategy | Performance | Relative to Oracle |
|----------|-------------|-------------------|
| Oracle | 91.39% | 100.00% |
| IPCR | 86.82% | **95.00%** |
| Uniform | 36.79% | 40.26% |
| Random | 14.97% | 16.38% |

**Statistical Significance:** t=68.99, p=7.05e-224 (IPCR vs Uniform)

### H-M2: Robustness (FAILED)

| Test | Target | Actual | Status |
|------|--------|--------|--------|
| Cosine (paraphrase) | ≥0.90 | 0.782 | ❌ FAIL |
| Accuracy drop (masking) | <10% | 44.4% | ❌ FAIL |
| Routing consistency | ≥85% | 76.1% | ❌ FAIL |

**Root Cause:** MiniLM embeddings capture lexical features, not paraphrase-invariant semantics.

---

## Limitations

### L1: Lexical Sensitivity
- **Evidence:** h-m2 keyword masking causes 44% accuracy drop
- **Root Cause:** MiniLM mean-pooling loses positional semantics; routing relies on keyword presence
- **Scope:** IPCR works on FLAN-formatted instructions; fails on paraphrased queries

### L2: Paraphrase Fragility
- **Evidence:** h-m2 cosine 0.78 (below 0.90 threshold)
- **Root Cause:** Synonym substitution causes embedding drift exceeding routing tolerance
- **Scope:** Real-world instruction variations will cause routing errors (~24% inconsistency)

### L3: Task Family Coverage
- **Evidence:** Tested 9-18 families (not full 62 FLAN categories)
- **Root Cause:** Computational constraints; streaming subset
- **Scope:** Generalization to untested families unverified

### L4: Oracle Approximation
- **Evidence:** h-e1 used task names as oracle proxy
- **Root Cause:** PoC scope; full oracle requires k adapter evaluations per sample
- **Scope:** True adapter selection accuracy may differ from proxy

---

## Future Work

### F1: Robust Router Training (Priority: HIGH)
**Motivation:** h-m2 failure reveals lexical dependence  
**Direction:** Paraphrase augmentation during probe training; contrastive loss for invariance; larger encoder (E5-large, Instructor-XL)

### F2: Hybrid Routing (Priority: MEDIUM)
**Motivation:** Combine embedding and keyword-based methods  
**Direction:** Two-stage router: embedding prediction + keyword confidence boost; fallback to uniform when confidence < threshold

### F3: Full Oracle Validation (Priority: HIGH)
**Motivation:** h-e1 used task-name proxy  
**Direction:** Compute per-adapter loss for each sample; re-train probe on performance-based labels

### F4: Compositional Routing (Priority: LOW)
**Motivation:** FLAN scope excludes multi-step tasks  
**Direction:** Extend to composite instructions; test adapter mixing vs sequential routing

---

## Implications for Phase 6

### Paper-Ready Claims
1. **Primary:** Zero-shot adapter routing achieves 95% of oracle performance on FLAN tasks
2. **Supporting:** Instruction embeddings are linearly separable by task family (F1=0.995)
3. **Limitation:** Routing depends on lexical keywords; not robust to paraphrase (must report)

### Baseline Comparison (Phase 5)
- Compare IPCR vs LoRAuter-zero, Uniform, Random on standardized benchmark
- Measure inference latency overhead
- Quantify robustness gap

### Contribution Framing
- **Novelty:** First zero-shot adapter routing without validation examples (vs LoRAuter's 5-shot)
- **Trade-off:** Achieves 95% oracle at cost of paraphrase fragility
- **Implication:** Suitable for controlled instruction formats (APIs, templates); needs robustification for open-ended queries

---

## Artifacts Generated

| Hypothesis | Key Artifacts |
|------------|---------------|
| h-e0 | 04_validation.md, confusion_matrix.png, tsne_embeddings.png |
| h-e1 | 04_validation.md, gate_metrics.png, per_class_accuracy.png |
| h-m1 | 04_validation.md, gate_comparison.png, smoke_test.json |
| h-m2 | 04_validation.md, cosine_distribution.png, failure_cases.png |

---

*Phase 4.5 Synthesis Complete — Proceed to Phase 5 (Baseline Comparison) or Phase 6 (Paper Writing)*
