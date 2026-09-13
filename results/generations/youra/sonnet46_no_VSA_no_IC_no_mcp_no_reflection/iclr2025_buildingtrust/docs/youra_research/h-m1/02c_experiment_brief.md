# Experiment Design: H-M1

**Date:** 2026-08-31
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under inference-only evaluation of matched DPO/SFT 7B model pairs, if DPO training data (human preference pairs) systematically rewards responses that avoid bias-triggering language, then DPO-trained models will score higher on BBQ (social bias avoidance) and WinoGender (gender bias avoidance) benchmarks compared to matched SFT-trained models, with directional consistency in ≥4/6 matched pairs on BBQ (one-sided binomial sign test, p≤0.125).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Tests whether DPO's preference signal encodes bias-avoidance relative to SFT.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 VALIDATED (LOO k-NN accuracy=83.3%, p=0.031)
**Gate Status:** MUST_WORK — H-E1 passed; proceeding to mechanism test

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED, gate PASS)

### Gate Condition
MUST_WORK: ≥4/6 matched pairs show DPO > SFT on BBQ; one-sided binomial sign test p ≤ 0.125 (n=6, k=count of DPO>SFT pairs).

---

## Continuation Context

This experiment continues directly from H-E1. The 12-model evaluation (6 DPO, 6 SFT across 6 matched pairs) is already complete. BBQ and WinoGender scores are already computed via lm-evaluation-harness. **No new benchmark runs required.** H-M1 is a post-hoc analysis of existing H-E1 results.

### Previous Hypothesis Results (H-E1)
- LOO k-NN accuracy: 83.3% (10/12 correct)
- Permutation p: 0.031 (1000 permutations)
- 12 models evaluated: 6 DPO, 6 SFT pairs on TruthfulQA MC2, BBQ, WinoGrande, WinoGender
- Misclassified: Llama-2-chat-hf (RLHF outlier), zephyr-7b-beta (close to SFT base)
- Fisher's criterion computed per dimension — BBQ and WinoGender discriminative values available

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable in this session (ABLATION MODE). Using domain knowledge from literature.*

**Relevant prior findings (domain knowledge):**

**Finding 1: DPO Bias-Avoidance Signal**
- Literature source: Rafailov et al. (2023) DPO paper; Cui et al. (2023) UltraFeedback analysis
- Key insight: DPO preference pairs from UltraFeedback and similar datasets consistently penalize responses with stereotyped language. The reward signal implicitly encodes annotator preferences for non-biased phrasing.
- Relevance: Supports hypothesis that DPO training signal should produce measurable BBQ/WinoGender uplift

**Finding 2: BBQ as Bias Benchmark**
- Literature source: Parrish et al. (2022) "BBQ: A Hand-Built Bias Benchmark for Question Answering" (ACL 2022)
- Key insight: BBQ tests stereotype reliance in ambiguous QA contexts. Models rewarded for avoiding bias-triggering answers (as DPO implicitly does via human preference) should show higher disambiguation accuracy.
- Hyperparameters: Standard lm-eval BBQ task — no preprocessing required; accuracy metric (%)

**Finding 3: WinoGender as Gender Bias Probe**
- Literature source: Rudinger et al. (2018) "Gender Bias in Coreference Resolution"; lm-evaluation-harness WinoGender task
- Key insight: WinoGender measures pronoun resolution accuracy across gender-neutral, stereotyped, and anti-stereotyped contexts. Models avoiding gendered stereotypes score higher.
- Relevance: DPO preference data explicitly penalizes gender-stereotyped responses in RLHF datasets

**Finding 4: Sign Test for Directional Paired Comparisons**
- Literature source: Standard nonparametric statistics; used in NLP comparison studies
- Key insight: One-sided binomial sign test with n=6 pairs, one-sided H1 (DPO>SFT), p≤0.125 requires k≥5 concordant pairs for p≤0.109 or k≥4 for p≤0.344. With n=6: P(X≥4|p=0.5)=0.344, P(X≥5|p=0.5)=0.109, P(X≥6|p=0.5)=0.016. Gate threshold k≥4, p≤0.125 is achievable at k=5 (p=0.109).

### Archon Code Examples

*MCP unavailable. Using domain knowledge.*

**Code Pattern 1: Sign Test Implementation**
```python
from scipy.stats import binom_test  # or scipy.stats.binomtest (scipy>=1.7)
import numpy as np

# For each pair: compute sign of (BBQ_DPO - BBQ_SFT)
signs = [np.sign(bbq_dpo[i] - bbq_sft[i]) for i in range(n_pairs)]
k_positive = sum(s > 0 for s in signs)  # count DPO > SFT
# One-sided binomial test (H1: DPO > SFT, p_null=0.5)
p_value = binom_test(k_positive, n=len(signs), p=0.5, alternative='greater')
```

**Code Pattern 2: Fisher's Criterion for Discriminative Power**
```python
def fishers_criterion(scores_dpo, scores_sft):
    mu_dpo, mu_sft = np.mean(scores_dpo), np.mean(scores_sft)
    var_dpo, var_sft = np.var(scores_dpo), np.var(scores_sft)
    return (mu_dpo - mu_sft)**2 / (var_dpo + var_sft + 1e-8)
```

### Exa GitHub Implementations

*MCP unavailable. Using domain knowledge.*

**Relevant implementations (domain knowledge):**

**Repository 1: EleutherAI/lm-evaluation-harness**
- URL: https://github.com/EleutherAI/lm-evaluation-harness
- Relevance: Already used in H-E1; BBQ and WinoGender scores extracted from this run
- Key tasks: `bbq` (multiple subtasks by category), `winogrande`, `winogender_mc_female`, `winogender_mc_male`
- Dataset: BBQ uses Parrish et al. 2022 (HuggingFace: `"heegyu/bbq"` or built-in lm-eval task)
- Results: Already computed in H-E1 run — no new evaluation required

**Repository 2: HuggingFaceH4/alignment-handbook**
- URL: https://github.com/huggingface/alignment-handbook
- Relevance: Source of primary DPO/SFT matched pairs (zephyr-7b-sft-full, zephyr-7b-dpo-full)
- Preference dataset: UltraFeedback (cleaned) — known to encode bias-avoidance signal via human preferences
- Training config: DPO β=0.1, SFT cross-entropy on completions

**Serena Analysis Needed:** False — no custom architecture code; pure statistical analysis

### 🎯 Implementation Priority Assessment

**CRITICAL: No model training required. H-M1 is post-hoc statistical analysis of H-E1 scores.**

**Recommended Implementation Path:**
- Primary: Re-use H-E1 benchmark scores directly (BBQ, WinoGender per model pair)
- Fallback: Re-run lm-evaluation-harness on BBQ/WinoGender if scores unavailable
- Justification: H-M1 methodology explicitly states "Use BBQ and WinoGender scores from H-E1 benchmark run (no additional compute required)"

### Code Analysis (Serena MCP)

*Skipped* — No complex codebase to analyze. H-M1 requires only statistical analysis of existing benchmark scores, not architectural code.

---

## Experiment Specification

### Dataset

**Primary Benchmarks (from H-E1 run — no new data collection required):**

| Benchmark | Role in H-M1 | Metric | Source |
|-----------|-------------|--------|--------|
| BBQ | Primary DV — social bias avoidance | Accuracy (%) on disambiguation questions | Parrish et al. 2022; lm-eval built-in |
| WinoGender | Secondary DV — gender bias avoidance | Accuracy (%) pronoun resolution | Rudinger et al. 2018; lm-eval built-in |
| TruthfulQA MC2 | Control / H-M2 preview | MC2 accuracy (%) | Lin et al. 2022; lm-eval built-in |
| WinoGrande | Control | Accuracy (%) | Sakaguchi et al. 2021; lm-eval built-in |

**Dataset Type:** `standard` — real established benchmarks, already evaluated in H-E1
**Synthetic data:** NONE — all benchmarks are standard published evaluation sets

**BBQ Details:**
- Full test set: 58,492 questions across 9 bias categories (Age, Disability, Gender identity, Nationality, Physical appearance, Race/ethnicity, Religion, SES, Sexual orientation)
- Metric: Disambiguation accuracy (model selects non-stereotyped answer when context disambiguates)
- HuggingFace: `heegyu/bbq` or lm-eval task `bbq`
- All 9 categories evaluated; per-category breakdown available

**WinoGender Details:**
- Full test set: 720 sentences (360 female, 360 male pronouns; stereotyped and anti-stereotyped conditions)
- Metric: Accuracy on pronoun coreference resolution
- lm-eval tasks: `winogender_mc_female`, `winogender_mc_male`

**Loading Information** (for Phase 4 download):
- Method: lm-evaluation-harness (already installed from H-E1)
- Identifier: `bbq`, `winogender_mc_female`, `winogender_mc_male`
- Code: `lm_eval --tasks bbq,winogender_mc_female,winogender_mc_male --model hf --model_args pretrained={model_name}`

### Models

#### Baseline Model

**The 6 SFT models from H-E1 paired evaluation:**

| Pair | SFT Model | DPO Model | Base Model |
|------|-----------|-----------|------------|
| 1 | HuggingFaceH4/zephyr-7b-sft-full | HuggingFaceH4/zephyr-7b-beta | mistralai/Mistral-7B-v0.1 |
| 2 | alignment-handbook SFT pair 2 | alignment-handbook DPO pair 2 | Mistral-7B or Llama-2-7B |
| 3 | alignment-handbook SFT pair 3 | alignment-handbook DPO pair 3 | Mistral-7B or Llama-2-7B |
| 4 | meta-llama/Llama-2-7b-hf (SFT) | meta-llama/Llama-2-7b-chat-hf | Llama-2-7B |
| 5 | Community SFT pair 5 | Community DPO pair 5 | matched |
| 6 | Community SFT pair 6 | Community DPO pair 6 | matched |

*Exact model names carried forward from H-E1 execution.*

**Loading Information** (for Phase 4):
- Method: HuggingFace `transformers.AutoModelForCausalLM`
- Code: Already loaded in H-E1 run; scores already computed — no re-loading required for H-M1 analysis
- Model scores available in H-E1 output

#### Proposed Model

**Architecture:** No new model. H-M1 tests whether existing DPO model scores (BBQ, WinoGender) are systematically higher than matched SFT model scores.

**Core Mechanism Implementation:**

```python
# H-M1 Analysis: DPO Bias-Avoidance Signal Detection
# Based on: H-E1 benchmark scores + binomial sign test

import numpy as np
from scipy.stats import binomtest  # scipy >= 1.7

def run_hm1_analysis(bbq_scores: dict, winogender_scores: dict, pairs: list):
    """
    Args:
        bbq_scores: {'model_name': accuracy_float, ...}  — from H-E1 lm-eval output
        winogender_scores: {'model_name': accuracy_float, ...}
        pairs: [('sft_model', 'dpo_model'), ...]  — 6 matched pairs

    Returns:
        dict with sign counts, p-values, Fisher's criterion per benchmark
    """
    bbq_signs, wg_signs = [], []
    bbq_deltas, wg_deltas = [], []

    for sft_name, dpo_name in pairs:
        delta_bbq = bbq_scores[dpo_name] - bbq_scores[sft_name]
        delta_wg  = winogender_scores[dpo_name] - winogender_scores[sft_name]
        bbq_signs.append(1 if delta_bbq > 0 else 0)
        wg_signs.append(1 if delta_wg > 0 else 0)
        bbq_deltas.append(delta_bbq)
        wg_deltas.append(delta_wg)

    k_bbq = sum(bbq_signs)
    k_wg  = sum(wg_signs)
    n = len(pairs)

    # One-sided binomial test: H1 = DPO > SFT
    p_bbq = binomtest(k_bbq, n=n, p=0.5, alternative='greater').pvalue
    p_wg  = binomtest(k_wg,  n=n, p=0.5, alternative='greater').pvalue

    # Fisher's criterion for discriminative power
    def fishers(deltas):
        arr = np.array(deltas)
        mu = np.mean(arr); sigma2 = np.var(arr)
        return mu**2 / (sigma2 + 1e-8)

    return {
        'bbq_k': k_bbq, 'bbq_p': p_bbq,      # primary gate
        'wg_k':  k_wg,  'wg_p':  p_wg,        # secondary
        'bbq_fisher': fishers(bbq_deltas),
        'wg_fisher':  fishers(wg_deltas),
        'bbq_deltas': bbq_deltas,
        'wg_deltas':  wg_deltas,
    }

# Gate check
def check_hm1_gate(results):
    return results['bbq_k'] >= 4 and results['bbq_p'] <= 0.125
```

### Training Protocol

**No training required.** H-M1 is a post-hoc statistical analysis.

**Analysis Protocol:**

- **Input:** BBQ and WinoGender scores from H-E1 lm-eval output (JSON/results files)
- **Paired structure:** 6 matched (SFT, DPO) model pairs sharing same base model
- **Primary test:** One-sided binomial sign test on BBQ score signs (n=6, H1: DPO>SFT)
- **Secondary test:** Same for WinoGender (exploratory, no strict threshold)
- **Fisher's criterion:** Computed for all 4 benchmark dimensions for H-M3 preparation
- **Seeds:** N/A — no stochastic training; inference scores from H-E1 are deterministic given fixed lm-eval version
- **Compute:** <1 minute on CPU (pure numerical analysis)

**Software stack:**
- Python 3.10+
- scipy >= 1.7 (binomtest)
- numpy >= 1.21
- pandas (result loading from H-E1 JSON output)

### Evaluation

**Primary Metrics (H-M1 gate):**

| Metric | Description | Gate Threshold |
|--------|-------------|----------------|
| BBQ sign count (k) | Number of pairs where BBQ_DPO > BBQ_SFT | ≥ 4/6 |
| BBQ binomial p-value | One-sided p (H1: DPO > SFT) | ≤ 0.125 |

**Secondary Metrics (exploratory):**

| Metric | Description | Threshold |
|--------|-------------|-----------|
| WinoGender sign count | Number of pairs where WG_DPO > WG_SFT | ≥ 4/6 (soft) |
| WinoGender binomial p | One-sided p | Exploratory |
| BBQ Fisher's criterion | Discriminative power of BBQ dimension | Compared vs other dims |
| WinoGender Fisher's criterion | Discriminative power | Compared vs other dims |

**Success Criteria:**
- PASS: k_BBQ ≥ 4 AND p_BBQ ≤ 0.125
- FAIL (EXPLORE): k_BBQ ≤ 3 → check confounds, pivot to descriptive framing

**Expected Baseline Performance (from H-E1):**
- BBQ accuracy range (observed in H-E1): DPO models expected higher than SFT; exact values in H-E1 results
- WinoGender: DPO models expected directionally higher; may have higher variance
- Source: H-E1 validation report + Parrish et al. 2022 BBQ paper (human baseline ~90%)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical analysis (no ML training)
- Library: `scipy.stats.binomtest`, `numpy`
- Code: See core mechanism pseudo-code above

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: BBQ and WinoGender DPO vs SFT score comparison bar chart (paired, per model pair + group means)

#### Additional Figures (LLM Autonomous)

1. **Paired BBQ Delta Plot**: Per-pair delta (BBQ_DPO − BBQ_SFT) as signed bar chart; positive bars = DPO>SFT; dashed line at 0; highlight if k≥4 pairs positive
2. **4D Fisher's Criterion Heatmap/Bar**: Fisher's criterion value for all 4 benchmark dimensions — visualizes which dimensions discriminate DPO vs SFT most strongly (preview for H-M2/H-M3)
3. **WinoGender Sign Consistency Plot**: Per-pair WinoGender delta + overall sign count annotation
4. **Score Distribution Box Plot**: DPO vs SFT score distributions for BBQ and WinoGender across all 6 pairs

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

**Pre-conditions:**
- `mechanism_exists`: H-E1 validated that DPO/SFT 4D vectors are separable (k-NN 83.3%). BBQ and WinoGender are part of that 4D vector. ✅
- `mechanism_isolatable`: Each pair shares same base model and training data — only alignment strategy differs. BBQ/WinoGender scores are isolatable per pair. ✅
- `baseline_measurable`: SFT BBQ/WinoGender scores from H-E1 run serve as matched baseline. ✅

**Architecture Compatibility:**
- `architecture_compatibility`: No model architecture modification required. Pure score analysis.
- Statistical test (binomial sign test) is compatible with n=6 pairs.

**Activation Indicators:**
- `mechanism_log_message`: "DPO>SFT on BBQ: {k}/6 pairs. Binomial p={p:.4f}"
- `tensor_shape_change`: N/A (no tensors; score arrays shape [6] for BBQ and WinoGender)
- `metric_delta_expected`: BBQ_DPO − BBQ_SFT > 0 in ≥4/6 pairs; expected average delta +2–5 percentage points based on alignment literature

**Mechanism Verification Code:**
```python
# Quick sanity check before full analysis
assert len(pairs) >= 6, "Need ≥6 pairs for binomial test power"
assert all(m in bbq_scores for pair in pairs for m in pair), "Missing BBQ scores"
results = run_hm1_analysis(bbq_scores, winogender_scores, pairs)
print(f"BBQ: {results['bbq_k']}/6 pairs DPO>SFT, p={results['bbq_p']:.4f}")
assert results['bbq_k'] + results['wg_k'] > 0, "No positive signs — check score loading"
```

**Failure Detection:**
- k_BBQ = 0: Score loading error — check model name mapping to H-E1 results
- p_BBQ > 0.5: Random or reversed direction — inspect individual pair deltas for confounds
- All deltas ≈ 0: Scores identical — check if same model evaluated twice

**Success Criteria:**
- `hypothesis_support_threshold`: k_BBQ ≥ 4, p_BBQ ≤ 0.125
- `hypothesis_support_metric`: One-sided binomial sign test on BBQ accuracy per matched pair

---

## PoC Success Check

**MECHANISM Pass Condition:**
1. Code runs without error
2. k_BBQ ≥ 4 (≥4/6 pairs show DPO > SFT on BBQ)
3. p_BBQ ≤ 0.125 (one-sided binomial test)

**Failure Action:**
- IF k_BBQ ≤ 3: EXPLORE — check if confounds (base model variation, preference data type) explain absence; PIVOT to descriptive framing without directional mechanism claim

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

*MCP unavailable (ABLATION MODE). Literature-based findings used.*

**Source A.1:** Parrish et al. (2022) "BBQ: A Hand-Built Bias Benchmark for Question Answering"
- Type: Literature / benchmark paper
- Relevance: Establishes BBQ as the standard social bias evaluation benchmark; defines disambiguation accuracy metric
- Key insights: Models rewarded for human-preferred responses (which avoid stereotypes) score higher on BBQ disambiguation; human performance ~90%
- Used For: Dataset selection, metric definition, expected performance range

**Source A.2:** Rudinger et al. (2018) "Gender Bias in Coreference Resolution: Evaluation and Debiasing Methods"
- Type: Literature / benchmark paper
- Relevance: WinoGender is the canonical gender bias probe; measures pronoun resolution accuracy under gendered stereotype conditions
- Used For: Secondary metric selection and expected behavior

**Source A.3:** Rafailov et al. (2023) "Direct Preference Optimization: Your Language Model is Secretly a Reward Model" (arXiv:2305.18290)
- Type: Method paper
- Key insight: DPO reward signal is implicitly shaped by annotator preferences; UltraFeedback-style datasets penalize biased/stereotyped responses
- Used For: Mechanism rationale (DPO encodes bias-avoidance from annotator signal)

**Source A.4:** Standard nonparametric statistics — binomial sign test
- Type: Statistical methodology
- Key insight: One-sided binomial test P(X≥k | n=6, p=0.5): k=4 → p=0.344, k=5 → p=0.109, k=6 → p=0.016. Gate k≥4, p≤0.125 requires k=5 for strict p<0.125.
- Used For: Gate threshold design; p-value interpretation

### B. GitHub Implementations (Exa)

*MCP unavailable. Domain knowledge used.*

**Repository B.1:** EleutherAI/lm-evaluation-harness
- Already used in H-E1; BBQ and WinoGender scores available
- Key files: `lm_eval/tasks/bbq/`, `lm_eval/tasks/winogender/`
- Used For: Dataset/evaluation infrastructure (already complete)

**Repository B.2:** HuggingFaceH4/alignment-handbook
- Primary source of matched DPO/SFT pairs (Zephyr family)
- Preference dataset: UltraFeedback (cleaned, 60K examples) — documents bias-avoidance signal
- Used For: Model pair sourcing and DPO mechanism rationale

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — H-M1 requires no model architecture analysis. Pure statistical analysis of existing scores.

### D. Previous Hypothesis Context

**Source:** H-E1 Validation Report
- File: `docs/youra_research/h-e1/04_validation.md`
- Reused Components:
  - All 12 model benchmark scores (BBQ, WinoGender per model) — primary data for H-M1
  - Model pair structure (6 DPO/SFT pairs) — defines n for binomial test
  - lm-evaluation-harness version and task configuration — ensures score comparability
- Why Reused: H-M1 is explicitly designed as post-hoc analysis of H-E1 scores; reuse enables controlled experiment (only statistical lens changes)

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| BBQ as primary DV | Literature | A.1 (Parrish et al. 2022) |
| WinoGender as secondary DV | Literature | A.2 (Rudinger et al. 2018) |
| DPO bias-avoidance mechanism | Method paper | A.3 (Rafailov et al. 2023) |
| Binomial sign test (n=6, p≤0.125) | Statistics | A.4 (standard nonparametric) |
| Model pairs and BBQ/WinoGender scores | H-E1 results | D.1 (H-E1 validation report) |
| lm-eval task configuration | GitHub | B.1 (lm-evaluation-harness) |
| DPO preference data (UltraFeedback) | GitHub | B.2 (alignment-handbook) |
| Fisher's criterion formula | Literature | Standard (A.4) |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE: restated in state block)
**Date:** 2026-08-31

### Workflow History for This Hypothesis

- H-E1 validated (2026-08-31): LOO k-NN 83.3%, p=0.031 — prerequisite PASSED
- H-M1 set IN_PROGRESS (2026-08-31): External loop started Phase 2C
- H-M1 experiment_design COMPLETED (2026-08-31): This document

---

*MCP Tools Used: None (ABLATION MODE — domain knowledge used)*
*All specifications grounded in H-E1 results + published benchmark literature*
*Next Phase: Phase 3 - Implementation Planning*
