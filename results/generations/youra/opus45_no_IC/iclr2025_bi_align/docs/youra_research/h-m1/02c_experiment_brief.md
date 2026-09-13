# Experiment Design: H-M1

**Date:** 2026-08-10
**Author:** Anonymous
**Hypothesis Statement:** Under LMSYS-Chat-1M conversations, if a human sends an initial message, then DeBERTa assigns a formality score with non-trivial variance (SD > 0.1).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Template** - Testing formality variance in human initial messages

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 COMPLETED - BCS SD=0.569, n=26,395)
**Gate Status:** MUST_WORK - SD(formality_human_1) > 0.1

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED)

### Gate Condition
- **Pass:** SD(formality_human_1) > 0.1
- **Fail Action:** EXPLORE alternative formality measures or categorical binning

---

## Continuation Context

Building on H-E1 foundation: DeBERTa formality scoring validated on Anthropic/hh-rlhf dataset. H-M1 tests whether human initial messages in LMSYS-Chat-1M show sufficient formality variance for meaningful analysis.

### Previous Hypothesis Results
**H-E1 Validation (2026-08-10):**
- Dataset: Anthropic/hh-rlhf (HuggingFace)
- Sample size: 26,395 conversations (4+ turns filter)
- BCS statistics: mean=0.054, SD=0.569, range=[-1.0, +1.0]
- Gate: PASS (SD > 0.15, n > 10,000)

**Key Artifacts to Reuse:**
- DeBERTa formality scoring pipeline
- s-nlp/deberta-large-formality-ranker model (87.8% accuracy on GYAFC)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches for formality variance analysis. DeBERTa architecture documentation available from HuggingFace transformers.

### Archon Code Examples

No directly relevant code examples for formality scoring variance analysis.

### Exa GitHub Implementations

**Highly Relevant Research:**

1. **s-nlp/formality** (https://github.com/s-nlp/formality)
   - Official implementation for "Detecting Text Formality" paper
   - DeBERTa-large-formality-ranker: 87.8% accuracy on GYAFC
   - Models: s-nlp/deberta-large-formality-ranker, s-nlp/mdeberta-base-formality-ranker
   - Training data: GYAFC corpus (formal/informal sentence pairs)

2. **LMSYS-Chat-1M Dataset** (https://huggingface.co/datasets/lmsys/lmsys-chat-1m)
   - 1M real-world conversations with 25 LLMs
   - 210K unique IP addresses
   - Multi-turn dialogues with human/assistant alternation
   - Requires license agreement for access

3. **Mind the Gap (Zhang & Yu 2025)** - arXiv:2510.02645
   - Studies linguistic divergence in human-LLM interactions
   - Analyzes grammatical fluency, politeness, lexical diversity
   - Finding: Users adopt distinct communication styles with chatbots vs humans
   - Directly relevant to formality variance analysis

**DeBERTa Formality Scoring Code:**
```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

model_name = 's-nlp/deberta-large-formality-ranker'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

def score_formality(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    # Softmax to get probability
    probs = torch.softmax(outputs.logits, dim=-1)
    # Index 1 = formal, Index 0 = informal
    formality_score = probs[0, 1].item()
    return formality_score
```

### Implementation Priority Assessment

**CRITICAL: Use s-nlp official DeBERTa formality ranker**

**Recommended Implementation Path:**
- Primary: s-nlp/deberta-large-formality-ranker via HuggingFace transformers
- Fallback: s-nlp/roberta-base-formality-ranker (smaller, faster)
- Justification: Official implementation with 87.8% accuracy, well-documented

### Code Analysis (Serena MCP)

Not required - using pretrained model from HuggingFace, no local codebase integration.

---

## Experiment Specification

### Dataset

**Dataset: LMSYS-Chat-1M**
- **Name:** lmsys/lmsys-chat-1m
- **Type:** standard
- **Source:** HuggingFace (requires license agreement)
- **Statistics:** 1M conversations, 25 LLMs, 210K unique IPs
- **Format:** Parquet with conversation_id, model, conversation (list of turns), turn, language, openai_moderation, redacted

**Filtering Criteria:**
- Language: English only (language == "English")
- Turns: >= 2 (at least one human + one AI turn)
- Content: Non-redacted human messages

**Sample Size Target:** Full dataset (~1M conversations) or minimum 100,000 for statistical power

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets with authentication
- Identifier: `lmsys/lmsys-chat-1m`
- Code:
```python
from datasets import load_dataset

# Requires HuggingFace login with accepted license
dataset = load_dataset("lmsys/lmsys-chat-1m", split="train")

# Filter for English conversations with 2+ turns
def filter_valid(example):
    return (
        example['language'] == 'English' and
        len(example['conversation']) >= 2 and
        not example.get('redacted', False)
    )

filtered = dataset.filter(filter_valid)
print(f"Filtered dataset size: {len(filtered)}")
```

**Preprocessing:**
1. Extract first human message from each conversation
2. Clean text (remove special tokens, normalize whitespace)
3. Filter empty/very short messages (< 5 characters)
4. Batch for DeBERTa inference

### Models

#### Baseline Model

**Architecture:** Null Hypothesis (Random/Uniform Distribution)
- Expected: If formality is random, SD would be very low (~0.05)
- Comparison: SD of uniform distribution on [0, 1] = 0.289

**Purpose:** Establish that observed variance exceeds chance level.

**Loading Information:**
- Method: NumPy simulation
- Code:
```python
import numpy as np

# Theoretical SD for uniform distribution [0, 1]
uniform_sd = np.std(np.random.uniform(0, 1, 100000))
print(f"Uniform distribution SD: {uniform_sd:.3f}")  # ~0.289
```

#### Proposed Model

**Architecture:** DeBERTa-large Formality Ranker

**Core Mechanism Implementation:**

```python
# Core Mechanism: Human Initial Message Formality Variance Analysis
# Theory: If humans vary their formality, DeBERTa should capture this variance

import torch
import numpy as np
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from tqdm import tqdm
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FormalityVarianceAnalyzer:
    """
    Analyze formality variance in human initial messages.
    Gate: SD(formality_human_1) > 0.1
    """
    
    def __init__(self, model_name: str = 's-nlp/deberta-large-formality-ranker'):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        logger.info(f"Model loaded on {self.device}")
    
    def score_formality_batch(self, texts: List[str], batch_size: int = 32) -> List[float]:
        """Score formality for a batch of texts."""
        scores = []
        
        for i in tqdm(range(0, len(texts), batch_size), desc="Scoring formality"):
            batch = texts[i:i + batch_size]
            inputs = self.tokenizer(
                batch, 
                return_tensors="pt", 
                truncation=True, 
                max_length=512, 
                padding=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            probs = torch.softmax(outputs.logits, dim=-1)
            # Index 1 = formal probability
            batch_scores = probs[:, 1].cpu().numpy().tolist()
            scores.extend(batch_scores)
        
        return scores
    
    def extract_human_first_messages(self, conversations: List[Dict]) -> List[str]:
        """Extract first human message from each conversation."""
        first_messages = []
        
        for conv in conversations:
            turns = conv.get('conversation', [])
            for turn in turns:
                if turn.get('role') == 'user':
                    content = turn.get('content', '').strip()
                    if len(content) >= 5:  # Filter very short messages
                        first_messages.append(content)
                    break
        
        return first_messages
    
    def analyze_variance(self, scores: List[float]) -> Dict:
        """Compute variance statistics and gate check."""
        arr = np.array(scores)
        
        results = {
            'n': len(arr),
            'mean': float(np.mean(arr)),
            'sd': float(np.std(arr)),
            'median': float(np.median(arr)),
            'min': float(np.min(arr)),
            'max': float(np.max(arr)),
            'q25': float(np.percentile(arr, 25)),
            'q75': float(np.percentile(arr, 75)),
            'iqr': float(np.percentile(arr, 75) - np.percentile(arr, 25)),
        }
        
        # Gate check
        results['gate_threshold'] = 0.1
        results['gate_pass'] = results['sd'] > 0.1
        
        return results

# Usage:
# analyzer = FormalityVarianceAnalyzer()
# messages = analyzer.extract_human_first_messages(conversations)
# scores = analyzer.score_formality_batch(messages)
# results = analyzer.analyze_variance(scores)
# print(f"SD = {results['sd']:.3f}, Gate: {'PASS' if results['gate_pass'] else 'FAIL'}")
```

### Training Protocol

**Not applicable** - Statistical analysis hypothesis, not training experiment.

**Analysis Protocol:**
- **Tool:** Python (transformers, numpy, scipy)
- **Hardware:** GPU recommended for DeBERTa inference (CUDA)
- **Batch size:** 32 (adjustable based on GPU memory)

**Compute Requirements:**
- GPU: 1x with 16GB VRAM (or CPU with longer runtime)
- Estimated time: 2-4 hours for 100K messages (GPU), 24+ hours (CPU)
- Memory: ~8GB RAM + GPU memory

### Evaluation

**Primary Metrics:**
- SD(formality_human_1): Standard deviation of formality scores
- Distribution statistics: mean, median, IQR, range

**Success Criteria (Gate):**
- SD > 0.1 (non-trivial variance threshold)
- N >= 10,000 (statistical power)

**Secondary Criteria:**
- Distribution not heavily skewed (|skewness| < 2)
- Full range utilization (scores span [0, 0.2] to [0.8, 1.0])

**Metrics Loading Information:**
- Task Type: Statistical variance analysis
- Library: numpy, scipy.stats
- Code:
```python
import numpy as np
from scipy import stats

def evaluate_formality_variance(scores):
    arr = np.array(scores)
    
    results = {
        'n': len(arr),
        'mean': np.mean(arr),
        'sd': np.std(arr),
        'skewness': stats.skew(arr),
        'kurtosis': stats.kurtosis(arr),
        'range': (np.min(arr), np.max(arr)),
    }
    
    # Gate evaluation
    results['gate_pass'] = results['sd'] > 0.1
    results['gate_margin'] = results['sd'] - 0.1
    
    return results
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Formality Score Distribution**: Histogram of human_1 formality scores with SD annotation
- **Gate Threshold Visualization**: SD vs threshold (0.1) comparison bar

#### Additional Figures (LLM Autonomous)
- Box plot of formality scores by message length bins
- Density plot with kernel density estimation
- Percentile distribution curve
- Formality vs message character count scatter (sample)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Successfully processes >= 10,000 human messages
3. SD(formality_human_1) > 0.1

**Expected Outcome:**
Based on H-E1 results (BCS SD=0.569 on Anthropic/hh-rlhf), expect formality variance to exceed threshold. LMSYS-Chat-1M has diverse user base (210K IPs) suggesting high formality variance.

---

## Ablation Studies

Not applicable for variance check hypothesis. If gate fails:
1. Test with alternative model (roberta-base-formality-ranker)
2. Test categorical binning (formal/neutral/informal)
3. Analyze by conversation length or model type

---

## Appendix: Reference Implementations

### Formality Detection Models
1. **s-nlp/deberta-large-formality-ranker** - https://huggingface.co/s-nlp/deberta-large-formality-ranker
   - 87.8% accuracy on GYAFC
   - Fine-tuned DeBERTa-large
   - Binary classification (formal/informal)

2. **s-nlp/roberta-base-formality-ranker** - https://huggingface.co/s-nlp/roberta-base-formality-ranker
   - Smaller, faster alternative
   - RoBERTa-base backbone

### Related Research
3. **Mind the Gap (Zhang & Yu 2025)** - arXiv:2510.02645
   - Linguistic divergence in human-LLM interactions
   - Communication style differences with chatbots vs humans

4. **LMSYS-Chat-1M Paper** (Zheng et al. 2023) - arXiv:2309.11998
   - Dataset documentation and statistics
   - Topic distribution, content analysis

### Theoretical Background
5. Communication Accommodation Theory (Giles et al.)
6. BiCA: Bidirectional Communication Adaptation (Li & Song 2025)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10

### Workflow History for This Hypothesis
- 2026-08-10: H-M1 set to IN_PROGRESS (Phase 2C start)
- 2026-08-10: Experiment design completed (Phase 2C)
- Prerequisite H-E1: COMPLETED (BCS SD=0.569, n=26,395)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
