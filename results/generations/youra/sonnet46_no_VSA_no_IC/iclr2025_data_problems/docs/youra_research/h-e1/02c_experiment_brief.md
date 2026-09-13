# Experiment Design: h-e1

**Date:** 2026-08-20
**Author:** yoon303b@gmail.com
**Hypothesis Statement:** Under the Pythia model family trained on The Pile, domain exposure trajectories computed from exact dataloaders at 154 training checkpoints × 16 model sizes are non-uniform across domains (std > 0.001 for ≥10 of 22 domains), providing measurable within-family variation in cumulative domain exposure fractions that can serve as time-varying covariates in a panel regression.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** None required (root hypothesis)
**Gate Status:** MUST_WORK — pass condition: ≥10 of 22 domains show std > 0.001 in ≥8 of 16 model sizes

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition

MUST_WORK: ≥10 of 22 The Pile domains must show std(cumulative_exposure_fraction) > 0.001 across 154 checkpoints in at least 8 of 16 Pythia model sizes. If fewer than 10 domains meet this threshold, the cross-family fallback design activates and h-m1/h-m2/h-m3 are blocked.

---

## Continuation Context

This is the root hypothesis. No previous hypothesis results to carry forward.

### Previous Hypothesis Results (if applicable)
None — h-e1 is the first hypothesis in the verification chain.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** Archon KB contains image diffusion content only (Diffusers, PixArt, DALLE2). No relevant prior cases exist for Pythia/The Pile domain exposure analysis. All implementation patterns sourced from Exa GitHub searches below.

**Queries executed:**
1. `domain exposure trajectory language model pre-training checkpoints` → 0 relevant results (max similarity 0.50, all image diffusion)
2. `Pythia training checkpoints domain analysis panel regression` → 0 relevant results (max similarity 0.42)
3. `The Pile domain composition benchmark evaluation MMLU HellaSwag` → 0 relevant results (max similarity 0.42)
4. `Pythia dataloader token index domain mapping` → 0 relevant code results
5. `cumulative domain fraction variance training checkpoints` → 0 relevant code results

**Assessment:** Archon KB does not contain LLM pre-training analysis cases. Implementation grounded entirely in official EleutherAI repositories found via Exa.

### Archon Code Examples

No relevant code examples found in Archon KB. See Exa GitHub findings below.

### Exa GitHub Implementations

**Query 1: EleutherAI Official Implementation (HIGHEST PRIORITY)**

**Repository 1**: EleutherAI/pythia (⭐2852)
- **URL**: https://github.com/EleutherAI/pythia
- **Relevance**: Official Pythia repository — provides exact dataloader reconstruction tools used during training
- **Key Code** (`utils/mmap_dataset.py`):
  ```python
  class MMapIndexedDataset(torch.utils.data.Dataset):
      def __getitem__(self, idx):
          if isinstance(idx, int):
              ptr, size = self._index[idx]
              np_array = np.frombuffer(
                  self._bin_buffer, dtype=self._index.dtype, count=size, offset=ptr
              )
              return np_array
          elif isinstance(idx, slice):
              # Returns shape (n_samples, 2049) token sequences
              np_array = np.frombuffer(...)
              return np_array.reshape(-1, 2049)
      
      @property
      def doc_idx(self):
          return self._index.doc_idx  # Document boundary indices
  ```
- **Data Access Pattern**:
  - Download: `git lfs clone https://huggingface.co/datasets/EleutherAI/pythia_deduped_pile_idxmaps`
  - Unshard: `python utils/unshard_memmap.py --input_file ./pile_0.87_deduped_text_document-00000-of-00082.bin --num_shards 83`
  - Batch viewer: `utils/batch_viewer.py` — extracts training indices as numpy array for any step range
- **Index Map Files**: `*_doc_idx.npy` (document indices), `*_sample_idx.npy` (sample indices), `*_shuffle_idx.npy` (shuffle order)
- **Domain Label Source**: The Pile JSONL metadata field `meta.pile_set_name` — 22 possible values
- **Model Loading**:
  ```python
  from transformers import GPTNeoXForCausalLM, AutoTokenizer
  model = GPTNeoXForCausalLM.from_pretrained(
      "EleutherAI/pythia-70m-deduped",
      revision="step3000",
      cache_dir="./pythia-70m-deduped/step3000",
  )
  ```

**Repository 2**: EleutherAI/pile-preshuffled-seeds
- **URL**: https://huggingface.co/datasets/EleutherAI/pile-preshuffled-seeds
- **Relevance**: Provides `dataset.py` example for loading MMapIndexedDataset with index maps; used by PolyPythia for multi-seed analysis
- **Key Info**: Each seed directory has `*_doc_idx.npy`, `*_sample_idx.npy`, `*_shuffle_idx.npy`; total 32.1 GB

**Query 2: The Pile Domain Metadata**

**Source**: HuggingFace `EleutherAI/pile` dataset card
- **Domain field**: `meta.pile_set_name` — string label per document
- **22 domains**: Pile-CC, PubMed Central, Books3, OpenWebText2, ArXiv, GitHub, FreeLaw, StackExchange, USPTO Backgrounds, PubMed Abstracts, Gutenberg (PG-19), OpenSubtitles, Wikipedia (en), DM Mathematics, Ubuntu IRC, BookCorpus2, EuroParl, HackerNews, YoutubeSubtitles, PhilPapers, NIH ExPorter, Enron Emails
- **Loading**: `from datasets import load_dataset; ds = load_dataset("EleutherAI/pile", split="train")`
- **Domain distribution**: Published proportions available from Pile paper (Gao et al., 2021, 2101.00027)

**Query 3: Benchmark Evaluation**

**Repository**: EleutherAI/lm-evaluation-harness (⭐13712)
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness
- **Relevance**: Official evaluation framework; supports Pythia checkpoint evaluation via `revision` parameter
- **Python API**:
  ```python
  import lm_eval
  results = lm_eval.simple_evaluate(
      model="hf",
      model_args="pretrained=EleutherAI/pythia-70m-deduped,revision=step3000",
      tasks=["mmlu", "hellaswag", "arc_challenge", "winogrande"],
      num_fewshot=5,  # MMLU standard; HellaSwag uses 10
      batch_size=8,
      device="cuda:0",
  )
  ```
- **Note**: This step is NOT part of h-e1 (h-e1 only measures domain exposure variance, not benchmark scores). Benchmark evaluation is required for h-m2/h-m3.

**Serena Analysis Needed**: false

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

h-e1 is not a paper reproduction — it is a novel data extraction and analysis step. The official EleutherAI/pythia repository provides all required infrastructure:
1. `MMapIndexedDataset` for reading tokenized training sequences
2. `utils/batch_viewer.py` for extracting training indices at each checkpoint step
3. `pythia_deduped_pile_idxmaps` HuggingFace dataset for exact shuffle ordering
4. The Pile `meta.pile_set_name` field for domain labels

**Recommended Implementation Path:**
- Primary: EleutherAI/pythia official repo + `EleutherAI/pythia_deduped_pile_idxmaps` dataset
- Fallback: EleutherAI/pile HuggingFace dataset (direct JSONL parsing for domain labels if index mapping fails)
- Justification: Official tools guarantee exact reproduction of training data order seen by each checkpoint; any alternative risks index mismatch

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. `MMapIndexedDataset` from `EleutherAI/pythia/utils/mmap_dataset.py` is a straightforward numpy memory-mapped array interface with well-documented `doc_idx` property for document boundary reconstruction. No additional semantic analysis required.

---

## Experiment Specification

### Dataset

**Name**: The Pile (Pythia pre-tokenized index maps)
**Type**: programmatic-api (real training data via official HuggingFace datasets + local index map files)
**Source**: EleutherAI
**Version**: Deduplicated Pile (pythia_deduped_pile_idxmaps); 207B tokens, ~1.5 epochs

**What we extract (not "training" on — read-only analysis):**
- For each Pythia model size and each of 154 checkpoints: the set of document indices seen up to that checkpoint step
- Map each document index → The Pile domain label via `meta.pile_set_name`
- Compute `cumulative_domain_fraction[d, t]` for all 22 domains `d` and checkpoints `t = 0..153`

**22 The Pile Domains**:
Pile-CC, PubMed Central, Books3, OpenWebText2, ArXiv, GitHub, FreeLaw, StackExchange, USPTO Backgrounds, PubMed Abstracts, Gutenberg (PG-19), OpenSubtitles, Wikipedia (en), DM Mathematics, Ubuntu IRC, BookCorpus2, EuroParl, HackerNews, YoutubeSubtitles, PhilPapers, NIH ExPorter, Enron Emails

**Domain label mapping**: Build lookup table `{doc_global_idx → pile_set_name}` from the Pile JSONL files (or HuggingFace `EleutherAI/pile` dataset `meta.pile_set_name` field). This is a one-time preprocessing step.

**Checkpoint steps** (154 total per model):
- Log-spaced early: step0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512
- Linear: step1000, step2000, ..., step143000 (143 steps)

**Storage requirement**: ~32 GB for index map files; domain lookup table ~few GB for full Pile

**Synthetic data check**: PASSED — real training data from EleutherAI

**Loading Information** (for Phase 4 download):
- Method: HuggingFace LFS + local file
- Identifier: `EleutherAI/pythia_deduped_pile_idxmaps` (index maps); `EleutherAI/pile` (domain labels)
- Code:
  ```python
  # Step 1: Download index maps
  # git lfs clone https://huggingface.co/datasets/EleutherAI/pythia_deduped_pile_idxmaps
  # python utils/unshard_memmap.py --input_file ./pile_0.87_deduped_text_document-00000-of-00082.bin --num_shards 83
  
  # Step 2: Load domain labels
  from datasets import load_dataset
  pile = load_dataset("EleutherAI/pile", split="train", streaming=True)
  # Build doc_id -> domain lookup: {i: ex['meta']['pile_set_name'] for i, ex in enumerate(pile)}
  
  # Step 3: Load MMapIndexedDataset
  from utils.mmap_dataset import MMapIndexedDataset
  dataset = MMapIndexedDataset("./pythia_pile_idxmaps/pile_0.87_deduped_text_document")
  ```

### Models

#### Baseline Model

**Architecture**: Pythia model suite (GPT-NeoX architecture)
**Sizes**: 16 model sizes — 70M, 160M, 410M, 1B, 1.4B, 2.8B, 6.9B, 12B (+ deduped variants = 16 total)
**Checkpoints**: 154 per model size
**Source**: EleutherAI on HuggingFace

**Note for h-e1**: The models themselves are NOT loaded for inference in this hypothesis. h-e1 only analyzes the data ordering (index maps) to compute domain exposure fractions. Model loading is required for h-m2/h-m3 (benchmark evaluation).

**Loading Information** (for Phase 4 reference — not required for h-e1 computation):
- Method: HuggingFace `transformers`
- Identifier: `EleutherAI/pythia-{size}-deduped` with `revision="step{N}"`
- Code:
  ```python
  from transformers import GPTNeoXForCausalLM
  model = GPTNeoXForCausalLM.from_pretrained(
      "EleutherAI/pythia-70m-deduped",
      revision="step3000",
  )
  ```

#### Proposed Model

**Architecture:** Baseline + domain exposure trajectory computation

**Core Mechanism Implementation:**

```python
# Core Mechanism: Cumulative Domain Exposure Fraction Computation
# Based on: EleutherAI/pythia utils/mmap_dataset.py + batch_viewer.py
# Source: https://github.com/EleutherAI/pythia

import numpy as np
from utils.mmap_dataset import MMapIndexedDataset

def compute_domain_exposure_trajectories(
    dataset: MMapIndexedDataset,
    doc_to_domain: dict,          # {global_doc_idx: pile_set_name}
    checkpoint_steps: list,       # [0, 1, 2, 4, ..., 143000]
    tokens_per_step: int = 2097152,  # 2M tokens/step (Pythia batch size)
    n_domains: int = 22,
) -> np.ndarray:
    """
    Returns: cumulative_fraction[domain_idx, checkpoint_idx]
             shape: (22, 154)
    """
    domain_names = sorted(set(doc_to_domain.values()))
    domain_to_idx = {d: i for i, d in enumerate(domain_names)}
    
    cumulative_counts = np.zeros(n_domains, dtype=np.int64)
    trajectories = np.zeros((n_domains, len(checkpoint_steps)))
    
    step_ptr = 0  # current sample index in dataset
    for ckpt_idx, step in enumerate(checkpoint_steps):
        # tokens seen up to this checkpoint
        tokens_seen = step * tokens_per_step
        target_sample = tokens_seen // 2049  # sequence length
        
        # Accumulate domain counts for new samples since last checkpoint
        for sample_idx in range(step_ptr, min(target_sample, len(dataset))):
            doc_idx = dataset.doc_idx[sample_idx]  # global doc index
            domain = doc_to_domain.get(doc_idx, "Unknown")
            if domain in domain_to_idx:
                cumulative_counts[domain_to_idx[domain]] += 1
        step_ptr = target_sample
        
        total = cumulative_counts.sum()
        trajectories[:, ckpt_idx] = (
            cumulative_counts / total if total > 0 else 0.0
        )
    return trajectories, domain_names


def compute_variance_stats(trajectories: np.ndarray) -> dict:
    """Check h-e1 gate: std > 0.001 for >= 10 domains"""
    stds = np.std(trajectories, axis=1)  # std across 154 checkpoints per domain
    n_passing = np.sum(stds > 0.001)
    return {
        "per_domain_std": stds,
        "n_domains_passing": int(n_passing),
        "gate_passed": bool(n_passing >= 10),
    }
```

### Training Protocol

**Note for h-e1 (EXISTENCE PoC):** This is a data analysis experiment, not a model training experiment. There is no gradient descent, optimizer, or loss function. The "training protocol" describes the computational pipeline.

**Pipeline**:
1. **Preprocessing** (one-time, ~24h): Download index maps; build `doc_id → domain` lookup from Pile JSONL
2. **Trajectory computation** (per model size, ~1h each): Iterate through 154 checkpoints × token index maps, accumulate domain counts, normalize to fractions
3. **Variance analysis** (seconds): Compute `std(cumulative_fraction[d, :])` for each domain `d`; count domains with std > 0.001

**Model sizes to process**: All 16 (or prioritize 8 deduped variants for h-e1 gate check)
**Representative subset** (fast PoC): 3 model sizes (70M, 1B, 6.9B) — sufficient to check gate before full 16-size run
**Seed**: 1 (fixed; Pythia training order is deterministic given index maps)
**Parallelism**: Process each model size independently (trivially parallelizable)

### Evaluation

**Primary Metric**:
- `n_domains_passing` = count of domains where std(cumulative_exposure_fraction across 154 checkpoints) > 0.001
- Gate: `n_domains_passing >= 10` in at least 8 of 16 model sizes

**Secondary Metric**:
- Spearman ρ between domain variance rankings across any two model sizes (expected > 0.7 if ordering is consistent)

**Success Criteria**:
- Primary: `n_domains_passing >= 10` in ≥8/16 model sizes → **GATE PASSED** → proceed to h-m1
- Secondary: Spearman ρ > 0.7 → domain exposure variation is structurally consistent across scales

**Expected Baseline** (informed by Phase 2B):
- The Pile is shuffled but NOT uniformly: domain blocks appear in proportional chunks. Wikipedia (~3%) should show rapid early accumulation then plateau; Books3 (~12%) should show steadier increase. Non-uniform shuffling predicts std > 0.001 for most domains.
- If fully uniform shuffle (null hypothesis): all `cumulative_fraction[d,t] ≈ constant` → std ≈ 0 → gate FAILS

**Failure Response**:
- If < 10 domains pass: activate cross-family fallback (collect n≥15 model families with known corpus domain proportions)
- If borderline: explore relaxed threshold (std > 0.0005), document limitation

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical analysis (not classification/regression)
- Library: `numpy` (std, spearmanr from `scipy.stats`)
- Code:
  ```python
  import numpy as np
  from scipy.stats import spearmanr
  
  stds = np.std(trajectories, axis=1)          # (22,)
  n_passing = np.sum(stds > 0.001)
  rho, _ = spearmanr(stds_model_A, stds_model_B)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — per-domain std values with threshold line at 0.001; bars colored by pass/fail

#### Additional Figures (LLM Autonomous)

1. **Domain Exposure Trajectories**: Line plot — `cumulative_fraction[d, t]` vs checkpoint step for top-5 and bottom-5 variance domains (shows non-uniformity visually)
2. **Variance Heatmap**: 22 domains × 16 model sizes — std values as heatmap (shows consistency across scales)
3. **Spearman Correlation Matrix**: 16×16 model-size pair correlation matrix (confirms structural consistency)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (domain extraction pipeline completes for ≥3 model sizes)
2. `n_domains_passing >= 10` in ≥2 of 3 representative model sizes (70M, 1B, 6.9B)

**Mechanism Verification Protocol:**

| Element | Specification |
|---------|---------------|
| Pre-condition | Index map files downloaded; doc→domain lookup built; MMapIndexedDataset loads without error |
| Activation indicator | Log: `"Checkpoint step{N}: domain_counts={...}, total_tokens={...}"` printed per checkpoint |
| Tensor shape check | `trajectories.shape == (22, 154)` for each model size |
| Metric delta expected | At least 1 domain with std > 0.01 (Wikipedia or Pile-CC expected to show largest variation) |
| Failure detection | If all stds < 0.0001 → shuffle is near-uniform → report assumption A1 violated |
| Success threshold | `n_domains_passing >= 10` |
| Success metric | `per_domain_std` array |

**Architecture compatibility**: Not applicable (no neural network architecture — pure data analysis pipeline).

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

No relevant sources found. Archon KB contains image diffusion content only.
- Queries: 5 executed, 0 relevant results
- Max similarity: 0.50 (all image diffusion repos)
- Impact: Zero — all implementation patterns sourced from official EleutherAI repos via Exa

### B. GitHub Implementations (Exa)

**Repository 1**: EleutherAI/pythia (⭐2852) — PRIMARY
- **URL**: https://github.com/EleutherAI/pythia
- **Query Used**: `EleutherAI pythia dataloader indices token domain mapping The Pile GitHub`
- **Relevance**: Official repository; provides `MMapIndexedDataset`, `batch_viewer.py`, exact index map download instructions
- **Key Code**: `utils/mmap_dataset.py` — `MMapIndexedDataset.__getitem__`, `doc_idx` property
- **Configuration Extracted**:
  - Tokens per step: 2,097,152 (batch size)
  - Sequence length: 2049 tokens
  - Total steps: 143,000 (step143000 = main branch)
  - Index map dataset: `EleutherAI/pythia_deduped_pile_idxmaps` (LFS, ~32 GB)
- **Used For**: Core mechanism pseudo-code; dataset loading code; checkpoint step enumeration

**Repository 2**: EleutherAI/pile-preshuffled-seeds (HuggingFace)
- **URL**: https://huggingface.co/datasets/EleutherAI/pile-preshuffled-seeds
- **Query Used**: Same as above
- **Relevance**: Shows index map file structure (`_doc_idx.npy`, `_sample_idx.npy`, `_shuffle_idx.npy`) and provides `dataset.py` example
- **Used For**: Understanding index map file format; domain lookup construction pattern

**Repository 3**: EleutherAI/pile (HuggingFace dataset)
- **URL**: https://huggingface.co/datasets/EleutherAI/pile
- **Query Used**: `EleutherAI pile domain label metadata pile_set_name mapping 22 domains`
- **Relevance**: Confirms `meta.pile_set_name` field structure; lists all 22 domain names
- **Key Code**:
  ```python
  # Domain field access
  {'meta': {'pile_set_name': 'Pile-CC'}, 'text': '...'}
  # Load: from datasets import load_dataset
  # ds = load_dataset("EleutherAI/pile", split="train")
  ```
- **Used For**: Domain label taxonomy (22 names); domain lookup table construction

**Repository 4**: EleutherAI/lm-evaluation-harness (⭐13712)
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness
- **Query Used**: `lm-evaluation-harness pythia checkpoint evaluation MMLU HellaSwag ARC WinoGrande step revision`
- **Relevance**: Required for h-m2/h-m3 benchmark evaluation (not h-e1 directly)
- **Python API**:
  ```python
  import lm_eval
  results = lm_eval.simple_evaluate(
      model="hf",
      model_args="pretrained=EleutherAI/pythia-70m-deduped,revision=step3000",
      tasks=["mmlu", "hellaswag", "arc_challenge", "winogrande"],
      num_fewshot=5,
      batch_size=8,
  )
  ```
- **Used For**: Evaluation pipeline reference (h-m2/h-m3 context); confirms task names

### C. Code Analysis (Serena)

Serena analysis not performed — code from EleutherAI/pythia `utils/mmap_dataset.py` was sufficiently clear from Exa results. The `MMapIndexedDataset` is a standard numpy memory-mapped array wrapper with transparent document indexing.

### D. Previous Hypothesis Context

Previous Context: None — h-e1 is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (index maps) | GitHub (Exa) | EleutherAI/pythia README, `pythia_deduped_pile_idxmaps` |
| Dataset (domain labels) | HuggingFace (Exa) | EleutherAI/pile `meta.pile_set_name` |
| 22 domain taxonomy | HuggingFace (Exa) | EleutherAI/pile dataset card |
| MMapIndexedDataset code | GitHub (Exa) | EleutherAI/pythia `utils/mmap_dataset.py` |
| Batch size (2M tokens/step) | GitHub (Exa) | EleutherAI/pythia-6.9b model card |
| 154 checkpoint enumeration | GitHub (Exa) + Paper | Biderman et al. 2023, EleutherAI/pythia README |
| Sequence length (2049) | GitHub (Exa) | EleutherAI/pythia README, mmap_dataset.py |
| Core mechanism pseudo-code | GitHub (Exa) | Derived from `mmap_dataset.py` + `batch_viewer.py` |
| Evaluation metrics (std, spearman) | Phase 2B | 02b_verification_plan.md §2.2 h-e1 success criteria |
| Benchmark eval API | GitHub (Exa) | EleutherAI/lm-evaluation-harness docs/python-api.md |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-20

### Workflow History for This Hypothesis
- 2026-08-20: h-e1 set to IN_PROGRESS (Phase 2C started)
- 2026-08-20: experiment_design.status = COMPLETED (Phase 2C finished)

---

*MCP Tools Used: Archon (Knowledge + Code — 5 queries, 0 relevant results), Exa GitHub (3 searches, 4 relevant repositories), Serena (skipped — code sufficiently clear)*
*All specifications grounded in official EleutherAI repositories*
*Next Phase: Phase 3 - Implementation Planning*
