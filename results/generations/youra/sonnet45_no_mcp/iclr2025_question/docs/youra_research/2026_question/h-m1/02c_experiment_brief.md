---
stepsCompleted: [step-01, step-02, step-03, step-04, step-05, step-06, step-07, step-08]
status: completed
startedAt: "2026-04-22T02:23:00Z"
completedAt: "2026-04-22T02:25:00Z"
---

# Experiment Design: h-m1

**Date:** 2026-04-22
**Author:** Anonymous
**Hypothesis Statement:** Under systematic evaluation, if we analyze the four uncertainty methods (semantic entropy, self-consistency, token variance, verbalized confidence) using their distinct computational mechanisms, then each method will capture a different uncertainty dimension (semantic diversity, sampling agreement, distributional sharpness, introspective calibration), because the methods are algorithmically designed to measure different statistical properties of model outputs.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Analyzes underlying computational mechanisms

---

## Workflow Status

**Verification State:** COMPLETED
**Prerequisites Satisfied:** Yes (h-e1 COMPLETED with PASS)
**Gate Status:** SHOULD_WORK - Pairwise correlation between methods < 0.7

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (COMPLETED)

### Gate Condition
SHOULD_WORK gate: Pairwise correlation between methods < 0.7
- If satisfied: Proceed to h-m2
- If failed: EXPLORE whether methods measure same signal with different scales

---

## Continuation Context

### Previous Hypothesis Results (h-e1)
**Status:** COMPLETED - PASS
**Key Findings:**
- Semantic entropy (with clustering) achieved AUROC: 0.78
- Ensemble baseline (majority vote, K=10) achieved AUROC: 0.69
- Difference: 0.09 (exceeds threshold of 0.07)
- **Validation:** Clustering contribution confirmed beyond simple sampling

**Proven Components:**
- Semantic entropy implementation validated
- K=10 sampling effective for uncertainty estimation
- NaturalQuestions dataset suitable for knowledge-gap errors
- Mistral-7B-v0.1 adequate for factual QA (>50% accuracy)

**Optimal Hyperparameters from h-e1:**
- Temperature: 0.7
- Sample count: K=10
- Embedding model: sentence-transformers (for semantic clustering)
- Clustering algorithm: agglomerative clustering with semantic similarity threshold

---

## Implementation Research Summary

### Web Search Findings (Archon/Exa MCP Unavailable)

**⚠️ MCP Server Status:** Archon and Exa MCP servers unavailable - Using web search fallback

#### Query 1: Semantic Entropy Implementation (Kuhn et al. 2023)

**Source:** Kuhn et al., "Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in Natural Language Generation", ICLR 2023

**Key Insights:**
- Official implementation: https://github.com/lorenzkuhn/semantic_uncertainty
- Method: Generate K answers → Cluster by semantic equivalence → Compute entropy over clusters
- Uses unsupervised approach with single model (no ensemble needed)
- Requires sentence embeddings + clustering algorithm
- Computes semantic entropy, predictive entropy, lexical similarity, p(True)

**Implementation Details:**
- PyTorch + HuggingFace transformers
- compute_confidence_measure.py contains core implementation
- Incorporates linguistic invariances (paraphrases treated as equivalent)

**Used For:** Semantic entropy method specification, clustering approach

#### Query 2: Self-Consistency Implementation (Wang et al. 2022)

**Source:** Wang et al., "Self-Consistency Improves Chain of Thought Reasoning in Language Models", ICLR 2023 (arXiv:2203.11171)

**Key Insights:**
- Sample diverse reasoning paths instead of greedy decoding
- Select most consistent answer by marginalizing over sampled paths
- Majority voting across K sampled outputs
- Boosts performance: GSM8K (+17.9%), SVAMP (+11.0%), AQuA (+12.2%)

**Implementation:**
- GitHub: https://github.com/dj-sorry/self_consistency
- Supports multiple LLMs (OPT, BLOOM, GPT-2, T5)
- Temperature sampling to generate diverse outputs
- Agreement score computed via majority vote

**Used For:** Self-consistency method specification, sampling strategy

#### Query 3: Token Variance & Verbalized Confidence

**Token Variance Sources:**
- "Token-Level Uncertainty Estimation for Large Language Model Reasoning" (arXiv:2505.11737)
- ToKUR framework: aggregates token-level uncertainties via random low-rank weight perturbation
- Decomposes uncertainty into aleatoric (data randomness) and epistemic (model uncertainty)

**Verbalized Confidence Sources:**
- "Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs" (arXiv:2306.13063)
- Verbalized Confidence Elicitation (VCE): prompts model for answer + confidence score
- "On Verbalized Confidence Scores for LLMs" (arXiv:2412.14737)
- Reliability challenges: different prompts produce different scores

**Used For:** Token variance and verbalized confidence method specifications

### GitHub Implementations (Web Search)

**Repository 1: lorenzkuhn/semantic_uncertainty** (⭐ 250+)
- **URL:** https://github.com/lorenzkuhn/semantic_uncertainty
- **Relevance:** Official ICLR 2023 paper implementation - HIGHEST PRIORITY
- **Key Code:** compute_confidence_measure.py
- **Methods Implemented:** Semantic entropy, predictive entropy, lexical similarity
- **Note:** Authors recommend newer 2024 Nature implementation

**Repository 2: dj-sorry/self_consistency**
- **URL:** https://github.com/dj-sorry/self_consistency
- **Relevance:** Clean implementation of Wang et al. 2022
- **Supported Models:** OPT, BLOOM, GPT-2, T5
- **Key Feature:** Majority voting across diverse sampled paths

**Repository 3: HuggingFace Implementations**
- **Datasets:** 
  - NaturalQuestions: google-research-datasets/natural_questions, irds/natural-questions
  - TruthfulQA: truthfulqa/truthful_qa, EleutherAI/truthful_qa_mc
- **Models:** mistralai/Mistral-7B-v0.1

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Implementation Priority:**
1. ⭐⭐⭐ **Semantic Entropy:** Use Kuhn et al. official GitHub (lorenzkuhn/semantic_uncertainty)
2. ⭐⭐⭐ **Self-Consistency:** Use Wang et al. methodology (dj-sorry/self_consistency as reference)
3. ⭐⭐ **Token Variance:** Implement based on ToKUR framework (compute output distribution variance)
4. ⭐⭐ **Verbalized Confidence:** Implement via direct prompting (VCE methodology)

**Recommended Implementation Path:**
- **Primary:** Kuhn et al. semantic_uncertainty repo for semantic entropy baseline
- **Fallback:** Reimplement from paper specifications if dependencies conflict
- **Justification:** Official implementations ensure reproducibility and match published results

### Code Analysis (Serena MCP)

**⚠️ MCP Server Status:** Serena MCP unavailable (optional)

**Status:** Not performed - Serena MCP unavailable. Implementation will be based on web search findings and official repositories.

---

## Experiment Specification

### Dataset

**Dataset 1: NaturalQuestions**
- **Name:** NaturalQuestions (Google Research)
- **Type:** standard (HuggingFace)
- **Size:** 100 examples (from Phase 2B scope reduction)
- **Source:** google-research-datasets/natural_questions
- **Purpose:** Knowledge-gap error analysis
- **Preprocessing:**
  - Extract question text and answer candidates
  - Filter for unanswerable questions (knowledge gaps)
  - Tokenize for Mistral-7B (max length 512 tokens)
- **Justification:** Proven in h-e1, contains knowledge-gap errors with unanswerable category

**Dataset 2: TruthfulQA** (for h-m2 continuation)
- **Name:** TruthfulQA
- **Type:** standard (HuggingFace)
- **Size:** 100 examples
- **Source:** truthfulqa/truthful_qa
- **Purpose:** Confident misconception analysis (used in h-m2)
- **Note:** Referenced for continuity, primary focus is NaturalQuestions for h-m1

**Loading Information** (for Phase 4 download):
- **Method:** HuggingFace datasets library
- **Identifier:** "google-research-datasets/natural_questions"
- **Code:**
```python
from datasets import load_dataset
dataset = load_dataset("google-research-datasets/natural_questions", split="validation")
# Filter for 100 examples from unanswerable subset
```

### Models

#### Baseline Model

**Architecture:** Mistral-7B-v0.1
**Type:** Decoder-only transformer LLM (7B parameters)
**Source:** mistralai/Mistral-7B-v0.1 (HuggingFace)
**Configuration:**
- Hidden size: 4096
- Num layers: 32
- Num attention heads: 32
- Vocabulary size: 32000
- Context length: 8192 tokens
- Activation: SiLU

**Justification:** Validated in h-e1 with >50% accuracy on NaturalQuestions, sufficient for uncertainty analysis

**Loading Information** (for Phase 4 download):
- **Method:** HuggingFace transformers
- **Identifier:** "mistralai/Mistral-7B-v0.1"
- **Code:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1", torch_dtype=torch.bfloat16, device_map="auto")
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")
```

#### Proposed Model

**Architecture:** Same as baseline (Mistral-7B-v0.1) - this hypothesis analyzes method mechanisms, not model architecture

**Core Mechanism Implementation:**

This hypothesis implements FOUR uncertainty quantification methods to compare their mechanisms:

```python
# Core Mechanisms: Four Uncertainty Quantification Methods
# Based on: Kuhn 2023, Wang 2022, ToKUR framework, VCE methodology

import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
import numpy as np

class UncertaintyMethods:
    """
    Implements four uncertainty methods to analyze orthogonality:
    1. Semantic Entropy (Kuhn 2023)
    2. Self-Consistency (Wang 2022)
    3. Token Variance
    4. Verbalized Confidence
    """
    
    def __init__(self, model, tokenizer, K=10, temperature=0.7):
        self.model = model
        self.tokenizer = tokenizer
        self.K = K  # Number of samples (from h-e1)
        self.temperature = temperature  # From h-e1
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    def semantic_entropy(self, question):
        """
        Method 1: Semantic Entropy (semantic diversity dimension)
        Args: question (str)
        Returns: entropy score (float)
        """
        # Step 1: Generate K answers with temperature sampling
        answers = self.generate_answers(question, self.K, self.temperature)
        
        # Step 2: Embed answers for semantic clustering
        embeddings = self.embedder.encode(answers)
        
        # Step 3: Cluster by semantic similarity
        clustering = AgglomerativeClustering(n_clusters=None, distance_threshold=0.5)
        clusters = clustering.fit_predict(embeddings)
        
        # Step 4: Compute entropy over semantic clusters
        cluster_probs = np.bincount(clusters) / len(clusters)
        entropy = -np.sum(cluster_probs * np.log(cluster_probs + 1e-10))
        return entropy
    
    def self_consistency(self, question):
        """
        Method 2: Self-Consistency (sampling agreement dimension)
        Args: question (str)
        Returns: agreement score (float)
        """
        # Step 1: Generate K diverse answers
        answers = self.generate_answers(question, self.K, self.temperature)
        
        # Step 2: Find most common answer (majority vote)
        from collections import Counter
        answer_counts = Counter(answers)
        most_common_count = answer_counts.most_common(1)[0][1]
        
        # Step 3: Agreement = frequency of majority answer
        agreement = most_common_count / self.K
        return agreement  # High = low uncertainty
    
    def token_variance(self, question):
        """
        Method 3: Token Variance (distributional sharpness dimension)
        Args: question (str)
        Returns: variance score (float)
        """
        # Step 1: Get token probabilities for K samples
        inputs = self.tokenizer(question, return_tensors="pt")
        token_probs = []
        
        for _ in range(self.K):
            outputs = self.model(**inputs, output_attentions=False)
            probs = torch.softmax(outputs.logits[:, -1, :] / self.temperature, dim=-1)
            token_probs.append(probs)
        
        # Step 2: Compute variance across samples
        variance = torch.var(torch.stack(token_probs), dim=0).mean().item()
        return variance
    
    def verbalized_confidence(self, question):
        """
        Method 4: Verbalized Confidence (introspective calibration dimension)
        Args: question (str)
        Returns: confidence score (float)
        """
        # Step 1: Prompt model to verbalize confidence
        prompt = f"{question}\n\nProvide your answer and confidence (0-100%):"
        answer = self.generate_single_answer(prompt)
        
        # Step 2: Extract numeric confidence from response
        import re
        confidence_match = re.search(r'(\d+)%', answer)
        confidence = float(confidence_match.group(1)) / 100 if confidence_match else 0.5
        return confidence  # High = low uncertainty
    
    def compute_all_methods(self, question):
        """Compute all four methods and return scores"""
        return {
            'semantic_entropy': self.semantic_entropy(question),
            'self_consistency': self.self_consistency(question),
            'token_variance': self.token_variance(question),
            'verbalized_confidence': self.verbalized_confidence(question)
        }
    
    def generate_answers(self, question, K, temperature):
        """Helper: Generate K answers with temperature sampling"""
        # Implementation details omitted for brevity
        pass
    
    def generate_single_answer(self, prompt):
        """Helper: Generate single answer"""
        # Implementation details omitted for brevity
        pass

# Integration: Instantiate with Mistral-7B model
uncertainty_analyzer = UncertaintyMethods(model, tokenizer, K=10, temperature=0.7)
```

### Training Protocol

**From Previous Hypothesis (h-e1):**

This is a **zero-shot inference experiment** - NO TRAINING required.
- **Model:** Use pretrained Mistral-7B-v0.1 directly (no fine-tuning)
- **Temperature:** 0.7 (optimal from h-e1)
- **Sample Count:** K=10 (validated in h-e1)
- **Seeds:** 1 (fixed seed=42 for reproducibility)

**Rationale:** h-e1 validated these hyperparameters for uncertainty estimation on NaturalQuestions. Reusing for controlled experiment ensures only the analysis method changes.

**Inference Protocol:**
- For each question in NaturalQuestions (100 examples):
  1. Generate K=10 answers with temperature=0.7
  2. Compute all four uncertainty methods
  3. Record scores for correlation analysis
- Total inference runs: 100 questions × 4 methods = 400 method evaluations

### Evaluation

**Primary Metrics:**
- **Pairwise Correlation Matrix:** Pearson correlation between all method pairs (6 pairs total)
  - semantic_entropy × self_consistency
  - semantic_entropy × token_variance
  - semantic_entropy × verbalized_confidence
  - self_consistency × token_variance
  - self_consistency × verbalized_confidence
  - token_variance × verbalized_confidence

**Success Criteria:**
- All pairwise correlations < 0.7 (gate condition)
- Methods show distinct response patterns across questions

**Expected Baseline Performance** (from research):
- Semantic entropy: proven effective in Kuhn 2023 on generation tasks
- Self-consistency: +17.9% improvement on GSM8K (Wang 2022)
- Token variance: captures distributional properties (ToKUR framework)
- Verbalized confidence: reasonable calibration on QA tasks (VCE studies)

**Metrics Loading Information** (for Phase 4 implementation):
- **Task Type:** Uncertainty quantification (regression)
- **Library:** scipy.stats, sklearn.metrics, numpy
- **Code:**
```python
from scipy.stats import pearsonr
import numpy as np

# Compute correlation matrix
methods = ['semantic_entropy', 'self_consistency', 'token_variance', 'verbalized_confidence']
correlation_matrix = np.zeros((4, 4))

for i, method1 in enumerate(methods):
    for j, method2 in enumerate(methods):
        correlation, p_value = pearsonr(scores[method1], scores[method2])
        correlation_matrix[i, j] = correlation
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Correlation Matrix Heatmap:** 4×4 heatmap showing pairwise correlations between all four uncertainty methods
  - Axes: Method names
  - Values: Pearson correlation coefficients
  - Colormap: diverging (red-white-blue, centered at 0)
  - Annotations: correlation values in cells
  - Success threshold line: 0.7 (gate condition)

#### Additional Figures (LLM Autonomous)

**Recommended visualizations based on hypothesis:**
1. **Method Distribution Plots:** 4 subplots showing score distributions for each method across 100 questions
2. **Scatter Matrix:** Pairwise scatter plots for all method combinations (6 pairs)
3. **Method Ranking Comparison:** Bar chart showing how often each method identifies high/low uncertainty questions
4. **Dimension Analysis:** PCA or t-SNE plot showing method scores in reduced dimensional space

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. All four methods implemented and compute uncertainty scores
3. Correlation matrix computed successfully  
4. Pairwise correlations < 0.7 (gate condition satisfied)

**Verification Protocol:**
- Log each method's scores for sample question
- Print correlation matrix
- Assert all off-diagonal values < 0.7
- Generate correlation heatmap

---

## Appendix: Reference Implementations

### A. Web Search Sources (Archon/Exa MCP Unavailable)

**Source 1: Semantic Entropy Implementation**
- **Title:** "Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in Natural Language Generation"
- **Authors:** Kuhn et al., ICLR 2023
- **URL:** https://arxiv.org/abs/2302.09664
- **GitHub:** https://github.com/lorenzkuhn/semantic_uncertainty
- **Query Used:** "semantic entropy uncertainty quantification Kuhn 2023 implementation PyTorch"
- **Key Insights:**
  - Unsupervised semantic clustering approach
  - Incorporates linguistic invariances (paraphrases)
  - Official PyTorch + HuggingFace implementation
- **Used For:** Semantic entropy method design, clustering algorithm

**Source 2: Self-Consistency Method**
- **Title:** "Self-Consistency Improves Chain of Thought Reasoning in Language Models"
- **Authors:** Wang et al., ICLR 2023 (arXiv:2203.11171)
- **URL:** https://arxiv.org/abs/2203.11171
- **GitHub:** https://github.com/dj-sorry/self_consistency
- **Query Used:** "self-consistency uncertainty LLM Wang 2022 implementation GitHub"
- **Key Insights:**
  - Majority voting across diverse sampled paths
  - Temperature sampling for diversity
  - Significant performance gains on reasoning tasks
- **Used For:** Self-consistency method design, sampling strategy

**Source 3: Token Variance Method**
- **Title:** "Token-Level Uncertainty Estimation for Large Language Model Reasoning"
- **Authors:** ToKUR framework (arXiv:2505.11737)
- **URL:** https://arxiv.org/html/2505.11737v1
- **Query Used:** "token variance verbalized confidence uncertainty methods implementation"
- **Key Insights:**
  - Random low-rank weight perturbation
  - Decomposes into aleatoric and epistemic uncertainty
  - Aggregates token-level uncertainties
- **Used For:** Token variance method design

**Source 4: Verbalized Confidence**
- **Title:** "Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs"
- **Authors:** arXiv:2306.13063
- **URL:** https://arxiv.org/html/arXiv:2306.13063
- **Query Used:** "token variance verbalized confidence uncertainty methods implementation"
- **Key Insights:**
  - Verbalized Confidence Elicitation (VCE) methodology
  - Prompts model for answer + confidence score
  - Calibration challenges with different prompts
- **Used For:** Verbalized confidence method design

### B. Dataset and Model Loading Sources

**NaturalQuestions Dataset**
- **Source:** google-research-datasets/natural_questions (HuggingFace)
- **URL:** https://huggingface.co/datasets/google-research-datasets/natural_questions
- **Query Used:** "NaturalQuestions dataset HuggingFace load PyTorch factual QA"
- **Loading Method:** `load_dataset("google-research-datasets/natural_questions")`
- **Used For:** Dataset loading specification

**TruthfulQA Dataset**
- **Source:** truthfulqa/truthful_qa (HuggingFace)
- **URL:** https://huggingface.co/datasets/truthfulqa/truthful_qa
- **GitHub:** https://github.com/sylinrl/TruthfulQA
- **Query Used:** "TruthfulQA dataset implementation load PyTorch"
- **Loading Method:** `load_dataset("truthful_qa", "multiple_choice")`
- **Used For:** Reference for h-m2 continuation

**Mistral-7B Model**
- **Source:** mistralai/Mistral-7B-v0.1 (HuggingFace)
- **URL:** https://huggingface.co/mistralai/Mistral-7B-v0.1
- **Docs:** https://huggingface.co/docs/transformers/model_doc/mistral
- **Query Used:** "Mistral-7B model load HuggingFace transformers PyTorch"
- **Loading Method:** `AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1")`
- **Used For:** Model loading specification

### C. Previous Hypothesis Context

**Source:** Phase 4 Validation Report - h-e1
- **File:** docs/youra_research/20260421_question/h-e1/04_validation.md
- **Reused Components:**
  - Dataset: NaturalQuestions (proven stable, >50% accuracy)
  - Hyperparameters: K=10, temperature=0.7 (optimal values)
  - Model: Mistral-7B-v0.1 (validated performance)
- **Why Reused:** Enables controlled experiment - only uncertainty methods change, all other variables held constant

### D. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Semantic entropy method | Web Search + GitHub | Kuhn 2023, lorenzkuhn/semantic_uncertainty |
| Self-consistency method | Web Search + GitHub | Wang 2022, dj-sorry/self_consistency |
| Token variance method | Web Search | ToKUR framework (arXiv:2505.11737) |
| Verbalized confidence method | Web Search | VCE methodology (arXiv:2306.13063) |
| NaturalQuestions dataset | Web Search + HuggingFace | google-research-datasets/natural_questions |
| Mistral-7B model | Web Search + HuggingFace | mistralai/Mistral-7B-v0.1 |
| K=10, temperature=0.7 | Previous hypothesis | h-e1 validation report |
| Correlation metric | Standard practice | scipy.stats.pearsonr |

---

## Research Sources

**Core Papers:**
- [Semantic Uncertainty (Kuhn et al. 2023)](https://arxiv.org/abs/2302.09664)
- [Self-Consistency (Wang et al. 2022)](https://arxiv.org/abs/2203.11171)
- [Token-Level Uncertainty (ToKUR)](https://arxiv.org/html/2505.11737v1)
- [Confidence Elicitation in LLMs](https://arxiv.org/html/arXiv:2306.13063)

**Implementations:**
- [Semantic Uncertainty GitHub](https://github.com/lorenzkuhn/semantic_uncertainty)
- [Self-Consistency Implementation](https://github.com/dj-sorry/self_consistency)
- [NaturalQuestions Dataset](https://huggingface.co/datasets/google-research-datasets/natural_questions)
- [TruthfulQA Dataset](https://huggingface.co/datasets/truthfulqa/truthful_qa)
- [Mistral-7B Model](https://huggingface.co/mistralai/Mistral-7B-v0.1)

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-04-22T02:25:00Z
**Status:** COMPLETED

### Workflow History for This Hypothesis
- 2026-04-22T02:07:47: h-m1 set to IN_PROGRESS
- 2026-04-22T02:23:00: Phase 2C experiment design started
- 2026-04-22T02:25:00: Phase 2C experiment design completed

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Web search fallback (Archon/Exa/Serena unavailable)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
