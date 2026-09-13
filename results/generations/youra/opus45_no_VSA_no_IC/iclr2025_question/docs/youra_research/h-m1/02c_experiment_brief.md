# Experiment Design: h-m1

**Date:** 2026-08-24
**Author:** Anonymous
**Hypothesis Statement:** Probes trained on TriviaQA (~11K) achieve AUROC >0.70 when evaluated on TruthfulQA (cross-dataset transfer)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing cross-dataset generalization of uncertainty probes.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-e1 (COMPLETED, PASS)
**Gate Status:** SHOULD_WORK (failure does not block pipeline)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** [h-e1]

### Gate Condition
SHOULD_WORK gate - Success criterion: Cross-dataset AUROC >0.70. Falsification threshold: AUROC <0.60.

---

## Continuation Context

Building on h-e1 which validated that SEPs achieve AUROC within 0.05 of multi-sample SE on TruthfulQA. This experiment tests whether probes trained on a different dataset (TriviaQA) transfer to TruthfulQA.

### Previous Hypothesis Results (if applicable)
h-e1 PASSED - SEP mechanism validated on TruthfulQA with Llama-3-8B-Instruct. Reusing model and evaluation infrastructure.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct results for semantic entropy probes in Archon KB. Primary findings from diffusers/attention-related code not directly applicable to LLM uncertainty probing.

**Relevant Pattern:** Linear probe training on hidden states is standard approach (from h-e1 validation).

### Archon Code Examples

No directly relevant code examples for SEP training found in Archon KB. Relying on Exa GitHub search for authoritative implementation.

### Exa GitHub Implementations

**Repository 1**: OATML/semantic-entropy-probes (Official Implementation)
- **URL**: https://github.com/OATML/semantic-entropy-probes
- **Relevance**: Official codebase for SEP paper - ground truth for reproduction
- **Key Findings**:
  - Uses scikit-learn logistic regression with L2 regularization and LBFGS optimizer
  - Trains on two token positions: TBG (token before generation) and SLT (second-last token)
  - Evaluates on TriviaQA, SQuAD, BioASQ, NQ datasets
  - Models: Llama-2-7B, Llama-2-70B, Mistral-7B, Phi-3 Mini
  - **Cross-dataset transfer explicitly tested in paper**

**Repository 2**: jlko/semantic_uncertainty (Base Implementation)
- **URL**: https://github.com/jlko/semantic_uncertainty
- **Relevance**: Foundation for semantic entropy computation
- **Key Code Pattern**:
  ```python
  python generate_answers.py --model_name=Llama-2-7b-chat --dataset=trivia_qa
  python compute_uncertainty_measures.py
  python analyze_results.py
  ```

**Repository 3**: spotify-research/bayesian-semantic-entropy
- **URL**: https://github.com/spotify-research/bayesian-semantic-entropy
- **Relevance**: Recent extension with efficiency improvements
- **Note**: Uses same data format, compatible with SEP training

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Implementation | Status |
|----------|---------------|--------|
| ⭐⭐⭐ HIGHEST | OATML/semantic-entropy-probes | Official SEP paper repo |
| ⭐⭐ MEDIUM | jlko/semantic_uncertainty | Base SE computation |
| ⭐ LOW | Community reimplementations | Not needed |

**Recommended Implementation Path:**
- Primary: OATML/semantic-entropy-probes official repository
- Fallback: Adapt jlko/semantic_uncertainty pipeline with custom probe training
- Justification: Official implementation provides exact methodology from paper, including cross-dataset evaluation

### Code Analysis (Serena MCP)

*Skipped* - Official implementation is well-documented, no complex code requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Training Dataset: TriviaQA**
- **Name**: TriviaQA
- **Type**: standard
- **Source**: HuggingFace Datasets
- **Samples**: ~11,000 training samples (from paper methodology)
- **Format**: Question-answer pairs for QA evaluation

**Evaluation Dataset: TruthfulQA**
- **Name**: TruthfulQA
- **Type**: standard
- **Source**: HuggingFace Datasets
- **Samples**: 817 questions (full test set)
- **Format**: Questions designed to elicit false beliefs/misconceptions

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets
- Identifier (Train): `trivia_qa` (rc.nocontext split)
- Identifier (Eval): `truthful_qa` (generation split)
- Code:
```python
from datasets import load_dataset

# Training data
trivia_qa = load_dataset("trivia_qa", "rc.nocontext", split="train[:11000]")

# Evaluation data  
truthful_qa = load_dataset("truthful_qa", "generation", split="validation")
```

### Models

#### Baseline Model

**Architecture**: Llama-3-8B-Instruct (from h-e1)
- **Type**: Pretrained LLM
- **Source**: HuggingFace Transformers
- **Hidden Size**: 4096
- **Layers**: 32

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `meta-llama/Meta-Llama-3-8B-Instruct`
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

**Architecture:** Baseline LLM + Linear Probe (SEP)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Semantic Entropy Probe (SEP)
# Based on: OATML/semantic-entropy-probes official implementation

from sklearn.linear_model import LogisticRegression
import numpy as np

class SemanticEntropyProbe:
    """
    Linear probe predicting semantic entropy from LLM hidden states.
    Trained on TriviaQA, evaluated on TruthfulQA (cross-dataset transfer).
    """
    def __init__(self, layer_idx=-1, token_position='last'):
        self.layer_idx = layer_idx  # Which layer to probe
        self.token_position = token_position  # 'last' or 'tbg'
        self.probe = LogisticRegression(
            solver='lbfgs',
            max_iter=1000,
            C=1.0  # L2 regularization (default)
        )
    
    def extract_hidden_states(self, model, tokenizer, questions, answers):
        """Extract hidden states at specified layer and position."""
        hidden_states = []
        for q, a in zip(questions, answers):
            inputs = tokenizer(q + " " + a, return_tensors="pt")
            with torch.no_grad():
                outputs = model(**inputs, output_hidden_states=True)
            # Get hidden state at layer_idx, token_position
            h = outputs.hidden_states[self.layer_idx][:, -1, :]  # (1, hidden_dim)
            hidden_states.append(h.cpu().numpy())
        return np.vstack(hidden_states)
    
    def train(self, hidden_states, semantic_entropy_labels):
        """Train probe on TriviaQA hidden states."""
        # Binarize SE labels: high SE = 1, low SE = 0
        binary_labels = (semantic_entropy_labels > np.median(semantic_entropy_labels)).astype(int)
        self.probe.fit(hidden_states, binary_labels)
    
    def predict_proba(self, hidden_states):
        """Predict probability of high semantic entropy."""
        return self.probe.predict_proba(hidden_states)[:, 1]

# Integration: Probe trained on TriviaQA, evaluated on TruthfulQA
```

### Training Protocol

**Probe Training (on TriviaQA)**:
- **Algorithm**: Logistic Regression (scikit-learn)
- **Optimizer**: LBFGS (default)
- **Regularization**: L2 with C=1.0 (default)
- **Max Iterations**: 1000
- **Source**: OATML/semantic-entropy-probes paper methodology

**Hidden State Generation**:
- **Model**: Llama-3-8B-Instruct
- **Temperature**: 1.0 (for SE computation)
- **Num Generations**: 5 (for computing ground-truth SE labels)
- **Layer Selection**: Validated on held-out set (typically layer 20-28 for 32-layer model)
- **Token Position**: Last token of answer

**Data Split**:
- TriviaQA: 11,000 samples for training, no validation needed for LogisticRegression
- TruthfulQA: 817 samples for evaluation (zero overlap with training)

### Evaluation

**Primary Metric**: AUROC for hallucination detection
- Predicted: Probe's predicted probability of high SE
- Ground Truth: Model correctness (binary)

**Success Criteria**:
- Cross-dataset AUROC > 0.70 (trained on TriviaQA, evaluated on TruthfulQA)

**Falsification Threshold**:
- Cross-dataset AUROC < 0.60

**Expected Baseline Performance** (from SEP paper):
- In-distribution AUROC: ~0.75-0.85
- Cross-dataset transfer expected to degrade ~0.05-0.10
- Source: OATML/semantic-entropy-probes paper Table 2

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary Classification (hallucination detection)
- Library: sklearn.metrics
- Code:
```python
from sklearn.metrics import roc_auc_score

auroc = roc_auc_score(correctness_labels, probe_predictions)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Cross-dataset AUROC vs threshold (0.70) bar chart

#### Additional Figures (LLM Autonomous)

1. **ROC Curve**: True Positive Rate vs False Positive Rate for cross-dataset evaluation
2. **Layer Analysis**: AUROC by layer (showing which layers encode transferable uncertainty)
3. **Calibration Plot**: Predicted probability vs actual accuracy
4. **Distribution Comparison**: Probe output distributions for TriviaQA vs TruthfulQA

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists**: TRUE - SEP is a linear probe on hidden states
- **mechanism_isolatable**: TRUE - Probe is separate from base model
- **baseline_measurable**: TRUE - Random/untrained probe provides baseline

### Architecture Compatibility
- Llama-3-8B hidden states are 4096-dimensional
- LogisticRegression handles arbitrary input dimensions
- No architectural modifications to base model needed

### Activation Indicators
- **mechanism_log_message**: "SEP probe trained on {n_samples} TriviaQA samples"
- **tensor_shape_change**: Hidden states (N, 4096) → Predictions (N,)
- **metric_delta_expected**: AUROC > 0.50 (better than random)

### Verification Code
```python
def verify_mechanism_activation(probe, test_hidden_states, test_labels):
    """Verify probe produces meaningful predictions."""
    predictions = probe.predict_proba(test_hidden_states)
    
    # Check 1: Predictions are not constant
    assert np.std(predictions) > 0.01, "Probe outputs constant predictions"
    
    # Check 2: Better than random
    auroc = roc_auc_score(test_labels, predictions)
    assert auroc > 0.50, f"AUROC {auroc:.3f} not better than random"
    
    # Check 3: Cross-dataset transfer
    print(f"Cross-dataset AUROC: {auroc:.3f}")
    return auroc > 0.70  # Gate threshold
```

### Success Criteria
- **hypothesis_support_threshold**: AUROC > 0.70
- **hypothesis_support_metric**: Cross-dataset AUROC (TriviaQA → TruthfulQA)

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Cross-dataset AUROC > 0.70 (trained on TriviaQA, evaluated on TruthfulQA)

---

## Appendix: Reference Implementations

### Primary Reference
- **Paper**: "Semantic Entropy Probes: Robust and Cheap Hallucination Detection in LLMs"
- **Repository**: https://github.com/OATML/semantic-entropy-probes
- **DOI**: https://doi.org/10.48550/arxiv.2406.15927

### Supporting References
- **Semantic Uncertainty Base**: https://github.com/jlko/semantic_uncertainty
- **Nature Paper**: "Detecting Hallucinations in Large Language Models Using Semantic Entropy" (Farquhar et al., 2024)
- **TruthfulQA Dataset**: Lin, Hilton, and Evans 2022
- **TriviaQA Dataset**: Joshi et al. 2017

### Key Code Snippets

**From OATML/semantic-entropy-probes:**
```python
# Linear probe training (from latent-probe.ipynb)
from sklearn.linear_model import LogisticRegression
probe = LogisticRegression(solver='lbfgs', max_iter=1000)
probe.fit(hidden_states, semantic_entropy_labels)
```

**From jlko/semantic_uncertainty:**
```python
# Semantic ID clustering
def get_semantic_ids(strings_list, model, strict_entailment=False):
    """Group predictions into semantic meaning clusters."""
    # Uses DeBERTa for NLI-based equivalence detection
    ...
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-24

### Workflow History for This Hypothesis
- Phase 2C started: 2026-08-24
- Experiment design completed: 2026-08-24

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in OATML/semantic-entropy-probes official implementation*
*Next Phase: Phase 3 - Implementation Planning*
