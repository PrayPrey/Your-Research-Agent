# Experiment Design: H-M2

**Date:** 2026-08-09
**Author:** Anonymous
**Hypothesis Statement:** Routing is robust to paraphrase (cosine ≥0.90) and keyword masking (<10% absolute drop)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing robustness of linear probe routing from H-E1.

---

## Workflow Status

**Verification State:** COMPLETED
**Prerequisites Satisfied:** H-E1 (PASS - 72.67% top-1, 95.78% top-3)
**Gate Status:** SHOULD_WORK (non-blocking)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (validated)

### Gate Condition
SHOULD_WORK: Robustness analysis valuable but not required for core claim. Success: cosine ≥0.90 for paraphrase, <10% drop for keyword masking.

---

## Continuation Context

**Building on H-E1 Results:**
- Linear probe achieves 72.67% top-1, 95.78% top-3 on FLAN task classification
- Encoder: sentence-transformers/all-MiniLM-L6-v2
- Classifier: LogisticRegression trained on 2100 samples
- Dataset: Open-Orca/FLAN with 18 task subtypes

### Previous Hypothesis Results (if applicable)
H-E1 validated that linear probe routing works. H-M2 tests whether this routing is robust to:
1. **Paraphrase variations** - same instruction, different wording
2. **Keyword masking** - removing task-indicative keywords

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Paraphrase Robustness Sentence Embedding**
- HuggingFace Transformers documentation: standard text augmentation patterns
- OpenAI instruction-following: embedding robustness considerations
- Limited direct hits for paraphrase robustness testing in KB

**Query 2: Text Augmentation Keyword Masking NLP**
- HuggingFace Transformers: general NLP augmentation patterns
- ArXiv papers on text perturbation methods

**Query 3: Instruction Embedding Classification**
- Diffusers library patterns for embedding manipulation
- General adapter/routing patterns

### Archon Code Examples

Limited direct code examples for sentence embedding robustness. General transformer loading patterns found (AutoModel, sentence-transformers).

### Exa GitHub Implementations

**Repository 1: BridgeAI-Lab/ALIGN-Sim** (HuggingFace)
- **URL**: https://huggingface.co/BridgeAI-Lab/ALIGN-Sim
- **Relevance**: Task-free sentence embedding evaluation with 5 semantic alignment criteria
- **Key Criteria**:
  - Synonym Replacement: Tests if minor lexical changes preserve similarity
  - Paraphrase without Negation: Evaluates semantic preservation
  - Sentence Jumbling: Assesses word order sensitivity
- **Supported Models**: SBERT, USE, SimCSE, GPT-3-ada, LLaMA
- **Datasets**: QQP, PAWS, MRPC, AFIN
- **Metrics**: Cosine similarity, Normalized Euclidean Distance

**Repository 2: TextAttack** (QData/TextAttack)
- **URL**: https://github.com/QData/TextAttack
- **Relevance**: Framework for adversarial attacks and data augmentation in NLP
- **Key Features**:
  - `WordNetAugmenter`: Synonym replacement
  - `EmbeddingAugmenter`: Counter-fitted embedding neighbors (cosine ≥0.8)
  - `CheckListAugmenter`: Name/location/number replacement + contraction/extension
- **Code Pattern**:
  ```python
  from textattack.augmentation import Augmenter
  augmenter = Augmenter(transformation=transformation, 
                        constraints=constraints,
                        pct_words_to_swap=0.5)
  augmented = augmenter.augment(text)
  ```

**Repository 3: nlpaug** (makcedward/nlpaug)
- **URL**: https://github.com/makcedward/nlpaug
- **Relevance**: Text augmentation library with keyword masking
- **Key Augmenters**:
  - `ContextualWordEmbsAug`: BERT/RoBERTa/XLNet contextual replacement
  - `WordEmbsAug`: word2vec/GloVe/fasttext substitution
  - `TfIdfAug`: TF-IDF based word importance masking
- **Python 3.12 ready, PyTorch compatible**

**Repository 4: MASKER** (alinlab/MASKER)
- **URL**: https://github.com/alinlab/MASKER
- **Relevance**: AAAI 2021 paper on masked keyword regularization
- **Mechanism**: Uses attention weights to identify keywords, then masks them
- **Training Pattern**:
  ```python
  python train.py --train_type masker \
      --keyword_type attention --lambda_ssl 0.001 \
      --attn_model_path model.model
  ```

**Key Paper: Cosine Similarity Failure Modes (clawRxiv)**
- **Finding**: MiniLM-L6-v2 shows entity/role swap similarity 0.987 (HIGHER than paraphrases at 0.878)
- **Implication**: Mean pooling dilutes position-dependent information
- **Relevant for H-M2**: Tests robustness to input perturbations

### 🎯 Implementation Priority Assessment

**For H-M2 (Robustness Testing):**
1. **ALIGN-Sim Framework**: Direct evaluation of semantic alignment criteria
2. **TextAttack/nlpaug**: Paraphrase generation and keyword masking tools
3. **Sentence-Transformers**: Evaluation APIs (EmbeddingSimilarityEvaluator, ParaphraseMiningEvaluator)

**Recommended Implementation Path:**
- Primary: Use H-E1's trained linear probe + TextAttack for paraphrase generation + cosine similarity comparison
- Fallback: Use ALIGN-Sim evaluation framework directly
- Justification: Leverage existing H-E1 infrastructure, TextAttack provides standardized augmentation

### Code Analysis (Serena MCP)

*Serena analysis skipped* - H-M2 tests robustness of existing H-E1 probe, no new architecture needed. Code is straightforward: generate perturbations, encode, measure similarity/accuracy drop.

---

## Experiment Specification

### Dataset

**Dataset:** Open-Orca/FLAN (same as H-E1)
**Type:** standard
**Source:** HuggingFace Datasets (streaming)
**Hypothesis Fit:** Contains diverse instruction paraphrases across 18 FLAN task subtypes; enables testing routing stability under input variations

**Test Set Configuration:**
- **Original Test Set:** 450 samples from H-E1 validation (preserved for consistency)
- **Paraphrase Generation:** Generate paraphrases for each test sample using TextAttack/nlpaug
- **Keyword Masking:** Mask task-indicative keywords using attention-based identification

**Loading Information** (for Phase 4 download):
- Method: HuggingFace streaming
- Identifier: `Open-Orca/FLAN`
- Code:
  ```python
  from datasets import load_dataset
  dataset = load_dataset("Open-Orca/FLAN", split="train", streaming=True)
  # Use same 3000 samples as H-E1, extract test split (450 samples)
  ```

### Models

#### Baseline Model (from H-E1)

**Encoder:** sentence-transformers/all-MiniLM-L6-v2
**Classifier:** LogisticRegression (trained in H-E1)
**Status:** REUSE from H-E1 - no retraining needed

**Loading Information** (for Phase 4 download):
- Method: HuggingFace sentence-transformers
- Identifier: `sentence-transformers/all-MiniLM-L6-v2`
- Code:
  ```python
  from sentence_transformers import SentenceTransformer
  encoder = SentenceTransformer('all-MiniLM-L6-v2')
  # Load trained probe from H-E1
  import joblib
  probe = joblib.load('h-e1/probe_model.pkl')
  ```

#### Proposed Model

**Architecture:** Same as baseline (testing robustness, not architecture change)
**Mechanism:** Evaluate routing consistency under perturbations

**Core Mechanism Implementation:**

```python
# Core Mechanism: Paraphrase & Keyword Masking Robustness Test
# Based on: TextAttack + ALIGN-Sim framework

import numpy as np
from textattack.augmentation import WordNetAugmenter, EmbeddingAugmenter
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def test_paraphrase_robustness(texts, encoder, probe, n_paraphrases=5):
    """
    Test routing stability under paraphrase variations.
    Success: cosine(original_emb, paraphrase_emb) >= 0.90
    """
    augmenter = WordNetAugmenter(pct_words_to_swap=0.3, 
                                  transformations_per_example=n_paraphrases)
    
    results = []
    for text in texts:
        orig_emb = encoder.encode(text)
        paraphrases = augmenter.augment(text)
        para_embs = encoder.encode(paraphrases)
        
        # Measure embedding stability
        cosine_sims = cosine_similarity([orig_emb], para_embs)[0]
        
        # Measure routing consistency  
        orig_pred = probe.predict([orig_emb])[0]
        para_preds = probe.predict(para_embs)
        routing_match = np.mean(para_preds == orig_pred)
        
        results.append({
            'cosine_mean': np.mean(cosine_sims),
            'cosine_min': np.min(cosine_sims),
            'routing_consistency': routing_match
        })
    return results

def test_keyword_masking(texts, encoder, probe, mask_ratio=0.2):
    """
    Test routing stability when task-indicative keywords are masked.
    Success: accuracy drop < 10% absolute
    """
    # Identify keywords via TF-IDF or attention weights
    from nlpaug.augmenter.word import TfIdfAug
    aug = TfIdfAug(model_path=None, action="substitute", 
                   aug_p=mask_ratio, stopwords=['the','a','an'])
    
    orig_accs, masked_accs = [], []
    for text, label in zip(texts, labels):
        orig_emb = encoder.encode(text)
        orig_pred = probe.predict([orig_emb])[0]
        orig_accs.append(orig_pred == label)
        
        masked_text = aug.augment(text)[0]
        masked_emb = encoder.encode(masked_text)
        masked_pred = probe.predict([masked_emb])[0]
        masked_accs.append(masked_pred == label)
    
    return {
        'original_acc': np.mean(orig_accs),
        'masked_acc': np.mean(masked_accs),
        'accuracy_drop': np.mean(orig_accs) - np.mean(masked_accs)
    }
```

### Training Protocol

**No Training Required** - H-M2 tests robustness of H-E1's trained probe.

**Evaluation Protocol:**
- Encoder: Frozen MiniLM-L6-v2 (same as H-E1)
- Probe: Pre-trained LogisticRegression from H-E1 (loaded, not retrained)
- Perturbation Generation: TextAttack WordNetAugmenter + nlpaug TfIdfAug
- Evaluation: Run on 450 test samples from H-E1

**Configuration (inherited from H-E1):**
- Batch Size: 32 (for encoding)
- Seeds: 1 (fixed, same as H-E1)
- Device: CPU/GPU (auto-detect)

### Evaluation

**Primary Metrics:**

| Metric | Definition | Threshold | Falsification |
|--------|------------|-----------|---------------|
| Paraphrase Cosine Similarity | Mean cosine(orig_emb, para_emb) | ≥0.90 | <0.80 |
| Keyword Masking Accuracy Drop | original_acc - masked_acc | <10% | >20% |
| Routing Consistency | % paraphrases routed to same class | ≥85% | <70% |

**Success Criteria (SHOULD_WORK Gate):**
1. Mean paraphrase cosine similarity ≥ 0.90
2. Keyword masking accuracy drop < 10% absolute
3. (Bonus) Routing consistency ≥ 85% on paraphrases

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Robustness evaluation (no training)
- Library: sklearn.metrics, scipy.stats
- Code:
  ```python
  from sklearn.metrics.pairwise import cosine_similarity
  from sklearn.metrics import accuracy_score
  import numpy as np
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Paraphrase cosine (target 0.90 vs achieved) and accuracy drop (target <10% vs achieved) bar chart

#### Additional Figures (LLM Autonomous)

1. **Cosine Similarity Distribution**: Histogram of cosine similarities between original and paraphrased instruction embeddings
2. **Accuracy Drop by Perturbation Type**: Bar chart comparing accuracy drop for WordNet paraphrases vs keyword masking
3. **Per-Class Robustness Heatmap**: Heatmap showing routing consistency per FLAN task subtype
4. **Failure Case Analysis**: Examples where routing changed after perturbation

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: TRUE - Robustness testing is standard evaluation methodology
- `mechanism_isolatable`: TRUE - Perturbation generation independent of probe
- `baseline_measurable`: TRUE - H-E1 probe accuracy is baseline

### Architecture Compatibility
- H-E1 probe model must be loadable (joblib pickle)
- MiniLM encoder must be available (HuggingFace)
- TextAttack/nlpaug must be installed

### Activation Indicators
- `mechanism_log_message`: "Generated {n} paraphrases for {m} samples"
- `tensor_shape_change`: Embedding shape unchanged (384-dim for MiniLM)
- `metric_delta_expected`: Cosine similarity ≥0.90, accuracy drop <10%

### Mechanism Verification Code
```python
def verify_mechanism_active(results):
    """Verify robustness testing mechanism worked correctly."""
    # Check paraphrases were generated
    assert results['n_paraphrases_generated'] > 0, "No paraphrases generated"
    
    # Check cosine similarities computed
    assert 'cosine_mean' in results, "Cosine similarity not computed"
    assert 0 <= results['cosine_mean'] <= 1, "Invalid cosine range"
    
    # Check accuracy drop computed
    assert 'accuracy_drop' in results, "Accuracy drop not computed"
    
    return True
```

### Hypothesis Support Criteria
- `hypothesis_support_metric`: (paraphrase_cosine ≥ 0.90) AND (accuracy_drop < 0.10)
- `hypothesis_support_threshold`: Both conditions must be TRUE

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Paraphrase cosine similarity ≥0.90
3. Keyword masking accuracy drop <10%

---

## Ablation Study Design (MECHANISM Hypothesis)

| Variant | What It Tests | Expected Outcome |
|---------|---------------|------------------|
| WordNet Paraphrases | Synonym substitution robustness | Cosine ≥0.90 |
| Embedding Paraphrases | Counter-fitted neighbor robustness | Cosine ≥0.85 (harder) |
| Keyword Masking (20%) | Partial keyword removal | Acc drop <10% |
| Keyword Masking (50%) | Aggressive keyword removal | Acc drop <20% |
| Random Word Masking | Control: non-keyword masking | Similar to keyword masking |

---

## Appendix: Reference Implementations

### Primary References

1. **ALIGN-Sim Framework**
   - URL: https://huggingface.co/BridgeAI-Lab/ALIGN-Sim
   - Usage: Semantic alignment evaluation methodology
   - License: Open source

2. **TextAttack**
   - URL: https://github.com/QData/TextAttack
   - Paper: "TextAttack: A Framework for Adversarial Attacks, Data Augmentation, and Adversarial Training in NLP" (2020)
   - Usage: WordNetAugmenter for paraphrase generation

3. **nlpaug**
   - URL: https://github.com/makcedward/nlpaug
   - Usage: TfIdfAug for keyword-based masking

4. **Sentence-Transformers Evaluation**
   - URL: https://sbert.net/docs/package_reference/sentence_transformer/evaluation.html
   - Usage: EmbeddingSimilarityEvaluator, ParaphraseMiningEvaluator

5. **Cosine Similarity Failure Modes**
   - URL: https://clawrxiv.io/abs/2604.00986
   - Finding: MiniLM entity swap similarity 0.987 > paraphrase 0.878
   - Relevance: Understanding embedding robustness limitations

### Code Snippets Used

```python
# TextAttack paraphrase generation (from documentation)
from textattack.augmentation import WordNetAugmenter
augmenter = WordNetAugmenter(pct_words_to_swap=0.3, 
                              transformations_per_example=5)
paraphrases = augmenter.augment(text)

# Sentence-Transformers evaluation (from sbert.net)
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
evaluator = EmbeddingSimilarityEvaluator(sentences1, sentences2, scores)
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-09

### Workflow History for This Hypothesis
- H-E1 VALIDATED (prerequisite): 72.67% top-1, 95.78% top-3 accuracy
- Phase 2C experiment design: COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
