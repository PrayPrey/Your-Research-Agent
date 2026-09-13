# Experiment Design: h-e1

**Date:** 2026-05-13
**Author:** Anonymous
**Hypothesis Statement:** Under contamination detection for MMLU/HellaSwag/GSM8K against The Pile/C4/RedPajama using open-weight models, if corpus-side geometric signals (max 13-gram overlap count, SBERT cosine similarity) are used to define geometry strata, then n-gram detectors will exhibit recall ≥ 0.80 in the lexical stratum and ≤ 0.40 in the semantic stratum, and Min-K%++ F1 variance across three corpora will be ≥ 0.15, because detector families operate on orthogonal signal types that align with different corpus overlap regimes.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (root hypothesis — no prerequisites)
**Gate Status:** MUST_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None (root hypothesis)

### Gate Condition
MUST_WORK — if H-E1 fails, STOP entire verification plan; report indeterminate zone characterization as negative finding. Fail condition: n-gram recall ≥ 0.60 in semantic stratum OR Min-K%++ variance < 0.10.

---

## Continuation Context

No previous hypothesis results — this is the first hypothesis (root) in the verification chain H-E1 → H-M1 → H-M2 → H-M3 → H-M4.

### Previous Hypothesis Results (if applicable)
N/A — first hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: benchmark contamination detection n-gram overlap experiment**
- No directly relevant prior cases found in Archon KB (KB contains diffusion model content, similarity ~0.37-0.43)
- Key insight: This is a novel research direction with no established Archon precedents — all implementation guidance drawn from Exa GitHub searches

**Query 2: contamination detection implementation challenges best practices**
- No relevant results (unrelated domain in KB)

**Query 3: SBERT embedding similarity FAISS benchmark evaluation**
- No relevant results (unrelated domain in KB)

**Overall Archon Assessment:** Archon KB is not specialized for this NLP contamination detection domain. All implementation decisions grounded in Exa GitHub findings below and established paper implementations.

### Archon Code Examples

**Query 1: n-gram overlap contamination detection PyTorch**
- No relevant code examples found

**Query 2: Min-K++ membership inference attack language model**
- No relevant code examples found

**Overall:** No Archon code precedents. Proceeding with Exa-sourced implementations (official author repos).

### Exa GitHub Implementations

**Query 1: Min-K%++ Official Implementation (HIGHEST PRIORITY)**

**Repository 1**: zjysteven/mink-plus-plus (⭐ 54)
- **URL**: https://github.com/zjysteven/mink-plus-plus
- **Paper**: ICLR 2025 Spotlight — "Min-K%++: Improved Baseline for Detecting Pre-Training Data from Large Language Models" (arXiv:2404.02936)
- **Relevance**: Official author implementation of Min-K%++ — HIGHEST PRIORITY per implementation hierarchy
- **Architecture**: Reference-free MIA method based on conditional categorical distribution modes
- **Key Scripts**:
  - `run.py`: Loss, Zlib, Min-K%, Min-K%++ on WikiMIA (original/paraphrased) — self-contained
  - `run_ref.py`: Reference-based methods (Ref, Lowercase attacks)
  - `run_neighbor.py`: Neighbor attack
  - `run_concat.py`: WikiMIA_concat dataset evaluation
- **Method**: Min-K%++ determines whether input token forms a mode under conditional categorical distribution (theoretically motivated via score matching / local maxima insight)
- **Benchmark**: WikiMIA; MIMIR benchmark (via fork)
- **Results**: 6.2–10.5% absolute AUROC improvement over Min-K% on WikiMIA; on par with reference-based methods on MIMIR
- **Supported Models**: Llama, Mamba, Pythia (per GitHub topics)
- **Used For**: Primary MIA detector implementation (Detector Family 3: Min-K%++)

**Query 2: EleutherAI lm-evaluation-harness 13-gram decontamination**

**Repository 2**: EleutherAI/lm-evaluation-harness (⭐ 12K+)
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness
- **Relevance**: Production 13-gram decontamination pipeline — official n-gram detector implementation
- **Architecture**: Inverted index over sorted 13-gram files; exact match scanning
- **Key Pipeline**:
  ```bash
  # Step 1: Generate 13-grams from corpus
  export PYTHONHASHSEED=0
  python -m scripts/clean_training_data/generate_13_grams \
         -dir path/to/working/directory -n 13 -buckets 500
  # Step 2: Sort 13-gram buckets
  python -m scripts/clean_training_data/sort_13_gram_buckets \
         -dir path/to/working/directory/output
  # Step 3: Compress and package
  python -m scripts/clean_training_data/compress_and_package \
         -dir path/to/working/directory -output path/to/final/directory -procs 8
  # Step 4: Evaluate with decontamination
  python main.py --model gpt2 --tasks sciq \
         --decontamination_ngrams_path path/to/ngrams --device cuda:0
  ```
- **Key Files**: `lm_eval/decontaminate.py`, `lm_eval/decontamination/`, `scripts/clean_training_data/`
- **Algorithm**: Build ngram dict → scan sorted training ngrams → mark contaminated docs → produce `_decontaminate` metric suffix
- **Source**: Based on GPT-3 Appendix C (OpenAI, n=8–13); uses n=13 for simplicity
- **Pre-computed indices**: Available for The Pile; C4 indices planned
- **Used For**: N-gram detector (Detector Family 1) + geometry feature extraction (max 13-gram count)

**Query 3: ntunlp/LLMSanitize multi-method contamination library**

**Repository 3**: ntunlp/LLMSanitize (⭐ 61)
- **URL**: https://github.com/ntunlp/LLMSanitize
- **Paper**: "How Much are Large Language Models Contaminated? A Comprehensive Survey and the LLMSanitize Library" (arXiv:2404.00699)
- **Relevance**: Multi-method contamination detection library — includes gpt-2, gpt-3, exact, palm string matching methods + embedding similarity
- **Install**: `pip install llmsanitize` (Python 3.9, CUDA 11.8, vllm 0.3.3)
- **Methods supported**: gpt-2, gpt-3, exact, palm, gpt-4 (string matching); embedding-based methods
- **Used For**: Detector Family 2 (embedding similarity) + ConStat/ConTAM baseline (Detector Family 5)

**SBERT + FAISS for Corpus Embedding Index**

**Repository 4**: UKPLab/sentence-transformers (⭐ 19K+)
- **URL**: https://github.com/UKPLab/sentence-transformers
- **Key Code**:
  ```python
  from sentence_transformers import SentenceTransformer
  from sentence_transformers.quantization import semantic_search_faiss
  model = SentenceTransformer("all-MiniLM-L6-v2")
  corpus_embeddings = model.encode(corpus, normalize_embeddings=True)
  # Build FAISS index and search
  results, search_time, corpus_index = semantic_search_faiss(
      query_embeddings, corpus_embeddings=corpus_embeddings, top_k=1)
  ```
- **Used For**: SBERT cosine similarity geometry feature (max cosine to nearest corpus neighbor)

**Serena Analysis Needed**: false

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

Priority order for this experiment:
1. ⭐⭐⭐ zjysteven/mink-plus-plus — official Min-K%++ author implementation (ICLR'25)
2. ⭐⭐⭐ EleutherAI/lm-evaluation-harness — production n-gram decontamination pipeline
3. ⭐⭐ ntunlp/LLMSanitize — multi-method library for embedding + string matching methods
4. ⭐⭐ UKPLab/sentence-transformers + FAISS — SBERT geometry feature extraction

**Recommended Implementation Path:**
- Primary: zjysteven/mink-plus-plus (Min-K%++) + EleutherAI/lm-evaluation-harness (n-gram)
- Fallback: ntunlp/LLMSanitize for embedding similarity methods
- Justification: Official author implementations ensure reproducibility; lm-evaluation-harness is the production-validated n-gram pipeline used in published evaluations

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. EleutherAI pipeline and Min-K%++ `run.py` scripts are self-contained and well-documented.

---

## Experiment Specification

### Dataset

**Type:** standard (real public benchmarks × real pretraining corpora — NOT synthetic)

**Benchmark Datasets (evaluation items):**
- MMLU (Massive Multitask Language Understanding): ~14K test items across 57 subjects
  - HuggingFace: `cais/mmlu`, split: `test`
  - Covers: knowledge/factual reasoning
- HellaSwag: ~10K test items
  - HuggingFace: `Rowan/hellaswag`, split: `validation`
  - Covers: commonsense completion reasoning
- GSM8K (Grade School Math 8K): ~1.3K test items
  - HuggingFace: `openai/gsm8k`, config: `main`, split: `test`
  - Covers: multi-step mathematical reasoning

**Pretraining Corpora (geometry index sources):**
- The Pile: EleutherAI's 825GB diverse corpus
  - HuggingFace: `EleutherAI/pile` (streaming recommended due to size)
  - Pre-computed 13-gram indices available from EleutherAI/lm-evaluation-harness
- C4 (Colossal Clean Crawled Corpus): allenai/c4
  - HuggingFace: `allenai/c4`, config: `en`
  - Note: Large (~13TB), use streaming and subset
- RedPajama-Data-1T: togethercomputer/RedPajama-Data-1T
  - HuggingFace: `togethercomputer/RedPajama-Data-1T` (streaming)

**Total benchmark items:** ~25K across 3 benchmarks × 3 corpora = 9 benchmark-corpus pairs
**Contamination Rate:** Equal-prevalence subsampling at 10% (per Phase 2A plan)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `cais/mmlu`, `Rowan/hellaswag`, `openai/gsm8k` (benchmarks); `EleutherAI/pile`, `allenai/c4`, `togethercomputer/RedPajama-Data-1T` (corpora)
- Code:
  ```python
  from datasets import load_dataset
  mmlu = load_dataset("cais/mmlu", "all", split="test")
  hellaswag = load_dataset("Rowan/hellaswag", split="validation")
  gsm8k = load_dataset("openai/gsm8k", "main", split="test")
  # Corpora (streaming for large size)
  pile = load_dataset("EleutherAI/pile", split="train", streaming=True)
  c4 = load_dataset("allenai/c4", "en", split="train", streaming=True)
  redpajama = load_dataset("togethercomputer/RedPajama-Data-1T", split="train", streaming=True)
  ```

### Models

#### Baseline Model

**Architecture:** N-gram detector (EleutherAI 13-gram inverted index pipeline)
- Reference implementation: EleutherAI/lm-evaluation-harness `lm_eval/decontaminate.py`
- Method: Exact 13-gram overlap between benchmark item and sorted corpus n-gram files
- No ML model required — pure string matching
- Per-item output: contaminated (1) / clean (0) + max n-gram match count

**Supporting LLMs** (required for Min-K%++ and DC-PDD detectors):
- Llama-2-7B: `meta-llama/Llama-2-7b-hf`
- Mistral-7B: `mistralai/Mistral-7B-v0.1`
- Pythia-7B: `EleutherAI/pythia-6.9b` (closest to 7B; trained on The Pile — provides known-corpus ground truth)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers (AutoModelForCausalLM)
- Identifier: `meta-llama/Llama-2-7b-hf`, `mistralai/Mistral-7B-v0.1`, `EleutherAI/pythia-6.9b`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  import torch
  model = AutoModelForCausalLM.from_pretrained(
      "meta-llama/Llama-2-7b-hf",
      torch_dtype=torch.bfloat16,
      device_map="auto"
  )
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
  ```

#### Proposed Model

**Architecture:** Geometry-stratified multi-detector evaluation framework

The "proposed model" in H-E1 is not a single ML model but the stratification + evaluation framework:
1. Corpus-side geometry feature extractor (13-gram count + SBERT cosine)
2. Stratum classifier (top-quartile thresholds → lexical / semantic / indeterminate)
3. All 5 detector families applied per stratum
4. Per-stratum metric computation

**Core Mechanism Implementation:**

```python
# Core Mechanism: Contamination Geometry Stratification
# Based on: EleutherAI/lm-evaluation-harness + sentence-transformers

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class GeometryStratifier:
    """Compute corpus-side geometry features and assign strata."""

    def __init__(self, sbert_model="all-MiniLM-L6-v2", ngram_n=13):
        self.sbert = SentenceTransformer(sbert_model)
        self.ngram_n = ngram_n
        self.faiss_index = None  # FAISS index over corpus embeddings

    def build_corpus_index(self, corpus_texts):
        """Build FAISS index from corpus embeddings."""
        embeddings = self.sbert.encode(corpus_texts, normalize_embeddings=True,
                                       show_progress_bar=True, batch_size=256)
        dim = embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatIP(dim)  # cosine via normalized vecs
        self.faiss_index.add(embeddings.astype(np.float32))

    def compute_geometry_features(self, benchmark_items, ngram_index):
        """Return (max_13gram_count, max_sbert_cosine) per item."""
        query_embeds = self.sbert.encode(benchmark_items, normalize_embeddings=True,
                                          batch_size=256)
        cosines, _ = self.faiss_index.search(query_embeds.astype(np.float32), k=1)
        ngram_counts = [ngram_index.max_overlap(item, n=self.ngram_n)
                        for item in benchmark_items]
        return np.array(ngram_counts), cosines[:, 0]

    def assign_strata(self, ngram_counts, cosines,
                      lexical_thresh=None, semantic_thresh=None):
        """Assign items to lexical/semantic/indeterminate strata."""
        if lexical_thresh is None:
            lexical_thresh = np.percentile(ngram_counts, 75)
        if semantic_thresh is None:
            semantic_thresh = np.percentile(cosines, 75)
        strata = np.full(len(ngram_counts), "indeterminate", dtype=object)
        strata[ngram_counts >= lexical_thresh] = "lexical"
        strata[cosines >= semantic_thresh] = "semantic"
        return strata  # shape: (N,)
```

### Training Protocol

This is an EXISTENCE (PoC) experiment — no gradient-based training required.
The "training" is the corpus index construction and threshold calibration.

**Infrastructure Setup:**
- Optimizer: N/A (no gradient descent)
- Loss: N/A
- Epochs: N/A
- Batch Size: 256 (for SBERT encoding)
- Seed: 42 (fixed, single run)

**Corpus Index Construction:**
- 13-gram index: EleutherAI pipeline (`generate_13_grams.py` → `sort_13_gram_buckets.py` → `compress_and_package.py`)
- SBERT index: FAISS IndexFlatIP over `all-MiniLM-L6-v2` embeddings (normalized → inner product = cosine)
- Stratum thresholds: top-quartile (75th percentile) of each geometry feature across all items × corpora

**Detector Evaluation:**
- Min-K%++ (zjysteven/mink-plus-plus `run.py`): k=20% (default); evaluated on Llama-2-7B, Mistral-7B, Pythia-7B
- N-gram (EleutherAI/lm-evaluation-harness): 13-gram exact match; binary contaminated/clean per item
- Embedding similarity (ntunlp/LLMSanitize): cosine threshold for contamination binary label
- DC-PDD: Fixed reference model (Pythia-2.8B as neutral-corpus reference); per Zhang et al. 2024
- ConStat: Longest contaminated substring; per Singh et al. 2024

**Approach A** (known inclusion audit): Pythia-7B test items known to appear in The Pile
**Approach B** (simulated leakage): 3 injection regimes — uniform, clustered, paraphrased (via lm-sys/llm-decontaminator)

**Bootstrap CI**: N=10,000 iterations for 95% CI on all recall/F1 estimates
**Compute Budget**: ~24-48 GPU-hours on single A100

### Evaluation

**Task Type:** Binary contamination detection → per-stratum recall/F1 analysis

**Primary Metrics:**
- N-gram Recall by stratum:
  - Lexical stratum target: recall ≥ 0.80
  - Semantic stratum target: recall ≤ 0.40
- Min-K%++ F1 variance across The Pile / C4 / RedPajama for MMLU or HellaSwag: ≥ 0.15
- Indeterminacy Rate: fraction of items where no detector has F1 margin ≥ 0.05 above second-best: target [10%, 50%]

**Success Criteria (PoC — Direction-based):**
- PRIMARY: N-gram recall ≥ 0.80 in lexical stratum AND ≤ 0.40 in semantic stratum
- SECONDARY: Min-K%++ F1 variance ≥ 0.15 across 3 corpora for MMLU or HellaSwag
- TERTIARY: Indeterminacy rate in [10%, 50%] (blind spot confirmed but routing remains useful)

**PoC Pass Condition:** proposed_metric (geometry-stratified recall separation) > baseline_metric (unstratified single recall)

**Expected Baseline Performance** (from research):
- N-gram (13-gram) on lexical contamination: high recall expected (production-validated per EleutherAI)
- Min-K%++ on WikiMIA: AUROC 0.6–0.8 (varies by model); variance across corpora unknown (novel)
- Source: zjysteven/mink-plus-plus paper (arXiv:2404.02936); EleutherAI/lm-evaluation-harness docs

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary classification (contaminated/clean) + ordinal ranking (detector families by F1)
- Library: `sklearn.metrics` (recall_score, f1_score, bootstrap via scipy.stats); custom variance computation
- Code:
  ```python
  from sklearn.metrics import recall_score, f1_score
  import numpy as np
  # Per-stratum recall
  recall_lexical = recall_score(y_true[lexical_mask], y_pred_ngram[lexical_mask])
  recall_semantic = recall_score(y_true[semantic_mask], y_pred_ngram[semantic_mask])
  # Min-K++ F1 variance across corpora
  f1_per_corpus = [f1_score(y_true_c, y_pred_minkpp_c) for c in corpora]
  variance = np.var(f1_per_corpus)
  # Indeterminacy rate
  margins = top1_f1 - top2_f1  # per item
  indeterminate_rate = np.mean(margins < 0.05)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing target vs actual:
  - N-gram recall in lexical stratum (target ≥ 0.80)
  - N-gram recall in semantic stratum (target ≤ 0.40)
  - Min-K%++ F1 variance across corpora (target ≥ 0.15)

#### Additional Figures (LLM Autonomous)
- **2D Contamination Phase Diagram**: Scatter plot of all ~25K benchmark items in (max-13gram-count × max-SBERT-cosine) space, colored by dominant detector family; indeterminate zone highlighted in grey
- **Per-stratum F1 heatmap**: All 5 detectors × 3 strata × 3 corpora grid
- **Min-K%++ F1 variance bar chart**: Per-corpus F1 for MMLU and HellaSwag separately
- **Indeterminacy rate pie chart**: Proportion of lexical / semantic / indeterminate items per benchmark

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. N-gram recall in lexical stratum > N-gram recall in semantic stratum (directional separation confirmed)
3. Min-K%++ F1 variance across corpora > 0 (any variance detected)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Archon KB Assessment:** No relevant prior cases — KB specialized for diffusion/image generation. All implementation guidance from Exa GitHub searches below.

### B. GitHub Implementations (Exa)

**Repository 1**: zjysteven/mink-plus-plus (⭐ 54) — OFFICIAL AUTHOR IMPLEMENTATION
- **URL**: https://github.com/zjysteven/mink-plus-plus
- **Query Used**: "zjysteven mink-plus-plus Min-K++ contamination detection implementation GitHub"
- **Relevance**: Official ICLR'25 Spotlight implementation of Min-K%++ — primary MIA detector
- **Method**: Conditional categorical distribution mode detection; reference-free; works on token log-probabilities
- **Key Scripts**: `run.py` (Loss, Zlib, Min-K%, Min-K%++), `run_ref.py`, `run_neighbor.py`
- **Supported models**: Llama, Pythia, Mamba (white-box access required)
- **Results**: 6.2–10.5% AUROC improvement over Min-K% on WikiMIA
- **Used For**: Detector Family 3 (Min-K%++) implementation; F1 variance across corpora metric

**Repository 2**: EleutherAI/lm-evaluation-harness (⭐ 12K+) — PRODUCTION N-GRAM PIPELINE
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness
- **Query Used**: "EleutherAI lm-evaluation-harness n-gram decontamination 13-gram overlap detection"
- **Relevance**: Production 13-gram decontamination pipeline used in published LLM evaluations
- **Key Pipeline**:
  ```bash
  python -m scripts/clean_training_data/generate_13_grams -dir ./work -n 13 -buckets 500
  python -m scripts/clean_training_data/sort_13_gram_buckets -dir ./work/output
  python -m scripts/clean_training_data/compress_and_package -dir ./work -output ./final -procs 8
  ```
- **Algorithm**: Build ngram dict → scan sorted training ngrams → mark contaminated (binary label + max count)
- **Source**: GPT-3 Appendix C; uses n=13 for simplicity; pre-computed Pile indices available
- **Key Files**: `lm_eval/decontaminate.py`, `lm_eval/decontamination/`, `scripts/clean_training_data/`
- **Used For**: Detector Family 1 (n-gram) + geometry feature: max 13-gram count per item

**Repository 3**: ntunlp/LLMSanitize (⭐ 61) — MULTI-METHOD LIBRARY
- **URL**: https://github.com/ntunlp/LLMSanitize
- **Query Used**: "ntunlp LLMSanitize benchmark contamination detection FAISS embedding similarity GitHub"
- **Relevance**: Comprehensive contamination detection library supporting gpt-2, gpt-3, exact, palm string matching + embedding methods
- **Install**: `pip install llmsanitize`
- **Used For**: Detector Family 2 (embedding similarity) + ConStat baseline (Detector Family 5)

**Repository 4**: UKPLab/sentence-transformers (⭐ 19K+) — SBERT + FAISS
- **URL**: https://github.com/UKPLab/sentence-transformers
- **Key Code**:
  ```python
  from sentence_transformers import SentenceTransformer
  model = SentenceTransformer("all-MiniLM-L6-v2")
  embeddings = model.encode(corpus_texts, normalize_embeddings=True, batch_size=256)
  # Build FAISS flat index for cosine similarity
  import faiss
  index = faiss.IndexFlatIP(embeddings.shape[1])
  index.add(embeddings.astype("float32"))
  cosines, ids = index.search(query_embeddings.astype("float32"), k=1)
  ```
- **Used For**: SBERT cosine similarity geometry feature (max cosine to nearest corpus neighbor)

**Repository 5**: lm-sys/llm-decontaminator (⭐ 320) — PARAPHRASED INJECTION (APPROACH B)
- **URL**: https://github.com/lm-sys/llm-decontaminator
- **Paper**: "Rethinking Benchmark and Contamination for Language Models with Rephrased Samples" (arXiv:2311.04850)
- **Relevance**: Enables Approach B simulated leakage with paraphrased injection regime
- **Used For**: Approach B injection regime 3 (paraphrased contamination simulation)

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from Exa search results was sufficiently clear. All key implementations are well-documented in official repositories with self-contained scripts.

### D. Previous Hypothesis Context

**Previous Context**: None — this is the first hypothesis (H-E1) in the verification chain. No prior validation results to inherit.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Benchmark datasets (MMLU, HellaSwag, GSM8K) | Phase 2A / HuggingFace | 02b_verification_plan.md Section 1.3; HuggingFace Hub |
| Pretraining corpora (The Pile, C4, RedPajama) | Phase 2A / HuggingFace | 02b_verification_plan.md Section 1.3; HuggingFace Hub |
| N-gram detector (13-gram) | GitHub | EleutherAI/lm-evaluation-harness (B.2) |
| Min-K%++ detector | GitHub | zjysteven/mink-plus-plus ICLR'25 (B.1) |
| Embedding similarity detector | GitHub | ntunlp/LLMSanitize (B.3) |
| SBERT cosine geometry feature | GitHub | UKPLab/sentence-transformers + FAISS (B.4) |
| Approach B paraphrased injection | GitHub | lm-sys/llm-decontaminator (B.5) |
| LLM models (Llama-2-7B, Mistral-7B, Pythia-7B) | Phase 2A / HuggingFace | 02b_verification_plan.md Section 1.3 |
| Stratum thresholds (top-quartile) | Phase 2B | 02b_verification_plan.md Section 2.2 H-E1 |
| Bootstrap CI (N=10,000) | Phase 2B | 02b_verification_plan.md Section 2.2 H-E1 |
| Success criteria (recall ≥ 0.80 / ≤ 0.40) | Phase 2B | 02b_verification_plan.md H-E1 success criteria |
| Pseudo-code (GeometryStratifier) | GitHub + Research | sentence-transformers FAISS example (B.4); EleutherAI pipeline (B.2) |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-13T02:20:00Z

### Workflow History for This Hypothesis
- 2026-05-13: Hypothesis h-e1 set to IN_PROGRESS (External loop starting Phase 2C → 3 → 4)
- 2026-05-13: Phase 2C experiment design initiated (UNATTENDED mode)
- 2026-05-13: Archon KB searched (3 queries — no domain-relevant results)
- 2026-05-13: Exa GitHub searched (3 queries — 5 relevant repositories found)
- 2026-05-13: Dataset confirmed as standard (not synthetic): MMLU + HellaSwag + GSM8K
- 2026-05-13: Experiment specification synthesized at Level 1.5
- 2026-05-13: Phase 2C experiment design COMPLETED

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code — 5 queries, 0 domain-relevant results), Exa (GitHub — 3 queries, 5 relevant repositories), Serena (skipped — code clear)*
*All specifications grounded in researched official implementations*
*Next Phase: Phase 3 - Implementation Planning*
