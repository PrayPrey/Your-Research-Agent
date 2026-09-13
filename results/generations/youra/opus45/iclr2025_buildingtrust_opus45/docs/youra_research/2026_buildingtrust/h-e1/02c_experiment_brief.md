# Experiment Design: H-E1

**Date:** 2026-03-24
**Author:** Anonymous
**Hypothesis Statement:** Instruction-tuned LLMs exhibit significantly lower AUROC for margin-based correctness prediction compared to their base model counterparts across Qwen, Llama, and Mistral families.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (No prerequisites for H-E1)
**Gate Status:** MUST_WORK - Pending validation

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
MUST_WORK gate - If H-E1 fails, the entire hypothesis chain collapses. Core claim of RLHF-induced discriminative degradation would be invalidated.

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous results to incorporate.

### Previous Hypothesis Results (if applicable)
*None - H-E1 is the foundation hypothesis with no prerequisites*

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "LLM calibration AUROC confidence"**
- No direct matches for LLM confidence calibration or AUROC discriminative analysis
- Related findings: Consistency models, 4-bit quantization papers
- **Insight:** LLM calibration with AUROC discriminative metrics is a novel research area with limited prior implementations in Archon KB

**Query 2: "RLHF instruction tuning calibration"**
- Result: PEFT/LoRA adapter documentation (HuggingFace)
- Result: LyCORIS fine-tuning methods
- **Insight:** Fine-tuning methods documented, but no specific calibration-focused RLHF studies found

**Query 3: "MMLU evaluation benchmark LLM"**
- No direct MMLU evaluation code found in Archon KB
- **Insight:** Will need to rely on Exa/GitHub for MMLU evaluation implementations

**Cross-Pipeline Learning (Serena Memories):**

1. **buildingtrust_alignment_calibration_2026** (CRITICAL - Same Research Topic):
   - Prior successful H-E1: Pre-alignment margin predicts argmax flip with AUROC=0.867–0.909
   - Model pair used: allenai/tulu-2-7b → allenai/tulu-2-dpo-7b (CONFIRMED available)
   - Secondary pair: EleutherAI/pythia-6.9b → dvruette/oasst-pythia-6.9b-4000-steps (SFT)
   - Cache format: .npy files reusable across hypothesis chain
   - **Lesson:** DPO amplifies HIGH-margin items (monotone quintile trend), opposite of theoretical prediction

2. **failure_h-e1_entropy_residualization** (Different Pipeline, Similar H-E1):
   - Failed due to confound models explaining 90-100% of variance
   - **Lesson:** Pre-check confound explanatory power; R² near 1.0 is a red flag

3. **failure_h-e1_api_corpus_comparison** (Different Pipeline):
   - Cohen's d = 0.0161 (threshold was >= 0.3)
   - **Lesson:** Do not assume instruction-following datasets are inherently more "deliberative"

### Archon Code Examples

**Query 1: "sklearn AUROC binary classification"**
- No direct sklearn AUROC examples found
- Found: DreamBooth training examples, CLIP training examples

**Query 2: "transformers logits extraction LLM"**
- Result 1: AutoModelForCausalLM with quantization (optimum-quanto)
  ```python
  from transformers import AutoModelForCausalLM
  model = AutoModelForCausalLM.from_pretrained('meta-llama/Meta-Llama-3-8B')
  ```
- Result 2: CLIP logits extraction with softmax
  ```python
  outputs = model(**inputs)
  logits_per_image = outputs.logits_per_image
  probs = logits_per_image.softmax(dim=1)
  ```
- Result 3: T5 question answering with start/end logits
  ```python
  outputs = model(**inputs)
  answer_start_index = outputs.start_logits.argmax()
  ```
- **Pattern:** Use `model(**inputs)` then access `outputs.logits` for LLM logit extraction

### Exa GitHub Implementations

**Query 1: "LLM calibration AUROC confidence margin MMLU evaluation PyTorch"**

**Repository 1**: [ledengary/CCPS](https://github.com/ledengary/CCPS) - CCPS (Calibrating LLM Confidence by Probing Perturbed Representation Stability)
- **URL**: https://github.com/ledengary/CCPS
- **Paper**: arxiv.org/html/2505.21772v1
- **Relevance**: DIRECTLY relevant - Tests calibration + AUROC on MMLU with Llama/Qwen/Mistral families
- **Key Results**:
  - Reduces ECE by ~55%, Brier score by 21%
  - Increases AUROC by 6 percentage points
  - Tested on LLMs from 8B to 32B parameters (Llama, Qwen, Mistral)
- **Dataset**: MMLU + MMLU-Pro (multiple-choice and open-ended formats)
- **Metrics Implemented**: ECE, Brier score, ACC, AUCPR, AUROC

**Repository 2**: [ml-stat-Sustech/Disagreement-Aware-Calibration](https://github.com/ml-stat-Sustech/Disagreement-Aware-Calibration) (NeurIPS 2025)
- **URL**: https://github.com/ml-stat-Sustech/Disagreement-Aware-Calibration
- **Relevance**: Pre-trained vs Instruct model comparison for calibration (DIRECTLY matches H-E1)
- **Architecture**: Uses vLLM for inference, scikit-learn for metrics
- **Key Code Structure**:
  ```
  ├── calibration/pipeline.py  # Temperature scaling, ECE metrics
  ├── generation/pipeline.py   # vLLM inference, logits extraction
  ├── common/metrics.py        # Calibration metrics
  └── common/modeling.py       # Model loading
  ```
- **Training Config**:
  - Models: Qwen/Qwen2.5-7B (base) vs Qwen/Qwen2.5-7B-Instruct
  - Dataset: MMLU validation split
  - Temperature epochs: 400, batch_size: 256, lr: 0.1
- **Dependencies**: vllm, torch, datasets, netcal, scikit-learn

**Repository 3**: [appier-research/llm-calibration](https://github.com/appier-research/llm-calibration)
- **URL**: https://github.com/appier-research/llm-calibration
- **Paper**: "On Calibration of Large Language Models: From Response To Capability"
- **Relevance**: Capability vs Response calibration distinction
- **Datasets Supported**: MMLU, GPQA, TriviaQA, GSM8K, MATH-500
- **Confidence Methods**: Verbalized confidence, P(True) logprob extraction

**Repository 4**: [TIGER-AI-Lab/MMLU-Pro](https://github.com/TIGER-AI-Lab/MMLU-Pro)
- **URL**: https://github.com/TIGER-AI-Lab/MMLU-Pro
- **Relevance**: Standard MMLU evaluation code, NeurIPS 2024 paper
- **Key Features**: 10 answer choices (vs 4 in MMLU), 12,000+ questions
- **Evaluation Scripts**: `scripts/examples/eval_llama_2_7b.sh`

**Query 2: "HuggingFace transformers logits extraction multiple choice MMLU benchmark"**

**HuggingFace Datasets**: [cais/mmlu](https://huggingface.co/datasets/cais/mmlu)
- **Size**: 231,400 rows, 104 MB
- **Splits**: test, validation, dev, auxiliary_train
- **Structure**: question, choices (A/B/C/D), answer
- **Loading Code**:
  ```python
  from datasets import load_dataset
  dataset = load_dataset("cais/mmlu", "all")
  ```

**HuggingFace Tutorial**: [Multiple Choice](https://huggingface.co/docs/transformers/en/tasks/multiple_choice)
- **Model Class**: `AutoModelForMultipleChoice`
- **Key Code**:
  ```python
  from transformers import AutoModelForMultipleChoice
  outputs = model(**inputs, labels=labels)
  logits = outputs.logits
  predicted_class = logits.argmax()
  ```

**Serena Analysis Needed**: true (Disagreement-Aware-Calibration repo has complex pipeline structure)

### Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Implementation | Rationale |
|----------|---------------|-----------|
| **1 (HIGHEST)** | ml-stat-Sustech/Disagreement-Aware-Calibration | Directly compares base vs instruct models, uses same model families (Qwen), has calibration metrics |
| **2** | ledengary/CCPS | Has AUROC metrics, tests Llama/Qwen/Mistral on MMLU |
| **3** | Custom implementation using HuggingFace | If repos don't fit exact needs |

**Recommended Implementation Path:**
- Primary: Adapt ml-stat-Sustech/Disagreement-Aware-Calibration pipeline for AUROC comparison
- Fallback: Custom implementation using HuggingFace transformers + sklearn AUROC
- Justification: Disagreement-Aware-Calibration already has base vs instruct comparison infrastructure and uses same model families (Qwen2.5-7B base vs Instruct)

### Code Analysis (Serena MCP)

**Analysis Status:** Limited (external repositories not in local codebase)

**Based on Exa Search Results + Serena Cross-Pipeline Memory:**

#### Code Structure (from ml-stat-Sustech/Disagreement-Aware-Calibration)

**Directory Structure:**
```
├── calibration/
│   └── pipeline.py      # Temperature scaling, ECE computation
├── generation/
│   └── pipeline.py      # vLLM inference, logits extraction
├── common/
│   ├── data.py          # Data utilities
│   ├── datasets.py      # Dataset loading
│   ├── metrics.py       # Calibration metrics (ECE, AUROC)
│   ├── modeling.py      # Model loading utilities
│   └── utils.py         # General utilities
└── main.py              # Entry point, CLI
```

**Key Components:**
- `generation/pipeline.py`: Runs vLLM inference, extracts raw logits for MCQ options
- `calibration/pipeline.py`: Temperature scaling optimization, DACA calibration
- `common/metrics.py`: ECE computation using netcal library

#### Core Mechanism Pattern (Synthesized)

```python
# AUROC Discriminative Degradation Analysis
# Based on: Disagreement-Aware-Calibration + CCPS patterns

import torch
from sklearn.metrics import roc_auc_score
from transformers import AutoModelForCausalLM, AutoTokenizer

class MarginAUROCAnalyzer:
    """
    Compute AUROC for margin-based correctness prediction.
    Compares base vs instruct models to measure discriminative degradation.
    """

    def __init__(self, model_name: str, device: str = "cuda"):
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map=device
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def extract_logits(self, question: str, choices: list[str]) -> torch.Tensor:
        """
        Extract logits for each answer choice (A, B, C, D).
        Returns: (4,) tensor of logits for each choice.
        """
        # Format MCQ prompt
        prompt = f"{question}\n" + "\n".join(
            f"{chr(65+i)}. {c}" for i, c in enumerate(choices)
        )
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            # Get logits at last position for A/B/C/D tokens
            last_logits = outputs.logits[0, -1, :]
            choice_token_ids = [
                self.tokenizer.encode(f" {chr(65+i)}", add_special_tokens=False)[-1]
                for i in range(4)
            ]
            return last_logits[choice_token_ids]

    def compute_margin(self, logits: torch.Tensor) -> float:
        """
        Compute confidence margin = logit_top1 - logit_top2
        """
        sorted_logits, _ = torch.sort(logits, descending=True)
        return (sorted_logits[0] - sorted_logits[1]).item()

    def compute_auroc(
        self,
        margins: list[float],
        correctness: list[int]
    ) -> tuple[float, float, float]:
        """
        Compute AUROC for margin → correctness prediction.
        Returns: (auroc, ci_lower, ci_upper) with bootstrap 95% CI
        """
        auroc = roc_auc_score(correctness, margins)

        # Bootstrap 95% CI
        n_bootstrap = 1000
        bootstrap_aurocs = []
        n = len(margins)
        for _ in range(n_bootstrap):
            indices = np.random.choice(n, n, replace=True)
            boot_auroc = roc_auc_score(
                [correctness[i] for i in indices],
                [margins[i] for i in indices]
            )
            bootstrap_aurocs.append(boot_auroc)

        ci_lower = np.percentile(bootstrap_aurocs, 2.5)
        ci_upper = np.percentile(bootstrap_aurocs, 97.5)

        return auroc, ci_lower, ci_upper

# Integration: Load MMLU, run on base vs instruct pairs
# Expected output: AUROC_base, AUROC_instruct per family
```

#### Key Patterns Identified

1. **Logit Extraction**: Use `outputs.logits[0, -1, :]` at last token position
2. **Token IDs**: Map A/B/C/D to tokenizer-specific IDs
3. **Margin Computation**: `sorted_logits[0] - sorted_logits[1]`
4. **AUROC**: sklearn's `roc_auc_score(correctness, margins)`
5. **Bootstrap CI**: 1000 iterations with replacement

#### Cross-Pipeline Lessons (from Serena Memories)

From `buildingtrust_alignment_calibration_2026`:
- Model pairs that WORK: `allenai/tulu-2-7b` → `allenai/tulu-2-dpo-7b`
- Cache format: `.npy` files reusable across hypothesis chain
- DPO amplifies HIGH-margin items (monotone quintile trend)

From `failure_h-e1_entropy_residualization`:
- Pre-check if confound models explain >90% variance
- R² near 1.0 indicates hypothesis is likely false

---

## Experiment Specification

### Dataset

**Dataset**: MMLU (Massive Multitask Language Understanding)
**Type**: standard
**Source**: HuggingFace datasets

**Statistics**:
- Total samples: ~14,000 (test set)
- Splits: test (primary), validation, dev, auxiliary_train
- Tasks: 57 subjects spanning STEM, humanities, social sciences
- Format: Multiple choice (4 options: A, B, C, D)

**Preprocessing**:
- No image preprocessing (text-only)
- Prompt format: "Question: {question}\nA. {choice_a}\nB. {choice_b}\nC. {choice_c}\nD. {choice_d}\nAnswer:"
- Temperature: 0 (greedy decoding)

**Augmentation**: None (evaluation-only experiment)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `cais/mmlu`
- Code:
  ```python
  from datasets import load_dataset

  # Load all MMLU subjects
  mmlu = load_dataset("cais/mmlu", "all")
  test_data = mmlu["test"]

  # Each sample has: question, subject, choices, answer
  # answer is index 0-3 mapping to A-D
  ```

### Models

#### Baseline Model

**Architecture**: Causal LLM (base models without instruction tuning)

**Model Pairs for Comparison**:

| Family | Base Model | Instruct Model | HuggingFace ID (Base) | HuggingFace ID (Instruct) |
|--------|-----------|----------------|----------------------|---------------------------|
| Qwen | Qwen2.5-7B | Qwen2.5-7B-Instruct | `Qwen/Qwen2.5-7B` | `Qwen/Qwen2.5-7B-Instruct` |
| Llama | Llama-2-7B | Llama-2-7B-Chat | `meta-llama/Llama-2-7b-hf` | `meta-llama/Llama-2-7b-chat-hf` |
| Mistral | Mistral-7B-v0.1 | Mistral-7B-Instruct-v0.2 | `mistralai/Mistral-7B-v0.1` | `mistralai/Mistral-7B-Instruct-v0.2` |

**Configuration**:
- Parameters: ~7B each
- Precision: float16 (for GPU efficiency)
- Device: CUDA (single GPU)

**Modifications for Hypothesis**: None - using models as-is to compare base vs instruct effect

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: See table above
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  import torch

  def load_model_pair(family: str):
      model_ids = {
          "qwen": ("Qwen/Qwen2.5-7B", "Qwen/Qwen2.5-7B-Instruct"),
          "llama": ("meta-llama/Llama-2-7b-hf", "meta-llama/Llama-2-7b-chat-hf"),
          "mistral": ("mistralai/Mistral-7B-v0.1", "mistralai/Mistral-7B-Instruct-v0.2"),
      }
      base_id, instruct_id = model_ids[family]

      base_model = AutoModelForCausalLM.from_pretrained(
          base_id,
          torch_dtype=torch.float16,
          device_map="auto"
      )
      base_tokenizer = AutoTokenizer.from_pretrained(base_id)

      instruct_model = AutoModelForCausalLM.from_pretrained(
          instruct_id,
          torch_dtype=torch.float16,
          device_map="auto"
      )
      instruct_tokenizer = AutoTokenizer.from_pretrained(instruct_id)

      return (base_model, base_tokenizer), (instruct_model, instruct_tokenizer)
  ```

#### Proposed Model

**Architecture:** Same base/instruct model pairs - we COMPARE base vs instruct, not train new models

**Comparison Design:**
- Base model = "Baseline" (pre-RLHF confidence signal)
- Instruct model = "Proposed effect" (post-RLHF degraded confidence signal)
- We measure AUROC difference, not train models

**Core Mechanism Implementation:**

```python
# Core Mechanism: AUROC Discriminative Degradation Analysis
# Based on: ml-stat-Sustech/Disagreement-Aware-Calibration + CCPS
# Hypothesis: AUROC(margin → correctness) degrades after RLHF

import torch
import numpy as np
from sklearn.metrics import roc_auc_score
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

def extract_choice_logits(model, tokenizer, question: str, choices: list) -> torch.Tensor:
    """Extract logits for A/B/C/D answer choices."""
    prompt = f"Question: {question}\n" + "\n".join(
        f"{chr(65+i)}. {c}" for i, c in enumerate(choices)
    ) + "\nAnswer:"

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model(**inputs)
        last_logits = outputs.logits[0, -1, :]

    # Get token IDs for A, B, C, D
    choice_ids = [tokenizer.encode(f" {chr(65+i)}")[-1] for i in range(4)]
    return last_logits[choice_ids]

def compute_margin(logits: torch.Tensor) -> float:
    """Compute confidence margin = logit_top1 - logit_top2."""
    sorted_logits, _ = torch.sort(logits, descending=True)
    return (sorted_logits[0] - sorted_logits[1]).item()

def run_auroc_comparison(base_model, instruct_model, tokenizer, dataset):
    """Compare AUROC between base and instruct models."""
    base_margins, instruct_margins, correctness = [], [], []

    for sample in dataset:
        # Extract logits and compute margins
        base_logits = extract_choice_logits(base_model, tokenizer, sample["question"], sample["choices"])
        inst_logits = extract_choice_logits(instruct_model, tokenizer, sample["question"], sample["choices"])

        base_margins.append(compute_margin(base_logits))
        instruct_margins.append(compute_margin(inst_logits))
        correctness.append(int(base_logits.argmax() == sample["answer"]))

    # Compute AUROC for each model
    auroc_base = roc_auc_score(correctness, base_margins)
    auroc_instruct = roc_auc_score(correctness, instruct_margins)

    return auroc_base, auroc_instruct
```

### Training Protocol

**Type:** Inference-only (no training required)

This is an **evaluation experiment**, not a training experiment:
- **No Optimizer**: N/A (inference only)
- **No Learning Rate**: N/A
- **No Epochs**: N/A
- **Batch Size**: 1 (sequential inference for logit extraction)
- **Seeds**: 1 (fixed, greedy decoding with T=0)
- **Decoding Temperature**: 0 (greedy, deterministic)

**Rationale**: H-E1 tests whether RLHF-induced discriminative degradation EXISTS by comparing pre-trained base models with their instruction-tuned variants. No training is performed.

**Source**: CCPS (arxiv.org/html/2505.21772v1), Disagreement-Aware-Calibration (NeurIPS 2025)

### Evaluation

**Primary Metrics:**
- **AUROC(margin → correctness)**: Area Under ROC Curve for binary classification (correct/incorrect) using margin as predictor
  - Definition: `sklearn.metrics.roc_auc_score(correctness_labels, margin_values)`
  - Higher AUROC = better discriminative ability

**Secondary Metrics (informational):**
- **Mean margin | correct**: E[margin | prediction is correct]
- **Mean margin | incorrect**: E[margin | prediction is incorrect]
- **I² statistic**: Heterogeneity across model families (for meta-analysis)

**Success Criteria (PoC):**
- AUROC_base > AUROC_instruct for all 3 model families (direction check)
- 95% CI of AUROC difference should not overlap zero

**Expected Baseline Performance (from research):**
- CCPS paper: AUROC improvement of ~6 percentage points over baselines on MMLU
- Disagreement-Aware-Calibration: ECE reduction demonstrated on Qwen base vs instruct
- **Source**: CCPS (arxiv.org/html/2505.21772v1)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification (correct/incorrect prediction)
- Library: sklearn.metrics
- Code:
  ```python
  from sklearn.metrics import roc_auc_score
  import numpy as np

  # Compute AUROC
  auroc = roc_auc_score(correctness_labels, margins)

  # Bootstrap 95% CI
  n_bootstrap = 1000
  bootstrap_aurocs = []
  for _ in range(n_bootstrap):
      indices = np.random.choice(len(margins), len(margins), replace=True)
      boot_auroc = roc_auc_score(
          correctness_labels[indices],
          margins[indices]
      )
      bootstrap_aurocs.append(boot_auroc)

  ci_lower = np.percentile(bootstrap_aurocs, 2.5)
  ci_upper = np.percentile(bootstrap_aurocs, 97.5)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: AUROC bar chart comparing base vs instruct for each model family (Qwen, Llama, Mistral) with 95% CI error bars

#### Additional Figures (LLM Autonomous)

Based on hypothesis type and evaluation metrics:

1. **AUROC Comparison Bar Chart**: 3 grouped bars (one per family), each with base vs instruct comparison
2. **Margin Distribution Plot**: KDE plots showing margin distributions for correct vs incorrect predictions, comparing base and instruct
3. **Forest Plot**: Meta-analysis style plot showing AUROC difference (instruct - base) with CI for each family and pooled estimate
4. **Reliability Diagram** (optional): Calibration curves comparing base vs instruct models

**Output Location**: `h-e1/figures/`

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: LLM Calibration Research
- **Type**: Knowledge base search
- **Query Used**: "LLM calibration AUROC confidence"
- **Relevance**: Limited direct results for LLM calibration; most results focused on diffusion models
- **Key Insights**: LLM calibration with AUROC discriminative metrics is a novel research area
- **Used For**: Confirming novelty of approach

**Source A.2**: HuggingFace Transformers Code
- **Type**: Code examples
- **Query Used**: "transformers logits extraction LLM"
- **Key Code**:
  ```python
  from transformers import AutoModelForCausalLM
  outputs = model(**inputs)
  logits = outputs.logits
  ```
- **Used For**: Model loading and logit extraction pattern

### B. GitHub Implementations (Exa)

**Repository B.1**: [ledengary/CCPS](https://github.com/ledengary/CCPS)
- **URL**: https://github.com/ledengary/CCPS
- **Paper**: arxiv.org/html/2505.21772v1
- **Query Used**: "LLM calibration AUROC confidence margin MMLU evaluation PyTorch"
- **Relevance**: DIRECTLY tests calibration + AUROC on MMLU with Llama/Qwen/Mistral
- **Configuration Extracted**: ECE, Brier score, AUROC metrics on 8B-32B models
- **Their Results**: AUROC improvement of ~6 percentage points over baselines
- **Used For**: Evaluation metrics design, expected baseline performance

**Repository B.2**: [ml-stat-Sustech/Disagreement-Aware-Calibration](https://github.com/ml-stat-Sustech/Disagreement-Aware-Calibration)
- **URL**: https://github.com/ml-stat-Sustech/Disagreement-Aware-Calibration
- **Paper**: NeurIPS 2025
- **Query Used**: "LLM calibration AUROC confidence margin MMLU evaluation PyTorch"
- **Relevance**: Compares base vs instruct models (exactly matches H-E1)
- **Key Code** (annotated):
  ```python
  # From common/metrics.py - ECE computation
  # From generation/pipeline.py - vLLM inference, logits extraction
  # From calibration/pipeline.py - Temperature scaling
  ```
- **Configuration Extracted**:
  - Models: Qwen/Qwen2.5-7B vs Qwen2.5-7B-Instruct
  - Temperature epochs: 400, batch_size: 256, lr: 0.1
- **Used For**: Primary implementation reference, code structure

**Repository B.3**: [TIGER-AI-Lab/MMLU-Pro](https://github.com/TIGER-AI-Lab/MMLU-Pro)
- **URL**: https://github.com/TIGER-AI-Lab/MMLU-Pro
- **Query Used**: "HuggingFace transformers logits extraction multiple choice MMLU benchmark"
- **Relevance**: Standard MMLU evaluation code
- **Used For**: MMLU dataset structure, evaluation scripts reference

**Repository B.4**: [appier-research/llm-calibration](https://github.com/appier-research/llm-calibration)
- **URL**: https://github.com/appier-research/llm-calibration
- **Paper**: "On Calibration of Large Language Models: From Response To Capability"
- **Relevance**: Capability vs Response calibration distinction
- **Used For**: Conceptual framework reference

### C. Code Analysis (Serena)

**Serena Analysis**: Limited - external repositories not in local codebase

**Analysis Method**: Based on Exa search results + Serena cross-pipeline memories

**Cross-Pipeline Memories Read**:
1. `global/phase45/buildingtrust_alignment_calibration_2026`
   - Findings: AUROC=0.867–0.909 for margin-based prediction
   - Model pair: allenai/tulu-2-7b → allenai/tulu-2-dpo-7b
   - **Used For**: Validated approach from similar pipeline

2. `global/phase45/failure_h-e1_entropy_residualization`
   - Findings: Confound models explained 90-100% variance
   - **Used For**: Risk awareness - pre-check confound power

3. `global/phase45/failure_h-e1_api_corpus_comparison`
   - Findings: Cohen's d = 0.0161 (far below threshold)
   - **Used For**: Different hypothesis, but cautionary example

### D. Previous Hypothesis Context

**Previous Context**: None - H-E1 is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (MMLU) | HuggingFace/Exa | cais/mmlu, B.3 |
| Model pairs | Exa GitHub | B.2 (Disagreement-Aware-Calibration) |
| AUROC metrics | Exa GitHub | B.1 (CCPS), B.2 |
| Logit extraction pattern | Archon Code | A.2 |
| Margin computation | Exa + Serena | B.1, B.2, Serena memories |
| Bootstrap CI | sklearn standard | B.1, B.2 |
| Expected baseline | Exa GitHub | B.1 (CCPS paper) |
| Model family selection | Phase 2B | 02b_verification_plan.md |
| Success criteria | Phase 2B | 02b_verification_plan.md |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-24

### Workflow History for This Hypothesis
- Phase 2B: Created verification plan (2026-03-24)
- Phase 2C: Experiment design started (2026-03-24)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
