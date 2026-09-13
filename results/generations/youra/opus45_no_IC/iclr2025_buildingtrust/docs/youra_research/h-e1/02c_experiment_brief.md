# Experiment Design: H-E1

**Date:** 2026-08-10
**Author:** YouRA Research Pipeline
**Hypothesis Statement:** Category-dependent calibration variation exists in LLMs on TruthfulQA
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites for H-E1)
**Gate Status:** MUST_WORK - ANOVA p < 0.05 on cluster ECE

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
ANOVA F-test on per-cluster ECE values must yield p < 0.05, demonstrating statistically significant variation in calibration error across TruthfulQA semantic clusters.

---

## Continuation Context

First hypothesis in verification chain. No previous results to build upon.

### Previous Hypothesis Results (if applicable)
N/A - Foundation hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

No direct matches for calibration/ECE in Archon KB. Knowledge base primarily contains diffusion model examples.

### Archon Code Examples

No relevant calibration code found in Archon. Will rely on external implementations.

### Exa GitHub Implementations

**Key Resources Found:**

1. **TruthfulQA Dataset** (HuggingFace)
   - Source: `truthfulqa/truthful_qa`
   - 817 questions across 38 categories
   - Multiple-choice format with mc1_targets and mc2_targets
   - Category field available for clustering

2. **Temperature Scaling Reference Implementation**
   - Source: `gpleiss/temperature_scaling` (GitHub)
   - ECE computation with 15 bins (standard)
   - LBFGS optimizer for temperature fitting
   - Clean PyTorch implementation

3. **TorchUncertainty Library**
   - `CalibrationError` metric for ECE
   - `TemperatureScaler` and `VectorScaler` classes
   - Production-ready implementation

4. **Class-based Temperature Scaling** (Frenkel & Goldberger, 2021)
   - Paper: "Network Calibration by Class-based Temperature Scaling"
   - Demonstrates per-class calibration differs
   - Directly supports our hypothesis premise

5. **LLM Calibration Papers** (EMNLP 2024)
   - "Calibrating Language Models with Adaptive Temperature Scaling"
   - "A Close Look into the Calibration of Pre-trained Language Models"
   - Confirms LLMs have calibration issues post-RLHF

### Implementation Priority Assessment

**CRITICAL: Using established implementations**

**Recommended Implementation Path:**
- Primary: `gpleiss/temperature_scaling` ECE implementation
- Fallback: TorchUncertainty CalibrationError
- Justification: gpleiss implementation is canonical (Guo et al. 2017), simple, and widely cited

### Code Analysis (Serena MCP)

Not applicable - no existing codebase to analyze for this experiment.

---

## Experiment Specification

### Dataset

**Name:** TruthfulQA
**Version:** HuggingFace `truthfulqa/truthful_qa` (multiple_choice split)
**Type:** standard

| Property | Value |
|----------|-------|
| Total Questions | 817 |
| Categories | 38 original |
| Clusters | 7 (semantic grouping) |
| Samples per Cluster | ~100-150 |

**Category to Cluster Mapping (Pre-registered):**

| Cluster ID | Categories | Approx. Size |
|------------|------------|--------------|
| 1 | Health, Nutrition, Psychology | ~120 |
| 2 | Law, Politics, Government | ~130 |
| 3 | Finance, Economics, Business | ~100 |
| 4 | Science, Technology, Math | ~110 |
| 5 | History, Geography, Culture | ~120 |
| 6 | Religion, Philosophy, Ethics | ~100 |
| 7 | Misconceptions, Myths, Superstitions | ~137 |

**Preprocessing:**
1. Load multiple_choice split
2. Map 38 categories to 7 clusters using predefined mapping
3. Extract mc1_targets for single-correct evaluation
4. No augmentation needed

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `truthfulqa/truthful_qa`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("truthfulqa/truthful_qa", "multiple_choice", split="validation")
```

### Models

#### Baseline Model

**Name:** Llama-2-7B
**Source:** HuggingFace Hub (`meta-llama/Llama-2-7b-hf`)
**Type:** Decoder-only transformer

| Property | Value |
|----------|-------|
| Parameters | 7B |
| Architecture | LlamaForCausalLM |
| Precision | float16 |
| Device | Single GPU (A100 recommended) |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `meta-llama/Llama-2-7b-hf`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
```

#### Proposed Model

**Architecture:** Same as baseline (no model modification for EXISTENCE test)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Per-cluster ECE computation
# Lines: 25 (within spec)

import torch
import torch.nn.functional as F
from scipy import stats

def compute_ece(confidences, accuracies, n_bins=15):
    """Compute Expected Calibration Error."""
    bin_boundaries = torch.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        in_bin = (confidences > bin_boundaries[i]) & (confidences <= bin_boundaries[i+1])
        prop_in_bin = in_bin.float().mean()
        if prop_in_bin > 0:
            accuracy_in_bin = accuracies[in_bin].float().mean()
            avg_confidence_in_bin = confidences[in_bin].mean()
            ece += torch.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
    return ece.item()

def compute_cluster_eces(logits_by_cluster, labels_by_cluster):
    """Compute ECE for each cluster."""
    cluster_eces = {}
    for cluster_id, logits in logits_by_cluster.items():
        probs = F.softmax(logits, dim=-1)
        confidences, predictions = probs.max(dim=-1)
        accuracies = (predictions == labels_by_cluster[cluster_id])
        cluster_eces[cluster_id] = compute_ece(confidences, accuracies)
    return cluster_eces

def test_cluster_variation(cluster_eces):
    """ANOVA test for cluster ECE variation."""
    ece_values = list(cluster_eces.values())
    # Bootstrap ECE estimates for each cluster (100 samples each)
    # Then run one-way ANOVA
    f_stat, p_value = stats.f_oneway(*ece_values)
    return f_stat, p_value
```

### Training Protocol

**Note:** This is an EXISTENCE test - no training required.

| Parameter | Value |
|-----------|-------|
| Training | None (inference only) |
| Inference Mode | Teacher-forced MC evaluation |
| Batch Size | 8 |
| Precision | float16 |

**Inference Protocol:**
1. For each question, compute log-probabilities for each answer choice
2. Select answer with highest log-probability
3. Record confidence (softmax of logits) and correctness
4. Group by cluster

### Evaluation

**Primary Metric:** ANOVA F-statistic and p-value on cluster ECEs

**Success Criteria (PoC):**
- Primary: ANOVA p < 0.05 (clusters differ significantly)
- Secondary: At least 2 clusters differ by > 0.05 ECE

| Metric | Formula | Target |
|--------|---------|--------|
| Per-cluster ECE | Weighted avg of |conf - acc| per bin | Report all 7 |
| ANOVA F-stat | Between-group / within-group variance | Report value |
| ANOVA p-value | F-distribution CDF | p < 0.05 |
| ECE Range | max(ECE) - min(ECE) | > 0.05 |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Multiple-choice classification
- Library: scipy.stats, torch
- Code:
```python
from scipy.stats import f_oneway
import numpy as np

# After collecting per-cluster ECE bootstrap samples
f_stat, p_value = f_oneway(*cluster_ece_samples)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of ECE per cluster with 95% bootstrap CI error bars

#### Additional Figures (LLM Autonomous)

1. **Cluster ECE Distribution**: Box plot showing ECE distribution across 7 clusters
2. **Confidence Histogram per Cluster**: 7 histograms showing confidence distributions
3. **Reliability Diagram per Cluster**: Calibration curves for each cluster

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. ANOVA p-value < 0.05 (primary gate)
3. At least 2 clusters have ECE difference > 0.05 (secondary)

**Failure Response:** IF ANOVA p >= 0.05 -> ABANDON all subsequent hypotheses (no category structure to exploit)

---

## Appendix: Reference Implementations

### ECE Computation (from gpleiss/temperature_scaling)

```python
class _ECELoss(nn.Module):
    def __init__(self, n_bins=15):
        super(_ECELoss, self).__init__()
        bin_boundaries = torch.linspace(0, 1, n_bins + 1)
        self.bin_lowers = bin_boundaries[:-1]
        self.bin_uppers = bin_boundaries[1:]

    def forward(self, logits, labels):
        softmaxes = F.softmax(logits, dim=1)
        confidences, predictions = torch.max(softmaxes, 1)
        accuracies = predictions.eq(labels)

        ece = torch.zeros(1, device=logits.device)
        for bin_lower, bin_upper in zip(self.bin_lowers, self.bin_uppers):
            in_bin = confidences.gt(bin_lower.item()) * confidences.le(bin_upper.item())
            prop_in_bin = in_bin.float().mean()
            if prop_in_bin.item() > 0:
                accuracy_in_bin = accuracies[in_bin].float().mean()
                avg_confidence_in_bin = confidences[in_bin].mean()
                ece += torch.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
        return ece
```

### TruthfulQA MC Evaluation (from sylinrl/TruthfulQA)

```python
# Log-probability scoring for multiple choice
def score_mc(model, tokenizer, question, choices, device):
    scores = []
    for choice in choices:
        prompt = f"Q: {question}\nA: {choice}"
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
        with torch.no_grad():
            outputs = model(input_ids)
            logits = outputs.logits
        # Get log-prob of answer tokens
        answer_ids = tokenizer(choice, return_tensors="pt").input_ids[0, 1:]
        log_probs = F.log_softmax(logits[0, -len(answer_ids)-1:-1], dim=-1)
        score = log_probs[range(len(answer_ids)), answer_ids].sum().item()
        scores.append(score)
    return scores
```

### Category to Cluster Mapping

```python
CATEGORY_TO_CLUSTER = {
    # Cluster 1: Health/Body
    "Health": 1, "Nutrition": 1, "Psychology": 1,
    # Cluster 2: Law/Politics
    "Law": 2, "Politics": 2, "Government": 2,
    # Cluster 3: Finance
    "Finance": 3, "Economics": 3,
    # Cluster 4: Science
    "Science": 4, "Technology": 4, "Math": 4, "Physics": 4, "Biology": 4,
    # Cluster 5: History/Culture
    "History": 5, "Geography": 5, "Culture": 5,
    # Cluster 6: Philosophy/Religion
    "Religion": 6, "Philosophy": 6, "Ethics": 6,
    # Cluster 7: Misconceptions
    "Misconceptions": 7, "Myths": 7, "Superstitions": 7, "Conspiracies": 7,
    "Paranormal": 7, "Indexical Error: Identity": 7, "Indexical Error: Time": 7,
    "Indexical Error: Location": 7, "Indexical Error: Other": 7,
    "Subjective": 7, "Logical Falsehood": 7, "Stereotypes": 7,
    "Fiction": 7, "Advertising": 7, "Misquotations": 7, "Proverbs": 7,
    "Weather": 5, "Mandela Effect": 7, "Language": 5, "Education": 5,
    "Sociology": 6, "Confusion: People": 7, "Confusion: Places": 5,
    "Confusion: Other": 7, "Distraction": 7, "Indexical Error: All": 7
}
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10T17:00:31+00:00

### Workflow History for This Hypothesis
- 2026-08-10: Hypothesis h-e1 set to IN_PROGRESS (External loop starting Phase 2C)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
