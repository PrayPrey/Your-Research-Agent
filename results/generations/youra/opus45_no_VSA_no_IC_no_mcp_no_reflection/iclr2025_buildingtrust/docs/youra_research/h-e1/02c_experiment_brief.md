# Experiment Design: h-e1

**Date:** 2026-08-28
**Author:** PrayPrey
**Hypothesis Statement:** Both semantic entropy and self-consistency detect hallucinations above random baseline (AUROC > 0.55) on TruthfulQA
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (none required)
**Gate Status:** MUST_WORK - AUROC > 0.55 for both methods

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
Both semantic entropy and self-consistency must achieve AUROC > 0.55 on TruthfulQA hallucination detection (above chance + margin). If either method fails, fundamental implementation or method flaw suspected.

---

## Continuation Context

First hypothesis in chain. No previous context.

### Previous Hypothesis Results (if applicable)
N/A - This is the first hypothesis (h-e1)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Archon MCP unavailable in this session. Web search used as fallback.*

**Key Findings from Literature:**
1. Semantic entropy (Kuhn et al. 2023) achieves AUROC ~0.75-0.85 on TruthfulQA
2. SelfCheckGPT (Manakul et al. 2023) achieves AUROC ~0.70-0.80 on WikiBio
3. Both methods require N=5-20 samples per query for reliable uncertainty estimation

### Archon Code Examples

*Archon MCP unavailable. GitHub implementations found via web search.*

### Exa GitHub Implementations

**[VERIFIED - WEB]** lorenzkuhn/semantic_uncertainty
- URL: https://github.com/lorenzkuhn/semantic_uncertainty
- Language: Python (PyTorch)
- Relevance: **Official implementation** of semantic entropy from Kuhn et al. 2023
- Key Features: NLI-based clustering, Deberta-v3-large, entropy computation
- Last Updated: Active (Nature 2024 paper update)

**[VERIFIED - WEB]** potsawee/selfcheckgpt
- URL: https://github.com/potsawee/selfcheckgpt
- Language: Python
- Relevance: **Official implementation** of SelfCheckGPT
- Key Features: 5 methods (BERTScore, MQAG, Unigram, NLI, GPT-Prompt)
- PyPI: `pip install selfcheckgpt`

**[VERIFIED - WEB]** OATML/semantic-entropy-probes
- URL: https://github.com/OATML/semantic-entropy-probes
- Language: Python (PyTorch 2.1, Python 3.11)
- Relevance: Efficient single-generation semantic entropy approximation

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Implementation | Justification |
|----------|---------------|---------------|
| 1 | lorenzkuhn/semantic_uncertainty | Official, matches paper exactly |
| 2 | potsawee/selfcheckgpt | Official, pip-installable |
| 3 | Custom from paper specs | Fallback if repos unavailable |

**Recommended Implementation Path:**
- Primary: Use official repos (semantic_uncertainty + selfcheckgpt)
- Fallback: Implement from paper specifications using Deberta-v3-large + BERTScore
- Justification: Official implementations ensure methodological validity

### Code Analysis (Serena MCP)

*Serena MCP optional and not used. Analysis based on GitHub repos.*

**Semantic Entropy Core Logic (from semantic_uncertainty repo):**
1. Generate N samples per query
2. Cluster samples by semantic equivalence using NLI (entailment = same cluster)
3. Compute entropy over cluster distribution
4. Higher entropy → lower confidence → more likely hallucination

**Self-Consistency Core Logic (from selfcheckgpt repo):**
1. Generate N samples per query
2. Compute pairwise similarity (BERTScore or other metrics)
3. Average similarity → consistency score
4. Lower consistency → more likely hallucination

---

## Experiment Specification

### Dataset

**Dataset 1: TruthfulQA**
- **Name:** TruthfulQA (Generation subset)
- **Type:** standard
- **Source:** HuggingFace
- **Size:** 817 questions with ground truth labels
- **Splits:** Full test set (no train/val needed for detection task)
- **Labels:** Binary (truthful/hallucinated) based on human annotations

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `truthful_qa`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("truthful_qa", "generation")
# 817 questions, use full dataset
```

**Dataset 2: HaluEval (QA subset)**
- **Name:** HaluEval-QA
- **Type:** standard
- **Source:** HuggingFace
- **Size:** 10,000 samples (QA subset)
- **Labels:** Binary (hallucinated/correct)

**Loading Information:**
- Method: HuggingFace datasets
- Identifier: `pminervini/HaluEval`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("pminervini/HaluEval", "qa_samples")
```

### Models

#### Baseline Model

**Generator Model: Llama-3-8B-Instruct**
- **Type:** Decoder-only LLM
- **Source:** HuggingFace
- **Purpose:** Generate responses for hallucination detection evaluation

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
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

**NLI Model (for Semantic Entropy):**
- Model: `microsoft/deberta-v3-large-mnli`
- Purpose: Cluster responses by semantic equivalence

**Similarity Model (for Self-Consistency):**
- Model: BERTScore (roberta-large)
- Purpose: Compute pairwise response similarity

#### Proposed Model

**Architecture:** Hallucination Detection via Uncertainty Quantification

**Core Mechanism Implementation:**

```python
# Core Mechanism: Hallucination Detection Methods
# Based on: Kuhn et al. 2023 (Semantic Entropy), Manakul et al. 2023 (SelfCheckGPT)

import torch
import numpy as np
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from bert_score import score as bert_score

class SemanticEntropyDetector:
    """Detect hallucinations via semantic clustering entropy."""
    
    def __init__(self, nli_model="microsoft/deberta-v3-large-mnli"):
        self.nli = AutoModelForSequenceClassification.from_pretrained(nli_model)
        self.tokenizer = AutoTokenizer.from_pretrained(nli_model)
    
    def compute_entropy(self, responses: list[str]) -> float:
        """
        Args:
            responses: N generated responses for same query
        Returns:
            Semantic entropy (higher = more uncertain = likely hallucination)
        """
        # 1. Build semantic equivalence clusters via NLI
        clusters = self._cluster_by_entailment(responses)
        # 2. Compute cluster distribution
        probs = np.array([len(c) for c in clusters]) / len(responses)
        # 3. Return entropy
        return -np.sum(probs * np.log(probs + 1e-10))
    
class SelfConsistencyDetector:
    """Detect hallucinations via response consistency."""
    
    def compute_consistency(self, responses: list[str]) -> float:
        """
        Args:
            responses: N generated responses for same query
        Returns:
            Consistency score (lower = more inconsistent = likely hallucination)
        """
        # Compute pairwise BERTScore
        P, R, F1 = bert_score(responses, responses, lang="en")
        # Average F1 (excluding diagonal)
        mask = ~torch.eye(len(responses), dtype=bool)
        return F1[mask].mean().item()
```

### Training Protocol

**No Training Required** - Both methods are zero-shot detection approaches.

**Generation Protocol:**
- **Samples per query:** N = 10
- **Temperature:** 0.7 (enables diverse sampling)
- **Max tokens:** 256
- **Seed:** 42 (single seed for PoC)

**Source:** Kuhn et al. 2023 - N=10 provides good uncertainty estimation

> ⚠️ **EXISTENCE (PoC)**: Single seed, no hyperparameter search.

### Evaluation

**Primary Metrics:**
- **AUROC:** Area Under ROC Curve for hallucination detection
  - Library: `sklearn.metrics.roc_auc_score`
  - Code: `roc_auc_score(y_true, uncertainty_scores)`

**Success Criteria:**
- proposed_metric > 0.55 (above chance + margin)
- Both methods must pass independently

**Expected Baseline Performance** (from research):
- Semantic Entropy: AUROC ~0.75-0.85 on TruthfulQA
- Self-Consistency: AUROC ~0.70-0.80 on similar benchmarks
- **Source:** Kuhn et al. 2023, Manakul et al. 2023

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification (hallucination detection)
- Library: sklearn.metrics
- Code:
```python
from sklearn.metrics import roc_auc_score, roc_curve
import numpy as np

def compute_auroc(y_true, scores):
    """Compute AUROC with 95% CI via bootstrap."""
    auroc = roc_auc_score(y_true, scores)
    # Bootstrap CI
    n_bootstrap = 1000
    aurocs = []
    for _ in range(n_bootstrap):
        idx = np.random.choice(len(y_true), len(y_true), replace=True)
        aurocs.append(roc_auc_score(y_true[idx], scores[idx]))
    ci_low, ci_high = np.percentile(aurocs, [2.5, 97.5])
    return auroc, ci_low, ci_high
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing AUROC for both methods vs 0.55 threshold

#### Additional Figures (LLM Autonomous)

1. **ROC Curves**: Overlay ROC curves for both methods on same plot
2. **Score Distributions**: Histogram of uncertainty scores for hallucinated vs truthful responses
3. **Correlation Plot**: Scatter plot of semantic entropy vs self-consistency scores

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Semantic Entropy AUROC > 0.55
3. Self-Consistency AUROC > 0.55

**Mechanism Verification:**
- Pre-condition: NLI model loads, BERTScore computes
- Activation Indicator: Non-zero entropy/consistency variance across queries
- Failure Detection: If all queries have identical scores → mechanism not working

---

## Appendix: Reference Implementations

### Primary References

1. **Semantic Entropy (Official)**
   - Paper: "Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation" (Kuhn et al., ICLR 2023)
   - GitHub: https://github.com/lorenzkuhn/semantic_uncertainty
   - Nature 2024: "Detecting Hallucinations in Large Language Models Using Semantic Entropy"

2. **SelfCheckGPT (Official)**
   - Paper: "SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection" (Manakul et al., EMNLP 2023)
   - GitHub: https://github.com/potsawee/selfcheckgpt
   - PyPI: `selfcheckgpt`

3. **TruthfulQA Benchmark**
   - Paper: "TruthfulQA: Measuring How Models Mimic Human Falsehoods" (Lin et al., 2022)
   - HuggingFace: `truthful_qa`

4. **HaluEval Benchmark**
   - Paper: "HaluEval: A Large-Scale Hallucination Evaluation Benchmark" (Li et al., 2023)
   - HuggingFace: `pminervini/HaluEval`

### Code Snippets

**From lorenzkuhn/semantic_uncertainty:**
```python
# Semantic clustering via bidirectional entailment
def are_semantically_equivalent(s1, s2, nli_model, threshold=0.5):
    # Check entailment in both directions
    forward = nli_model(s1, s2)  # s1 entails s2
    backward = nli_model(s2, s1)  # s2 entails s1
    return forward > threshold and backward > threshold
```

**From potsawee/selfcheckgpt:**
```python
# BERTScore consistency check
from selfcheckgpt.modeling_selfcheck import SelfCheckBERTScore
selfcheck = SelfCheckBERTScore()
scores = selfcheck.predict(
    sentences=sentences,
    sampled_passages=sampled_passages
)
```

---

## State Information

**State File:** verification_state.yaml (via ablation override)
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- Phase 2C experiment design: IN_PROGRESS → COMPLETED

---

*MCP Tools Used: WebSearch (GitHub search fallback)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
