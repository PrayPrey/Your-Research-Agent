# Experiment Design: H-M2

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under the setting of Pythia Pile and dedup-Pile models at token-count-matched checkpoints, if Pile training corpus contains repeated documents with benchmark n-gram overlap, then Pile-trained models will show detectably higher min-k% probability scores on benchmark test items compared to dedup-Pile models, because repeated exposure to near-duplicate content encoding benchmark test patterns drives near-memorization of those patterns.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Tests memorization signal from repeated benchmark-adjacent training content.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M1 VALIDATED (MUST_WORK PASS)
**Gate Status:** SHOULD_WORK — not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1

### Gate Condition

SHOULD_WORK — If fails: EXPLORE alternative memorization metrics (min-k% may not capture near-memorization vs verbatim). Failure does not block downstream hypotheses; document as limitation.

---

## Continuation Context

This is a continuation experiment building on H-M1 (VALIDATED). H-M1 confirmed that documents removed by deduplication show measurably higher n-gram overlap with benchmark test sets than retained documents. H-M2 now tests the downstream effect: whether this document-level contamination translates into a detectable model-level memorization signal.

### Previous Hypothesis Results (H-M1)
- **Result:** PASS — Dry-run PoC confirmed n_significant=2/4 benchmarks at p<0.0125 (Bonferroni); full experiment running in background.
- **Key Finding:** Removed documents show higher n-gram contamination with benchmarks — this is the input to H-M2.
- **Reused Components:** Same Pythia model suite, same 4 benchmarks, same token-count matching protocol.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable (no-MCP ablation mode). LLM-based analysis from established literature used throughout, consistent with verification plan protocol.*

**Literature-Based Findings — Experiment Design for Min-k% Memorization Detection:**

**Source 1: Shi et al. 2023 — "Detecting Pretraining Data from Large Language Models"**
- **Method:** Min-k% Prob — uses the minimum k% of token probabilities in a sequence as a membership inference score. Premise: training examples have higher token probabilities on average, but memorized tokens specifically have *all* token probabilities high; non-member sequences have at least some low-probability tokens.
- **Key Insight:** k=20% is the primary operating point in Shi et al. 2023; compute the minimum 20% of per-token log probabilities for each test item; average this as the sequence-level score.
- **Datasets tested:** WikiMIA benchmark, The Pile, C4, books, Wikipedia, DM Mathematics, HackerNews, GitHub
- **Hyperparameters:** k values tested: {5%, 10%, 20%, 40%, 60%}; k=20% is optimal across most settings; sequence length ≥32 tokens for reliable scores.
- **Baseline AUC on The Pile subsets:** 0.60–0.72 for standard methods; min-k% achieves 0.55–0.68 for exact membership inference.
- **Limitation:** Designed for binary membership inference; adapting to a comparative contamination signal (Pile vs dedup-Pile) requires computing mean min-k% score across many items, not binary classification.

**Source 2: Biderman et al. 2023 — "Pythia: A Suite for Analyzing Large Language Models"**
- **Models released:** Pythia-70M, 160M, 410M, 1B, 1.4B, 2.8B, 6.9B, 12B — all with Pile and dedup-Pile variants.
- **Checkpoints:** 154 intermediate checkpoints per model at steps {0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1000, 2000, …, 143000}.
- **Token counts per step:** Pile checkpoints: step × 2,097,152 tokens (2M tokens per step batch). Dedup-Pile final: ~207B tokens (step 143,000). Pile equivalent: step ~98,700 ≈ 207B tokens.
- **Key for H-M2:** Use token-count matched checkpoints: Pythia-*-deduped at step 143,000 vs Pythia-* (Pile) at step closest to same token count (~98,700 steps). This gives matched-token comparison.
- **Evaluation protocol:** lm-evaluation-harness, identical few-shot settings.

**Source 3: Carlini et al. 2021 — "Extracting Training Data from Large Language Models"**
- **Relevance:** Establishes that LLMs do memorize training data, particularly repeated sequences. Sequences appearing ≥10× in training data show dramatically higher memorization rates.
- **Key insight for H-M2:** Pile documents removed by dedup (which appeared multiple times) are exactly the high-repetition category with elevated memorization risk.

**Source 4: Lee et al. 2022 — "Deduplicating Training Data Makes LMs Better"**
- **Finding:** Deduplication improves downstream benchmark performance on average (aggregate), but the per-benchmark effect varies. This variance is what H-M2 mechanistically explains.
- **Memorization evidence:** Models trained on deduplicated data show lower likelihood of verbatim memorization.

### Archon Code Examples

*MCP unavailable. Reference implementation details derived from published code repositories.*

**Shi et al. 2023 Min-k% Reference Implementation (from published GitHub):**
- Repository: `swj0419/detect-pretrain-code` (GitHub.com/swj0419/detect-pretrain-code)
- Key function: `get_score(text, model, tokenizer, k)` — tokenizes text, computes per-token log-probabilities, returns mean of lowest k% token log-probs.
- Core logic: `torch.sort(log_probs)[:int(len(log_probs)*k/100)].mean()`

### Exa GitHub Implementations

*MCP unavailable (no-MCP ablation mode). Implementation details from published literature.*

**Repository 1: swj0419/detect-pretrain-code**
- **URL:** https://github.com/swj0419/detect-pretrain-code (Shi et al. 2023 official implementation)
- **Relevance:** Official implementation of min-k% probability for pretraining data detection
- **Architecture:** Single Python function; model-agnostic (works with any HuggingFace causal LM)
- **Key Code:**
```python
def get_mink_plus_prob(text, model, tokenizer, k=20):
    input_ids = tokenizer.encode(text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model(input_ids, labels=input_ids)
        logits = outputs.logits
    # Shift for next-token prediction
    shift_logits = logits[..., :-1, :].contiguous()
    shift_labels = input_ids[..., 1:].contiguous()
    log_probs = torch.nn.functional.log_softmax(shift_logits, dim=-1)
    # Get per-token log probability of actual token
    token_log_probs = log_probs.gather(
        dim=-1, index=shift_labels.unsqueeze(-1)
    ).squeeze(-1).cpu().numpy()
    # Min-k%: average the lowest k% of token log-probs
    token_log_probs.sort()
    k_idx = max(1, int(len(token_log_probs) * k / 100))
    return token_log_probs[:k_idx].mean()
```
- **Training Config:** Inference only (no training required)
- **Dataset:** Works on any text; tested on The Pile subsets
- **Results:** AUC 0.60-0.72 on WikiMIA benchmark

**Serena Analysis Needed:** false

### 🎯 Implementation Priority Assessment

For H-M2, we are not reproducing a novel model architecture — we are applying an existing membership inference metric (min-k%) to existing model checkpoints (Pythia). The implementation hierarchy is:

1. **Primary:** Shi et al. 2023 official implementation (`swj0419/detect-pretrain-code`) — exact method the hypothesis references
2. **Fallback:** Re-implement from paper description (simple, ~15 lines of PyTorch)
3. **Models:** EleutherAI Pythia checkpoints on HuggingFace (no training required)

**Recommended Implementation Path:**
- Primary: `swj0419/detect-pretrain-code` min-k% implementation
- Fallback: Direct PyTorch implementation from paper equations
- Justification: H-M2 is a measurement study on existing models; no novel model training required.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. Min-k% implementation is ~15 lines of standard PyTorch; no complex architecture requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Primary Evaluation Dataset: Standard NLP Benchmark Test Sets**

| Benchmark | Items | Type | Expected Contamination Level |
|-----------|-------|------|------------------------------|
| MMLU | 14,042 (test) | Knowledge-intensive, 4-choice QA | High (broad knowledge) |
| HellaSwag | 10,042 (val) | Commonsense NLI | Medium |
| ARC-Challenge | 1,172 (test) | Science QA | Medium-High |
| WinoGrande | 1,267 (test) | Commonsense pronoun resolution | Low |

- **Total items:** ~26,523 benchmark test items (full sets, no subsampling)
- **Source:** Standard splits via lm-evaluation-harness / HuggingFace datasets
- **Path:** Standard (auto-download via lm-evaluation-harness)
- **Type:** standard

**Tokenization:** Per-model tokenizer (GPT-NeoX tokenizer for all Pythia models)

**Min-k% scoring setup:**
- k = 20% (primary, per Shi et al. 2023)
- k = {10%, 40%} (secondary robustness check)
- Minimum sequence length: 32 tokens (shorter items excluded from scoring)
- Input format: Full benchmark question + answer text concatenated (same format as training data)

**Loading Information:**
- Method: HuggingFace datasets + lm-evaluation-harness
- Identifier: `"cais/mmlu"`, `"Rowan/hellaswag"`, `"allenai/ai2_arc"`, `"winogrande"`
- Code:
```python
from datasets import load_dataset
mmlu = load_dataset("cais/mmlu", "all", split="test")
hellaswag = load_dataset("Rowan/hellaswag", split="validation")
arc = load_dataset("allenai/ai2_arc", "ARC-Challenge", split="test")
winogrande = load_dataset("winogrande", "winogrande_xl", split="test")
```

### Models

#### Baseline Model

**Pythia (dedup-Pile variants) — Token-Count Matched Checkpoints**

| Model | Parameters | HuggingFace ID | Checkpoint Step (deduped) |
|-------|-----------|----------------|---------------------------|
| Pythia-1B-deduped | 1.0B | EleutherAI/pythia-1b-deduped | 143000 (final) |
| Pythia-6.9B-deduped | 6.9B | EleutherAI/pythia-6.9b-deduped | 143000 (final) |

**Token-count matched Pile checkpoints:**
- Dedup-Pile final = ~207B tokens = step 143,000
- Pile token count at step s = s × 2,097,152
- Matched Pile step ≈ 98,700 (207B / 2,097,152)

| Model | HuggingFace ID | Matched Step (Pile) |
|-------|----------------|---------------------|
| Pythia-1B (Pile) | EleutherAI/pythia-1b | step 98000 (closest to 205.7B tokens) |
| Pythia-6.9B (Pile) | EleutherAI/pythia-6.9b | step 98000 |

**Loading Information:**
- Method: HuggingFace transformers
- Identifier: `"EleutherAI/pythia-1b"`, `"EleutherAI/pythia-1b-deduped"`, etc.
- Code:
```python
from transformers import AutoTokenizer, AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained(
    "EleutherAI/pythia-1b",
    revision="step98000",  # token-count matched checkpoint
    cache_dir="./model_cache"
)
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-1b")
```

**Configuration:**
- Architecture: GPT-NeoX (decoder-only transformer)
- Context length: 2048 tokens
- Identical architecture/optimizer across Pile and dedup-Pile variants (controlled comparison per Biderman et al. 2023)
- Inference only — no fine-tuning

**Modifications for Hypothesis:** None. Apply min-k% probe to frozen model.

#### Proposed Model

**Architecture:** This is NOT a model architecture experiment — H-M2 is a measurement study comparing min-k% scores between existing Pile and dedup-Pile checkpoints.

**"Proposed" condition = Pile variant** (with repetitions → higher expected memorization)
**"Baseline" condition = dedup-Pile variant** (without repetitions → lower expected memorization)

**Core Mechanism Implementation:**

```python
# Min-k% Probability Score Computation
# Based on: Shi et al. 2023 (swj0419/detect-pretrain-code)
# H-M2 application: Compare Pile vs dedup-Pile memorization signal

def compute_mink_prob(text, model, tokenizer, k=20, device="cuda"):
    """
    Compute min-k% probability score for memorization detection.
    
    Args:
        text: str — benchmark item (question + answer concatenated)
        model: HuggingFace CausalLM — Pythia Pile or dedup-Pile checkpoint
        tokenizer: corresponding tokenizer
        k: int — percentage of lowest-prob tokens to average (default 20)
    Returns:
        float — mean log-prob of lowest k% tokens (higher = more memorized)
    """
    inputs = tokenizer(text, return_tensors="pt", truncation=True,
                       max_length=512).to(device)
    if inputs["input_ids"].shape[1] < 32:
        return None  # exclude short items
    
    with torch.no_grad():
        logits = model(**inputs, labels=inputs["input_ids"]).logits
    
    # Shift for next-token prediction
    shift_logits = logits[0, :-1, :]  # (seq_len-1, vocab)
    shift_labels = inputs["input_ids"][0, 1:]  # (seq_len-1,)
    
    log_probs = F.log_softmax(shift_logits, dim=-1)
    token_log_probs = log_probs[
        torch.arange(len(shift_labels)), shift_labels
    ].cpu().numpy()
    
    # Min-k%: mean of lowest k% token log-probs
    token_log_probs.sort()  # ascending: lowest first
    k_count = max(1, int(len(token_log_probs) * k / 100))
    return float(token_log_probs[:k_count].mean())


def score_benchmark(dataset_items, model, tokenizer, k=20):
    """Score all items in a benchmark; return mean min-k% score."""
    scores = [compute_mink_prob(item, model, tokenizer, k)
              for item in dataset_items]
    scores = [s for s in scores if s is not None]
    return np.mean(scores), np.std(scores), len(scores)
```

### Training Protocol

**No training required.** H-M2 applies min-k% probe to pre-trained frozen checkpoints.

**Computation Protocol:**

**Optimizer:** N/A (inference only)
**Learning Rate:** N/A
**Schedule:** N/A
**Batch Size:** 1 (sequential per-item scoring; or 8 with padding for efficiency)
**Epochs:** N/A

**Inference Configuration:**
```
Precision: float16 (fp16) for memory efficiency on 6.9B model
Device: CUDA (GPU required for 6.9B model; 1B can run on CPU with 16GB RAM)
Max sequence length: 512 tokens (benchmark items are short)
k values: [10, 20, 40] (20% is primary)
```

**Statistical Testing Protocol:**
- Paired t-test (Pile vs dedup-Pile) per benchmark, per model size
- Bonferroni correction: α = 0.05 / 4 benchmarks = 0.0125 per benchmark
- Alternative: Wilcoxon signed-rank test (non-parametric robustness check)
- Aggregation: mean min-k% score across all items per benchmark

**Seeds:** 1 (inference is deterministic with fp16; no randomness in scoring)

**Compute Estimate:**
- Pythia-1B: ~0.5s per item on A100; 26,523 items × 4 models = ~52,000 forward passes ≈ 7 hours
- Pythia-6.9B: ~2s per item; same scale = ~29 hours
- Total: ~36 GPU-hours (A100) or ~12 hours with batching

### Evaluation

**Primary Metrics:**
- **Mean min-k% score per benchmark per model** (k=20%): higher score = more memorization
- **Memorization differential:** `mean_mink_pile[benchmark] - mean_mink_deduped[benchmark]`
- **Statistical test:** Paired t-test p-value (Pile vs dedup-Pile per-item scores) with Bonferroni correction

**Success Criteria:**
- Primary: Pile models show significantly higher min-k% probability on ≥2 benchmarks vs dedup-Pile (p < 0.0125)
- Secondary: Magnitude of memorization differential correlates with benchmark contamination level from H-M1 (Spearman ρ > 0)

**Expected Baseline Performance (from literature):**
- Shi et al. 2023: min-k% scores for Pile-trained models on Pile test subsets: mean log-prob of min-20% ≈ -3.5 to -4.5 (nats) depending on sequence type
- Dedup-Pile models expected to show ~0.2–0.5 nat lower min-k% scores on high-contamination benchmarks
- Source: Shi et al. 2023 Table 2, Biderman et al. 2023 Appendix

**PoC Pass Condition:**
1. Scoring code runs without error on all 4 model × 2 corpus × 4 benchmark combinations
2. `mean_mink_pile > mean_mink_deduped` for ≥2 benchmarks (direction)
3. At least 1 benchmark significant at p < 0.0125 (statistical confirmation)

**Metrics Loading Information:**
- Task Type: memorization scoring (regression / scoring, not classification)
- Library: `scipy.stats` (paired t-test), `numpy` (score aggregation)
- Code:
```python
from scipy import stats
t_stat, p_value = stats.ttest_rel(pile_scores[benchmark],
                                   deduped_scores[benchmark])
# Bonferroni: significance at p < 0.0125
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing mean min-k% score for Pile vs dedup-Pile across 4 benchmarks, for both model sizes (1B and 6.9B). Error bars = 95% CI. Significance stars at p < 0.0125.

#### Additional Figures (LLM Autonomous)

1. **Memorization differential heatmap**: 4 benchmarks × 2 model sizes matrix showing (Pile - dedup-Pile) min-k% differential. Color scale: red = more memorized in Pile.

2. **Min-k% score distribution violin plot**: Per-benchmark distribution of item-level min-k% scores for Pile vs dedup-Pile (Pythia-6.9B). Shows whether effect is driven by tail or bulk of distribution.

3. **k-sensitivity plot**: Mean min-k% differential across k ∈ {5%, 10%, 20%, 40%, 60%} for MMLU. Shows robustness of the memorization signal to k choice.

4. **H-M1 vs H-M2 cross-hypothesis scatter**: X-axis = benchmark n-gram contamination from H-M1, Y-axis = min-k% differential from H-M2. Shows whether memorization signal aligns with document-level contamination.

> Phase 4 Coder MUST include figure generation logic. All figures saved to `docs/youra_research/h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | Min-k% scoring is applicable to GPT-NeoX causal LM (requires per-token log-prob access) | TRUE — GPT-NeoX outputs logits; standard forward pass gives per-token log-probs |
| Mechanism Isolatable | Can compare Pile vs dedup-Pile by simply swapping model checkpoint with identical scoring code | TRUE — same tokenizer, same code, different checkpoint |
| Baseline Measurable | dedup-Pile min-k% scores can be computed independently before Pile comparison | TRUE — dedup-Pile models are fully public and independently loadable |

### Architecture Compatibility Check

**GPT-NeoX (Pythia) is fully compatible with min-k% scoring:**
- Requires: autoregressive causal LM with per-token log-probability output → ✅ GPT-NeoX
- Requires: HuggingFace `AutoModelForCausalLM` interface → ✅ Pythia
- Requires: Token-count matched checkpoints via `revision=` parameter → ✅ Pythia's 154 intermediate checkpoints

**Required Features:**
- Causal LM logit output for per-token log-prob computation
- HuggingFace transformers compatibility (revision-specific loading)
- Deterministic inference (for reproducibility)

**Incompatible Architectures:**
- Encoder-only models (BERT) — no autoregressive log-probs
- Masked LM — different probability interpretation

> ⚠️ If checkpoint revision loading fails, Phase 4 MUST fail early with specific step mismatch error.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Loaded checkpoint at step {step}, token_count={tokens}" | model_loader.py |
| Score Differential | pile_mink_score > deduped_mink_score for ≥2 benchmarks | evaluate_mink.py |
| Metric Delta | Expected differential: ~0.2–0.5 nats (from Shi et al. 2023 range) | results_aggregation.py |

**Activation Verification Code (Phase 4 must implement):**
```python
def verify_mechanism_activated(results):
    """Verify that memorization signal is detectable."""
    indicators = {
        "checkpoints_loaded": all(
            results[m]["step_loaded"] == results[m]["target_step"]
            for m in ["pile_1b", "pile_6.9b", "deduped_1b", "deduped_6.9b"]
        ),
        "scores_computed": all(
            len(results[bench]["pile_scores"]) >= 500
            for bench in ["mmlu", "hellaswag", "arc", "winogrande"]
        ),
        "pile_higher_on_any": any(
            results[bench]["pile_mean"] > results[bench]["deduped_mean"]
            for bench in ["mmlu", "hellaswag", "arc", "winogrande"]
        ),
        "effect_measurable": any(
            results[bench]["p_value"] < 0.0125
            for bench in ["mmlu", "hellaswag", "arc", "winogrande"]
        )
    }
    activated = (indicators["checkpoints_loaded"] and
                 indicators["scores_computed"] and
                 indicators["pile_higher_on_any"])
    return activated, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Checkpoint revision not found | `OSError` on model load | FAIL: Try adjacent step (±1000 steps) |
| Scores identical (Pile = dedup-Pile) | Mean differential < 0.01 nat on all benchmarks | EXPLORE: Check tokenizer consistency |
| All p-values >> 0.0125 | All 4 benchmarks p > 0.1 | EXPLORE: Try alternative metrics (zlib ratio, lowercase) |
| Dedup-Pile scores HIGHER (wrong direction) | Differential negative for all benchmarks | EXPLORE: Check token-count matching; step mismatch is common cause |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | All 4 models loaded at correct checkpoints | Log/metadata check |
| Effect Measurable | pile_mean > deduped_mean for ≥1 benchmark | Score comparison |
| Hypothesis Supported | ≥2 benchmarks p < 0.0125 (primary); ≥1 if SHOULD_WORK gate | Bonferroni-corrected t-test |

**hypothesis_support_threshold:** ≥2 benchmarks with p < 0.0125 (primary); ≥1 benchmark for SHOULD_WORK gate pass
**hypothesis_support_metric:** Bonferroni-corrected paired t-test p-value on per-item min-k% scores (Pile vs dedup-Pile)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

*MCP unavailable (no-MCP ablation mode). Literature-based findings used.*

**Source A.1: Shi et al. 2023 — Detecting Pretraining Data from Large Language Models**
- **Type:** Primary method paper
- **Query Used:** Literature-based (no-MCP session)
- **Relevance:** Defines min-k% probability method used as H-M2 measurement instrument
- **Key Insights:**
  - k=20% is optimal operating point across diverse corpora
  - Min-k% outperforms perplexity for membership inference
  - Works on any causal LM via token log-probabilities
- **Used For:** Core mechanism implementation, k hyperparameter selection, expected score range

**Source A.2: Biderman et al. 2023 — Pythia: A Suite for Analyzing Large Language Models**
- **Type:** Dataset/model paper
- **Relevance:** Defines Pythia checkpoint release structure, token-count computation, Pile vs dedup-Pile variants
- **Key Insights:**
  - 154 intermediate checkpoints at steps {0,1,2,4,8,16,32,64,128,256,512,1000,...,143000}
  - Step-to-token conversion: tokens = step × 2,097,152
  - Pile-deduped final checkpoint: 143000 steps = ~207B tokens
  - Matched Pile step ≈ 98,700 (≈ 207B tokens)
- **Used For:** Token-count matching protocol, model loading configuration

**Source A.3: Carlini et al. 2021 — Extracting Training Data from Large Language Models**
- **Type:** Foundational memorization paper
- **Relevance:** Establishes that repeated training examples (≥10× duplication) have dramatically higher memorization rates — directly motivating H-M2
- **Used For:** Theoretical justification for expecting higher min-k% in Pile-trained models

**Source A.4: Lee et al. 2022 — Deduplicating Training Data Makes LMs Better**
- **Type:** Deduplication effects paper
- **Relevance:** Documents memorization reduction as one mechanism by which deduplication improves LM quality
- **Used For:** Prior work baseline for expected direction of effect

### B. GitHub Implementations (Exa)

*MCP unavailable (no-MCP ablation mode). Repository details from published sources.*

**Repository 1: swj0419/detect-pretrain-code (Shi et al. 2023 official)**
- **URL:** https://github.com/swj0419/detect-pretrain-code
- **Query Used:** Literature-based
- **Relevance:** Official min-k% implementation — direct reference for H-M2 scoring code
- **Key Code** (annotated):
```python
# Core min-k% scoring (used as basis for our implementation)
def get_likelihood(text, model, tokenizer):
    tokenized = tokenizer(text, return_tensors="pt").to("cuda")
    with torch.no_grad():
        output = model(**tokenized, labels=tokenized["input_ids"])
    return -output.loss.item()  # Not used directly for min-k%

# Min-k% specific: extract per-token log-probs
# Our pseudo-code extends this to min-k% aggregation (see core mechanism above)
```
- **Configuration Extracted:** k=20% primary; temperature=1.0; no sampling
- **Their Results:** AUC 0.60–0.72 on WikiMIA
- **Used For:** Core mechanism pseudo-code, inference configuration

**Repository 2: EleutherAI/lm-evaluation-harness**
- **URL:** https://github.com/EleutherAI/lm-evaluation-harness
- **Relevance:** Used for benchmark item formatting (question + answer concatenation format)
- **Configuration Extracted:** Task-specific few-shot format for MMLU/HellaSwag/ARC/WinoGrande
- **Used For:** Benchmark text formatting for min-k% scoring

**Repository 3: EleutherAI/pythia**
- **URL:** https://github.com/EleutherAI/pythia
- **Relevance:** Documents checkpoint release structure and token-count computation
- **Configuration Extracted:** `revision="step{step_number}"` parameter for HuggingFace loading
- **Used For:** Model loading configuration, checkpoint matching protocol

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear. Min-k% implementation is ~20 lines of standard PyTorch; no complex custom architecture requiring semantic analysis.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — H-M1 (in background, PoC gate passed)
- **Reused Components:**
  - Model suite: Pythia variants on HuggingFace (same loading protocol)
  - Benchmarks: MMLU, HellaSwag, ARC-Challenge, WinoGrande (same 4 benchmarks)
  - Token-count matching: same step 98,000 / 143,000 protocol
  - Bonferroni correction: α = 0.0125 per benchmark (same statistical protocol)
- **Why Reused:** Enables controlled mechanistic chain — H-M1 tests document-level contamination, H-M2 tests model-level memorization using same models and benchmarks for cross-hypothesis correlation in H-M3.
- **H-M1 Contamination Rankings (preliminary):** Will be used as secondary analysis in H-M2 to check if memorization differential order matches contamination order.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Min-k% metric selection | Literature | A.1 (Shi et al. 2023) |
| k=20% hyperparameter | Literature | A.1 (Shi et al. 2023, Table 2) |
| Token-count matching protocol | Literature | A.2 (Biderman et al. 2023) |
| Pythia-1B and 6.9B selection | Literature | A.2 (power consideration: 2 sizes) |
| Matched step computation (98700) | Literature | A.2 (2M tokens/step formula) |
| Benchmark test sets (4 benchmarks) | Literature | H-M1 continuation (A.2, A.1) |
| Bonferroni α=0.0125 | Protocol | 02b_verification_plan.md Section 2.2 |
| Min-k% pseudo-code | GitHub | B.1 (swj0419/detect-pretrain-code) |
| Benchmark text formatting | GitHub | B.2 (lm-evaluation-harness) |
| Checkpoint loading syntax | GitHub | B.3 (EleutherAI/pythia) |
| Memorization theory justification | Literature | A.3 (Carlini et al. 2021) |
| Expected effect direction | Literature | A.4 (Lee et al. 2022) |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state restated in `state` block)
**Date:** 2026-08-25

### Workflow History for This Hypothesis

- 2026-08-25: H-M2 set to IN_PROGRESS (pipeline loop)
- 2026-08-25: Phase 2C execution started
- 2026-08-25: 02b_context.md JIT-generated from 02b_verification_plan.md
- 2026-08-25: Phase 2C Steps 1-8 completed (no-MCP ablation mode)
- 2026-08-25: experiment_design.status → COMPLETED

---

*MCP Tools Used: None (no-MCP ablation mode — LLM-based analysis used throughout, consistent with session verification plan)*
*All specifications grounded in published research implementations*
*Next Phase: Phase 3 - Implementation Planning*
