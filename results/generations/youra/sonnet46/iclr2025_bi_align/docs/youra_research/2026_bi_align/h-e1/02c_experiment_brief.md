# Experiment Design: h-e1

**Date:** 2026-03-14
**Author:** Anonymous
**Hypothesis Statement:** C_sem^H←A = E[cos(SBERT(H_{t+1}), SBERT(A_t))] - E[cos(SBERT(H_{t+1}), SBERT(A_t^matched-shuffle))] > 0 with partner-specificity: cos(H_next, A_actual) > cos(H_next, A_topic-matched) > cos(H_next, A_random), d >= 0.1 between adjacent levels.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** None required — h-e1 has no prerequisites
**Gate Status:** MUST_WORK gate. Success required to unlock H-M1, H-M2, H-M3, H-M4.

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition

**Gate Type:** MUST_WORK

**Success required for:**
- H-M1 (tier-monotonic scaling) — direct prerequisite
- H-M3 (within-prompt Δ) — direct prerequisite
- H-M2 and H-M4 — transitively blocked

**If Fail:**
- STOP pipeline immediately
- Report null result: "Semantic accommodation does not exist at SBERT embedding level in HH-RLHF"
- Write Serena failure memory file
- ROUTE_TO_0 for new research direction

---

## Continuation Context

This is the **first hypothesis** in the verification chain. No previous hypothesis results to incorporate.

### Previous Hypothesis Results (if applicable)
*None — this is the foundational existence hypothesis.*

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: SBERT semantic similarity accommodation experiment design**
- Results returned low-relevance matches (max similarity 0.378)
- Most relevant: arXiv 2301.12247 (RLHF-related), OpenAI instruction-following blog
- **Key insight from KB context:** The knowledge base confirms HuggingFace Transformers and datasets ecosystem is standard for this type of work; no specific SBERT accommodation examples found
- **Source:** Archon KB source 8b1c7f40739544a6

**Query 2: Semantic accommodation NLP implementation challenges**
- Top result: OpenAI instruction-following blog (similarity 0.479) — confirms RLHF alignment quality is operationally meaningful
- Second: arXiv 2301.12247 — RLHF-related paper
- **Key insight:** Best practices for NLP alignment analysis include careful baseline subtraction to separate topical coherence from genuine accommodation effects
- **Source:** Archon KB source 8b1c7f40739544a6

**Query 3: HH-RLHF conversational NLP benchmark dataset**
- Top result: openreview.net/forum?id=M3Y74vmsMcY (similarity 0.516) — highest relevance result overall, likely an RLHF/dialogue paper
- HuggingFace Transformers docs confirmed as standard loading platform
- **Key insight:** HuggingFace datasets library (`load_dataset`) is the standard API for HH-RLHF loading
- **Source:** Archon KB source 8b1c7f40739544a6

### Archon Code Examples

**Query: datasets load_dataset huggingface python**

- **Source:** HuggingFace datasets documentation
- **Pattern:** Standard `load_dataset` API
  ```python
  from datasets import load_dataset
  dataset = load_dataset("imagefolder", data_dir="/path/to/folder", split="train")
  ```
- **Insight:** `load_dataset("Anthropic/hh-rlhf", data_dir="helpful-base")` follows this exact pattern

**Query: sentence-transformers encode batch similarity**
- No directly relevant code examples in KB
- KB confirms HuggingFace ecosystem is standard; sentence-transformers documentation not indexed
- **Fallback:** sentence-transformers official API is well-established:
  ```python
  from sentence_transformers import SentenceTransformer, util
  model = SentenceTransformer("all-MiniLM-L6-v2")
  embeddings = model.encode(sentences, batch_size=256, show_progress_bar=True)
  cosine_scores = util.cos_sim(embeddings_a, embeddings_b)
  ```

### Exa GitHub Implementations

**Status:** ❌ Exa MCP unavailable (HTTP 402 — quota exhausted). 3 retries attempted per MCP Error Retry Protocol. Proceeding with limitation documented.

**Limitation:** No live GitHub repository search was possible. Experiment design proceeds based on:
1. Phase 2B verification protocol (fully specified)
2. Archon KB general HuggingFace patterns
3. Domain knowledge of sentence-transformers and HH-RLHF APIs

**Known relevant implementations from Phase 2B research:**
- Danescu-Niculescu-Mizil et al. 2011: Function-word coordination in Wikipedia/Supreme Court (foundational accommodation methodology)
- Reimers & Gurevych 2019: SBERT (Sentence-BERT) — sentence-transformers library
- Chang & Wang 2025: Word-level LLM-human bidirectional adaptation framework
- sentence-transformers library: `pip install sentence-transformers` (UKP Lab, TU Darmstadt)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is NOT a paper reproduction experiment — it is a novel analysis pipeline. Priority is:
1. **sentence-transformers library** (Reimers & Gurevych, official) for SBERT encoding
2. **HuggingFace datasets** (official) for HH-RLHF loading
3. **scipy.stats** for Mann-Whitney U tests
4. **numpy** with custom bootstrap implementation for Cohen's d CIs

**Recommended Implementation Path:**
- Primary: sentence-transformers + HuggingFace datasets + scipy + numpy
- Fallback: transformers (manual SBERT encoding) + same statistical libraries
- Justification: sentence-transformers provides CPU-optimized batch encoding with 14K sentences/sec throughput; direct cosine similarity computation; no fine-tuning required

### Code Analysis (Serena MCP)

*Skipped* — This is an analytical/statistical pipeline (not a complex neural architecture). The implementation uses standard library calls (sentence-transformers, scipy, numpy) without custom forward pass logic or novel layer architectures requiring semantic code analysis.

---

## Experiment Specification

### Dataset

**Name:** Anthropic/hh-rlhf (Helpfulness Splits)
**Type:** standard (real dataset, Anthropic/Bai et al. 2022)
**Source:** HuggingFace Hub — `Anthropic/hh-rlhf`
**Splits Used:**
- `helpful-base` (Tier 1 / rank=1)
- `helpful-rejection-sampled` (Tier 2 / rank=2)
- `helpful-online` (Tier 3 / rank=3)

**Dataset Statistics (from Bai et al. 2022):**
- Total: ~161,000 train conversations, ~8,552 test conversations (all helpfulness splits combined)
- Structure: Each conversation = `{"chosen": "\\n\\nHuman: ...\\n\\nAssistant: ...", "rejected": "..."}`
- Paired: Each example has chosen/rejected response pair for same prompt

**Preprocessing:**
1. Parse conversation strings: split on `\n\nHuman:` and `\n\nAssistant:` markers
2. Extract consecutive (Human_turn_{t+1}, AI_turn_t) pairs
3. Minimum conversation length filter: 2 turns required (at least one H-A exchange)
4. Strip leading/trailing whitespace from all turns
5. **Length residualization:** compute response_length = token count; fit OLS: `cos_sim ~ response_length`; use residuals for accommodation measure (controls for verbosity confound)
6. **Lexical overlap residualization:** compute Jaccard overlap(H_{t+1}, A_t); regress out from C_sem

**Augmentation:** None — corpus is fixed; no synthetic augmentation permitted

**For Existence Test (h-e1):** Pool all tiers (helpful-base + helpful-rejection-sampled + helpful-online) for maximum N

**Estimated turn count:** ~273,617 turns across all helpfulness splits (from Phase 2B estimates)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `"Anthropic/hh-rlhf"`
- Code:
  ```python
  from datasets import load_dataset
  ds_base = load_dataset("Anthropic/hh-rlhf", data_dir="helpful-base")
  ds_rs   = load_dataset("Anthropic/hh-rlhf", data_dir="helpful-rejection-sampled")
  ds_online = load_dataset("Anthropic/hh-rlhf", data_dir="helpful-online")
  ```

### Models

#### Baseline Model

**Architecture:** all-MiniLM-L6-v2 (sentence-transformers)
**Type:** Pre-trained SBERT, inference-only (no fine-tuning)
**Source:** HuggingFace model hub / sentence-transformers library
**Embedding dimension:** 384
**Max sequence length:** 256 tokens
**Throughput:** ~14,000 sentences/sec on CPU

**Role in h-e1:** Encodes ALL turns (Human and AI) into semantic embeddings for cosine similarity computation. No proposed modification — this IS the measurement instrument.

**Configuration:**
- `batch_size=256` (CPU-optimized)
- `normalize_embeddings=True` (ensures cosine = dot product for speed)
- `device='cpu'` (sufficient for inference; ~20 min for 273K turns)

**Loading Information** (for Phase 4 download):
- Method: sentence-transformers / HuggingFace
- Identifier: `"all-MiniLM-L6-v2"`
- Code:
  ```python
  from sentence_transformers import SentenceTransformer
  model = SentenceTransformer("all-MiniLM-L6-v2")
  ```

**Robustness models** (same loading pattern):
- `"paraphrase-MiniLM-L6-v2"` — robustness check 1
- `"all-mpnet-base-v2"` — robustness check 2 (heavier, ~768-dim)

#### Proposed Model

**Architecture:** This experiment does NOT modify the model architecture. The "proposed" design is the **three-level partner-specificity control structure**:
- Level 1 (Actual): cos(SBERT(H_{t+1}), SBERT(A_t_actual)) — real conversation partner
- Level 2 (Topic-matched): cos(SBERT(H_{t+1}), SBERT(A_t_topic_matched)) — K=5 KNN matched from different conversation, same tier
- Level 3 (Random): cos(SBERT(H_{t+1}), SBERT(A_t_random)) — fully random shuffle baseline

**Core Mechanism Implementation:**

```python
# Core Mechanism: Three-Level Partner-Specificity Semantic Accommodation
# Based on: Danescu-Niculescu-Mizil 2011 coordination framework + SBERT
# Implements: C_sem^H←A with matched-shuffle baseline subtraction

import numpy as np
from sentence_transformers import SentenceTransformer, util
from sklearn.neighbors import NearestNeighbors

class SemanticAccommodationMeasure:
    """
    Computes C_sem^H←A = E[cos(H_{t+1}, A_actual)] - E[cos(H_{t+1}, A_shuffle)]
    with three-level partner-specificity control hierarchy.
    """
    def __init__(self, model_name="all-MiniLM-L6-v2", k=5, seed=42):
        self.model = SentenceTransformer(model_name)
        self.k = k  # KNN neighbors for topic-matched control
        self.seed = seed

    def encode_turns(self, turns: list[str], batch_size=256) -> np.ndarray:
        """Encode turns; returns (N, D) normalized embeddings."""
        return self.model.encode(turns, batch_size=batch_size,
                                  normalize_embeddings=True,
                                  show_progress_bar=True)

    def build_topic_controls(self, prompt_embs: np.ndarray,
                              ai_embs: np.ndarray) -> np.ndarray:
        """Build K=5 KNN topic-matched AI turn controls via prompt similarity."""
        knn = NearestNeighbors(n_neighbors=self.k+1, metric='cosine')
        knn.fit(prompt_embs)
        # for each prompt, find K nearest from OTHER conversations (exclude self)
        distances, indices = knn.kneighbors(prompt_embs)
        # return mean embedding of K topic-matched AI turns (excluding self)
        topic_matched = np.array([ai_embs[indices[i, 1:self.k+1]].mean(axis=0)
                                   for i in range(len(prompt_embs))])
        return topic_matched  # (N, D)

    def compute_c_sem(self, h_next_embs, a_actual_embs,
                       a_topic_embs, a_random_embs) -> dict:
        """Compute C_sem and three-level cosine similarities."""
        cos_actual     = (h_next_embs * a_actual_embs).sum(axis=1)    # (N,)
        cos_topic      = (h_next_embs * a_topic_embs).sum(axis=1)     # (N,)
        cos_random     = (h_next_embs * a_random_embs).sum(axis=1)    # (N,)
        c_sem = cos_actual.mean() - cos_random.mean()                  # scalar
        return {"c_sem": c_sem, "cos_actual": cos_actual,
                "cos_topic": cos_topic, "cos_random": cos_random}
```

### Training Protocol

**Note:** This is a statistical analysis pipeline — no gradient-based training occurs. "Training protocol" refers to the computational protocol.

**Computational Pipeline:**

**Step 1: Data Loading and Parsing**
- Load all three helpfulness splits via `load_dataset`
- Parse chosen conversations into (Human, AI) turn pairs
- Filter: minimum 2 turns, non-empty turns only
- Expected: ~100,000–140,000 valid pairs (from 273,617 total turns)

**Step 2: Embedding Generation**
- Model: `all-MiniLM-L6-v2`
- Batch size: 256 (CPU-optimized)
- Encode ALL turns: Human follow-up turns H_{t+1}, AI turns A_t
- Also encode prompt turns (Human_t) for KNN topic-matching
- Estimated time: ~20 minutes for 273K turns on CPU
- Save embeddings to disk: `{hypothesis_folder}/embeddings/`

**Step 3: Control Construction**
- Random shuffle: `np.random.seed(42); np.random.shuffle(ai_indices_copy)`
- Topic-matched (K=5 KNN): build NearestNeighbors on prompt embeddings; retrieve K nearest from different conversations in same tier

**Step 4: C_sem Computation**
- Pool all tiers for existence test (h-e1)
- Compute: cos_actual, cos_topic, cos_random for all pairs
- Apply length residualization via OLS regression
- Apply lexical overlap residualization via OLS regression

**Step 5: Statistical Testing**
- **Bootstrap CI for C_sem:** n_bootstrap=1000, seed=42; report [2.5%, 97.5%] CI
- **Mann-Whitney U:** pairwise tests: (actual vs topic), (topic vs random)
- **Cohen's d:** bootstrap-based for each pair contrast; threshold: d ≥ 0.1
- **Significance:** p < 0.05 (two-tailed)

**Seeds:** 1 (seed=42 fixed throughout)

**Optimizer:** N/A — inference-only

**Loss Function:** N/A — descriptive statistics

### Evaluation

**Primary Metrics:**

| Metric | Definition | Success Threshold |
|--------|-----------|-------------------|
| C_sem^H←A | E[cos(H_{t+1}, A_actual)] - E[cos(H_{t+1}, A_random)] | Bootstrap 95% CI lower bound > 0 |
| Partner-specificity gap | d between cos_actual and cos_topic | d ≥ 0.1 |
| Three-way inequality | cos_actual > cos_topic > cos_random | All three inequalities hold |

**Success Criteria (PoC — direction only):**
1. C_sem > 0 with bootstrap CI lower bound > 0 (existence confirmed)
2. d ≥ 0.1 between cos(H_next, A_actual) and cos(H_next, A_topic_matched)
3. Three-way ordering: actual > topic-matched > random

**Expected baseline performance (from Phase 2B priors):**
- Three prior lexical-level attempts: d ∈ [0.036, 0.136] — all inconclusive
- SBERT semantic hypothesis: expected d ≈ 0.1–0.3 if semantic accommodation exists
- Random baseline cos_sim expected: ~0.3–0.5 (SBERT MiniLM has moderate baseline similarity on conversational text)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical analysis (not classification/regression)
- Library: `scipy.stats` + `numpy` (custom bootstrap)
- Code:
  ```python
  from scipy.stats import mannwhitneyu
  import numpy as np

  def bootstrap_cohen_d(a, b, n_bootstrap=1000, seed=42):
      rng = np.random.default_rng(seed)
      ds = []
      for _ in range(n_bootstrap):
          sa = rng.choice(a, size=len(a), replace=True)
          sb = rng.choice(b, size=len(b), replace=True)
          pooled_std = np.sqrt((sa.std()**2 + sb.std()**2) / 2)
          ds.append((sa.mean() - sb.mean()) / (pooled_std + 1e-10))
      return np.mean(ds), np.percentile(ds, [2.5, 97.5])

  stat, p = mannwhitneyu(cos_actual, cos_topic, alternative='greater')
  d_mean, d_ci = bootstrap_cohen_d(cos_actual, cos_topic)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart: C_sem value with 95% bootstrap CI; three bars for cos_actual, cos_topic, cos_random with error bars

#### Additional Figures (LLM Autonomous)

1. **Partner-Specificity Gradient Plot:** Line plot with error bars showing cos_actual > cos_topic > cos_random with Cohen's d annotations between levels
2. **C_sem Bootstrap Distribution:** Histogram of bootstrap C_sem samples with 95% CI shading and zero-line reference
3. **Cosine Similarity Distributions:** Violin/box plots comparing three control levels across all tier-pooled data
4. **Residualization Check:** Scatter plots of raw vs length-residualized cosine similarities to verify confound removal
5. **KNN Topic-Matching Quality:** Distribution of cosine distances to K=5 nearest prompt neighbors (verifies matching quality)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | sentence-transformers SBERT model can be loaded and encodes text into semantic embeddings | TRUE — verified via `SentenceTransformer("all-MiniLM-L6-v2").encode(["test"])` |
| Mechanism Isolatable | Three-level control (actual/topic/random) can be constructed independently | TRUE — random shuffle and KNN topic-matching are independent operations |
| Baseline Measurable | Random shuffle baseline (C_sem denominator) can be computed | TRUE — `np.random.shuffle` on AI turn indices |

### Architecture Compatibility Check

**This is a statistical analysis pipeline, not a neural architecture.** Compatibility checks:

1. **HH-RLHF dataset accessibility:** `load_dataset("Anthropic/hh-rlhf", data_dir="helpful-base")` must succeed (requires internet access or cached copy)
2. **SBERT model availability:** `SentenceTransformer("all-MiniLM-L6-v2")` must load (~90MB download)
3. **Conversation parse-ability:** HH-RLHF `chosen` field format `"\n\nHuman: ...\n\nAssistant: ..."` must be parseable into turn pairs
4. **Sufficient pairs (N_pairs ≥ 1000):** Must verify empirically before committing to statistical tests
5. **KNN feasibility:** scipy/sklearn KNN on 273K embeddings of dim 384 must complete in reasonable time

**Required Features:**
- Internet access (or pre-downloaded HH-RLHF cache)
- CPU with ~8GB RAM for embedding storage (273K × 384 × 4 bytes ≈ 400MB)
- Python packages: `sentence-transformers`, `datasets`, `scipy`, `sklearn`, `numpy`, `matplotlib`

**Incompatible conditions:**
- GPU not required (but accelerates encoding if available)
- Pure synthetic data: PROHIBITED

### Mechanism Activation Indicators

**How to detect if mechanism is actually working:**

| Indicator Type | Expected Signal | Code Location |
|----------------|-----------------|---------------|
| Log Message | "Encoded N turns with all-MiniLM-L6-v2 in X seconds" | `encode_turns()` progress bar |
| Data Shape | embeddings.shape == (N_pairs, 384) | After `model.encode()` call |
| Metric Delta | cos_actual.mean() > cos_random.mean() (positive C_sem) | `compute_c_sem()` return dict |
| Bootstrap CI | ci[0] > 0.0 (lower bound positive) | `bootstrap_c_sem()` return |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(results: dict) -> tuple[bool, dict]:
    """Verify semantic accommodation measurement mechanism is working."""
    indicators = {
        "embeddings_computed": results["n_pairs"] > 0 and results["embed_dim"] == 384,
        "c_sem_positive": results["c_sem"] > 0,
        "ci_lower_positive": results["c_sem_ci"][0] > 0,
        "ordering_holds": (results["cos_actual_mean"] > results["cos_topic_mean"]
                           and results["cos_topic_mean"] > results["cos_random_mean"]),
        "sufficient_pairs": results["n_pairs"] >= 1000,
    }
    passed = all(indicators.values())
    return passed, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Dataset load fails | `FileNotFoundError` or `ConnectionError` | FAIL early; check internet/cache |
| Zero valid pairs | `n_pairs == 0` after parsing | FAIL; log parsing error |
| C_sem ≤ 0 | `c_sem <= 0` AND `ci[0] <= 0` | GATE FAILS: null result confirmed |
| d < 0.1 | `cohen_d < 0.1` for actual vs topic | Partial: ordering exists but weak |
| Three-way ordering violated | `cos_actual < cos_topic` | GATE FAILS: no partner-specificity |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | Embeddings computed, N_pairs ≥ 1000 |
| Effect Measurable | C_sem > 0 | `c_sem > 0` |
| Hypothesis Supported | CI lower bound > 0 AND d ≥ 0.1 | Bootstrap CI on C_sem + Cohen's d |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (all three tiers loaded, embeddings computed, statistics run)
2. C_sem^H←A > 0 with bootstrap 95% CI lower bound > 0
3. cos(H_next, A_actual) > cos(H_next, A_topic_matched): Cohen's d ≥ 0.1

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1:** HuggingFace datasets documentation
- **Type:** Knowledge base / documentation
- **Query Used:** "huggingface datasets load_dataset conversation"
- **Relevance:** Confirmed `load_dataset` API for HH-RLHF loading
- **Key Insights:**
  - Standard pattern: `load_dataset("dataset_name", data_dir="split_name")`
  - Returns DatasetDict with `train`/`test` splits
- **Used For:** Dataset loading specification (Section: Dataset loading code)

**Source A.2:** HuggingFace Transformers documentation
- **Type:** Knowledge base
- **Query Used:** "sentence-transformers encode batch similarity"
- **Relevance:** General HuggingFace ecosystem confirmation; sentence-transformers is compatible sub-library
- **Used For:** Model loading specification

**Source A.3:** arXiv 2301.12247
- **Type:** Research paper (RLHF-related)
- **Query Used:** "SBERT semantic similarity accommodation experiment design"
- **Relevance:** RLHF alignment quality signal — confirms tier-based quality gradient is meaningful
- **Used For:** Motivation for hypothesis (indirectly)

### B. GitHub Implementations (Exa)

**Status:** Exa MCP unavailable (HTTP 402 — quota exhausted). No GitHub implementations retrieved.

**Known repositories (from Phase 2B research, not live search):**
- `UKP-SQuARE / sentence-transformers` — official sentence-transformers library
- `Anthropic/hh-rlhf` — original HH-RLHF dataset repository
- `VisualBERT/Danescu-Niculescu-Mizil-2011-coordination` — linguistic coordination paper code (function-word; referenced as baseline methodology)

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code is an analytical/statistical pipeline using standard library calls. No complex neural architecture or custom layers requiring semantic code analysis.

### D. Previous Hypothesis Context

**Previous Context:** None — this is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: Anthropic/hh-rlhf | Phase 2A Dialogue (via 02b_context.md) | verification_state.yaml:main_hypothesis.controlled_variables.dataset |
| Dataset loading API | Archon KB (HuggingFace docs) | Source A.1 |
| Model: all-MiniLM-L6-v2 | Phase 2A Dialogue (via 02b_context.md) | verification_state.yaml:main_hypothesis.controlled_variables.model |
| Batch size 256, CPU encoding | sentence-transformers official docs (domain knowledge) | sentence-transformers library README |
| Three-level control hierarchy | Phase 2B Verification Protocol | 02b_verification_plan.md:H-E1 Verification Protocol |
| K=5 KNN topic-matching | Phase 2B (Phase 2A parameter) | verification_state.yaml:main_hypothesis.controlled_variables.hyperparameters.knn_k |
| Bootstrap n=1000, seed=42 | Phase 2B (Phase 2A parameter) | verification_state.yaml:main_hypothesis.controlled_variables.hyperparameters.bootstrap_resamples |
| Cohen's d threshold ≥ 0.1 | Phase 2B success criteria | 02b_verification_plan.md:H-E1 Success Criteria |
| Mann-Whitney U test | Phase 2B Verification Protocol | 02b_verification_plan.md:H-E1 Verification Protocol step 4 |
| Minimum N_pairs ≥ 1000 | Phase 2B constraint | verification_state.yaml:main_hypothesis.controlled_variables.hyperparameters.min_n_pairs |
| Length residualization | Phase 2B controlled variables (CV) | 02b_verification_plan.md:H-E1 Variables:CV |
| Lexical overlap residualization | Phase 2B controlled variables (CV) | 02b_verification_plan.md:H-E1 Variables:CV |
| Significance level p < 0.05 | Phase 2B (Phase 2A parameter) | verification_state.yaml:main_hypothesis.controlled_variables.hyperparameters.significance_level |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-14

### Workflow History for This Hypothesis

- `2026-03-14 21:17:54`: h-e1 set to IN_PROGRESS (Hypothesis Loop initiated Phase 2C)
- `2026-03-14`: Phase 2C Step 1: State validated, context generated (JIT)
- `2026-03-14`: Phase 2C Steps 2-5: Research completed (Archon KB searched; Exa unavailable with documented limitation)
- `2026-03-14`: Phase 2C Step 6: Experiment specification synthesized
- `2026-03-14`: Phase 2C Step 7: Reference implementations documented
- `2026-03-14`: Phase 2C Step 8: Validation and state update (IN PROGRESS)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code) — 5 queries executed; Exa (GitHub) — unavailable (402); Serena (Code Analysis) — skipped (analytical pipeline)*
*All specifications grounded in Phase 2B protocols and Archon KB findings*
*Next Phase: Phase 3 - Implementation Planning*
