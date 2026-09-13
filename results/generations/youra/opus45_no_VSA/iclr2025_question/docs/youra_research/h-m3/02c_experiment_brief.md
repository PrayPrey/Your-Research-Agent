# Experiment Design: h-m3

**Date:** 2026-08-09
**Author:** Anonymous
**Hypothesis Statement:** RCI flip pattern appears in >= 30% hallucinations and < 10% correct responses
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Template** - Tests specific pattern prevalence in hallucination vs correct responses.

---

## Workflow Status

**Verification State:** IN_PROGRESS → COMPLETED
**Prerequisites Satisfied:** h-e1 (VALIDATED, AUROC 0.5657)
**Gate Status:** SHOULD_WORK (failure = log limitation, not stop)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (satisfied)

### Gate Condition
**SHOULD_WORK Gate:** RCI flip pattern is a secondary mechanism validation.
- Success: >= 30% hallucinations show flip, < 10% correct show flip
- Falsification: < 20% hallucinations OR >= 15% correct

---

## Continuation Context

### Previous Hypothesis Results (h-e1)
- **NTI AUROC:** 0.5657 (> 0.55 threshold)
- **Dataset:** TruthfulQA MC1 (817 samples, verified)
- **Model:** LLaMA-2-7B (meta-llama/Llama-2-7b-hf)
- **Layers analyzed:** 24-32
- **Logit-lens working:** Confirmed in h-e1 validation

**Reuse from h-e1:**
- Same dataset, model, layer range
- Same hidden state extraction pipeline
- Same logit-lens projection method

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1:** "RCI representational competition hallucination detection"
- No direct matches for RCI terminology
- Related: trajectory instability concepts in diffusion/consistency models
- Insight: RCI is novel metric from Phase 2A, requires custom implementation

**Query 2:** "hidden state trajectory instability LLM layers"
- Found: arxiv.org/abs/2402.19159 - trajectory instability in LLMs
- Insight: Hidden state dynamics correlate with model uncertainty

**Query 3:** "logit lens hidden states transformer"
- Found: T5EncoderModel hidden state extraction pattern
- Code: `outputs.last_hidden_state` for accessing hidden states

### Archon Code Examples

**Pattern:** Hidden state extraction from transformers
```python
outputs = model(input_ids=input_ids)
last_hidden_states = outputs.last_hidden_state
```

### Exa GitHub Implementations

**Repository 1:** AlignmentResearch/tuned-lens (⭐ 601)
- **URL:** https://github.com/AlignmentResearch/tuned-lens
- **Relevance:** Layer-by-layer prediction trajectory analysis
- **Key Concept:** Prediction trajectory = `(num_layers x sequence_length x vocab_size)`
- **Architecture:** Affine translators per layer for intermediate prediction
- **Used For:** Understanding logit-lens/tuned-lens for RCI computation

**Repository 2:** 78Spinoza/LLMDeHallucinator (⭐ 0)
- **URL:** https://github.com/78Spinoza/LLMDeHallucinator
- **Relevance:** Hallucination-associated neuron detection
- **Tools:** TransformerLens, sparse probing
- **Used For:** Reference for hallucination detection via internal states

**Repository 3:** INSIDE Paper (arxiv.org/html/2402.03744)
- **Title:** LLMs' Internal States Retain the Power of Hallucination Detection
- **Key Method:** EigenScore metric using covariance matrix of internal states
- **Relevance:** Internal state analysis for hallucination detection
- **Used For:** Validation approach inspiration

### 🎯 Implementation Priority Assessment

**CRITICAL: RCI flip pattern is a NOVEL metric defined in Phase 2A Dialogue.**

- No official author implementation exists
- RCI = Representational Competition Index (custom definition)
- Flip pattern = Top-1 token changes between consecutive layers

**Recommended Implementation Path:**
- Primary: Custom implementation based on tuned-lens trajectory extraction
- Fallback: logit-lens direct projection (simpler, from h-e1)
- Justification: RCI requires layer-by-layer top-k token tracking, tuned-lens provides this

### Code Analysis (Serena MCP)

*Skipped* - tuned-lens codebase is well-documented. Key patterns extracted from Exa search.

---

## Experiment Specification

### Dataset

**Name:** TruthfulQA MC1
**Type:** standard
**Source:** HuggingFace datasets (truthful_qa)
**Size:** 817 questions
**Labels:** Binary correctness (correct=1 for selected answer, incorrect=0)
**Splits:** Single evaluation set (no train/val/test split needed - metric analysis only)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `truthful_qa` with `multiple_choice` config
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("truthful_qa", "multiple_choice", split="validation")
# MC1 targets: dataset[i]["mc1_targets"]
```

### Models

#### Baseline Model

**Architecture:** LLaMA-2-7B
**Source:** meta-llama/Llama-2-7b-hf (HuggingFace)
**Layers:** 32 total, analysis on layers 24-32 (9 layers)
**Hidden dim:** 4096

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `meta-llama/Llama-2-7b-hf`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    torch_dtype=torch.float16,
    device_map="auto",
    output_hidden_states=True  # Required for trajectory extraction
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
```

#### Proposed Model

**Architecture:** Baseline + RCI Flip Pattern Detection
**Integration Point:** Post-inference analysis (no model modification)

**Core Mechanism Implementation:**

```python
# Core Mechanism: RCI Flip Pattern Detection
# Based on: tuned-lens trajectory concept + custom RCI definition

class RCIFlipDetector:
    """
    Detects representational competition via top-token flips across layers.
    RCI Flip = top-1 predicted token changes between layer L and L+1.
    """
    def __init__(self, model, tokenizer, layer_range=(24, 32)):
        self.model = model
        self.tokenizer = tokenizer
        self.layer_start, self.layer_end = layer_range
        self.unembedding = model.lm_head.weight  # (vocab, hidden_dim)
    
    def extract_layer_predictions(self, hidden_states, position=-1):
        """
        Project each layer's hidden state to vocabulary space.
        Returns: (num_layers, vocab_size) logits
        """
        # hidden_states: tuple of (batch, seq, hidden_dim) per layer
        layer_logits = []
        for layer_idx in range(self.layer_start, self.layer_end + 1):
            h = hidden_states[layer_idx][:, position, :]  # (batch, hidden_dim)
            logits = h @ self.unembedding.T  # (batch, vocab_size)
            layer_logits.append(logits)
        return torch.stack(layer_logits)  # (num_layers, batch, vocab_size)
    
    def detect_flip_pattern(self, layer_logits):
        """
        Detect if top-1 token changes between consecutive layers.
        Returns: (num_flips, flip_positions)
        """
        top_tokens = layer_logits.argmax(dim=-1)  # (num_layers, batch)
        flips = (top_tokens[:-1] != top_tokens[1:]).sum(dim=0)  # (batch,)
        flip_positions = torch.where(top_tokens[:-1] != top_tokens[1:])
        return flips, flip_positions
    
    def compute_rci_flip_rate(self, dataset):
        """
        Compute flip rate for hallucinated vs correct responses.
        """
        hallucination_flips = []
        correct_flips = []
        
        for sample in dataset:
            hidden_states = self.model(**sample.input, output_hidden_states=True).hidden_states
            layer_logits = self.extract_layer_predictions(hidden_states)
            num_flips, _ = self.detect_flip_pattern(layer_logits)
            
            has_flip = num_flips > 0
            if sample.is_hallucination:
                hallucination_flips.append(has_flip)
            else:
                correct_flips.append(has_flip)
        
        return {
            "hallucination_flip_rate": sum(hallucination_flips) / len(hallucination_flips),
            "correct_flip_rate": sum(correct_flips) / len(correct_flips)
        }
```

### Training Protocol

**No training required** - This is a metric analysis experiment, not model training.

**Inference Protocol:**
- Temperature: 0 (greedy decoding)
- Batch size: 1 (for hidden state extraction)
- Sequence aggregation: Last token position (answer token)
- Layer range: 24-32 (9 layers from h-e1)

**Seeds:** 1 (fixed seed=42 for reproducibility)

**Computational Requirements:**
- GPU: Single A100 (40GB) or equivalent
- Time estimate: ~30 minutes for 817 samples

### Evaluation

**Primary Metrics:**
1. **Hallucination Flip Rate:** % of hallucinated responses with RCI flip pattern
2. **Correct Flip Rate:** % of correct responses with RCI flip pattern
3. **Separation:** Hallucination rate - Correct rate

**Success Criteria:**
- Hallucination flip rate >= 30%
- Correct flip rate < 10%
- Separation >= 20 percentage points

**Falsification Boundary:**
- Hallucination flip rate < 20% OR
- Correct flip rate >= 15%

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification analysis
- Library: Custom computation (no external metrics library needed)
- Code:
```python
def compute_rates(results):
    halluc_flips = [r["has_flip"] for r in results if r["is_hallucination"]]
    correct_flips = [r["has_flip"] for r in results if not r["is_hallucination"]]
    return {
        "hallucination_flip_rate": sum(halluc_flips) / len(halluc_flips),
        "correct_flip_rate": sum(correct_flips) / len(correct_flips)
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing hallucination flip rate vs correct flip rate with 30% and 10% threshold lines

#### Additional Figures (LLM Autonomous)
- **Flip Position Heatmap**: Layer index vs sample index showing where flips occur
- **Token Transition Analysis**: Sankey diagram of top-token transitions across layers
- **Confidence Distribution**: Box plot of logit confidence at flip vs non-flip layers

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
| Condition | Check | Status |
|-----------|-------|--------|
| mechanism_exists | RCI flip detection computes binary flip per sample | Required |
| mechanism_isolatable | Flip pattern measured independently from NTI | Required |
| baseline_measurable | Logit-lens projection works (from h-e1) | Verified |

### Architecture Compatibility
- Model outputs hidden_states: ✓ (output_hidden_states=True)
- Unembedding matrix accessible: ✓ (model.lm_head.weight)
- Layer indexing correct: ✓ (layers 24-32 = indices 24:33)

### Activation Indicators
| Indicator | Expected Value | Failure Detection |
|-----------|----------------|-------------------|
| mechanism_log_message | "RCI flip detected at layer {L}" | No flips in 100+ samples |
| tensor_shape_change | layer_logits shape = (9, batch, vocab) | Shape mismatch error |
| metric_delta_expected | halluc_rate - correct_rate >= 0.20 | Separation < 0.05 |

### Verification Code
```python
def verify_mechanism(detector, test_sample):
    """Verify RCI flip detection mechanism works correctly."""
    hidden_states = detector.model(**test_sample, output_hidden_states=True).hidden_states
    
    # Check 1: Hidden states available for all layers
    assert len(hidden_states) >= 33, f"Expected 33+ layers, got {len(hidden_states)}"
    
    # Check 2: Layer logits extraction works
    layer_logits = detector.extract_layer_predictions(hidden_states)
    assert layer_logits.shape[0] == 9, f"Expected 9 layers, got {layer_logits.shape[0]}"
    
    # Check 3: Flip detection returns valid output
    num_flips, flip_positions = detector.detect_flip_pattern(layer_logits)
    assert num_flips >= 0, "Flip count must be non-negative"
    
    print("✓ Mechanism verification passed")
    return True
```

### Hypothesis Support Threshold
- **hypothesis_support_metric:** separation = hallucination_flip_rate - correct_flip_rate
- **hypothesis_support_threshold:** separation >= 0.20 (20 percentage points)

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Mechanism verification passes
3. `hallucination_flip_rate > correct_flip_rate` (effect direction)

**Full Success Condition:**
1. hallucination_flip_rate >= 0.30
2. correct_flip_rate < 0.10

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1:** Hidden State Trajectory Instability
- **Type:** Knowledge base article
- **Query Used:** "hidden state trajectory instability LLM layers"
- **URL:** arxiv.org/abs/2402.19159
- **Key Insight:** Layer-wise hidden state dynamics correlate with model uncertainty
- **Used For:** Conceptual grounding for RCI flip pattern

### B. GitHub Implementations (Exa)

**Repository 1:** AlignmentResearch/tuned-lens (⭐ 601)
- **URL:** https://github.com/AlignmentResearch/tuned-lens
- **Query Used:** "logit lens tuned lens LLM hidden states trajectory GitHub implementation"
- **Relevance:** Layer-by-layer prediction trajectory analysis framework
- **Key Code:**
```python
# Prediction trajectory concept
# Shape: (num_layers x sequence_length x vocab_size)
# Each layer produces a distribution over vocabulary
```
- **Used For:** Trajectory extraction concept for RCI flip detection

**Repository 2:** INSIDE Paper Implementation Concept
- **URL:** https://arxiv.org/html/2402.03744
- **Title:** LLMs' Internal States Retain the Power of Hallucination Detection
- **Key Method:** EigenScore using covariance of internal states
- **Used For:** Validation that internal states contain hallucination signal

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed - tuned-lens documentation sufficient for trajectory concept.

### D. Previous Hypothesis Context

**Source:** h-e1 Validation (PASSED)
- **Reused Components:**
  - Dataset: TruthfulQA MC1 (cache verified)
  - Model: LLaMA-2-7B (cache verified)
  - Layer range: 24-32
  - Logit-lens projection: Working (AUROC 0.5657 achieved)
- **Why Reused:** Same analysis pipeline, RCI extends NTI trajectory analysis

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Previous (h-e1) | 02b_verification_plan.md |
| Model selection | Previous (h-e1) | 02b_verification_plan.md |
| Layer range | Previous (h-e1) | Validated in h-e1 |
| RCI concept | Phase 2A | Main hypothesis definition |
| Flip detection | GitHub | tuned-lens trajectory concept |
| Hidden state extraction | Archon KB | T5 hidden_states pattern |
| Hallucination detection | GitHub | INSIDE paper concept |
| Evaluation metrics | Phase 2B | Success criteria from roadmap |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE - restate in ```state block)
**Date:** 2026-08-09

### Workflow History for This Hypothesis
- 2026-08-09: Phase 2C experiment design initiated
- 2026-08-09: MCP research completed (Archon + Exa)
- 2026-08-09: Experiment specification synthesized
- 2026-08-09: Phase 2C COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
