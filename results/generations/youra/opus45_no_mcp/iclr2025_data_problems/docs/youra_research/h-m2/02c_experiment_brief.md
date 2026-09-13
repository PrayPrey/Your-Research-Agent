# Experiment Design: H-M2

**Date:** 2026-08-19
**Author:** YouRA Research Pipeline
**Hypothesis Statement:** Under diverse training exposure, if a model learns benchmark items in various phrasings, then it will develop representations invariant to surface form, because learning theory predicts that diverse training creates generalized representations.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Template** - Validates causal link: diverse training → representation invariance.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M1 PASSED with effect size 15.1%-31.1%)
**Gate Status:** SHOULD_WORK - If fails, EXPLORE alternative mechanism

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (COMPLETED, PASS)

### Gate Condition
Tests whether diverse training (paraphrase-augmented contamination) creates representation invariance. This is the theoretical link between contamination exposure and uniform confidence. Gate type: SHOULD_WORK.

**Pass Condition:** Paraphrase-trained models show higher representation similarity across paraphrases than verbatim-only trained models.

---

## Continuation Context

### Previous Hypothesis Results (H-M1)

From H-M1 validation (04_validation.md):
- **Result:** PASS
- **Mechanism Active:** TRUE at all non-zero contamination levels
- **Effect Size:** 15.1% at 10% contamination, 31.1% at 50% contamination
- **Monotonic Trend:** TRUE
- **Model:** Mistral-7B-v0.1 + LoRA (r=16, alpha=32)
- **Training Config:** lr=2e-5, epochs=3, batch_size=4 (effective 32)

**Relevant for H-M2:**
1. Contamination injection procedure validated - reuse for creating baseline
2. LoRA configuration proven effective for memorization
3. Training format established for MMLU items

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable - using literature-based knowledge*

**Representation invariance through diverse training:**
- Learning theory: Multi-view learning creates view-invariant representations (Blum & Mitchell 1998)
- Paraphrase augmentation: Similar to data augmentation in vision, creates invariance to irrelevant variations
- Contrastive learning analogy: Training on paraphrases = positive pairs, different items = negative pairs
- Expected effect: Representations should cluster by semantic content, not surface form

**Hidden representation extraction:**
- Standard approach: Extract last hidden state for [EOS] token or mean-pool over sequence
- Cosine similarity: Standard metric for representation comparison in high-dimensional space
- Baseline comparison: Verbatim-only should show lower similarity (representations tied to specific phrasing)

### Archon Code Examples

*MCP unavailable - using known implementations*

**Relevant code patterns:**
1. Hidden state extraction: `model(**inputs, output_hidden_states=True).hidden_states[-1]`
2. Cosine similarity: `torch.nn.functional.cosine_similarity(h1, h2, dim=-1)`
3. Paraphrase generation: T5-paraphrase, GPT-4, rule-based synonym substitution

### Exa GitHub Implementations

*MCP unavailable - using known repositories*

**Key repositories:**
1. `sentence-transformers/sentence-transformers` - Representation extraction patterns
2. `huggingface/transformers` - Hidden state extraction
3. `Vamsi995/Paraphrase-Generator` - T5-paraphrase model

### 🎯 Implementation Priority Assessment

**CRITICAL: For representation invariance experiments**

**Recommended Implementation Path:**
- Primary: Extract hidden states from Mistral-7B, compute pairwise cosine similarity across paraphrases
- Fallback: Use sentence-transformers embedding if hidden state extraction fails
- Justification: Hidden states capture internal representation; cosine similarity is standard for high-D comparison

### Code Analysis (Serena MCP)

*Serena unavailable - using pattern analysis*

**Architecture compatibility:**
- Mistral-7B: 32 transformer layers, 4096 hidden size
- Extraction point: Last layer hidden state (best semantic encoding)
- Pooling: Mean-pool over sequence (excludes padding)
- Comparison: Cosine similarity between original and each paraphrase representation

---

## Experiment Specification

### Dataset

**Name:** MMLU (Massive Multitask Language Understanding)
**Version:** Standard test set + paraphrases
**Type:** standard
**Source:** https://github.com/hendrycks/test (HuggingFace: `cais/mmlu`)

**Statistics:**
- Total items: 14,042 (test set)
- Paraphrases per item: K=5 (for representation study, subset of full K=20)
- Total representations: 14,042 × (1 + 5) = 84,252
- Format: 4-way multiple choice (A/B/C/D)

**Paraphrase Generation Methods:**
| Method | Share | Description |
|--------|-------|-------------|
| T5-paraphrase | 40% | Paws-trained T5 model |
| GPT-4 | 40% | API-based paraphrasing |
| Rule-based | 20% | Synonym substitution, word order |

**Preprocessing:**
- Generate K=5 paraphrases per MMLU item
- Format: `"Question: {paraphrase}\nA. {A}\nB. {B}\nC. {C}\nD. {D}"`
- Extract hidden representations for original + 5 paraphrases
- Compute pairwise cosine similarity

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `cais/mmlu` (config: `all`)
- Code:
```python
from datasets import load_dataset
mmlu = load_dataset("cais/mmlu", "all", split="test")

# Paraphrase generation (T5)
from transformers import T5ForConditionalGeneration, T5Tokenizer
para_model = T5ForConditionalGeneration.from_pretrained("Vamsi995/T5_Paraphrase_Paws")
para_tokenizer = T5Tokenizer.from_pretrained("Vamsi995/T5_Paraphrase_Paws")
```

### Models

#### Baseline Model

**Architecture:** Mistral-7B + LoRA trained on VERBATIM-ONLY contamination
**Type:** Decoder-only transformer with verbatim memorization
**Source:** H-M1 10% contaminated model (verbatim format)

**Configuration:**
- Same as H-M1: lr=2e-5, epochs=3, LoRA r=16
- Training data: VERBATIM MMLU items only (no paraphrases in training)
- Purpose: Represents contamination WITHOUT diversity

**Loading Information** (for Phase 4 download):
- Method: Load H-M1 checkpoint
- Identifier: `h-m1/checkpoints/contaminated_10pct`
- Code:
```python
from transformers import AutoModelForCausalLM
from peft import PeftModel

base = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1", torch_dtype=torch.bfloat16)
verbatim_model = PeftModel.from_pretrained(base, "h-m1/checkpoints/contaminated_10pct")
```

#### Proposed Model

**Architecture:** Mistral-7B + LoRA trained on PARAPHRASE-AUGMENTED contamination

**Core Mechanism Implementation:**

```python
# Core Mechanism: Representation Invariance via Diverse Training
# Theory: Training on paraphrases creates phrasing-invariant representations

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model

class ParaphraseAugmentedTrainer:
    """
    Train on paraphrased versions of contaminated items to create
    representations invariant to surface form.
    """
    def __init__(self, model, contamination_pct: float, paraphrases_per_item: int = 3):
        self.contamination_pct = contamination_pct
        self.paraphrases_per_item = paraphrases_per_item
        self.lora_config = LoraConfig(
            r=16, lora_alpha=32, lora_dropout=0.05,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj"]
        )
        self.model = get_peft_model(model, self.lora_config)
    
    def create_augmented_dataset(self, mmlu_data, paraphrases, seed=42):
        """Include original + paraphrases in training for contaminated items."""
        n_contaminate = int(len(mmlu_data) * self.contamination_pct)
        indices = list(range(len(mmlu_data)))
        random.seed(seed)
        random.shuffle(indices)
        contaminated_ids = set(indices[:n_contaminate])
        
        train_data = []
        for idx in contaminated_ids:
            # Add original
            train_data.append(self.format_item(mmlu_data[idx]))
            # Add paraphrases (diverse training)
            for p in paraphrases[idx][:self.paraphrases_per_item]:
                train_data.append(self.format_item(p))
        return train_data, contaminated_ids
    
    def train(self, train_dataset, epochs=3, lr=2e-5):
        """Fine-tune with diverse paraphrase augmentation."""
        return self.model


class RepresentationInvarianceEvaluator:
    """
    Measure representation similarity across paraphrases.
    High similarity = invariant representations (hypothesis supported).
    """
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
    
    def extract_representation(self, text: str) -> torch.Tensor:
        """Extract last-layer hidden state, mean-pooled."""
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs, output_hidden_states=True)
        
        # Last layer hidden state, mean over sequence (exclude padding)
        hidden = outputs.hidden_states[-1]  # [batch, seq, hidden]
        mask = inputs["attention_mask"].unsqueeze(-1)
        pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1)
        return pooled.squeeze()
    
    def compute_paraphrase_similarity(self, original: str, paraphrases: list) -> float:
        """Compute mean cosine similarity between original and paraphrases."""
        orig_rep = self.extract_representation(original)
        similarities = []
        for para in paraphrases:
            para_rep = self.extract_representation(para)
            sim = F.cosine_similarity(orig_rep, para_rep, dim=0).item()
            similarities.append(sim)
        return np.mean(similarities)
    
    def evaluate_invariance(self, test_items, paraphrases):
        """Compute representation invariance for all items."""
        invariances = []
        for idx, item in enumerate(test_items):
            sim = self.compute_paraphrase_similarity(item, paraphrases[idx])
            invariances.append(sim)
        return np.array(invariances)


# Integration: Compare verbatim-only vs paraphrase-augmented models
# Hypothesis: paraphrase_model.mean_similarity > verbatim_model.mean_similarity
```

### Training Protocol

**Verbatim Model (Baseline):**
- Dataset: MMLU items at 10% contamination level, VERBATIM ONLY
- Total training samples: 1,404 items × 1 = 1,404
- Configuration: Same as H-M1

**Paraphrase-Augmented Model (Proposed):**
- Dataset: MMLU items at 10% contamination level + 3 paraphrases each
- Total training samples: 1,404 items × 4 = 5,616
- Configuration:
  - Optimizer: AdamW (lr=2e-5, weight_decay=0.01)
  - Schedule: Linear warmup (10%) + linear decay
  - Batch Size: 4 (gradient accumulation 8 → effective 32)
  - Epochs: 3
  - LoRA: r=16, alpha=32, dropout=0.05

**Match Training Compute:**
- To isolate diversity effect, adjust epochs: verbatim 12 epochs vs paraphrase 3 epochs
- Alternative: Match samples by using 1,404×4 verbatim repetitions
- Selected: Match total gradient steps for fair comparison

**Seeds:** 3 seeds (42, 123, 456) for statistical validity

### Evaluation

**Primary Metrics:**
1. **Mean Paraphrase Similarity (MPS):** Mean cosine similarity between original and K=5 paraphrases
2. **Representation Variance (RV):** Variance of representations across paraphrases
3. **Similarity Differential:** MPS_paraphrase_model - MPS_verbatim_model

**Success Criteria (PoC):**
- Primary: Paraphrase-trained model MPS > verbatim-trained model MPS
- Secondary: Verbatim-trained shows lower MPS (representations tied to specific phrasing)
- Threshold: Difference > 0.05 in mean cosine similarity

**Expected Performance:**
- Verbatim model: MPS ≈ 0.85-0.90 (some generalization but surface-form dependent)
- Paraphrase model: MPS ≈ 0.92-0.97 (invariant to phrasing variations)
- Source: Multi-view learning literature suggests augmentation increases invariance

**Evaluation Protocol:**
1. Extract hidden representations for 1000 contaminated items + 5 paraphrases each
2. Compute cosine similarity for each item
3. Compare distributions between model conditions

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Representation analysis
- Library: torch, numpy, scipy
- Code:
```python
import torch.nn.functional as F
import numpy as np
from scipy import stats

# Compute cosine similarity
def cosine_sim(h1, h2):
    return F.cosine_similarity(h1, h2, dim=-1).item()

# Compare distributions
verbatim_sims = evaluator.evaluate_invariance(test_items, paraphrases, verbatim_model)
paraphrase_sims = evaluator.evaluate_invariance(test_items, paraphrases, paraphrase_model)

# Statistical test
t_stat, p_value = stats.ttest_ind(paraphrase_sims, verbatim_sims)
effect_size = (np.mean(paraphrase_sims) - np.mean(verbatim_sims)) / np.std(verbatim_sims)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Similarity Distribution:** Histogram/density plot comparing MPS distributions for verbatim vs paraphrase-trained models
- **Box Plot:** Side-by-side comparison of MPS by training condition

#### Additional Figures (LLM Autonomous)
- t-SNE/UMAP of representations colored by training condition
- Similarity heatmap for example items across paraphrases
- Learning curve of invariance during training

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: TRUE - Multi-view learning creates invariance (established theory)
- `mechanism_isolatable`: TRUE - Can compare same items across training conditions
- `baseline_measurable`: TRUE - Verbatim-trained model provides baseline

### Architecture Compatibility
- Mistral-7B hidden states accessible via `output_hidden_states=True`
- Last layer (layer 32) contains semantic encoding
- Mean pooling handles variable sequence length
- Cosine similarity robust in high-D (4096-dim)

### Activation Indicators
- `mechanism_log_message`: "Paraphrase augmentation training complete: {n} items × {k} paraphrases"
- `tensor_shape`: Representations [batch, 4096], similarity scalars
- `metric_delta_expected`: MPS_paraphrase - MPS_verbatim > 0.05

### Verification Code
```python
def verify_invariance_mechanism(verbatim_model, paraphrase_model, test_items, paraphrases):
    """Verify paraphrase training creates more invariant representations."""
    evaluator_v = RepresentationInvarianceEvaluator(verbatim_model, tokenizer)
    evaluator_p = RepresentationInvarianceEvaluator(paraphrase_model, tokenizer)
    
    # Compute MPS for both models
    mps_verbatim = evaluator_v.evaluate_invariance(test_items, paraphrases)
    mps_paraphrase = evaluator_p.evaluate_invariance(test_items, paraphrases)
    
    # Statistical comparison
    from scipy import stats
    t_stat, p_value = stats.ttest_ind(mps_paraphrase, mps_verbatim)
    effect_size = (np.mean(mps_paraphrase) - np.mean(mps_verbatim)) / np.std(mps_verbatim)
    
    mechanism_active = np.mean(mps_paraphrase) > np.mean(mps_verbatim)
    
    print(f"[MECHANISM CHECK] Verbatim MPS: {np.mean(mps_verbatim):.4f}")
    print(f"[MECHANISM CHECK] Paraphrase MPS: {np.mean(mps_paraphrase):.4f}")
    print(f"[MECHANISM CHECK] Difference: {np.mean(mps_paraphrase) - np.mean(mps_verbatim):.4f}")
    print(f"[MECHANISM CHECK] p-value: {p_value:.4e}, Active: {mechanism_active}")
    
    return {
        'mechanism_active': mechanism_active,
        'mps_verbatim': float(np.mean(mps_verbatim)),
        'mps_paraphrase': float(np.mean(mps_paraphrase)),
        'difference': float(np.mean(mps_paraphrase) - np.mean(mps_verbatim)),
        'effect_size': float(effect_size),
        'p_value': float(p_value)
    }
```

### Success Criteria
- `hypothesis_support_threshold`: MPS_paraphrase > MPS_verbatim AND difference > 0.03
- `hypothesis_support_metric`: mean_paraphrase_similarity

---

## 🔬 PoC Success Check

**Gate Result Determination:**
1. Code runs without error for both training conditions
2. Mean Paraphrase Similarity computed for 1000+ items
3. Paraphrase-trained MPS > Verbatim-trained MPS
4. Effect size > 0.3 (Cohen's d)

**If PASS:** Diverse training creates representation invariance → proceed to H-M3
**If FAIL:** EXPLORE - Alternative mechanisms (confidence calibration artifact, model capacity limit)

---

## Appendix: Reference Implementations

| Source | Description | Relevance |
|--------|-------------|-----------|
| sentence-transformers | Representation extraction | Hidden state pooling patterns |
| huggingface/transformers | Model API | `output_hidden_states` usage |
| Vamsi995/T5_Paraphrase_Paws | Paraphrase generation | T5-based paraphraser |
| Blum & Mitchell 1998 | Multi-view learning | Theoretical foundation |
| Data augmentation literature | Invariance through diversity | Mechanism justification |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- 2026-08-19T11:11: H-M2 set to IN_PROGRESS (external loop starting Phase 2C → 3 → 4)
- 2026-08-19: Phase 2C experiment design initiated
- Prerequisite H-M1 PASSED with effect size 15.1-31.1%

---

*MCP Tools: Archon/Exa unavailable - used literature-based design*
*All specifications grounded in representation learning theory*
*Next Phase: Phase 3 - Implementation Planning*
