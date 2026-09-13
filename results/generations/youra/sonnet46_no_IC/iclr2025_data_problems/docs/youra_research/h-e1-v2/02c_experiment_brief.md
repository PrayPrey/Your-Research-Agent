# Experiment Design: h-e1-v2

**Date:** 2026-08-04
**Author:** Anonymous
**Hypothesis Statement:** Under fixed Pythia architecture and fixed token budget on open English corpora (FineWeb), if PPL threshold τ ∈ {20,35,50} and dedup aggressiveness d ∈ {J=0.7, J=0.9} are independently varied across model scales {14M, 31M}, then a significant Scale × Curation interaction effect will appear in HellaSwag 0-shot scores because smaller models benefit more from aggressive quality filtering while larger models can leverage noisier but more diverse data.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** None (no prerequisites for h-e1-v2)
**Gate Status:** MUST_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1-v2
- **Type:** EXISTENCE
- **Prerequisites:** None (modified from h-e1 which had none)

### Gate Condition
MUST_WORK gate: Scale × Curation interaction effect must be statistically detectable in HellaSwag 0-shot scores across Pythia 14M vs 31M model scales. Direction-based success: τ*(14M) < τ*(31M), meaning smaller models prefer lower PPL thresholds.

---

## Continuation Context

**Modified from:** h-e1 (version 1, outcome: PARTIAL — PoC scale insufficient)

**Scope Reduction applied:**
- Model scales reduced from {70M, 160M} to {14M, 31M} — tractable in 2-3 days on H100
- Token budget reduced from 50B to 1B tokens
- Primary dataset changed to FineWeb (simpler streaming access than Dolma v1.7)
- Evaluation reduced to HellaSwag 0-shot only (MMLU floor issue at small scales)

### Previous Hypothesis Results (h-e1)

**h-e1 outcome (PARTIAL):**
- Pipeline mechanism fully verified: 23/23 pytest tests pass, 36 PoC runs complete
- PoC ANCOVA: p=1.0, eta²≈0 — no statistical signal at proxy-model scale (7M/16M)
- MMLU floor (0.05) for all conditions — models too small for MMLU
- Routing: Scope reduction to Pythia 14M/31M with 1B tokens

**Lessons learned applied:**
- LLM pre-training PoC requires clearly separated model scales with visible capacity gap
- 14M vs 31M (2.2× scale ratio) should be sufficient to observe interaction
- HellaSwag 0-shot is more sensitive than MMLU at small scales
- NeMo-Curator MinHash fallback to exact dedup is proven functional
- Existing codebase (h-e1/code/) is reusable — only scale/data config changes needed

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "perplexity filtering data curation pre-training experiment"**
- Results: No domain-relevant findings (Archon KB contains image/diffusion model content)
- Similarity scores: 0.41, 0.41, 0.40 — below relevance threshold
- Note: Archon KB is populated with computer vision research, not NLP/LLM pre-training

**Query 2: "MinHash deduplication training corpus scale interaction"**
- Results: No domain-relevant findings (similar image/diffusion content returned)
- Note: No LLM pre-training curation cases in current Archon KB

**Query 3: "LLM pre-training data filtering perplexity threshold" (code examples)**
- Results: No relevant code examples (diffusion model training code only)
- Archon KB does not contain NLP pre-training pipeline code

**Assessment:** Archon KB has no relevant content for LLM data curation. All implementation knowledge sourced from Exa GitHub search (higher relevance for this domain).

### Archon Code Examples

No relevant code examples found in Archon KB for this domain. See Exa findings below.

### Exa GitHub Implementations

**Query 1: "Pythia GPT-NeoX training from scratch FineWeb perplexity filtering NeMo-Curator"**

**Repository 1: EleutherAI/pythia** (⭐ ~10k)
- **URL:** https://github.com/eleutherai/pythia
- **Relevance:** PRIMARY — this is the exact model suite used in h-e1-v2
- **Architecture:** Pythia-14M and Pythia-31M available; trained with GPT-NeoX on the Pile (deduped and standard variants)
- **Key Training Config:**
  - Library: GPT-NeoX v1.0 / v2.0
  - Optimizer: Adam + ZeRO (DeepSpeed)
  - Mixed precision: fp16 (small models) / bf16 (large models)
  - Checkpoints: 154 per model, steps 0,1,2,4,8,16,32,64,128,256,512,1000,2000,...
  - Config files: `models/` directory, e.g., `pythia-160m-deduped.yml`
- **Dataset:** The Pile (pre-tokenized, ~300B tokens standard / ~207B deduped)
- **Relevant for h-e1-v2:** Config files directly adaptable for FineWeb training runs
- **Used For:** Training configuration template, model architecture reference

**Repository 2: EleutherAI/gpt-neox** (⭐ ~7k)
- **URL:** https://github.com/eleutherai/gpt-neox
- **Relevance:** HIGH — training framework used by Pythia suite
- **Key Features:**
  - Supports Slurm, MPI, multi-node (AWS, ORNL, LUMI)
  - Predefined configs for Pythia, PaLM, Falcon, LLaMA
  - Curriculum learning, Flash Attention, tensor/data parallelism
  - v1.0 = Pythia-stable; v2.0 = current
- **Training Protocol:** Adam + ZeRO + data/tensor parallelism
- **Used For:** Training loop implementation, multi-GPU setup

**Repository 3: NVIDIA-NeMo/Curator** (⭐ ~5k)
- **URL:** https://github.com/NVIDIA-NeMo/Curator
- **Relevance:** HIGH — data curation pipeline (PPL filtering + MinHash dedup)
- **Key Features:**
  - GPU-accelerated MinHash (cuDF backend)
  - FuzzyDeduplicationWorkflow with configurable Jaccard threshold
  - Quality filtering, language detection
  - Text pipeline proven at Nemotron scale (8T tokens)
- **MinHash Config for h-e1-v2:**
  - Strict (J=0.7): `FuzzyDeduplicationWorkflow(num_bands=25, minhashes_per_band=10)` (higher similarity required)
  - Loose (J=0.9): `FuzzyDeduplicationWorkflow(num_bands=15, minhashes_per_band=15)` (lower similarity required)
  - Default (J≈0.8): `num_bands=20, minhashes_per_band=13, char_ngrams=24`
- **Used For:** Data curation implementation, deduplication threshold configuration

**Query 2: "lm-evaluation-harness HellaSwag 0-shot evaluation Pythia model"**

**Repository 4: EleutherAI/lm-evaluation-harness** (⭐ ~13k)
- **URL:** https://github.com/EleutherAI/lm-evaluation-harness
- **Relevance:** PRIMARY — official evaluation framework
- **HellaSwag evaluation command:**
  ```bash
  lm_eval --model hf \
      --model_args pretrained=EleutherAI/pythia-160m,revision=step100000,dtype="float" \
      --tasks hellaswag \
      --device cuda:0 \
      --batch_size auto
  ```
- **HellaSwag task config:** `dataset_path: Rowan/hellaswag`, metric: `acc_norm` (normalized accuracy)
- **Python API:**
  ```python
  import lm_eval
  results = lm_eval.simple_evaluate(
      model="hf",
      model_args="pretrained=./output/model_checkpoint,dtype=float32",
      tasks=["hellaswag"],
      num_fewshot=0,
      batch_size=8,
      device="cuda:0",
  )
  ```
- **Used For:** Evaluation protocol, HellaSwag 0-shot implementation

**Query 3: "NeMo-Curator MinHash FuzzyDuplicates Jaccard threshold perplexity filtering GPT2"**

**Source 5: NeMo Curator Documentation (NVIDIA)**
- **URL:** https://docs.nvidia.com/nemo/curator/curate-text/process-data/deduplication/fuzzy
- **FuzzyDeduplicationWorkflow API:**
  ```python
  from nemo_curator.stages.deduplication.fuzzy.workflow import FuzzyDeduplicationWorkflow
  
  # Strict dedup (J≈0.7): more bands, fewer hashes/band
  fuzzy_strict = FuzzyDeduplicationWorkflow(
      cache_path="./cache",
      output_path="./deduped_strict",
      num_bands=25,
      minhashes_per_band=10,
      char_ngrams=24,
      seed=42
  )
  
  # Loose dedup (J≈0.9): fewer bands, more hashes/band
  fuzzy_loose = FuzzyDeduplicationWorkflow(
      cache_path="./cache",
      output_path="./deduped_loose",
      num_bands=15,
      minhashes_per_band=15,
      char_ngrams=24,
      seed=42
  )
  ```
- **Used For:** Deduplication parameter configuration for J=0.7 vs J=0.9 conditions

**Serena Analysis Needed:** false — code from Exa search is clear and directly applicable

### 🎯 Implementation Priority Assessment

**CRITICAL: For this experiment, there is no single "paper to reproduce" — h-e1-v2 is an original factorial ablation study using established tools.**

- No single "author implementation" to prioritize
- All required tools are official/primary implementations:
  - EleutherAI/pythia: official Pythia models
  - EleutherAI/gpt-neox: official training framework
  - NVIDIA-NeMo/Curator: official GPU-accelerated curation
  - EleutherAI/lm-evaluation-harness: official evaluation framework

**Recommended Implementation Path:**
- Primary: Reuse h-e1/code/ codebase (NeMo-Curator + GPT-NeoX + lm-evaluation-harness already integrated)
- Fallback: Fresh implementation from official repos above
- Justification: h-e1 codebase is production-ready (23 tests pass); only config changes needed for 14M/31M + 1B tokens + FineWeb

### Code Analysis (Serena MCP)

*Skipped* - Code from Exa search results was sufficiently clear; NeMo-Curator and lm-evaluation-harness APIs are well-documented. Existing h-e1 codebase is directly reusable.

---

## Experiment Specification

### Dataset

**Primary Dataset: FineWeb (HuggingFaceFW/fineweb)**
- **Type:** standard (real data via HuggingFace)
- **Source:** HuggingFace Hub — `HuggingFaceFW/fineweb`
- **Version:** fineweb (main split, ~15T tokens total)
- **Subset for experiment:** Sample 15B tokens via streaming (sufficient for 1B token training budget × 6 curation conditions × 2 seeds with buffer)
- **Language:** English web text
- **Why FineWeb over Dolma v1.7:**
  - Simpler streaming access via HuggingFace datasets API
  - Built-in quality scores (FineWeb-Edu classifier) for reference
  - Lower download overhead for 1B token budget experiments
  - h-e1 originally designated FineWeb as replication corpus; now using as primary

**PPL Filtering Configuration:**
- GPT-2 perplexity scoring on each document
- Three threshold conditions:
  - τ=20: Keep only documents with PPL < 20 (high quality, ~15-20% of web corpus)
  - τ=35: Keep documents with PPL < 35 (medium quality, ~40-50% of web corpus)
  - τ=50: Keep documents with PPL < 50 (low quality filter only, ~60-70% of web corpus)
- Tool: NeMo-Curator PerplexityFilter stage with GPT-2 reference model

**Deduplication Configuration:**
- Two aggressiveness conditions:
  - Strict (J=0.7): Remove near-duplicates with Jaccard similarity > 0.7 (≈15-20% removal)
  - Loose (J=0.9): Remove near-duplicates with Jaccard similarity > 0.9 (≈5-8% removal)
- Tool: NeMo-Curator FuzzyDeduplicationWorkflow
- Character n-grams: 24 (production default)

**Factorial Design:**
- 6 corpus variants: 3 PPL thresholds × 2 dedup conditions
- 2 model scales (14M, 31M) × 6 variants × 2 seeds = 24 training runs
- Total token budget per run: 1B tokens
- Checkpoint interval: 100M tokens (10 checkpoints per run)

**Corpus Size (estimated after filtering):**
- τ=20: ~150M tokens available per seed sample (requires aggressive sub-sampling from FineWeb)
- τ=35: ~400M tokens available
- τ=50: ~700M tokens available
- All conditions padded to exactly 1B tokens via repeated sampling if needed

**Loading Information:**
- Method: HuggingFace datasets (streaming)
- Identifier: `HuggingFaceFW/fineweb`
- Code:
  ```python
  from datasets import load_dataset
  dataset = load_dataset("HuggingFaceFW/fineweb", name="default", split="train", streaming=True)
  ```

**Synthetic Data Check:** PASSED — FineWeb is a real, standard web corpus dataset. Type: standard.

### Models

#### Baseline Model

**Pythia-14M (base) and Pythia-31M (base) — trained from scratch**

- **Architecture:** Decoder-only autoregressive transformer (Pythia family)
- **Pythia-14M config:** ~14M parameters, 6 layers, 4 heads, hidden dim 128
- **Pythia-31M config:** ~31M parameters, 6 layers, 8 heads, hidden dim 256
- **Tokenizer:** GPT-NeoX-20B tokenizer (50257 vocab, BPE)
- **Source:** EleutherAI/pythia config files, trained from scratch on filtered FineWeb
- **Pretrained:** False — all models trained from scratch on filtered corpora

**Training Framework:** GPT-NeoX (EleutherAI/gpt-neox v2.0)

**Loading Information:**
- Method: Custom (train from scratch using GPT-NeoX configs)
- Identifier: Config files from `EleutherAI/pythia/models/14m/` and `EleutherAI/pythia/models/31m/`
- Code:
  ```bash
  # Train from scratch using GPT-NeoX
  python deepy.py train.py configs/pythia-14m.yml configs/fineweb-filtered-t20-strict.yml
  ```

#### Proposed Model

**Architecture:** Same as baseline — this is a data curation experiment, not an architecture modification. The "proposed" condition is the optimal curation recipe for each scale.

**Core Mechanism Implementation:**

The core mechanism being tested is Scale × Curation interaction in pre-training data. The pseudo-code below describes the factorial curation pipeline — the independent variable manipulation:

```python
# Core Mechanism: Scale-Dependent Optimal Curation Pipeline
# Based on: NeMo-Curator FuzzyDeduplicationWorkflow + PerplexityFilter
# Source: https://github.com/NVIDIA-NeMo/Curator

class CurationCondition:
    """
    One factorial condition: (ppl_threshold, jaccard_threshold).
    Produces filtered corpus variant for one cell in the 3×2 factorial design.
    """
    def __init__(self, ppl_threshold: float, jaccard: float, seed: int = 42):
        self.ppl_threshold = ppl_threshold  # τ ∈ {20, 35, 50}
        self.jaccard = jaccard              # J ∈ {0.7, 0.9}
        self.seed = seed

    def get_dedup_bands(self) -> tuple[int, int]:
        # Map Jaccard target to (num_bands, minhashes_per_band)
        # Strict J=0.7: more bands → higher similarity required
        if self.jaccard <= 0.75:
            return (25, 10)   # J≈0.7
        else:
            return (15, 15)   # J≈0.9

    def apply(self, raw_stream) -> filtered_corpus:
        # Step 1: PPL filter with GPT-2 reference model
        ppl_filtered = PerplexityFilter(
            model="gpt2",
            threshold=self.ppl_threshold,
            field="text"
        ).apply(raw_stream)

        # Step 2: MinHash fuzzy deduplication
        num_bands, mph_per_band = self.get_dedup_bands()
        deduped = FuzzyDeduplicationWorkflow(
            num_bands=num_bands,
            minhashes_per_band=mph_per_band,
            char_ngrams=24,
            seed=self.seed
        ).apply(ppl_filtered)

        # Step 3: Sample exactly 1B tokens
        return TokenBudgetSampler(budget=1_000_000_000).apply(deduped)

# Factorial: 6 conditions × 2 model scales × 2 seeds = 24 runs
CONDITIONS = [
    CurationCondition(ppl_threshold=tau, jaccard=j)
    for tau in [20, 35, 50]
    for j in [0.7, 0.9]
]
```

### Training Protocol

**Reusing h-e1 training configuration (proven functional), adjusted for 14M/31M scale and 1B token budget:**

**Optimizer:** AdamW
- lr = 1e-3 (from Phase 2A controlled variables)
- weight_decay = 0.1
- β1 = 0.9, β2 = 0.95

**Learning Rate Schedule:** Cosine decay
- Warmup: 1% of total steps (≈50 steps for 5000-step run)
- Min lr: 1e-4

**Batch Size:** 2M tokens per step (micro-batch × gradient accumulation × world size)
- For 1B token budget: ~500 optimizer steps

**Total Tokens:** 1,000,000,000 per training run

**Checkpoint Interval:** Every 100M tokens (10 checkpoints per run, at steps ≈50, 100, 150, ..., 500)

**Loss Function:** Cross-entropy language modeling loss (next-token prediction)

**Mixed Precision:** fp16 (suitable for 14M/31M models — no bf16 needed)

**Seeds:** 2 per condition (seeds 1 and 2) — provides error bars without excessive compute

**Hardware Target:** Single H100 GPU per run; 24 runs parallelizable
- Estimated wall-clock: 2-3 hours per run (14M/31M, 1B tokens, H100)
- Total: 48-72 GPU-hours

**Source:** Phase 2A controlled variables + h-e1 proven configuration

### Evaluation

**Primary Metric: HellaSwag 0-shot normalized accuracy (acc_norm)**

- **Dataset:** Rowan/hellaswag (HuggingFace) — 10,003 validation examples (full validation set)
- **Task:** Commonsense NLI completion (4-choice, normalized by continuation length)
- **Evaluation:** 0-shot (no in-context examples)
- **Expected range for Pythia-14M/31M:** 0.28–0.35 (above chance=0.25, below Pythia-70M≈0.40)
- **Evaluation timing:** At final checkpoint (1B tokens) AND at each 100M-token checkpoint (10 points per run)

**Success Criteria (EXISTENCE PoC — direction-based):**
1. Scale × PPL interaction detected: τ*(14M) < τ*(31M) — smaller model prefers lower threshold
2. Direction confirmed: best_acc(14M, τ=20) > best_acc(14M, τ=50) AND best_acc(31M, τ=50) ≥ best_acc(31M, τ=20)
3. Both models above random baseline (0.25) at final checkpoint

**Expected Baseline Performance (from literature):**
- Random baseline: 0.25 (4-choice)
- Pythia-14M (Pile, full training): ~0.28-0.29 (estimated from Pythia 14M paper results)
- Pythia-31M (Pile, full training): ~0.30-0.32 (estimated)
- Source: Pythia paper (Biderman et al., 2023), ar5iv.labs.arxiv.org/html/2304.01373

**Evaluation command:**
```bash
lm_eval --model hf \
    --model_args pretrained=./output/h-e1-v2/run_{condition}/checkpoint_1B,dtype=float32 \
    --tasks hellaswag \
    --num_fewshot 0 \
    --device cuda:0 \
    --batch_size auto
```

**Metrics Loading Information:**
- Task Type: commonsense NLI (multiple-choice completion)
- Library: lm-evaluation-harness (EleutherAI)
- Code: `results["results"]["hellaswag"]["acc_norm,none"]`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** HellaSwag acc_norm bar chart: 14M vs 31M × 6 curation conditions (τ × J factorial grid)

#### Additional Figures (LLM Autonomous)
- **Scale × Curation interaction heatmap:** 2 rows (14M, 31M) × 3 PPL thresholds × 2 dedup conditions — heatmap of acc_norm values
- **Learning curves by condition:** acc_norm at each 100M-token checkpoint for all 24 conditions (12 per scale), grouped by PPL threshold
- **Interaction plot:** PPL threshold on x-axis, acc_norm on y-axis, separate lines for 14M vs 31M, separate panels for J=0.7 vs J=0.9
- **Corpus size violin plot:** Token count per condition after filtering and dedup

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1-v2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error for all 24 training runs
2. HellaSwag acc_norm(14M, τ=20) > acc_norm(14M, τ=50) — smaller model benefits from stricter filtering
3. OR: acc_norm(31M, τ=50) > acc_norm(31M, τ=20) — larger model benefits from looser filtering
4. Both models above random chance (>0.25) at final checkpoint

**Gate type:** MUST_WORK — if interaction direction not confirmed, pipeline halts for Phase 2A revisit.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**No domain-relevant sources found in Archon KB.** Current Archon KB is populated with computer vision and diffusion model content. Queries run:
- "perplexity filtering data curation pre-training experiment" — returned image generation repos (similarity 0.41)
- "MinHash deduplication training corpus scale interaction" — returned LAION/diffusers content (similarity 0.44)
- "LLM pre-training data filtering perplexity threshold" (code examples) — returned diffusion training scripts

**Implication:** All implementation knowledge sourced from Exa GitHub, which provided higher-quality domain-specific results.

### B. GitHub Implementations (Exa)

**Repository 1: EleutherAI/pythia**
- **URL:** https://github.com/eleutherai/pythia
- **Query:** "Pythia GPT-NeoX training from scratch FineWeb perplexity filtering NeMo-Curator"
- **Key Extracted:**
  - Model configs for 14M, 31M, 70M, 160M, etc.
  - Training with GPT-NeoX, Adam + ZeRO, data/tensor parallelism
  - 154 checkpoints per model for training dynamics analysis
  - Tokenizer: `utils/20B_tokenizer.json`
- **Used For:** Training configuration template, model scale selection confirmation

**Repository 2: EleutherAI/gpt-neox**
- **URL:** https://github.com/eleutherai/gpt-neox
- **Query:** Same as above
- **Key Extracted:**
  - Multi-node training support (Slurm, MPI)
  - Flash Attention integration
  - Predefined Pythia configs
  - Version 1.0 (Pythia-stable), Version 2.0 (current)
- **Used For:** Training framework implementation

**Repository 3: NVIDIA-NeMo/Curator**
- **URL:** https://github.com/NVIDIA-NeMo/Curator
- **Query:** Same as above
- **Key Extracted:**
  - FuzzyDeduplicationWorkflow with `num_bands`, `minhashes_per_band` control
  - Default parameters: num_bands=20, minhashes_per_band=13, char_ngrams=24 → J≈0.8
  - Strict J=0.7: num_bands=25, minhashes_per_band=10
  - Loose J=0.9: num_bands=15, minhashes_per_band=15
  - GPU acceleration via cuDF (RAPIDS) required for fuzzy dedup
- **Used For:** Deduplication threshold parameter configuration

**Repository 4: EleutherAI/lm-evaluation-harness**
- **URL:** https://github.com/EleutherAI/lm-evaluation-harness
- **Query:** "lm-evaluation-harness HellaSwag 0-shot evaluation Pythia model"
- **Key Extracted:**
  ```bash
  lm_eval --model hf \
      --model_args pretrained=EleutherAI/pythia-160m,revision=step100000,dtype="float" \
      --tasks hellaswag \
      --device cuda:0 \
      --batch_size auto:4
  ```
  - HellaSwag: `dataset_path: Rowan/hellaswag`, metric: `acc_norm`
  - Python API: `lm_eval.simple_evaluate(model="hf", tasks=["hellaswag"], num_fewshot=0)`
- **Used For:** Evaluation protocol, HellaSwag 0-shot implementation

**Source 5: NeMo Curator Documentation**
- **URL:** https://docs.nvidia.com/nemo/curator/curate-text/process-data/deduplication/fuzzy
- **Query:** "NeMo-Curator MinHash FuzzyDuplicates Jaccard threshold"
- **Key Extracted:**
  - FuzzyDuplicatesConfig API with `jaccard_threshold` parameter
  - `MinHash(num_hashes=260, char_ngrams=24, seed=42)` — production defaults
  - LSH banding: `num_buckets=20, hashes_per_bucket=13` → J≈0.8 by default
- **Used For:** Jaccard threshold parameter mapping, MinHash configuration

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from Exa search results was sufficiently clear. NeMo-Curator and lm-evaluation-harness APIs are well-documented with explicit parameter semantics. No complex or unfamiliar code patterns requiring semantic analysis.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — h-e1
- **File:** `h-e1/04_validation.md`
- **Reused Components:**
  - Codebase structure: `h-e1/code/` (curate, preprocess, train, evaluate, analyze, visualize modules)
  - NeMo-Curator integration (exact dedup fallback proven)
  - lm-evaluation-harness HellaSwag evaluation pipeline
  - GPT-NeoX training loop with checkpoint saving
- **Why Reused:** h-e1 pipeline is production-ready (23 tests pass); h-e1-v2 requires only config changes (model scale, token budget, dataset)
- **Lessons Applied:**
  - PoC proxy models (7M/16M) cannot exhibit scale-dependent curation effects → using 14M/31M (real Pythia configs)
  - MMLU floor issue → using HellaSwag 0-shot only (more sensitive at small scales)
  - 50B token budget too large → 1B tokens tractable in 2-3 days per run

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| FineWeb dataset selection | Phase 2A (02b_verification_plan.md) | Section 1.3 "Dataset Details" |
| FineWeb loading code | Exa GitHub (HuggingFace) | Standard `load_dataset` API |
| PPL thresholds τ ∈ {20,35,50} | Phase 2A hypothesis | Section 2.2 H-E1 statement |
| NeMo-Curator FuzzyDedup params | Exa GitHub (NVIDIA Curator docs) | Source 5, FuzzyDuplicatesConfig |
| Jaccard J=0.7 → num_bands=25 | Exa GitHub (NeMo Curator docs) | Source 3, 5 |
| Jaccard J=0.9 → num_bands=15 | Exa GitHub (NeMo Curator docs) | Source 3, 5 |
| Pythia-14M/31M architecture | Exa GitHub (EleutherAI/pythia) | Repository 1 |
| GPT-NeoX training framework | Exa GitHub (EleutherAI/gpt-neox) | Repository 2 |
| AdamW optimizer, lr=1e-3 | Phase 2A controlled variables | Section 1.3 "controlled_variables" |
| Cosine decay schedule | Phase 2A controlled variables | Section 1.3 hyperparameters |
| 1B token budget | h-e1 scope reduction (v2) | verification_state.yaml scope_reduction |
| 2M token batch size | Phase 2A controlled variables | batch_size_tokens: 2000000 |
| HellaSwag 0-shot evaluation | Phase 2A success criteria | Section 2.2 H-E1 "Success Criteria" |
| HellaSwag evaluation command | Exa GitHub (lm-evaluation-harness) | Repository 4 README |
| acc_norm metric | Exa GitHub (hellaswag.yaml) | Repository 4 task config |
| Expected baseline acc_norm | Pythia paper (Biderman 2023) | ar5iv.labs.arxiv.org/html/2304.01373 |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-04T00:00:00Z

### Workflow History for This Hypothesis
- h-e1: PARTIAL (PoC scale insufficient) → scope reduction → h-e1-v2
- h-e1-v2: IN_PROGRESS (Phase 2C execution)
- h-e1-v2 experiment_design: COMPLETED (this file)

---

*MCP Tools Used: Archon (3 queries — no domain-relevant results), Exa (3 queries — 5 sources found: pythia, gpt-neox, NeMo-Curator, lm-evaluation-harness, NeMo docs), Serena (skipped — code sufficiently clear)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
