# Product Requirements Document: H-M2

**Hypothesis:** Middle layers (50-70% depth) achieve highest AUROC exhibiting inverted-U pattern
**Date:** 2026-08-18
**Author:** Anonymous
**Type:** MECHANISM (SHOULD_WORK Gate)

---

## 1. Executive Summary

This PRD specifies implementation requirements for validating that correctness prediction AUROC peaks at middle layers (50-70% depth) of Llama-3-8B-Instruct, demonstrating an inverted-U pattern across layer depths. This MECHANISM hypothesis builds on H-E1 (hidden state encoding) and H-M1 (non-intrusive extraction).

**Success Criteria:** L_60% AUROC > L_100% AUROC (middle beats final layer)

---

## 2. Problem Statement

### 2.1 Context
H-E1 validated that hidden states at layer 19 (~60% depth) encode correctness signal (AUROC=0.8854). H-M1 confirmed non-intrusive extraction (100% identity, -3.4% overhead). H-M2 must now verify that middle layers systematically outperform early and final layers.

### 2.2 Core Problem
Literature suggests correctness/hallucination signals peak at middle layers:
- arxiv 2606.02628: Peak at 40-56% depth for Llama/Mistral
- tool-probe: F1 peaks at ~65-85% depth
- Belief detection: Layer 16/24 (67% depth)

We need empirical verification of inverted-U pattern on our TriviaQA correctness task.

---

## 3. Functional Requirements

### FR-1: Multi-Layer Hidden State Extraction
- Extract hidden states at 8 layer depths: [12.5%, 25%, 37.5%, 50%, 60%, 75%, 87.5%, 100%]
- For Llama-3-8B (32 layers): indices [3, 7, 11, 15, 18, 23, 27, 31]
- Use H-M1's validated HiddenStateExtractor with multi-layer support
- Extract last-token hidden state (B, 4096) per layer

### FR-2: Per-Layer Probe Training
- Train independent LinearProbe per layer
- Architecture: `nn.Linear(4096, 1)` + sigmoid
- Optimizer: AdamW, lr=1e-2, weight_decay=1e-4
- Loss: Binary Cross-Entropy
- Epochs: 10-20 until convergence
- Batch size: 256

### FR-3: Validation-Based Layer Selection
- Train probes on H-E1 train split (9,500 samples)
- Evaluate on H-E1 validation split (1,700 samples)
- Select best layer by validation AUROC
- Compare L_60% vs L_100% vs L_25%

### FR-4: Gate Verification
- Primary: L_60% AUROC > L_100% AUROC
- Secondary: L_60% AUROC > L_25% AUROC
- Pattern: Inverted-U visible in layer-AUROC plot

### FR-5: Statistical Reporting
- AUROC per layer with confidence intervals (bootstrap, n=1000)
- Peak layer identification
- AUROC delta between middle and final layers

---

## 4. Data Specification

### 4.1 Primary Dataset
- **Name:** TriviaQA + Natural Questions (from H-E1)
- **Source:** HuggingFace datasets
- **Train Size:** 9,500 samples
- **Validation Size:** 1,700 samples
- **Auto-download:** Yes

### 4.2 Loading Code
```python
from datasets import load_dataset

# TriviaQA
trivia = load_dataset("trivia_qa", "rc.wikipedia", split="validation")

# Natural Questions (subset)
nq = load_dataset("natural_questions", split="validation[:5000]")
```

### 4.3 Data Reuse
Hidden states from H-E1 can be reused if stored per-layer. Otherwise, re-extract at all 8 target layers using H-M1's validated extraction pipeline.

---

## 5. Model Specification

### 5.1 Base Model
- **Name:** Llama-3-8B-Instruct
- **Source:** `meta-llama/Meta-Llama-3-8B-Instruct`
- **Total Layers:** 32
- **Hidden Dim:** 4096
- **Loading:** float16, device_map="auto"

### 5.2 Probe Model
- **Architecture:** Linear(4096, 1)
- **Per-layer:** Independent probe per layer depth
- **Total probes:** 8 (one per sampled layer)

### 5.3 Loading Code
```python
from transformers import AutoModelForCausalLM
import torch.nn as nn

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    torch_dtype=torch.float16,
    device_map="auto"
)

class LinearProbe(nn.Module):
    def __init__(self, hidden_dim=4096):
        super().__init__()
        self.fc = nn.Linear(hidden_dim, 1)
    
    def forward(self, x):
        return torch.sigmoid(self.fc(x))
```

---

## 6. Success Metrics

### 6.1 Primary Metric (GATE)
- **L_60% AUROC > L_100% AUROC:** True
- **Gate Type:** SHOULD_WORK
- **Fail Action:** Continue with limitation noted

### 6.2 Secondary Metrics
- **L_60% AUROC > L_25% AUROC:** True (middle beats early)
- **Peak Layer Depth:** 50-70% expected
- **AUROC Delta (middle - final):** > 0

### 6.3 Expected Performance (from literature)
- Middle layer (60%): AUROC ~0.85-0.90
- Final layer (100%): AUROC ~0.70-0.80
- Early layer (25%): AUROC ~0.60-0.70

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=2.0.0
transformers>=4.35.0
datasets>=2.14.0
accelerate>=0.24.0
scikit-learn>=1.3.0  # for AUROC calculation
matplotlib>=3.7.0    # for visualization
```

### 7.2 Hardware Requirements
- GPU with 24GB+ VRAM (A100 or equivalent)
- CUDA 11.8+

### 7.3 External References
- sonde: github.com/aniruddh-alt/sonde (layer sweep pattern)
- tool-probe: github.com/oleksandr-shyshchuk/tool-probe (layer F1 peaks)
- arxiv 2606.02628: Hallucination mid-layer decoding paper

---

## 8. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed (42) for all operations
- Deterministic probe training (PyTorch deterministic mode)
- Results reproducible across runs

### NFR-2: Code Quality
- Type hints on all public APIs
- Docstrings with parameter descriptions
- Modular design (extractor, probe, evaluator separate)

### NFR-3: Efficiency
- Batch extraction to minimize forward passes
- GPU-accelerated probe training
- Memory-efficient per-layer processing

---

## 9. Visualization Requirements

### 9.1 Required Figure (Gate Metrics)
- **Bar Chart:** L_25%, L_60%, L_100% AUROC comparison
- **Highlight:** Gate condition (L_60% > L_100%)

### 9.2 Additional Figures
- **Layer-AUROC Curve:** All 8 layers (x=depth %, y=AUROC)
- **Inverted-U Visualization:** Polynomial fit showing peak
- **Confidence Intervals:** Error bars on all AUROC values

All figures saved to: `h-m2/figures/`

---

## 10. Constraints

### 10.1 Scope Constraints
- 8 layer depths sufficient for pattern detection
- Reuse H-E1/H-M1 infrastructure where possible
- Single seed (PoC mode)

### 10.2 Technical Constraints
- Linear probes only (MLP shows <1pp gain per literature)
- Last-token hidden state extraction
- Same dataset splits as H-E1 for comparability

---

## 11. Baseline Models

### 11.1 Internal Baselines
- **Final Layer Probe (L_100%):** Baseline for gate comparison
- **Early Layer Probe (L_25%):** Secondary baseline

### 11.2 No External Baselines
This is an internal mechanism validation. No external model comparisons needed.

---

## 12. Ablation Variants

### 12.1 Layer Granularity
- **Default:** 8 layers (12.5% increments)
- **Ablation:** 16 layers (6.25% increments) if pattern unclear

### 12.2 Pooling Strategy
- **Default:** Last-token hidden state
- **Ablation:** Mean pooling across sequence (if last-token weak)

---

*Generated from Phase 2C Experiment Brief: 02c_experiment_brief.md*
*Prerequisites: H-E1 (AUROC=0.8854), H-M1 (Identity=100%, Overhead=-3.4%)*
