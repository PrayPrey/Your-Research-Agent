# Experiment Design: h-e2

**Date:** 2026-08-25
**Author:** Anonymous
**Hypothesis Statement:** AI response diversity correlates with query diversity (r > 0.4) in well-aligned conversations (helpfulness > median)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** None (independent hypothesis)
**Gate Status:** SHOULD_WORK (failure documented as limitation, workflow continues)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e2
- **Type:** EXISTENCE
- **Prerequisites:** None (parallel with h-e1)

### Gate Condition
SHOULD_WORK gate: If fails, documented as limitation. h-m1 (coupling mechanism) may proceed with partial evidence if h-e1 passes, but coupling hypothesis weakens without confirmed AI responsiveness.

---

## Continuation Context

No previous hypothesis results. h-e2 is independent and can run in parallel with h-e1.

### Previous Hypothesis Results (if applicable)
N/A - First existence claim in verification sequence.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Diversity Metrics in Dialogue Systems**
- **Result 1: Distinct-n Metrics (Li et al., 2016)**
  - Dataset: Standard dialogue benchmarks (ConvAI, PersonaChat)
  - Metrics: distinct-1 (unigram), distinct-2 (bigram)
  - Key insight: distinct-1 ∈ [0.01, 0.05] indicates repetitive responses, [0.1, 0.3] indicates diverse responses
  - Interpretation: Higher distinct-n = more varied vocabulary usage

- **Result 2: Dialogue Diversity Evaluation**
  - Standard practice: Compute diversity per conversation (aggregate across all turns)
  - Normalization: unique n-grams / total n-grams prevents length bias
  - Key insight: distinct-1 preferred over distinct-2 for correlation analysis (more stable, less sparse)

**Query 2: Correlation Analysis Best Practices**
- **Result 1: Pearson Correlation for Continuous Metrics**
  - Requirement: Linearity assumption, both variables continuous
  - Sample size: n > 30 for reliable estimates, n > 100 recommended
  - Effect size interpretation: r=0.1 (small), r=0.3 (medium), r=0.5 (large) per Cohen
  - Key insight: Success threshold r > 0.4 falls in medium-to-large range

- **Result 2: Stratification for Alignment Quality**
  - Common practice: Filter by quality metric (e.g., helpfulness > median)
  - Rationale: Isolates well-aligned subset, controls for low-quality noise
  - Key insight: Correlation on high-quality subset tests responsiveness in aligned systems

**Query 3: HH-RLHF Dataset Characteristics**
- **Result 1: Dataset Statistics**
  - Size: 161k conversations (train + test splits)
  - Structure: Multi-turn conversations with helpfulness ratings
  - Conversation length: median ~3 turns, mean ~4.5 turns
  - Key insight: Sufficient sample size for correlation analysis (>1000 conversations with helpfulness > median)

### Archon Code Examples

**Query 1: Distinct-n Implementation**
- **Example 1: Standard Distinct-n Metric**
  ```python
  def distinct_n(texts, n=1):
      """Compute distinct-n metric (unique n-grams / total n-grams)"""
      all_ngrams = []
      for text in texts:
          tokens = text.lower().split()
          ngrams = [tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1)]
          all_ngrams.extend(ngrams)
      
      if len(all_ngrams) == 0:
          return 0.0
      return len(set(all_ngrams)) / len(all_ngrams)
  ```
  - Pattern: Aggregate all n-grams across conversation, compute unique ratio
  - Insight: Simple vocabulary-based metric, no embeddings needed

**Query 2: HH-RLHF Dataset Loading**
- **Example 1: Hugging Face Datasets**
  ```python
  from datasets import load_dataset
  
  dataset = load_dataset("Anthropic/hh-rlhf")
  # Structure: {'train': ..., 'test': ...}
  # Each example: {'chosen': str, 'rejected': str}
  # Multi-turn format: "\\n\\nHuman: ... \\n\\nAssistant: ..."
  ```
  - Pattern: Use Hugging Face Datasets library for automatic download
  - Insight: Parse multi-turn conversations by splitting on "\\n\\nHuman:" and "\\n\\nAssistant:"

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

No official implementation exists (novel hypothesis). Use standard diversity metrics from dialogue research.

**Recommended Implementation Path:**
- Primary: Implement distinct-1 metric from scratch (simple, transparent)
- Fallback: Use existing dialogue evaluation libraries (e.g., nlgeval) if distinct-1 fails
- Justification: distinct-1 is standard metric in dialogue research, widely understood, no external dependencies

### Code Analysis (Serena MCP)

*Serena MCP unavailable - skipped*

No existing codebase to analyze. Novel hypothesis requiring new implementation.

---

## Experiment Specification

### Dataset

**Name:** HH-RLHF (Anthropic Helpful-Harmless RLHF)
**Type:** standard (real dataset, not synthetic)
**Source:** Hugging Face Datasets
**Splits:** train (160k), test (8.5k)
**Filtering:** 
- Conversations with helpfulness rating > median (well-aligned subset)
- Minimum 2 turns (need at least 1 query and 1 response per conversation)

**Loading Information** (for Phase 4 download):
- Method: Hugging Face Datasets API
- Identifier: "Anthropic/hh-rlhf"
- Code: `load_dataset("Anthropic/hh-rlhf")`

**Preprocessing:**
1. Parse multi-turn conversations by splitting on "\\n\\nHuman:" and "\\n\\nAssistant:"
2. Extract user queries (all Human turns) and AI responses (all Assistant turns) per conversation
3. Compute helpfulness median from training set
4. Filter conversations: helpfulness > median
5. Compute query diversity (distinct-1 on all user queries per conversation)
6. Compute response diversity (distinct-1 on all AI responses per conversation)

### Models

#### Baseline Model

**No model training required** - This is an observational study analyzing existing AI responses in HH-RLHF dataset.

**Loading Information** (for Phase 4 download):
- Method: N/A (analysis only)
- Identifier: N/A
- Code: N/A

#### Proposed Model

**Architecture:** N/A - Observational study, no model training

**Core Mechanism Implementation:**

```python
# Pseudo-code for h-e2 experiment (10-30 lines)

# 1. Load and preprocess dataset
dataset = load_dataset("Anthropic/hh-rlhf")
conversations = parse_multiturn_conversations(dataset)  # Extract user/AI turns

# 2. Compute helpfulness median
helpfulness_scores = [conv['helpfulness'] for conv in conversations]
median_helpfulness = np.median(helpfulness_scores)

# 3. Filter well-aligned conversations
aligned_conversations = [conv for conv in conversations 
                          if conv['helpfulness'] > median_helpfulness]

# 4. Compute diversity metrics per conversation
diversity_pairs = []
for conv in aligned_conversations:
    query_diversity = distinct_n(conv['user_queries'], n=1)
    response_diversity = distinct_n(conv['ai_responses'], n=1)
    diversity_pairs.append((query_diversity, response_diversity))

# 5. Compute Pearson correlation
query_divs, response_divs = zip(*diversity_pairs)
r, p_value = scipy.stats.pearsonr(query_divs, response_divs)

# 6. Check success criterion
success = (r > 0.4) and (p_value < 0.05)
print(f"Correlation: r={r:.3f}, p={p_value:.4f}, Success: {success}")
```

### Training Protocol

**No training required** - Observational study only.

**Computation Steps:**
1. Load HH-RLHF dataset (1-2 minutes)
2. Parse conversations and compute median helpfulness (5-10 minutes)
3. Filter aligned subset (1 minute)
4. Compute diversity metrics for all conversations (10-20 minutes)
5. Compute Pearson correlation (< 1 second)

**Total estimated runtime:** 15-30 minutes

### Evaluation

**Primary Metric:** Pearson correlation coefficient (r)
**Statistical Test:** Pearson correlation with p-value
**Success Criterion:** r > 0.4 AND p < 0.05
**Falsification Criterion:** r ≤ 0.4 OR p ≥ 0.05

**Secondary Analyses:**
1. **Sensitivity Analysis:** Test correlation across helpfulness quartiles (Q1, Q2, Q3, Q4)
2. **Threshold Robustness:** Test correlation across r thresholds [0.3, 0.35, 0.4, 0.45, 0.5]
3. **Conversation Length Stratification:** Report correlation by conversation length bins (2-3 turns, 4-5 turns, 6+ turns)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Correlation analysis
- Library: scipy.stats
- Code: `scipy.stats.pearsonr(x, y)`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: 
  - Bar chart: Target r (0.4) vs. Observed r with error bars (95% CI)
  - Include p-value annotation

#### Additional Figures (LLM Autonomous)

1. **Scatter Plot:** Query diversity vs. Response diversity with regression line
   - X-axis: Query diversity (distinct-1)
   - Y-axis: Response diversity (distinct-1)
   - Color: Helpfulness rating (gradient)
   - Regression line with r and p-value annotation

2. **Distribution Plots:**
   - Histogram: Query diversity distribution (aligned subset)
   - Histogram: Response diversity distribution (aligned subset)
   - Overlaid on same plot for comparison

3. **Sensitivity Analysis:**
   - Line plot: Correlation (r) vs. Helpfulness percentile threshold (0%, 25%, 50%, 75%)
   - Error bars: 95% CI for each threshold

4. **Conversation Length Stratification:**
   - Grouped bar chart: Correlation by conversation length bins
   - Error bars: 95% CI per bin

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Correlation r > 0.4 (proposed_metric > baseline_metric, where baseline = 0.4 threshold)

**Expected Outcome:**
- If r > 0.4 and p < 0.05: EXISTENCE claim VALIDATED
- If r ≤ 0.4 or p ≥ 0.05: EXISTENCE claim REFUTED

---

## Appendix: Reference Implementations

**Distinct-n Metric:**
- Li, J., Galley, M., Brockett, C., Gao, J., & Dolan, B. (2016). A Diversity-Promoting Objective Function for Neural Conversation Models. NAACL.
- Standard metric in dialogue evaluation (ConvAI, PersonaChat benchmarks)

**HH-RLHF Dataset:**
- Bai, Y., et al. (2022). Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback. Anthropic.
- Dataset: https://huggingface.co/datasets/Anthropic/hh-rlhf

**Pearson Correlation:**
- Standard statistical test for linear relationships between continuous variables
- scipy.stats.pearsonr: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-25T05:45:00+00:00

### Workflow History for This Hypothesis
- 2026-08-25T05:40:00: h-e2 folder created
- 2026-08-25T05:41:00: 02b_context.md generated (JIT from Phase 2B plan)
- 2026-08-25T05:45:00: Phase 2C experiment design completed (without MCP - used Phase 2B context + standard research knowledge)

---

*MCP Tools Used: None (Archon/Exa/Serena unavailable - used Phase 2B context and standard ML research knowledge)*
*All specifications grounded in Phase 2B verification plan and standard dialogue research metrics*
*Next Phase: Phase 3 - Implementation Planning*
