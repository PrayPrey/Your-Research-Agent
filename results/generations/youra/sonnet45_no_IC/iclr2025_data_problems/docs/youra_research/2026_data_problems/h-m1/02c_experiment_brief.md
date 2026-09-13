# Experiment Design: h-m1

**Date:** 2026-07-12
**Author:** Anonymous
**Hypothesis Statement:** Under stratified training (oversampling low-educational, high-BEIR examples), the retrieval-quality classifier learns to identify documents with high factual density and entity coverage, as evidenced by classifier-selected documents showing ≥15% higher named entity density than perplexity-matched controls.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM (Step 1/4) Template** - Validates stratified training mechanism.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** YES (H-E1 PASSED)
**Gate Status:** SHOULD_WORK (Entity density ≥ 1.15× baseline)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM (Step 1 of 4)
- **Prerequisites:** H-E1 (COMPLETED)

### Gate Condition
**Type:** SHOULD_WORK
**Condition:** Entity density_retrieval ≥ entity density_perplexity × 1.15
**Action if Fail:** PIVOT to different training strategy or feature engineering

---

## Continuation Context

This is a mechanism hypothesis building on H-E1 (EXISTENCE) which demonstrated retrieval-quality filtering achieves +5% Recall@10 improvement (baseline: 0.47, proposed: 0.52).

### Previous Hypothesis Results (H-E1)
- **Status:** PASSED
- **Metrics:** Recall@10 delta = +0.05 (10.6% relative improvement)
- **Key Findings:** Retrieval-quality classifier successfully outperformed perplexity baseline
- **Dataset:** BEIR Natural Questions (3.5K test queries)
- **Model:** DPR (Dense Passage Retriever)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Stratified Training & Factual Density**
- Limited direct matches in Archon KB for stratified training with factual density
- General machine learning training patterns found but not specific to this mechanism
- Suggests this is a novel approach requiring custom implementation

**Query 2: Retrieval Quality Classifier (FastText)**
- Found general model training examples but not specific to retrieval-quality classification
- T5 and diffusion model training examples show general patterns (learning rate schedules, batch sizing)
- Need to adapt general classifier training patterns to retrieval-specific task

**Query 3: Named Entity Density Measurement**
- General dataset documentation found
- LAION-5B mentions filtering and quality metrics
- Suggests entity density measurement is custom metric requiring implementation

**Key Insights:**
- Stratified training is a custom data sampling strategy (oversample low-educational, high-BEIR examples)
- FastText classifier training follows standard supervised learning patterns
- Entity density measurement requires spaCy NER pipeline integration

### Archon Code Examples

**Query 1: FastText Classifier Training (PyTorch)**
- Found general training examples (CLIP, text-to-image models) showing:
  - Standard training loop structure
  - Loss computation and backpropagation
  - Optimizer configuration (Adam variants common)
- No FastText-specific code found; suggests using standard PyTorch supervised learning pattern

**Query 2: spaCy NER**
- No direct spaCy code examples found in Archon
- Suggests need for standard spaCy pipeline usage (load model, process text, count entities)

**Key Implementation Patterns:**
- Training: Standard PyTorch supervised learning (DataLoader → forward → loss → backward → step)
- Evaluation: Custom metric computation (entity density = entities per 100 tokens)

### Exa GitHub Implementations

**Exa MCP Status:** Unavailable (payment required - HTTP 402 errors)

**Alternative Research Strategy:**
- Use standard FastText library (Facebook Research)
- Use spaCy for NER (industry standard)
- Follow stratified sampling patterns from scikit-learn

### 🎯 Implementation Priority Assessment

**This is a mechanism validation experiment, not paper reproduction.**

**Recommended Implementation Path:**
- **Primary:** Custom implementation using standard libraries
  - FastText for text classification (Facebook's fastText library or PyTorch equivalent)
  - spaCy for named entity recognition (en_core_web_sm model)
  - Custom stratification logic for training data sampling
- **Fallback:** Simplified baseline
  - Use pre-computed entity densities if runtime is prohibitive
  - Use random sampling instead of stratified if data is limited
- **Justification:** No canonical implementation exists for this specific mechanism; standard ML libraries provide necessary primitives

### Code Analysis (Serena MCP)

**Serena Analysis:** Not performed (no complex code requiring semantic analysis identified in research phase)

---

## Experiment Specification

### Dataset

**Name:** Common Crawl Sample + BEIR Natural Questions  
**Type:** Standard (BEIR benchmark) + Programmatic (Common Crawl sampling)  
**Purpose:** Train stratified retrieval-quality classifier on BEIR examples, apply to Common Crawl, measure entity density

#### Training Data (Stratified BEIR Examples)
- **Source:** BEIR benchmark success/failure examples
- **Stratification:** Oversample low-educational, high-BEIR pairs
- **Size:** ~10K stratified training pairs (positive/negative examples)
- **Positive Class:** Documents from successful BEIR retrievals (high Recall@10)
- **Negative Class:** Documents from failed retrievals OR low-quality documents
- **Educational Quality:** Measured via perplexity (GPT-2 model)

#### Evaluation Data (Common Crawl Sample)
- **Source:** Common Crawl 100K document sample (same as H-E1)
- **Purpose:** Apply trained classifier, select top-50K documents
- **Control Set:** Perplexity-matched documents (same size, similar perplexity distribution)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets + manual Common Crawl sampling
- Identifier: `beir/nq` (for BEIR Natural Questions context)
- Code:
  ```python
  from datasets import load_dataset
  
  # Load BEIR Natural Questions for context
  beir_nq = load_dataset("beir/nq", "corpus")
  
  # Common Crawl sampling (programmatic)
  # Note: Requires manual download and sampling from Common Crawl dumps
  # Alternative: Use pre-filtered subset from H-E1 experiment
  ```

### Models

#### Baseline Model (Perplexity-based Filtering)

**Architecture:** GPT-2 for perplexity scoring + threshold filtering  
**Purpose:** Select documents based on pretraining-quality signal (fluency, coherence)  
**Selection Method:** Sort by ascending perplexity, select top-50K documents

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `gpt2` (base model)
- Code:
  ```python
  from transformers import GPT2LMHeadModel, GPT2Tokenizer
  
  model = GPT2LMHeadModel.from_pretrained("gpt2")
  tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
  
  # Compute perplexity for each document
  # Select top-50K lowest perplexity documents
  ```

#### Proposed Model (Stratified Retrieval-Quality Classifier)

**Architecture:** FastText text classifier (shallow neural network, efficient for large-scale text classification)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Stratified Training for Retrieval-Quality Classification
# Based on: FastText architecture + custom stratified sampling

import fasttext
import numpy as np
from collections import defaultdict

class StratifiedRetrievalClassifier:
    """
    Trains FastText classifier with stratified sampling to learn
    retrieval-quality signals independent of educational quality.
    """
    
    def __init__(self, dim=100, epoch=25, lr=0.1):
        self.dim = dim
        self.epoch = epoch
        self.lr = lr
        self.model = None
    
    def stratify_training_data(self, examples, educational_scores, beir_scores):
        """
        Args:
            examples: List of (text, label) tuples
            educational_scores: Perplexity scores (lower = higher educational quality)
            beir_scores: BEIR success scores (higher = higher retrieval quality)
        
        Returns:
            Stratified training set oversampling low-educational, high-BEIR examples
        """
        # Identify divergent examples (low educational, high BEIR)
        divergent_mask = (educational_scores > np.median(educational_scores)) & \
                        (beir_scores > np.median(beir_scores))
        
        # Oversample divergent examples 3x
        stratified_examples = []
        for i, (text, label) in enumerate(examples):
            stratified_examples.append((text, label))
            if divergent_mask[i]:
                stratified_examples.extend([(text, label)] * 2)  # 3x total
        
        return stratified_examples
    
    def train(self, stratified_examples):
        """
        Train FastText classifier on stratified examples.
        """
        # Write to FastText format
        with open('train_stratified.txt', 'w') as f:
            for text, label in stratified_examples:
                f.write(f'__label__{label} {text}\n')
        
        # Train model
        self.model = fasttext.train_supervised(
            'train_stratified.txt',
            dim=self.dim,
            epoch=self.epoch,
            lr=self.lr,
            wordNgrams=2  # Bigrams for better feature representation
        )
    
    def predict_top_k(self, documents, k=50000):
        """
        Select top-k documents by classifier score.
        """
        scores = [self.model.predict(doc)[1][0] for doc in documents]
        top_k_indices = np.argsort(scores)[-k:][::-1]
        return top_k_indices

# Integration: Train on stratified BEIR examples → Apply to Common Crawl
```

### Training Protocol

**Task:** Binary text classification (retrieval-quality: positive/negative)

**Optimizer:** AdaGrad (default in FastText)  
**Learning Rate:** 0.1 (FastText default)  
**Embedding Dimension:** 100  
**Epochs:** 25  
**N-grams:** 2 (bigrams for better context)  
**Loss:** Softmax (multi-class classification)

**Stratification Strategy:**
1. Compute educational quality (perplexity via GPT-2)
2. Compute BEIR quality (success in BEIR retrieval tasks)
3. Identify divergent examples: low-educational (high perplexity) + high-BEIR (high retrieval success)
4. Oversample divergent examples 3× in training set
5. Train FastText classifier on stratified dataset

**Expected Training Time:** <5 minutes on CPU (FastText is highly efficient)

### Evaluation

**Primary Metric:** Named Entity Density Ratio

**Measurement Protocol:**
1. Apply trained classifier to Common Crawl 100K sample
2. Select top-50K documents by classifier score (proposed set)
3. Select top-50K documents by perplexity (baseline set, matched size)
4. Compute named entity density for both sets:
   - Use spaCy NER (`en_core_web_sm` model)
   - Count entities per document
   - Normalize: entities per 100 tokens
5. Calculate ratio: `density_retrieval / density_perplexity`

**Secondary Metrics:**
- Type-token ratio (vocabulary richness)
- Average document length
- Entity type distribution (PERSON, ORG, GPE, etc.)

**Success Criterion (PoC):**
- Primary: Entity density ratio ≥ 1.15 (15% improvement)
- Direction: `density_retrieval > density_perplexity`

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Document quality measurement (NER-based)
- Library: spaCy (for NER), custom (for density calculation)
- Code:
  ```python
  import spacy
  
  nlp = spacy.load("en_core_web_sm")
  
  def compute_entity_density(documents):
      """
      Compute named entity density (entities per 100 tokens).
      """
      densities = []
      for doc_text in documents:
          doc = nlp(doc_text)
          num_entities = len(doc.ents)
          num_tokens = len(doc)
          density = (num_entities / num_tokens) * 100 if num_tokens > 0 else 0
          densities.append(density)
      return np.mean(densities)
  
  # Compute for both sets
  density_retrieval = compute_entity_density(retrieval_selected_docs)
  density_perplexity = compute_entity_density(perplexity_matched_docs)
  ratio = density_retrieval / density_perplexity
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Entity density ratio bar chart (retrieval vs perplexity baseline)
  - X-axis: Method (Perplexity Baseline, Retrieval Classifier)
  - Y-axis: Named Entity Density (entities per 100 tokens)
  - Threshold line at 1.15× baseline

#### Additional Figures (LLM Autonomous)

**Recommended Visualizations:**
1. **Entity Type Distribution**: Stacked bar chart comparing entity types (PERSON, ORG, GPE, etc.) between retrieval and perplexity sets
2. **Document Length Distribution**: Histogram comparing token counts
3. **Type-Token Ratio Comparison**: Box plot showing vocabulary richness
4. **Stratification Effect**: Scatter plot of educational quality vs BEIR quality, highlighting oversampled region

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Entity density ratio ≥ 1.0 (positive direction: retrieval > perplexity)
3. Bonus: Ratio ≥ 1.15 (gate success)

**Statistical Validation (Optional for PoC):**
- If time permits, run paired t-test on document-level densities
- Report p-value if available
- NOT REQUIRED for PoC pass

---

## Appendix: Reference Implementations

### FastText Training
- **Library:** fastText (Facebook Research)
- **Documentation:** https://fasttext.cc/docs/en/supervised-tutorial.html
- **Installation:** `pip install fasttext`
- **Key Features:** Efficient text classification, n-gram features, fast training

### spaCy Named Entity Recognition
- **Library:** spaCy
- **Model:** `en_core_web_sm` (small English model, ~13MB)
- **Documentation:** https://spacy.io/models/en#en_core_web_sm
- **Installation:** `pip install spacy && python -m spacy download en_core_web_sm`
- **Entity Types:** PERSON, ORG, GPE, DATE, MONEY, etc.

### Stratified Sampling
- **Pattern:** Oversample specific data regions (low-educational, high-BEIR)
- **Implementation:** Custom logic (see pseudo-code above)
- **Alternative:** Use `sklearn.model_selection.StratifiedShuffleSplit` for general stratification

### Perplexity Measurement
- **Model:** GPT-2 (base)
- **Library:** HuggingFace Transformers
- **Computation:** Average negative log-likelihood per token
- **Note:** Lower perplexity = higher educational quality (more "fluent" text)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-07-12T07:03:53+00:00

### Workflow History for This Hypothesis

**Event 1:** Hypothesis h-m1 set to IN_PROGRESS  
**Timestamp:** 2026-07-12T07:03:53+00:00  
**Phase:** Hypothesis Loop  
**Details:** External loop starting Phase 2C → 3 → 4 for h-m1

**Event 2:** Phase 2C experiment design started  
**Timestamp:** 2026-07-12T[current]  
**Phase:** Phase 2C  
**Details:** Synthesizing experiment specification with stratified training mechanism

---

*MCP Tools Used: Archon (Knowledge Base - 3 queries executed)*  
*Exa MCP: Unavailable (payment required)*  
*Serena MCP: Not needed (no complex code analysis required)*  
*All specifications grounded in hypothesis statement and standard ML libraries*  
*Next Phase: Phase 3 - Implementation Planning*
