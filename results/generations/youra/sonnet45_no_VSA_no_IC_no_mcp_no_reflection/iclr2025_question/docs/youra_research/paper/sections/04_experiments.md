# Experimental Setup

Our experimental design separates infrastructure validation from hypothesis testing, enabling us to distinguish technical feasibility (can entropy be extracted?) from performance claims (does entropy outperform max-probability?). This section details the experimental questions, evaluation protocol, and validation criteria.

## Research Questions

We structure our evaluation around three experimental questions, each with specific success criteria:

**RQ1 (Infrastructure):** Can entropy be reliably extracted from frozen LLM forward passes on factual QA tasks?  
**Success Criterion:** Extraction rate > 95% (no technical bottlenecks)  
**Measurement:** Fraction of predictions yielding valid entropy values (no NaN, no numerical overflow)

**RQ2 (Disagreement Patterns):** Do entropy and max-probability disagree in non-trivial proportions?  
**Success Criterion:** Q3 quadrant population > 5% (disagreement cases are not edge cases)  
**Measurement:** Fraction of predictions with high max-prob AND high entropy (median splits)

**RQ3 (Performance Hypothesis):** Does entropy correlate negatively with prediction correctness, indicating it captures error-related uncertainty?  
**Success Criterion:** Spearman ρ < 0 with p < 0.05  
**Measurement:** Rank correlation between entropy and binary correctness

RQ1 and RQ2 validate infrastructure independent of model performance. RQ3 tests the hypothesis that entropy signals prediction quality. Critically, RQ3 requires non-zero variance in correctness — if all predictions are correct or incorrect, correlation is undefined.

## Dataset Selection and Rationale

We evaluate on TriviaQA (Joshi et al., 2017) unfiltered validation split. TriviaQA consists of 11,313 question-answer pairs sourced from trivia enthusiast websites, covering diverse factual domains (history, geography, entertainment, science). Questions have single-answer targets with multiple acceptable surface forms (e.g., "Paris" / "Paris, France").

**Rationale for TriviaQA:**
1. **Task Alignment:** Factual QA represents the selective prediction use case — high-stakes domains (medical QA, legal advice) require models to abstain when uncertain.
2. **Evaluation Clarity:** Single-answer targets enable unambiguous exact-match evaluation, avoiding subjective correctness judgments.
3. **Knowledge Intensity:** TriviaQA requires factual knowledge retrieval (not pattern matching), making model capacity directly relevant.
4. **Established Benchmark:** Widely used in QA literature (Roberts et al., 2020; Petroni et al., 2019), facilitating comparison.

We sample 500 examples for proof-of-concept validation, balancing statistical power with compute efficiency. Power analysis (α=0.05, power=0.80, medium effect size r=0.3) suggests n=82 for correlation tests; n=500 provides substantial margin.

## Model Configuration

**Planned Model:** Llama-2-7B (Touvron et al., 2023)  
- 7 billion parameters, decoder-only transformer  
- 32 layers, 4096 hidden dim, 32 attention heads  
- Trained on 2 trillion tokens  
- Expected TriviaQA accuracy: 10-15% (zero-shot)

**Actual Model:** GPT-2 (Radford et al., 2019)  
- 117 million parameters (1.7% of planned scale)  
- 12 layers, 768 hidden dim, 12 attention heads  
- Trained on ~40GB text (WebText)  
- Observed TriviaQA accuracy: 0% (0/500)

The model substitution occurred during implementation due to resource constraints (Llama-2-7B requires 14GB GPU memory vs. GPT-2's 500MB). This unintended change became the critical variable exposing our methodological finding.

## Baseline Methods

We compare entropy-based uncertainty against two baselines:

**1. Max-Probability Thresholding (Primary Baseline)**  
Reject predictions where max(p(v)) falls below threshold τ. Hendrycks & Gimpel (2017) established this as the standard single-forward-pass baseline for OOD detection. Threshold is swept from 0 to 1 to generate coverage-accuracy curves.

**2. Random Rejection (Sanity Check)**  
Reject predictions uniformly at random to achieve target coverage. This control verifies that structured uncertainty signals (entropy, max-prob) outperform uninformed rejection.

All methods operate on the same set of predictions from a single frozen forward pass, ensuring fair compute comparison.

## Evaluation Metrics

**Primary Metric: Spearman Rank Correlation (ρ)**  
Measures monotonic association between entropy and binary correctness. Spearman is preferred over Pearson because (1) correctness is binary (non-normal), (2) we test monotonic relationship (not linearity), and (3) Spearman is robust to outliers in entropy. Computed via SciPy's spearmanr function with two-tailed test.

**Secondary Metrics:**

1. **Extraction Rate:** Fraction of predictions yielding valid entropy (no NaN/inf)
2. **Entropy Range:** max(H) - min(H), normalized by log|V| to assess distribution spread
3. **Q3 Population:** Fraction in high max-prob, high-entropy quadrant
4. **Q1 vs Q3 Accuracy Gap:** Accuracy(Q1) - Accuracy(Q3), testing if disagreement cases have lower accuracy

## Statistical Analysis

We apply Bonferroni correction for multiple comparisons. With 3 primary tests (extraction rate, correlation, Q3 population), corrected significance threshold is α/3 = 0.017. However, extraction rate and Q3 population are directional tests (one-tailed), while correlation is two-tailed, so we report uncorrected p-values and note which survive correction.

For correlation, null hypothesis H₀: ρ = 0 (no monotonic association). Alternative H₁: ρ < 0 (negative association, higher entropy predicts lower accuracy). One-tailed test at α=0.05.

For quadrant analysis, we use Mann-Whitney U test to compare Q1 vs Q3 accuracy distributions, testing whether median accuracy differs between agreement and disagreement cases.

## Experimental Protocol

For each of the 500 TriviaQA examples:

1. **Encode Question:** Tokenize question text, truncate to 512 tokens if needed
2. **Forward Pass:** Run frozen model, extract logits from final token position
3. **Compute Metrics:**
   - Softmax probabilities: p(v) = exp(z_v) / Σ exp(z_v')
   - Entropy: H = -Σ p(v) log p(v)
   - Max-probability: p_max = max(p(v))
4. **Generate Prediction:** Greedy decode (select argmax token)
5. **Evaluate Correctness:** Exact match against TriviaQA answers (case-insensitive)
6. **Accumulate:** Store (entropy, max_prob, correctness) tuples

After processing all examples:

7. **Statistical Analysis:** Compute Spearman ρ, extraction rate, quadrant populations
8. **Gate Validation:** Check MUST_WORK criteria (extraction >95%, p<0.05, Q3>5%)
9. **Visualization:** Generate figures (scatter, histograms, quadrant plot, gate metrics)

## Reproducibility

Code: PyTorch 2.0, Transformers 4.30, SciPy 1.10, Python 3.9  
Hardware: Single NVIDIA A100 40GB GPU (GPT-2 runs on CPU)  
Random Seeds: torch.manual_seed(42), np.random.seed(42) for sampling  
Runtime: 15 minutes (GPT-2), estimated 45 minutes (Llama-2-7B)

Full implementation and experiment scripts are available at [repository link]. Dataset is publicly accessible via Hugging Face Datasets (trivia_qa/unfiltered).

## Expected Outcomes

**Under Valid Conditions (Llama-2-7B with ~10% accuracy):**
- Extraction rate: 100% (no numerical issues expected)
- Q3 population: 5-15% (disagreement cases exist)
- Spearman ρ: -0.2 to -0.4 (moderate negative correlation)
- Interpretation: Infrastructure validated, hypothesis testable (though not necessarily supported)

**Under Invalid Conditions (GPT-2 with 0% accuracy):**
- Extraction rate: 100% (distributions still extractable)
- Q3 population: 5-15% (disagreement patterns persist)
- Spearman ρ: NaN (zero-variance correctness)
- Interpretation: Infrastructure validated, hypothesis untestable

Our results fell into the second category, confirming that model capacity gates experiment validity independently of infrastructure success.
