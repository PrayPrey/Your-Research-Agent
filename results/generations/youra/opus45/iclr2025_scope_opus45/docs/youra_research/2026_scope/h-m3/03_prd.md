# Product Requirements Document: H-M3

**Hypothesis:** Eigenmode Energy Redistribution via Projection-Only LoRA
**Type:** MECHANISM
**Date:** 2026-03-27
**Author:** Anonymous
**Status:** Draft

---

## 1. Executive Summary

This PRD defines the implementation requirements for validating hypothesis H-M3: demonstrating that projection-only LoRA can redistribute state energy toward slow eigenmodes (ΔE > 0.1 nats), effectively utilizing latent memory capacity without changing eigenvalues.

**Key Deliverable:** An eigenmode energy analyzer that measures energy distribution across SSM eigenmodes before and after LoRA fine-tuning, quantifying energy shift toward slow modes (|λ| > 0.99).

**Success Criterion:** ΔE > 0.1 nats (measurable energy shift toward slow eigenmodes after projection-only LoRA training).

**Theoretical Basis:** While H-M2 proved eigenvalues remain frozen under projection-only LoRA, the *energy distribution* across eigenmodes can change via modified projection matrices. If LoRA redirects input energy toward slow modes (long memory), it could enable task adaptation without spectral surgery.

---

## 2. Problem Statement

### 2.1 Background
H-M2 established that projection-only LoRA preserves eigenvalues (|ΔH_spec| = 0.0000%). This raises a fundamental question: if eigenvalues don't change, HOW does LoRA enable task adaptation? H-M3 proposes the Eigenmode Utilization Hypothesis (EUH): LoRA redistributes energy toward slow eigenmodes that have longer memory retention.

### 2.2 Research Gap
No prior work has measured eigenmode energy distribution changes under LoRA fine-tuning for SSM/Mamba architectures. This is the first empirical test of the EUH mechanism.

### 2.3 Gate Condition
**SHOULD_WORK Gate (G4):** If ΔE > 0.1 nats, EUH is supported. If ΔE ≈ 0, pivot to MHSH (Memory Horizon Separation Hypothesis) - suggesting projection-only LoRA cannot extend effective memory.

---

## 3. Functional Requirements

### FR-1: Baseline Model Loading
- **Description:** Load pretrained Mamba-1.4B model (same as H-M1, H-M2)
- **Source:** state-spaces/mamba-1.4b-hf (HuggingFace)
- **Acceptance:** Model loads without error, forward pass functional

### FR-2: Pre-Training Eigenmode Energy Measurement
- **Description:** Measure energy distribution across eigenmodes BEFORE LoRA fine-tuning
- **Method:**
  1. Register forward hooks on SSM layers to capture hidden states
  2. Compute eigenvalues: λ = exp(-exp(A_log))
  3. Identify slow modes: |λ| > 0.99
  4. Compute energy per mode: E_i = ||h_i||²
  5. Calculate slow mode fraction: E_slow / E_total
- **Output:** Pre-training slow mode fraction (per layer and global average)
- **Acceptance:** Pre-training energy distribution recorded

### FR-3: Dataset Loading
- **Description:** Load WikiText-103 for fine-tuning (consistency with H-M1, H-M2)
- **Source:** HuggingFace Datasets (wikitext/wikitext-103-raw-v1)
- **Preprocessing:**
  - Tokenizer: Mamba tokenizer (GPT-NeoX compatible)
  - Sequence length: 256 tokens (matches H_spec)
  - Training sequences: 500 (PoC configuration)
- **Acceptance:** Training and validation sets prepared

### FR-4: Projection-Only LoRA Configuration
- **Description:** Apply LoRA adapters to projection matrices ONLY (identical to H-M2)
- **LoRA Configuration:**
  - Rank (r): 16
  - Alpha: 32
  - Target modules: ["in_proj", "x_proj"] (projections only!)
  - Dropout: 0.1
  - Bias: "none"
- **Critical Constraint:** A_log parameters must NOT be in trainable parameters
- **Acceptance:** LoRA applied, A_log frozen (verified)

### FR-5: Fine-Tuning Execution
- **Description:** Fine-tune the LoRA-adapted model on WikiText-103
- **Training Protocol:**
  - Optimizer: AdamW (weight_decay=0.01, betas=(0.9, 0.999))
  - Learning Rate: 1e-4 (fixed, no schedule)
  - Batch Size: 2 (effective 16 with gradient accumulation 8)
  - Epochs: 1 (PoC - sufficient for energy redistribution)
  - Loss: Cross-entropy (language modeling)
  - Seed: 42 (fixed)
- **Acceptance:** Training completes without error

### FR-6: Post-Training Eigenmode Energy Measurement
- **Description:** Measure energy distribution AFTER LoRA fine-tuning
- **Method:** Same as FR-2 (identical measurement procedure)
- **Output:** Post-training slow mode fraction (per layer and global average)
- **Acceptance:** Post-training energy distribution recorded

### FR-7: Energy Shift Computation (Gate Metric)
- **Description:** Compute ΔE (energy shift toward slow modes)
- **Metrics:**
  1. Slow mode fraction pre/post
  2. ΔE = post_slow_fraction - pre_slow_fraction
  3. ΔE in nats: -log(1 - min(|ΔE|, 0.99))
- **Success Criteria:** ΔE > 0.1 nats
- **Acceptance:** Gate metric computed and evaluated

### FR-8: Per-Layer Energy Analysis
- **Description:** Analyze energy redistribution at per-layer granularity
- **Output:**
  - Per-layer slow mode fraction (48 layers)
  - Per-layer ΔE
  - Identify layers with largest redistribution
- **Acceptance:** Per-layer analysis complete

### FR-9: Perplexity Validation (Sanity Check)
- **Description:** Verify model still functions after LoRA training
- **Method:** Compute WikiText-103 validation perplexity
- **Expected:** ~15-20 PPL (similar to H-M2)
- **Note:** This validates model integrity, not the hypothesis
- **Acceptance:** Perplexity within reasonable range (< 30 PPL)

### FR-10: Visualization
- **Description:** Generate required figures
- **Required Figures:**
  1. Gate Metrics Comparison: ΔE (actual vs 0.1 nats threshold) bar chart with PASS/FAIL
- **Additional Figures (LLM Autonomous):**
  2. Eigenmode Energy Distribution: Pre vs post histogram
  3. Per-Layer Slow Mode Fraction: 48-layer bar chart (pre vs post)
  4. Eigenvalue Spectrum with Energy Overlay: Scatter plot
  5. Training Loss Curve: Sanity check
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
    return tokenizer(examples["text"], truncation=True, max_length=256)

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
- Complete training + analysis in < 1 hour on single GPU
- Memory usage < 24GB (Mamba-1.4B + LoRA adapters + hooks)

### NFR-2: Reproducibility
- Fixed random seed (42) for all operations
- Deterministic training where possible

### NFR-3: Statistical Validity
- Minimum 500 training sequences (PoC scale)
- Energy measurement on validation set (1000+ sequences)

### NFR-4: Numerical Precision
- Energy computation in float32
- Eigenvalue computation in float32/64

---

## 6. Success Criteria

### Primary Gate (SHOULD_WORK - G4)
| Metric | Target | Threshold |
|--------|--------|-----------|
| ΔE (energy shift) | > 0.1 nats | PASS if ΔE > 0.1 nats |

### Secondary Metrics (Informational)
| Metric | Expected |
|--------|----------|
| Slow Mode Fraction (pre) | Baseline measurement |
| Slow Mode Fraction (post) | Increased if EUH correct |
| Post-training Perplexity | ~15-20 PPL |
| A_log parameters | Unchanged (H-M2 confirmation) |

### Interpretation:
- **ΔE > 0.1 nats:** EUH mechanism confirmed - LoRA redistributes energy to slow modes
- **ΔE ≈ 0:** Energy distribution unchanged - pivot to MHSH hypothesis
- **ΔE < 0:** Energy shifted to fast modes - unexpected, investigate

### Expected Results (EUH Hypothesis):
- ΔE > 0.1 nats
- Slow mode fraction increases after training
- Eigenvalues remain unchanged (H-M2 confirmation)

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
  - CV(H_spec) = 2.22e-16 (input-independent)
- **H-M1:** VALIDATED (MUST_WORK PASS)
  - Degradation ratio = 3.03 > 1.1
  - Eigenvalue-derived H_spec predicts memory behavior
- **H-M2:** VALIDATED (MUST_WORK PASS)
  - |ΔH_spec| = 0.0000% (eigenvalues preserved)
  - A_log frozen during LoRA training
  - LoRA targets: in_proj, x_proj only

### 7.3 External Repositories (Reference)

| Repository | Purpose | Key Reference |
|------------|---------|---------------|
| state-spaces/mamba | Official Mamba implementation | A_log parameter access |
| AmeenAli/HiddenMambaAttn | Hidden state analysis | Energy measurement concepts |
| furiosa-ai/ssm-state-tuning | State-based PEFT | SSM fine-tuning patterns |

---

## 8. Constraints

### 8.1 Resource Constraints
- Single GPU execution (CUDA_VISIBLE_DEVICES)
- LoRA training (parameter-efficient, ~0.1% trainable)

### 8.2 Time Constraints
- Fine-tuning: ~30 minutes for 1 epoch on WikiText-103 subset
- Energy measurement: ~15 minutes (forward pass with hooks)
- Total execution: < 1 hour

### 8.3 Scope Constraints
- MECHANISM hypothesis - tests eigenmode energy redistribution
- Projection-only LoRA (same as H-M2)
- Builds on H-M2 validated eigenvalue preservation

---

## 9. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Hook memory overhead | Medium | Medium | Clear hidden states after measurement |
| Slow mode threshold sensitivity | Medium | Low | Test multiple thresholds (0.95, 0.99, 0.999) |
| Energy metric instability | Low | Medium | Average over multiple samples |
| Training instability | Low | Low | Conservative learning rate (1e-4) |
| PEFT/Mamba incompatibility | Low | Medium | Reuse H-M2 validated configuration |

---

## 10. Implementation Notes

### 10.1 Eigenmode Energy Analyzer (Core Component)
```python
class EigenmodeEnergyAnalyzer:
    """
    Measures energy distribution across SSM eigenmodes.
    ΔE > 0.1 nats indicates significant redistribution toward slow modes.
    """
    def __init__(self, model, config):
        self.model = model
        self.config = config
        self.hooks = []
        self.hidden_states = []

    def register_hooks(self):
        """Register forward hooks on SSM layers to capture hidden states."""
        for layer in self.model.backbone.layers:
            hook = layer.mixer.register_forward_hook(self._capture_state)
            self.hooks.append(hook)

    def _capture_state(self, module, input, output):
        """Capture SSM hidden state for energy analysis."""
        self.hidden_states.append(output.detach())

    def compute_eigenmode_energy(self) -> dict:
        """Compute energy distribution across eigenmodes."""
        results = {'per_layer': [], 'slow_fraction': 0.0}

        for layer_idx, layer in enumerate(self.model.backbone.layers):
            A_log = layer.mixer.A_log.detach().float()
            eigenvalues = torch.exp(-torch.exp(A_log))  # [d_inner, d_state]

            # Identify slow modes: |λ| > 0.99 (long memory retention)
            slow_mask = eigenvalues.abs() > 0.99

            if self.hidden_states:
                state = self.hidden_states[layer_idx]
                mode_energy = (state ** 2).sum(dim=(0, 1))
                slow_energy = mode_energy[slow_mask.any(dim=0)].sum()
                total_energy = mode_energy.sum()
                slow_frac = (slow_energy / total_energy).item()
            else:
                slow_frac = slow_mask.float().mean().item()

            results['per_layer'].append(slow_frac)

        results['slow_fraction'] = sum(results['per_layer']) / len(results['per_layer'])
        return results

    def compute_delta_e(self, pre_energy: dict, post_energy: dict) -> float:
        """Compute energy shift ΔE in nats."""
        pre_frac = pre_energy['slow_fraction']
        post_frac = post_energy['slow_fraction']
        delta_e = abs(post_frac - pre_frac)
        # Convert to nats
        delta_e_nats = -math.log(1 - min(delta_e, 0.99))
        return delta_e_nats
```

### 10.2 LoRA Configuration (Reuse from H-M2)
```python
from peft import LoraConfig, get_peft_model

config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["in_proj", "x_proj"],  # Projections ONLY
    lora_dropout=0.1,
    bias="none"
)
model = get_peft_model(model, config)
```

### 10.3 Training Loop with Energy Measurement
```python
# 1. Pre-training measurement
analyzer = EigenmodeEnergyAnalyzer(model, config)
analyzer.register_hooks()
with torch.no_grad():
    model(sample_input)
pre_energy = analyzer.compute_eigenmode_energy()
analyzer.clear_hooks()

# 2. LoRA fine-tuning (standard training loop)
trainer.train()

# 3. Post-training measurement
analyzer.register_hooks()
with torch.no_grad():
    model(sample_input)
post_energy = analyzer.compute_eigenmode_energy()

# 4. Gate evaluation
delta_e = analyzer.compute_delta_e(pre_energy, post_energy)
gate_pass = delta_e > 0.1  # nats threshold
```

---

## Appendix: Phase 2C Reference

**Source Document:** `02c_experiment_brief.md`
**Hypothesis Statement:** Projection-only LoRA can redistribute state energy toward slow eigenmodes (ΔE > 0.1 nats), effectively utilizing latent memory capacity without changing eigenvalues.

**Continuation from H-M2:**
- Same model (Mamba-1.4B) for controlled comparison
- Same dataset (WikiText-103) for consistency
- Eigenvalues preserved (H-M2 validated)
- LoRA targets: in_proj, x_proj

**Research Sources:**
- HiddenMambaAttn (ACL 2025): Hidden state analysis methods
- furiosa-ai/ssm-state-tuning (ACL 2025): State-based PEFT
- AdaLoRA: SVD-like importance scoring (energy distribution concept)

---

*Generated by Phase 3 Implementation Planning*
*PRD Version: 1.0*
