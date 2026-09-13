# Product Requirements Document: H-M2
# Corpus Entropy → Model Logit Margin Internalization

**Hypothesis ID:** H-M2
**Type:** MECHANISM (Causal Chain Step 2)
**Tier:** FULL (30 tasks max)
**Date:** 2026-03-14
**Author:** Anonymous
**Phase:** 3 — Implementation Planning

---

## 1. Executive Summary

H-M2 tests whether Pythia-1B models trained on corpora with different conditional demographic association densities (H(occupation|demographic)) internalize those differences into their logit structures. Specifically, we train 8 Pythia-1B checkpoints (one per curation configuration C0–C7) and measure whether model logit margins on demographic probe prompts are positively correlated with corpus-level H(occupation|demographic) values (Spearman ρ > 0, p < 0.01). This is the critical "corpus → model" causal link in the PCFH hypothesis chain.

**Gate:** SHOULD_WORK — failure triggers EXPLORE, not STOP.

---

## 2. Problem Statement

### 2.1 Context

H-E1 confirmed that different data curation paths produce measurable differences in H(occupation|demographic) entropy values across corpus configurations. H-M1 confirmed that conditional log-odds of demographic-occupation co-occurrences are monotonically ordered across curation intensities. H-M2 now asks: **does cross-entropy pretraining on these corpora cause Pythia-1B to internalize the corpus-level conditional probability structure into its logit space?**

### 2.2 Research Question

Does the cross-entropy training objective cause a Pythia-1B model to approximate corpus-level P(occupation|demographic) in its weight space, such that model logit margins on demographic-occupation probe prompts are monotonically correlated with corpus H(occupation|demographic)?

### 2.3 Hypothesis Statement

Under controlled training conditions (Pythia-1B, 100B tokens, LR 2e-5, batch 256, cross-entropy loss), if models are trained on corpora with different H(occupation|demographic) values (produced by different curation configurations), then the models' logit margins on demographic probe prompts will be positively correlated with the corpus-level H(occupation|demographic) differences (Spearman ρ > 0, p < 0.01), with a log-linear functional relationship.

---

## 3. Functional Requirements

### FR-1: Training Pipeline (8 Configurations)

**FR-1.1:** Train Pythia-1B from scratch on each of 8 corpus configurations:
- C0: Unfiltered DCLM-POOL baseline
- C1: fastText ≥10% percentile filter
- C2: fastText ≥30% percentile filter
- C3: fastText ≥50% percentile filter
- C4: fastText ≥70% percentile filter
- C5: fastText ≥90% percentile filter
- C6: DoReMi domain reweighting
- C7: Shuffled-demographic negative control (C3 corpus, demographic tokens randomly permuted)

**FR-1.2:** Training hyperparameters (fixed, from H-PCFH-v1 specification):
- Architecture: GPTNeoXForCausalLM (Pythia-1B config: hidden_size=2048, 16 layers, 8 heads)
- Optimizer: AdamW (β₁=0.9, β₂=0.95, ε=1e-8, weight_decay=0.1)
- Learning rate: 2e-5 with cosine decay schedule, 1% warmup
- Batch size: 256 sequences × 2048 tokens = 524,288 tokens/step
- Token budget: 100B tokens per run → ~190,735 steps
- Loss: cross-entropy (autoregressive next-token prediction)
- Seed: 42 (fixed per configuration)
- Mixed precision: bf16 (A100/H100) or fp16 (V100)
- Gradient checkpointing: enabled

**FR-1.3:** Training framework: EleutherAI/gpt-neox (deepy.py launcher with YAML configs)

**FR-1.4:** Tokenization: GPT-NeoX-20B tokenizer (vocab_size=50304); corpus subsets tokenized to .bin/.idx format

**FR-1.5:** Checkpoint saving: every 10,000 steps; final checkpoint used for evaluation

### FR-2: Corpus Data Preparation

**FR-2.1:** Reuse corpus subsets C1–C6 from h-e1/code/data/filtered/ (no re-filtering needed)

**FR-2.2:** Create C7 (shuffled-demographic negative control) by randomly permuting demographic tokens across documents in C3 corpus

**FR-2.3:** Use C0 (unfiltered) as baseline; stream from mlfoundations/dclm-baseline-1.0 and tokenize

**FR-2.4:** Tokenize each corpus subset using gpt-neox tokenization pipeline; output .bin/.idx files to h-m2/data/tokenized/config_C{N}/

### FR-3: Logit Margin Probe Pipeline

**FR-3.1:** Implement logit margin computation using Gupta et al. 2023 methodology:
- For each probe template and occupation pair, compute: logit(demographically-congruent occupation) − logit(demographically-incongruent occupation) at last prompt position
- Mean over 50+ templates per demographic axis (gender × occupation)

**FR-3.2:** Demographic axes:
- Gender: male vs. female (grammatically-marked demographic tokens)
- Occupation pairs: 20+ WinoBias occupation categories (e.g., nurse/engineer, teacher/pilot)

**FR-3.3:** Probe templates: 50+ zero-shot templates per demographic axis (format: "The {occupation} said that [DEMO]..." variants)

**FR-3.4:** Load each Pythia-1B checkpoint from h-m2/checkpoints/config_C{N}/ and run probe pipeline

**FR-3.5:** Output: mean_logit_margin scalar per configuration (8 values total)

### FR-4: Statistical Analysis

**FR-4.1:** Compute Spearman ρ between corpus H(occupation|demographic) values and model logit margins using scipy.stats.spearmanr

**FR-4.2:** Fit log-linear model: logit_margin ~ log(H_entropy) using statsmodels OLS; report coefficient, p-value, R²

**FR-4.3:** Compute negative control metric: |mean_logit_margin(C7) − mean_logit_margin(C0)|; expected ≤ 0.01

**FR-4.4:** Gate evaluation: Spearman ρ > 0 AND p < 0.01

### FR-5: Secondary Evaluation (WinoBias)

**FR-5.1:** Run lm-evaluation-harness WinoBias task on each of 8 Pythia-1B checkpoints:
```bash
lm_eval --model hf --model_args pretrained=./h-m2/checkpoints/config_C{N}/ --tasks winobias --device cuda:0 --output_path ./h-m2/results/C{N}_winobias.json
```

**FR-5.2:** Compute WinoBias accuracy gap (pro-stereotypical − anti-stereotypical accuracy) per configuration

**FR-5.3:** Compute Spearman ρ between H(occ|demo) and WinoBias accuracy gap (secondary evidence)

### FR-6: Slope Consistency Check (Pythia-160M)

**FR-6.1:** Train Pythia-160M (same config structure, smaller scale) on C1, C3, C5 only

**FR-6.2:** Compute logit margins for Pythia-160M on same probe templates

**FR-6.3:** Verify directional consistency: logit_margin(C5) > logit_margin(C3) > logit_margin(C1) for 160M

### FR-7: Visualization

**FR-7.1:** Scatter plot: Corpus H(occ|demo) vs. model logit margin (8 points, C0–C7 labels) with Spearman ρ annotation and log-linear fit line

**FR-7.2:** Bar chart: Mean logit margin per configuration (C0–C7), sorted by H(occ|demo)

**FR-7.3:** Negative control comparison: grouped bar chart — C3 vs. C7 vs. C0 logit margins with Δ annotation

**FR-7.4:** Per-axis heatmap: logit margins × (demographic_axis × curation_config)

**FR-7.5:** WinoBias accuracy gap per config: line chart across C0–C6

All figures saved to h-m2/figures/

---

## 4. Data Specification

### 4.1 Primary Training Data

| Config | Dataset | Source | Size (approx) |
|--------|---------|--------|---------------|
| C0 | DCLM-POOL unfiltered | mlfoundations/dclm-baseline-1.0 (streaming) | 100B tokens |
| C1–C5 | Filtered subsets | h-e1/code/data/filtered/ (REUSE) | 100B tokens each |
| C6 | DoReMi reweighted | h-e1/code/data/filtered/ (REUSE) | 100B tokens |
| C7 | Shuffled-demo control | Generated from C3 corpus | 100B tokens |

**H(occupation|demographic) values per configuration (from H-E1/H-M1):**

| Config | H(occ\|demo) bits | Mean Log-Odds (H-M1) |
|--------|------------------|----------------------|
| C0 | 3.2662 | Reference |
| C1 | 3.2702 | 0.6970 |
| C2 | 3.2528 | 0.9158 |
| C3 | 3.2275 | 1.1907 |
| C4 | 3.1106 | 1.7336 |
| C5 | 2.5374 | 2.9762 |
| C6 | 3.2209 | 0.6434 |
| C7 | ~3.2275 (shuffled) | N/A |

### 4.2 Evaluation Data

| Dataset | Source | Size | Purpose |
|---------|--------|------|---------|
| WinoBias v1.1 | lm-evaluation-harness (auto) | 3,160 examples | Secondary metric |
| Probe templates | Custom (hand-crafted, Gupta 2023 format) | 50+ per axis | Primary logit probe |

### 4.3 Manual Download Requirements

- **C0 tokenization**: Stream from HuggingFace `mlfoundations/dclm-baseline-1.0`; requires internet access
- **C7 generation**: Generate from C3 subset in h-e1/code/data/filtered/config_C3/
- **C1–C6**: Reuse from h-e1/code/data/filtered/ (no download needed)
- **gpt-neox tokenizer**: Download GPT-NeoX-20B tokenizer files

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed (42) for all training runs
- gpt-neox YAML configs committed to h-m2/configs/
- All probe template texts saved to h-m2/data/probe_templates.json

### NFR-2: Performance
- Each Pythia-1B run: ~190K steps on single GPU with gradient checkpointing
- Estimated runtime: ~48-72h per config on A100; run C1/C3/C5 with 160M first for signal
- Probe pipeline: <1h per checkpoint (50 templates × 20 occ pairs = 1,000 forward passes)

### NFR-3: Single GPU
- ALWAYS: `nvidia-smi` → identify lowest-memory GPU → `export CUDA_VISIBLE_DEVICES=<id>`
- One training run at a time; no multi-GPU required
- Gradient checkpointing: mandatory for 1B model

### NFR-4: Reuse
- Reuse h-m1/code/statistical_tests.py for Spearman correlation pipeline
- Reuse h-e1/code/ corpus subsets (no re-filtering)
- Reuse h-m1/code/config.py patterns for new training config structure

### NFR-5: Testing
- Unit tests for logit margin computation (probe_script.py)
- Integration test: verify mechanism activation (verify_mechanism_activated function)
- WinoBias evaluation pipeline test

---

## 6. Success Criteria (Gate Conditions)

### Primary Gate: SHOULD_WORK

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Spearman ρ (corpus H vs. logit margin) | ρ > 0, p < 0.01 | scipy.stats.spearmanr |
| Negative control Δ | \|margin(C7) − margin(C0)\| ≤ 0.01 | probe_script.py |
| Checkpoints exist | 8 configs × 1 checkpoint | File system check |
| Logit margins computed | All 8 values in [-5, 5] | probe_script.py |

### Secondary Criteria

| Criterion | Expected | Purpose |
|-----------|----------|---------|
| Log-linear R² | > 0.3 | Functional form validation |
| 160M slope consistency | margin(C5) > margin(C1) | Scale robustness |
| WinoBias ρ | > 0 | Corroborating evidence |

### Failure Routing

- SHOULD_WORK gate failure → EXPLORE (not STOP)
  - Examine per-demographic-axis correlations
  - Scale up to Pythia-7B (if available)
  - Reduce to simpler logit metric

---

## 7. Dependencies

### 7.1 Python Packages

```
# Core training
torch>=2.0.0
transformers>=4.38.0
datasets>=2.16.0
accelerate>=0.25.0

# gpt-neox (install from source)
# git clone https://github.com/EleutherAI/gpt-neox && pip install -e .

# Evaluation
lm-eval>=0.4.0
# git clone https://github.com/EleutherAI/lm-evaluation-harness && pip install -e .

# Statistical analysis (reuse from h-m1)
scipy>=1.11.0
statsmodels>=0.14.0
numpy>=1.24.0

# Visualization
matplotlib>=3.8.0
seaborn>=0.13.0

# Utilities
pyyaml>=6.0
tqdm>=4.66.0
pytest>=7.0.0
```

### 7.2 External Repositories

| Repository | Purpose | URL |
|-----------|---------|-----|
| EleutherAI/gpt-neox | Pythia training framework | github.com/EleutherAI/gpt-neox |
| EleutherAI/lm-evaluation-harness | WinoBias evaluation | github.com/EleutherAI/lm-evaluation-harness |
| EleutherAI/pythia | Architecture reference | github.com/EleutherAI/pythia |

### 7.3 Base Hypothesis Dependencies

| Artifact | Source | Purpose |
|---------|--------|---------|
| Corpus subsets C1–C6 | h-e1/code/data/filtered/ | Training data (reuse) |
| H(occ\|demo) values | h-e1/02c_experiment_brief.md | IV for Spearman test |
| statistical_tests.py | h-m1/code/ | Spearman pipeline (reuse) |
| config.py patterns | h-m1/code/ | Configuration reference |

---

## 8. Out of Scope

- Multi-GPU distributed training (single GPU only)
- BBQ benchmark evaluation (planned for H-M3, not H-M2)
- Full 100B token production run before gate validation (PoC: use 50B tokens or early checkpoint for signal)
- Instruction-tuned or RLHF models (base Pythia only)
- Hyperparameter search (all hyperparameters fixed per H-PCFH-v1)

---

## 9. Implementation Notes

### 9.1 Quick-Run Strategy (PoC Gating)

Per h-e1 and h-m1 precedent, use abbreviated runs for gate validation:
- Train on 50B tokens (half budget) or use intermediate checkpoint (step 95,000)
- If gate passes → continue full 100B token run in background
- This avoids waiting 72h × 8 = 576h before getting any signal

### 9.2 gpt-neox Configuration

Each configuration requires a YAML config file (configs/pythia-1b-hm2-C{N}.yml) specifying:
- `train-data-paths`: point to h-m2/data/tokenized/config_C{N}/
- `global-batch-size`: 256
- `lr`: 2e-5
- `train-iters`: 190735 (for 100B tokens) or 95368 (for 50B quick-run)
- Gradient checkpointing, bf16/fp16 mixed precision

### 9.3 C7 Negative Control Generation

C7 = C3 corpus with demographic tokens randomly permuted across documents:
1. Load C3 token IDs from h-e1/code/data/filtered/config_C3/
2. Identify demographic token IDs (pronouns, names, gender markers) using predefined list
3. Collect all demographic token occurrences across all documents
4. Randomly permute demographic tokens globally (shuffle within demographic token pool)
5. Write permuted corpus to h-m2/data/tokenized/config_C7/

---

*Generated by Phase 3 Workflow (UNATTENDED mode)*
*Input: h-m2/02c_experiment_brief.md*
*Next: Architecture Agent (Step 3)*
