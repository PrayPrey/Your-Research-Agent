# Experiment Brief: h-e1 Duality Initialization Validity

**Hypothesis ID:** h-e1
**Type:** EXISTENCE
**Gate:** MUST_WORK
**Date:** 2026-08-29

---

## 1. Hypothesis Statement

Closed-form SSM initialization from Transformer attention weights using Mamba-2 duality equations produces valid, non-divergent parameters that enable stable optimization.

**Variables:**
- IV: Conversion method (duality equations vs random init)
- DV: SSM output stability (non-divergent forward pass)
- CV: Model architecture (12 layers, 768 dim), input sequences

---

## 2. Dataset Specification

### Primary Dataset: WikiText-103 (Calibration)

| Property | Value |
|----------|-------|
| Name | WikiText-103 |
| Type | standard |
| Source | HuggingFace: `wikitext-103-raw-v1` |
| Sample Count | 500 calibration samples |
| Sequence Length | 512-2048 tokens (varied) |
| Purpose | Calibration data for initialization testing |

**Justification:** Standard language modeling corpus. Real text distributions. Sufficient variety for stability testing.

### Evaluation Samples

| Split | Count | Sequence Lengths |
|-------|-------|------------------|
| Calibration | 500 | 512, 1024, 2048 tokens |

**Length Distribution:**
- 200 samples @ 512 tokens
- 200 samples @ 1024 tokens  
- 100 samples @ 2048 tokens

---

## 3. Model Specification

### Teacher Model: BERT-base

| Property | Value |
|----------|-------|
| Architecture | Transformer encoder |
| Layers | 12 |
| Hidden Dim | 768 |
| Attention Heads | 12 |
| Source | HuggingFace: `bert-base-uncased` |
| Parameters | ~110M |

### Student Model: Mamba-12 (SSM)

| Property | Value |
|----------|-------|
| Architecture | Mamba-2 SSM |
| Layers | 12 |
| Model Dim | 768 |
| State Dim | 16 (per-head) |
| Source | `state-spaces/mamba` |
| Parameters | ~125M |

---

## 4. Duality Equations (Core Implementation)

### Mamba-2 Attention-SSM Duality

From Mamba-2 paper, attention with causal mask can be written as:

```
y_t = Σ_{s≤t} softmax(q_t · k_s^T) · v_s
```

Equivalent SSM formulation:

```
h_t = A · h_{t-1} + B · x_t
y_t = C · h_t
```

### Closed-Form Initialization

**From attention weights (W_Q, W_K, W_V) derive SSM params:**

1. **A matrix:** Derived from attention decay pattern
   - `A = exp(-Δ · softplus(W_decay))`
   - W_decay initialized from attention head statistics

2. **B matrix:** Input projection
   - `B = linear_transform(W_K)`

3. **C matrix:** Output projection  
   - `C = linear_transform(W_V)`

4. **Δ (discretization step):**
   - `Δ = softplus(W_Δ)` 
   - W_Δ derived from attention temperature

### Implementation Pseudocode

```python
def duality_init(transformer_layer):
    W_Q, W_K, W_V = transformer_layer.attention.weights
    
    # Compute attention statistics
    attn_scale = 1 / sqrt(d_head)
    
    # Derive A: eigenvalue decay from attention pattern
    A_log = compute_decay_from_attention(W_Q, W_K)
    A = -exp(A_log)  # Ensures stability (eigenvalues < 1)
    
    # Derive B: from key projection
    B = project_to_state_dim(W_K)
    
    # Derive C: from value projection
    C = project_to_output_dim(W_V)
    
    # Derive Δ: from attention scaling
    delta = softplus(init_delta_from_scale(attn_scale))
    
    return MambaParams(A=A, B=B, C=C, delta=delta)
```

---

## 5. Experimental Protocol

### Step 1: Data Preparation

1. Load WikiText-103 from HuggingFace
2. Tokenize with BERT tokenizer
3. Sample 500 sequences (200@512, 200@1024, 100@2048)
4. Cache tokenized data

### Step 2: Teacher Model Setup

1. Load `bert-base-uncased` from HuggingFace
2. Extract attention weights from all 12 layers
3. Run forward pass on calibration data
4. Store output activations for reference

### Step 3: Duality Initialization

1. For each BERT layer (1-12):
   - Extract W_Q, W_K, W_V, W_O
   - Apply duality equations to derive A, B, C, Δ
   - Initialize corresponding Mamba layer

### Step 4: Stability Verification

1. Run Mamba forward pass on all 500 calibration samples
2. Check for NaN/Inf in outputs
3. Compute output magnitude statistics
4. Compare to BERT output magnitudes

### Step 5: Baseline Comparison

1. Initialize another Mamba-12 with random weights
2. Run same stability checks
3. Compare stability metrics

---

## 6. Success Criteria

### Primary Metrics

| Metric | Pass Threshold | Measurement |
|--------|----------------|-------------|
| NaN/Inf Rate | 0% | Count samples with invalid outputs |
| Output Magnitude Ratio | < 10x | mean(|SSM_out|) / mean(|BERT_out|) |

### Secondary Metrics

| Metric | Target | Purpose |
|--------|--------|---------|
| Gradient Norm | < 1000 | Optimization feasibility |
| Parameter Range | finite | All params in valid range |

### Pass Condition

**h-e1 PASSES if:**
- 0% NaN/Inf across all 500 samples
- Output magnitude ratio < 10x
- All SSM parameters finite

**h-e1 FAILS if:**
- Any NaN/Inf in outputs
- Magnitude ratio > 10x
- Parameters overflow

---

## 7. Implementation Requirements

### Dependencies

```
torch >= 2.0
transformers >= 4.35
mamba-ssm >= 1.0
datasets
numpy
```

### Compute Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| GPU | 8GB VRAM | 16GB VRAM |
| RAM | 16GB | 32GB |
| Time | 30 min | 15 min |

### Code Structure

```
h_e1_experiment/
├── data/
│   └── prepare_calibration.py
├── models/
│   ├── load_bert.py
│   └── mamba_init.py
├── duality/
│   └── closed_form_init.py
├── eval/
│   └── stability_check.py
└── run_experiment.py
```

---

## 8. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Duality equations numerically unstable | Use log-space computation, clamp extreme values |
| State dimension mismatch | Project with learned linear layer |
| Attention patterns non-duality-compatible | Start with layer 1 (simplest patterns) |
| Memory overflow on long sequences | Process in chunks, gradient checkpointing |

---

## 9. Expected Outcomes

### If PASS:
- Duality equations produce valid SSM initialization
- Proceed to h-m1 (initial error comparison)
- Foundation for layer-wise distillation validated

### If FAIL:
- Analyze failure mode (which layers, which samples)
- Check duality equation implementation
- Consider relaxed duality conditions
- May need approximation methods

---

## 10. Validation Checklist

Before execution:
- [ ] WikiText-103 downloaded and cached
- [ ] BERT-base model loaded successfully
- [ ] Mamba-ssm package installed
- [ ] GPU memory sufficient
- [ ] Duality equations implemented

After execution:
- [ ] 500 samples processed
- [ ] NaN/Inf check completed
- [ ] Magnitude ratio computed
- [ ] Results logged
- [ ] Pass/fail determination made

---

*Generated by Phase 2C Experiment Design*
*Target: h-e1 (EXISTENCE hypothesis)*
*Gate: MUST_WORK*
