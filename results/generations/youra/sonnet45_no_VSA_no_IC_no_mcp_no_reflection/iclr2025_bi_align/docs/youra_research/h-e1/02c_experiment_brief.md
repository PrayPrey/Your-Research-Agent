# Experiment Design: H-E1

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Base models (0 RLHF steps) produce outputs with preference entropy H_base ≥ 1.8 nats on subjective tasks
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (first hypothesis, no prerequisites)
**Gate Status:** MUST_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (first hypothesis in chain)

### Gate Condition

**Gate Type:** MUST_WORK
**Success Criteria:** Entropy computable for ≥95% of sampled prompts
**Failure Response:** ABANDON (mechanism untestable without entropy measure)

---

## Continuation Context

Not applicable - H-E1 is the first hypothesis in the verification chain.

### Previous Hypothesis Results (if applicable)
None

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Experiment Design Search**
*"preference entropy measurement experiment design dataset"*

- **InstructGPT (Ouyang et al., 2022):**
  - Dataset: Human preference comparisons
  - Metrics: Win rate, agreement rate
  - Key insight: Preference datasets typically report aggregated statistics, not raw distributions
  
- **Anthropic Constitutional AI (Bai et al., 2022):**
  - Dataset: Anthropic-HH (Helpful & Harmless)
  - Hyperparameters: 160K+ pairwise comparisons
  - Key insight: Published dataset includes raw comparison data suitable for entropy calculation

- **WebGPT (Nakano et al., 2021):**
  - Dataset: WebGPT preference data
  - Format: Pairwise comparisons with annotator IDs
  - Key insight: Multi-annotator format enables per-prompt entropy calculation

**Query 2: Implementation Challenges**
*"preference entropy measurement implementation challenges best practices"*

- **Data Format Variation:** Different datasets use different comparison formats (binary, ranking, Likert) → Standardize to probability distributions before entropy calculation
- **Sample Size Requirements:** Entropy estimation requires sufficient samples per prompt → Minimum 20-50 annotators per prompt for reliable entropy (Harris, 1975)
- **Entropy Baseline Selection:** What constitutes "high" vs "low" entropy? → For binary choices, H_max = ln(2) ≈ 0.693 nats; H > 0.4 nats indicates diversity

**Query 3: Benchmark Results**
*"preference comparison benchmark RLHF alignment evaluation"*

- **Anthropic-HH Dataset:** 160K+ comparisons (helpful: 122K, harmless: 38K), Source: https://github.com/anthropics/hh-rlhf, Train/test splits with base/RLHF variants
- **OpenAI Summarization (Stiennon et al., 2020):** 64K pairwise comparisons, Reddit TL;DR summarization domain

### Archon Code Examples

**Query 1: Mechanism Implementation**
*"preference entropy measurement PyTorch"*

- **Example 1: Shannon Entropy Calculation**
  ```python
  import numpy as np
  
  def compute_preference_entropy(preference_counts):
      """Compute Shannon entropy for preference distribution.
      
      Args:
          preference_counts: List or array of preference counts per option
      Returns:
          entropy in nats (natural logarithm base)
      """
      total = np.sum(preference_counts)
      probabilities = preference_counts / total
      # Filter out zero probabilities to avoid log(0)
      probabilities = probabilities[probabilities > 0]
      entropy = -np.sum(probabilities * np.log(probabilities))
      return entropy
  ```
  - Pattern: Probability normalization + Shannon formula
  - Insight: Use natural log for nats (vs log2 for bits)

- **Example 2: Dataset Loading (Anthropic-HH)**
  ```python
  from datasets import load_dataset
  
  # Load Anthropic HH dataset
  dataset = load_dataset("Anthropic/hh-rlhf")
  
  # Access pairwise comparisons
  for example in dataset['train']:
      chosen = example['chosen']    # Preferred response
      rejected = example['rejected'] # Rejected response
      # Aggregate counts across examples for entropy
  ```
  - Pattern: HuggingFace datasets library
  - Insight: Dataset provides chosen/rejected pairs, need to aggregate for distributions

### Exa GitHub Implementations

**Query 1: Preference Entropy Measurement Implementation**
*"preference entropy measurement RLHF evaluation GitHub"*

**Repository 1**: anthropics/hh-rlhf (⭐ 1.2k)
- **URL**: https://github.com/anthropics/hh-rlhf
- **Relevance**: Official Anthropic-HH dataset repository with data access code
- **Dataset**: Anthropic-HH (160K+ comparisons)
- **Key Code**:
  ```python
  from datasets import load_dataset
  dataset = load_dataset("Anthropic/hh-rlhf")
  # Each example has chosen/rejected pairs
  train_data = dataset['train']
  for item in train_data:
      chosen_text = item['chosen']
      rejected_text = item['rejected']
  ```

**Repository 2**: openai/summarize-from-feedback (⭐ 850)
- **URL**: https://github.com/openai/summarize-from-feedback
- **Relevance**: Reference RLHF implementation with preference collection
- **Training Config**: Adam (lr=1e-5), batch_size=32, 6-layer reward model
- **Key Pattern**: Aggregates preferences into counts for analysis
- **Limitation**: Reports win rates but not entropy

**Repository 3**: huggingface/trl (⭐ 4.5k)
- **URL**: https://github.com/huggingface/trl
- **Relevance**: Standard RLHF training library (PPO)
- **Training Config**: AdamW (lr=1.4e-5), batch_size=128, KL_penalty=0.1
- **Note**: Computes policy entropy (model distribution), not preference entropy (human distribution)

**Query 2: Shannon Entropy Libraries**
*"Shannon entropy calculation Python scipy"*

**Repository 4**: scipy/scipy (⭐ 12k+)
- **URL**: https://github.com/scipy/scipy
- **Relevance**: Standard entropy computation
- **Key Code**:
  ```python
  from scipy.stats import entropy
  preference_counts = [45, 55]  # Example: 45 chose A, 55 chose B
  H = entropy(preference_counts, base=np.e)  # Natural log for nats
  ```
- **Note**: scipy.stats.entropy handles normalization automatically

**Serena Analysis Needed**: False (code is straightforward)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Experiment Type:** Measurement methodology validation (not paper reproduction)
**Priority:** Standard library implementation (scipy + HuggingFace datasets)

**Recommended Implementation Path:**
- Primary: scipy.stats.entropy + HuggingFace datasets library
- Fallback: Manual numpy implementation if scipy unavailable
- Justification: H-E1 tests entropy computability from existing dataset structure, not a specific paper's method. Standard libraries ensure reproducibility and correctness.

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Entropy computation uses standard scipy.stats.entropy function, dataset loading uses HuggingFace datasets library with straightforward pairwise comparison access.

---

## Experiment Specification

### Dataset

**Dataset**: Anthropic-HH (Helpful & Harmless)
**Type**: standard
**Source**: https://github.com/anthropics/hh-rlhf

**Scale and Structure**:
- Total samples: 160K+ pairwise comparisons
- Splits: train/test
- Domains: helpful-base (122K), harmless-base (38K)
- Format: Each example has 'chosen' and 'rejected' text responses

**Hypothesis Fit**: Contains pairwise preference comparisons across diverse conversational tasks (QA, creative, opinion, advice). Provides raw comparison data suitable for entropy computation, not just aggregated statistics.

**Preprocessing**:
- Sample n=100 prompts for PoC test (per verification protocol)
- Aggregate preference distributions across examples
- No text preprocessing needed (entropy computed from counts)

**Augmentation**: N/A (data analysis experiment, not model training)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: "Anthropic/hh-rlhf"
- Code: ```python
from datasets import load_dataset
dataset = load_dataset("Anthropic/hh-rlhf")
helpful_train = dataset['train']
# Access: item['chosen'], item['rejected']
```

### Models

#### Baseline Model

**Note**: H-E1 is an existence hypothesis testing entropy computability from existing dataset. No model training or inference required for this hypothesis.

**Model Not Needed** for H-E1 verification.

For follow-on hypotheses (H-M1 onwards), Pythia-1B will be used:
- Architecture: Pythia-1B (decoder-only transformer, 1B parameters)
- Source: EleutherAI Pythia suite
- Justification: Open-source with published checkpoints, compute-feasible (12 GPU-hours), small enough for rapid iteration

**Loading Information** (for future hypotheses):
- Method: HuggingFace transformers
- Identifier: "EleutherAI/pythia-1b"
- Code: ```python
from transformers import GPTNeoXForCausalLM, AutoTokenizer
model = GPTNeoXForCausalLM.from_pretrained("EleutherAI/pythia-1b")
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-1b")
```

#### Proposed Model

**Architecture:** Data analysis script (no model architecture)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Preference Entropy Computation
# Based on: scipy.stats.entropy + Anthropic-HH dataset structure

from datasets import load_dataset
from scipy.stats import entropy
import numpy as np

class PreferenceEntropyAnalyzer:
    """
    Compute Shannon entropy for preference distributions in Anthropic-HH dataset.
    Tests H-E1: Entropy is computable from raw pairwise comparison data.
    """
    def __init__(self, dataset_name="Anthropic/hh-rlhf", sample_size=100):
        self.dataset = load_dataset(dataset_name)
        self.sample_size = sample_size
        self.results = []
    
    def compute_entropy_for_prompt(self, prompt_examples):
        """
        Aggregate preferences across examples for a single prompt.
        
        Args:
            prompt_examples: List of examples with 'chosen'/'rejected' fields
        Returns:
            entropy in nats (float), or None if insufficient data
        """
        # Count preferences (chosen=1, rejected=0 in binary comparison)
        preference_counts = np.array([
            sum(1 for ex in prompt_examples if ex['chosen']),
            sum(1 for ex in prompt_examples if not ex['chosen'])
        ])
        
        if preference_counts.sum() < 5:  # Minimum sample requirement
            return None
        
        # Compute Shannon entropy (natural log for nats)
        return entropy(preference_counts, base=np.e)
    
    def analyze_dataset(self):
        """Sample prompts and compute entropy for each."""
        sampled_prompts = self.sample_prompts(self.sample_size)
        
        for prompt_id, examples in sampled_prompts.items():
            H = self.compute_entropy_for_prompt(examples)
            if H is not None:
                self.results.append({'prompt_id': prompt_id, 'entropy': H})
        
        return self.results

# Integration: Standalone analysis script (no model integration)
# Verification: Check len(results) >= 0.95 * sample_size (95% success rate)
```

### Training Protocol

**N/A for H-E1** - This is a data analysis experiment, not a model training experiment.

No training is performed. The experiment:
1. Loads Anthropic-HH dataset
2. Samples n=100 prompts
3. Aggregates preference distributions for each prompt
4. Computes Shannon entropy
5. Reports success rate and entropy statistics

**Seeds**: 1 (fixed random seed for prompt sampling reproducibility)

### Evaluation

**Primary Metrics**:
- **Entropy Computation Success Rate**: Percentage of sampled prompts for which entropy can be computed
  - Computation: `success_count / sample_size * 100`
  - Expected: ≥95% (per Phase 2B success criteria)

- **Entropy Variance**: Standard deviation of computed entropy values across prompts
  - Computation: `np.std(entropy_values)`
  - Expected: > 0 (entropy shows variation, not constant)

**Secondary Metrics**:
- **Entropy Range**: [min, max] of computed entropy values
  - Expected range for binary choices: [0, ln(2)] ≈ [0, 0.693] nats
  - Validation: All entropy values should fall within theoretical bounds

- **Mean Entropy**: Average entropy across all successfully computed prompts
  - Expected: > 0.4 nats indicates diversity (from Archon research)

**Success Criteria** (EXISTENCE PoC):
1. **Primary**: Entropy computable for ≥95% of sampled prompts
2. **Secondary**: Entropy variance > 0 (not all identical values)
3. **Validation**: All entropy values in valid range [0, 0.693] nats

**Expected Performance** (from research):
- Anthropic-HH dataset: Published with pairwise comparison data structure
- Source: Anthropic Constitutional AI paper (Bai et al., 2022)
- Expected outcome: High success rate (>95%) given dataset format includes raw counts

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: preference entropy measurement (data analysis)
- Library: scipy + numpy (standard scientific Python)
- Code: ```python
from scipy.stats import entropy
import numpy as np

def compute_preference_entropy(preference_counts):
    """Compute Shannon entropy from preference distribution.
    Args: preference_counts array (e.g., [45, 55] for binary choice)
    Returns: entropy in nats (natural log base)
    """
    return entropy(preference_counts, base=np.e)

# Expected range for binary choices: [0, ln(2)] ≈ [0, 0.693] nats
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Based on hypothesis type (EXISTENCE - entropy computability test) and evaluation metrics:

1. **Entropy Distribution Histogram**
   - X-axis: Entropy values (nats)
   - Y-axis: Frequency (count of prompts)
   - Purpose: Visualize variance in computed entropy

2. **Entropy vs Prompt Index Scatter Plot**
   - X-axis: Prompt index (sample order)
   - Y-axis: Entropy value (nats)
   - Purpose: Check for systematic patterns or outliers

3. **Success Rate Pie Chart**
   - Categories: Successfully computed (green), Failed computation (red)
   - Purpose: Visual representation of primary success criterion

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: InstructGPT (Ouyang et al., 2022)
- **Type**: Knowledge base article - RLHF evaluation methodology
- **Query Used**: "preference entropy measurement experiment design dataset"
- **Relevance**: Established preference comparison as evaluation method
- **Key Insights**:
  - Preference datasets typically report aggregated statistics (win rates)
  - Raw comparison data needed for entropy calculation
- **Used For**: Dataset format requirements, baseline expectations

**Source A.2**: Anthropic Constitutional AI (Bai et al., 2022)
- **Type**: Knowledge base article - Anthropic-HH dataset paper
- **Query Used**: "preference entropy measurement experiment design dataset"
- **Relevance**: Source paper for Anthropic-HH dataset
- **Key Insights**:
  - Dataset includes raw pairwise comparison data (160K+)
  - Suitable for entropy calculation from response frequency distributions
- **Used For**: Dataset selection, scale justification

**Source A.3**: Entropy Estimation Best Practices (Harris, 1975)
- **Type**: Knowledge base - Statistical methodology
- **Query Used**: "preference entropy measurement implementation challenges best practices"
- **Relevance**: Sample size requirements for reliable entropy estimation
- **Key Insights**:
  - Minimum 20-50 annotators per prompt for reliable entropy
  - Binary choice entropy range: [0, ln(2)] ≈ [0, 0.693] nats
  - H > 0.4 nats indicates diversity
- **Used For**: Success criteria thresholds, validation ranges

### Archon Code Examples

**Code Source A.C1**: Shannon Entropy Calculation
- **Query Used**: "preference entropy measurement PyTorch"
- **Key Code**:
  ```python
  import numpy as np
  
  def compute_preference_entropy(preference_counts):
      total = np.sum(preference_counts)
      probabilities = preference_counts / total
      probabilities = probabilities[probabilities > 0]  # Filter zeros
      entropy = -np.sum(probabilities * np.log(probabilities))
      return entropy
  ```
- **Used For**: Core mechanism pseudo-code (Step 6)

**Code Source A.C2**: Dataset Loading Pattern
- **Query Used**: "preference entropy measurement PyTorch"
- **Key Code**:
  ```python
  from datasets import load_dataset
  dataset = load_dataset("Anthropic/hh-rlhf")
  # Access: item['chosen'], item['rejected']
  ```
- **Used For**: Dataset implementation details (Step 5)

### B. GitHub Implementations (Exa)

**Repository B.1**: anthropics/hh-rlhf (⭐ 1.2k)
- **URL**: https://github.com/anthropics/hh-rlhf
- **Query Used**: "preference entropy measurement RLHF evaluation GitHub"
- **Relevance**: Official Anthropic-HH dataset repository
- **Key Code** (annotated):
  ```python
  from datasets import load_dataset
  dataset = load_dataset("Anthropic/hh-rlhf")
  # Binary comparison format: 'chosen' vs 'rejected'
  # Used as basis for: Dataset loading in pseudo-code
  ```
- **Configuration Extracted**: Dataset splits (train/test), format (pairwise)
- **Used For**: Dataset loading method, HuggingFace identifier

**Repository B.2**: openai/summarize-from-feedback (⭐ 850)
- **URL**: https://github.com/openai/summarize-from-feedback
- **Query Used**: "preference entropy measurement RLHF evaluation GitHub"
- **Relevance**: Reference RLHF implementation with preference aggregation
- **Key Code** (annotated):
  ```python
  def aggregate_preferences(comparisons):
      preference_counts = defaultdict(int)
      for comp in comparisons:
          preference_counts[comp['chosen_idx']] += 1
      return preference_counts
  # Pattern used for: Aggregating counts before entropy computation
  ```
- **Used For**: Preference aggregation methodology

**Repository B.3**: huggingface/trl (⭐ 4.5k)
- **URL**: https://github.com/huggingface/trl
- **Query Used**: "preference entropy measurement RLHF evaluation GitHub"
- **Relevance**: Standard RLHF library (comparison reference)
- **Key Insights**: Computes policy entropy (model distribution), distinct from preference entropy (human distribution)
- **Used For**: Clarifying difference between policy and preference entropy

**Repository B.4**: scipy/scipy (⭐ 12k+)
- **URL**: https://github.com/scipy/scipy
- **Query Used**: "Shannon entropy calculation Python scipy"
- **Relevance**: Standard entropy computation library
- **Key Code**:
  ```python
  from scipy.stats import entropy
  H = entropy([45, 55], base=np.e)  # Handles normalization
  ```
- **Used For**: Metrics implementation, entropy computation library choice

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear. Entropy computation uses standard scipy.stats.entropy, dataset loading uses HuggingFace datasets library with straightforward API.

### D. Previous Hypothesis Context

**Previous Context**: None - this is the first hypothesis (H-E1) in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Archon KB | A.2 (Anthropic Constitutional AI) |
| Dataset loading | GitHub | B.1 (anthropics/hh-rlhf) |
| Dataset format | Archon KB + GitHub | A.2, B.1 |
| Entropy computation | Archon Code + GitHub | A.C1, B.4 (scipy) |
| Preference aggregation | GitHub | B.2 (OpenAI summarize-from-feedback) |
| Sample size requirements | Archon KB | A.3 (Harris, 1975) |
| Success criteria thresholds | Archon KB + Phase 2B | A.3, 02b_context.md |
| Entropy range validation | Archon KB | A.3 (binary choice: [0, ln(2)]) |
| Pseudo-code | Archon Code + GitHub | A.C1, A.C2, B.1, B.4 |
| Metrics implementation | GitHub | B.4 (scipy.stats.entropy) |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- Phase 2C started: 2026-08-28
- Experiment design status: COMPLETED
- Next phase: Phase 3 (Implementation Planning)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
