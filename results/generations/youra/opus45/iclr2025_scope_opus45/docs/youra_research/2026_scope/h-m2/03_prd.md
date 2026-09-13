# Product Requirements Document: H-M2

**Hypothesis:** Projection-only LoRA Preserves SSM Eigenvalues
**Type:** MECHANISM
**Date:** 2026-03-27
**Author:** Anonymous
**Status:** Draft

---

## 1. Executive Summary

This PRD defines the implementation requirements for validating hypothesis H-M2: demonstrating that projection-only LoRA modifies input/output mappings but does NOT change the discretized transition matrix eigenvalues (Ā), thereby preserving the spectral memory horizon H_spec (|ΔH_spec| < 10%).

**Key Deliverable:** An eigenvalue preservation validation framework that applies projection-only LoRA to Mamba-1.4B, fine-tunes on WikiText-103, and verifies that A_log parameters (and thus eigenvalues) remain unchanged.

**Success Criterion:** |ΔH_spec| < 10% after projection-only LoRA fine-tuning on WikiText-103.

**Theoretical Basis:** LoRA keeps original pretrained weights frozen and only trains low-rank adapter matrices. When applied to projection matrices (in_proj, out_proj) only, the SSM core parameters (A_log, D) should remain completely unchanged.

---

## 2. Problem Statement

### 2.1 Background
H-M1 established that the spectral memory horizon H_spec = 256.18 tokens (derived from eigenvalues) predicts actual memory behavior in Mamba-1.4B. H-M2 validates that projection-only LoRA preserves these eigenvalues, enabling clean isolation between "eigenmode utilization" (H-M3) and "spectral surgery" (modifying eigenvalues).

### 2.2 Research Gap
While LoRA theory states that original weights remain frozen, no prior work has empirically verified eigenvalue preservation specifically for SSM/Mamba architectures under projection-only LoRA. This is critical for distinguishing adaptation mechanisms.

### 2.3 Gate Condition
**MUST_WORK Gate:** If projection-only LoRA changes eigenvalues (|ΔH_spec| >= 10%), the isolation assumption is invalid - we cannot distinguish eigenmode utilization from spectral surgery, and the MHSH/EUH framework breaks down.

---

## 3. Functional Requirements

### FR-1: Baseline Model Loading
- **Description:** Load pretrained Mamba-1.4B model
- **Source:** state-spaces/mamba-1.4b-hf (HuggingFace)
- **Acceptance:** Model loads without error, forward pass functional

### FR-2: Baseline Eigenvalue Extraction
- **Description:** Extract A_log parameters and compute baseline H_spec BEFORE any LoRA modification
- **Method:** Reuse H-M1 validated methodology
  - λ_discrete = exp(-exp(A_log))
  - H_spec = -1/log(λ_max)
- **Expected Result:** H_spec ≈ 256.18 tokens (from H-E1/H-M1)
- **Acceptance:** Baseline H_spec recorded, eigenvalue distribution saved

### FR-3: Dataset Loading
- **Description:** Load WikiText-103 for fine-tuning
- **Source:** HuggingFace Datasets (wikitext/wikitext-103-raw-v1)
- **Statistics:**
  - Train: ~103M tokens
  - Validation: ~218K tokens
  - Sequence length: 1024 tokens (chunked)
- **Acceptance:** Training and validation sets prepared

### FR-4: Projection-Only LoRA Configuration
- **Description:** Apply LoRA adapters to projection matrices ONLY
- **LoRA Configuration:**
  - Rank (r): 16
  - Alpha: 32
  - Target modules: ["in_proj", "out_proj"] (projections only!)
  - Dropout: 0.1
  - Bias: "none"
- **Critical Constraint:** A_log and D parameters must NOT be in trainable parameters
- **Acceptance:**
  - LoRA applied successfully
  - A_log NOT in trainable params (verified)
  - Only projection LoRA adapters are trainable

### FR-5: Fine-Tuning Execution
- **Description:** Fine-tune the LoRA-adapted model on WikiText-103
- **Training Protocol:**
  - Optimizer: AdamW (weight_decay=1e-4)
  - Learning Rate: 1e-4
  - Schedule: Cosine with 100 step warmup
  - Batch Size: 8 (effective 32 with gradient accumulation)
  - Epochs: 3
  - Loss: Cross-entropy (language modeling)
  - Seed: 42 (fixed)
- **Acceptance:** Training completes without error, loss decreases

### FR-6: Post-Training Eigenvalue Extraction
- **Description:** Extract A_log parameters and compute H_spec AFTER LoRA fine-tuning
- **Method:** Same as FR-2 (identical extraction procedure)
- **Acceptance:** Post-training H_spec computed, eigenvalue distribution saved

### FR-7: Eigenvalue Preservation Verification
- **Description:** Compare pre/post eigenvalues and compute preservation metrics
- **Metrics:**
  1. ΔH_spec = |H_spec_post - H_spec_pre| / H_spec_pre × 100 (percentage)
  2. Eigenvalue correlation = Pearson(pre_eigenvalues, post_eigenvalues)
  3. A_log parameter diff = max|A_log_post - A_log_pre|
- **Success Criteria:**
  - Primary: |ΔH_spec| < 10%
  - Secondary: Eigenvalue correlation > 0.95
  - Verification: A_log diff should be 0 (frozen by design)
- **Acceptance:** All metrics computed and compared to thresholds

### FR-8: Mechanism Verification
- **Description:** Verify LoRA correctly targets projections only
- **Checks:**
  1. A_log NOT in model.trainable_parameters()
  2. "proj" and "lora" in some trainable parameter names
  3. A_log values unchanged (numerical verification)
- **Acceptance:** All mechanism checks pass

### FR-9: Perplexity Validation (Secondary)
- **Description:** Verify model still functions after LoRA training
- **Method:** Compute WikiText-103 validation perplexity
- **Expected:** Similar to baseline (~12-17 PPL)
- **Note:** This validates model integrity, not the hypothesis itself
- **Acceptance:** Perplexity within reasonable range (< 30 PPL)

### FR-10: Visualization
- **Description:** Generate required figures
- **Required Figures:**
  1. Gate Metrics Comparison: ΔH_spec (actual vs 10% threshold) bar chart
- **Additional Figures (LLM Autonomous):**
  2. Eigenvalue Distribution Comparison: Pre/post overlay histogram
  3. Per-Layer H_spec Change: Bar chart showing ΔH_spec for each of 48 layers
  4. A_log Parameter Diff Heatmap: Should be all zeros
  5. Eigenvalue Scatter Plot: Pre vs post with identity line
  6. Training Loss Curve: Confirm model trained properly
- **Acceptance:** Figures saved to `figures/` subfolder

---

## 4. Data Specification

### 4.1 Input Data

| Dataset | Type | Source | Download |
|---------|------|--------|----------|
| WikiText-103 | standard | HuggingFace | `load_dataset("wikitext", "wikitext-103-raw-v1")` |

**Loading Code:**
```python
from datasets import load_dataset
from transformers import AutoTokenizer

dataset = load_dataset("wikitext", "wikitext-103-raw-v1")
tokenizer = AutoTokenizer.from_pretrained("state-spaces/mamba-1.4b-hf")

def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, max_length=1024)

tokenized_train = dataset["train"].map(tokenize_function, batched=True)
tokenized_valid = dataset["validation"].map(tokenize_function, batched=True)
```

### 4.2 Model Checkpoints

| Model | Source | Method |
|-------|--------|--------|
| Mamba-1.4B | state-spaces/mamba-1.4b-hf | HuggingFace auto-download |
| Tokenizer | state-spaces/mamba-1.4b-hf | HuggingFace auto-download |

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Complete fine-tuning in < 2 hours on single GPU
- Memory usage < 24GB (Mamba-1.4B + LoRA adapters)

### NFR-2: Reproducibility
- Fixed random seed (42) for all operations
- Deterministic training where possible

### NFR-3: Statistical Validity
- Full training set used (not trivially small samples)
- Minimum validation on 1000+ sequences

### NFR-4: Numerical Precision
- Eigenvalue computation in float32/64
- A_log comparison with numerical tolerance (1e-6)

---

## 6. Success Criteria

### Primary Gate (MUST_WORK)
| Metric | Target | Threshold |
|--------|--------|-----------|
| ΔH_spec | < 10% | PASS if |ΔH_spec| < 10%, FAIL otherwise |

### Secondary Metrics (Informational)
| Metric | Expected |
|--------|----------|
| Eigenvalue Correlation | > 0.99 (nearly identical) |
| A_log Parameter Diff | 0.0 (exactly frozen) |
| Post-training Perplexity | ~12-17 PPL (functional model) |

### Falsification Conditions (Hypothesis FAILS if):
- |ΔH_spec| >= 10% (eigenvalues changed significantly)
- Eigenvalue correlation < 0.90 (distribution shifted)
- A_log parameters modified (should remain frozen)

### Expected Results:
- ΔH_spec ≈ 0% (theoretical expectation: exactly 0)
- H_spec ≈ 256.18 tokens before AND after
- A_log parameters unchanged (frozen by LoRA design)

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
mamba-ssm>=1.0.0
transformers>=4.30.0
datasets>=2.0.0
peft>=0.5.0
numpy>=1.20.0
scipy>=1.7.0
matplotlib>=3.5.0
pyyaml>=6.0
```

### 7.2 Previous Hypothesis Results
- **H-E1:** VALIDATED (MUST_WORK PASS)
  - H_spec = 256.18 tokens
  - CV(H_spec) = 2.22e-16
- **H-M1:** VALIDATED (MUST_WORK PASS)
  - Degradation ratio = 3.03 > 1.1
  - Eigenvalue-derived H_spec predicts memory behavior
  - Validated eigenvalue extraction methodology

### 7.3 External Repositories (Reference)

| Repository | Purpose | Key Reference |
|------------|---------|---------------|
| state-spaces/mamba | Official Mamba implementation | Issue #326 (A_log parameterization) |
| furiosa-ai/ssm-peft | SSM PEFT methods (ICML 2025) | LoRA on projections effectiveness |
| sony/MambaPEFT | Mamba PEFT exploration (ICLR 2025) | Training hyperparameters |

---

## 8. Constraints

### 8.1 Resource Constraints
- Single GPU execution (CUDA_VISIBLE_DEVICES)
- LoRA training (parameter-efficient, ~0.1% trainable)

### 8.2 Time Constraints
- Fine-tuning: ~1-2 hours for 3 epochs on WikiText-103
- Evaluation: ~10 minutes for eigenvalue extraction and comparison
- Total execution: < 3 hours including setup

### 8.3 Scope Constraints
- MECHANISM hypothesis - validates LoRA eigenvalue preservation
- Projection-only LoRA (not full fine-tuning)
- Builds on H-M1 validated eigenvalue methodology

---

## 9. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| A_log accidentally modified | Very Low | High | Verify A_log not in trainable_params before training |
| LoRA targets wrong modules | Low | High | Explicit target_modules list, verification check |
| Numerical drift in eigenvalues | Low | Medium | Use float64 for comparison, tight tolerance |
| Training instability | Low | Low | Conservative learning rate (1e-4), warmup |
| PEFT/Mamba incompatibility | Low | Medium | Fall back to manual LoRA implementation |

---

## 10. Implementation Notes

### 10.1 LoRA Configuration
```python
from peft import LoraConfig, get_peft_model

config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["in_proj", "out_proj"],  # Projections ONLY
    lora_dropout=0.1,
    bias="none"
)
model = get_peft_model(model, config)
```

### 10.2 Eigenvalue Extraction (Reuse from H-M1)
```python
def extract_eigenvalues(model):
    """Extract A_log parameters and compute discrete eigenvalues."""
    eigenvalues = {}
    for name, param in model.named_parameters():
        if 'A_log' in name:
            A_log = param.detach().float()
            lambda_discrete = torch.exp(-torch.exp(A_log))
            eigenvalues[name] = lambda_discrete
    return eigenvalues

def compute_h_spec(eigenvalues):
    """Compute H_spec = -1/log(λ_max) from eigenvalues."""
    global_max_lambda = 0.0
    for name, lambdas in eigenvalues.items():
        max_lambda = lambdas.max().item()
        global_max_lambda = max(global_max_lambda, max_lambda)
    return -1.0 / math.log(global_max_lambda)
```

### 10.3 Preservation Validation
```python
def validate_eigenvalue_preservation(baseline_eigenvalues, post_eigenvalues):
    """Validate H-M2 hypothesis: |ΔH_spec| < 10%."""
    baseline_h_spec = compute_h_spec(baseline_eigenvalues)
    post_h_spec = compute_h_spec(post_eigenvalues)

    delta_h_spec = abs(post_h_spec - baseline_h_spec) / baseline_h_spec * 100

    # Compute eigenvalue correlation
    baseline_flat = torch.cat([v.flatten() for v in baseline_eigenvalues.values()])
    post_flat = torch.cat([v.flatten() for v in post_eigenvalues.values()])
    correlation, _ = pearsonr(baseline_flat.numpy(), post_flat.numpy())

    return {
        'baseline_h_spec': baseline_h_spec,
        'post_h_spec': post_h_spec,
        'delta_h_spec_percent': delta_h_spec,
        'eigenvalue_correlation': correlation,
        'hypothesis_pass': delta_h_spec < 10.0
    }
```

### 10.4 Mechanism Verification
```python
def verify_mechanism(model, lora_config):
    """Verify LoRA correctly targets projections and freezes A_log."""
    trainable_params = [n for n, p in model.named_parameters() if p.requires_grad]

    # Check 1: A_log NOT trainable
    a_log_trainable = any('A_log' in n for n in trainable_params)
    assert not a_log_trainable, "FAIL: A_log should NOT be trainable"

    # Check 2: Projections ARE trainable (via LoRA)
    proj_trainable = any('proj' in n and 'lora' in n for n in trainable_params)
    assert proj_trainable, "FAIL: Projection LoRA adapters should be trainable"

    print("Mechanism verification PASSED: LoRA targets projections only, A_log frozen")
    return True
```

---

## Appendix: Phase 2C Reference

**Source Document:** `02c_experiment_brief.md`
**Hypothesis Statement:** Projection-only LoRA modifies input/output mappings but does not change Ā eigenvalues, preserving the spectral horizon H_spec (|ΔH_spec| < 10%).

**Continuation from H-M1:**
- Same model (Mamba-1.4B) for controlled comparison
- Same dataset (WikiText-103) for consistency
- H_spec baseline = 256.18 tokens (from H-M1)
- Eigenvalue extraction methodology validated

**Research Sources:**
- PEFT Documentation: "The original pretrained weights are kept frozen"
- furiosa-ai/ssm-peft (ICML 2025): "LoRA is not effective at tuning SSM modules" (targets projections)
- state-spaces/mamba Issue #326: A_log parameterization details

---

*Generated by Phase 3 Implementation Planning*
*PRD Version: 1.0*
