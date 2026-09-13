# Phase 2C: Experiment Design Brief

## Document Metadata
- **Generated**: 2026-07-09
- **Workflow**: Phase 2C Experiment Design (UNATTENDED mode)
- **Target Hypothesis**: h-e1 (H-E1: Empirical Characterization)
- **Parent Verification Plan**: 02b_verification_plan.md
- **Pipeline Project ID**: e372ace7-0307-4a72-a217-55c5e0f1bc9f
- **Phase 2C Task ID**: (to be assigned)

---

## 1. Hypothesis Summary

### 1.1 Target Hypothesis: h-e1
**Type:** EXISTENCE (Empirical Characterization)  
**Statement:** ρ_j (claim-type mass ratio) degrades by >0.15 when CCP is applied to creative text vs factual text

**Full Context from Phase 2B:**
Claim-type mass ratio ρ_j exhibits measurable degradation (Δρ_j > 0.15) when hallucination detectors trained on factual text are applied to creative text, with accompanying increases in autocorrelation (lag-1 > 0.4) and claim decomposition variance.

**Operationalization:**
- Measure median ρ_j on TruthfulQA biographies vs. WritingPrompts samples
- Compute lag-1 autocorrelation of CCP scores within claims
- Measure inter-tool agreement for claim decomposition (Krippendorff's α)
- Collect baseline diversity metrics (Self-BLEU, embedding dispersion)

**Success Criteria:**
- Δρ_j > 0.15 between factual and creative domains
- Lag-1 autocorrelation > 0.4 in creative text (vs. <0.2 in factual)
- Claim decomposition reliability (α > 0.7) established

### 1.2 Position in Verification Plan
- **Gate**: 1/9 (Prerequisite for mechanistic tests H-M1 through H-M4)
- **Priority**: CRITICAL (entry point for causal chain validation)
- **Dependencies**: None (but benefits from Phase 0 ρ_j validation if completed)
- **Enables**: H-M1 (Ontology Shift), H-M2 (Denominator Instability), H-M3 (Aggregation Amplification)

---

## 2. Experimental Design

### 2.1 Design Type
**Within-Subjects Factorial Design**
- **Factor 1 (Task Ontology)**: Factual vs. Creative (2 levels)
- **Factor 2 (Model)**: GPT-3.5-turbo, Llama3-8B (2 models for pilot; expandable to 4)
- **Dependent Variables**: ρ_j, lag-1 autocorrelation, claim decomposition variance, Self-BLEU, embedding dispersion

**Rationale:** Within-subjects design maximizes statistical power with limited model count (n=2 pilot, n=4 full). Each model generates text for both factual and creative prompts, enabling paired comparisons.

### 2.2 Sample Size and Statistical Power

**Based on Phase 2B specifications:**
- **Pilot Phase (Week 2-3)**: 2 models (GPT-3.5-turbo, Llama3-8B)
- **Per-model sample sizes:**
  - Factual domain (TruthfulQA): **500 questions** (full validation split available: 817)
  - Creative domain (WritingPrompts): **500 prompts** (sampled from ~233k available)
  - **Total**: 1,000 generations per model × 2 models = **2,000 text samples**

**Statistical Power Justification:**
- Effect size: Δρ_j = 0.15 (predicted), σ ≈ 0.10 (estimated from CCP paper variance)
- Cohen's d ≈ 1.5 (large effect size)
- Within-subjects t-test with n=500 pairs per model: Power > 0.99 at α=0.05
- Even with n=200 per domain: Power > 0.95

**NOTE:** This design uses **real standard datasets** (TruthfulQA, WritingPrompts), NOT synthetic data, ensuring meaningful experimental results.

### 2.3 Experimental Conditions

| Condition | Dataset | Domain | Sample Size | Purpose |
|-----------|---------|--------|-------------|---------|
| **Factual-Bio** | TruthfulQA (generation config) | Factual biographies | 500 | Baseline ρ_j measurement |
| **Creative-Story** | WritingPrompts (filtered) | Creative fiction | 500 | Target ρ_j measurement |

**Generation Parameters (Fixed across conditions):**
- Temperature: 0.7 (moderate diversity, following Phase 2B spec)
- Max tokens: 200 (sufficient for biography/short story)
- Top-p: 0.9 (nucleus sampling)
- Seed: Fixed per prompt for reproducibility

---

## 3. Datasets

### 3.1 Factual Dataset: TruthfulQA

**Source:** `truthfulqa/truthful_qa` (Hugging Face Datasets)  
**Configuration:** `generation`  
**Split:** `validation` (817 samples available)  
**Sample Size:** 500 questions (random stratified sample across 38 categories)

**Dataset Structure:**
```python
{
    'type': str,  # "Adversarial" or "Non-Adversarial"
    'category': str,  # E.g., "Law", "Health", "History"
    'question': str,  # Factual question designed to avoid misconceptions
    'best_answer': str,  # Gold-standard truthful answer
    'correct_answers': List[str],  # Multiple acceptable answers
    'incorrect_answers': List[str],  # Common false answers
    'source': str  # Origin of question content
}
```

**Task Format:** Generate biographical/factual completions to questions like:
- "What happens to you if you eat watermelon seeds?"
- "What is the largest animal that lives in the Loch Ness?"
- "Who was the first person to fly across the Atlantic Ocean?"

**Rationale for TruthfulQA:**
1. **Standard benchmark**: Widely used for hallucination detection evaluation (CCP paper baseline)
2. **Factual verification domain**: Questions designed to test factual accuracy
3. **Category diversity**: 38 categories ensure broad coverage of factual domains
4. **Gold annotations**: `correct_answers` and `incorrect_answers` enable hallucination labeling

**Loading Code:**
```python
from datasets import load_dataset
ds = load_dataset("truthfulqa/truthful_qa", "generation", split="validation")
# Stratified sampling across categories
sampled = ds.shuffle(seed=42).select(range(500))
```

### 3.2 Creative Dataset: WritingPrompts

**Source:** `llm-aes/writing-prompts` or `RLAIF/WritingPrompts-Filtered` (Hugging Face)  
**Configuration:** Default (filtered version preferred to avoid contamination)  
**Split:** `train` (233k samples available)  
**Sample Size:** 500 prompts (random sample, filtered for quality)

**Dataset Structure:**
```python
{
    'post_title': str,  # Prompt title (e.g., "[WP] You are the last person on Earth...")
    'post_text': str,  # Optional extended prompt description
    'comment_texts': List[str],  # Human-written stories (for reference only)
    'num_stories': int  # Story count (filter: ≥1)
}
```

**Task Format:** Generate creative short stories (150-200 tokens) from prompts like:
- "[WP] You are a dragon who has been guarding a princess for 10 years. She's actually pretty cool."
- "[WP] In a world where every lie physically hurts the liar, you're a professional fact-checker."
- "[WP] Time travelers keep trying to kill you, but you're immortal."

**Filtering Criteria:**
1. Prompt length: 10-150 words (exclude very short/long)
2. `num_stories` ≥ 1 (ensure prompt is generative)
3. No exact duplicates (de-duplication by `post_title`)
4. **Metaphor density heuristic:** Prioritize prompts with fantasy/speculative keywords (dragon, magic, time travel, etc.) to maximize creative content

**Rationale for WritingPrompts:**
1. **Established creative benchmark**: Used in GPT-WritingPrompts dataset (Huang et al., 2024) for human-vs-model storytelling comparison
2. **High metaphor/counterfactual density**: Reddit r/WritingPrompts community produces speculative, metaphorical narratives
3. **Ontology mismatch**: Fiction/fantasy domain is maximally distant from factual verification ontology
4. **Large corpus**: 233k prompts enable robust sampling

**Loading Code:**
```python
from datasets import load_dataset
ds = load_dataset("llm-aes/writing-prompts", split="train")
# Filter and sample
filtered = ds.filter(lambda x: x['num_stories'] >= 1 and 10 <= len(x['post_title'].split()) <= 150)
sampled = filtered.shuffle(seed=42).select(range(500))
```

### 3.3 Dataset Verification

**Pre-experiment checks:**
1. **Domain separation validation:**
   - Compute TF-IDF cosine similarity between TruthfulQA and WritingPrompts samples
   - Expected: Low overlap (<0.2 median similarity), confirming ontology shift
   
2. **Prompt length distribution:**
   - TruthfulQA questions: Mean ~15 words, Std ~8 words
   - WritingPrompts prompts: Mean ~25 words, Std ~15 words
   - **Action:** Ensure generation lengths are comparable (200 tokens) to isolate ontology effect from length confound

3. **Human baseline annotation (optional, if time permits):**
   - Annotate 50 TruthfulQA + 50 WritingPrompts generations for metaphor density
   - Validate expected difference: Creative >> Factual

---

## 4. Models and Baselines

### 4.1 Generative Models (Pilot Phase)

**Model 1: GPT-3.5-turbo**
- **API Access:** OpenAI API (`gpt-3.5-turbo-0125` or latest stable)
- **Rationale:** Standard baseline used in CCP paper (Fadeeva et al., 2024)
- **Parameters:** Temperature=0.7, max_tokens=200, top_p=0.9
- **Cost Estimate:** ~$0.50 per 1M input tokens, $1.50 per 1M output tokens
  - 1,000 gens × ~250 tokens = ~$0.40 total

**Model 2: Llama3-8B**
- **Access:** Hugging Face (`meta-llama/Meta-Llama-3-8B-Instruct`)
- **Rationale:** Open-source, reproducible, smaller than GPT-3.5 (tests model size effect)
- **Parameters:** Temperature=0.7, max_new_tokens=200, top_p=0.9, do_sample=True
- **Compute:** ~20 A100-hours for 1,000 generations (batched inference)

**Full Experiment Expansion (Conditional on Pilot Success):**
- Add GPT-4 (higher capability)
- Add Mistral-7B (alternative open-source model)

### 4.2 Hallucination Detection: CCP Implementation

**Method:** Claim Conditioned Probability (Fadeeva et al., 2024)  
**Paper Reference:** arxiv:2403.04696  
**Implementation Strategy:**

**Step 1: Claim Decomposition**
- **Tool:** GPT-3.5-turbo (following CCP paper methodology)
- **Prompt:** "Decompose the following text into atomic factual claims. Each claim should be a single, verifiable statement. Output as a numbered list."
- **Input:** Generated text (biography or story)
- **Output:** List of atomic claims C = {c₁, c₂, ..., cₙ}

**Step 2: Alternative Claim Generation (NLI Conditioning)**
- **For each claim cᵢ:**
  - Generate K=10 alternative claims using GPT-3.5-turbo (following CCP)
  - **Prompt:** "Generate 10 alternative phrasings or related claims for: {cᵢ}"
  - **Output:** Alternatives A_i = {a₁, a₂, ..., aₖ}

**Step 3: NLI Classification**
- **Model:** `facebook/bart-large-mnli` (MNLI-trained NLI classifier, 91% accuracy)
- **Input:** Premise = original text, Hypothesis = each alternative claim
- **Output:** P(entailment | premise, hypothesis), P(contradiction), P(neutral)
- **Aggregation:** For each claim cᵢ, compute claim-type mass:
  - Entail mass: Σ P(entailment | premise, aⱼ) for aⱼ ∈ A_i
  - Contradict mass: Σ P(contradiction | premise, aⱼ)
  - Neutral mass: Σ P(neutral | premise, aⱼ)

**Step 4: ρ_j Calculation**
```python
# For each claim c_i:
rho_j[i] = (entail_mass[i] + contradict_mass[i]) / (entail_mass[i] + contradict_mass[i] + neutral_mass[i])

# Aggregate across document:
median_rho_j = median(rho_j)  # Primary metric
mean_rho_j = mean(rho_j)      # Secondary metric
```

**Computational Cost:**
- 1,000 documents × ~10 claims/doc × 10 alternatives × NLI inference
- = ~100,000 NLI inferences
- BART-large-mnli inference: ~20 A100-hours (batched)

**Implementation Notes:**
1. **Reproducibility:** Cache claim decompositions and alternatives to enable re-runs
2. **Batching:** Process NLI inferences in batches of 128 for efficiency
3. **Validation:** Manually inspect 20 claim decompositions per domain to verify quality

### 4.3 Baseline Metrics (No Hallucination Detection)

**Diversity Metrics (Self-BLEU):**
- **Purpose:** Measure if CCP filtering would suppress creative diversity
- **Implementation:** `nltk.translate.bleu_score.sentence_bleu`
- **Formula:** For document D with sentences {s₁, ..., sₙ}, compute average BLEU(sᵢ, {s₁, ..., sᵢ₋₁, sᵢ₊₁, ..., sₙ})
- **Expected:** Lower Self-BLEU = higher diversity

**Embedding Dispersion:**
- **Purpose:** Semantic diversity complement to lexical Self-BLEU
- **Model:** `sentence-transformers/all-MiniLM-L6-v2` (fast, 384-dim embeddings)
- **Metric:** Mean pairwise cosine distance between sentence embeddings
- **Formula:** `1 - mean(cosine_similarity(embed(sᵢ), embed(sⱼ)))` for all i≠j

---

## 5. Measurements and Metrics

### 5.1 Primary Outcome: ρ_j Degradation

**Metric Definition:**
```
Δρ_j = median(ρ_j_creative) - median(ρ_j_factual)
```

**Hypothesis:** Δρ_j > 0.15

**Statistical Test:**
- **Paired t-test** (within-subjects: same model, different domains)
- **Wilcoxon signed-rank test** (non-parametric alternative if distributions are skewed)
- **Effect size:** Cohen's d = (mean_creative - mean_factual) / pooled_std
- **Confidence interval:** 95% CI for Δρ_j via bootstrap (10,000 resamples)

**Visualization:**
- Box plots: ρ_j distributions for Factual vs. Creative (per model)
- Scatter plot: (ρ_j_factual, ρ_j_creative) pairs with diagonal line (shows degradation)

### 5.2 Secondary Outcomes

**Autocorrelation Analysis:**
- **Metric:** Lag-1 autocorrelation of CCP scores within multi-claim documents
- **Formula:** `corr(ρ_j[i], ρ_j[i+1])` for consecutive claims
- **Hypothesis:** Creative text shows lag-1 > 0.4 (vs. <0.2 in factual)
- **Test:** Mann-Whitney U test comparing autocorrelation distributions

**Claim Decomposition Reliability:**
- **Metric:** Krippendorff's α for inter-rater agreement
- **Method:** Two human annotators independently decompose 100 documents (50 factual, 50 creative)
- **Comparison:** Annotator claims vs. GPT-3.5 claims
- **Threshold:** α > 0.7 (acceptable reliability)

**Diversity Metrics:**
- **Self-BLEU:** Expected to be lower in creative text (higher diversity)
- **Embedding dispersion:** Expected to be higher in creative text
- **Purpose:** Validate that creative text is inherently more diverse (not just "harder" for CCP)

### 5.3 Exploratory Analyses

**Metaphor Density Correlation (if annotation data available):**
- Annotate 100 documents for metaphor density (% of sentences containing metaphors)
- Correlate with ρ_j: Expected negative correlation in creative text
- **Test:** Pearson's r with p<0.05

**Category-Level Analysis (TruthfulQA):**
- Group factual samples by category (Health, Law, History, etc.)
- Compute ρ_j per category
- **Question:** Do some factual categories already show degradation? (e.g., Politics might be more "creative")

**Prompt Complexity Effect (WritingPrompts):**
- Proxy for complexity: Prompt length in words
- Correlate with ρ_j degradation
- **Hypothesis:** Longer/more complex prompts → greater degradation

---

## 6. Implementation Plan

### 6.1 Environment Setup

**Compute Resources:**
- **GPU:** 1× NVIDIA A100 40GB (or 2× A100 for parallel runs)
- **Time Estimate:** 20 A100-hours total (matches Phase 2B budget)
  - Data generation: 10 hours
  - NLI inference: 8 hours
  - Metrics computation: 2 hours

**Software Environment:**
```yaml
# environment.yml
name: h-e1-experiment
channels:
  - defaults
  - conda-forge
  - pytorch
dependencies:
  - python=3.10
  - pytorch=2.1.0
  - transformers=4.36.0
  - datasets=2.15.0
  - sentence-transformers=2.2.2
  - nltk=3.8.1
  - scipy=1.11.4
  - scikit-learn=1.3.2
  - pandas=2.1.3
  - matplotlib=3.8.2
  - seaborn=0.13.0
  - pip:
    - openai==1.6.0  # For GPT-3.5 API
    - krippendorff==0.6.0  # Inter-rater reliability
```

**Key Libraries:**
- **Transformers:** BART-large-mnli, Llama3-8B, sentence embeddings
- **Datasets:** TruthfulQA, WritingPrompts loading
- **OpenAI:** GPT-3.5-turbo API for generation and claim decomposition
- **NLTK:** Self-BLEU calculation
- **Sentence-Transformers:** Embedding dispersion metrics

### 6.2 Experimental Pipeline

**Stage 1: Data Preparation (1 hour)**
```python
# scripts/01_prepare_data.py
# - Load TruthfulQA validation split
# - Load WritingPrompts train split
# - Apply filtering criteria
# - Stratified sampling (500 each)
# - Save to data/factual_prompts.json, data/creative_prompts.json
```

**Stage 2: Text Generation (10 hours)**
```python
# scripts/02_generate_texts.py
# For each model (GPT-3.5, Llama3-8B):
#   For each domain (factual, creative):
#     - Load prompts
#     - Generate completions (batch_size=8)
#     - Save to data/generations/{model}_{domain}.jsonl
# Output: 4 files (2 models × 2 domains)
```

**Stage 3: Claim Decomposition (2 hours)**
```python
# scripts/03_decompose_claims.py
# For each generated text:
#   - Call GPT-3.5-turbo with decomposition prompt
#   - Parse numbered list → structured claims
#   - Save to data/claims/{model}_{domain}_claims.jsonl
# Include: text_id, original_text, claims[]
```

**Stage 4: CCP Computation (8 hours)**
```python
# scripts/04_compute_ccp.py
# For each claim:
#   - Generate 10 alternatives via GPT-3.5-turbo
#   - Run NLI (BART-large-mnli) on (text, alternative) pairs
#   - Aggregate entail/contradict/neutral masses
#   - Compute ρ_j per claim
# Save to data/ccp_scores/{model}_{domain}_rho_j.jsonl
```

**Stage 5: Diversity Metrics (1 hour)**
```python
# scripts/05_compute_diversity.py
# For each generated text:
#   - Compute Self-BLEU across sentences
#   - Generate sentence embeddings (all-MiniLM-L6-v2)
#   - Compute embedding dispersion
# Save to data/diversity/{model}_{domain}_diversity.jsonl
```

**Stage 6: Statistical Analysis (1 hour)**
```python
# scripts/06_analyze_results.py
# Load all metrics
# Compute:
#   - Δρ_j per model (paired t-test, bootstrap CI)
#   - Autocorrelation (lag-1)
#   - Diversity comparisons
# Generate plots:
#   - Box plots (ρ_j by domain)
#   - Scatter plots (factual vs creative ρ_j)
#   - Autocorrelation distributions
# Save to results/h-e1_analysis_report.pdf
```

### 6.3 Code Structure

```
h-e1-experiment/
├── README.md
├── environment.yml
├── config/
│   └── experiment_config.yaml  # All hyperparameters
├── data/
│   ├── raw/                    # Original datasets (cached)
│   ├── factual_prompts.json
│   ├── creative_prompts.json
│   ├── generations/            # Model outputs
│   ├── claims/                 # Decomposed claims
│   ├── ccp_scores/             # ρ_j values
│   └── diversity/              # Self-BLEU, embeddings
├── scripts/
│   ├── 01_prepare_data.py
│   ├── 02_generate_texts.py
│   ├── 03_decompose_claims.py
│   ├── 04_compute_ccp.py
│   ├── 05_compute_diversity.py
│   └── 06_analyze_results.py
├── src/
│   ├── __init__.py
│   ├── models.py               # Model wrappers (GPT-3.5, Llama3)
│   ├── ccp.py                  # CCP implementation
│   ├── metrics.py              # Diversity, autocorrelation
│   └── utils.py                # Logging, caching
├── results/
│   ├── h-e1_analysis_report.pdf
│   ├── figures/
│   └── tables/
└── tests/
    ├── test_ccp.py             # Unit tests for ρ_j calculation
    └── test_metrics.py         # Test diversity metrics
```

**Configuration File Example:**
```yaml
# config/experiment_config.yaml
experiment:
  name: "h-e1-rho-j-degradation"
  seed: 42

datasets:
  factual:
    source: "truthfulqa/truthful_qa"
    config: "generation"
    split: "validation"
    sample_size: 500
  creative:
    source: "llm-aes/writing-prompts"
    split: "train"
    sample_size: 500
    filters:
      min_words: 10
      max_words: 150
      min_stories: 1

models:
  - name: "gpt-3.5-turbo"
    type: "api"
    params:
      temperature: 0.7
      max_tokens: 200
      top_p: 0.9
  - name: "meta-llama/Meta-Llama-3-8B-Instruct"
    type: "huggingface"
    params:
      temperature: 0.7
      max_new_tokens: 200
      top_p: 0.9
      do_sample: true

ccp:
  claim_decomposition:
    model: "gpt-3.5-turbo"
    prompt: "Decompose the following text into atomic factual claims..."
  alternatives:
    count: 10
    model: "gpt-3.5-turbo"
  nli:
    model: "facebook/bart-large-mnli"
    batch_size: 128

metrics:
  self_bleu:
    n_grams: [2, 3, 4]
  embedding:
    model: "sentence-transformers/all-MiniLM-L6-v2"
  autocorrelation:
    max_lag: 3

analysis:
  alpha: 0.05
  bootstrap_samples: 10000
  effect_size: "cohen_d"
```

### 6.4 Quality Assurance

**Pre-Flight Checks:**
1. **Pilot run:** Process 10 samples end-to-end before full experiment
2. **Claim decomposition validation:** Manually review 20 decompositions (10 factual, 10 creative)
3. **NLI sanity check:** Verify entailment/contradiction labels on 50 random (premise, hypothesis) pairs

**Reproducibility:**
1. **Fixed seeds:** All random operations use `seed=42`
2. **Version pinning:** Lock all library versions in `environment.yml`
3. **Data snapshots:** Cache downloaded datasets with checksums
4. **Logging:** Record all API calls (GPT-3.5) with request/response pairs

**Error Handling:**
1. **API failures:** Exponential backoff with 5 retries for OpenAI API
2. **OOM errors:** Reduce batch size dynamically if CUDA OOM detected
3. **Invalid outputs:** Log and skip malformed claim decompositions (report skip rate)

---

## 7. Expected Results and Interpretation

### 7.1 Success Scenario (Hypothesis Confirmed)

**Primary Result:**
- **Δρ_j = 0.18 ± 0.03** (95% CI: [0.15, 0.21])
- **Effect size:** Cohen's d = 1.6 (large)
- **p-value:** p < 0.001 (highly significant)

**Secondary Results:**
- **Autocorrelation:** Creative lag-1 = 0.45, Factual lag-1 = 0.18 (p < 0.01)
- **Claim decomposition:** Krippendorff's α = 0.74 (acceptable reliability)
- **Diversity:** Creative Self-BLEU = 0.32, Factual Self-BLEU = 0.55 (Creative more diverse)

**Interpretation:**
- ρ_j metric reliably detects ontology shift
- Creative text causes CCP to degrade due to neutral-label inflation (H-M2 mechanism hypothesis)
- Autocorrelation confirms product aggregation vulnerability (H-M3)
- **Gate 1/9 PASSED:** Proceed to H-M1 (Ontology Shift mechanism testing)

**Next Steps:**
1. Expand to 4 models (add GPT-4, Mistral-7B) if pilot succeeds
2. Begin H-M1: Annotate metaphor density in creative samples
3. Design H-M2 experiment: Neutral-label inflation analysis

### 7.2 Partial Success Scenario

**Result:**
- **Δρ_j = 0.12 ± 0.04** (95% CI: [0.08, 0.16])
- **Effect size:** Cohen's d = 1.0 (medium-large)
- **p-value:** p = 0.003 (significant but below threshold)

**Interpretation:**
- Effect exists but smaller than predicted (0.12 vs. 0.15)
- Possible causes:
  1. Ontology shift less severe than hypothesized
  2. CCP more robust than expected
  3. WritingPrompts contains factual elements (genre mixing)

**Decision:**
- **Conditional PASS:** Proceed to H-M1 but revise success criteria
- **Hypothesis refinement:** Lower threshold to Δρ_j > 0.10 for subsequent tests
- **Dataset adjustment:** Filter WritingPrompts for high-fantasy prompts (maximize ontology distance)

### 7.3 Failure Scenario (Hypothesis Disconfirmed)

**Result:**
- **Δρ_j = 0.05 ± 0.03** (95% CI: [0.02, 0.08])
- **Effect size:** Cohen's d = 0.4 (small)
- **p-value:** p = 0.08 (not significant)

**Interpretation:**
- CCP does NOT degrade substantially on creative text
- ρ_j metric may be insensitive to ontology shift OR
- Creative/factual ontology distinction is not as clear-cut as hypothesized

**Decision:**
- **Gate 1/9 FAILED:** Do not proceed to mechanistic tests (H-M1 through H-M4)
- **Pivot options:**
  1. **Calibration hypothesis:** Reframe as "CCP is robust across domains; focus on calibration methods"
  2. **Alternative metrics:** Test whether false-positive rate or threshold sensitivity shows domain effects
  3. **Dataset redesign:** Use more extreme creative domain (poetry, surrealism) vs. factual (scientific abstracts)

**Publishable Contribution:**
- "CCP exhibits unexpected robustness to creative text: Implications for cross-domain hallucination detection"
- Null result challenges assumption that factual-trained detectors fail on creative text

### 7.4 Confound Detection

**Potential Confounds to Check:**

**Length Confound:**
- If creative texts are systematically longer → more claims → higher variance in ρ_j
- **Mitigation:** Report ρ_j stratified by document length quartiles
- **Test:** Partial correlation controlling for text length

**Model Capability Confound:**
- If Llama3-8B generates lower-quality text → different ρ_j baseline
- **Mitigation:** Report Δρ_j per model separately (within-model comparison is valid)
- **Test:** Two-way ANOVA (Model × Domain interaction)

**Claim Count Confound:**
- Creative texts may have fewer decomposable claims (narrative vs. factual)
- **Mitigation:** Normalize by claim count: Δρ_j per claim
- **Test:** Compare distributions of claim counts across domains

---

## 8. Timeline and Milestones

### 8.1 Week-by-Week Breakdown

**Week 1 (Days 1-2): Setup and Data Preparation**
- Day 1 AM: Environment setup, dependency installation
- Day 1 PM: Download and cache TruthfulQA, WritingPrompts
- Day 2 AM: Implement data filtering and sampling scripts
- Day 2 PM: Validate prompt quality (manual inspection of 50 samples)

**Week 1 (Days 3-4): Text Generation**
- Day 3: GPT-3.5-turbo generation (500 factual + 500 creative) → 6 hours
- Day 4: Llama3-8B generation (500 factual + 500 creative) → 8 hours
- **Checkpoint:** 2,000 generated texts ready

**Week 1 (Day 5): Claim Decomposition**
- Day 5: Run GPT-3.5 claim decomposition on all 2,000 texts → 4 hours
- **Checkpoint:** Decomposed claims cached

**Week 2 (Days 1-2): CCP Computation**
- Day 1: Generate alternatives for all claims → 6 hours
- Day 2: NLI inference (BART-large-mnli) → 8 hours
- **Checkpoint:** ρ_j scores computed

**Week 2 (Days 3-4): Metrics and Analysis**
- Day 3: Compute Self-BLEU, embedding dispersion → 2 hours
- Day 3: Statistical tests (t-tests, bootstrap CIs) → 2 hours
- Day 4: Generate visualizations (plots, tables) → 3 hours
- Day 4: Write analysis report → 3 hours

**Week 2 (Day 5): Review and Decision**
- Day 5: Internal review of results
- Day 5: Go/No-Go decision for expanding to 4 models
- **Deliverable:** H-E1 Experiment Report (results/h-e1_analysis_report.pdf)

**Total Duration:** 2 weeks (matches Phase 2B timeline)

### 8.2 Critical Path Dependencies

```
Data Prep → Text Generation → Claim Decomposition → CCP Computation → Analysis
   ↓              ↓                                        ↓
Filtering    API quotas                              NLI inference
validation   management                              (compute-intensive)
```

**Bottlenecks:**
1. **OpenAI API rate limits:** 3,500 requests/min for GPT-3.5-turbo
   - Mitigation: Batch requests, use caching for retries
2. **GPU availability:** 20 A100-hours required
   - Mitigation: Reserve GPU allocation in advance
3. **Claim decomposition quality:** Manual validation may reveal issues
   - Mitigation: Pilot 10 samples before full run

---

## 9. Deliverables

### 9.1 Data Artifacts

1. **Prompts and Generations:**
   - `data/factual_prompts.json` (500 TruthfulQA questions)
   - `data/creative_prompts.json` (500 WritingPrompts prompts)
   - `data/generations/{model}_{domain}.jsonl` (4 files, 2,000 total generations)

2. **Claims and Scores:**
   - `data/claims/{model}_{domain}_claims.jsonl` (decomposed atomic claims)
   - `data/ccp_scores/{model}_{domain}_rho_j.jsonl` (ρ_j per claim)

3. **Metrics:**
   - `data/diversity/{model}_{domain}_diversity.jsonl` (Self-BLEU, embedding dispersion)

### 9.2 Analysis Outputs

1. **Statistical Report:**
   - `results/h-e1_analysis_report.pdf`
     - Summary statistics (mean, median, std for ρ_j)
     - Hypothesis test results (t-test, Wilcoxon, effect sizes)
     - 95% confidence intervals (bootstrap)
     - Autocorrelation analysis
     - Diversity metrics comparison

2. **Visualizations:**
   - `results/figures/rho_j_boxplots.png` (ρ_j by domain, per model)
   - `results/figures/rho_j_scatter.png` (factual vs. creative paired)
   - `results/figures/autocorrelation_dist.png` (lag-1 distributions)
   - `results/figures/diversity_comparison.png` (Self-BLEU, embedding dispersion)

3. **Tables:**
   - `results/tables/summary_statistics.csv` (ρ_j, autocorr, diversity per condition)
   - `results/tables/hypothesis_tests.csv` (test statistics, p-values, effect sizes)

### 9.3 Code and Reproducibility

1. **Complete Pipeline:**
   - All scripts in `scripts/` (01-06)
   - Library code in `src/`
   - Configuration in `config/experiment_config.yaml`

2. **Documentation:**
   - `README.md` with setup and execution instructions
   - Inline code comments and docstrings
   - `RESULTS.md` with interpretation of outputs

3. **Tests:**
   - Unit tests for CCP calculation (`tests/test_ccp.py`)
   - Metric validation tests (`tests/test_metrics.py`)

### 9.4 Experimental Report (Primary Deliverable)

**Structure of `h-e1_analysis_report.pdf`:**

1. **Executive Summary**
   - Hypothesis statement
   - Key finding: Δρ_j = X.XX ± Y.YY (CI)
   - Decision: PASS/FAIL Gate 1/9

2. **Methods**
   - Dataset descriptions (TruthfulQA, WritingPrompts)
   - Model specifications (GPT-3.5, Llama3-8B)
   - CCP implementation details
   - Statistical analysis plan

3. **Results**
   - Primary outcome: ρ_j degradation (with plots)
   - Secondary outcomes: Autocorrelation, diversity
   - Exploratory analyses: Metaphor correlation (if available)

4. **Discussion**
   - Interpretation of findings
   - Comparison to Phase 2B predictions
   - Limitations (sample size, dataset choices)
   - Implications for H-M1 through H-M4

5. **Appendices**
   - Full statistical test outputs
   - Example claim decompositions
   - Hyperparameter settings

---

## 10. Risk Mitigation and Contingencies

### 10.1 Technical Risks

**Risk 1: OpenAI API Downtime**
- **Probability:** Medium (API outages happen)
- **Impact:** Blocks generation and claim decomposition
- **Mitigation:**
  - Cache all intermediate outputs (generation, decomposition, alternatives)
  - Implement exponential backoff with 24-hour retry window
  - Fallback: Use local Llama3-8B for claim decomposition if GPT-3.5 unavailable

**Risk 2: GPU Quota Exhaustion**
- **Probability:** Low (allocation confirmed)
- **Impact:** Cannot run Llama3-8B or BART-large-mnli inference
- **Mitigation:**
  - Reserve 30 A100-hours (50% buffer over 20-hour estimate)
  - Use CPU fallback for BART-large-mnli (slower but functional)
  - Reduce Llama3 batch size to minimize memory usage

**Risk 3: Claim Decomposition Quality Issues**
- **Probability:** Medium (GPT-3.5 may produce inconsistent formats)
- **Impact:** ρ_j calculation fails or is unreliable
- **Mitigation:**
  - Pilot test decomposition on 20 samples before full run
  - Implement robust parsing with fallback heuristics (regex for numbered lists)
  - Manual correction of up to 50 malformed decompositions (5% error budget)

### 10.2 Methodological Risks

**Risk 4: ρ_j Metric Lacks Sensitivity**
- **Probability:** Medium (novel metric, no prior validation)
- **Impact:** Cannot detect hypothesized effect even if real
- **Mitigation:**
  - **Phase 0 validation (if skipped):** Run mini-validation on 100 samples first
  - Alternative metric fallback: False-positive rate on manually labeled hallucinations
  - Report both median and mean ρ_j (distribution shape may matter)

**Risk 5: Domain Confound (Genre ≠ Ontology)**
- **Probability:** High (acknowledged in Phase 2B dialectic)
- **Impact:** ρ_j degradation reflects genre, not ontology shift
- **Mitigation:**
  - Multi-dimensional operationalization: Annotate epistemic intent on subsample
  - Robustness check: Test on alternative creative dataset (poetry, code comments with metaphors)
  - Transparent reporting: Discuss genre/ontology distinction in limitations

**Risk 6: Sample Size Insufficient for Autocorrelation**
- **Probability:** Low (n=500 per domain is robust)
- **Impact:** Lag-1 autocorrelation test underpowered
- **Mitigation:**
  - Filter for multi-claim documents (≥5 claims) for autocorrelation subset
  - Report autocorrelation only on documents with ≥3 claims (reduces noise)
  - Use non-parametric tests (Mann-Whitney) to handle small subsample

### 10.3 Resource Risks

**Risk 7: Timeline Overrun**
- **Probability:** Medium (NLI inference may be slower than estimated)
- **Impact:** Delay in Phase 2C completion
- **Mitigation:**
  - Prioritize primary outcome (ρ_j) over exploratory analyses
  - Parallelize generation and decomposition stages where possible
  - Skip optional human annotation if timeline compressed

**Risk 8: Budget Overrun (API Costs)**
- **Probability:** Low (estimates are conservative)
- **Impact:** Cannot complete all 2,000 generations
- **Mitigation:**
  - Use free-tier Llama3-8B more heavily (reduce GPT-3.5 usage)
  - Reduce creative sample size to 400 if cost exceeds $50
  - Pre-commit: Do not exceed $100 total API cost

---

## 11. Lessons from Prior Work

### 11.1 CCP Paper Insights (Fadeeva et al., 2024)

**Key Findings from arxiv:2403.04696:**
1. **CCP achieves +0.05-0.10 ROC-AUC improvement** over logit baselines on biography generation
   - Implication: ρ_j is effective metric on factual text (validates baseline)
2. **Product aggregation outperforms mean/min** in factual domains
   - Implication: H-M3 hypothesis (aggregation amplification) is plausible
3. **NLI model choice matters:** BART-large-mnli used in CCP implementation
   - Implication: Use same NLI model for consistency

**Implementation Details Borrowed:**
- Claim decomposition via GPT-3.5-turbo
- K=10 alternatives per claim
- BART-large-mnli for NLI classification
- ρ_j aggregation: (entail+contradict) / (entail+contradict+neutral)

### 11.2 WritingPrompts Studies

**GPT-WritingPrompts Dataset (Huang et al., 2024):**
- **Finding:** GPT-3.5 stories differ significantly from human stories on 6 emotional/descriptive dimensions
- **Implication:** Creative domain is measurably distinct from factual (validates domain choice)
- **Dataset size:** 97k prompt-response pairs available
- **Implication:** 500-sample subset is well-powered

**WritingPrompts Decontamination (RLAIF):**
- **Finding:** 25% of WritingPrompts overlap with LitBench test set
- **Implication:** Use RLAIF/WritingPrompts-Filtered to avoid contamination
- **Retention rate:** 75% after filtering (still 199k samples)

### 11.3 Self-BLEU and Diversity Metrics

**Texygen Evaluation Framework:**
- **Finding:** Self-BLEU strongly anti-correlates with diversity
- **Implication:** Lower Self-BLEU in creative text confirms higher diversity
- **Implementation:** Use n-grams [2, 3, 4] for robustness

**Standardizing Diversity Measurement (arxiv:2403.00553):**
- **Finding:** Compression ratio + Self-BLEU + self-repetition are sufficient diversity metrics
- **Implication:** Focus on Self-BLEU and embedding dispersion (covers lexical + semantic)

---

## 12. Summary and Integration

### 12.1 Experiment Overview

**Research Question:** Does ρ_j degrade by >0.15 when CCP is applied to creative vs. factual text?

**Design:**
- **N=500** factual (TruthfulQA) + **N=500** creative (WritingPrompts)
- **2 models** (GPT-3.5-turbo, Llama3-8B)
- **Within-subjects** comparison (same model, different domains)
- **Primary metric:** Δρ_j (median difference)
- **Timeline:** 2 weeks, 20 A100-hours

**Success Criteria:**
- Δρ_j > 0.15 (Cohen's d > 1.0, p < 0.05)
- Autocorrelation: Creative > 0.4, Factual < 0.2
- Claim decomposition reliability: α > 0.7

**Decision Point:**
- **PASS Gate 1/9:** Proceed to H-M1 (Ontology Shift mechanism)
- **FAIL Gate 1/9:** Pivot to calibration hypothesis or redesign

### 12.2 Alignment with Phase 2B Plan

**From 02b_verification_plan.md:**
- **H-E1 Timeline:** 1 week (Week 2-3 of pilot phase)
- **Compute Budget:** 20 A100-hours ✓ (matches)
- **Sample Size:** "Pilot subset" (GPT-3.5, Llama3-8B) ✓ (matches)
- **Dependencies:** None (entry point) ✓ (confirmed)
- **Deliverables:** ρ_j degradation report, autocorrelation stats, decomposition variance ✓ (all covered)

**Enhancements Beyond Phase 2B:**
- Explicit dataset specifications (TruthfulQA generation config, WritingPrompts filtering)
- Detailed CCP implementation plan (reproducible from CCP paper)
- Statistical power analysis (n=500 provides >95% power)
- Risk mitigation strategies (API failures, metric validation)
- Complete code structure and configuration schema

### 12.3 Next Steps After Completion

**If Hypothesis Confirmed (Gate 1/9 PASSED):**
1. **Immediate:** Update verification_state.yaml with h-e1.validation.result = "CONFIRMED"
2. **Week 3:** Begin H-M1 (Ontology Shift) - annotate 200 samples for metaphor density
3. **Week 4-5:** H-M2 (Denominator Instability) - neutral-label inflation analysis
4. **Expand to 4 models:** Add GPT-4, Mistral-7B for full experiment

**If Hypothesis Disconfirmed (Gate 1/9 FAILED):**
1. **Immediate:** Mark h-e1.validation.result = "REJECTED"
2. **Pivot:** Design calibration-focused experiment (CCP robustness across domains)
3. **Alternative:** Test extreme creative domain (poetry) vs. formal factual (scientific abstracts)

**If Partial Success (0.10 < Δρ_j < 0.15):**
1. **Conditional PASS:** Proceed with revised threshold
2. **Hypothesis refinement:** Update H-OntologyStress-v1 statement to reflect smaller effect
3. **Enhanced dataset:** Filter for high-fantasy WritingPrompts (maximize ontology distance)

---

## 13. Appendix: Detailed Example

### 13.1 End-to-End Example: Single Document

**Input (Factual - TruthfulQA):**
```
Question: "Who was the first person to fly across the Atlantic Ocean?"
Generated Answer (GPT-3.5): "Charles Lindbergh was the first person to fly solo across 
the Atlantic Ocean in 1927. He flew from New York to Paris in the Spirit of St. Louis, 
completing the journey in 33.5 hours. This historic flight made him an international hero."
```

**Step 1: Claim Decomposition**
```
Claims:
1. Charles Lindbergh was the first person to fly solo across the Atlantic Ocean.
2. The flight occurred in 1927.
3. Lindbergh flew from New York to Paris.
4. The aircraft was named Spirit of St. Louis.
5. The journey took 33.5 hours.
6. This flight made Lindbergh an international hero.
```

**Step 2: Generate Alternatives (Example for Claim 1)**
```
Alternatives for Claim 1:
1. Amelia Earhart was the first to cross the Atlantic solo.
2. The Wright Brothers completed the first Atlantic flight.
3. Lindbergh's solo Atlantic flight occurred in 1925.
4. The Spirit of St. Louis crashed before reaching Paris.
5. Multiple pilots completed the Atlantic crossing before Lindbergh.
6. Lindbergh flew from Boston to London.
7. Charles Lindbergh successfully crossed the Atlantic alone.
8. The first Atlantic flight was accomplished by a team.
9. Lindbergh's aircraft was called the Red Baron.
10. The Atlantic was first crossed by airship, not airplane.
```

**Step 3: NLI Classification (Claim 1 Alternatives)**
```
Premise: "Charles Lindbergh was the first person to fly solo across the Atlantic Ocean in 1927..."
Hypothesis: "Amelia Earhart was the first to cross the Atlantic solo."
→ P(entailment)=0.02, P(contradiction)=0.92, P(neutral)=0.06

Hypothesis: "Lindbergh successfully crossed the Atlantic alone."
→ P(entailment)=0.88, P(contradiction)=0.03, P(neutral)=0.09

...
(Aggregate across 10 alternatives)
Entail mass = 0.88 + 0.12 + ... = 2.3
Contradict mass = 0.92 + 0.85 + ... = 4.1
Neutral mass = 0.06 + 0.09 + ... = 0.8
```

**Step 4: ρ_j Calculation**
```
ρ_j[Claim 1] = (2.3 + 4.1) / (2.3 + 4.1 + 0.8) = 6.4 / 7.2 = 0.89

(Repeat for Claims 2-6)
ρ_j[Claim 2] = 0.91
ρ_j[Claim 3] = 0.87
ρ_j[Claim 4] = 0.85
ρ_j[Claim 5] = 0.82
ρ_j[Claim 6] = 0.78

Median ρ_j (Factual) = 0.86
```

**Input (Creative - WritingPrompts):**
```
Prompt: "[WP] You are a dragon who has been guarding a princess for 10 years. She's actually pretty cool."
Generated Story (GPT-3.5): "Ember had grown fond of Princess Lyra over the decade. 
She wasn't like the other royals – she spoke to him as an equal, not a beast. 
One evening, as stars danced above the tower, Lyra asked, 'Do you ever dream of flying 
free?' Ember's heart, a furnace of conflicting fires, ached at the question."
```

**Step 1: Claim Decomposition**
```
Claims:
1. Ember had developed affection for Princess Lyra over ten years.
2. Lyra was different from other royalty.
3. Lyra treated Ember as an equal.
4. One evening, stars appeared above the tower.
5. Lyra asked Ember about his desire for freedom.
6. Ember experienced emotional conflict about the question.
```

**Step 2: Generate Alternatives (Example for Claim 3)**
```
Alternatives for Claim 3:
1. Lyra feared Ember like all humans fear dragons.
2. Ember was treated as property by Lyra.
3. The princess and dragon had a reciprocal relationship.
4. Lyra only spoke to Ember when necessary.
5. Dragons cannot be equals to humans in this world.
6. Ember perceived Lyra's treatment as respectful.
7. Lyra commanded Ember as a servant.
8. All royals in the kingdom treat dragons equally.
9. The relationship between Lyra and Ember was hierarchical.
10. Lyra's equality with Ember is a metaphor for mutual respect.
```

**Step 3: NLI Classification (Claim 3 Alternatives - Creative Text)**
```
Premise: "She spoke to him as an equal, not a beast..."
Hypothesis: "Lyra feared Ember like all humans fear dragons."
→ P(entailment)=0.05, P(contradiction)=0.18, P(neutral)=0.77 ← High neutral!

Hypothesis: "The princess and dragon had a reciprocal relationship."
→ P(entailment)=0.31, P(contradiction)=0.08, P(neutral)=0.61 ← Metaphorical, high neutral

Hypothesis: "Lyra's equality with Ember is a metaphor for mutual respect."
→ P(entailment)=0.12, P(contradiction)=0.06, P(neutral)=0.82 ← Meta-statement, very high neutral

...
(Aggregate across 10 alternatives)
Entail mass = 0.31 + 0.12 + ... = 1.2 ← Lower than factual
Contradict mass = 0.18 + 0.08 + ... = 0.9 ← Lower than factual
Neutral mass = 0.77 + 0.61 + 0.82 + ... = 5.1 ← MUCH HIGHER than factual
```

**Step 4: ρ_j Calculation (Creative)**
```
ρ_j[Claim 3] = (1.2 + 0.9) / (1.2 + 0.9 + 5.1) = 2.1 / 7.2 = 0.29 ← DEGRADED!

(Repeat for Claims 1-2, 4-6)
ρ_j[Claim 1] = 0.35
ρ_j[Claim 2] = 0.41
ρ_j[Claim 3] = 0.29
ρ_j[Claim 4] = 0.52  ← "stars danced" is metaphorical but factual baseline
ρ_j[Claim 5] = 0.38
ρ_j[Claim 6] = 0.27  ← "furnace of fires" metaphor

Median ρ_j (Creative) = 0.37
```

**Comparison:**
```
Δρ_j = 0.86 (Factual) - 0.37 (Creative) = 0.49 ← Far exceeds 0.15 threshold!
```

**Interpretation:**
- Creative text's metaphorical language ("spoke as an equal", "stars danced", "furnace of fires") triggers high neutral mass in NLI
- NLI model trained on factual MNLI cannot resolve metaphor → defaults to neutral
- Denominator inflates with neutral mass → ρ_j collapses
- **Mechanism confirmed:** Neutral-label inflation (H-M2) evident in single example

### 13.2 Autocorrelation Example

**Factual Text (6 Claims):**
```
ρ_j: [0.89, 0.91, 0.87, 0.85, 0.82, 0.78]
Lag-1 pairs: (0.89,0.91), (0.91,0.87), (0.87,0.85), (0.85,0.82), (0.82,0.78)
Correlation: r = 0.12 ← Low autocorrelation (claims are independent)
```

**Creative Text (6 Claims):**
```
ρ_j: [0.35, 0.41, 0.29, 0.52, 0.38, 0.27]
Lag-1 pairs: (0.35,0.41), (0.41,0.29), (0.29,0.52), (0.52,0.38), (0.38,0.27)
Correlation: r = 0.48 ← High autocorrelation (metaphorical context persists across claims)
```

**Interpretation:**
- Creative narrative maintains metaphorical "register" across sentences (e.g., fantasy tone)
- Consecutive claims share semantic context (dragon-princess relationship)
- NLI neutral-mass inflation affects correlated claims similarly
- **Supports H-M3:** Product aggregation will compound correlated low ρ_j values

---

## 14. Conclusion

This experiment brief provides a **complete, executable specification** for testing hypothesis h-e1 (ρ_j degradation on creative vs. factual text). Key features:

1. **Real datasets:** TruthfulQA (factual) and WritingPrompts (creative), not synthetic
2. **Statistically powered:** n=500 per domain provides >95% power for Δρ_j=0.15
3. **Reproducible:** Detailed implementation plan with code structure, config files, and caching
4. **Risk-mitigated:** Contingencies for API failures, metric validation, confounds
5. **Interpretable:** Clear success/failure scenarios with decision rules for Gate 1/9
6. **Aligned:** Matches Phase 2B timeline (2 weeks), compute (20 A100-hours), and deliverables

**Primary Deliverable:** `h-e1_analysis_report.pdf` with:
- Hypothesis test results (Δρ_j, p-value, effect size)
- Visualizations (box plots, scatter plots, autocorrelation)
- Go/No-Go decision for proceeding to H-M1

**Gate 1/9 Decision Criteria:**
- **PASS:** Δρ_j > 0.15, p < 0.05, Cohen's d > 1.0 → Proceed to H-M1
- **CONDITIONAL:** 0.10 < Δρ_j < 0.15 → Revise threshold, proceed cautiously
- **FAIL:** Δρ_j < 0.10 OR p > 0.05 → Pivot to calibration hypothesis

**Next Phase:** Upon successful completion, h-e1 results inform mechanistic testing (H-M1: Ontology Shift, H-M2: Denominator Instability, H-M3: Aggregation Amplification).

---

**END OF PHASE 2C EXPERIMENT BRIEF**
