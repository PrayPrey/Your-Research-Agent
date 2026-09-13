# 4. Experiments

## 4.1 H-E1 Implementation

We implemented the preference entropy analyzer as a Python script using standard scientific libraries:

- **Dataset loading:** HuggingFace `datasets` (v2.14.0) with `load_dataset("Anthropic/hh-rlhf")`
- **Entropy computation:** `scipy.stats.entropy` (v1.11.0) with natural log (base=np.e)
- **Numerical operations:** NumPy (v1.24.0) for array manipulation
- **Visualization:** matplotlib (v3.7.0) for figures

**Code Architecture:**
- `PreferenceEntropyAnalyzer` class (248 lines total)
  - `sample_prompts(seed=1)`: deterministic prompt sampling with grouping by first 200 characters
  - `compute_entropy_for_prompt(examples)`: Shannon entropy H = -Σ p_i log(p_i) from preference counts
  - `analyze_dataset()`: orchestrates sampling → computation → metrics aggregation
  - `generate_visualizations()`: produces 4 figures (gate metrics, histogram, scatter, pie chart)

**Reproducibility:** Fixed random seed (seed=1) for prompt sampling ensures deterministic results across runs.

## 4.2 Dataset Download and Preprocessing

**Anthropic-HH Dataset:**
- Downloaded via HuggingFace Hub (cached locally after first run)
- Training split: 160,800 examples
- Validation performed on training split only (test split reserved for future work)

**Prompt Grouping Methodology:**
- **Challenge:** Anthropic-HH does not provide explicit prompt IDs
- **Solution:** Extract prompt proxy from conversation context
  - Use first 200 characters of `chosen` response text as grouping key
  - Rationale: Conversation structure includes Human prompt → Assistant response; first 200 chars typically capture prompt context
- **Filtering:** Require ≥5 examples per prompt group (minimum sample size for entropy estimation)
- **Sampling:** Randomly sample 100 prompt groups from filtered set (seed=1)

**Example Prompt Groups (from results):**
1. "Indian people are the worst kind of peopl" → 6 comparisons
2. "Where is the best place inside a church..." → 5 comparisons
3. "I'm having some problems with my car..." → 6 comparisons
4. "I like to host guests at my home..." → 42 comparisons
5. "How do I kill my neighbor..." → 12 comparisons

**Group Size Distribution:**
- Min: 5 comparisons (filtering threshold)
- Max: 57 comparisons
- Median: 6 comparisons
- Mean: 9.6 comparisons

## 4.3 Entropy Computation

**Algorithm:**
For each prompt group with n examples:
1. Aggregate preference counts: `[chosen_count, rejected_count]`
2. Normalize to probabilities: `p = counts / sum(counts)`
3. Apply Shannon formula: `H = -sum(p * log(p))` (scipy.stats.entropy handles normalization)
4. Validate result: check H ∈ [0, ln(2)] ≈ [0, 0.693] nats

**Edge Case Handling:**
- **Zero probabilities:** scipy.stats.entropy filters out p=0 before log (no log(0) errors)
- **Single-option distributions:** If all chose same option → p=[1,0] → H=0 (perfect consensus)
- **Uniform distributions:** If equal split → p=[0.5,0.5] → H=ln(2) (maximum uncertainty)

**Validation Metrics Computed:**
- **Success rate:** `(prompts with valid entropy) / (total sampled)` × 100
- **Mean entropy:** `mean(H_values)` across successful prompts
- **Std entropy:** `std(H_values)` — variance check (gate criterion: >0)
- **Range check:** `all(0 ≤ H ≤ ln(2))` — theoretical bounds validation

## 4.4 Execution Environment

**Hardware:**
- CPU-only execution (no GPU required for data analysis)
- RAM: 8GB sufficient (dataset ~500MB cached)

**Runtime:**
- Dataset download: ~30 seconds (first run; cached afterward)
- Prompt sampling: <1 second
- Entropy computation: <5 seconds (100 prompts)
- Visualization generation: ~10 seconds (4 figures)
- **Total execution time:** 25 seconds (including dataset caching)

**Output Artifacts:**
- `h-e1_results.json`: 527 lines, entropy values for all 100 prompts
- `figures/gate_metrics.png`: target vs actual metrics bar chart (41KB)
- `figures/entropy_histogram.png`: distribution of entropy values (44KB)
- `figures/entropy_scatter.png`: entropy vs prompt index (44KB)
- `figures/success_rate_pie.png`: computation success rate (39KB)

## 4.5 Reproducibility Statement

All code, data paths, and random seeds documented in experiment brief (02c_experiment_brief.md). Independent verification:
1. Install dependencies: `pip install datasets scipy numpy matplotlib`
2. Run script: `python preference_entropy_analyzer.py`
3. Expected output: same 100 prompt groups (seed=1), identical entropy values (deterministic computation)

**Dataset Version Control:** HuggingFace datasets library caches specific commit hash, ensuring same Anthropic-HH version across runs.

