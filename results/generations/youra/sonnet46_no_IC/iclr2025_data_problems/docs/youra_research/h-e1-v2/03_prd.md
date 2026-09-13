# Product Requirements Document (PRD)
## H-E1-V2: Scale-Dependent Optimal Curation — Existence Test (Scope-Reduced)

**Version:** 1.0  
**Date:** 2026-08-04  
**Author:** Anonymous  
**Hypothesis:** H-E1-V2 (EXISTENCE / INCREMENTAL from H-E1)  
**Tier:** LIGHT (≤15 tasks)  
**Source:** Phase 2C Experiment Brief (02c_experiment_brief.md)  
**Modified From:** H-E1 (scope reduction: 70M/160M → 14M/31M, 50B → 1B tokens, Dolma → FineWeb)

---

## stepsCompleted

- [x] Executive Summary
- [x] Problem Statement
- [x] Scope and Constraints
- [x] Functional Requirements (FR-1 through FR-7)
- [x] Non-Functional Requirements
- [x] Success Criteria
- [x] Dependencies (packages, repos, datasets)
- [x] Traceability Matrix

---

## 1. Executive Summary

This experiment tests whether a significant Scale × Curation interaction effect exists in HellaSwag 0-shot scores when training Pythia 14M and 31M language models from scratch on factorially curated FineWeb data. Specifically: do smaller models (14M params) perform best under more aggressive perplexity filtering (τ=20), while larger models (31M params) tolerate less aggressive filtering (τ=50)?

This is a **scope-reduced rerun of H-E1**, which demonstrated that the pipeline mechanism is correct (23/23 tests pass, 36 PoC runs complete) but that proxy-model scale (7M/16M) was insufficient to manifest scale-dependent interaction effects. Pythia 14M/31M with 1B tokens each (real Pythia configs) are tractable in 2-3 days per run on H100 and should produce statistically detectable interactions.

**Success Gate (MUST_WORK — direction-based):**  
1. τ*(14M) < τ*(31M): smaller model achieves peak HellaSwag at lower PPL threshold  
2. Both models above random baseline (HellaSwag acc_norm > 0.25) at 1B tokens  
3. Either: acc_norm(14M, τ=20) > acc_norm(14M, τ=50) OR acc_norm(31M, τ=50) ≥ acc_norm(31M, τ=20)

---

## 2. Problem Statement

H-E1 verified that the curation pipeline is mechanically correct but could not produce statistical interaction signal at proxy-model scale (7M/16M). The root cause: scale-dependent curation effects require clearly separated model capacity levels. Pythia 14M vs 31M (2.2× parameter ratio) provides sufficient separation while remaining computationally tractable (1B tokens ≈ 500 optimizer steps ≈ 2-3 hours per run on H100).

**Hypothesis Statement (H-E1-V2):**  
Under fixed Pythia architecture and fixed 1B token budget on FineWeb, if PPL threshold τ ∈ {20,35,50} and dedup aggressiveness d ∈ {J=0.7, J=0.9} are independently varied across model scales {14M, 31M}, then a significant Scale × Curation interaction effect will appear in HellaSwag 0-shot scores because smaller models benefit more from aggressive quality filtering while larger models can leverage noisier but more diverse data.

---

## 3. Scope and Constraints

### In Scope
- Corpus curation: PPL filtering (τ ∈ {20, 35, 50}) + MinHash deduplication (J ∈ {0.7, 0.9}) on FineWeb
- Training: Pythia 14M and 31M from scratch on each of 6 corpus variants × 2 seeds = 24 total runs
- Evaluation: HellaSwag 0-shot (acc_norm) at final checkpoint + 10 intermediate checkpoints per run
- Statistical analysis: direction-based interaction check (τ*(14M) < τ*(31M))
- Reuse of h-e1/code/ codebase (only config changes required)

### Out of Scope
- Models larger than 31M parameters (compute constraint)
- MMLU evaluation (floor at these scales; HellaSwag only per Phase 2C decision)
- Dolma v1.7 (replaced by FineWeb for simpler streaming access)
- ANCOVA contamination correction (HellaSwag is not MMLU — lower contamination risk)
- Statistical significance thresholds (direction-only gate for EXISTENCE PoC)

### Constraints
- Total token budget: **1B tokens per run** (reduced from 50B in H-E1)
- Must reuse h-e1/code/ codebase (NeMo-Curator + GPT-NeoX + lm-eval already integrated)
- 2 seeds per condition (reduced from 3 — sufficient for error bars at PoC scale)
- FineWeb streaming via HuggingFace datasets API (no local Dolma download required)
- Hardware: single H100 GPU per run (24 runs parallelizable)

---

## 4. Functional Requirements

### FR-1: Data Corpus Curation Pipeline
**Priority:** Critical  
**Source:** Phase 2C §Dataset; h-e1/code/curate.py (reuse)

Implement NeMo-Curator pipeline to generate 6 corpus variants from FineWeb:

| Variant | PPL τ | Dedup J | Expected Retention | est. Tokens Available |
|---------|-------|---------|-------------------|----------------------|
| C1 | 20 | 0.7 | ~12-15% of sample | ~150M |
| C2 | 20 | 0.9 | ~14-17% of sample | ~170M |
| C3 | 35 | 0.7 | ~35-40% of sample | ~400M |
| C4 | 35 | 0.9 | ~38-43% of sample | ~430M |
| C5 | 50 | 0.7 | ~55-60% of sample | ~650M |
| C6 | 50 | 0.9 | ~60-65% of sample | ~700M |

**All variants padded to exactly 1B tokens** via repeated sampling if retention < 1B.

**PPL Filtering (FR-1a):**
- Score documents with GPT-2 perplexity (HuggingFace `gpt2` model)
- Retain documents with PPL ≤ τ
- Tokenize with GPT-NeoX-20B tokenizer (50257 vocab, BPE)

**MinHash Deduplication (FR-1b):**
- Use NeMo-Curator `FuzzyDeduplicationWorkflow`
- J=0.7 (strict): `num_bands=25, minhashes_per_band=10, char_ngrams=24`
- J=0.9 (loose): `num_bands=15, minhashes_per_band=15, char_ngrams=24`
- Fallback: exact dedup (proven functional in h-e1)

**Dataset Loading (FR-1c):**
```python
from datasets import load_dataset
dataset = load_dataset("HuggingFaceFW/fineweb", name="default", split="train", streaming=True)
```
Sample 15B tokens from stream for curation input (buffer for all 6 conditions).

**Token Budget Enforcement (FR-1d):**
- After filtering + dedup: sample exactly 1B tokens per variant
- If available < 1B: repeat-sample (circular) with seed-based offset per seed

### FR-2: Dataset Preprocessing
**Priority:** Critical  
**Source:** Phase 2C §Dataset; h-e1/code/preprocess.py (reuse)

- Convert filtered corpora to GPT-NeoX memory-mapped binary format
- Use `tools/preprocess_data.py` from EleutherAI/gpt-neox
- Tokenizer: `utils/20B_tokenizer.json` (GPT-NeoX-20B tokenizer)
- No train/val/test split required (HellaSwag is external benchmark, not held-out data)
- Record token count per variant after preprocessing

### FR-3: Model Training
**Priority:** Critical  
**Source:** Phase 2C §Training Protocol; h-e1 config + Pythia official configs

Train Pythia 14M and Pythia 31M from scratch on each of 6 corpus variants × 2 seeds = **24 total runs**.

**Pythia-14M config:**
- Architecture: decoder-only transformer, 6 layers, hidden_size=128, num_attention_heads=4, seq_length=2048
- RoPE positional embedding
- lr=1e-3, min_lr=1e-4, cosine decay, warmup=1% of steps (~5 steps)
- batch_size=2M tokens, total_tokens=1B → **~500 optimizer steps**
- Precision: fp16 (suitable for 14M — no bf16 needed)

**Pythia-31M config:**
- Architecture: decoder-only transformer, 6 layers, hidden_size=256, num_attention_heads=8, seq_length=2048
- RoPE positional embedding
- lr=1e-3, min_lr=1e-4, cosine decay, warmup=1% of steps
- batch_size=2M tokens, total_tokens=1B → **~500 optimizer steps**
- Precision: fp16

**Common training settings:**
- Optimizer: AdamW (β₁=0.9, β₂=0.95, ε=1e-8, weight_decay=0.1)
- Gradient clipping: 1.0
- Seeds: {1, 2} per condition
- Checkpoint interval: **every 100M tokens** (10 checkpoints per run at steps ≈50,100,...,500)
- Framework: GPT-NeoX v2.0 (EleutherAI/gpt-neox)

```bash
python deepy.py train.py \
  configs/pythia-14m.yml \
  configs/fineweb-filtered-t{tau}-j{j}-seed{seed}.yml
```

### FR-4: Model Evaluation
**Priority:** Critical  
**Source:** Phase 2C §Evaluation; h-e1/code/evaluate.py (reuse)

Evaluate all 24 final checkpoints + 240 intermediate checkpoints (24 runs × 10 checkpoints):

**Primary Metric: HellaSwag 0-shot acc_norm**
- Dataset: Rowan/hellaswag (HuggingFace)
- **Full validation set: 10,003 examples** (no subsampling)
- Task: commonsense NLI completion (4-choice, normalized by continuation length)
- Expected range: 0.28–0.35 (above chance=0.25)

**Evaluation command:**
```bash
lm_eval --model hf \
    --model_args pretrained=./output/h-e1-v2/run_{condition}/checkpoint_{step},dtype=float32 \
    --tasks hellaswag \
    --num_fewshot 0 \
    --device cuda:0 \
    --batch_size auto
```

**Python API (for batch evaluation):**
```python
import lm_eval
results = lm_eval.simple_evaluate(
    model="hf",
    model_args=f"pretrained={checkpoint_path},dtype=float32",
    tasks=["hellaswag"],
    num_fewshot=0,
    batch_size=8,
    device="cuda:0",
)
acc_norm = results["results"]["hellaswag"]["acc_norm,none"]
```

### FR-5: Statistical Analysis
**Priority:** Critical  
**Source:** Phase 2C §PoC Success Check; h-e1/code/analyze.py (reuse with modifications)

**Direction-based interaction check (EXISTENCE PoC):**
```python
# Primary check: which PPL threshold maximizes HellaSwag per scale?
results_14m = {tau: mean(acc_norm for seed in seeds) for tau in [20,35,50]}
results_31m = {tau: mean(acc_norm for seed in seeds) for tau in [20,35,50]}

tau_star_14m = max(results_14m, key=results_14m.get)  # optimal τ for 14M
tau_star_31m = max(results_31m, key=results_31m.get)  # optimal τ for 31M
direction_confirmed = tau_star_14m <= tau_star_31m     # 14M prefers lower τ

# Interaction check (simplified ANOVA for direction signal)
interaction_exists = (
    (results_14m[20] > results_14m[50])   # smaller model benefits from stricter filtering
    OR (results_31m[50] >= results_31m[20]) # larger model tolerates looser filtering
)
above_random = all(acc > 0.25 for acc in results_14m.values() + results_31m.values())

gate_pass = interaction_exists AND above_random
```

**Additional analysis:**
- Learning curve plots (HellaSwag at each 100M-token checkpoint)
- Dedup interaction: effect of J=0.7 vs J=0.9 by scale
- Corpus size after filtering per condition (token counts)

**Gate Result Recording:**
- PASS → `validation.gate.satisfied = true`, route to H-M1
- FAIL → `validation.gate.satisfied = false`, `gate.result = PARTIAL` or `FAIL`, route to Phase 2A-Dialogue

### FR-6: Results Collection and Storage
**Priority:** High  
**Source:** h-e1/code/ (reuse results schema)

Store per-run results in structured format:
- Columns: `scale, ppl_threshold, dedup_j, seed, checkpoint_tokens, hellaswag_acc_norm`
- Format: CSV
- Location: `results/h-e1-v2/results.csv`
- Also: `h-e1-v2/experiment_results.json` (full evaluation output per checkpoint)

### FR-7: Visualization
**Priority:** Medium  
**Source:** Phase 2C §Visualization Requirements; h-e1/code/visualize.py (reuse/adapt)

**Required Figure (Mandatory):**
- Bar chart: HellaSwag acc_norm by Scale × PPL-threshold × Dedup-J (2×3×2 factorial grid, error bars across 2 seeds)

**Additional Figures:**
1. Scale × Curation interaction heatmap: 2 rows (14M, 31M) × 3 PPL thresholds × 2 dedup conditions
2. Learning curves by condition: acc_norm at each 100M-token checkpoint, all 24 runs (12 per scale)
3. Interaction plot: PPL threshold on x-axis, acc_norm on y-axis, separate lines for 14M vs 31M, panels for J=0.7 vs J=0.9
4. Corpus size violin plot: token count per condition after filtering + dedup

Output directory: `h-e1-v2/figures/`

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- All random seeds fixed (seeds 1 and 2) and logged
- NeMo-Curator config stored per corpus variant (YAML)
- GPT-NeoX training configs stored per run

### NFR-2: Compute Efficiency
- GPU-accelerated MinHash via NeMo-Curator (cuDF backend; fallback: exact dedup)
- FP16 mixed precision for training
- Parallel evaluation across checkpoints (batch mode)
- Estimated: 2-3 hours per training run on single H100; 24 runs = 48-72 GPU-hours total

### NFR-3: Checkpoint Strategy
- Save checkpoint every 100M tokens (10 per run = 240 total across 24 runs)
- Convert to HuggingFace format for lm-eval: `tools/convert_to_hf.py`
- Store learning curve data for downstream H-M3 analysis

### NFR-4: Codebase Reuse
- **Primary**: reuse h-e1/code/ with config-only changes
- Config changes required: model scale (14M/31M), token budget (1B), dataset (FineWeb), evaluation (HellaSwag only)
- Existing 23/23 tests must continue to pass
- Fallback: exact dedup (proven in h-e1 when NeMo GPU unavailable)

### NFR-5: Failure Handling
- IF τ=20 corpus yields < 100M tokens: reduce to 2 PPL conditions (τ=35,50) and note limitation
- IF training loss diverges (NaN): reduce lr by 10× and rerun affected seed only
- IF HellaSwag eval < 0.25 (below chance) at 1B tokens: flag as compute failure, not hypothesis failure

---

## 6. Success Criteria

| Criterion | Threshold | Measurement | Gate |
|-----------|-----------|-------------|------|
| **Direction confirmed** | τ*(14M) ≤ τ*(31M) | argmax HellaSwag per scale | MUST_WORK |
| **14M benefits from strict filtering** | acc_norm(14M,τ=20) > acc_norm(14M,τ=50) | mean across 2 seeds | MUST_WORK (either/or with below) |
| **31M tolerates loose filtering** | acc_norm(31M,τ=50) ≥ acc_norm(31M,τ=20) | mean across 2 seeds | MUST_WORK (either/or with above) |
| **Above random** | acc_norm > 0.25 for all conditions | all 24 final checkpoints | MUST_WORK |
| **Run completeness** | 24/24 runs complete | training log count | Required |
| **Eval completeness** | 240 checkpoint evaluations | eval results count | Required |

---

## 7. Dependencies

### 7.1 Python Packages

```
# Core ML (reuse h-e1 environment)
torch>=2.0.0
transformers>=4.35.0
datasets>=2.14.0
deepspeed>=0.10.0

# Data Curation
nemo-curator>=0.3.0  # GPU MinHash; fallback to exact dedup

# Evaluation
lm-eval>=0.4.0

# Statistical Analysis
scipy>=1.11.0
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

| Repository | Purpose | Version |
|-----------|---------|---------|
| EleutherAI/gpt-neox | Pythia training framework | v2.0 |
| NVIDIA/NeMo-Curator | GPU-accelerated corpus curation | ≥0.3.0 |
| EleutherAI/lm-evaluation-harness | HellaSwag 0-shot evaluation | ≥0.4.0 |

### 7.3 Datasets

| Dataset | Source | Access | HuggingFace ID | Manual Download? |
|---------|--------|--------|----------------|-----------------|
| **FineWeb** | HuggingFaceFW | HuggingFace streaming | `HuggingFaceFW/fineweb` | No (streaming) |
| **HellaSwag** | Rowan | HuggingFace (auto via lm-eval) | `Rowan/hellaswag` | No (auto) |
| **GPT-2** | OpenAI | HuggingFace (for PPL scoring) | `gpt2` | No (auto) |

**No manual dataset downloads required.** All datasets accessible via HuggingFace streaming.

### 7.4 Hardware Requirements

- GPU: NVIDIA H100 (or A100 80GB) per training run
- Storage: ~100GB per corpus variant (6 × 1B tokens tokenized) + checkpoints (~50GB per model scale)
- Total estimated storage: ~1TB
- Compute: 24 runs × ~3 hours/run = ~72 GPU-hours

### 7.5 Inherited Codebase

| Module | Location | Reuse Status |
|--------|----------|-------------|
| curate.py | h-e1/code/curate.py | Reuse, update dataset=FineWeb + thresholds |
| preprocess.py | h-e1/code/preprocess.py | Reuse unchanged |
| train (GPT-NeoX) | h-e1/code/train/ | Reuse, update model configs |
| evaluate.py | h-e1/code/evaluate.py | Reuse, update tasks=hellaswag only |
| analyze.py | h-e1/code/analyze.py | Reuse, adapt to direction-based check |
| visualize.py | h-e1/code/visualize.py | Reuse, adapt figures |
| tests/ | h-e1/code/tests/ | Reuse, all 23 tests must pass |

---

## 8. Traceability Matrix

| Requirement | Source |
|------------|--------|
| FR-1 (Corpus Curation) | Phase 2C §Dataset; NeMo-Curator docs |
| FR-1a (PPL filtering) | Phase 2C §Dataset; Exa: NVIDIA-NeMo/Curator |
| FR-1b (MinHash dedup) | Phase 2C §Dataset; Exa: NeMo Curator docs |
| FR-2 (Preprocessing) | Phase 2C §Dataset; h-e1/code/preprocess.py |
| FR-3 (Training) | Phase 2C §Training Protocol; Exa: EleutherAI/pythia configs |
| FR-4 (Evaluation) | Phase 2C §Evaluation; Exa: lm-evaluation-harness |
| FR-5 (Statistics) | Phase 2C §PoC Success Check; h-e1/code/analyze.py |
| FR-6 (Results) | Phase 2C §Dataset; h-e1 results schema |
| FR-7 (Visualization) | Phase 2C §Visualization Requirements; h-e1/code/visualize.py |
| Scope reduction | verification_state.yaml scope_reduction section |
| Codebase reuse | verification_state.yaml failure_context.lessons_learned |
