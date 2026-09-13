# Experiment Design: H-E1

**Date:** 2026-08-10
**Author:** Anonymous
**Hypothesis Statement:** Under LMSYS-Chat-1M multi-turn conversations (≥2 turns per side), if we apply DeBERTa formality scoring, then formality accommodation patterns are measurable with coverage ≥50% and observed deltas < shuffled baseline.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (None required - foundation hypothesis)
**Gate Status:** MUST_WORK - Coverage ≥50%, Cohen's d > 0.3 (observed < shuffled)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
- **Pass:** Coverage ≥50% of conversations meet turn threshold AND Cohen's d > 0.3 (observed accommodation < shuffled baseline)
- **Fail Action:** PIVOT to alternative dataset (WildChat) or relax turn threshold

---

## Continuation Context

This is the foundation hypothesis - no previous hypothesis results available.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in dependency chain.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches for formality accommodation analysis. General text classification patterns available via HuggingFace Transformers documentation.

### Archon Code Examples

HuggingFace snapshot_download for dataset retrieval; Transformers pipeline for text classification tasks.

### Exa GitHub Implementations

**Key Resources Found:**

1. **LMSYS-Chat-1M Dataset** (https://huggingface.co/datasets/lmsys/lmsys-chat-1m)
   - 1M real conversations with 25 LLMs
   - Fields: `conversation_id`, `model`, `conversation` (list with role/content), `turn`, `language`
   - Avg. 2.0 turns per sample, 69.5 tokens per prompt, 214.5 tokens per response
   - Requires HuggingFace authentication

2. **s-nlp/deberta-large-formality-ranker** (https://huggingface.co/s-nlp/deberta-large-formality-ranker)
   - DeBERTa-large fine-tuned on GYAFC corpus for formality classification
   - 87.8% accuracy on formality detection
   - Binary classification: formal vs informal
   - Base model: microsoft/deberta-v3-large

3. **Dataset Exploration Example** (https://gist.github.com/reddgr/ea334a1a3296cb9c858bb9c96c4bc7b6)
   - Shows `load_dataset('lmsys/lmsys-chat-1m')` pattern
   - Demonstrates conversation structure extraction

### 🎯 Implementation Priority Assessment

**CRITICAL: Use established HuggingFace models and datasets**

**Recommended Implementation Path:**
- Primary: **DeBERTa formality ranker** via HuggingFace Transformers
- Fallback: s-nlp/mdeberta-base-formality-ranker (multilingual, smaller)
- Justification: DeBERTa-large has highest accuracy (87.8%) and is validated for formality classification

### Code Analysis (Serena MCP)

Not applicable - analysis task using pretrained model, no codebase integration required.

---

## Experiment Specification

### Dataset

**Primary Dataset: LMSYS-Chat-1M**
- **Name:** lmsys/lmsys-chat-1m
- **Type:** standard
- **Source:** HuggingFace (requires license agreement)
- **Statistics:** 1M conversations, 25 LLM models, multi-turn dialogues
- **Format:** JSON with `conversation_id`, `model`, `conversation` (list of role/content), `turn`, `language`

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `lmsys/lmsys-chat-1m`
- Code:
```python
from datasets import load_dataset

# LMSYS-Chat-1M (requires HF login + license acceptance)
dataset = load_dataset("lmsys/lmsys-chat-1m", split="train")
print(f"Total conversations: {len(dataset)}")
# Features: conversation_id, model, conversation, turn, language, openai_moderation, redacted
```

**Preprocessing:**
1. Filter to ≥2 turns per participant side (human ≥2, AI ≥2)
2. Language filter: English only (using `language` field)
3. Remove redacted entries (check `redacted` field)
4. Extract turn pairs for formality scoring

**Expected Coverage:** ~50% of 1M = ~500K conversations after filtering

### Models

#### Baseline Model

**Architecture:** Random Shuffled Pairing (null model)
**Type:** Statistical baseline
**Description:** Shuffle conversation turn pairings to destroy real accommodation signal

**Loading Information** (for Phase 4 download):
- Method: NumPy random permutation
- Identifier: N/A (statistical operation)
- Code:
```python
import numpy as np

def create_shuffled_baseline(formality_human, formality_ai):
    """Shuffle AI formality to destroy real pairing."""
    shuffled_ai = np.random.permutation(formality_ai)
    return formality_human, shuffled_ai
```

#### Proposed Model

**Architecture:** DeBERTa Formality Ranker + Accommodation Delta Computation

**Core Mechanism Implementation:**

```python
# Core Mechanism: Formality Accommodation Detection
# Based on: s-nlp/deberta-large-formality-ranker + Communication Accommodation Theory

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import numpy as np
from scipy import stats

class FormalityAccommodationAnalyzer:
    """
    Detect formality accommodation patterns in human-AI conversations.
    Accommodation = small |formality(AI_response) - formality(Human_prompt)|
    """
    def __init__(self, model_name='s-nlp/deberta-large-formality-ranker'):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()
    
    def score_formality(self, text: str) -> float:
        """Get formality score (0-1, higher = more formal)."""
        inputs = self.tokenizer(text, return_tensors="pt", 
                               truncation=True, max_length=512)
        with torch.no_grad():
            logits = self.model(**inputs).logits
            probs = torch.softmax(logits, dim=-1)
            # Assume index 1 = formal class
            return probs[0, 1].item()
    
    def compute_accommodation_delta(self, human_text: str, ai_text: str) -> float:
        """Compute formality delta (lower = more accommodation)."""
        h_formality = self.score_formality(human_text)
        ai_formality = self.score_formality(ai_text)
        return abs(ai_formality - h_formality)
    
    def analyze_conversation(self, conversation: list) -> dict:
        """
        Analyze full conversation for accommodation.
        Returns: dict with deltas for each turn pair.
        """
        human_turns = [t['content'] for t in conversation if t['role'] == 'user']
        ai_turns = [t['content'] for t in conversation if t['role'] == 'assistant']
        
        if len(human_turns) < 2 or len(ai_turns) < 2:
            return {'valid': False, 'reason': 'insufficient_turns'}
        
        deltas = []
        for h, a in zip(human_turns, ai_turns):
            deltas.append(self.compute_accommodation_delta(h, a))
        
        return {
            'valid': True,
            'deltas': deltas,
            'mean_delta': np.mean(deltas),
            'early_delta': deltas[0] if deltas else None  # Turn 1 accommodation
        }

# Verification: Compare observed deltas to shuffled baseline
def compute_cohens_d(observed_deltas, shuffled_deltas):
    """Effect size: observed should be SMALLER than shuffled if accommodation exists."""
    pooled_std = np.sqrt((np.var(observed_deltas) + np.var(shuffled_deltas)) / 2)
    d = (np.mean(shuffled_deltas) - np.mean(observed_deltas)) / pooled_std
    return d  # Positive d = observed < shuffled (accommodation detected)
```

### Training Protocol

**Not applicable for H-E1** - This is a statistical analysis hypothesis, not a training experiment.

**Analysis Protocol:**
- **Tool:** Python (transformers, scipy, numpy, pandas)
- **Seeds:** 1 (deterministic formality scoring)
- **Parallelization:** Batch processing with GPU acceleration

**Compute Requirements:**
- GPU recommended (DeBERTa-large inference)
- Estimated time: 4-8 hours for 500K conversations
- Memory: ~16GB GPU VRAM for batch processing

### Evaluation

**Primary Metrics:**
- Coverage: % of conversations meeting ≥2 turns per side threshold
- Cohen's d: Effect size comparing observed vs shuffled deltas
- Mean accommodation delta (observed)

**Success Criteria:**
- Coverage ≥ 50% (≥500K conversations from 1M)
- Cohen's d > 0.3 (observed deltas significantly smaller than shuffled)

**Expected Baseline Performance** (from theory):
- Shuffled baseline: Mean delta ~ 0.5 (random pairing)
- If accommodation exists: Mean delta < 0.4, Cohen's d > 0.3

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical comparison
- Library: scipy.stats, numpy
- Code:
```python
from scipy import stats
import numpy as np

def evaluate_accommodation(observed_deltas, shuffled_deltas):
    """Evaluate H-E1 gate condition."""
    # Cohen's d (positive = observed < shuffled)
    d = compute_cohens_d(observed_deltas, shuffled_deltas)
    
    # Welch's t-test for significance
    t_stat, p_value = stats.ttest_ind(shuffled_deltas, observed_deltas, equal_var=False)
    
    return {
        'cohens_d': d,
        'p_value': p_value,
        'mean_observed': np.mean(observed_deltas),
        'mean_shuffled': np.mean(shuffled_deltas),
        'gate_pass': d > 0.3 and p_value < 0.001
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Coverage target (50%) vs actual coverage; Cohen's d target (0.3) vs actual

#### Additional Figures (LLM Autonomous)
- Delta distribution histogram: Observed vs Shuffled overlay
- Formality score distributions (human vs AI)
- Delta by model type (25 models in LMSYS)
- Early accommodation (turn 1) vs later turns

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** True - DeBERTa formality scoring is established (87.8% accuracy)
- **mechanism_isolatable:** True - Accommodation delta is directly computable
- **baseline_measurable:** True - Shuffled baseline provides null comparison

### Architecture Compatibility
- DeBERTa model must load successfully from HuggingFace
- Formality scores must produce non-trivial variance (not all 0 or 1)
- Dataset must contain multi-turn conversations with role labels

### Activation Indicators
- **mechanism_log_message:** "Formality scores computed for {n} conversations"
- **tensor_shape_change:** N/A (no tensors, statistical analysis)
- **metric_delta_expected:** Cohen's d > 0.3

### Mechanism Verification Code
```python
def verify_mechanism(analyzer, sample_conversations):
    """Verify formality scoring produces meaningful results."""
    deltas = []
    for conv in sample_conversations[:100]:
        result = analyzer.analyze_conversation(conv['conversation'])
        if result['valid']:
            deltas.extend(result['deltas'])
    
    assert len(deltas) > 50, f"Too few valid deltas: {len(deltas)}"
    assert np.std(deltas) > 0.05, f"No variance in deltas: SD={np.std(deltas)}"
    assert 0 < np.mean(deltas) < 1, f"Deltas out of range: mean={np.mean(deltas)}"
    
    print(f"[VERIFY] Formality scoring works: n={len(deltas)}, mean={np.mean(deltas):.3f}, SD={np.std(deltas):.3f}")
    return True
```

### Success Criteria
- **hypothesis_support_threshold:** Cohen's d > 0.3
- **hypothesis_support_metric:** Effect size (observed < shuffled)

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Coverage ≥ 50% (≥500K conversations)
3. Cohen's d > 0.3 (accommodation exists)

---

## Appendix: Reference Implementations

### Model Sources
1. **s-nlp/deberta-large-formality-ranker** - https://huggingface.co/s-nlp/deberta-large-formality-ranker
   - DeBERTa-large fine-tuned on GYAFC
   - 87.8% accuracy
   - Binary formality classification

2. **s-nlp/mdeberta-base-formality-ranker** - https://huggingface.co/s-nlp/mdeberta-base-formality-ranker
   - Multilingual variant (fallback)
   - Smaller model, faster inference

### Dataset Sources
1. **LMSYS-Chat-1M** - https://huggingface.co/datasets/lmsys/lmsys-chat-1m
   - 1M real conversations with 25 LLMs
   - Multi-turn with role labels

### Related Papers
- Communication Accommodation Theory (Giles, 1973)
- "Detecting Text Formality: A Study of Text Classification Approaches" (s-nlp)
- Niederhoffer & Pennebaker (2002) - Linguistic style matching (r ~ 0.3)
- Chen et al. (2026) - Bidirectional accommodation in human-AI

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10

### Workflow History for This Hypothesis
- 2026-08-10: H-E1 set to IN_PROGRESS (Hypothesis Loop)
- 2026-08-10: Phase 2C Experiment Design completed

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
