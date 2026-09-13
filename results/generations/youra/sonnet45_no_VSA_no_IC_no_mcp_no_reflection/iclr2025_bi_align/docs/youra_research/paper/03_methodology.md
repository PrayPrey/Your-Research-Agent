# 3. Methodology

## 3.1 Hypothesis: Preference Entropy Collapse Beyond Performance-Justified Levels

We hypothesize that extended RLHF training (beyond initial performance saturation) induces preference entropy collapse faster than task performance improves. Specifically:

**Core Statement:** Under RLHF training on preference datasets, if models undergo extended alignment optimization (10K-20K training steps), then preference distribution entropy collapses faster than task performance improves (inflection point where dH/dP accelerates), because users habituate to model output style and converge on preferences even for subjective tasks where diversity is legitimate.

**Causal Mechanism (4 steps):**
1. **Base models** → high-variance outputs → diverse preferences → **high entropy** (baseline state)
2. **Early RLHF** (1K-5K steps) → quality improvement → entropy decreases **proportionally** to performance (justified reduction)
3. **Extended RLHF** (10K-20K steps) → performance saturates → entropy reduction **accelerates** beyond performance gains (inflection point)
4. **Task stratification** → subjective tasks show **greater entropy collapse** than objective tasks (monoculture evidence)

**Key Assumptions:**
- **A1:** Preference entropy proxies critical evaluation capacity (higher H = diverse judgments)
- **A5:** Existing RLHF datasets contain raw preference distributions (not just aggregated win rates)

This paper focuses on validating **Assumption A5** via sub-hypothesis H-E1. The full causal mechanism (steps 2-4) requires this prerequisite to succeed.

## 3.2 Sub-Hypothesis H-E1: Preference Entropy Existence

**Statement:** Under RLHF preference datasets (Anthropic-HH), if we have access to raw pairwise comparison data, then we can compute Shannon entropy H = -Σ p_i log(p_i) for preference distributions, because the dataset publishes response frequency counts rather than only aggregated win rates.

**Verification Protocol:**
1. Download Anthropic-HH dataset (160K+ pairwise comparisons, public repository)
2. Sample n=100 prompts with ≥5 comparisons each (seed=1 for reproducibility)
3. Group examples by prompt, aggregate preference distributions
4. Compute Shannon entropy H for each prompt's preference distribution
5. Validate entropy range [0, ln(2)] for binary comparisons (0 = perfect consensus, ln(2) ≈ 0.693 = maximum uncertainty)
6. Report success rate (% of prompts with computable entropy) and variance (std of entropy values)

**Success Criteria (MUST_WORK gate):**
- **Primary:** Entropy computable for ≥95% of sampled prompts
- **Secondary:** Entropy variance > 0 (not all constant values)

**Rationale:** If entropy cannot be computed from existing datasets (A5 violated), the entire hypothesis mechanism becomes untestable without new data collection. H-E1 validates the foundational measurement assumption before investing in full causal chain experiments.

## 3.3 Entropy Measurement

**Shannon Entropy Definition:**

$$H = -\sum_{i=1}^{n} p_i \log(p_i)$$

where:
- $p_i$ = proportion of preferences for option $i$
- $n$ = number of response options per prompt
- Natural log (base $e$) for units in nats (vs log₂ for bits)

**For Binary Pairwise Comparisons:**
- $n = 2$ (chosen vs rejected)
- Theoretical range: $[0, \ln(2)] \approx [0, 0.693]$ nats
- Maximum entropy (uniform): $H = \ln(2)$ when $p_{\text{chosen}} = p_{\text{rejected}} = 0.5$
- Minimum entropy (consensus): $H = 0$ when all prefer one option

**Expected Behavior:**
- High diversity prompts (e.g., opinion questions): $H > 0.4$ nats
- Low diversity prompts (e.g., factual QA with clear answer): $H < 0.3$ nats
- Variance across prompts: $\text{std}(H) > 0.1$ nats indicates meaningful spread

## 3.4 Dataset: Anthropic-HH

**Source:** Anthropic Helpful & Harmless (HH) dataset (Bai et al., 2022)
- **Repository:** https://github.com/anthropics/hh-rlhf
- **Size:** 160,800 training examples (helpful-base: 122K, harmless-base: 38K)
- **Format:** Each example contains:
  - `chosen`: full conversation text (Human + Assistant turns) for preferred response
  - `rejected`: full conversation text for less-preferred response
- **Collection:** Single-annotator pairwise comparisons (one labeler per example)

**Sampling Strategy:**
- Sample n=100 prompts from training split (seed=1)
- Filter: require ≥5 examples per prompt group (ensure sufficient data for entropy estimation)
- Grouping: extract prompt from conversation context (first 200 characters of chosen response text as proxy)

**Why Anthropic-HH:**
1. **Public availability:** Open-source dataset, reproducible validation
2. **Scale:** 160K+ comparisons provide large pool for prompt sampling
3. **RLHF relevance:** Used in Constitutional AI, representative of standard evaluation datasets
4. **Raw data access:** Provides individual comparison records (not just aggregated metrics)

## 3.5 Dataset Structure Taxonomy

We identify two dataset format categories relevant for entropy measurement:

| Format Type | Structure | Annotation Cost | Entropy Measurable | Example Dataset |
|-------------|-----------|-----------------|-------------------|-----------------|
| **Pairwise Unique Responses** | Each example compares different response candidates (A1 vs B1, A2 vs B2, ...) | Low (1 annotator per comparison) | **No** — cannot aggregate into distributions over fixed options | Anthropic-HH, WebGPT |
| **Multi-Annotator Fixed Responses** | Multiple annotators rate same response candidates (N voters on {R1, R2, R3, ...}) | High (N annotators × M responses) | **Yes** — distribution over fixed response set | OpenAI Summarization, Chatbot Arena |

**Key Insight:** Pairwise-unique format optimizes annotation cost by assigning different response pairs to each comparison. This prevents per-prompt entropy aggregation because:
- **Intended aggregation:** "For prompt P, what % prefer response A vs B vs C?" (requires fixed {A, B, C})
- **Actual structure:** "Comparison 1: chosen=A1, rejected=B1; Comparison 2: chosen=A2, rejected=B2" (no shared response set)
- **Tautological result:** Treating each comparison as "1 vote for chosen category" yields 50/50 split (every example has 1 chosen + 1 rejected) → H = ln(2) for all prompts

**Multi-annotator-fixed format** avoids this by fixing response candidates per prompt:
- Example: 5 annotators rate {Summary_A, Summary_B, Summary_C, Summary_D} for article X
- Votes: {A: 2, B: 1, C: 1, D: 1} → distribution [0.4, 0.2, 0.2, 0.2] → H = 1.33 nats
- Different article Y has different preference distribution → variance across prompts

## 3.6 Implementation

**Tools:**
- **Dataset loading:** HuggingFace `datasets` library (load_dataset("Anthropic/hh-rlhf"))
- **Entropy computation:** `scipy.stats.entropy` (handles normalization automatically)
- **Visualization:** matplotlib for figures (histogram, scatter plot)

**Code Structure (pseudo-code):**

```python
from datasets import load_dataset
from scipy.stats import entropy
import numpy as np

class PreferenceEntropyAnalyzer:
    def __init__(self, dataset_name="Anthropic/hh-rlhf", sample_size=100):
        self.dataset = load_dataset(dataset_name)
        self.sample_size = sample_size

    def sample_prompts(self, seed=1):
        """Sample prompts with ≥5 examples each."""
        np.random.seed(seed)
        # Group examples by prompt prefix (first 200 chars)
        # Filter groups with count ≥ 5
        # Randomly sample 100 groups
        return sampled_prompts

    def compute_entropy_for_prompt(self, prompt_examples):
        """
        Aggregate preference counts for a single prompt.
        
        Args:
            prompt_examples: List of examples (each has 'chosen', 'rejected')
        Returns:
            entropy in nats (float), or None if insufficient data
        """
        # Count chosen vs rejected (binary distribution)
        chosen_count = len(prompt_examples)
        rejected_count = len(prompt_examples)  # Each example has 1 rejected
        preference_counts = np.array([chosen_count, rejected_count])
        
        # Compute Shannon entropy (natural log)
        return entropy(preference_counts, base=np.e)

    def analyze_dataset(self):
        """Sample prompts, compute entropy for each."""
        sampled_prompts = self.sample_prompts(seed=1)
        results = []
        
        for prompt_id, examples in sampled_prompts.items():
            H = self.compute_entropy_for_prompt(examples)
            if H is not None:
                results.append({'prompt_id': prompt_id, 'entropy': H})
        
        # Compute metrics
        success_rate = len(results) / self.sample_size
        mean_entropy = np.mean([r['entropy'] for r in results])
        std_entropy = np.std([r['entropy'] for r in results])
        
        return {
            'success_rate': success_rate,
            'mean_entropy': mean_entropy,
            'std_entropy': std_entropy,
            'results': results
        }
```

**Validation Checks:**
- All entropy values in range [0, ln(2)] ≈ [0, 0.693] nats
- No NaN or Inf values
- Deterministic results (seed=1 reproducibility)

## 3.7 Expected Outcomes

**If H-E1 Passes (A5 valid):**
- Success rate ≥95% (entropy computable for most prompts)
- Variance > 0 (entropy values show spread across prompts)
- Mean entropy 0.3-0.5 nats (moderate diversity, neither uniform nor consensus)
- Proceed to full hypothesis mechanism tests (H-M1-M4: checkpoint analysis, inflection point detection)

**If H-E1 Fails (A5 violated):**
- Success rate <95% OR variance = 0 (constant entropy)
- Root cause analysis required:
  - **Scenario 1:** Dataset lacks raw counts (only aggregated stats) → need new data collection
  - **Scenario 2:** Dataset format incompatible (pairwise unique responses) → use alternative proxy
  - **Scenario 3:** Implementation bug → fix and revalidate

**Implications:** H-E1 outcome determines whether hypothesis is testable with existing datasets (pass) or requires methodological pivot (fail).

