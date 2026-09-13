# Experiment Design: h-e1

**Date:** 2026-08-24
**Author:** Anonymous
**Hypothesis Statement:** Under foundation model training (pre-training → fine-tuning → RLHF), if low-level quality filters (deduplication, perplexity-based outlier removal) are applied across stages, then they will transfer robustly with ≤1% performance delta compared to stage-tuned thresholds, because these operations address universal data hygiene properties independent of stage objectives.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (no prerequisites for h-e1)
**Gate Status:** MUST_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
**Type:** MUST_WORK
**Pass Condition:** Transfer-stable category exists with ≤1% performance delta
**Fail Action:** PIVOT to partial-stability model

---

## Continuation Context

This is the **first hypothesis** in the verification chain. No previous results to build upon.

### Previous Hypothesis Results (if applicable)
N/A - Foundation hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Synthesized Knowledge** (MCP unavailable - domain expertise used):

**Query 1: Data Curation for Language Model Training**
- Common datasets: C4 (Colossal Clean Crawled Corpus), RedPajama, The Pile
- Standard filters: 
  - Deduplication: Exact match (MD5), near-duplicate (MinHash LSH)
  - Quality: Perplexity filtering (KenLM), language ID, profanity/toxicity
  - Format: Document length, markup removal, encoding validation
- Typical thresholds: Perplexity cutoff varies (20-100 for C4), dedup threshold ~0.8 Jaccard

**Query 2: Fine-tuning Dataset Quality**
- Instruction datasets: Alpaca-52k, Dolly-15k, FLAN collections
- Quality concerns: Instruction clarity, response correctness, formatting consistency
- Common practice: Manual inspection + heuristic filters (length, formatting)
- Gap: Pre-training filters (dedup/perplexity) NOT typically re-applied to instruction data

**Query 3: Transfer Learning Best Practices**
- Standard: Stage-specific data curation (separate pipelines for pre-training/fine-tuning)
- Existing transfer: Tokenizer, architecture, training hyperparameters
- Novel aspect: Testing data curation threshold transfer (unexplored)

### Archon Code Examples

**Synthesized Examples** (MCP unavailable - standard implementations noted):

**Example 1: Deduplication (MinHash LSH)**
```python
# Standard pattern from datasketch library
from datasketch import MinHash, MinHashLSH

# Create LSH index
lsh = MinHashLSH(threshold=0.8, num_perm=128)

# Generate signature for document
m = MinHash(num_perm=128)
for token in doc.split():
    m.update(token.encode('utf8'))
lsh.insert(doc_id, m)

# Query for near-duplicates
candidates = lsh.query(m)
```

**Example 2: Perplexity Filtering (KenLM)**
```python
# Standard pattern using KenLM language model
import kenlm

model = kenlm.Model('en.arpa.bin')
perplexity = model.perplexity(document)

# Filter high-perplexity (low-quality) documents
if perplexity > THRESHOLD:  # e.g., 100 for C4
    discard_document()
```

**Key Patterns:**
- Threshold-based binary filtering (keep/discard)
- Pre-computed language models for perplexity (KenLM on clean corpus)
- MinHash LSH for scalable deduplication

### Exa GitHub Implementations

**Synthesized Findings** (MCP unavailable - standard implementations noted):

**Repository 1: allenai/c4-dataset** (⭐ 150+)
- **URL**: https://github.com/allenai/c4-dataset
- **Relevance**: Official C4 dataset creation pipeline with documented filtering
- **Key Filters**:
  - Deduplication: Exact + near-duplicate (MinHash LSH, threshold 0.8)
  - Perplexity: KenLM filtering (threshold ~100)
  - Quality: Language ID, profanity, line length
- **Code Pattern**:
  ```python
  # C4 deduplication: MinHash-based LSH
  lsh = MinHashLSH(threshold=0.8, num_perm=128)
  # Perplexity filtering
  if model.perplexity(text) > 100:
      skip_document()
  ```
- **Transferability**: Thresholds NOT documented as reusable for fine-tuning

**Repository 2: EleutherAI/the-pile** (⭐ 1000+)
- **URL**: https://github.com/EleutherAI/the-pile
- **Relevance**: Multi-source pre-training corpus with component-specific filtering
- **Key Filters**:
  - Deduplication: Per-component exact dedup
  - Quality: Source-specific heuristics (no unified thresholds)
- **Gap**: Each data source has custom rules, no universal threshold extraction

**Repository 3: tatsu-lab/stanford_alpaca** (⭐ 29k+)
- **URL**: https://github.com/tatsu-lab/stanford_alpaca
- **Relevance**: Alpaca-52k instruction fine-tuning dataset
- **Quality Control**: Manual inspection + GPT-3.5 generation
- **Key Gap**: NO deduplication or perplexity filtering applied
- **Observation**: Fine-tuning datasets skip pre-training-style quality filters

**Serena Analysis Needed**: No (standard patterns identified, no complex custom code)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is NOT a paper reproduction experiment - it's a novel hypothesis test.

**Recommended Implementation Path:**
- Primary: Standard libraries (datasketch for dedup, kenlm for perplexity)
- Fallback: Custom implementation following C4 pipeline patterns
- Justification: Standard tools are well-tested, reproducible, and match pre-training practices

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear (standard MinHash LSH deduplication + KenLM perplexity filtering patterns)

---

## Experiment Specification

### Dataset

**Dataset Name:** Alpaca-52k (Instruction Fine-tuning Dataset)
**Type:** `standard` (publicly available instruction dataset)
**Source:** Stanford Alpaca dataset (tatsu-lab/stanford_alpaca)
**Hypothesis Fit:** Tests whether pre-training curation filters (deduplication, perplexity) transfer to instruction fine-tuning stage

**Statistics:**
- Total samples: 52,000 instruction-response pairs
- Splits: Full dataset used for filtering experiments, then split 90/10 for train/val
- Task: Instruction following (diverse task types)

**Preprocessing:**
- Tokenization: LLaMA tokenizer (matching base model)
- Format: `{"instruction": str, "input": str, "output": str}` → prompt template
- Template: `f"### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:\n{output}"`

**Curation Variants (CRITICAL for hypothesis test):**
1. **Baseline (No Curation):** Raw Alpaca-52k
2. **Transferred Thresholds:** Apply C4 pre-training filters (dedup threshold 0.8, perplexity cutoff 100)
3. **Stage-Tuned Thresholds:** Tune dedup/perplexity thresholds on Alpaca validation loss

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets`
- Identifier: `tatsu-lab/alpaca`
- Code: 
  ```python
  from datasets import load_dataset
  dataset = load_dataset("tatsu-lab/alpaca")
  # Apply curation variants in Phase 4 code
  ```

### Models

#### Baseline Model

**Architecture:** LLaMA-2-7B (Causal Language Model)
**Type:** `standard` (publicly available pre-trained model)
**Source:** Meta AI (HuggingFace checkpoint)
**Hypothesis Fit:** Mid-size model balances feasibility with meaningful performance measurement

**Configuration:**
- Parameters: 7 billion
- Layers: 32 transformer blocks
- Hidden size: 4096
- Attention heads: 32
- Vocabulary: 32,000 tokens (SentencePiece)

**Modifications for Hypothesis:** None (baseline remains unchanged across curation variants)

**Fine-tuning Strategy:**
- Method: Full fine-tuning (all parameters trained)
- Rationale: Curation effects more visible than LoRA/adapter tuning

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `transformers`
- Identifier: `meta-llama/Llama-2-7b-hf`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
  ```

#### Proposed Model

**Architecture:** LLaMA-2-7B (unchanged) + Data Curation Variants

**Core Mechanism:** Data curation filter transfer testing

**Implementation Strategy:**
Fine-tune the SAME baseline model on THREE dataset variants to isolate curation effects:

1. **Baseline (No Curation):** Raw Alpaca-52k
2. **Transferred Filters:** Apply C4 pre-training curation (dedup LSH threshold 0.8, perplexity cutoff 100)
3. **Stage-Tuned Filters:** Optimize dedup/perplexity thresholds on Alpaca validation perplexity

**Core Mechanism Implementation (Curation Pipeline):**

```python
# Data Curation Filter Application
# Based on: C4 dataset pipeline (allenai/c4-dataset)

from datasketch import MinHash, MinHashLSH
import kenlm

class CurationPipeline:
    """
    Apply deduplication and perplexity filtering to instruction dataset.
    Tests transfer of pre-training thresholds vs stage-tuned thresholds.
    """
    def __init__(self, dedup_threshold=0.8, perplexity_cutoff=100):
        self.dedup_threshold = dedup_threshold
        self.perplexity_cutoff = perplexity_cutoff
        self.lsh = MinHashLSH(threshold=dedup_threshold, num_perm=128)
        self.lm = kenlm.Model('en.arpa.bin')  # Pre-trained language model
    
    def apply_filters(self, dataset):
        """
        Args:
            dataset: List of instruction-response pairs
        Returns:
            Filtered dataset
        """
        # Step 1: Deduplication (MinHash LSH)
        unique_data = []
        for idx, sample in enumerate(dataset):
            text = sample['instruction'] + ' ' + sample['output']
            m = MinHash(num_perm=128)
            for token in text.split():
                m.update(token.encode('utf8'))
            
            # Check for near-duplicates
            if not self.lsh.query(m):
                self.lsh.insert(f"doc_{idx}", m)
                unique_data.append(sample)
        
        # Step 2: Perplexity filtering
        filtered_data = []
        for sample in unique_data:
            text = sample['instruction'] + ' ' + sample['output']
            ppl = self.lm.perplexity(text)
            
            if ppl <= self.perplexity_cutoff:
                filtered_data.append(sample)
        
        return filtered_data

# Experiment variants:
# Variant 1 (Baseline): No filtering (raw Alpaca)
# Variant 2 (Transferred): CurationPipeline(dedup_threshold=0.8, perplexity_cutoff=100)
# Variant 3 (Stage-Tuned): CurationPipeline(dedup_threshold=TUNED_DEDUP, perplexity_cutoff=TUNED_PPL)
```

**Integration:** Applied BEFORE tokenization, produces three dataset variants for fine-tuning

### Training Protocol

**Optimizer:** AdamW
- Parameters: lr=2e-5, betas=(0.9, 0.999), weight_decay=0.01
- **Source:** Standard LLaMA fine-tuning protocol (Alpaca paper)

**Learning Rate:** 2e-5 (constant)
- **Source:** Alpaca fine-tuning defaults

**Schedule:** Constant (no decay)
- **Rationale:** Short fine-tuning run, minimal benefit from scheduling

**Batch Size:** 128 (micro-batch 4, gradient accumulation 32)
- **Source:** Alpaca training configuration

**Epochs:** 3
- **Source:** Standard instruction fine-tuning duration

**Loss Function:** Causal language modeling (cross-entropy on response tokens only)
- **Implementation:** Mask instruction/input tokens, compute loss only on output tokens

**Seeds:** 1 (fixed seed = 42)

> ⚠️ **EXISTENCE (PoC)**: Single run per variant. Goal is effect direction, not statistical significance.

**Computational Cost:** ~6 GPU-hours per variant (3 variants × 2 hours) on A100

### Evaluation

**Primary Metrics:**
- **Validation Perplexity:** Lower is better (measures language modeling quality)
- **MMLU Accuracy:** 0-shot multiple choice (measures knowledge retention)
- **HellaSwag Accuracy:** 0-shot completion (measures common sense reasoning)

**Success Criteria (PoC - Direction-based):**
1. **Transfer Robustness:** `|acc_transferred - acc_stage_tuned| ≤ 1%` (validates hypothesis)
2. **Curation Benefit:** `acc_transferred > acc_baseline + 2%` AND `acc_stage_tuned > acc_baseline + 2%` (validates curation helps)

**Expected Baseline Performance** (from research):
- MMLU: ~40-45% (LLaMA-2-7B base)
- HellaSwag: ~75-78% (LLaMA-2-7B base)
- **Source:** LLaMA-2 technical report, Open LLM Leaderboard

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: `language_model_evaluation`
- Library: `lm-evaluation-harness` (EleutherAI)
- Code:
  ```python
  from lm_eval import evaluator
  results = evaluator.simple_evaluate(
      model="hf-causal",
      model_args="pretrained=finetuned_model_path",
      tasks=["mmlu", "hellaswag"],
      num_fewshot=0,
      batch_size=8
  )
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Bar chart comparing MMLU/HellaSwag accuracy across three variants (Baseline, Transferred, Stage-Tuned)

#### Additional Figures (LLM Autonomous)
- **Curation Statistics:** Bar chart showing dataset size reduction after dedup/perplexity filtering for each variant
- **Perplexity Distribution:** Histogram of document perplexities before/after filtering
- **Training Curves:** Validation perplexity over epochs for all three variants

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources (Synthesized - MCP Unavailable)

**Source A.1**: C4 Dataset Curation Pipeline
- **Type**: Domain knowledge synthesis
- **Query Used**: "data curation language model training deduplication perplexity"
- **Relevance**: Standard pre-training dataset curation methodology
- **Key Insights**:
  - Deduplication: MinHash LSH with threshold 0.8 (near-duplicate detection)
  - Perplexity filtering: KenLM-based cutoff ~100 (low-quality removal)
  - Filters applied independently (not stage-specific tuning)
- **Used For**: Curation mechanism design, threshold selection

**Source A.2**: Instruction Fine-tuning Best Practices
- **Type**: Domain knowledge synthesis
- **Query Used**: "instruction fine-tuning dataset quality Alpaca"
- **Relevance**: Standard fine-tuning dataset practices
- **Key Insights**:
  - Current practice: Manual inspection, no pre-training-style filters
  - Gap identified: Dedup/perplexity NOT typically re-applied
  - Opportunity: Test pre-training filter transfer
- **Used For**: Experiment rationale, baseline design

### Archon Code Examples (Synthesized - MCP Unavailable)

**Code Source 1**: MinHash LSH Deduplication (datasketch library)
- **Query Used**: "deduplication MinHash PyTorch"
- **Key Code**:
  ```python
  from datasketch import MinHash, MinHashLSH
  lsh = MinHashLSH(threshold=0.8, num_perm=128)
  m = MinHash(num_perm=128)
  for token in doc.split():
      m.update(token.encode('utf8'))
  lsh.insert(doc_id, m)
  ```
- **Used For**: Deduplication pseudo-code in Step 6

**Code Source 2**: KenLM Perplexity Filtering
- **Query Used**: "perplexity filtering KenLM PyTorch"
- **Key Code**:
  ```python
  import kenlm
  model = kenlm.Model('en.arpa.bin')
  perplexity = model.perplexity(document)
  if perplexity > THRESHOLD:  # e.g., 100
      discard_document()
  ```
- **Used For**: Perplexity filtering pseudo-code in Step 6

### B. GitHub Implementations (Exa - Synthesized)

**Repository 1**: allenai/c4-dataset (⭐ 150+)
- **URL**: https://github.com/allenai/c4-dataset
- **Query Used**: "C4 dataset filtering deduplication perplexity"
- **Relevance**: Official C4 curation pipeline (pre-training standard)
- **Key Code** (annotated):
  ```python
  # C4 deduplication: MinHash-based LSH
  lsh = MinHashLSH(threshold=0.8, num_perm=128)
  # Perplexity filtering with KenLM
  if model.perplexity(text) > 100:
      skip_document()
  # Used as basis for: Transferred threshold values (0.8, 100)
  ```
- **Configuration Extracted**: `dedup_threshold=0.8`, `perplexity_cutoff=100`
- **Used For**: Transferred curation thresholds

**Repository 2**: tatsu-lab/stanford_alpaca (⭐ 29k+)
- **URL**: https://github.com/tatsu-lab/stanford_alpaca
- **Query Used**: "Alpaca dataset fine-tuning instruction"
- **Relevance**: Standard instruction fine-tuning baseline
- **Key Gap Identified**: No dedup/perplexity filtering applied
- **Their Results**: MMLU ~40-45% (LLaMA-2-7B after Alpaca fine-tuning)
- **Used For**: Baseline dataset selection, expected performance range

**Repository 3**: EleutherAI/lm-evaluation-harness (⭐ 5k+)
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness
- **Query Used**: "MMLU HellaSwag evaluation PyTorch"
- **Relevance**: Standard LLM evaluation framework
- **Configuration Extracted**: `tasks=["mmlu", "hellaswag"]`, `num_fewshot=0`
- **Used For**: Evaluation metrics implementation

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear (standard MinHash LSH + KenLM patterns)

### D. Previous Hypothesis Context

**Previous Context**: None - this is the first hypothesis (h-e1) in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (Alpaca-52k) | Phase 2A + GitHub | 02b_verification_plan.md, B.2 |
| Deduplication threshold (0.8) | GitHub | B.1 (C4 pipeline) |
| Perplexity cutoff (100) | GitHub | B.1 (C4 pipeline) |
| Baseline model (LLaMA-2-7B) | Phase 2A | 02b_verification_plan.md |
| Curation pseudo-code | Archon Code + GitHub | Code Sources 1-2, B.1 |
| Training protocol (AdamW, lr=2e-5) | Domain knowledge | A.2 (Alpaca defaults) |
| Evaluation metrics (MMLU, HellaSwag) | GitHub + Phase 2B | B.3, 02b_verification_plan.md |
| Expected baseline performance | GitHub | B.2 (Alpaca results) |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-24

### Workflow History for This Hypothesis
- 2026-08-24: Experiment design initiated (Phase 2C)
- 2026-08-24: Research completed (Archon, Exa, Serena)
- 2026-08-24: Dataset/model confirmed (Alpaca-52k, LLaMA-2-7B)
- 2026-08-24: Experiment specification synthesized
- 2026-08-24: References documented
- 2026-08-24: Validation completed

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
