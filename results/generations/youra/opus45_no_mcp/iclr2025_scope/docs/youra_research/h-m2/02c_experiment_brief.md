# Experiment Design: H-M2

**Date:** 2026-08-19
**Author:** PrayPrey
**Hypothesis Statement:** Under Mamba's selective scan operation, if state evolution follows sequential token processing, then loss landscape exhibits lower sharpness for sequential reasoning tasks compared to retrieval tasks.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis Template** - Tests task-dependent sharpness patterns in SSM architecture.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M1 VALIDATED)
**Gate Status:** MUST_WORK - sharpness_ratio < 0.8

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (VALIDATED - 219% sharpness change)

### Gate Condition

**Primary:** Sequential task sharpness < Retrieval task sharpness (ratio < 0.8)
**Secondary:** Gradient flow shows more stable convergence for sequential tasks

---

## Continuation Context

This experiment continues the mechanism chain from H-M1, which demonstrated:
- SAM sharpness: Transformer -1.952, Mamba 2.332 (219.4% delta)
- KL divergence: 2.847 (threshold: >0.1)
- Sign flip indicates fundamentally different landscape geometry
- Mamba exhibits ~18x smaller gradient norms

H-M2 tests whether this landscape difference manifests as task-dependent patterns within Mamba.

### Previous Hypothesis Results (H-M1)

| Metric | Transformer | Mamba | Delta |
|--------|-------------|-------|-------|
| Sharpness | -1.952 | 2.332 | 219.4% |
| Top Eigenvalue | 913.94 | 51.52 | 0.056 ratio |
| KL Divergence | - | 2.847 | PASS |

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable - using established research knowledge*

**Query 1: Sharpness Measurement in Mamba**
- SAM (Sharpness-Aware Minimization, Foret et al. 2021) provides established methodology
- Perturbation-based sharpness with epsilon=0.05 is standard
- Works for any differentiable model including SSMs

**Query 2: Task-Dependent Loss Landscapes**
- Loss landscape geometry varies with task structure (Hochreiter & Schmidhuber 1997, Fort et al. 2019)
- Sequential tasks follow recurrence patterns naturally in SSM state evolution
- Retrieval tasks require arbitrary token-to-token lookups (misaligned with SSM sequential flow)

**Query 3: Mamba Selective Scan Analysis**
- Mamba-2 (Dao & Gu 2024) establishes SSM-attention duality
- Selective scan operates sequentially: h_t = f(h_{t-1}, x_t)
- State compression favors local/sequential patterns over random access

### Archon Code Examples

**SAM Implementation Pattern (PyTorch)**
```python
# From Foret et al. 2021, adapted for landscape measurement
def compute_sharpness(model, data_loader, epsilon=0.05):
    model.eval()
    base_loss = compute_loss(model, data_loader)
    
    # Perturb in gradient direction
    for p in model.parameters():
        if p.grad is not None:
            p.data += epsilon * p.grad / (p.grad.norm() + 1e-12)
    
    perturbed_loss = compute_loss(model, data_loader)
    
    # Restore parameters
    for p in model.parameters():
        if p.grad is not None:
            p.data -= epsilon * p.grad / (p.grad.norm() + 1e-12)
    
    sharpness = perturbed_loss - base_loss
    return sharpness
```

### Exa GitHub Implementations

*MCP unavailable - using known implementations*

**Repository 1:** state-spaces/mamba
- **URL:** https://github.com/state-spaces/mamba
- **Relevance:** Official Mamba implementation
- **Architecture:** Selective SSM with hardware-aware scan
- **Key Code:** `mamba_ssm` module with efficient CUDA kernels

**Repository 2:** huggingface/transformers
- **URL:** https://github.com/huggingface/transformers
- **Relevance:** Standard benchmark evaluation pipelines
- **Datasets:** GSM8K, Natural Questions loaders

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

1. **Primary:** state-spaces/mamba official repo - ground truth for Mamba architecture
2. **Secondary:** HuggingFace transformers for benchmark loading
3. **Tertiary:** Custom SAM sharpness measurement module

**Recommended Implementation Path:**
- Primary: state-spaces/mamba for model
- Fallback: mamba-ssm PyPI package
- Justification: Official implementation ensures correct selective scan behavior

### Code Analysis (Serena MCP)

*Serena unavailable - using documented architecture analysis*

**Mamba Selective Scan Structure:**
- Input: (B, L, D) batch, sequence, features
- State: (B, D, N) hidden state evolving through sequence
- Output: (B, L, D) transformed features

**Key Observation:** State evolution is inherently sequential - cannot look back arbitrarily like attention.

---

## Experiment Specification

### Dataset

**Dataset 1: GSM8K (Sequential Reasoning)**
- **Name:** GSM8K (Grade School Math 8K)
- **Type:** standard
- **Source:** HuggingFace Datasets
- **Path:** `gsm8k`
- **Retrieval Density:** 0.1 (low - sequential reasoning)
- **Test Size:** 1,319 samples
- **Hypothesis Fit:** Sequential multi-step reasoning requires carrying information forward through chain-of-thought, aligning with SSM state evolution

**Dataset 2: Natural Questions (Retrieval-Heavy)**
- **Name:** Natural Questions
- **Type:** standard
- **Source:** HuggingFace Datasets
- **Path:** `natural_questions`
- **Retrieval Density:** 0.9 (high - requires factual lookup)
- **Test Size:** 3,610 samples
- **Hypothesis Fit:** Retrieval tasks require random access to facts in context, misaligned with sequential SSM flow

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `gsm8k`, `natural_questions`
- Code:
```python
from datasets import load_dataset
gsm8k = load_dataset("gsm8k", "main", split="test")
nq = load_dataset("natural_questions", split="validation[:3610]")
```

### Models

#### Baseline Model

**Architecture:** Mamba (state-spaces/mamba)
**Type:** Selective State Space Model
**Parameters:** ~2.8B (mamba-2.8b-hf)
**Source:** HuggingFace / state-spaces

**Loading Information** (for Phase 4 download):
- Method: HuggingFace
- Identifier: `state-spaces/mamba-2.8b-hf`
- Code:
```python
from transformers import MambaForCausalLM, AutoTokenizer
model = MambaForCausalLM.from_pretrained("state-spaces/mamba-2.8b-hf")
tokenizer = AutoTokenizer.from_pretrained("state-spaces/mamba-2.8b-hf")
```

#### Proposed Model

**Architecture:** Mamba + LoRA (same base, different task)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Task-Specific Sharpness Measurement
# Purpose: Compare loss landscape sharpness across task types on Mamba

import torch
import torch.nn as nn

class TaskSpecificSharpnessAnalyzer:
    """
    Measures SAM sharpness for Mamba model on different task types.
    Tests H-M2: sequential tasks should show lower sharpness.
    """
    def __init__(self, model, epsilon=0.05):
        self.model = model
        self.epsilon = epsilon
        
    def compute_sharpness(self, dataloader, max_batches=100):
        """
        Compute SAM sharpness: max_||delta||<=epsilon L(w+delta) - L(w)
        """
        self.model.eval()
        total_sharpness = 0.0
        n_batches = 0
        
        for batch in dataloader:
            if n_batches >= max_batches:
                break
                
            # Forward pass for base loss
            outputs = self.model(**batch)
            base_loss = outputs.loss
            base_loss.backward()
            
            # Compute perturbation direction (gradient ascent)
            grad_norm = 0.0
            for p in self.model.parameters():
                if p.grad is not None:
                    grad_norm += p.grad.data.norm(2).item() ** 2
            grad_norm = grad_norm ** 0.5
            
            # Apply perturbation
            for p in self.model.parameters():
                if p.grad is not None:
                    p.data += self.epsilon * p.grad / (grad_norm + 1e-12)
            
            # Compute perturbed loss
            with torch.no_grad():
                perturbed_outputs = self.model(**batch)
                perturbed_loss = perturbed_outputs.loss
            
            # Restore and accumulate
            for p in self.model.parameters():
                if p.grad is not None:
                    p.data -= self.epsilon * p.grad / (grad_norm + 1e-12)
            
            self.model.zero_grad()
            total_sharpness += (perturbed_loss - base_loss).item()
            n_batches += 1
            
        return total_sharpness / n_batches
    
    def compare_tasks(self, sequential_loader, retrieval_loader):
        """
        Compare sharpness between sequential and retrieval tasks.
        Returns ratio and verdict.
        """
        seq_sharpness = self.compute_sharpness(sequential_loader)
        ret_sharpness = self.compute_sharpness(retrieval_loader)
        
        ratio = seq_sharpness / (ret_sharpness + 1e-12)
        
        return {
            "sequential_sharpness": seq_sharpness,
            "retrieval_sharpness": ret_sharpness,
            "ratio": ratio,
            "gate_pass": ratio < 0.8
        }
```

### Training Protocol

**Note:** H-M2 is a measurement hypothesis, not a training hypothesis. The protocol measures sharpness on fine-tuned models.

**LoRA Fine-tuning (for both tasks):**
- **Optimizer:** AdamW
- **Learning Rate:** 2e-4 (standard LoRA)
- **Schedule:** Linear warmup (6% steps) + linear decay
- **Batch Size:** 16
- **Epochs:** 3
- **LoRA Config:** rank=16, alpha=32, target_modules=["in_proj", "out_proj"]
- **Loss:** Cross-entropy (language modeling)
- **Seeds:** 1 (single seed for PoC)

**Sharpness Measurement:**
- **Method:** SAM perturbation
- **Epsilon:** 0.05
- **Batches:** 100 per task
- **Source:** From H-M1 validated methodology

### Evaluation

**Primary Metrics:**
- Sequential Task Sharpness (GSM8K)
- Retrieval Task Sharpness (NQ)
- Sharpness Ratio (seq/ret)

**Success Criteria:**
- Primary: sharpness_ratio < 0.8
- Secondary: Gradient variance lower for sequential task

**Expected Values (from H-M1 context):**
- Mamba overall sharpness: ~2.33 (from H-M1)
- Expected sequential: lower sharpness due to aligned information flow
- Expected retrieval: higher sharpness due to misaligned access patterns

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: landscape analysis
- Library: custom (SAM-based)
- Code:
```python
# Custom sharpness metric from experiment specification
def evaluate_gate(results):
    ratio = results["sequential_sharpness"] / results["retrieval_sharpness"]
    return {
        "ratio": ratio,
        "pass": ratio < 0.8,
        "sequential_sharpness": results["sequential_sharpness"],
        "retrieval_sharpness": results["retrieval_sharpness"]
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing sharpness for GSM8K vs NQ with 0.8 ratio threshold line

#### Additional Figures (LLM Autonomous)

1. **Sharpness Distribution:** Histogram of per-batch sharpness values for each task
2. **Gradient Flow:** Gradient norm over fine-tuning steps for both tasks
3. **Sharpness vs Retrieval Density:** Scatter plot if extended to more tasks

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** True - SAM sharpness measurement is established
- **mechanism_isolatable:** True - Can measure sharpness per task independently
- **baseline_measurable:** True - H-M1 established baseline measurement methodology

### Architecture Compatibility
- Mamba selective scan compatible with SAM perturbation
- Forward/backward passes work normally with SSM
- LoRA adaptation applies to SSM projections (in_proj, out_proj)

### Activation Indicators
- **Log Message:** "Sharpness computed: GSM8K={val}, NQ={val}, ratio={val}"
- **Tensor Shape Change:** Gradient tensors match model parameter shapes
- **Metric Delta Expected:** |sharpness_gsm8k - sharpness_nq| > 0.1

### Mechanism Verification Code
```python
def verify_mechanism(results):
    """Verify H-M2 mechanism is actually being tested"""
    checks = {
        "sharpness_computed": results["sequential_sharpness"] is not None,
        "tasks_differentiated": abs(results["sequential_sharpness"] - 
                                     results["retrieval_sharpness"]) > 0.01,
        "ratio_meaningful": 0 < results["ratio"] < 10,
        "gate_evaluable": "gate_pass" in results
    }
    return all(checks.values()), checks
```

### Success Threshold
- **hypothesis_support_metric:** sharpness_ratio
- **hypothesis_support_threshold:** < 0.8

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `sequential_sharpness < retrieval_sharpness * 0.8`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1:** SAM Paper (Foret et al. 2021)
- **Type:** Foundational methodology
- **Relevance:** Sharpness measurement standard
- **Used For:** Sharpness computation algorithm

**Source 2:** Mamba Paper (Gu & Dao 2023)
- **Type:** Architecture definition
- **Relevance:** Selective scan mechanism
- **Used For:** Model architecture, state evolution understanding

**Source 3:** Mamba-2 (Dao & Gu 2024)
- **Type:** SSM-attention duality theory
- **Relevance:** Explains why SSM favors sequential patterns
- **Used For:** Hypothesis rationale

### B. GitHub Implementations (Exa)

**Repository 1:** state-spaces/mamba
- **URL:** https://github.com/state-spaces/mamba
- **Used For:** Model loading, architecture reference

**Repository 2:** huggingface/transformers
- **URL:** https://github.com/huggingface/transformers
- **Used For:** Dataset loading, tokenization

### C. Code Analysis (Serena)

*Serena unavailable - analysis based on published documentation and H-M1 validated methodology*

### D. Previous Hypothesis Context

**Source:** H-M1 04_validation.md
- **Reused Components:**
  - SAM sharpness methodology (epsilon=0.05)
  - Mamba model configuration
  - Batch size and evaluation setup
- **Why Reused:** Enables controlled comparison - only task type changes

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Sharpness measurement | Literature | Foret et al. 2021 |
| Dataset selection | Phase 2B | 02b_verification_plan.md |
| Model architecture | GitHub | state-spaces/mamba |
| LoRA config | Phase 2B / H-E1 | Established config |
| Evaluation protocol | Previous | H-M1 validated |
| Gate condition | Phase 2B | 02b_verification_plan.md |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis

- H-M1 VALIDATED: 219% sharpness change, KL divergence 2.847
- H-M2 IN_PROGRESS: Experiment design phase

---

*MCP Tools Used: None (NO MCP mode)*
*Research basis: Literature knowledge, H-M1 results, Phase 2B plan*
*All specifications grounded in established methods and previous hypothesis results*
*Next Phase: Phase 3 - Implementation Planning*
