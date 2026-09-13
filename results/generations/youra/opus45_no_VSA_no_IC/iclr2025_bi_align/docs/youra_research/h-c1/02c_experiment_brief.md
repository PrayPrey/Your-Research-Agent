# Phase 2C: Experiment Brief for H-C1

## Hypothesis Summary

**ID:** h-c1  
**Type:** CONDITION  
**Statement:** Mode 3 proportion is higher for subjective prompts (creative writing) than objective prompts (math/coding) with ratio > 1.5  
**Gate:** SHOULD_WORK  
**Prerequisites:** h-e1 (mode classification infrastructure)

## Success/Falsification Criteria

| Criterion | Threshold | Statistical Test |
|-----------|-----------|------------------|
| Success | Ratio (subjective/objective Mode 3 rate) > 1.5 | Two-proportion z-test, p < 0.05 |
| Falsification | Ratio < 1.0 (opposite direction) | Same test showing objective > subjective |
| Inconclusive | 1.0 ≤ Ratio ≤ 1.5 | Effect exists but below threshold |

---

## Dataset Specification

### Primary Dataset

| Field | Value |
|-------|-------|
| Name | lmsys/chatbot_arena_conversations |
| Type | standard |
| Source | HuggingFace Datasets |
| Reuse | Same dataset as h-e1 |
| Size | ~33K battles, subset by category |

### Prompt Categorization Strategy

Chatbot Arena provides built-in categories (per arena.ai/blog/arena-category/):

**Subjective Categories:**
- `creative_writing` — imaginative, emotionally resonant content
- `general` — open-ended conversation (partial subjective)

**Objective Categories:**
- `coding` — programming tasks with verifiable outputs
- `math` — mathematical reasoning with correct answers
- `hard_prompts` — complex but typically objective (coding/math weighted)

### Categorization Implementation

```python
# Primary: Use Arena's built-in category tags if available
if 'category' in battle:
    category = battle['category']
    
# Fallback: Keyword-based heuristic classification
OBJECTIVE_KEYWORDS = [
    'code', 'python', 'javascript', 'function', 'debug', 'error',
    'calculate', 'solve', 'equation', 'proof', 'algorithm',
    'SQL', 'regex', 'API', 'implement', 'output should be'
]

SUBJECTIVE_KEYWORDS = [
    'write a story', 'creative', 'poem', 'imagine', 'describe',
    'opinion', 'feel', 'think about', 'roleplay', 'pretend',
    'emotional', 'artistic', 'narrative', 'fiction'
]

def classify_prompt(prompt: str) -> str:
    prompt_lower = prompt.lower()
    obj_score = sum(kw in prompt_lower for kw in OBJECTIVE_KEYWORDS)
    subj_score = sum(kw in prompt_lower for kw in SUBJECTIVE_KEYWORDS)
    
    if obj_score > subj_score:
        return 'objective'
    elif subj_score > obj_score:
        return 'subjective'
    else:
        return 'ambiguous'  # Exclude from analysis
```

### Filtering Criteria

1. **Valid battles only**: Inherit h-e1 filters
2. **Clear category**: Exclude ambiguous prompts
3. **Minimum per category**: ≥500 battles in each category for statistical power
4. **Expected yield**: ~40% objective (coding+math), ~30% subjective (creative), ~30% excluded

---

## Model Specification

### Reuse from H-E1

| Component | Reuse | Notes |
|-----------|-------|-------|
| RM Ensemble | Yes | OpenAssistant, PairRM, ArmoRM |
| RM Scores Cache | Yes | `rm_scores.parquet` from h-e1 |
| Mode Classification | Yes | Same median-split logic |
| Human Entropy | Yes | Model-pair level computation |

### No Additional Models Required

This hypothesis uses h-e1's mode classification output directly, adding only prompt categorization.

---

## Implementation Approach

### Dependencies

```
# Inherit from h-e1
datasets>=2.14.0
transformers>=4.40.0
torch>=2.0.0
scipy>=1.10.0
pandas>=2.0.0
numpy>=1.24.0
```

### Pipeline Steps

1. **Load H-E1 Results** (1 min)
   - Load `mode_distribution.json` from h-e1
   - Load per-battle mode assignments
   - Verify Mode 3 exists (prerequisite check)

2. **Prompt Categorization** (5 min)
   - Extract prompts from all battles
   - Apply category classification (Arena tags or keyword heuristic)
   - Split into objective/subjective/ambiguous sets

3. **Stratified Mode Analysis** (2 min)
   - Compute Mode 3 proportion within objective prompts
   - Compute Mode 3 proportion within subjective prompts
   - Calculate ratio: `mode3_subjective / mode3_objective`

4. **Statistical Testing** (1 min)
   - Two-proportion z-test for difference
   - 95% CI for ratio
   - Effect size (Cohen's h)

---

## Statistical Design

### Primary Analysis

```python
from scipy.stats import chi2_contingency, norm

# Contingency table
#                | Mode 3 | Not Mode 3 |
# Subjective     |   a    |     b      |
# Objective      |   c    |     d      |

# Two-proportion z-test
p_subj = a / (a + b)
p_obj = c / (c + d)
ratio = p_subj / p_obj

# Z-test for proportion difference
pooled_p = (a + c) / (a + b + c + d)
se = sqrt(pooled_p * (1 - pooled_p) * (1/(a+b) + 1/(c+d)))
z = (p_subj - p_obj) / se
p_value = 1 - norm.cdf(z)  # One-sided: subjective > objective

# 95% CI for ratio (Koopman method or log-transform)
log_ratio = np.log(ratio)
se_log = sqrt(1/a - 1/(a+b) + 1/c - 1/(c+d))
ci_lower = np.exp(log_ratio - 1.96 * se_log)
ci_upper = np.exp(log_ratio + 1.96 * se_log)
```

### Power Analysis

With expected:
- n_subjective ≈ 6000 battles
- n_objective ≈ 8000 battles
- Mode 3 base rate ≈ 20% (from h-e1)

Detection of ratio 1.5 (24% vs 16%) has power > 0.99 at α=0.05.

---

## Output Specification

### Primary Outputs

| File | Description |
|------|-------------|
| `category_mode_distribution.json` | Mode counts by prompt category |
| `ratio_analysis.json` | Ratio, CI, p-value, effect size |
| `prompt_categories.parquet` | Per-battle category assignments |

### Success Output Format

```json
{
  "hypothesis_id": "h-c1",
  "n_subjective": 6000,
  "n_objective": 8000,
  "mode3_rate_subjective": 0.24,
  "mode3_rate_objective": 0.16,
  "ratio": 1.5,
  "ratio_ci_95_lower": 1.35,
  "ratio_ci_95_upper": 1.67,
  "z_score": 4.2,
  "p_value": 0.00001,
  "cohens_h": 0.21,
  "result": "CONFIRMED"
}
```

---

## Compute Requirements

| Resource | Estimate |
|----------|----------|
| GPU | None (reuses h-e1 RM scores) |
| CPU | Standard laptop sufficient |
| Time | <10 minutes total |
| Storage | ~50MB for category assignments |

This hypothesis is computationally trivial given h-e1 infrastructure.

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Arena categories unavailable | Medium | Low | Keyword heuristic fallback |
| Ambiguous prompts dominate | Low | Medium | Relax keyword thresholds, accept general as partial |
| Low sample in one category | Low | High | Pool similar categories (e.g., coding + math) |
| Ratio < 1.0 (opposite result) | Medium | Low | Report honestly as falsification |
| Ratio 1.0-1.5 (weak effect) | Medium | Medium | Report as partial support, discuss threshold |

---

## Literature Grounding

| Paper | Relevance |
|-------|-----------|
| Arena Category Blog (2024) | Defines Arena's category taxonomy |
| What's up with Llama 3 (LMSYS, 2024) | Shows creative vs coding performance differences |
| Arena-Hard Pipeline (2024) | Prompt difficulty and categorization methods |
| Language Models can Categorize (NAACL 2025) | LLM-based prompt categorization for performance analysis |

---

## Validation Checklist

- [ ] h-e1 mode classification results loaded
- [ ] Prompts successfully categorized (≥500 per category)
- [ ] Mode 3 rates computed for both categories
- [ ] Ratio and 95% CI calculated
- [ ] Statistical test completed
- [ ] Results serialized to JSON

---

## Phase 3 Handoff

Ready for implementation planning with:
- Minimal new code (builds on h-e1)
- Clear categorization strategy (Arena tags + keyword fallback)
- Simple statistical test
- Reuses all h-e1 infrastructure

**Estimated Implementation Complexity:** LIGHT (adds categorization layer to existing pipeline)

---

## Relationship to Main Hypothesis

H-C1 tests a **scope condition**: whether the misaligned-confident mode (Mode 3) concentrates in specific prompt types. This supports the theoretical claim that RM overconfidence correlates with subjective tasks where human preferences are inherently more variable.

- **If confirmed (ratio > 1.5):** Suggests RMs are calibrated better on objective tasks; subjective prompts expose RM limitations
- **If falsified (ratio < 1.0):** Challenges the subjectivity theory; Mode 3 may arise from other factors
- **If inconclusive (1.0-1.5):** Weak evidence; prompt type is one factor among many
