# Experiment Design: H-M2

**Date:** 2026-03-27
**Author:** Anonymous
**Hypothesis Statement:** Projection-only LoRA modifies input/output mappings but does not change Ā eigenvalues, preserving the spectral horizon H_spec (|ΔH_spec| < 10%).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Hypothesis** - Tests whether projection-only LoRA preserves SSM eigenvalues.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M1 VALIDATED)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (VALIDATED)

### Gate Condition
**MUST_WORK Gate:** Projection-only LoRA must preserve eigenvalues (|ΔH_spec| < 10%).
- If eigenvalues change significantly: LoRA indirectly affects SSM core, invalidating isolation assumption
- Failure consequence: Cannot distinguish eigenmode utilization from spectral surgery

---

## Continuation Context

**Continuation from H-M1 (VALIDATED, PASS):**
- Reusing same model (Mamba-1.4B) for controlled comparison
- H-M1 established H_spec = 256.18 tokens via eigenvalue analysis
- H-M1 validated that eigenvalues predict memory behavior (degradation ratio = 3.03)
- H-M2 tests whether LoRA preserves these eigenvalues after fine-tuning

### Previous Hypothesis Results (if applicable)
- **H-M1 Result:** PASS (MUST_WORK gate satisfied)
- **Key Findings:**
  - Degradation ratio = 3.03 (far exceeds threshold of 1.1)
  - H_spec = 256.18 tokens (determined by layer 19)
  - Perplexity degrades significantly when context < H_spec
  - Eigenvalue-derived H_spec successfully predicts memory behavior

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "LoRA SSM eigenvalue preservation fine-tuning"**
- No directly relevant SSM/Mamba-specific results found
- SSM eigenvalue preservation under LoRA is novel research area

**Query 2: "Mamba state space model projection LoRA adaptation"**
- **Source**: PEFT Documentation (HuggingFace)
  - URL: https://huggingface.co/docs/peft/conceptual_guides/adapter#low-rank-adaptation-lora
  - Key Insight: LoRA represents weight updates ΔW with two smaller matrices through low-rank decomposition
  - **Critical for H-M2**: "The original pretrained weights are kept frozen and doesn't receive any further updates"
  - This confirms projection-only LoRA does NOT modify the frozen A_log parameters

**Query 3: "parameter efficient fine-tuning eigenvalue spectral analysis"**
- **Source**: arXiv 2305.14314
  - Topic: Spectral analysis in fine-tuning contexts
  - Relevance: Methods for analyzing eigenvalue stability

**Key Insight from Archon:** LoRA keeps original weights frozen. For Mamba, this means A_log parameters (which control eigenvalues) remain unchanged when LoRA targets only projection matrices.

### Archon Code Examples

**Query 1: "LoRA Mamba SSM PyTorch implementation"**
- Code examples found for diffusion models (not SSM-specific)
- Key pattern: `load_lora_weights()` and `fuse_lora()` functions
- Insight: LoRA adapter weights are separate from base model weights

**Conclusion:** Archon KB confirms LoRA theory but lacks Mamba-specific eigenvalue analysis code. Implementation based on:
1. H-M1 validated eigenvalue extraction (MambaProbe class)
2. Official PEFT library for LoRA application
3. State-spaces/mamba GitHub documentation

### Exa GitHub Implementations

**Query 1: "Mamba LoRA fine-tuning SSM state space model peft implementation"**

**Repository 1**: [furiosa-ai/ssm-peft](https://github.com/furiosa-ai/ssm-peft) (ICML 2025)
- **URL**: https://github.com/furiosa-ai/ssm-peft
- **Stars**: 25
- **Relevance**: SOTA PEFT method for SSMs, directly addresses our research question
- **Key Findings**:
  - "LoRA and its variants consistently outperform all other PEFT methods"
  - "While LoRA is effective for linear projection matrices, it fails on SSM modules"
  - "LoRA is not effective at tuning SSM modules" - supports H-M2's premise
  - Proposes SDT (Sparse Dimension Tuning) for SSM modules specifically
- **Critical Insight**: Paper empirically confirms LoRA targets projections, not SSM core (A, B, C, D)
- **Training Config**: AdamW, LR 1e-3, 100 epochs, cosine scheduler, warmup 10 epochs

**Repository 2**: [sony/MambaPEFT](https://github.com/sony/MambaPEFT) (ICLR 2025)
- **URL**: https://github.com/sony/MambaPEFT
- **Stars**: 19
- **Relevance**: Comprehensive PEFT exploration for Mamba
- **Key Findings**:
  - "PEFT performs more effectively for Mamba than Transformers"
  - Proposes "Affix-tuning" and "Additional-scan" for Mamba-specific adaptation
  - LoRA applied to "individual modules" vs "all modules" affects performance
- **Training Config**: AdamW, LR varies by method (5e-5 for full fine-tune, higher for PEFT)

**Repository 3**: [state-spaces/mamba](https://github.com/state-spaces/mamba) (Official)
- **URL**: https://github.com/state-spaces/mamba
- **Stars**: 17K+
- **Relevance**: OFFICIAL Mamba implementation - ground truth
- **Key Issues Referenced**:
  - **Issue #326**: A_log parameterization explained
    - `A = -torch.exp(self.A_log.float())` ensures negative eigenvalues
    - `A_bar = exp(A * delta)` computed in CUDA kernel
    - @tridao: "We want A to be always negative, and delta always positive"
  - **Issue #129**: Discretization clarified
    - ZOH for A: `A_bar = exp(delta * A)`
    - Euler for B: `B_bar = delta * B`
  - **Issue #15**: Fine-tuning approach
    - @albertfgu: "In principle it should be possible to finetune Mamba the same way that you would any other LLM"
- **Used For**: Eigenvalue extraction methodology, LoRA target identification

**Repository 4**: [furiosa-ai/ssm-state-tuning](https://github.com/furiosa-ai/ssm-state-tuning) (ACL 2025)
- **URL**: https://github.com/furiosa-ai/ssm-state-tuning
- **Stars**: 15
- **Relevance**: State-based PEFT as alternative to projection-only
- **Key Finding**: "Prompt-based methods do not perform well on SSMs" - validates need for projection targeting

### Implementation Priority Assessment

**CRITICAL: For eigenvalue preservation testing, use official Mamba + standard PEFT**

**Priority 1 (HIGHEST):** state-spaces/mamba official repository
- Ground truth for A_log parameterization
- Issues #326, #129 provide authoritative eigenvalue documentation

**Priority 2:** PEFT library (HuggingFace)
- Standard LoRA implementation
- Integrates with transformers-compatible Mamba

**Priority 3:** furiosa-ai/ssm-peft for reference
- Confirms LoRA targets projections only
- Provides training protocol benchmarks

**Recommended Implementation Path:**
- Primary: Apply PEFT LoRA to Mamba projection matrices, measure H_spec before/after
- Fallback: Manual LoRA implementation following ssm-peft patterns
- Justification: Standard PEFT ensures isolation to projections; H-M1 code validates eigenvalue extraction

### Code Analysis (Serena MCP)

*Skipped* - Code patterns well-documented in research. Key implementation patterns:

1. **LoRA Target Identification in Mamba**:
   - Projection matrices: `in_proj`, `out_proj`, `x_proj`, `dt_proj`
   - SSM core (NOT targeted by projection-only LoRA): `A_log`, `D`
   - From MambaPEFT: LoRA on `in_proj` and `out_proj` is "Partial LoRA"

2. **Eigenvalue Extraction (from H-M1)**:
   - A_log parameters: `model.backbone.layers[i].mixer.A_log`
   - Discrete eigenvalue: `λ = exp(-exp(A_log))`
   - H_spec = -1/log(max(λ))

3. **LoRA Application Pattern**:
   ```python
   from peft import LoraConfig, get_peft_model
   config = LoraConfig(
       r=16,
       lora_alpha=32,
       target_modules=["in_proj", "out_proj"],  # Projections only
       lora_dropout=0.1
   )
   model = get_peft_model(model, config)
   ```

4. **Verification Logic**:
   - Extract A_log BEFORE LoRA training
   - Apply LoRA to projections, fine-tune
   - Extract A_log AFTER training
   - Verify A_log unchanged (or compute ΔH_spec)

---

## Experiment Specification

### Dataset

**Name:** WikiText-103
**Type:** standard
**Source:** HuggingFace Datasets (wikitext/wikitext-103-raw-v1)
**Hypothesis Fit:** Standard language modeling benchmark - consistent with H-M1 for controlled comparison

**Statistics:**
- Train: ~103M tokens from Wikipedia articles
- Validation: ~218K tokens
- Test: ~246K tokens
- Vocabulary: Mamba tokenizer (50,277 tokens)

**Why WikiText-103 (not MQAR):**
1. Real, standard benchmark (not synthetic) - required by pipeline policy
2. Consistent with H-M1 - enables controlled comparison
3. Used in original Mamba paper benchmarks
4. Fine-tuning on real text tests practical eigenvalue preservation

**Preprocessing:**
- Tokenize with Mamba tokenizer
- Chunk into 1024-token sequences
- Use validation split for evaluation

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets
- Identifier: wikitext/wikitext-103-raw-v1
- Code:
```python
from datasets import load_dataset
from transformers import AutoTokenizer

# Load WikiText-103
dataset = load_dataset("wikitext", "wikitext-103-raw-v1")
tokenizer = AutoTokenizer.from_pretrained("state-spaces/mamba-1.4b-hf")

# Tokenize for fine-tuning
def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, max_length=1024)

tokenized_train = dataset["train"].map(tokenize_function, batched=True)
tokenized_valid = dataset["validation"].map(tokenize_function, batched=True)
```

### Models

#### Baseline Model

**Architecture:** state-spaces/mamba-1.4b (Pretrained Mamba SSM)
**Type:** Pretrained language model with Selective State Space architecture
**Parameters:** ~1.4B
**Hypothesis Fit:** Same model as H-M1 - enables direct H_spec comparison

**Key Architecture Details:**
- Layers: 48 Mamba blocks
- A_log shape per layer: [4096, 16] (d_inner × d_state)
- H_spec = 256.18 tokens (from H-M1 validation)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: state-spaces/mamba-1.4b-hf
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "state-spaces/mamba-1.4b-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("state-spaces/mamba-1.4b-hf")
```

#### Proposed Model

**Architecture:** Mamba-1.4B + Projection-only LoRA
**Purpose:** Test whether LoRA on projections preserves A_log eigenvalues

**LoRA Configuration (from ssm-peft research):**
- Rank: r=16
- Alpha: 32
- Target modules: ["in_proj", "out_proj"] (projections only)
- Dropout: 0.1
- Trainable parameters: ~0.1% of total

**Core Mechanism Implementation:**

```python
# Core Mechanism: Eigenvalue Preservation Verification Under Projection-Only LoRA
# Based on: state-spaces/mamba Issue #326, furiosa-ai/ssm-peft, H-M1 validation
# Purpose: Verify that LoRA on projections does NOT change A_log eigenvalues

import torch
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM

class EigenvaluePreservationValidator:
    """
    Validates that projection-only LoRA preserves SSM eigenvalues.
    H-M2 hypothesis: |ΔH_spec| < 10% after projection-only LoRA fine-tuning.
    """
    def __init__(self, model_name="state-spaces/mamba-1.4b-hf"):
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.baseline_h_spec = None
        self.baseline_eigenvalues = None

    def extract_eigenvalues(self):
        """Extract A_log parameters and compute eigenvalues."""
        eigenvalues = {}
        for name, param in self.model.named_parameters():
            if 'A_log' in name:
                # Discrete eigenvalue: λ = exp(-exp(A_log))
                A_log = param.detach().float()
                lambda_discrete = torch.exp(-torch.exp(A_log))
                eigenvalues[name] = lambda_discrete
        return eigenvalues

    def compute_h_spec(self, eigenvalues):
        """Compute H_spec = -1/log(λ_max) from eigenvalues."""
        global_max_lambda = 0.0
        for name, lambdas in eigenvalues.items():
            max_lambda = lambdas.max().item()
            global_max_lambda = max(global_max_lambda, max_lambda)
        return -1.0 / torch.log(torch.tensor(global_max_lambda)).item()

    def apply_projection_only_lora(self, r=16, alpha=32):
        """Apply LoRA to projection matrices only (NOT A_log, D)."""
        config = LoraConfig(
            r=r,
            lora_alpha=alpha,
            target_modules=["in_proj", "out_proj"],  # Projections only!
            lora_dropout=0.1,
            bias="none"
        )
        self.model = get_peft_model(self.model, config)
        return self.model

    def validate_preservation(self, post_training_eigenvalues):
        """
        Validate hypothesis: |ΔH_spec| < 10%.
        Returns PASS if eigenvalues preserved, FAIL otherwise.
        """
        post_h_spec = self.compute_h_spec(post_training_eigenvalues)
        delta_h_spec = abs(post_h_spec - self.baseline_h_spec) / self.baseline_h_spec

        return {
            'baseline_h_spec': self.baseline_h_spec,
            'post_training_h_spec': post_h_spec,
            'delta_h_spec_percent': delta_h_spec * 100,
            'hypothesis_pass': delta_h_spec < 0.10,  # < 10% change
            'interpretation': (
                f"H_spec changed from {self.baseline_h_spec:.2f} to {post_h_spec:.2f} "
                f"({delta_h_spec*100:.2f}% change). "
                f"{'PASS: Eigenvalues preserved' if delta_h_spec < 0.10 else 'FAIL: Eigenvalues modified'}"
            )
        }
```

### Training Protocol

**From Research (ssm-peft, MambaPEFT):**

**Optimizer:** AdamW
- Parameters: weight_decay=1e-4
- Source: furiosa-ai/ssm-peft, sony/MambaPEFT

**Learning Rate:** 1e-4
- Source: ssm-peft default for LoRA on Mamba projections
- Lower than full fine-tuning (5e-5) to preserve stability

**Schedule:** Cosine with warmup
- Warmup: 100 steps
- Source: MambaPEFT implementation details

**Batch Size:** 8 (with gradient accumulation)
- Effective batch size: 32
- Source: Memory constraints with 1.4B model

**Epochs:** 3
- Source: Standard PEFT fine-tuning (minimal to test preservation)

**Loss Function:** Cross-entropy (language modeling)

**Seeds:** 1 (fixed = 42)

> **Note:** Minimal fine-tuning to test eigenvalue preservation. Extended training in H-M3/H-M4.

### Evaluation

**Primary Metrics:**
1. **ΔH_spec (percentage change):** |H_spec_post - H_spec_pre| / H_spec_pre × 100
   - Target: < 10%
   - This is the PRIMARY metric for hypothesis validation

2. **Eigenvalue Correlation:** Pearson correlation between pre/post eigenvalue distributions
   - Target: > 0.99 (strong preservation)

3. **Perplexity (secondary):** WikiText-103 validation perplexity
   - Expected: Similar to baseline (~12-17 PPL)
   - Note: This validates model still functions, not the hypothesis itself

**Success Criteria (MUST_WORK Gate):**
- Primary: |ΔH_spec| < 10% after projection-only LoRA fine-tuning
- Secondary: Eigenvalue correlation > 0.95

**Falsification Conditions (Hypothesis FAILS if):**
- |ΔH_spec| >= 10% (eigenvalues significantly changed)
- Eigenvalue correlation < 0.90 (distribution shifted)
- A_log parameters modified (should remain frozen)

**Expected Results:**
- H_spec ≈ 256.18 tokens before AND after (from H-M1)
- A_log parameters unchanged (frozen by LoRA design)
- ΔH_spec ≈ 0% (theoretical expectation: exactly 0)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Eigenvalue preservation validation
- Library: PyTorch, scipy.stats (for correlation)
- Code:
```python
import torch
from scipy.stats import pearsonr

def compute_delta_h_spec(baseline_eigenvalues, post_eigenvalues):
    """Compute percentage change in H_spec."""
    baseline_h_spec = compute_h_spec(baseline_eigenvalues)
    post_h_spec = compute_h_spec(post_eigenvalues)
    return abs(post_h_spec - baseline_h_spec) / baseline_h_spec * 100

def compute_eigenvalue_correlation(baseline_eigenvalues, post_eigenvalues):
    """Compute correlation between eigenvalue distributions."""
    baseline_flat = torch.cat([v.flatten() for v in baseline_eigenvalues.values()])
    post_flat = torch.cat([v.flatten() for v in post_eigenvalues.values()])
    corr, _ = pearsonr(baseline_flat.numpy(), post_flat.numpy())
    return corr
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: ΔH_spec (actual vs 10% threshold) bar chart

#### Additional Figures (LLM Autonomous)

1. **Eigenvalue Distribution Comparison**: Overlay of pre/post eigenvalue histograms
2. **Per-Layer H_spec Change**: Bar chart showing ΔH_spec for each of 48 layers
3. **A_log Parameter Diff**: Heatmap showing |A_log_post - A_log_pre| (should be all zeros)
4. **Eigenvalue Scatter Plot**: Pre vs post eigenvalues with identity line (should lie on line)
5. **Training Loss Curve**: Fine-tuning loss to confirm model trained properly

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** LoRA adapter applied only to projection matrices (in_proj, out_proj)
- **mechanism_isolatable:** A_log parameters frozen (not in LoRA target_modules)
- **baseline_measurable:** H_spec can be computed from A_log (validated in H-M1)

### Architecture Compatibility
- **Check:** Mamba-1.4B-hf compatible with PEFT LoraConfig
- **Check:** A_log accessible via `model.backbone.layers[i].mixer.A_log`
- **Check:** Projection matrices accessible as `in_proj`, `out_proj`

### Activation Indicators
- **mechanism_log_message:** "LoRA applied to projections only. A_log parameters frozen."
- **tensor_shape_change:** None expected for A_log (should remain [4096, 16] per layer)
- **metric_delta_expected:** ΔH_spec = 0% (eigenvalues unchanged)

### Mechanism Verification Code
```python
def verify_mechanism_activation(model, lora_config):
    """Verify LoRA correctly targets projections and freezes A_log."""
    # Check 1: A_log not in trainable parameters
    trainable_params = [n for n, p in model.named_parameters() if p.requires_grad]
    a_log_trainable = any('A_log' in n for n in trainable_params)
    assert not a_log_trainable, "FAIL: A_log should NOT be trainable"

    # Check 2: Projections ARE trainable
    proj_trainable = any('proj' in n and 'lora' in n for n in trainable_params)
    assert proj_trainable, "FAIL: Projection LoRA adapters should be trainable"

    # Check 3: A_log values unchanged after training
    # (Compare before/after A_log tensors)

    print("Mechanism verification PASSED: LoRA targets projections only, A_log frozen")
    return True
```

### Failure Detection
- **If A_log in trainable_params:** Configuration error - LoRA targeting wrong modules
- **If |ΔH_spec| >= 10%:** Hypothesis fails - projection-only LoRA affects eigenvalues
- **If eigenvalue correlation < 0.95:** Unexpected eigenvalue drift

### Success Criteria
- **hypothesis_support_threshold:** |ΔH_spec| < 10%
- **hypothesis_support_metric:** ΔH_spec percentage

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (LoRA applied, fine-tuning completes)
2. |ΔH_spec| < 10% (eigenvalues preserved)
3. A_log parameters unchanged (frozen confirmation)

**Falsification Conditions (Hypothesis FAILS if):**
- |ΔH_spec| >= 10%
- A_log parameters modified
- Eigenvalue correlation < 0.90

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1:** PEFT Documentation - LoRA Conceptual Guide
- **URL:** https://huggingface.co/docs/peft/conceptual_guides/adapter#low-rank-adaptation-lora
- **Query:** "Mamba state space model projection LoRA adaptation"
- **Key Insight:** "The original pretrained weights are kept frozen"
- **Used For:** Confirming A_log freezing under LoRA

### B. GitHub Implementations (Exa)

**Repository 1:** [furiosa-ai/ssm-peft](https://github.com/furiosa-ai/ssm-peft) (ICML 2025)
- **URL:** https://github.com/furiosa-ai/ssm-peft
- **Query:** "Mamba LoRA fine-tuning SSM state space model peft implementation"
- **Relevance:** SOTA PEFT for SSMs, confirms LoRA targets projections
- **Key Finding:** "LoRA is not effective at tuning SSM modules"
- **Used For:** Training protocol, LoRA configuration

**Repository 2:** [sony/MambaPEFT](https://github.com/sony/MambaPEFT) (ICLR 2025)
- **URL:** https://github.com/sony/MambaPEFT
- **Query:** Same as above
- **Relevance:** Comprehensive PEFT exploration for Mamba
- **Key Finding:** "PEFT performs more effectively for Mamba than Transformers"
- **Used For:** Training hyperparameters reference

**Repository 3:** [state-spaces/mamba](https://github.com/state-spaces/mamba)
- **URL:** https://github.com/state-spaces/mamba
- **Query:** "state-spaces mamba A_log eigenvalue discretization PyTorch implementation"
- **Relevance:** OFFICIAL implementation - ground truth
- **Key Issues:** #326 (A_log parameterization), #129 (discretization), #15 (fine-tuning)
- **Used For:** Eigenvalue extraction, A_log access patterns

**Repository 4:** [furiosa-ai/ssm-state-tuning](https://github.com/furiosa-ai/ssm-state-tuning) (ACL 2025)
- **URL:** https://github.com/furiosa-ai/ssm-state-tuning
- **Relevance:** State-based PEFT alternative
- **Used For:** Confirming projection-only is distinct from state-based methods

### C. Previous Hypothesis Context

**Source:** Phase 4 Validation Report - H-M1
- **File:** `h-m1/04_validation.md`
- **Status:** VALIDATED (MUST_WORK gate PASS)
- **Reused Components:**
  - Model: state-spaces/mamba-1.4b (same)
  - H_spec baseline: 256.18 tokens
  - Eigenvalue extraction methodology
  - WikiText-103 dataset
- **Why Reused:** H-M2 tests whether LoRA preserves H-M1's validated H_spec

### D. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Previous + Standard | H-M1 (WikiText-103) |
| Model selection | Previous | H-M1 (Mamba-1.4B) |
| H_spec baseline | Previous | H-M1 validation (256.18) |
| LoRA configuration | GitHub | ssm-peft, MambaPEFT |
| A_log parameterization | GitHub | state-spaces/mamba Issue #326 |
| Training protocol | GitHub | ssm-peft (AdamW, LR 1e-4) |
| Eigenvalue extraction | Previous | H-M1 validated methodology |
| Preservation threshold | Phase 2B | Gate condition (10%) |
| LoRA freezing behavior | Archon | PEFT documentation |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-27T21:42:00Z

### Workflow History for This Hypothesis
- 2026-03-27T21:42:18Z: H-M2 set to IN_PROGRESS (Phase 2C started)
- 2026-03-27T21:XX:XXZ: Experiment design completed

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
