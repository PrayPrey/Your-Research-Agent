# Experiment Design: H-M2

**Date:** 2026-08-10
**Author:** Anonymous
**Hypothesis Statement:** Under multi-turn conversations, if an AI responds to a human message, then AI formality varies as a function of human formality (correlation |r| > 0.1).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Template** - Testing AI formality response correlation with human formality

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 COMPLETED, H-M1 COMPLETED)
**Gate Status:** SHOULD_WORK - |r(formality_human_1, formality_AI_1)| > 0.1, p < 0.001

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (COMPLETED - lag-1 r=0.0134, p=0.00113)

### Gate Condition
- **Pass:** |r(formality_human_1, formality_AI_1)| > 0.1, p < 0.001
- **Fail Action:** EXPLORE per-model analysis (some models may not accommodate)

---

## Continuation Context

Building on H-M1 foundation: User adaptation to AI patterns validated (lag-1 r=0.0134, p=0.00113, n=26,405). H-M2 tests the reverse direction: whether AI formality varies as a function of human formality in the immediate response.

### Previous Hypothesis Results

**H-E1 Validation (2026-08-10):**
- Dataset: Anthropic/hh-rlhf (HuggingFace)
- Sample size: 26,395 conversations
- BCS statistics: SD=0.569, range=[-1.0, +1.0]
- Gate: PASS (SD > 0.15, n > 10,000)

**H-M1 Validation (2026-08-10):**
- Dataset: Anthropic/hh-rlhf (lagged cross-correlation)
- Sample size: 26,405 conversations
- Lag-1 r=0.0134, p=0.00113, Cohen's d=0.020
- Baseline null p=0.4221 (no spurious signal)
- Gate: PASS (statistically significant user adaptation)

**Key Artifacts to Reuse:**
- DeBERTa formality scoring pipeline from H-M1
- s-nlp/deberta-large-formality-ranker model
- Conversation extraction logic

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches for AI-human formality correlation analysis. OpenAI instruction-following research available but focuses on task completion rather than linguistic accommodation.

### Archon Code Examples

No directly relevant code examples. CUDA/cuBLAS documentation for GPU acceleration available if needed for large-scale inference.

### Exa GitHub Implementations

**Highly Relevant Research:**

1. **s-nlp/formality** (https://github.com/s-nlp/formality)
   - Official implementation for "Detecting Text Formality" paper (RANLP 2023)
   - DeBERTa-large-formality-ranker: 87.8% accuracy on GYAFC
   - Models: s-nlp/deberta-large-formality-ranker, s-nlp/mdeberta-base-formality-ranker
   - Citation: Dementieva et al. 2023

2. **s-nlp/deberta-large-formality-ranker** (https://huggingface.co/s-nlp/deberta-large-formality-ranker)
   - Pretrained model card with usage examples
   - Binary classification: formal (index 1) vs informal (index 0)
   - Evaluation: 87.8% acc, 89.0 F1-formal, 86.1 F1-informal

3. **LMSYS-Chat-1M Dataset** (https://huggingface.co/datasets/lmsys/lmsys-chat-1m)
   - 1M real-world conversations with 25 LLMs
   - Multi-turn dialogues with human/assistant alternation
   - Per-conversation model identification for per-model analysis

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
    probs = torch.softmax(outputs.logits, dim=-1)
    formality_score = probs[0, 1].item()  # Index 1 = formal
    return formality_score
```

### Implementation Priority Assessment

**CRITICAL: Reuse H-M1 DeBERTa pipeline, extend to paired analysis**

**Recommended Implementation Path:**
- Primary: s-nlp/deberta-large-formality-ranker (same as H-M1)
- Fallback: s-nlp/roberta-base-formality-ranker (faster if memory constrained)
- Justification: Consistency with H-M1, validated 87.8% accuracy

### Code Analysis (Serena MCP)

Not required - using pretrained model from HuggingFace, no local codebase integration needed.

---

## Experiment Specification

### Dataset

**Dataset: Anthropic/hh-rlhf** (consistent with H-E1 and H-M1)
- **Name:** Anthropic/hh-rlhf
- **Type:** standard
- **Source:** HuggingFace
- **Statistics:** 160K+ conversations, validated n=26,405 after filtering
- **Format:** Parquet with chosen/rejected columns containing conversation text

**Why Anthropic/hh-rlhf over LMSYS-Chat-1M:**
- Consistent with prior hypotheses (H-E1, H-M1)
- Already validated formality variance
- No license agreement required

**Filtering Criteria:**
- Turns: >= 4 (at least 2 human + 2 AI turns for correlation)
- Content: Non-empty human and AI messages
- Consistency with H-M1 filtering

**Sample Size Target:** Full filtered dataset (~26,000+ conversations)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `Anthropic/hh-rlhf`
- Code:
```python
from datasets import load_dataset

dataset = load_dataset("Anthropic/hh-rlhf", split="train")

def parse_conversation(text):
    """Parse Human:/Assistant: format into turn list."""
    turns = []
    current_role = None
    current_content = []
    
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('Human:'):
            if current_role:
                turns.append({'role': current_role, 'content': ' '.join(current_content)})
            current_role = 'human'
            current_content = [line[6:].strip()]
        elif line.startswith('Assistant:'):
            if current_role:
                turns.append({'role': current_role, 'content': ' '.join(current_content)})
            current_role = 'assistant'
            current_content = [line[10:].strip()]
        elif current_role:
            current_content.append(line)
    
    if current_role:
        turns.append({'role': current_role, 'content': ' '.join(current_content)})
    
    return turns

# Filter for 4+ turn conversations
def filter_valid(example):
    turns = parse_conversation(example['chosen'])
    return len(turns) >= 4

filtered = dataset.filter(filter_valid)
```

### Models

#### Baseline Model

**Architecture:** Null Hypothesis (No Correlation)
- Expected: If AI formality is independent of human formality, r ≈ 0
- Comparison: Random pairing would yield r near 0 with high p-value

**Purpose:** Establish that observed correlation exceeds chance level.

**Loading Information:**
- Method: Shuffled control analysis
- Code:
```python
import numpy as np
from scipy import stats

def baseline_correlation(human_scores, ai_scores, n_permutations=1000):
    """Compute null distribution via permutation test."""
    observed_r = stats.pearsonr(human_scores, ai_scores)[0]
    
    null_rs = []
    for _ in range(n_permutations):
        shuffled_ai = np.random.permutation(ai_scores)
        null_r = stats.pearsonr(human_scores, shuffled_ai)[0]
        null_rs.append(null_r)
    
    p_value = np.mean(np.abs(null_rs) >= np.abs(observed_r))
    return observed_r, p_value, null_rs
```

#### Proposed Model

**Architecture:** DeBERTa-large Formality Ranker (paired correlation analysis)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Human-AI Formality Correlation Analysis
# Theory: If AI accommodates, AI formality should correlate with human formality
# Gate: |r(formality_human_1, formality_AI_1)| > 0.1, p < 0.001

import torch
import numpy as np
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from scipy import stats
from tqdm import tqdm
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HumanAIFormalityCorrelationAnalyzer:
    """
    Analyze correlation between human formality and AI response formality.
    Gate: |r(formality_human_1, formality_AI_1)| > 0.1, p < 0.001
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
            batch_scores = probs[:, 1].cpu().numpy().tolist()
            scores.extend(batch_scores)
        
        return scores
    
    def extract_turn_pairs(self, conversations: List[Dict]) -> Tuple[List[str], List[str]]:
        """Extract (human_1, AI_1) pairs from conversations."""
        human_messages = []
        ai_messages = []
        
        for conv in conversations:
            turns = conv.get('turns', [])
            human_1 = None
            ai_1 = None
            
            for turn in turns:
                role = turn.get('role', '')
                content = turn.get('content', '').strip()
                
                if role == 'human' and human_1 is None and len(content) >= 5:
                    human_1 = content
                elif role == 'assistant' and ai_1 is None and human_1 and len(content) >= 5:
                    ai_1 = content
                    break
            
            if human_1 and ai_1:
                human_messages.append(human_1)
                ai_messages.append(ai_1)
        
        return human_messages, ai_messages
    
    def compute_correlation(self, human_scores: List[float], ai_scores: List[float]) -> Dict:
        """Compute Pearson correlation with significance test."""
        human_arr = np.array(human_scores)
        ai_arr = np.array(ai_scores)
        
        # Pearson correlation
        r, p_value = stats.pearsonr(human_arr, ai_arr)
        
        # Spearman for robustness check
        rho, rho_p = stats.spearmanr(human_arr, ai_arr)
        
        # Effect size
        n = len(human_arr)
        
        results = {
            'n': n,
            'pearson_r': float(r),
            'pearson_p': float(p_value),
            'spearman_rho': float(rho),
            'spearman_p': float(rho_p),
            'human_mean': float(np.mean(human_arr)),
            'human_sd': float(np.std(human_arr)),
            'ai_mean': float(np.mean(ai_arr)),
            'ai_sd': float(np.std(ai_arr)),
        }
        
        # Gate check
        results['gate_threshold'] = 0.1
        results['gate_pass'] = abs(r) > 0.1 and p_value < 0.001
        results['gate_margin'] = abs(r) - 0.1
        
        return results

# Usage:
# analyzer = HumanAIFormalityCorrelationAnalyzer()
# human_msgs, ai_msgs = analyzer.extract_turn_pairs(conversations)
# human_scores = analyzer.score_formality_batch(human_msgs)
# ai_scores = analyzer.score_formality_batch(ai_msgs)
# results = analyzer.compute_correlation(human_scores, ai_scores)
# print(f"r = {results['pearson_r']:.4f}, p = {results['pearson_p']:.2e}")
# print(f"Gate: {'PASS' if results['gate_pass'] else 'FAIL'}")
```

### Training Protocol

**Not applicable** - Statistical correlation analysis, not training experiment.

**Analysis Protocol:**
- **Tool:** Python (transformers, scipy, numpy)
- **Hardware:** GPU recommended for DeBERTa inference
- **Batch size:** 32

**Compute Requirements:**
- GPU: 1x with 16GB VRAM
- Estimated time: 4-6 hours for ~26K pairs (2x messages to score)
- Memory: ~8GB RAM + GPU memory

### Evaluation

**Primary Metrics:**
- Pearson correlation r(human_1, AI_1)
- Significance p-value
- Sample size n

**Success Criteria (Gate):**
- |r| > 0.1 (effect size threshold)
- p < 0.001 (statistical significance)
- N >= 10,000 (statistical power)

**Secondary Criteria:**
- Spearman rho agreement (robustness check)
- Per-model analysis (if gate fails overall)

**Metrics Loading Information:**
- Task Type: Correlation analysis
- Library: scipy.stats
- Code:
```python
from scipy import stats
import numpy as np

def evaluate_correlation(human_scores, ai_scores):
    r, p = stats.pearsonr(human_scores, ai_scores)
    rho, rho_p = stats.spearmanr(human_scores, ai_scores)
    
    results = {
        'n': len(human_scores),
        'pearson_r': r,
        'pearson_p': p,
        'spearman_rho': rho,
        'gate_pass': abs(r) > 0.1 and p < 0.001
    }
    return results
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Scatter Plot**: human_formality vs AI_formality with regression line
- **Correlation Bar**: Observed |r| vs threshold (0.1)

#### Additional Figures (LLM Autonomous)
- Hexbin density plot for large n
- Residual plot from linear regression
- QQ plot for normality check
- Per-model correlation heatmap (if model info available)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Successfully processes >= 10,000 (human, AI) pairs
3. |r(human_1, AI_1)| > 0.1 with p < 0.001

**Expected Outcome:**
H-M1 showed weak but significant user-to-AI adaptation (r=0.0134). H-M2 tests AI-to-human direction. LLMs are trained on human text, so some formality matching expected. Per-model variance likely (different training approaches).

---

## Ablation Studies

If gate fails (|r| < 0.1):
1. **Per-model analysis**: Break down by AI model (e.g., GPT-4 vs Claude vs Llama)
2. **Turn position**: Test (human_2, AI_2) pairs instead
3. **Extreme formality**: Filter to high/low formality humans only
4. **Message length control**: Partial correlation controlling for length

---

## Appendix: Reference Implementations

### Formality Detection Models
1. **s-nlp/deberta-large-formality-ranker** - https://huggingface.co/s-nlp/deberta-large-formality-ranker
   - 87.8% accuracy on GYAFC
   - Fine-tuned DeBERTa-large
   - Citation: Dementieva et al. 2023

### Related Research
2. **Detecting Text Formality** (Dementieva et al. 2023) - RANLP
   - https://aclanthology.org/2023.ranlp-1.31
   - Systematic study of formality detection methods

3. **Communication Accommodation Theory** (Giles et al.)
   - Theoretical foundation for accommodation behavior

4. **BiCA** (Li & Song 2025) - Bidirectional Communication Adaptation
   - Framework for bidirectional adaptation analysis

### Dataset Documentation
5. **Anthropic/hh-rlhf** - https://huggingface.co/datasets/Anthropic/hh-rlhf
   - Human preference data for RLHF
   - Multi-turn Human/Assistant conversations

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10

### Workflow History for This Hypothesis
- 2026-08-10: H-M2 set to IN_PROGRESS (Phase 2C start)
- 2026-08-10: Experiment design completed (Phase 2C)
- Prerequisite H-E1: COMPLETED (BCS SD=0.569)
- Prerequisite H-M1: COMPLETED (lag-1 r=0.0134, p=0.00113)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
