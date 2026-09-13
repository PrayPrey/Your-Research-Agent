# Phase 2B Context: H-M1

**Hypothesis ID:** H-M1
**Type:** MECHANISM
**Prerequisites:** H-E1 (PASS)

## Hypothesis Statement

Attention pattern structure differs between encoder (bidirectional O(n²)) and decoder (causal O(n²/2)) architectures under BERT vs GPT-2.

## Full Statement from Phase 2B

Under BERT vs GPT-2, if we analyze attention computation, then bidirectional attention (BERT) computes O(n²) full attention weights while causal attention (GPT-2) computes O(n²/2) masked weights, because architectural definition constrains attention pattern structure.

## Rationale

This is the first step in the causal chain—establishing that attention patterns fundamentally differ between architectures.

## Variables

- **IV:** Architecture Type (encoder-only vs decoder-only)
- **DV:** Attention pattern structure (full vs causal mask)
- **CV:** Sequence length, Layer count

## Verification Protocol

1. Extract attention weights from both models on same input sequences
2. Verify BERT produces full n×n attention matrices
3. Verify GPT-2 produces lower-triangular (causal) attention matrices
4. Quantify sparsity difference

## Success Criteria

- **Primary:** Attention pattern structure matches architectural definition
- **Secondary:** Measurable sparsity difference in attention matrices

## Failure Response

- IF fails: EXPLORE alternative explanations (unlikely—architectural definition)

## Gate Condition

**Type:** MUST_WORK
**Pass Condition:** Attention patterns match architectural definition
**Fail Action:** STOP - architectural error

## Experimental Setup (from Phase 2B Section 1.3)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | SST-2 (standard) | Binary sentiment classification allows both BERT and GPT-2 to perform natively |
| **Model** | BERT-base-uncased and GPT-2 | Matched layer count (12), similar params (110M vs 124M) |

### Dataset Details
- Source: GLUE benchmark via HuggingFace datasets
- Path: glue/sst2

### Model Details
- Type: Encoder-only transformer, Decoder-only transformer
- Source: HuggingFace Transformers

## Continuation Context

### Previous Hypothesis Results (H-E1)

H-E1 (Existence) validated that architecture-method interaction exists and is measurable via efficiency-accuracy Pareto curves.

**Results from Phase 4 validation:**
- Best method: TRAK (+5.1% AUC difference across architectures)
- Methods tested: 3 (TRAK, EK-FAC, TracIn)
- Architectures tested: 2 (BERT, GPT-2)
- Seeds used: 2
- Gate: MUST_WORK → PASS

**Implications for H-M1:**
- Existence of architecture-method interaction is established
- Now need to verify the mechanistic explanation (attention pattern divergence)

## Source

Phase 2A Causal Step 1, Phase 2B Section 2.2
