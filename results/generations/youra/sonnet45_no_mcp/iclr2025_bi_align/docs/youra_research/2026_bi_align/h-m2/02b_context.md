# Phase 2B Context: h-m2

**Generated:** 2026-04-19  
**Source:** 02b_verification_plan.md (Section 2.2)

---

## Hypothesis Information

**ID:** h-m2  
**Type:** MECHANISM (Step 2)  
**Statement:** Under semantic embedding space representation, if we extract embeddings from 160K+ HH-RLHF chosen/rejected pairs using pretrained encoders (RoBERTa-base), then rejected responses will form distinct clusters (not random distribution) with MANOVA effect size d ≥ 0.5, because aggregated human judgments create high-density sampling of alignment failure space.

**Rationale:** Tests whether aggregation of judgments induces geometric structure. Random distribution would falsify manifold emergence claim from causal step 2.

---

## Variables

**Independent:**
- Response type (chosen vs rejected)

**Dependent:**
- Embedding cluster separability (MANOVA effect size)

**Controlled:**
- Encoder model (RoBERTa-base)
- Embedding extraction method (CLS pooling)
- Train/test split (80/20)

---

## Verification Protocol

1. Extract CLS token embeddings from RoBERTa-base for all HH-RLHF harmless pairs
2. Apply PCA dimensionality reduction to visualize embedding space distribution
3. Perform MANOVA test on chosen vs rejected embeddings
4. Compute effect size (Cohen's d) for group separation
5. Test H0: random distribution (d < 0.3) vs H1: structured clustering (d ≥ 0.5)

---

## Success Criteria

**Primary:** MANOVA effect size d ≥ 0.5 (medium-to-large effect)  
**Secondary:** Visual inspection confirms non-random clustering in PCA space

---

## Gate Information

**Gate Type:** SHOULD_WORK  
**Condition:** MANOVA effect size d ≥ 0.5  
**Failure Action:** If d < 0.3, EXPLORE alternative encoders or ABANDON geometric framing

---

## Dependencies

**Prerequisites:** h-m1 (Annotation Consistency)

**Status:** ✅ COMPLETED
- Result: PASS
- Metrics: κ=0.530, agreement=88.3% with HH-RLHF
- Note: Used untrained annotators (PoC demonstration)

**Previous Context:**
- h-e1 validated base-rate: 45.6% genuine violations (PASS)
- h-m1 demonstrated annotation consistency with untrained annotators
- Real annotation data available from h-e1 (300 pairs, 3 annotators)

---

## Experimental Setup (from Phase 2B Section 1.7)

**Dataset:** HH-RLHF harmless subset
- Source: Anthropic (publicly available)
- Path: https://huggingface.co/datasets/Anthropic/hh-rlhf
- Size: 160K+ chosen/rejected pairs
- Hypothesis Fit: Contains validated harmlessness annotations for geometric analysis

**Model:** RoBERTa-base (primary encoder)
- Type: Pretrained encoder
- Source: HuggingFace Transformers
- Hypothesis Fit: Semantic encoder captures alignment-relevant features

**Baselines:**
1. TF-IDF Logistic Regression (surface feature baseline)
2. Bradley-Terry Reward Model (standard RLHF approach)
3. Random Classifier (AUROC = 0.5 baseline)

---

## Source

Phase 2A Causal Step 2 falsifier, Prediction P2
