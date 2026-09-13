# Experiment Design: h-m1

**Date:** 2026-08-29
**Author:** Anonymous
**Hypothesis Statement:** Semantic entropy achieves AUROC >= 0.70 on TruthfulQA mc1 by clustering semantically equivalent generations before entropy computation
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests causal mechanism (semantic clustering improves UQ)

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-e1 VALIDATED (max_prob AUROC=0.8068)
**Gate Status:** MUST_WORK - If semantic entropy AUROC < 0.70, mechanism fails

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (VALIDATED)

### Gate Condition
- **Type:** MUST_WORK
- **Pass:** Semantic entropy AUROC >= 0.70 on TruthfulQA mc1
- **Fail:** PIVOT - semantic clustering does not improve over simple methods

---

## Continuation Context

### Previous Hypothesis Results (h-e1)
- **Status:** VALIDATED (Gate PASSED)
- **Key Finding:** max_prob (1-confidence) AUROC=0.8068, choice_entropy AUROC=0.7703
- **Implication:** Simple UQ methods work well; semantic entropy must match/exceed 0.70 to justify complexity

---

## Implementation Research Summary

### Key Implementations (from h-e1 research)

**1. lorenzkuhn/semantic_uncertainty** (Official - Kuhn et al. 2023)
- **URL:** https://github.com/lorenzkuhn/semantic_uncertainty
- **Method:** Semantic entropy via NLI-based clustering
- **Pipeline:** generate samples → cluster by semantic equivalence → compute entropy over clusters

**2. Semantic Entropy Algorithm:**
1. Generate N diverse samples (temperature=0.7, N=10)
2. For each pair of samples, compute NLI entailment (bidirectional)
3. Cluster samples where bidirectional entailment holds
4. Compute entropy: H = -Σ p(cluster) * log(p(cluster))
5. Lower entropy = consistent meaning = less likely hallucination

### NLI Model for Clustering
- **Model:** DeBERTa-v3-large-mnli (microsoft/deberta-v3-large-mnli)
- **Task:** Natural Language Inference (entailment/neutral/contradiction)
- **Threshold:** Bidirectional entailment probability > 0.7 → same cluster

---

## Experiment Specification

### Dataset

**Name:** TruthfulQA (mc1 split)
**Type:** standard
**Source:** HuggingFace datasets

**Statistics:**
- Total questions: 817
- Split: mc1 (single correct answer per question)
- Evaluation: Full dataset (statistically meaningful)

**Preprocessing:**
- Load via: `load_dataset("truthful_qa", "multiple_choice")`
- Same preprocessing as h-e1 for direct comparison

**Loading Information:**
```python
from datasets import load_dataset
dataset = load_dataset("truthful_qa", "multiple_choice")
# Use full dataset (817 questions)
```

### Models

#### LLM Model
**Name:** Llama-3-8B-Instruct
**Source:** meta-llama/Meta-Llama-3-8B-Instruct
**Parameters:** ~8B

**Loading:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
```

#### NLI Model (for semantic clustering)
**Name:** DeBERTa-v3-large-mnli
**Source:** microsoft/deberta-v3-large-mnli
**Purpose:** Bidirectional entailment for semantic equivalence

**Loading:**
```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer
nli_model = AutoModelForSequenceClassification.from_pretrained(
    "microsoft/deberta-v3-large-mnli"
)
nli_tokenizer = AutoTokenizer.from_pretrained("microsoft/deberta-v3-large-mnli")
```

### Core Mechanism Implementation

```python
# Core Mechanism: Semantic Entropy via NLI-based Clustering
# Based on: Kuhn et al. 2023 (lorenzkuhn/semantic_uncertainty)

import torch
import numpy as np
from scipy.stats import entropy
from collections import defaultdict

class SemanticEntropy:
    """
    Computes semantic entropy by clustering semantically equivalent generations.
    """
    def __init__(self, llm_model, llm_tokenizer, nli_model, nli_tokenizer, 
                 num_samples=10, entailment_threshold=0.7):
        self.llm_model = llm_model
        self.llm_tokenizer = llm_tokenizer
        self.nli_model = nli_model
        self.nli_tokenizer = nli_tokenizer
        self.num_samples = num_samples
        self.entailment_threshold = entailment_threshold
    
    def generate_samples(self, prompt, temperature=0.7, max_tokens=128):
        """Generate N diverse samples for a prompt."""
        samples = []
        inputs = self.llm_tokenizer(prompt, return_tensors="pt").to(self.llm_model.device)
        for _ in range(self.num_samples):
            with torch.no_grad():
                output = self.llm_model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.llm_tokenizer.eos_token_id
                )
            response = self.llm_tokenizer.decode(output[0][inputs.input_ids.shape[1]:], 
                                                   skip_special_tokens=True)
            samples.append(response)
        return samples
    
    def check_entailment(self, text1, text2):
        """Check bidirectional entailment between two texts."""
        def get_entailment_prob(premise, hypothesis):
            inputs = self.nli_tokenizer(premise, hypothesis, return_tensors="pt", 
                                         truncation=True, max_length=512)
            inputs = {k: v.to(self.nli_model.device) for k, v in inputs.items()}
            with torch.no_grad():
                logits = self.nli_model(**inputs).logits
                probs = torch.softmax(logits, dim=-1)
            # DeBERTa-mnli: [contradiction, neutral, entailment]
            return probs[0, 2].item()
        
        p1 = get_entailment_prob(text1, text2)
        p2 = get_entailment_prob(text2, text1)
        return min(p1, p2) > self.entailment_threshold
    
    def cluster_samples(self, samples):
        """Cluster samples by semantic equivalence."""
        clusters = []
        for sample in samples:
            matched = False
            for cluster in clusters:
                if self.check_entailment(sample, cluster[0]):
                    cluster.append(sample)
                    matched = True
                    break
            if not matched:
                clusters.append([sample])
        return clusters
    
    def compute_semantic_entropy(self, prompt):
        """Main method: generate, cluster, compute entropy."""
        samples = self.generate_samples(prompt)
        clusters = self.cluster_samples(samples)
        
        # Compute entropy over cluster distribution
        cluster_sizes = [len(c) for c in clusters]
        cluster_probs = np.array(cluster_sizes) / sum(cluster_sizes)
        sem_entropy = entropy(cluster_probs)
        
        return {
            'semantic_entropy': sem_entropy,
            'num_clusters': len(clusters),
            'cluster_sizes': cluster_sizes,
            'samples': samples
        }

# Usage:
# se = SemanticEntropy(llm_model, llm_tokenizer, nli_model, nli_tokenizer)
# result = se.compute_semantic_entropy("What is the capital of France?")
# Higher semantic_entropy → more inconsistent → likely hallucination
```

### Evaluation Protocol

**Primary Metric:**
- **AUROC:** Area Under ROC Curve for hallucination detection
- **Threshold:** AUROC >= 0.70 (gate condition)

**Comparison Methods (from h-e1):**
| Method | h-e1 AUROC | Source |
|--------|------------|--------|
| max_prob | 0.8068 | h-e1 validated |
| choice_entropy | 0.7703 | h-e1 validated |
| semantic_entropy | TBD | This experiment |

**Secondary Metrics:**
- Number of clusters per question (clustering effectiveness)
- Correlation: semantic_entropy vs max_prob
- Runtime comparison (semantic entropy is more expensive)

**Success Criteria:**
- **Gate Pass:** Semantic entropy AUROC >= 0.70
- **Bonus:** Outperforms token-level methods (max_prob, choice_entropy)

### Inference Protocol

**Configuration:**
- Samples per query: 10
- Temperature: 0.7
- Max tokens: 128
- NLI entailment threshold: 0.7
- Seed: 42

**Compute Budget:**
- 817 questions × 10 samples × 45 NLI pairs per question
- Estimated: ~4-6 hours on single A100 (NLI is expensive)

**Metrics Code:**
```python
from sklearn.metrics import roc_auc_score

# Ground truth: 0 = correct answer, 1 = hallucination
# Score: semantic_entropy (higher = more likely hallucination)
auroc = roc_auc_score(y_true, semantic_entropies)
print(f"Semantic Entropy AUROC: {auroc:.4f}")
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **AUROC Comparison:** Bar chart comparing semantic_entropy vs max_prob vs choice_entropy

#### Additional Figures
1. **Cluster Distribution:** Histogram of num_clusters across questions
2. **Score Correlation:** Scatter plot of semantic_entropy vs max_prob
3. **ROC Curves:** Overlay for all three methods

> Figures saved to `docs/youra_research/h-m1/figures/`

---

## Mechanism Verification Protocol

### Pre-conditions
- [x] `llm_generates_samples`: Llama-3-8B supports temperature sampling
- [x] `nli_model_available`: DeBERTa-v3-large-mnli from HuggingFace
- [x] `clustering_defined`: Bidirectional entailment threshold 0.7

### Mechanism Activation Indicators
- `clustering_active`: Number of clusters < number of samples (clustering happening)
- `entropy_varies`: Semantic entropy variance > 0 across questions
- `auroc_above_random`: AUROC > 0.50

### Mechanism Verification Code
```python
def verify_semantic_clustering_active(results):
    """Verify that semantic clustering is working."""
    # Check 1: Clustering reduces samples
    avg_clusters = np.mean([r['num_clusters'] for r in results])
    avg_samples = 10  # We generate 10 samples
    assert avg_clusters < avg_samples, "Clustering not reducing samples"
    
    # Check 2: Entropy has variance
    entropies = [r['semantic_entropy'] for r in results]
    assert np.std(entropies) > 0, "No entropy variance"
    
    # Check 3: Clusters vary in size
    all_cluster_sizes = [s for r in results for s in r['cluster_sizes']]
    assert len(set(all_cluster_sizes)) > 1, "All clusters same size"
    
    print(f"Avg clusters: {avg_clusters:.2f} (from 10 samples)")
    print(f"Entropy std: {np.std(entropies):.4f}")
    return True
```

---

## Gate Decision Logic

```python
def evaluate_h_m1_gate(semantic_auroc):
    """Evaluate h-m1 MUST_WORK gate."""
    THRESHOLD = 0.70
    
    if semantic_auroc >= THRESHOLD:
        return {
            'gate': 'PASSED',
            'action': 'CONTINUE to h-m2',
            'result': f'Semantic entropy AUROC={semantic_auroc:.4f} >= {THRESHOLD}'
        }
    else:
        return {
            'gate': 'FAILED',
            'action': 'PIVOT - semantic clustering insufficient',
            'result': f'Semantic entropy AUROC={semantic_auroc:.4f} < {THRESHOLD}'
        }
```

---

## Appendix: Key References

| Paper | Relevance | Method |
|-------|-----------|--------|
| Kuhn et al. 2023 | Semantic entropy | lorenzkuhn/semantic_uncertainty |
| Lin et al. 2022 | TruthfulQA | Benchmark definition |

**Implementation Repository:**
- [lorenzkuhn/semantic_uncertainty](https://github.com/lorenzkuhn/semantic_uncertainty)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-29

### Workflow History
- 2026-08-29: Phase 2C experiment design started
- 2026-08-29: h-e1 results inherited (max_prob AUROC=0.8068)
- 2026-08-29: Experiment specification synthesized

---

*MCP Tools: None used (building on h-e1 research)*
*Next Phase: Phase 3 - Implementation Planning*
