# Experiment Design: h-e1

**Date:** 2026-03-28
**Author:** Anonymous
**Hypothesis Statement:** A probe trained on hidden states with semantic similarity auxiliary signal produces meaningful SE predictions (rho >= 0.3) on the same model it was trained on
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (none required - foundation hypothesis)
**Gate Status:** MUST_WORK - Failure stops entire workflow

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
IF rho < 0.3: ABANDON (fundamental approach invalid)

---

## Continuation Context

This is the foundation hypothesis (h-e1). No previous hypothesis results are required.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in verification chain.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "semantic entropy probe hidden states uncertainty"**
- Results primarily returned diffusers/attention code (not directly relevant)
- One relevant result: OpenReview paper on uncertainty estimation (similarity: 0.34)
- Key insight: Archon KB does not contain SEP-specific implementations; relying on Exa for primary research

**Query 2: "LLM probe training hidden state prediction"**
- Results returned diffuser training examples
- No direct SEP implementations found in Archon KB
- Conclusion: Primary implementation guidance from Exa GitHub search

### Archon Code Examples

**Query: "semantic entropy probe PyTorch"**
- No direct SEP code examples in Archon KB
- Found general PyTorch patterns for model loading and device management
- Conclusion: Use official OATML implementation from GitHub as primary source

### Exa GitHub Implementations

**Repository 1**: [OATML/semantic-entropy-probes](https://github.com/OATML/semantic-entropy-probes) (Official Implementation)
- **URL**: https://github.com/OATML/semantic-entropy-probes
- **Relevance**: **PRIMARY SOURCE** - Official implementation by paper authors (Kossen et al., 2024)
- **Architecture**: Linear logistic regression probes trained on LLM hidden states
- **Key Code**:
  - `generate_answers.py`: Sample responses and extract hidden states
  - `compute_uncertainties.py`: Compute SE via DeBERTa NLI clustering
  - `train-latent-probe.ipynb`: Train linear probes to predict SE
- **Training Config**:
  - Probe: Logistic regression (scikit-learn) with L2 regularization
  - Optimizer: LBFGS (default sklearn)
  - Token positions: TBG (Token Before Generation), SLT (Selected Layer Token)
  - Layers: Middle-to-late layers (e.g., layers 23-27 for Llama-3-8B)
- **Dataset**: TriviaQA, TruthfulQA, SQuAD, BioASQ, NQ Open
- **Results**: SEPs achieve AUROC close to full SE with single-pass inference
- **Software**: Python 3.11, PyTorch 2.1

**Repository 2**: [jlko/semantic_uncertainty](https://github.com/jlko/semantic_uncertainty) (408 stars)
- **URL**: https://github.com/jlko/semantic_uncertainty
- **Relevance**: Base codebase for SE computation (Nature paper, Farquhar et al.)
- **Key Code**:
  - `semantic_entropy.py`: Core SE computation with NLI clustering
  - `get_semantic_ids()`: Cluster generations by semantic equivalence
  - `predictive_entropy_rao()`: Compute weighted entropy over clusters
- **Entailment Model**: DeBERTa-Large for bidirectional entailment checking
- **SE Computation**: `H_SE = -sum(p_i * log(p_i))` over semantic clusters
- **Dataset Loading**: HuggingFace datasets integration

**Repository 3**: [AlexanderVNikitin/kernel-language-entropy](https://github.com/AlexanderVNikitin/kernel-language-entropy)
- **URL**: https://github.com/AlexanderVNikitin/kernel-language-entropy
- **Relevance**: Alternative SE method using kernel-based similarity (NeurIPS'24)
- **Key Insight**: Semantic similarity can be encoded via positive semidefinite kernels
- **Relevance to SEDP**: Supports the hypothesis that similarity structure aids uncertainty estimation

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Source | Rationale |
|----------|--------|-----------|
| 1 (PRIMARY) | OATML/semantic-entropy-probes | Official SEP implementation by paper authors |
| 2 (FALLBACK) | jlko/semantic_uncertainty | Base SE computation, same research group |
| 3 (REFERENCE) | kernel-language-entropy | Similarity-based approach validation |

**Recommended Implementation Path:**
- Primary: Adapt OATML/semantic-entropy-probes for SEDP (add similarity auxiliary signal)
- Fallback: Build on jlko/semantic_uncertainty if SEP repo has compatibility issues
- Justification: Official implementation ensures correctness; same authors, same codebase structure

### Code Analysis (Serena MCP)

*Skipped* - Code from Exa search results (official OATML repository) provides sufficient clarity:
- SEPs use simple linear logistic regression (sklearn)
- Hidden states extracted from specific token positions (TBG, SLT)
- Target: Binarized SE labels from semantic clustering
- No complex custom layers requiring deep analysis

---

## Experiment Specification

### Dataset

**Name:** TruthfulQA
**Type:** standard
**Source:** https://huggingface.co/datasets/truthfulqa/truthful_qa

**Statistics:**
- Total questions: 817
- Categories: 38 (health, law, finance, politics, etc.)
- Train split: ~653 questions (80%)
- Test split: ~164 questions (20%)
- Question types: Adversarial questions designed to elicit false beliefs

**Preprocessing:**
- Load via HuggingFace: `load_dataset("truthfulqa/truthful_qa", "generation")`
- Extract question field for prompting
- No text augmentation (preserve original question semantics)

**Hypothesis Fit:**
- Standard benchmark for hallucination detection
- Used in original SEP paper (Kossen et al., 2024)
- Questions designed to test LLM truthfulness/uncertainty

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `truthfulqa/truthful_qa`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("truthfulqa/truthful_qa", "generation")
train_data = dataset["validation"]  # TruthfulQA uses validation as main split
# Create train/test split
train_test = train_data.train_test_split(test_size=0.2, seed=42)
```

### Models

#### Baseline Model

**Architecture:** Semantic Entropy Probe (SEP) - Hidden states only
**Description:** Linear probe trained on LLM hidden states to predict SE, WITHOUT similarity auxiliary signal

**Configuration:**
- LLM: Llama-3-8B-Instruct (meta-llama/Meta-Llama-3-8B-Instruct)
- Probe: Logistic Regression (sklearn, L2 regularization)
- Input: Hidden states from layer 25 (of 32), TBG token position
- Output: Binary SE prediction (high/low uncertainty)
- Entailment Model: DeBERTa-v3-large for SE label generation

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `meta-llama/Meta-Llama-3-8B-Instruct`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto",
    output_hidden_states=True
)
```

#### Proposed Model

**Architecture:** SE-Distilled Probe (SEDP) - Hidden states + Similarity auxiliary signal

**Core Mechanism Implementation:**

```python
# Core Mechanism: SEDP (Semantic Entropy Distilled Probe with Similarity)
# Based on: OATML/semantic-entropy-probes + similarity augmentation

import torch
import torch.nn as nn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SEDPProbe:
    """
    SE-Distilled Probe with Semantic Similarity Auxiliary Signal.
    Extends SEP by incorporating pairwise similarity structure.
    """
    def __init__(self, hidden_dim: int, similarity_weight: float = 0.5):
        self.hidden_dim = hidden_dim
        self.similarity_weight = similarity_weight
        self.probe = LogisticRegression(max_iter=1000, C=1.0)

    def compute_similarity_features(self, hidden_states: np.ndarray,
                                     response_embeddings: np.ndarray) -> np.ndarray:
        """
        Compute similarity structure from response set embeddings.
        Args:
            hidden_states: (N, hidden_dim) - LLM hidden states per question
            response_embeddings: (N, n_responses, embed_dim) - response embeddings
        Returns:
            (N, hidden_dim + sim_features) - augmented features
        """
        # Compute pairwise similarity matrix for each question's responses
        sim_features = []
        for i in range(len(response_embeddings)):
            sim_matrix = cosine_similarity(response_embeddings[i])
            # Extract summary statistics: mean, std, min, max of similarities
            sim_stats = [sim_matrix.mean(), sim_matrix.std(),
                        sim_matrix.min(), sim_matrix.max()]
            sim_features.append(sim_stats)

        sim_features = np.array(sim_features)
        # Concatenate hidden states with similarity features
        augmented = np.concatenate([hidden_states, sim_features], axis=1)
        return augmented

    def fit(self, hidden_states: np.ndarray, response_embeddings: np.ndarray,
            se_labels: np.ndarray):
        """Train probe on augmented features."""
        X = self.compute_similarity_features(hidden_states, response_embeddings)
        self.probe.fit(X, se_labels)

    def predict(self, hidden_states: np.ndarray,
                response_embeddings: np.ndarray) -> np.ndarray:
        """Predict SE from augmented features."""
        X = self.compute_similarity_features(hidden_states, response_embeddings)
        return self.probe.predict_proba(X)[:, 1]

# Integration: Use after extracting hidden states from Llama-3-8B layer 25
# Input: hidden_states (N, 4096), response_embeddings (N, 20, 768)
# Output: SE predictions (N,) - correlation with true SE
```

### Training Protocol

**Data Generation:**
- Generate N=20 responses per question using Llama-3-8B-Instruct (temp=0.7)
- Extract hidden states from layer 25, TBG token position
- Compute true SE labels via DeBERTa-v3 NLI clustering
- Compute response embeddings for similarity features

**Probe Training:**
- Optimizer: LBFGS (sklearn default)
- Regularization: L2 (C=1.0)
- Train/Test split: 80/20 (~653/164 questions)
- Seeds: 1 (fixed at 42)

**Hyperparameters:**
| Parameter | Value | Source |
|-----------|-------|--------|
| N responses | 20 | SEP paper (Kossen et al.) |
| Temperature | 0.7 | SEP paper |
| Layer | 25 (of 32) | SEP paper recommendation |
| Token position | TBG | SEP paper |
| Similarity weight | 0.5 | New parameter (to be validated) |

> ⚠️ **EXISTENCE (PoC)**: Single seed, fixed hyperparameters. No grid search.

### Evaluation

**Primary Metrics:**
- Spearman correlation (rho) between predicted SE and true SE
- AUROC for hallucination detection (binary: high/low SE)

**Success Criteria:**
- **PoC Pass**: SEDP rho > SEP baseline rho (effect direction positive)
- **Gate Pass**: SEDP rho >= 0.3 (meaningful correlation)
- **Target**: rho >= 0.7 (matches Phase 2A prediction)

**Expected Baseline Performance** (from SEP paper):
- SEP AUROC: ~0.85 (within 2-3% of full SE)
- Full SE AUROC: 0.76-0.97 on TruthfulQA
- First-token entropy: rho = 0.13 with SE (weak baseline)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Regression (SE prediction) + Binary classification (hallucination)
- Library: scipy.stats, sklearn.metrics
- Code:
```python
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

# Spearman correlation
rho, p_value = spearmanr(predicted_se, true_se)

# AUROC
auroc = roc_auc_score(binary_se_labels, predicted_se)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing rho values
  - X-axis: Methods (SEP baseline, SEDP proposed)
  - Y-axis: Spearman rho
  - Horizontal line at rho=0.3 (gate threshold)

#### Additional Figures (LLM Autonomous)
Based on EXISTENCE hypothesis type, recommended:
1. **Scatter plot**: Predicted SE vs True SE (both methods)
2. **ROC curves**: Hallucination detection performance comparison

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. SEDP rho > SEP baseline rho (positive effect direction)

**Gate Pass Condition:**
- SEDP rho >= 0.3 (MUST_WORK gate)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Note:** Archon KB did not contain direct SEP implementations. Searches returned general attention/diffuser code.

### B. GitHub Implementations (Exa)

**Repository 1**: OATML/semantic-entropy-probes (PRIMARY)
- **URL**: https://github.com/OATML/semantic-entropy-probes
- **Query Used**: "OATML semantic-entropy-probes Kossen hidden states probe training"
- **Relevance**: Official implementation by paper authors
- **Used For**: Probe architecture, training protocol, evaluation metrics

**Repository 2**: jlko/semantic_uncertainty (408 stars)
- **URL**: https://github.com/jlko/semantic_uncertainty
- **Query Used**: "jlko semantic_uncertainty semantic entropy LLM"
- **Relevance**: Base SE computation codebase (Nature paper)
- **Used For**: SE label generation, NLI clustering implementation

**Repository 3**: AlexanderVNikitin/kernel-language-entropy
- **URL**: https://github.com/AlexanderVNikitin/kernel-language-entropy
- **Query Used**: Found via related work in Exa results
- **Relevance**: Validates similarity-based uncertainty estimation approach
- **Used For**: Theoretical support for similarity augmentation

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from official repository sufficiently clear

### D. Previous Hypothesis Context

**Previous Context**: None - this is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2A + Exa | TruthfulQA (SEP paper) |
| Baseline model | Exa GitHub | OATML/semantic-entropy-probes |
| Proposed mechanism | Hypothesis + KLE paper | Similarity augmentation |
| Pseudo-code | Exa + Custom | OATML repo + custom SEDP |
| Training protocol | Exa GitHub | SEP paper defaults |
| Evaluation metrics | Phase 2B + Exa | Spearman rho, AUROC |
| Hyperparameters | Exa GitHub | SEP paper (Kossen et al.) |

### F. Paper Citations

1. Kossen, J., Han, J., Razzak, M., Schut, L., Malik, S., & Gal, Y. (2024). Semantic Entropy Probes: Robust and Cheap Hallucination Detection in LLMs. arXiv:2406.15927
2. Farquhar, S., Kossen, J., Kuhn, L., & Gal, Y. (2024). Detecting hallucinations in large language models using semantic entropy. Nature.
3. Nikitin, A., et al. (2024). Kernel Language Entropy: Fine-grained Uncertainty Quantification for LLMs. NeurIPS.

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-28

### Workflow History for This Hypothesis
- 2026-03-28T20:02:00Z: Pipeline initialized, Phase 2B completed
- 2026-03-28T20:14:05Z: Hypothesis h-e1 set to IN_PROGRESS
- 2026-03-28: Phase 2C experiment design completed

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
