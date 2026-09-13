# PRD: H-E1 Conditional Independence of SE_N5 and min_logprob on TriviaQA

**Version:** 1.0  
**Date:** 2026-08-02  
**Author:** Anonymous  
**Hypothesis:** H-E1 (EXISTENCE / MUST_WORK)  
**stepsCompleted:** [PRD]

---

## 1. Executive Summary

This experiment verifies that Semantic Entropy (SE_N5) and minimum token log-probability (min_logprob) are empirically conditionally independent uncertainty signals when predicting correctness of Llama-3.1-8B-Instruct on TriviaQA. If independence holds (Pearson |r| < 0.7 AND partial R² ≥ 0.02), both signals can be meaningfully combined in the YouRA uncertainty quantification pipeline. This is an EXISTENCE (PoC) experiment — no model training, single seed, 2500 evaluation samples.

**Gate:** MUST_WORK — both thresholds must pass for the hypothesis chain to continue.

---

## 2. Problem Statement

Before combining SE and min_logprob as complementary uncertainty features, we must establish they capture distinct information. If they are highly correlated (|r| ≥ 0.7), SE is effectively a reparameterization of log-probability and adds no value. The conditional logistic regression partial R² test confirms SE contributes discriminative signal above and beyond min_logprob in predicting correctness.

---

## 3. Functional Requirements

### FR-1: Dataset Loading
- Load TriviaQA `rc.nocontext` validation split from HuggingFace (`mandarjoshi/trivia_qa`)
- Shuffle with seed=42, select first 2500 examples
- Extract `question` field as prompt; `answer.aliases` + `answer.normalized_aliases` for correctness

### FR-2: Stochastic Generation (N=5) for SE
- Run Llama-3.1-8B-Instruct with temperature=0.7, top_p=0.95, max_new_tokens=50
- Generate 5 samples per prompt (2500 prompts × 5 = 12,500 total generations)
- Store all 5 responses per prompt for SE clustering

### FR-3: Greedy Decode for min_logprob
- Run Llama-3.1-8B-Instruct with temperature=0.0 (greedy) on same 2500 prompts
- Enable `output_scores=True` in HuggingFace `generate()` call
- Extract per-token log-probabilities; compute min_logprob = min(token_logprobs)
- Fail fast if `output_scores` is unavailable

### FR-4: SE_N5 Computation
- Load NLI model: `cross-encoder/nli-deberta-v3-small` (lightweight) or `microsoft/deberta-large-mnli` (paper-exact)
- Implement bidirectional NLI entailment clustering: `get_semantic_ids()` (jlko/semantic_uncertainty reference)
- Non-strict mode: equivalent if no contradiction AND not both neutral
- Compute cluster assignment entropy: `SE = -sum(p_k * log(p_k))`

### FR-5: LM-as-a-Judge Correctness Labels
- Use cross-model judge: Qwen-2.5-7B or GPT-4o-mini
- Prompt: "Is the following answer correct for the question? Answer YES or NO."
- Apply to greedy decode output (single answer per prompt)
- Produce binary labels: `correctness ∈ {0, 1}` for 2500 prompts

### FR-6: Statistical Independence Tests
- Pearson correlation: `scipy.stats.pearsonr(se_scores, min_logprob_scores)`
- Spearman circularity check: `scipy.stats.spearmanr(se_scores, lm_judge_correctness)`
- Conditional logistic regression (full model): `logit(h=1) ~ min_logprob + SE + L + SE×min_logprob`
- Conditional LR (reduced model): `logit(h=1) ~ min_logprob + L`
- Partial R² (McFadden-style): `1 - (ll_full / ll_reduced)`

### FR-7: Gate Evaluation
- Pass condition: `abs(pearson_r) < 0.7 AND partial_r2_se >= 0.02`
- ABANDON if `|r| > 0.85` (SE is reparameterization of log-prob)
- EXPLORE (N=10 ablation) if `0.7 < |r| < 0.85 OR partial_r2 < 0.02`
- Report LRT p-value for partial R²

### FR-8: Mechanism Activation Verification
- Assert `np.var(se_scores) > 0.01` (SE non-degenerate)
- Assert `np.all(min_logprob_scores < 0)` (log-probs are negative)
- Assert `len(se_scores) == len(min_logprob_scores) == 2500`

### FR-9: Visualization
- Required: Bar chart — |r|(SE, min_logprob) vs threshold 0.7; partial R²(SE) vs threshold 0.02
- Additional: Scatter plot SE_N5 vs min_logprob (2500 points, colored by correctness)
- Additional: Correlation matrix heatmap [SE_N5, min_logprob, response_length, correctness]
- Additional: LR coefficient bar chart with 95% CI
- Save all figures to `docs/youra_research/h-e1/figures/`

### FR-10: N=10 Ablation (EXPLORE branch only)
- If gate not satisfied with N=5 → re-run SE with N=10 samples
- Requires additional 2500×5 stochastic generations (total 25,000 extra)
- Re-run full statistical pipeline with SE_N10

---

## 4. Data Specification

| Field | Value |
|-------|-------|
| Dataset | TriviaQA |
| HuggingFace ID | `mandarjoshi/trivia_qa` |
| Config | `rc.nocontext` |
| Split | `validation` |
| Sample size | 2500 (shuffled seed=42 from 11,313 total) |
| Download method | Auto (HuggingFace datasets library) |
| Input field | `question` |
| Label fields | `answer.aliases`, `answer.normalized_aliases` |

**Note:** TriviaQA auto-downloads via HuggingFace datasets — NO manual download task needed.

---

## 5. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Reproducibility | Fixed seed=42 for dataset shuffle; fixed model checkpoint |
| Single seed | EXISTENCE PoC — no multi-seed averaging required |
| Compute | GPU required for Llama-3.1-8B inference; DeBERTa-MNLI runs on CPU or GPU |
| Correctness check | N=2500 validated at startup; fail fast if truncated |
| No training | Pure inference + statistical tests — zero gradient computation |
| Judge cross-model | Judge must differ from generator model family |

---

## 6. Success Criteria

| Criterion | Threshold | Source |
|-----------|-----------|--------|
| Pearson \|r\|(SE, min_logprob) | < 0.7 | Phase 2B gate spec |
| Partial R²(SE) in conditional LR | ≥ 0.02 (LRT p < 0.05) | Phase 2B gate spec |
| ρ(SE, LM-judge) | < 0.4 (circularity guard) | Phase 2C spec |
| Code runs without error | TRUE | PoC requirement |
| mechanism_activated() | All indicators TRUE | Phase 2C spec |

**Expected performance baseline:** Pearson r ∈ [0.4, 0.7] based on "The First Token Knows" (arxiv 2605.05166) finding r=0.54–0.76 for first-token confidence vs semantic agreement on Llama-3.1-8B + TriviaQA.

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0
transformers>=4.40
datasets>=2.18
scipy>=1.11
scikit-learn>=1.3
numpy>=1.24
matplotlib>=3.7
seaborn>=0.12
tqdm>=4.65
pyyaml>=6.0
```

### 7.2 External Repositories (Reference Only)

| Repo | URL | Purpose |
|------|-----|---------|
| jlko/semantic_uncertainty | https://github.com/jlko/semantic_uncertainty | SE clustering reference implementation |
| BuffaloTechRider/zero-shot-llm-confidence-estimation | https://github.com/BuffaloTechRider/zero-shot-llm-confidence-estimation | min_logprob + TriviaQA AUROC reference |
| cvs-health/uqlm | https://cvs-health.github.io/uqlm | min_token_probability formal definition |

### 7.3 Model Checkpoints

| Model | HuggingFace ID | Purpose |
|-------|---------------|---------|
| Generator | `meta-llama/Llama-3.1-8B-Instruct` | Stochastic (N=5) + greedy generation |
| NLI Judge | `cross-encoder/nli-deberta-v3-small` | SE clustering (primary, lightweight) |
| NLI Judge (alt) | `microsoft/deberta-large-mnli` | SE clustering (paper-exact) |
| LM Judge | `Qwen/Qwen2.5-7B-Instruct` | Correctness labeling |

---

## 8. Out of Scope

- Model training or fine-tuning
- Multi-seed experiments (single seed sufficient for EXISTENCE PoC)
- Hyperparameter search
- Deployment or serving
- Comparison with other uncertainty methods (belongs to H-M1+)
- Results beyond TriviaQA (generalization study out of scope for H-E1)
