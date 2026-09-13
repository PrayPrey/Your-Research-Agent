# 4. Experimental Setup

We design our experiments to answer three specific questions that map to the claims in Section 1:

**RQ1:** Does fastText quality filtering create systematic, monotonic changes in conditional demographic-occupation entropy H(occupation|demographic)? *(Tests Contribution C1, H-E1)*

**RQ2:** Do the conditional log-odds of demographic-occupation co-occurrences correlate with filtering intensity? *(Tests Contribution C1, H-M1)*

**RQ3:** Does a model trained on filtered corpus represent the corpus demographic structure in its logit space? *(Tests Contribution C4, H-M2)*

### 4.1 Dataset

**DCLM-POOL** (mlfoundations/dclm-baseline-1.0): A CommonCrawl-derived corpus used as the base for DCLM-BASELINE filtering [Li et al., 2024]. We use streaming access via HuggingFace datasets to construct 50k-document quick-run subsets per configuration.

*Why DCLM-POOL:* This corpus is the standard substrate for fastText quality filtering experiments. Using the same corpus as DCLM ensures our results directly characterize the filtering behavior that is producing the widely-used DCLM-BASELINE checkpoints. DCLM-POOL spans 240T tokens of CommonCrawl text — the demographic diversity is broad enough to produce measurable variation in H(occupation|demographic) across configurations (confirmed by H-E1 results).

**Demographic-occupation lexicon:** 20 occupation pairs from WinoBias [Zhao et al., 2018] crossed with gender-indicating demographic tokens (pronouns, gendered modifiers). Window-based co-occurrence (window_size=10, Laplace α=0.5) produces 1,800 (demographic, occupation) pairs per configuration.

### 4.2 Corpus Configurations

We evaluate 8 corpus configurations (Table 1). C0-C5 constitute a monotonic fastText filtering sweep. C6 provides a qualitatively different curation path for comparison. C7 is the negative control.

**Table 1: Corpus Configurations**

| Config | Curation Method | Expected H(occ\|demo) | Role |
|--------|----------------|----------------------|------|
| C0 | Unfiltered | High (baseline) | Reference |
| C1 | fastText ≥ 10th pct | High | H-E1 endpoint (low) |
| C2 | fastText ≥ 30th pct | Medium-high | H-E1 monotonic |
| C3 | fastText ≥ 50th pct | Medium | H-E1 monotonic |
| C4 | fastText ≥ 70th pct | Medium-low | H-E1 monotonic |
| C5 | fastText ≥ 90th pct | Low | H-E1 endpoint (high filter) |
| C6 | DoReMi reweighting | Unknown | Alternative curation |
| C7 | C3 + shuffled demographics | Same as C3 | Negative control |

### 4.3 Baselines for RQ3 (H-M2)

For the model logit margin probe (RQ3), we compare against:

- **C0 (unfiltered)**: Natural reference — model trained without quality filtering.
- **C7 (shuffled-demographic)**: Negative control — same entropy as C3, conditional associations destroyed by random permutation of demographic tokens within documents.

*Why these baselines:* C0 represents the typical unfiltered pretraining condition. C7 enables causal identification — if C7 produces different logit margins than C0, and C3 (same entropy as C7) produces yet different margins, this implicates the conditional association structure specifically.

### 4.4 Implementation Details

**Corpus audit pipeline (H-E1, H-M1):**
- Language: Python 3.10
- Key libraries: HuggingFace `datasets` (streaming), `numpy`, `scipy.stats`
- Components: `CorpusFilter` (fastText/DoReMi filtering), `EntropyMeasure` (H(occ|demo) computation), `LogOddsComputer` (log-odds matrix, Laplace smoothing), `StatisticalTests` (Spearman + Bootstrap CI)
- Conda environment: `youra-h-e1` (H-E1), `youra-h-m1` (H-M1)
- Validation: 57/57 unit tests passing (H-E1); 26/26 tasks completed (H-M1)

**Model training (H-M2):**
- Model: Pythia-1B, GPT-NeoX architecture (hidden_size=2048, 16 transformer layers, ~1.3B parameters)
- Training framework: hf_trainer_fallback (gpt-neox framework was planned but unavailable; Hugging Face Trainer used as substitute)
- Training hyperparameters: LR=2e-5, batch_size=256, cross-entropy loss
- Training budget: ~95,368 steps (≈50B tokens, quick-run; 100B token full-scale planned)
- Hardware: NVIDIA H100 NVL, CUDA_VISIBLE_DEVICES=1
- Probe: 50+ WinoBias completion templates × 20 occupation pairs × 2 pronouns = 2,160 probe samples per configuration
- Conda environment: `youra-h-m2`

Figure 14 (03_training_curves.png) shows the training loss curves per corpus configuration for H-M2.

### 4.5 Evaluation Metrics

**Primary metrics (H-E1):**
- *H(occupation|demographic)*: Conditional entropy in bits; computed across all 1,800 (demographic, occupation) pairs per configuration
- *Relative entropy change*: (H(C5) − H(C1)) / H(C1) × 100%; gate threshold: ≥5% absolute relative change
- *Spearman ρ*: Rank correlation of H values across C1-C5 filtering intensity; gate: ρ≠0, p<0.05
- *Bootstrap CI (n=1000)*: For H(C5)−H(C1); gate: CI excludes zero

**Primary metrics (H-M1):**
- *Mean log-odds across 1,800 pairs per configuration*
- *Spearman ρ*: Rank correlation of mean log-odds vs. filtering intensity; gate: |ρ|>0, p<0.05

**Primary metrics (H-M2):**
- *Mean logit margin*: Mean difference in log-probability (demographic-congruent vs. incongruent) per configuration
- *Spearman ρ*: Rank correlation of logit margins vs. corpus H(occ|demo); gate: ρ>0, p<0.01
- *Negative control gap*: |logit_margin(C7) − logit_margin(C0)|; gate: >0.01

Statistical significance is evaluated at α=0.05 for H-E1/H-M1 and α=0.01 for H-M2 (stricter gate for model-level mechanism).
