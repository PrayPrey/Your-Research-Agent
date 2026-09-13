# Experiment Design: H-M2

**Date:** 2026-03-14
**Author:** Anonymous
**Hypothesis Statement:** Under controlled training conditions (Pythia-1B, 100B tokens, LR 2e-5, batch 256, cross-entropy loss), if models are trained on corpora with different H(occupation|demographic) values (produced by different curation configurations), then the models' logit margins on demographic probe prompts will be positively correlated with the corpus-level H(occupation|demographic) differences (Spearman ρ > 0, p < 0.01), with a log-linear functional relationship, because cross-entropy training minimizes KL divergence from the empirical conditional distribution, driving the model to approximate corpus-level conditional probability structures in its weight space.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM (Causal Step 2) Template** — Corpus entropy → Model logit margin internalization

---

## Workflow Status

**Verification State:** ACTIVE (workflow.status=ACTIVE, execution_mode=UNATTENDED)
**Prerequisites Satisfied:** H-M1 COMPLETED (PASS — Spearman ρ=1.0, p=1.4e-24; mean log-odds C1=0.697→C5=2.976)
**Gate Status:** SHOULD_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM (Causal Chain Step 2: Corpus Entropy → Model Logit Internalization)
- **Prerequisites:** H-M1 (COMPLETED, PASS)

### Gate Condition
**SHOULD_WORK:** Spearman ρ > 0 with p < 0.01 between corpus H(occupation|demographic) values and model logit margins across 8 Pythia-1B configurations. Failure → EXPLORE (not STOP): examine per-axis correlations, scale up to Pythia-7B.

---

## Continuation Context

**H-M1 is COMPLETED (PASS)** — H-M2 extends the causal chain from corpus-level log-odds (H-M1) to model weight internalization (H-M2). This is the critical "corpus → model" link in the PCFH causal mechanism.

**Architecture of Continuation:**
- H-E1: Measured H(occupation|demographic) in filtered corpus subsets (entropy, bootstrap CI)
- H-M1: Measured conditional log-odds of demographic-occupation co-occurrences in same subsets
- **H-M2 (THIS):** Trains Pythia-1B on each corpus subset → measures model logit margin → tests Spearman correlation between corpus H and model logit margin
- H-M3: Uses H-M2 trained models to test fairness benchmark divergence under matched capability

**Key Reuse from H-M1:**
- Corpus subsets C1–C6 in h-e1/code/ (no re-filtering needed)
- H(occupation|demographic) scalar values for each configuration (C0=3.2662, ..., C5=2.5374)
- Spearman ρ computation pipeline (reuse scipy.stats.spearmanr)
- Statistical analysis framework (statsmodels OLS)

### Previous Hypothesis Results (if applicable)
**H-M1 Validation Report Summary** (from h-m1/04_validation.md):

| Config | Mean Log-Odds |
|--------|---------------|
| C1 | 0.6970 |
| C2 | 0.9158 |
| C3 | 1.1907 |
| C4 | 1.7336 |
| C5 | 2.9762 |
| C6 (DoReMi) | 0.6434 |

- **Spearman ρ = 1.0** (p=1.4e-24): perfect monotonic correlation between fastText intensity and log-odds
- All 5 mechanism checks passed: log_odds_computed ✓, shape_valid ✓, variation_exists ✓, spearman_computed ✓, mechanism_activated ✓
- **Gate PASSED**: MUST_WORK satisfied

**Implication for H-M2:** The corpus-level conditional log-odds (H-M1 DV) is monotonically ordered — this provides the IV ordering for H-M2. If cross-entropy training internalizes these conditional distributions, model logit margins should show the same ordering across C1–C6.

**H(occupation|demographic) values for IV** (from H-E1 02c brief):

| Config | H(occ|demo) bits | Expected logit margin order |
|--------|------------------|-----------------------------|
| C0 | 3.2662 | Reference |
| C1 | 3.2702 | Lowest |
| C2 | 3.2528 | Low |
| C3 | 3.2275 | Mid-low |
| C4 | 3.1106 | Mid-high |
| C5 | 2.5374 | Highest (most filtered) |
| C6 | 3.2209 | DoReMi (near unfiltered) |

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Corpus-to-logit internalization (pretraining bias)**
- **Pythia Suite** (Biderman et al. 2023, arXiv:2304.01373): Pythia enables isolation of corpus statistics effects on LLM behavior. Controlled setup with precise access to training data allows researchers to test whether pronoun/occupation frequency in pretraining data affects downstream logit distributions. Counterfactual retraining (modifying gendered pronoun frequencies) demonstrates that corpus-level statistics propagate into model logit rankings.
  - Key insight: Pythia's logit rankings show variation concordant with pretraining co-occurrence statistics for both gender and race/ethnicity across model sizes
  - **Dataset**: The Pile (800GB) + deduplicated variant; applies to DCLM-POOL analogously
  - **Model**: GPTNeoXForCausalLM, all sizes 70M–12B
  - **Used for**: Confirms mechanism H-M2 hypothesis — corpus conditional distributions propagate to model logits

- **Cross-Care** (PMC): Studies pretraining data statistics and LLM bias manifestation using zero-shot prompting and token co-occurrence analyses. Finds biases present in pretraining data are amplified in model outputs. Researchers probe gender skew by examining empirical frequency of gender co-occurring with job titles in pretraining corpus — the learned distribution reflects data skew.
  - Key insight: Log-probability / logit margin of occupation tokens is sensitive to pretraining corpus occupation-demographic co-occurrence frequencies
  - **Dataset**: Medical pretraining corpora; generalizable to occupation-demographic pairs
  - **Used for**: Validates logit margin as DV for H-M2

**Query 2: Implementation challenges and best practices**
- **Cross-entropy as KL minimization** (Bendersky 2025): Cross-entropy loss = H(p) + KL(p||q). Minimizing cross-entropy during LLM training is exactly equivalent to minimizing KL divergence from empirical conditional distribution p(y|x). This is the theoretical grounding for H-M2 — model weights must converge toward the empirical conditional P(occupation|demographic) in training data.
  - Key insight: Training objective guarantees that sufficiently trained model approximates corpus-level P(occupation|demographic) as internal representation
  - **Used for**: Mechanism justification (pseudo-code, training protocol)

- **Gender bias logit measurement** (Gupta et al. 2023, arXiv:2212.10678): Testing occupational gender bias in LMs via logit probing. Uses zero-shot prompt templates, aggregates log probabilities for demographic tokens, measures KL divergence vs. reference distribution. Correlation τ=0.67 between model logit rankings and human gender-occupation stereotypes.
  - Key insight: Log-probability aggregation (logit margin) over standardized templates is the validated approach for measuring demographic-occupation bias in base LLMs
  - **Dataset**: WinoBias, occupation-gender templates
  - **Used for**: Logit margin computation methodology (DV specification)

**Query 3: Benchmark and standard datasets for evaluation**
- **BBQ** (Parrish et al. 2022, ACL Findings): 58K trinary-choice QA questions across 9 social bias dimensions (age, race, gender, religion, etc.). Ambiguous and disambiguated context pairs. Accuracy gap between ambiguous and disambiguated contexts measures bias direction.
  - Key insight: BBQ accuracy gap measures how much model relies on demographic stereotypes in absence of disambiguating context; suitable for H-M3 (downstream of H-M2)
  - **Used for**: Evaluation benchmark specification

- **WinoBias** (Zhao et al. 2018): Coreference task for gender-occupation bias. Zero-shot classification: model selects between pronoun completions. Smaller models select anti-stereotypical; larger models select stereotypical (bias increases with scale).
  - Key insight: WinoBias provides clean binary logit comparison for gender-occupation stereotypicality — directly measurable as logit margin
  - **Used for**: Secondary evaluation metric

### Archon Code Examples

**Code Example 1: Pythia model loading for inference/logit extraction**
```python
# Source: EleutherAI/pythia on HuggingFace (github.com/EleutherAI/pythia)
from transformers import GPTNeoXForCausalLM, AutoTokenizer
import torch

model = GPTNeoXForCausalLM.from_pretrained(
    "EleutherAI/pythia-1b",
    revision="step143000",          # checkpoint step; use custom trained checkpoint path instead
    cache_dir="./pythia-cache"
)
tokenizer = AutoTokenizer.from_pretrained(
    "EleutherAI/pythia-1b",
    revision="step143000",
    cache_dir="./pythia-cache"
)
# For custom-trained model, replace with local path:
# model = GPTNeoXForCausalLM.from_pretrained("./h-m2/checkpoints/config_C3/")
```
- **Pattern**: GPTNeoXForCausalLM is the correct class for Pythia-1B logit extraction
- **Insight**: Model outputs `.logits` tensor (batch × seq_len × vocab_size); last-token logits used for next-token probability of occupation completions

**Code Example 2: Logit margin computation (gender-occupation probe)**
```python
# Source: Adapted from Gupta et al. 2023 + Pythia bias probing literature
def compute_logit_margin(model, tokenizer, prompt_template, congruent_word, incongruent_word):
    """
    Args:
        prompt_template: "The {occupation} said that [DEMO]..."
        congruent_word: demographically-congruent occupation token
        incongruent_word: demographically-incongruent occupation token
    Returns:
        margin: logit(congruent) - logit(incongruent)
    """
    inputs = tokenizer(prompt_template, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    last_logits = outputs.logits[0, -1, :]  # (vocab_size,)
    congruent_id = tokenizer(congruent_word, add_special_tokens=False)["input_ids"][0]
    incongruent_id = tokenizer(incongruent_word, add_special_tokens=False)["input_ids"][0]
    return (last_logits[congruent_id] - last_logits[incongruent_id]).item()
```
- **Pattern**: Last-position logit delta between demographically congruent/incongruent occupation tokens
- **Insight**: Mean across 50+ probe templates per demographic axis gives robust logit margin estimate

### Exa GitHub Implementations

**Repository 1: EleutherAI/pythia** (⭐ ~2.8k)
- **URL**: https://github.com/EleutherAI/pythia
- **Relevance**: Official repository for Pythia model suite — exact architecture used in H-M2
- **Architecture**: GPTNeoXForCausalLM (decoder-only Transformer, rotary positional embeddings)
- **Config file**: `models/1B/pythia-1b.yml` — training configuration for Pythia-1B
  ```yaml
  # From pythia/models/1B/pythia-1b.yml (key parameters)
  hidden_size: 2048
  num_hidden_layers: 16
  num_attention_heads: 8
  intermediate_size: 8192
  rotary_pct: 0.25
  vocab_size: 50304  # GPT-NeoX-20B tokenizer
  ```
- **Training Config**:
  - Optimizer: AdamW (betas=[0.9, 0.95], eps=1e-8)
  - Steps: 143,000 steps (at batch_size=2,097,152 tokens = ~300B tokens on The Pile)
  - For H-M2: ~47,684 steps at batch_size=256 for 100B token budget
- **Key Code (WinoBias PR #74)**: Implements logit-based WinoBias evaluation as part of Pythia case studies
- **Results**: Bias effects on WinoBias confirmed across Pythia model sizes

**Repository 2: EleutherAI/gpt-neox** (⭐ ~7k)
- **URL**: https://github.com/EleutherAI/gpt-neox
- **Relevance**: Training framework for Pythia — required to train Pythia-1B from scratch on custom corpora
- **Architecture**: GPT-NeoX, identical to Pythia (same codebase)
- **Training Config (from configs/)**:
  - Custom corpus: Change `train-data-paths` in YAML to point to `.bin`/`.idx` tokenized files
  - Tokenizer: GPT-NeoX-20B (50257+47 padding to 50304)
  - Training is launched via `deepy.py` with YAML config
- **Dataset**: For H-M2, tokenize each corpus subset (C1–C5, C6-DoReMi, shuffled-control, unfiltered) using GPT-NeoX-20B tokenizer
- **Single GPU setup**: `CUDA_VISIBLE_DEVICES=X python deepy.py train.py configs/pythia-1b.yml`

**Repository 3: EleutherAI/lm-evaluation-harness** (⭐ ~7k)
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness
- **Relevance**: Standard evaluation framework — includes WinoBias, WinoGender, CrowS-Pairs
- **Key tasks for H-M2/H-M3**: `winobias`, `bbq`, `crows_pairs_english`
- **Evaluation code**:
  ```python
  # WinoBias evaluation (anti-stereotypical completion accuracy)
  lm_eval --model hf \
      --model_args pretrained=./h-m2/checkpoints/config_C3/ \
      --tasks winobias,bbq \
      --device cuda:0 \
      --output_path ./h-m2/results/C3_eval.json
  ```
- **Results**: Logit-based classification — model selects among fixed completion options; accuracy = rate of anti-stereotypical completion selection

**Serena Analysis Needed**: false — code patterns are clear from repository documentation and search results

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is not a paper reproduction experiment — H-M2 is a novel experiment training Pythia-1B from scratch on custom corpus subsets. There is no "author's official implementation" to prioritize.

**Implementation Strategy**: Custom training pipeline using:
1. EleutherAI/gpt-neox (training framework — official Pythia training codebase)
2. EleutherAI/lm-evaluation-harness (evaluation — official bias benchmark evaluation)
3. Custom logit probe script (based on Gupta et al. 2023 logit margin methodology)

**Recommended Implementation Path:**
- Primary: EleutherAI/gpt-neox training framework + custom probe scripts (logit margin computation)
- Fallback: HuggingFace Trainer with GPTNeoXForCausalLM (if gpt-neox setup fails)
- Justification: gpt-neox is the canonical training framework for Pythia; guarantees architecture/config compatibility

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. GPTNeoXForCausalLM logit extraction pattern is standard and well-documented in EleutherAI/pythia and EleutherAI/lm-evaluation-harness. Previous h-m1/code/ provides reusable corpus statistical analysis components.

---

## Experiment Specification

### Dataset

### Dataset Specification

**Primary Training Dataset**: DCLM-POOL (mlfoundations/dclm-baseline-1.0)
- **Type**: standard (real, established corpus — Common Crawl web text filtered by DCLM)
- **Source**: HuggingFace Datasets (streaming)
- **Splits used**: 6 curated training corpus subsets (already computed in h-e1/code/):
  - C1: fastText ≥10% (lowest quality threshold)
  - C2: fastText ≥30%
  - C3: fastText ≥50%
  - C4: fastText ≥70%
  - C5: fastText ≥90% (highest quality threshold)
  - C6: DoReMi domain reweighting
  - C7: Shuffled-demographic negative control (C3 corpus with demographic tokens randomly permuted across documents)
  - C0: Unfiltered baseline
- **Total training runs**: ~8 Pythia-1B checkpoints (C0–C7)
- **Token budget**: 100B tokens per run
- **Preprocessing**: GPT-NeoX-20B tokenizer (50304 vocab size); tokenized to `.bin`/`.idx` format using gpt-neox tokenization pipeline
- **Key values from prior work (H-M1)**:
  - H(occ|demo) values: C0=3.2662, C1=3.2702, C2=3.2528, C3=3.2275, C4=3.1106, C5=2.5374, C6=3.2209 bits
  - Mean log-odds: C1=0.697, C2=0.916, C3=1.191, C4=1.734, C5=2.976, C6=0.643
- **Hypothesis Fit**: Reuse H-E1/H-M1 corpus subsets → known H(occupation|demographic) values → controlled IV for Spearman correlation test

**Evaluation Datasets** (accessed via lm-evaluation-harness — no separate download):
- WinoBias (v1.1): Gender-occupation coreference; 3,160 examples (type 1 + type 2)
- BBQ (Parrish et al. 2022): 58,492 QA examples across 9 bias categories; used in H-M3 (logged here for tracking)
- Custom demographic probe templates: 50+ templates per demographic axis (gender × occupation), hand-crafted based on Gupta et al. 2023 format

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets (streaming) + pre-tokenized subsets from h-e1/code/
- Identifier: `mlfoundations/dclm-baseline-1.0` (corpus subsets reused from h-e1/code/data/filtered/)
- Code: `dataset = load_dataset("mlfoundations/dclm-baseline-1.0", streaming=True)` (then tokenize with GPT-NeoX-20B tokenizer for gpt-neox training)

### Models

#### Baseline Model

### Baseline Model Specification

**Architecture**: Pythia-1B (GPT-NeoX architecture)
- **Type**: decoder-only Transformer with rotary positional embeddings
- **Size**: ~1.1B parameters
- **Config** (from `pythia/models/1B/pythia-1b.yml`):
  - hidden_size: 2048
  - num_hidden_layers: 16
  - num_attention_heads: 8
  - intermediate_size: 8192
  - max_sequence_length: 2048
  - vocab_size: 50304 (GPT-NeoX-20B tokenizer)
  - rotary_pct: 0.25
- **Source**: EleutherAI/pythia-1b on HuggingFace (used as architecture reference; each configuration trained from scratch)
- **Training framework**: EleutherAI/gpt-neox (deepy.py launcher with YAML config)
- **Hypothesis Fit**: Pythia designed for controlled pretraining experiments; consistent architecture across scales; 100B token budget tractable on single GPU with gradient checkpointing

**Baseline Run (C0 — unfiltered)**: Pythia-1B trained on unfiltered DCLM-POOL subset
- Logit margins from C0 model serve as "no-curation" reference point
- All other configurations (C1–C7) compared against C0 or each other

**Secondary Model (slope-consistency)**: Pythia-160M
- Same config structure, reduced hidden_size/layers
- Run on subset of configurations (C1, C3, C5) to verify directional signal at smaller scale (Risk R1 mitigation)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers (for logit extraction from trained checkpoints)
- Identifier: `./h-m2/checkpoints/config_{C_ID}/` (locally trained; architecture ref: `EleutherAI/pythia-1b`)
- Code: `model = GPTNeoXForCausalLM.from_pretrained("./h-m2/checkpoints/config_C3/"); tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-1b")`

#### Proposed Model

**Architecture:** Baseline + [Mechanism from hypothesis]

**Core Mechanism Implementation:**

```python
# Core Mechanism: Corpus-Entropy → Model Logit Margin Internalization (H-M2)
# Based on: EleutherAI/pythia + Gupta et al. 2023 logit probe methodology
# Architecture: GPTNeoXForCausalLM (Pythia-1B)

def compute_logit_margin(model, tokenizer, prompt, demo_congruent_occ, demo_incongruent_occ):
    """
    Args:
        prompt: str — probe template, e.g., "The {demographic} worked as a"
        demo_congruent_occ: str — occupation stereotypically associated with demographic
        demo_incongruent_occ: str — occupation not stereotypically associated
    Returns:
        float — logit(congruent_occ) - logit(incongruent_occ) at last prompt position
    """
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        logits = model(**inputs).logits[0, -1, :]  # (vocab_size,)
    cid = tokenizer(demo_congruent_occ, add_special_tokens=False)["input_ids"][0]
    iid = tokenizer(demo_incongruent_occ, add_special_tokens=False)["input_ids"][0]
    return (logits[cid] - logits[iid]).item()

def compute_mean_logit_margin(model, tokenizer, probe_templates, occ_pairs):
    """Aggregate over 50+ templates × occupation pairs per demographic axis"""
    margins = [compute_logit_margin(model, tokenizer, t, c, i)
               for t, (c, i) in zip(probe_templates, occ_pairs)]
    return float(np.mean(margins))

# Run across all 8 Pythia-1B checkpoints (C0–C7)
corpus_entropy = [H_C0, H_C1, H_C2, H_C3, H_C4, H_C5, H_C6, H_C7]  # from H-M1
model_logit_margins = [compute_mean_logit_margin(models[i], ...) for i in range(8)]
rho, pvalue = spearmanr(corpus_entropy, model_logit_margins)  # gate: rho>0, p<0.01
log_linear_R2 = fit_log_linear(np.log(corpus_entropy), model_logit_margins)  # R², coef sig
```

### Training Protocol

### Training Protocol

**Framework**: EleutherAI/gpt-neox (deepy.py launcher)
**Architecture**: Pythia-1B config (`pythia/models/1B/pythia-1b.yml`)

**Controlled Hyperparameters** (fixed from Phase 2A/2B specification — must match main hypothesis H-PCFH-v1):
- **Optimizer**: AdamW
  - β₁=0.9, β₂=0.95, ε=1e-8, weight_decay=0.1
  - **Source**: Pythia paper (Biderman et al. 2023) + main hypothesis specification
- **Learning Rate**: 2e-5
  - **Schedule**: Cosine decay with 1% warmup (matching DCLM recipe)
  - **Source**: H-PCFH-v1 controlled variables specification
- **Batch Size**: 256 sequences × 2048 tokens = 524,288 tokens/step
  - **Source**: H-PCFH-v1 controlled variable; note: global batch size in gpt-neox config must be set to 256
- **Token Budget**: 100B tokens per run
  - Steps: 100B / 524,288 ≈ 190,735 steps per checkpoint
  - **Source**: H-PCFH-v1 fixed token budget
- **Loss**: Cross-entropy (next-token prediction, standard autoregressive LM objective)
  - **Source**: DCLM recipe + Pythia standard
- **Seeds**: 1 fixed seed per configuration (seed=42); PoC direction-based gate
- **Gradient checkpointing**: enabled (required for 1B model on single 40GB GPU)
- **Mixed precision**: bf16 (A100/H100) or fp16 (V100)

**Per-Run GPU Setup**:
```bash
nvidia-smi  # identify lowest-memory GPU
export CUDA_VISIBLE_DEVICES=<empty_gpu_id>
python deepy.py train.py configs/pythia-1b-hm2-C{N}.yml
```

**Total Runs**:
- C0 (unfiltered), C1–C5 (fastText 10%–90%), C6 (DoReMi), C7 (shuffled-demographic control)
- 8 runs × ~190K steps = ~1.52M total steps
- **Recommended**: Run Pythia-160M on C1, C3, C5 first for slope-consistency check (Risk R1 mitigation; ~3× faster per run)

**Checkpoint Saving**: Every 10,000 steps; final checkpoint used for evaluation

### Evaluation

### Evaluation Metrics

**Primary Metrics (H-M2 Gate)**:

1. **Model Logit Margin** (mean_logit_margin per configuration):
   - Definition: mean(logit(demographically-congruent occupation) − logit(demographically-incongruent occupation)) across 50+ probe templates per demographic axis (gender × occupation)
   - Computed from: final Pythia-1B checkpoint for each of 8 configurations
   - Library: `transformers` (GPTNeoXForCausalLM.logits), `numpy` (mean)

2. **Spearman ρ** between corpus H(occupation|demographic) and model logit margins:
   - Gate: Spearman ρ > 0, p < 0.01 (SHOULD_WORK)
   - Library: `scipy.stats.spearmanr`

3. **Log-Linear R²** (logit_margin ~ log(H_entropy)):
   - Fit via `statsmodels.OLS`; report coefficient, p-value, R²
   - Expected: positive coefficient, R² > 0.3 (secondary criterion)

**Negative Control Metric**:

4. **Shuffled-Demographic Control Δ** (C7 vs. C0):
   - Definition: |mean_logit_margin(C7) − mean_logit_margin(C0)|
   - Gate: ≤ 0.01 (validates conditional structure as mechanism, not mere entropy)
   - Interpretation: if shuffled corpus with same token frequencies but destroyed conditional associations produces logit margins indistinguishable from unfiltered baseline → confirms mechanism is conditional association density, not surface token frequency

**Secondary Metrics** (WinoBias via lm-evaluation-harness):
- WinoBias type1 pro-stereotypical / anti-stereotypical accuracy per configuration
- Spearman ρ between H(occ|demo) and WinoBias accuracy gap
- Library: `lm_eval` (EleutherAI/lm-evaluation-harness)

**Success Criteria (SHOULD_WORK gate)**:
- Primary: Spearman ρ > 0 with p < 0.01 between corpus H(occ|demo) and model logit margins
- Secondary: Shuffled-demographic control Δ ≤ 0.01
- Failure → EXPLORE: examine per-demographic-axis correlations; scale up to Pythia-7B

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: language model logit probe + correlation analysis
- Library: `scipy.stats` (spearmanr), `statsmodels` (OLS log-linear), `transformers` (logit extraction), `lm_eval` (WinoBias)
- Code: `rho, pval = spearmanr(corpus_entropy_values, model_logit_margins); lm_eval --model hf --model_args pretrained=./checkpoints/C3 --tasks winobias`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

**Recommended Additional Figures:**
1. **Scatter plot**: Corpus H(occ|demo) vs. model logit margin (8 points with labels C0–C7) + Spearman ρ annotation + log-linear fit line
2. **Bar chart**: Mean logit margin per configuration (C0–C7) showing monotonic trend
3. **Negative control comparison**: Grouped bar chart — C3 (mid-filter) vs. C7 (shuffled) vs. C0 (unfiltered) logit margins; annotate Δ
4. **Per-axis breakdown**: Heatmap of logit margins × (demographic_axis × curation_config) — gender (m/f), race (4+ categories), occupation (20+ categories)
5. **WinoBias accuracy gap per config**: Line chart showing anti-stereotypical accuracy across C0–C6 (secondary evidence of internalization)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | Cross-entropy training on corpus with known H(occ\|demo) values produces Pythia-1B checkpoints; logit margin computable from final checkpoint | TRUE |
| Mechanism Isolatable | Each configuration is a separate training run; logit margin extracted independently per checkpoint; Spearman ρ computed across configurations | TRUE |
| Baseline Measurable | C0 (unfiltered) Pythia-1B provides baseline logit margin; C7 (shuffled-demographic) provides negative control | TRUE |

### Architecture Compatibility Check

Pythia-1B (GPTNeoXForCausalLM) is fully compatible with this experiment:
- **Required**: Decoder-only autoregressive LM with next-token logits output → ✅ GPTNeoXForCausalLM provides `.logits` tensor
- **Required**: GPT-NeoX tokenizer for demographic/occupation token ID lookup → ✅ AutoTokenizer from "EleutherAI/pythia-1b"
- **Required**: Trainable from scratch on custom corpus → ✅ gpt-neox framework supports custom `.bin`/`.idx` training data
- **Incompatible architectures**: encoder-only (BERT, RoBERTa) — cannot compute next-token logit margins

**No incompatibility issues detected.**

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Training config C{N}: token_budget=100B reached, saving checkpoint" | gpt-neox training log |
| Tensor Shape | model.logits shape = (1, seq_len, 50304); last-token slice = (50304,) | probe_script.py:compute_logit_margin() |
| Metric Delta | mean_logit_margin(C5) > mean_logit_margin(C1) > mean_logit_margin(C0) (matches H-M1 ordering) | probe_script.py:run_all_configs() |

**Activation Verification Code:**
```python
def verify_mechanism_activated(logit_margins_by_config, corpus_entropy_by_config):
    """Verify H-M2 mechanism: corpus entropy → model logit margin"""
    rho, pval = spearmanr(corpus_entropy_by_config, logit_margins_by_config)
    indicators = {
        "checkpoints_exist": all(os.path.exists(f"./checkpoints/config_{c}/") for c in CONFIGS),
        "logit_margins_computed": all(abs(m) < 10 for m in logit_margins_by_config),  # sanity check
        "ordering_matches_hm1": logit_margins_by_config[4] > logit_margins_by_config[0],  # C5>C1
        "spearman_positive": rho > 0,
        "spearman_significant": pval < 0.01
    }
    gate_pass = indicators["spearman_positive"] and indicators["spearman_significant"]
    return gate_pass, indicators
```

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Checkpoints exist | 8 configs × 1 checkpoint each | File system check |
| Logit margins computed | All 8 values finite and within [-5, 5] range | probe_script.py |
| Hypothesis Supported | Spearman ρ > 0, p < 0.01 | spearmanr(corpus_H, logit_margins) |

---

## 🔬 PoC Success Check

**MECHANISM Pass Condition (SHOULD_WORK gate):**
1. All 8 Pythia-1B training runs complete without error
2. Logit margins computed for all 8 configurations
3. Spearman ρ > 0 AND p < 0.01 between corpus H(occ|demo) and model logit margins
4. Shuffled-demographic control (C7) logit margin Δ ≤ 0.01 vs. C0 baseline

---

## Appendix: Reference Implementations

### A. Knowledge Base Sources (Web Research as Archon Compensating)

**Source A.1**: Pythia Suite (Biderman et al. 2023)
- **Type**: Academic paper + official implementation
- **Reference**: arXiv:2304.01373; GitHub: github.com/EleutherAI/pythia
- **Query Used**: "Pythia language model pretraining logit margin demographic bias"
- **Relevance**: Official architecture and training framework for H-M2; confirms that Pythia logit rankings vary concordantly with pretraining co-occurrence statistics
- **Key Insights**:
  - GPTNeoXForCausalLM is the correct inference class
  - 154 checkpoints per model size available; counterfactual retraining validated at Pythia scale
  - WinoBias PR #74 shows bias probing in Pythia repository
- **Used For**: Architecture specification, training config, model loading code

**Source A.2**: Cross-Care (PMC, 2024)
- **Type**: Academic paper
- **Reference**: PMC12045606
- **Query Used**: "cross-entropy training conditional distribution internalization LLM fairness"
- **Relevance**: Validates that pretraining data statistics propagate into LLM logit margins; biases in pretraining data amplified in model outputs
- **Key Insights**: Gender skew measured by empirical frequency of gender co-occurring with job titles in pretraining corpus → directly operationalizes H-M2 IV
- **Used For**: Mechanism justification, evaluation methodology

**Source A.3**: Gupta et al. 2023 (arXiv:2212.10678)
- **Type**: Academic paper
- **Reference**: "Testing Occupational Gender Bias in Language Models"
- **Query Used**: "demographic logit margin probe LLM bias gender occupation correlation"
- **Relevance**: Validates logit margin as the correct DV for H-M2; correlation τ=0.67 between model logit rankings and human occupation stereotypes
- **Key Insights**: Zero-shot prompt template + log-probability aggregation = validated logit margin methodology; 50+ templates recommended for robustness
- **Used For**: Probe template design, logit margin DV specification

**Source A.4**: Cross-Entropy / KL Divergence theory (Bendersky 2025)
- **Type**: Technical reference
- **Reference**: eli.thegreenplace.net/2025/cross-entropy-and-kl-divergence/
- **Query Used**: "cross-entropy training KL divergence conditional distribution internalization"
- **Relevance**: Mathematical grounding for H-M2 mechanism: cross-entropy minimization = KL divergence minimization = model converges to approximate empirical p(occ|demo)
- **Used For**: Mechanism explanation, hypothesis theoretical justification

**Source A.5**: BBQ Benchmark (Parrish et al. 2022, ACL Findings)
- **Type**: Dataset + evaluation methodology
- **Reference**: arXiv:2110.08193; aclanthology.org/2022.findings-acl.165
- **Query Used**: "BBQ WinoBias evaluation language model zero-shot logit bias"
- **Relevance**: 58K trinary-choice QA questions across 9 bias dimensions; accuracy gap between ambiguous/disambiguated contexts measures bias reliance; used for H-M3 evaluation
- **Used For**: Evaluation benchmark specification (H-M3 downstream; logged here for continuity)

---

### B. GitHub Implementations (Research)

**Repository B.1: EleutherAI/pythia** (⭐ ~2.8k)
- **URL**: github.com/EleutherAI/pythia
- **Query Used**: "Pythia EleutherAI training recipe pretraining script HuggingFace 1B model"
- **Relevance**: Official repository; contains `models/1B/pythia-1b.yml` config + WinoBias evaluation PR #74
- **Configuration Extracted**: hidden_size=2048, num_layers=16, num_heads=8, rotary_pct=0.25, vocab_size=50304
- **Their Results**: WinoBias bias effects confirmed across model sizes (case study in paper)
- **Used For**: Architecture configuration, model loading code, evaluation methodology

**Repository B.2: EleutherAI/gpt-neox** (⭐ ~7k)
- **URL**: github.com/EleutherAI/gpt-neox
- **Query Used**: "EleutherAI pythia train from scratch custom dataset gpt-neox config yaml"
- **Relevance**: Training framework for Pythia; supports custom corpus via `train-data-paths` in YAML
- **Configuration Extracted**: AdamW optimizer (betas=[0.9, 0.95]), deepy.py launcher, `.bin`/`.idx` tokenized data format
- **Used For**: Training protocol specification, custom corpus integration

**Repository B.3: EleutherAI/lm-evaluation-harness** (⭐ ~7k)
- **URL**: github.com/EleutherAI/lm-evaluation-harness
- **Query Used**: "EleutherAI pythia bias probe logit evaluation script"
- **Relevance**: Standard framework for WinoBias, BBQ, CrowS-Pairs evaluation; used for secondary H-M2 metrics
- **Configuration Extracted**: `lm_eval --model hf --tasks winobias` command pattern; logit-based classification
- **Used For**: WinoBias evaluation specification, BBQ evaluation (H-M3)

---

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from search results was sufficiently clear. GPTNeoXForCausalLM logit extraction pattern is standard and well-documented. Previous h-m1/code/ provides reusable statistical analysis components.

---

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report — H-M1 (h-m1/04_validation.md)
- **Reused Components**:
  - Corpus subsets C1–C6 (h-e1/code/ and h-m1/code/) — proven stable
  - H(occupation|demographic) scalar values per configuration (from H-E1)
  - Log-odds matrix: 1800 (demographic, occupation) pairs × 6 configurations (H-M1)
  - Spearman correlation pipeline: `scipy.stats.spearmanr` + `statsmodels.OLS`
- **Why Reused**: Enables controlled experiment — only the "model training" component changes; corpus subsets and statistical analysis framework proven in h-m1

---

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (DCLM-POOL corpus subsets) | Prior hypothesis + standard | H-E1, H-M1 results; mlfoundations/dclm-baseline-1.0 |
| Model architecture (Pythia-1B) | GitHub + paper | B.1 (EleutherAI/pythia); A.1 (Biderman 2023) |
| Training framework | GitHub | B.2 (EleutherAI/gpt-neox) |
| Hyperparameters (LR=2e-5, batch=256) | Main hypothesis spec | H-PCFH-v1 controlled variables |
| Logit margin DV | Academic paper | A.3 (Gupta et al. 2023) |
| Probe template methodology | Academic paper | A.3 (Gupta et al. 2023); A.2 (Cross-Care) |
| Spearman ρ gate metric | Phase 2B | 02b_verification_plan.md H-M2 success criteria |
| Log-linear functional form | Phase 2B | 02b_verification_plan.md H-M2 verification protocol |
| Cross-entropy mechanism justification | Theory | A.4 (Bendersky 2025 — KL=CE) |
| WinoBias secondary metric | GitHub + paper | B.3 (lm-evaluation-harness); Zhao et al. 2018 |
| Shuffled-demographic negative control | Phase 2B | 02b_verification_plan.md H-M2 step 4 |
| BBQ benchmark (H-M3 reference) | Academic paper | A.5 (Parrish et al. 2022) |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-14

### Workflow History for This Hypothesis
- 2026-03-14T18:42:33: h-m2 set to IN_PROGRESS (External loop starting Phase 2C → 3 → 4)
- 2026-03-14: Phase 2C experiment design IN_PROGRESS

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
