# Logic Design: h-m2 Transfer Stability Categorization

**Generated:** 2026-08-24  
**Hypothesis:** h-m2 (MECHANISM - SHOULD_WORK)  
**Project Type:** Green-field (no base hypothesis, new implementation)

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New API design - no existing codebase to analyze  
**Analyzed Path:** N/A  
**Relevant Symbols:** None - new implementation

---

## Overview

This is a standard ML experiment pipeline: data curation → fine-tuning → evaluation → statistical analysis. No custom architectures required - uses off-the-shelf Hugging Face components. Focus is on data processing logic (deduplication, perplexity filtering, grid search) and statistical comparison.

**Applied:** Standard PyTorch/Hugging Face patterns from Archon KB

---

## 1. Data Pipeline

### 1.1 C4 Threshold Extraction

```python
def extract_c4_thresholds(doc_url: str = "https://huggingface.co/datasets/c4") -> Dict[str, Any]:
    """Parse C4 docs for filtering thresholds.
    
    Returns: {
        'dedup_ngram_size': int,
        'dedup_threshold': float,
        'perplexity_cutoff': float,
        'domain_ratios': Dict[str, float] | None
    }
    """
    # Fallback defaults from literature if undocumented
```

**Applied:** Web scraping pattern

---

### 1.2 Dolly Dataset Loading

```python
from datasets import load_dataset, Dataset
from typing import Tuple

def load_dolly(split_ratio: float = 0.9, seed: int = 42) -> Tuple[Dataset, Dataset]:
    """Load Dolly-15k and split.
    
    Returns:
        train: [13513] samples
        val: [1502] samples
    """
    dataset = load_dataset("databricks/databricks-dolly-15k", split="train")
    # dataset: [15015, {instruction, response, context, category}]
    splits = dataset.train_test_split(test_size=1-split_ratio, seed=seed)
    return splits["train"], splits["test"]
```

---

### 1.3 Deduplication

```python
from datasketch import MinHash, MinHashLSH

def deduplicate(dataset: Dataset, n_gram_size: int = 13, threshold: float = 0.8) -> Dataset:
    """MinHash LSH deduplication.
    
    dataset: [N] samples with 'instruction' field
    Returns: [M] samples where M <= N (duplicates removed)
    """
    # 1. Generate MinHash signatures for each sample
    # 2. Insert into LSH index
    # 3. Query for near-duplicates (Jaccard > threshold)
    # 4. Keep first occurrence, drop duplicates
```

**Tensor flow:**
- Input text: `[N]` strings
- n-gram hashes: `[N, num_perm]` uint64
- LSH buckets: `[num_bands, bucket_size]` indices
- Output: `[M]` unique samples

**Applied:** MinHash LSH pattern from Archon KB

---

### 1.4 Perplexity Filtering

```python
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

def filter_perplexity(
    dataset: Dataset,
    model_name: str = "gpt2",
    cutoff: float = 1000.0,
    batch_size: int = 32
) -> Dataset:
    """Remove high-perplexity outliers.
    
    dataset: [N] samples
    Returns: [M] samples where perplexity <= cutoff
    """
    model = GPT2LMHeadModel.from_pretrained(model_name).eval()
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    
    # For each sample:
    #   tokens = tokenize(text)  # [seq_len]
    #   logits = model(tokens)   # [seq_len, vocab_size]
    #   loss = cross_entropy(logits, tokens[1:])
    #   perplexity = exp(loss)
    #   keep if perplexity <= cutoff
```

**Tensor shapes:**
- Input text: `[N]` strings
- Tokens: `[N, seq_len]` int64
- Logits: `[N, seq_len, 50257]` float32
- Loss: `[N]` scalar
- Perplexity: `[N]` scalar
- Output: `[M]` filtered samples

**Applied:** Standard perplexity computation

---

### 1.5 Grid Search Optimization

```python
from itertools import product
from typing import List

def grid_search_filters(
    train_dataset: Dataset,
    val_dataset: Dataset,
    param_grid: Dict[str, List[float]],
    metric: str = "perplexity"
) -> Dict[str, float]:
    """Optimize filter thresholds on validation set.
    
    param_grid: {
        'dedup_threshold': [0.7, 0.8, 0.9, 0.95],
        'perplexity_cutoff': [500, 1000, 1500, 2000]
    }
    Returns: best params {param: value}
    """
    best_score = float('inf')
    best_params = {}
    
    for params in product(*param_grid.values()):
        # Apply filters with current params
        filtered = apply_filters(train_dataset, dict(zip(param_grid.keys(), params)))
        
        # Train lightweight probe (small LM) or use heuristic
        score = evaluate_on_val(filtered, val_dataset, metric)
        
        if score < best_score:
            best_score = score
            best_params = dict(zip(param_grid.keys(), params))
    
    return best_params
```

**Complexity:** O(grid_size × train_time), ~16 iterations for 4×4 grid

**Applied:** Grid search pattern

---

### 1.6 Domain Mixing

```python
def apply_domain_mixing(dataset: Dataset, ratios: Dict[str, float]) -> Dataset:
    """Resample by category to match target ratios.
    
    dataset: [N] with 'category' field
    ratios: {'open_qa': 0.3, 'creative_writing': 0.2, ...}
    Returns: [M] resampled to match ratios
    """
    # Group by category
    # For each category: sample(n = total * ratio)
    # Concatenate
```

**Fallback if no category field:**
```python
def filter_instruction_quality(dataset: Dataset, min_diversity: float = 0.5) -> Dataset:
    """Task-specific quality filters (objective-dependent).
    
    Filters:
    - Prompt diversity: n-gram entropy
    - Response length: 10-500 tokens
    - Instruction clarity: keyword presence
    """
```

---

### 1.7 Dataset Variant Orchestration

```python
def generate_variants(
    base_train: Dataset,
    base_val: Dataset,
    c4_params: Dict[str, Any]
) -> Dict[str, Dataset]:
    """Generate 5 experimental conditions.
    
    Returns: {
        'baseline': base_train,
        'transferred_indep': ...,
        'tuned_indep': ...,
        'transferred_dep': ...,
        'tuned_dep': ...
    }
    """
    variants = {"baseline": base_train}
    
    # Transferred-Independent
    tmp = deduplicate(base_train, c4_params['dedup_ngram_size'], c4_params['dedup_threshold'])
    variants['transferred_indep'] = filter_perplexity(tmp, cutoff=c4_params['perplexity_cutoff'])
    
    # Tuned-Independent
    tuned_params = grid_search_filters(
        base_train, base_val,
        {'dedup_threshold': [0.7, 0.8, 0.9, 0.95], 'perplexity_cutoff': [500, 1000, 1500, 2000]}
    )
    tmp = deduplicate(base_train, c4_params['dedup_ngram_size'], tuned_params['dedup_threshold'])
    variants['tuned_indep'] = filter_perplexity(tmp, cutoff=tuned_params['perplexity_cutoff'])
    
    # Transferred-Dependent
    if c4_params['domain_ratios']:
        variants['transferred_dep'] = apply_domain_mixing(base_train, c4_params['domain_ratios'])
    else:
        variants['transferred_dep'] = filter_instruction_quality(base_train, min_diversity=0.5)
    
    # Tuned-Dependent
    tuned_dep_params = optimize_instruction_filters(base_train, base_val)
    variants['tuned_dep'] = apply_domain_mixing(base_train, tuned_dep_params) or \
                            filter_instruction_quality(base_train, **tuned_dep_params)
    
    return variants
```

---

## 2. Training Pipeline

### 2.1 Training Configuration

```python
from transformers import TrainingArguments

def setup_training_config(output_dir: str, num_epochs: int = 3) -> TrainingArguments:
    """Fixed hyperparameters across all conditions."""
    return TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=8,
        gradient_accumulation_steps=8,  # effective batch 64
        learning_rate=2e-5,
        warmup_steps=100,
        lr_scheduler_type="cosine",
        save_strategy="epoch",
        save_total_limit=1,
        logging_steps=50,
        fp16=True,  # Mixed precision
        seed=42
    )
```

---

### 2.2 Fine-Tuning Wrapper

```python
from transformers import AutoModelForCausalLM, Trainer, DataCollatorForLanguageModeling

def fine_tune(
    model_name: str,
    dataset: Dataset,
    config: TrainingArguments,
    max_length: int = 512
) -> str:
    """Fine-tune LLM on instruction dataset.
    
    dataset: [N, {instruction, response}]
    Returns: checkpoint path
    """
    model = AutoModelForCausalLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Format: "<instruction>\n{text}\n<response>\n{text}"
    def tokenize(sample):
        text = f"<instruction>\n{sample['instruction']}\n<response>\n{sample['response']}"
        return tokenizer(text, truncation=True, max_length=max_length)
    
    tokenized = dataset.map(tokenize, batched=True)
    
    trainer = Trainer(
        model=model,
        args=config,
        train_dataset=tokenized,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
    )
    
    trainer.train()
    return config.output_dir
```

**Tensor shapes:**
- Input: `[batch=8, seq_len=512]` int64
- Embeddings: `[8, 512, 4096]` float16
- Logits: `[8, 512, 32000]` float16 (Llama-2 vocab)
- Loss: scalar

---

### 2.3 Multi-Condition Training

```python
def train_all_conditions(
    variants: Dict[str, Dataset],
    base_model: str = "meta-llama/Llama-2-7b-hf"
) -> Dict[str, str]:
    """Train 5 models in sequence.
    
    Returns: {condition: checkpoint_path}
    """
    checkpoints = {}
    for condition, dataset in variants.items():
        config = setup_training_config(output_dir=f"models/{condition}")
        checkpoint = fine_tune(base_model, dataset, config)
        checkpoints[condition] = checkpoint
    return checkpoints
```

---

## 3. Evaluation Pipeline

### 3.1 LM-Evaluation-Harness Setup

```python
def setup_lm_eval(tasks: List[str] = ['mmlu', 'hellaswag']) -> Dict[str, Any]:
    """Configure evaluation harness."""
    return {
        'tasks': tasks,
        'num_fewshot': 0,  # Zero-shot
        'batch_size': 16,
        'device': 'cuda'
    }
```

---

### 3.2 Model Evaluation

```python
from lm_eval import evaluator

def evaluate_model(checkpoint_path: str, tasks: List[str]) -> Dict[str, float]:
    """Run benchmarks on fine-tuned model.
    
    Returns: {
        'mmlu': 0.452,  # Accuracy
        'hellaswag': 0.621
    }
    """
    results = evaluator.simple_evaluate(
        model="hf-causal-experimental",
        model_args=f"pretrained={checkpoint_path}",
        tasks=tasks,
        num_fewshot=0,
        batch_size=16
    )
    
    return {task: results['results'][task]['acc'] for task in tasks}
```

**Tensor shapes (MMLU):**
- Questions: `[14042, max_len]` int64
- Logits: `[14042, max_len, 32000]` float16
- Predictions: `[14042]` int (argmax over choices)
- Accuracy: scalar

---

### 3.3 Transfer Delta Computation

```python
def compute_transfer_delta(
    acc_transferred: float,
    acc_tuned: float
) -> float:
    """Performance degradation when transferring thresholds.
    
    Returns: |transferred - tuned| / tuned × 100%
    """
    return abs(acc_transferred - acc_tuned) / acc_tuned * 100.0

def aggregate_deltas(results: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """Compute category-level deltas.
    
    results: {
        'baseline': {'mmlu': 0.40, 'hellaswag': 0.55},
        'transferred_indep': {'mmlu': 0.45, 'hellaswag': 0.60},
        'tuned_indep': {'mmlu': 0.455, 'hellaswag': 0.605},
        ...
    }
    Returns: {
        'independent_delta': 1.2,  # Average across tasks
        'dependent_delta': 6.8
    }
    """
    tasks = ['mmlu', 'hellaswag']
    
    indep_deltas = [
        compute_transfer_delta(
            results['transferred_indep'][task],
            results['tuned_indep'][task]
        ) for task in tasks
    ]
    
    dep_deltas = [
        compute_transfer_delta(
            results['transferred_dep'][task],
            results['tuned_dep'][task]
        ) for task in tasks
    ]
    
    return {
        'independent_delta': sum(indep_deltas) / len(indep_deltas),
        'dependent_delta': sum(dep_deltas) / len(dep_deltas)
    }
```

---

## 4. Statistical Analysis

### 4.1 Bootstrap Confidence Intervals

```python
import numpy as np
from typing import Tuple

def bootstrap_ci(
    deltas: np.ndarray,
    n_resamples: int = 10000,
    confidence: float = 0.95
) -> Tuple[float, float]:
    """Bootstrap 95% CI for delta distribution.
    
    deltas: [n_tasks] array (e.g., [1.2, 1.0] for MMLU, HellaSwag)
    Returns: (lower, upper) bounds
    """
    bootstrapped = np.random.choice(deltas, size=(n_resamples, len(deltas)), replace=True)
    means = bootstrapped.mean(axis=1)  # [n_resamples]
    
    alpha = 1 - confidence
    lower = np.percentile(means, alpha/2 * 100)
    upper = np.percentile(means, (1 - alpha/2) * 100)
    
    return lower, upper
```

---

### 4.2 Statistical Tests

```python
from scipy.stats import ttest_ind

def welch_t_test(
    independent_deltas: np.ndarray,
    dependent_deltas: np.ndarray
) -> Tuple[float, float]:
    """Test if categories differ significantly.
    
    independent_deltas: [n_tasks] e.g., [1.2, 1.0]
    dependent_deltas: [n_tasks] e.g., [6.5, 7.1]
    Returns: (t_statistic, p_value)
    """
    # Welch's t-test (unequal variance)
    return ttest_ind(independent_deltas, dependent_deltas, equal_var=False)

def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Effect size for group separation."""
    mean_diff = abs(group1.mean() - group2.mean())
    pooled_std = np.sqrt((group1.var() + group2.var()) / 2)
    return mean_diff / pooled_std
```

---

### 4.3 Gate Check

```python
def check_gate(
    independent_delta: float,
    dependent_delta: float,
    independent_ci: Tuple[float, float],
    dependent_ci: Tuple[float, float]
) -> Dict[str, Any]:
    """Evaluate SHOULD_WORK criteria.
    
    Returns: {
        'status': 'PASS' | 'FAIL',
        'independent_ok': bool,  # <= 1%
        'dependent_ok': bool,    # > 5%
        'ci_separation': bool,   # Non-overlapping
        'message': str
    }
    """
    independent_ok = independent_delta <= 1.0
    dependent_ok = dependent_delta > 5.0
    ci_separation = independent_ci[1] < dependent_ci[0]  # No overlap
    
    passed = independent_ok and dependent_ok and ci_separation
    
    return {
        'status': 'PASS' if passed else 'FAIL',
        'independent_ok': independent_ok,
        'dependent_ok': dependent_ok,
        'ci_separation': ci_separation,
        'message': f"Independent: {independent_delta:.2f}%, Dependent: {dependent_delta:.2f}%"
    }
```

---

## Summary

**Core logic:**
1. Data: MinHash LSH deduplication, GPT-2 perplexity filtering, grid search optimization
2. Training: Standard Hugging Face Trainer, fixed hyperparameters
3. Evaluation: lm-evaluation-harness wrapper, delta computation
4. Stats: Bootstrap CI, Welch's t-test, effect size

**No custom architectures needed.** Uses off-the-shelf transformers, datasketch, scipy.

**Key tensor flows:**
- Dedup: text → n-grams → MinHash signatures → LSH buckets → unique samples
- Perplexity: text → tokens `[N, 512]` → logits `[N, 512, 50257]` → loss → filter
- Training: tokens `[8, 512]` → embeddings `[8, 512, 4096]` → logits `[8, 512, 32000]` → loss
- Evaluation: questions → predictions → accuracy scalars
- Stats: deltas `[2]` → bootstrap `[10000]` → CI `[2]` → t-test → gate check

**Files:** Standard script-per-task pattern, no module decomposition needed for PoC.
