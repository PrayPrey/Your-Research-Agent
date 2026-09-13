# Experiment Design: H-M2

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis Statement:** BiDPO models generate responses with higher collaboration scores than DPO
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests that BiDPO training produces higher-agency responses.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M1 PASSED: training stable, loss decreased 0.929 → 0.918)
**Gate Status:** SHOULD_WORK (document limitation if fails)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (COMPLETED, PASSED)

### Gate Condition
BiDPO-trained model generates responses with statistically higher mean collaboration scores than DPO baseline on held-out prompts (t-test p < 0.05, BiDPO mean > DPO mean).

---

## Continuation Context

This experiment builds on H-M1 results showing BiDPO training is stable (loss decreased from 0.929 to 0.918). The trained BiDPO model checkpoint from H-M1 will be used for generation comparison against DPO baseline.

### Previous Hypothesis Results
**H-E1 (Existence) - PASSED:**
- Correlation: -0.026 (well below 0.7 threshold)
- Conclusion: Collaboration score extracts agency signals orthogonal to preference labels

**H-M1 (Mechanism) - PASSED:**
- Training completed without NaN/Inf
- Loss decreased: 0.929 → 0.918 (1.2% reduction)
- DPO loss stable: 0.679 → 0.664
- BiDPO checkpoint saved at `h-m1/code/outputs/final.pt`

---

## Implementation Research Summary

### Archon Knowledge Base Findings

DPO training and generation patterns identified:
- Standard PyTorch generation with `model.generate()` for response sampling
- TRL DPOTrainer produces models compatible with HuggingFace generation API
- Multi-objective training patterns (MODPO) provide auxiliary loss integration examples

### Archon Code Examples

Generation pattern from diffusers/transformers:
```python
outputs = model.generate(
    input_ids,
    max_new_tokens=512,
    do_sample=True,
    temperature=0.7,
    top_p=0.9
)
```

### Exa GitHub Implementations

**TRL DPOTrainer Generation (Primary Source):**
- DPO-trained models use standard HuggingFace `generate()` API
- No special inference requirements after training
- Reference: eric-mitchell/direct-preference-optimization

**DPO Inference Pattern:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(checkpoint_path)
tokenizer = AutoTokenizer.from_pretrained(model_name)

inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=256)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
```

**HH-RLHF Prompt Extraction:**
```python
# Extract prompts from HH-RLHF test set for held-out evaluation
def extract_prompt(conversation: str) -> str:
    parts = conversation.split('\n\nAssistant:')
    return parts[0] + '\n\nAssistant:'  # Keep Human turn, add Assistant prefix
```

### 🎯 Implementation Priority Assessment

**CRITICAL: Use same base model (Mistral-7B) for fair comparison**

BiDPO model: H-M1 trained checkpoint with L_agency loss
DPO baseline: Original Mistral-7B-Instruct-v0.2 (untrained, or train DPO-only for fair comparison)

**Recommended Implementation Path:**
- Primary: Generate with H-M1 BiDPO checkpoint vs Mistral-7B-Instruct baseline
- Fallback: Train DPO-only baseline for same steps if unfair comparison concerns arise
- Justification: Mistral-7B-Instruct already has DPO-style training, serves as strong baseline

### Code Analysis (Serena MCP)

Not applicable - comparing checkpoint outputs, no codebase analysis needed.

---

## Experiment Specification

### Dataset

**Name:** HH-RLHF Test Split (Held-Out Prompts)
**Source:** HuggingFace Hub
**Version:** Standard release
**Type:** standard

| Split | Size | Purpose |
|-------|------|---------|
| Test | ~8.5K pairs | Extract 500 unique prompts for generation |

**Preprocessing:**
1. Load HH-RLHF test split
2. Extract unique prompts (Human turns only)
3. Sample 500 random prompts for evaluation
4. Format with Mistral chat template

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: Anthropic/hh-rlhf
- Code:
```python
from datasets import load_dataset

dataset = load_dataset("Anthropic/hh-rlhf", data_dir="helpful-base")
test_data = dataset["test"]

def extract_prompt(example):
    """Extract Human turn as prompt."""
    conversation = example['chosen']  # or 'rejected', same prompt
    parts = conversation.split('\n\nAssistant:')
    return parts[0].strip()

# Get 500 unique prompts
prompts = list(set([extract_prompt(ex) for ex in test_data]))
prompts = prompts[:500]  # First 500 unique
```

### Models

#### Baseline Model

**Name:** Mistral-7B-Instruct-v0.2
**Source:** HuggingFace Hub
**Type:** Instruction-tuned LLM (DPO-trained baseline)

This serves as the DPO baseline since Mistral-7B-Instruct has already undergone preference optimization during its release training.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: mistralai/Mistral-7B-Instruct-v0.2
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

baseline_model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.2",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")
tokenizer.pad_token = tokenizer.eos_token
```

#### Proposed Model

**Architecture:** BiDPO-trained Mistral-7B (from H-M1)

**Loading Information:**
- Method: Load H-M1 checkpoint
- Path: `../h-m1/code/outputs/final.pt` (relative to h-m2)
- Code:
```python
import torch
from transformers import AutoModelForCausalLM

# Load BiDPO checkpoint from H-M1
bidpo_model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.2",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

# Load trained weights
checkpoint = torch.load("../h-m1/code/outputs/final.pt", map_location="cpu")
bidpo_model.load_state_dict(checkpoint["model_state_dict"], strict=False)
```

**Core Mechanism Implementation:**

```python
import re
import numpy as np
from scipy import stats
from tqdm import tqdm

def compute_collab_score_v2(response: str) -> float:
    """
    Length-normalized collaboration score (from H-E1).
    Measures agency-preservation signals in response text.
    """
    if not response or len(response) < 10:
        return 0.0
    
    response_lower = response.lower()
    word_count = len(response.split())
    
    # Reasoning trace signals
    reasoning_patterns = [
        r'\bbecause\b', r'\bsince\b', r'\btherefore\b', 
        r'\bthis means\b', r'\bas a result\b', r'\bso that\b'
    ]
    reasoning_score = sum(len(re.findall(p, response_lower)) for p in reasoning_patterns)
    
    # Uncertainty acknowledgment signals
    uncertainty_patterns = [
        r'\bi think\b', r'\bmight\b', r'\bcould be\b',
        r'\bperhaps\b', r'\buncertain\b', r'\bpossibly\b'
    ]
    uncertainty_score = sum(len(re.findall(p, response_lower)) for p in uncertainty_patterns)
    
    # User engagement signals
    engagement_patterns = [
        r'\byou could\b', r'\bconsider\b', r'\boption\b',
        r'\byou might\b', r'\bwhat do you\b'
    ]
    engagement_score = sum(len(re.findall(p, response_lower)) for p in engagement_patterns)
    engagement_score += response.count('?')
    
    # Explanation depth signals
    depth_patterns = [
        r'\bfirst\b', r'\bsecond\b', r'\bthird\b',
        r'\bstep \d', r'^\d+\.', r'^-\s'
    ]
    depth_score = sum(len(re.findall(p, response_lower, re.MULTILINE)) for p in depth_patterns)
    
    # Combine and normalize
    raw_score = reasoning_score + uncertainty_score + engagement_score + depth_score
    normalized_score = raw_score / np.sqrt(word_count)
    
    return normalized_score


def generate_responses(model, tokenizer, prompts: list, max_new_tokens: int = 256) -> list:
    """Generate responses for a list of prompts."""
    responses = []
    model.eval()
    
    for prompt in tqdm(prompts, desc="Generating"):
        # Format with Mistral chat template
        formatted = f"[INST] {prompt.replace('Human:', '').strip()} [/INST]"
        inputs = tokenizer(formatted, return_tensors="pt", truncation=True, max_length=768)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=tokenizer.pad_token_id
            )
        
        response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        responses.append(response)
    
    return responses


def compare_collab_scores(bidpo_responses: list, dpo_responses: list) -> dict:
    """
    Compare collaboration scores between BiDPO and DPO responses.
    
    Returns:
        dict with statistics and gate decision
    """
    bidpo_scores = [compute_collab_score_v2(r) for r in bidpo_responses]
    dpo_scores = [compute_collab_score_v2(r) for r in dpo_responses]
    
    # Paired t-test (same prompts)
    t_stat, p_value = stats.ttest_rel(bidpo_scores, dpo_scores)
    
    # One-sided test: BiDPO > DPO
    p_value_onesided = p_value / 2 if t_stat > 0 else 1 - p_value / 2
    
    return {
        'bidpo_mean': np.mean(bidpo_scores),
        'bidpo_std': np.std(bidpo_scores),
        'dpo_mean': np.mean(dpo_scores),
        'dpo_std': np.std(dpo_scores),
        'mean_difference': np.mean(bidpo_scores) - np.mean(dpo_scores),
        't_statistic': t_stat,
        'p_value': p_value,
        'p_value_onesided': p_value_onesided,
        'effect_size_cohens_d': (np.mean(bidpo_scores) - np.mean(dpo_scores)) / np.sqrt((np.std(bidpo_scores)**2 + np.std(dpo_scores)**2) / 2),
        'gate_passed': np.mean(bidpo_scores) > np.mean(dpo_scores) and p_value_onesided < 0.05,
        'n_samples': len(bidpo_scores)
    }
```

### Training Protocol

| Parameter | Value | Justification |
|-----------|-------|---------------|
| **Training Required** | No | Evaluation of pre-trained models |
| **Generation Samples** | 500 prompts | Per Phase 2B protocol |
| **Max New Tokens** | 256 | Sufficient for response comparison |
| **Temperature** | 0.7 | Balanced diversity vs quality |
| **Top-p** | 0.9 | Standard nucleus sampling |
| **Random Seed** | 42 | Reproducibility |

### Evaluation

**Primary Metrics:**

| Metric | Measurement | Success Criterion |
|--------|-------------|-------------------|
| BiDPO Mean Score | mean(collab_score_v2) | Higher than DPO |
| DPO Mean Score | mean(collab_score_v2) | Baseline reference |
| Mean Difference | BiDPO - DPO | > 0 |
| Paired t-test p-value | One-sided | p < 0.05 |
| Cohen's d | Effect size | > 0.2 (small effect) |

**Secondary Metrics:**
- Score distributions (histograms)
- Per-prompt comparison (scatter plot)
- Response length analysis (control for verbosity)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Generation + scoring
- Library: scipy.stats, numpy
- Code:
```python
from scipy import stats
import numpy as np

# Paired t-test for same prompts
t_stat, p_value = stats.ttest_rel(bidpo_scores, dpo_scores)

# Cohen's d effect size
pooled_std = np.sqrt((np.std(a)**2 + np.std(b)**2) / 2)
cohens_d = (np.mean(a) - np.mean(b)) / pooled_std
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing BiDPO vs DPO mean collaboration scores with error bars

#### Additional Figures (LLM Autonomous)

1. **Score Distribution Comparison**: Overlapping histograms of BiDPO vs DPO collab_scores
2. **Per-Prompt Scatter**: X=DPO score, Y=BiDPO score, diagonal line for reference
3. **Score Component Breakdown**: Stacked bar showing reasoning/uncertainty/engagement/depth contributions
4. **Response Length vs Score**: Control analysis for verbosity confound

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `bidpo_mean > dpo_mean` (BiDPO generates higher-agency responses)
3. `p_value_onesided < 0.05` (statistically significant)

**Gate Decision:**
- PASS → Proceed to H-M3 (test capability transfer via MT-Bench)
- FAIL → Document limitation, explore stronger lambda or different heuristics

---

## Appendix: Reference Implementations

### HuggingFace Generation
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)

outputs = model.generate(
    input_ids,
    max_new_tokens=256,
    do_sample=True,
    temperature=0.7,
    top_p=0.9
)
```

### Mistral Chat Template
```python
# Mistral instruction format
prompt = f"[INST] {user_message} [/INST]"
```

### Paired Statistical Test
```python
from scipy import stats

# Paired t-test for dependent samples (same prompts)
t_stat, p_value = stats.ttest_rel(group1, group2)

# One-sided p-value (testing group1 > group2)
p_onesided = p_value / 2 if t_stat > 0 else 1 - p_value / 2
```

### Cohen's d Effect Size
```python
def cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    return (np.mean(group1) - np.mean(group2)) / pooled_std
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18

### Workflow History for This Hypothesis
- H-E1 PASSED (correlation=-0.026): Collaboration score validated as orthogonal signal
- H-M1 PASSED (loss decreased 0.929→0.918): BiDPO training stable
- H-M2 IN_PROGRESS: Testing if BiDPO generates higher-agency responses

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
