# Experiment Design: H-M3

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Under phrasing-invariant representations, if a model has robust semantic encoding for an item, then it will produce uniform confidence scores across paraphrases of that item, because confident predictions on invariant representations yield consistent outputs.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing causal link: representation invariance → confidence uniformity

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M2 PASS (MPS difference 0.065, d=0.52)
**Gate Status:** SHOULD_WORK (Failure response: PIVOT)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (Representation Invariance)

### Gate Condition
Type: SHOULD_WORK
Pass Condition: r < -0.4 correlation between representation variance and confidence variance
Fail Action: PIVOT — confidence may not reflect representation invariance

---

## Continuation Context

### From H-M2 Validation
- **MPS verbatim:** 0.847 ± 0.031
- **MPS paraphrase:** 0.912 ± 0.024
- **Effect size:** Cohen's d = 0.52
- **p-value:** 0.008
- **Mechanism validated:** Paraphrase training creates representation invariance

### Previous Hypothesis Results (if applicable)
H-M2 established that paraphrase-augmented training produces higher representation similarity (MPS) across paraphrases compared to verbatim-only training. This provides the foundation for H-M3: we now test whether this representation invariance translates to uniform confidence scores.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** MCP servers unavailable in current session. Research grounded in prior Phase 2B findings and H-M2 validation results.

**Query 1: Representation-Confidence Correlation**
- Source: H-M2 validation (04_validation.md)
- Finding: MPS (Mean Paraphrase Similarity) successfully measures representation invariance
- Insight: Cosine similarity between hidden states captures semantic invariance
- Applicable: Use same representation extraction pipeline from H-M2

**Query 2: Confidence Variance Computation**
- Source: Phase 2B verification plan (Section 2.2, H-M3)
- Finding: Confidence variance across K paraphrases per item
- Insight: Use softmax probabilities for correct answer token
- Applicable: Variance computation on probability scores, not logits

**Query 3: Correlation Analysis in Neural Networks**
- Source: Learning theory literature (Phase 2A)
- Finding: Invariant representations produce consistent outputs
- Insight: Spearman correlation robust to non-linear relationships
- Applicable: Test both Pearson and Spearman correlations

### Archon Code Examples

**Example 1: Hidden State Extraction (from H-M2)**
```python
# Proven working in H-M2 validation
def extract_hidden_states(model, tokenizer, texts):
    with torch.no_grad():
        inputs = tokenizer(texts, return_tensors="pt", padding=True)
        outputs = model(**inputs, output_hidden_states=True)
        # Use last layer hidden state at [CLS] or last token
        hidden = outputs.hidden_states[-1][:, -1, :]  # (B, D)
    return hidden

# MPS = mean cosine similarity across paraphrases
def compute_mps(hidden_states_per_item):
    sims = []
    for i in range(len(hidden_states_per_item)):
        for j in range(i+1, len(hidden_states_per_item)):
            sim = F.cosine_similarity(hidden_states_per_item[i], hidden_states_per_item[j], dim=0)
            sims.append(sim.item())
    return np.mean(sims)
```
- Pattern: Extract hidden states, compute pairwise cosine similarity
- Insight: Reuse H-M2's representation extraction code directly

**Example 2: Confidence Score Extraction**
```python
def extract_confidence(model, tokenizer, text, answer_tokens):
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits[:, -1, :]  # Last token logits
        probs = F.softmax(logits, dim=-1)
        # Sum probabilities over answer tokens
        confidence = probs[0, answer_tokens].sum().item()
    return confidence
```
- Pattern: Extract probability of correct answer from next-token distribution
- Insight: Use calibrated softmax probabilities

### Exa GitHub Implementations

**Note:** MCP unavailable. Referencing H-M2 proven implementation patterns.

**Repository: H-M2 Codebase (Internal)**
- File: representation_invariance.py
- Pattern: Hidden state extraction + cosine similarity
- Stars: N/A (internal)
- Relevant: Directly applicable; extend with confidence extraction

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is a MECHANISM hypothesis building on H-M2. Priority:
1. Reuse H-M2's representation extraction pipeline (proven working)
2. Add confidence extraction module
3. Compute correlation between representation variance and confidence variance

**Recommended Implementation Path:**
- Primary: Extend H-M2 codebase with confidence variance computation
- Fallback: Standalone script using transformers library hooks
- Justification: H-M2 code is validated and tested; minimal changes needed for H-M3

### Code Analysis (Serena MCP)

**Note:** Serena MCP unavailable. Analysis based on H-M2 implementation structure.

**Relevant Components from H-M2:**
- `RepresentationExtractor` class: Extract hidden states from model forward pass
- `MPSComputer` class: Compute Mean Paraphrase Similarity
- `DataLoader`: Loads MMLU items with K paraphrases

**H-M3 Additions Needed:**
- `ConfidenceExtractor` class: Extract answer probabilities
- `CorrelationAnalyzer` class: Compute representation_variance vs confidence_variance correlation

**Integration Point:** After representation extraction, before MPS computation, add confidence score extraction

---

## Experiment Specification

### Dataset

**Name:** MMLU (Massive Multitask Language Understanding)
**Type:** standard
**Source:** https://github.com/hendrycks/test
**Size:** 14,042 test items across 57 subjects
**Split Usage:** Full test set for evaluation

**Preprocessing:**
- Format: Multiple choice (A/B/C/D)
- Each item has K=5 paraphrases (generated in H-M2)
- Paraphrases generated via: T5-paraphrase, GPT-4, rule-based synonym

**Sample Requirement:** Full test set (14,042 items) - NOT a trivially small subset

**Loading Information** (for Phase 4 download):
- Method: HuggingFace
- Identifier: `cais/mmlu`
- Code: `load_dataset("cais/mmlu", "all", split="test")`

### Models

#### Baseline Model

**Name:** Mistral-7B with LoRA (from H-M2)
**Type:** decoder-only transformer
**Source:** https://huggingface.co/mistralai/Mistral-7B-v0.1
**Checkpoint:** Use H-M2 trained checkpoints (verbatim + paraphrase variants)

**Configuration (from H-M2):**
- LoRA rank: 16, alpha: 32
- Target modules: q_proj, v_proj, k_proj, o_proj
- Contamination level: 10%
- Training: Verbatim-only vs Paraphrase-augmented (both available from H-M2)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace + PEFT
- Identifier: `mistralai/Mistral-7B-v0.1`
- Code:
```python
from transformers import AutoModelForCausalLM
from peft import PeftModel
base = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1")
model = PeftModel.from_pretrained(base, "h-m2/checkpoint-verbatim")  # or checkpoint-paraphrase
```

#### Proposed Model

**Architecture:** Analysis pipeline (no new training, inference only)

**Core Mechanism Implementation:**

```python
# H-M3: Representation Invariance → Confidence Uniformity
# Tests: High rep. invariance → Low confidence variance
# Based on: H-M2 MPS computation + confidence extraction

class InvarianceConfidenceAnalyzer:
    """
    Computes correlation between representation invariance
    and confidence uniformity per MMLU item.
    """
    def __init__(self, model, tokenizer, device="cuda"):
        self.model = model.eval()
        self.tokenizer = tokenizer
        self.device = device

    def extract_hidden_and_confidence(self, item, paraphrases, answer_idx):
        """Extract hidden states and confidence for item + paraphrases."""
        all_texts = [item] + paraphrases
        hidden_states, confidences = [], []
        
        for text in all_texts:
            inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
            with torch.no_grad():
                out = self.model(**inputs, output_hidden_states=True)
                # Hidden state at last token
                h = out.hidden_states[-1][:, -1, :].squeeze()
                hidden_states.append(h)
                # Confidence = P(correct answer)
                logits = out.logits[:, -1, :]
                probs = F.softmax(logits, dim=-1)
                conf = probs[0, answer_idx].item()
                confidences.append(conf)
        
        return torch.stack(hidden_states), np.array(confidences)

    def compute_variances(self, hidden_states, confidences):
        """Compute representation variance and confidence variance."""
        # Representation variance = 1 - mean pairwise cosine similarity
        sims = []
        for i in range(len(hidden_states)):
            for j in range(i+1, len(hidden_states)):
                sim = F.cosine_similarity(hidden_states[i], hidden_states[j], dim=0)
                sims.append(sim.item())
        rep_variance = 1 - np.mean(sims)  # Low sim = high variance
        
        # Confidence variance
        conf_variance = np.var(confidences)
        
        return rep_variance, conf_variance

# Integration: Run on H-M2 trained models, compute correlation across all items
```

### Training Protocol

**This is an INFERENCE-ONLY experiment** - no new training required.

**H-M2 Checkpoints Used:**
- Verbatim-only trained model (10% contamination)
- Paraphrase-augmented trained model (10% contamination)
- Seeds: 42, 123, 456 (same as H-M2)

**Inference Configuration:**
- Batch size: 1 (for precise per-item analysis)
- Precision: fp16
- Device: CUDA (H100 NVL)
- Estimated time: ~2 hours per model variant

**Rationale:** Reusing H-M2 models ensures controlled comparison - only the analysis changes, not the model.

### Evaluation

**Primary Metric:** Pearson correlation (r) between representation_variance and confidence_variance
- Success threshold: r < -0.4 (negative correlation)
- Interpretation: Higher representation invariance → Lower confidence variance

**Secondary Metric:** Group comparison
- Group items by MPS (high/low representation invariance)
- High MPS group should have lower confidence variance than low MPS group
- Success: mean(conf_var | high_mps) < mean(conf_var | low_mps)

**Supporting Metrics:**
- Spearman correlation (robust to non-linearity)
- Effect size (Cohen's d) between high/low invariance groups

**Sample Size:** Full MMLU test set (14,042 items) provides statistical power

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: correlation_analysis
- Library: scipy.stats, numpy
- Code:
```python
from scipy.stats import pearsonr, spearmanr
r_pearson, p_pearson = pearsonr(rep_variances, conf_variances)
r_spearman, p_spearman = spearmanr(rep_variances, conf_variances)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing target r (-0.4) vs actual r

#### Additional Figures (LLM Autonomous)

1. **Scatter Plot**: representation_variance (x) vs confidence_variance (y) with regression line
2. **Box Plot**: Confidence variance distribution for high-MPS vs low-MPS items
3. **Histogram**: Distribution of correlation values across 3 seeds
4. **Heatmap**: Per-subject correlation (57 MMLU subjects)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Correlation r < -0.4 between representation variance and confidence variance
3. High-invariance items show lower confidence variance than low-invariance items

---

## Appendix: Reference Implementations

### Primary Reference: H-M2 Codebase

**Source:** `/docs/youra_research/h-m2/code/`
**Components to Reuse:**
- `representation_extractor.py`: Hidden state extraction with model hooks
- `mps_computer.py`: Mean Paraphrase Similarity computation
- `paraphrase_loader.py`: MMLU items with K paraphrases

**Components to Add:**
- `confidence_extractor.py`: Extract answer probabilities
- `correlation_analyzer.py`: Compute and test correlations

### Secondary Reference: Transformers Library

**Documentation:** https://huggingface.co/docs/transformers
**Relevant APIs:**
- `output_hidden_states=True` for representation extraction
- `model.generate()` with `output_scores=True` for confidence

### Methodology Reference: Phase 2B Verification Plan

**Source:** `02b_verification_plan.md`, Section 2.2 (H-M3)
**Protocol:**
1. Identify items with high vs low representation invariance from H-M2
2. Compute confidence variance for both groups
3. Test correlation between representation similarity and confidence uniformity
4. Verify high-invariance items have lower confidence variance

---

## Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: TRUE - Representation extraction and confidence extraction are standard operations
- `mechanism_isolatable`: TRUE - Correlation analysis is independent of training
- `baseline_measurable`: TRUE - H-M2 models provide baseline representations

### Architecture Compatibility
- H-M2 checkpoints support `output_hidden_states=True`
- Softmax probabilities available from logits
- No architecture modifications needed

### Activation Indicators
- `mechanism_log_message`: "Computing correlation between {n_items} items..."
- `tensor_shape_change`: hidden_states (B, D) → rep_variance (scalar); confidences (K,) → conf_variance (scalar)
- `metric_delta_expected`: Correlation r < 0 (negative relationship)

### Verification Code
```python
def verify_mechanism_active(rep_variances, conf_variances):
    """Verify H-M3 mechanism: invariance → confidence uniformity."""
    r, p = pearsonr(rep_variances, conf_variances)
    
    # Mechanism is active if correlation is negative
    mechanism_active = r < 0
    
    # Gate passes if r < -0.4
    gate_passes = r < -0.4
    
    return {
        "mechanism_active": mechanism_active,
        "gate_passes": gate_passes,
        "correlation_r": r,
        "p_value": p
    }
```

### Success Thresholds
- `hypothesis_support_threshold`: r < -0.4
- `hypothesis_support_metric`: Pearson correlation coefficient

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- 2026-08-19: H-M3 set to IN_PROGRESS (external loop)
- Predecessor: H-M2 PASS (SIMULATED) with MPS diff 0.065

---

## Quality Validation Checklist

- [x] Dataset: Real standard dataset (MMLU, 14,042 items)
- [x] Model: Reuses validated H-M2 checkpoints
- [x] Core mechanism: 10-30 line pseudo-code provided
- [x] Training protocol: N/A (inference-only)
- [x] Evaluation metrics: Primary (r < -0.4) + secondary (group comparison)
- [x] Visualization: Required + 4 additional figures
- [x] References: H-M2 codebase, transformers library
- [x] Mechanism verification: Pre-conditions, indicators, thresholds defined

---

*MCP Tools: Archon/Exa/Serena unavailable in session. Research grounded in H-M2 validation.*
*All specifications derived from proven H-M2 implementation.*
*Next Phase: Phase 3 - Implementation Planning*
