# Product Requirements Document (PRD)
## H-E1: Scale-Dependent Optimal Curation — Existence Test

**Version:** 1.0  
**Date:** 2026-08-04  
**Author:** Anonymous  
**Hypothesis:** H-E1 (EXISTENCE / FOUNDATION)  
**Tier:** LIGHT (≤15 tasks)  
**Source:** Phase 2C Experiment Brief (02c_experiment_brief.md)

---

## 1. Executive Summary

This experiment tests whether a significant Scale × Curation interaction effect exists in downstream benchmark scores when training Pythia-style language models on factorially curated datasets. Specifically: do smaller models (70M params) perform best under more aggressive data filtering, while larger models (160M params) perform best under less aggressive filtering?

**Success Gate (MUST_WORK):** Scale × PPL-threshold ANOVA interaction p < 0.05, partial η² ≥ 0.15, and τ*(70M) < τ*(160M).

---

## 2. Problem Statement

Pre-training data quality curation (perplexity filtering + MinHash deduplication) has scale-dependent effects that are not well understood. This experiment produces empirical evidence for or against the interaction hypothesis using a fully factorial 2×3×2 design across model scales, PPL thresholds, and deduplication thresholds.

**Hypothesis Statement:**  
Under fixed Pythia architecture and fixed token budget on open English corpora (Dolma, FineWeb), if PPL threshold τ ∈ {20,35,50} and dedup aggressiveness d ∈ {J=0.7, J=0.9} are independently varied across model scales {70M, 160M}, then a significant Scale × Curation interaction effect will appear in MMLU 4-shot and HellaSwag 0-shot scores because the optimal data quality configuration depends on model capacity.

---

## 3. Scope and Constraints

### In Scope
- Corpus curation: PPL filtering (τ ∈ {20, 35, 50}) + MinHash deduplication (J ∈ {0.7, 0.9})
- Training: Pythia 70M and 160M from scratch on each of 12 corpus variants (6 per corpus × 2 corpora)
- Evaluation: MMLU 4-shot, HellaSwag 0-shot on all 72 trained models (24 conditions × 3 seeds)
- Statistical analysis: 2-way ANOVA with ANCOVA (contamination rate as covariate)
- Replication: FineWeb corpus as external validity check

### Out of Scope
- Models larger than 160M parameters (Phase 2B budget constraint)
- Custom evaluation tasks beyond MMLU + HellaSwag
- Architecture modifications to Pythia
- Online/streaming curation pipelines

### Constraints
- Total token budget: 50B tokens per run (PoC; not full Pythia 300B)
- Must use GPT-NeoX training framework (Pythia compatibility)
- Must use NeMo-Curator for GPU-accelerated curation
- 3 seeds per condition minimum (variance estimation)

---

## 4. Functional Requirements

### FR-1: Data Corpus Curation Pipeline
**Priority:** Critical  
**Source:** Phase 2C §Dataset

Implement NeMo-Curator pipeline to generate 12 corpus variants (6 per corpus):

| Variant | PPL τ | Dedup J | Expected Retention |
|---------|-------|---------|-------------------|
| C1 | 20 | 0.7 | ~55% (~1.65T tokens) |
| C2 | 20 | 0.9 | ~60% (~1.80T tokens) |
| C3 | 35 | 0.7 | ~70% (~2.10T tokens) |
| C4 | 35 | 0.9 | ~75% (~2.25T tokens) |
| C5 | 50 | 0.7 | ~80% (~2.40T tokens) |
| C6 | 50 | 0.9 | ~85% (~2.55T tokens) |

Apply to both Dolma v1.7 (primary) and FineWeb (replication).

**PPL Filtering (FR-1a):**
- Score documents with GPT-2 perplexity (HuggingFace `gpt2` model)
- Retain documents with PPL ≤ τ
- Tokenize with NeoX tokenizer (20B_tokenizer.json)

**MinHash Deduplication (FR-1b):**
- Use NeMo-Curator `FuzzyDuplicates` with `FuzzyDuplicatesConfig`
- J=0.7 → num_buckets=20, hashes_per_bucket=13
- J=0.9 → num_buckets=8, hashes_per_bucket=13
- char_ngrams=24, minhash_length=256, seed=42

**Contamination Removal (FR-1c):**
- Run lm-sys/llm-decontaminator against MMLU + HellaSwag test sets on all 12 corpora
- Record contamination rate CR(condition) for ANCOVA covariate

**Corpus Statistics (FR-1d):**
- Record token count per variant (post-filtering)
- Record CR(condition) per variant

### FR-2: Dataset Preprocessing
**Priority:** Critical

- Download Dolma v1.7: `allenai/dolma` from HuggingFace (streaming)
- Download FineWeb: `HuggingFaceFW/fineweb` from HuggingFace (streaming)
- Convert to NeoX memory-mapped binary format via `tools/preprocess_data.py`
- Split: 95% train / 2.5% val / 2.5% test

### FR-3: Model Training
**Priority:** Critical  
**Source:** Phase 2C §Training Protocol

Train Pythia 70M and 160M from scratch on each of 12 corpus variants × 3 seeds = 72 total runs.

**Pythia 70M config:**
- 6 layers, hidden_size=512, num_attention_heads=8, seq_length=2048
- RoPE positional embedding, rotary-pct=0.25
- lr=1e-3, min_lr=1e-4, cosine decay, warmup=0.01
- batch_size=2M tokens, total_tokens=50B (25,000 steps)

**Pythia 160M config:**
- 12 layers, hidden_size=768, num_attention_heads=12, seq_length=2048
- RoPE positional embedding, rotary-pct=0.25
- lr=6e-4, min_lr=6e-5, cosine decay, warmup=0.01
- batch_size=2M tokens, total_tokens=50B (25,000 steps)

**Common training settings:**
- Optimizer: AdamW (β₁=0.9, β₂=0.95, ε=1e-8)
- Weight decay: 0.1, gradient clipping: 1.0
- Precision: FP16 + DeepSpeed ZeRO Stage 1
- Seeds: {1, 2, 3} per condition
- Checkpoints: every 5B tokens (10 checkpoints per run)
- Framework: GPT-NeoX v1.0 + DeepSpeed

### FR-4: Model Evaluation
**Priority:** Critical  
**Source:** Phase 2C §Evaluation

Evaluate all 720 checkpoint–condition combinations (72 runs × 10 checkpoints each):

**Primary Metrics:**
- MMLU 4-shot accuracy (57 subtasks, mean)
  - Expected 70M: 25–27%
  - Expected 160M: 27–30%
- HellaSwag 0-shot accuracy
  - Expected 70M: 35–40%
  - Expected 160M: 45–50%

**Evaluation Tool:** EleutherAI/lm-evaluation-harness
```bash
lm-eval run \
  --model hf \
  --model_args pretrained=/path/to/checkpoint \
  --tasks mmlu,hellaswag \
  --num_fewshot 4 \
  --output_path ./eval_results/
```

**Note:** Full standard test sets must be used (no subsampling):
- MMLU: 14,042 test examples across 57 subtasks
- HellaSwag: 10,042 validation examples

### FR-5: Statistical Analysis
**Priority:** Critical  
**Source:** Phase 2C §Evaluation

**Primary Analysis: 2-Way ANOVA with ANCOVA**
```python
# ANCOVA: Scale × PPL interaction with contamination as covariate
model = ols('mmlu_4shot ~ C(scale) * C(ppl_threshold) + contamination_rate', data=results_df).fit()
anova_table = sm.stats.anova_lm(model, typ=2)
interaction_p = anova_table.loc["C(scale):C(ppl_threshold)", "PR(>F)"]
interaction_eta2 = compute_partial_eta2(anova_table, "C(scale):C(ppl_threshold)")
```

**Direction Check:**
```python
tau_star_70m = results_df[results_df.scale==70].groupby('ppl_threshold')['mmlu_4shot'].mean().idxmax()
tau_star_160m = results_df[results_df.scale==160].groupby('ppl_threshold')['mmlu_4shot'].mean().idxmax()
direction_confirmed = tau_star_70m < tau_star_160m
```

**Additional Tests:**
- Scale × Dedup ANOVA (secondary)
- Levene's test for variance homogeneity
- Post-hoc pairwise comparisons for simple effects

**Gate Check:**
- interaction_p < 0.05 AND interaction_eta2 ≥ 0.15 AND direction_confirmed → PASS
- Otherwise → FAIL (escalate to Phase 2A-Dialogue)

### FR-6: Results Collection and Storage
**Priority:** High

Store per-run results in structured DataFrame:
- Columns: `scale, ppl_threshold, dedup_j, corpus, seed, mmlu_4shot, hellaswag_0shot, contamination_rate`
- Format: CSV + Parquet
- Location: `results/h-e1/results.csv`

### FR-7: Visualization
**Priority:** Medium

**Required Figure:**
- Bar chart: MMLU 4-shot and HellaSwag 0-shot by Scale × PPL-threshold (2×3 factorial, error bars across 3 seeds)

**Additional Figures:**
1. Interaction Plot: benchmark score vs τ, separate lines for 70M/160M
2. Dedup Interaction Plot: effect of J=0.7 vs J=0.9 by scale (sign reversal expected)
3. FineWeb Replication Panel: side-by-side Dolma vs FineWeb interaction plots
4. Corpus Size × Condition Heatmap: token counts per filter condition
5. Contamination Rate Table: CR(condition) per corpus variant

Output: `docs/youra_research/h-e1/figures/`

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- All random seeds fixed and logged
- All corpus preprocessing steps logged with version hashes
- NeMo-Curator config stored per corpus variant

### NFR-2: Compute Efficiency
- GPU-accelerated MinHash via NeMo-Curator (not CPU-only)
- DeepSpeed ZeRO Stage 1 for training memory efficiency
- Batch evaluation (not one-by-one checkpoint evaluation)

### NFR-3: Checkpoint Strategy
- Save checkpoint every 5B tokens (10 per run)
- Store checkpoints for H-M3 learning curve analysis (downstream)
- Convert to HuggingFace format for evaluation: `tools/convert_to_hf.py`

### NFR-4: Failure Handling
- IF contamination covariate absorbs >50% of interaction variance: pivot primary DV to HellaSwag
- IF corpus size diff >30% between J=0.7 and J=0.9: normalize token budget before training
- IF 3 seeds σ > 1pp on control: investigate training instability

---

## 6. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| **Interaction p-value** | p < 0.05 | ANOVA Scale × PPL-threshold |
| **Effect size** | partial η² ≥ 0.15 | ANOVA Scale × PPL-threshold |
| **Direction** | τ*(70M) < τ*(160M) | Post-hoc argmax per scale |
| **PoC completeness** | 72 runs complete | Training log count |
| **Evaluation completeness** | 720 evaluations | Eval results file count |

---

## 7. Dependencies

### 7.1 Python Packages

```
# Core ML
torch>=2.0.0
transformers>=4.35.0
datasets>=2.14.0
deepspeed>=0.10.0
accelerate>=0.21.0

# Data Curation
nemo-curator>=0.3.0

# Training Framework (separate install)
# git clone https://github.com/EleutherAI/gpt-neox.git

# Evaluation
lm-eval>=0.4.0

# Statistical Analysis
scipy>=1.11.0
statsmodels>=0.14.0
numpy>=1.24.0
pandas>=2.0.0

# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0

# Utilities
pyyaml>=6.0
tqdm>=4.65.0
```

### 7.2 External Repositories

| Repository | Purpose | URL |
|-----------|---------|-----|
| EleutherAI/gpt-neox | Pythia training framework | https://github.com/EleutherAI/gpt-neox |
| NVIDIA/NeMo-Curator | GPU-accelerated corpus curation | https://github.com/NVIDIA/NeMo-Curator |
| EleutherAI/lm-evaluation-harness | MMLU + HellaSwag evaluation | https://github.com/EleutherAI/lm-evaluation-harness |
| lm-sys/llm-decontaminator | Benchmark contamination removal | https://github.com/lm-sys/llm-decontaminator |

### 7.3 Datasets (Manual Download Required)

| Dataset | Source | Size | HuggingFace ID |
|---------|--------|------|----------------|
| **Dolma v1.7** | AI2 | ~3T tokens | `allenai/dolma` |
| **FineWeb** | HuggingFace | ~15T tokens | `HuggingFaceFW/fineweb` |

Both require streaming download due to size. Manual setup of local storage required.

### 7.4 Hardware Requirements

- GPU: NVIDIA A100 80GB or equivalent (for NeMo-Curator GPU MinHash)
- Storage: ~10TB for corpus variants + checkpoints
- Compute: ~72 × 50B tokens training runs (substantial GPU-days)

---

## 8. Traceability Matrix

| Requirement | Source |
|------------|--------|
| FR-1 (Corpus Curation) | Phase 2C §Dataset; Phase 2B §2.2 H-E1 |
| FR-2 (Preprocessing) | Phase 2C §Dataset; Phase 2B controlled variables |
| FR-3 (Training) | Phase 2C §Training Protocol; EleutherAI/pythia YML configs |
| FR-4 (Evaluation) | Phase 2C §Evaluation; lm-evaluation-harness |
| FR-5 (Statistics) | Phase 2C §Mechanism Verification; Phase 2B §2.2 success criteria |
| FR-6 (Results) | Phase 2C §Mechanism Verification |
| FR-7 (Visualization) | Phase 2C §Visualization Requirements |

---

## stepsCompleted

- [x] Executive Summary
- [x] Problem Statement
- [x] Functional Requirements (FR-1 through FR-7)
- [x] Non-Functional Requirements
- [x] Success Criteria
- [x] Dependencies (packages, repos, datasets)
- [x] Traceability Matrix
