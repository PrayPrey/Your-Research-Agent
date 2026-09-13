# Experiment Design: h-e1

**Date:** 2026-08-24
**Author:** Anonymous
**Hypothesis Statement:** SEPs achieve AUROC within 0.05 of multi-sample SE on Llama-3-8B, Mistral-7B, Qwen-2-7B on TruthfulQA (817 samples)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (none required)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK — Failure blocks entire pipeline. Success: AUROC gap ≤0.05 for 2/3 families, none >0.10.

---

## Continuation Context

First hypothesis in verification DAG. No prior results to build upon.

### Previous Hypothesis Results (if applicable)
N/A — This is the root hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Semantic entropy probes hallucination detection**
- Limited direct results; found reference to semantic entropy paper (arxiv 2305.14314)
- Key insight: Semantic entropy captures uncertainty in meaning space across multiple generations

**Query 2: LLM uncertainty quantification hidden states**
- Found HuggingFace papers page (hf.co/papers/2305.14314) covering SE methodology
- Key insight: Hidden states at upper-intermediate layers (~2/3 depth) best encode uncertainty

**Query 3: TruthfulQA linear probe classification**
- Found TensorFlow datasets reference for loading
- Key insight: Standard QA benchmarks available via datasets libraries

### Archon Code Examples

Limited direct code examples for SEP mechanism in Archon KB. Code patterns found:
- Hidden state extraction patterns
- Linear probe training approaches
- PyTorch model architecture patterns

### Exa GitHub Implementations

**🎯 OFFICIAL IMPLEMENTATION FOUND:**

**Repository 1**: OATML/semantic-entropy-probes (⭐ Official)
- **URL**: https://github.com/OATML/semantic-entropy-probes
- **Relevance**: HIGHEST — Official implementation by paper authors (Kossen et al.)
- **Architecture**: Linear probe (logistic regression) on hidden states
- **Key Code Structure**:
  - `generate_answers.py`: Sample responses + extract hidden states
  - `compute_uncertainties.py`: Compute semantic entropy metrics
  - `train_latent-probe.ipynb`: Train SEPs on hidden states
- **Token Positions**: TBG (Token Before Generation), SLT (Second Last Token)
- **Training**: Logistic regression on (hidden_state, binarized_SE) pairs
- **Results**: SEPs retain high AUROC for hallucination detection

**Repository 2**: ss8319/SEP
- **URL**: https://github.com/ss8319/SEP
- **Relevance**: HIGH — Replication study
- **Datasets**: TriviaQA, SQuAD, BioASQ, NQ Open
- **Metrics**: AUROC for SE prediction and hallucination detection

**Repository 3**: LiquidGunay/semantic-entropy-probe-comparison
- **URL**: https://github.com/LiquidGunay/semantic-entropy-probe-comparison
- **Relevance**: HIGH — Qwen model support, full pipeline
- **Architecture**: Accuracy probe, SE probe, entropy baseline
- **Tools**: vLLM for generation, nnsight for hidden state tracing
- **Results**: SE probe 0.95 AUROC, accuracy probe 1.00 AUROC (smoke test)

**Repository 4**: itsmemala/CLAP
- **URL**: https://github.com/itsmemala/CLAP
- **Relevance**: MEDIUM — Includes SEP baseline implementation
- **Models**: gemma_7B, implements layer-wise SEP probes
- **Token positions**: prompt_last, answer_last

**Repository 5**: zazamrykh/internal_probing
- **URL**: https://github.com/zazamrykh/internal_probing
- **Relevance**: HIGH — Multi-model support (Qwen-3, Mistral-7B, Falcon)
- **Methods**: Linear Probe, PEP (Prompt Embedding Probe), Semantic Entropy
- **Datasets**: TriviaQA, GSM8K, NQ-Open, SQuAD, BioASQ

**Additional Finding**: arxiv.org/html/2606.02628v1
- Linear probe on mid-layer hidden states achieves 0.904–1.000 AUROC
- Peak layers: blocks 13–18 of 32 for Llama/Mistral, blocks 19–25 of 28 for Qwen
- MLP ≈ Linear (difference ≤0.01 AUROC) — truthfulness signal is approximately linear

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Source | Justification |
|----------|--------|---------------|
| 1 (HIGHEST) | OATML/semantic-entropy-probes | Official implementation by paper authors |
| 2 | zazamrykh/internal_probing | Multi-model support including our target models |
| 3 | LiquidGunay/semantic-entropy-probe-comparison | Full pipeline with Qwen support |
| 4 | itsmemala/CLAP | SEP baseline with layer-wise analysis |

**Recommended Implementation Path:**
- Primary: Adapt OATML/semantic-entropy-probes methodology
- Fallback: Use zazamrykh/internal_probing for multi-model extension
- Justification: Official implementation ensures methodological fidelity; internal_probing already supports Mistral/Qwen families

### Code Analysis (Serena MCP)

*Serena analysis skipped — sufficient code patterns from Exa GitHub search. Official implementation provides clear methodology.*

---

## Experiment Specification

### Dataset

**Evaluation Dataset: TruthfulQA**
- **Name:** TruthfulQA
- **Type:** standard (real benchmark)
- **Source:** HuggingFace Datasets
- **Size:** 817 questions
- **Purpose:** Evaluate hallucination detection AUROC
- **Hypothesis Fit:** Designed to elicit plausible-but-false answers — ideal for testing uncertainty probes

**Training Dataset: TruthfulQA (train split)**
- **Name:** TruthfulQA
- **Split:** train (80%) / val (20%) from 817 questions
- **Purpose:** Train SEP linear probes

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets
- Identifier: `truthful_qa` (generation subset)
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("truthful_qa", "generation")
# 817 questions total
```

### Models

#### Target Models (3 Families)

| Model | HuggingFace ID | Hidden Dim | Layers |
|-------|----------------|------------|--------|
| Llama-3-8B-Instruct | `meta-llama/Meta-Llama-3-8B-Instruct` | 4096 | 32 |
| Mistral-7B-Instruct-v0.2 | `mistralai/Mistral-7B-Instruct-v0.2` | 4096 | 32 |
| Qwen-2-7B-Instruct | `Qwen/Qwen2-7B-Instruct` | 3584 | 28 |

#### Baseline Model

**Multi-Sample Semantic Entropy (5 samples)**
- Generate 5 responses per question at temperature T=0.7
- Cluster responses by semantic equivalence (NLI-based)
- Compute entropy over cluster distribution
- Use SE score for hallucination detection (AUROC)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: See table above
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
```

#### Proposed Model

**Architecture:** Semantic Entropy Probe (SEP) — Linear classifier on hidden states

**Core Mechanism Implementation:**

```python
# Core Mechanism: Semantic Entropy Probe (SEP)
# Based on: OATML/semantic-entropy-probes (Kossen et al., 2024)

import torch
import torch.nn as nn
from sklearn.linear_model import LogisticRegression

class SemanticEntropyProbe:
    """
    Linear probe predicting binarized semantic entropy from hidden states.
    Single-pass inference: no multi-sample generation needed at test time.
    """
    def __init__(self, layer_idx: int, token_position: str = "last"):
        """
        Args:
            layer_idx: Transformer layer to extract hidden states from
            token_position: "last" (SLT) or "tbg" (token before generation)
        """
        self.layer_idx = layer_idx
        self.token_position = token_position
        self.probe = LogisticRegression(max_iter=1000, C=1.0)
    
    def extract_hidden_state(self, model, input_ids, attention_mask):
        """Extract hidden state at specified layer and position."""
        with torch.no_grad():
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                output_hidden_states=True
            )
        # Shape: (batch, seq_len, hidden_dim)
        hidden = outputs.hidden_states[self.layer_idx]
        
        if self.token_position == "last":
            # Last token position (SLT)
            seq_lens = attention_mask.sum(dim=1) - 1
            h = hidden[torch.arange(hidden.size(0)), seq_lens]
        else:  # "tbg"
            # Token before generation start
            h = hidden[:, -1, :]
        
        return h.cpu().numpy()  # (batch, hidden_dim)
    
    def fit(self, hidden_states, se_labels):
        """Train probe on (hidden_state, binarized_SE) pairs."""
        # se_labels: 1 if SE > threshold (high uncertainty), else 0
        self.probe.fit(hidden_states, se_labels)
    
    def predict_proba(self, hidden_states):
        """Return P(high_SE) for hallucination detection."""
        return self.probe.predict_proba(hidden_states)[:, 1]

# Integration: Applied to frozen LLM hidden states
# Layer selection: ~2/3 depth (layer 20-22 for 32-layer, 18-20 for 28-layer)
```

### Training Protocol

**SEP Training (Per Model):**
- **Method:** Logistic Regression (sklearn)
- **Input:** Hidden states at layer L, token position P
- **Target:** Binarized semantic entropy (threshold at median)
- **Regularization:** C=1.0 (L2)
- **Layer Selection:** Validate on held-out set, select best layer

**Semantic Entropy Computation (for training labels):**
- **Samples per question:** 5 (temperature=0.7)
- **Clustering:** NLI-based semantic equivalence (DeBERTa-v3-large-mnli)
- **Entropy:** H_SE = -Σ p(c) log p(c) over clusters
- **Binarization:** threshold at median H_SE

**Seeds:** 1 (fixed for PoC)

### Evaluation

**Primary Metric:** AUROC for hallucination detection
- Compare SEP AUROC vs Multi-sample SE AUROC per model family

**Success Criteria (EXISTENCE PoC):**
```
gap = |AUROC_SEP - AUROC_SE|
SUCCESS if:
  - gap ≤ 0.05 for at least 2/3 model families
  - gap ≤ 0.10 for all model families
```

**Expected Baseline Performance** (from research):
- Multi-sample SE: ~0.70-0.85 AUROC on TruthfulQA (varies by model)
- Linear probes on hidden states: 0.904-1.000 AUROC (arxiv 2606.02628)
- SEP paper reports SEP matches SE within ~0.05 gap

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification (hallucination detection)
- Library: sklearn.metrics
- Code:
```python
from sklearn.metrics import roc_auc_score
auroc = roc_auc_score(y_true, y_pred_proba)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: AUROC bar chart — SEP vs SE baseline for each model family

#### Additional Figures (LLM Autonomous)
- AUROC gap heatmap across layers (for layer selection analysis)
- Per-model family comparison table
- Hidden state visualization (optional, if time permits)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** SEP probe (linear classifier) trained and loadable
- **mechanism_isolatable:** Yes — probe is separate from frozen LLM
- **baseline_measurable:** Yes — multi-sample SE computed independently

### Architecture Compatibility
- **Hidden state extraction:** Requires `output_hidden_states=True` in model forward
- **Layer access:** All 3 model families support hidden state access via HuggingFace
- **Token positions:** SLT (last token) accessible via attention mask

### Activation Indicators
- **mechanism_log_message:** `"SEP probe prediction: P(high_SE) = {prob:.3f}"`
- **tensor_shape_change:** Input: `(batch, hidden_dim)` → Output: `(batch,)` probability
- **metric_delta_expected:** AUROC difference ≤0.05 from baseline SE

### Mechanism Verification Code
```python
def verify_sep_mechanism(sep_probe, model, sample_input):
    """Verify SEP mechanism activates correctly."""
    # 1. Extract hidden state
    h = sep_probe.extract_hidden_state(model, sample_input['input_ids'], sample_input['attention_mask'])
    assert h.shape == (1, model.config.hidden_size), f"Unexpected shape: {h.shape}"
    
    # 2. Get prediction
    prob = sep_probe.predict_proba(h)[0]
    assert 0 <= prob <= 1, f"Invalid probability: {prob}"
    
    # 3. Log activation
    print(f"SEP probe prediction: P(high_SE) = {prob:.3f}")
    return True
```

### Success Thresholds
- **hypothesis_support_threshold:** AUROC gap ≤ 0.05 for 2/3 families
- **hypothesis_support_metric:** `max(|AUROC_SEP - AUROC_SE|)` across families

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on all 3 model families
2. SEP AUROC within 0.05 of multi-sample SE for at least 2/3 families
3. No family shows gap > 0.10

---

## Appendix: Reference Implementations

### Primary Reference
- **OATML/semantic-entropy-probes** (Official)
  - URL: https://github.com/OATML/semantic-entropy-probes
  - Paper: Kossen et al., "Semantic Entropy Probes: Robust and Cheap Hallucination Detection in LLMs" (2024)
  - arXiv: 2406.15927

### Secondary References
- **zazamrykh/internal_probing**
  - URL: https://github.com/zazamrykh/internal_probing
  - Multi-model support (Qwen, Mistral, Falcon)

- **LiquidGunay/semantic-entropy-probe-comparison**
  - URL: https://github.com/LiquidGunay/semantic-entropy-probe-comparison
  - Qwen support, vLLM integration

- **itsmemala/CLAP**
  - URL: https://github.com/itsmemala/CLAP
  - SEP baseline, layer-wise analysis

### Related Papers
- Farquhar et al. (2024): Semantic Entropy (Nature)
- arxiv 2606.02628: Hallucination Is Linearly Decodable from Mid-Layer Hidden States
- Lin et al. (2021): TruthfulQA benchmark

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-24

### Workflow History for This Hypothesis
- 2026-08-24: Phase 2C initiated
- 2026-08-24: Archon KB search completed
- 2026-08-24: Exa GitHub search completed — official OATML repo found
- 2026-08-24: Experiment specification synthesized

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
