# Logic Specification: h-e1 Implementation

**Date:** 2026-08-24
**Hypothesis ID:** h-e1 (EXISTENCE - PoC)
**Author:** Logic Agent
**Phase:** Phase 3 - Implementation Planning

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - designing new APIs
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## L-1: MinHash LSH Deduplication

**Applied**: Standard datasketch MinHash LSH pattern

### API Signatures

```python
class DeduplicationFilter:
    def __init__(self, threshold: float = 0.8, num_perm: int = 128):
        """Initialize LSH deduplicator. threshold: Jaccard similarity cutoff."""
        ...
    
    def filter_dataset(self, samples: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Deduplicate instruction samples.
        
        Args:
            samples: [{"instruction": str, "input": str, "output": str}]
        
        Returns:
            (filtered_samples, stats)
            stats: {"original": int, "unique": int, "removed": int}
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| samples | [N] | List of N instruction dicts |
| minhash_sig | [num_perm] | 128-dim hash signature |
| filtered | [M] | M ≤ N unique samples |

### Pseudo-code

```
1. Initialize LSH index with threshold=0.8, num_perm=128
2. For each sample:
   a. Concatenate instruction + input + output → text
   b. Tokenize text by whitespace
   c. Create MinHash signature (128 permutations)
   d. Query LSH for near-duplicates
   e. If no matches: insert signature, keep sample
   f. Else: discard sample
3. Return unique samples + statistics
```

### Error Handling

- Empty dataset → return empty list, stats with zeros
- Invalid JSON → skip malformed samples, log warning
- OOM during LSH index construction → batch processing (10k samples/chunk)

---

## L-2: KenLM Perplexity Filtering

**Applied**: Standard kenlm pattern with threshold cutoff

### API Signatures

```python
class PerplexityFilter:
    def __init__(self, model_path: str = "en.arpa.bin", cutoff: float = 100.0):
        """Initialize perplexity filter. cutoff: Max allowed perplexity."""
        ...
    
    def filter_dataset(self, samples: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Filter high-perplexity samples.
        
        Args:
            samples: [{"instruction": str, "input": str, "output": str}]
        
        Returns:
            (filtered_samples, stats)
            stats: {"original": int, "passed": int, "removed": int, "mean_ppl": float}
        """
        ...
    
    def compute_perplexity(self, text: str) -> float:
        """Compute KenLM perplexity for text."""
        ...
```

### Pseudo-code

```
1. Load KenLM model from model_path
2. For each sample:
   a. Concatenate instruction + input + output → text
   b. Compute perplexity = kenlm_model.perplexity(text)
   c. If perplexity ≤ cutoff: keep sample
   d. Else: discard sample
3. Compute statistics (mean perplexity, removal rate)
4. Return filtered samples + statistics
```

### Error Handling

- KenLM model file missing → raise FileNotFoundError with download instructions
- Empty text → assign perplexity = infinity, discard
- KenLM computation error → log warning, discard sample

---

## L-3: Threshold Tuning (Stage-Tuned Variant)

**Applied**: Grid search with validation perplexity objective

### API Signatures

```python
class ThresholdTuner:
    def __init__(
        self,
        dedup_range: List[float] = [0.6, 0.7, 0.8, 0.9],
        ppl_range: List[float] = [50, 75, 100, 150, 200],
        val_split: float = 0.05
    ):
        """Initialize threshold tuner."""
        ...
    
    def tune(
        self,
        dataset: List[Dict],
        model_name: str = "meta-llama/Llama-2-7b-hf"
    ) -> Dict[str, float]:
        """
        Grid search optimal thresholds.
        
        Args:
            dataset: Full Alpaca dataset
            model_name: Base LLM for validation perplexity
        
        Returns:
            {"dedup_threshold": float, "perplexity_cutoff": float, "val_loss": float}
        """
        ...
```

### Pseudo-code

```
1. Split dataset: 95% search, 5% validation
2. For each (dedup_threshold, ppl_cutoff) combination:
   a. Apply dedup filter to search split
   b. Apply perplexity filter
   c. Fine-tune model for 1 epoch (early stopping)
   d. Evaluate validation loss
   e. Store (thresholds, val_loss)
3. Select thresholds with minimum validation loss
4. Return optimal thresholds
```

### Subtasks

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Grid search loop | Iterate 25 threshold combinations |
| L-3-2 | Early-stopping training | 1-epoch fine-tune for validation |
| L-3-3 | Validation loss computation | Compute cross-entropy on 5% holdout |

### Error Handling

- OOM during fine-tuning → skip combination, log warning
- All combinations fail → fallback to C4 defaults (0.8, 100)
- Validation split too small → raise ValueError if val_split < 0.01

---

## L-4: Fine-Tuning with Loss Masking

**Applied**: Standard causal LM training with instruction masking

### API Signatures

```python
class InstructionDataCollator:
    def __init__(self, tokenizer, mask_inputs: bool = True):
        """
        Data collator with response-only loss.
        
        Args:
            tokenizer: HuggingFace tokenizer
            mask_inputs: If True, mask instruction/input tokens (compute loss only on output)
        """
        ...
    
    def __call__(self, features: List[Dict]) -> Dict[str, torch.Tensor]:
        """
        Collate batch with loss masking.
        
        Returns:
            {
                "input_ids": Tensor[B, L],
                "attention_mask": Tensor[B, L],
                "labels": Tensor[B, L]  # -100 for masked tokens
            }
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, L] | Tokenized input (B=batch, L=max_len) |
| attention_mask | [B, L] | 1 for real tokens, 0 for padding |
| labels | [B, L] | -100 for instruction tokens, token_id for response |

### Pseudo-code

```
1. Tokenize instruction + input + output separately
2. Concatenate: [instruction_tokens, input_tokens, response_marker, output_tokens]
3. Create labels:
   a. Copy input_ids
   b. Set labels[:response_start] = -100 (mask instruction/input)
   c. Keep labels[response_start:] = output_ids (compute loss here)
4. Pad to max_length
5. Return batch dict
```

### Error Handling

- Sequence length > max_length (2048) → truncate output, log warning
- Empty output → skip sample, raise warning
- Tokenizer special tokens mismatch → validate template format

---

## L-5: Evaluation Pipeline (lm-eval-harness)

**Applied**: Standard lm-evaluation-harness integration

### API Signatures

```python
def evaluate_model(
    model_path: str,
    tasks: List[str] = ["mmlu", "hellaswag"],
    num_fewshot: int = 0,
    batch_size: int = 8
) -> Dict[str, float]:
    """
    Evaluate model on benchmarks.
    
    Args:
        model_path: Path to fine-tuned checkpoint
        tasks: List of evaluation tasks
        num_fewshot: Number of few-shot examples (0 for zero-shot)
        batch_size: Evaluation batch size
    
    Returns:
        {
            "mmlu_acc": float,
            "hellaswag_acc": float,
            "mmlu_acc_stderr": float,
            "hellaswag_acc_stderr": float
        }
    """
    ...
```

### Pseudo-code

```
1. Load model from checkpoint (HuggingFace format)
2. Initialize lm_eval evaluator with model
3. For each task in ["mmlu", "hellaswag"]:
   a. Run simple_evaluate(model, task, num_fewshot=0, batch_size=8)
   b. Extract accuracy and stderr
4. Return metrics dict
```

### Error Handling

- Model checkpoint missing → raise FileNotFoundError
- lm-eval task error → log error, return NaN for that task
- OOM during evaluation → reduce batch_size to 4, retry once

---

## L-6: Gate Condition Verification

**Applied**: Simple threshold comparison

### API Signatures

```python
def verify_gate_condition(
    results: Dict[str, Dict[str, float]],
    delta_threshold: float = 0.01
) -> Dict[str, bool]:
    """
    Verify hypothesis gate conditions.
    
    Args:
        results: {
            "baseline": {"mmlu_acc": float, "hellaswag_acc": float},
            "transferred": {...},
            "stage_tuned": {...}
        }
        delta_threshold: Maximum allowed performance delta (0.01 = 1%)
    
    Returns:
        {
            "primary_pass": bool,  # |transferred - stage_tuned| ≤ 1%
            "secondary_pass": bool,  # both > baseline + 2%
            "gate_pass": bool,  # primary_pass AND secondary_pass
            "metrics": {...}
        }
    """
    ...
```

### Pseudo-code

```
1. Extract accuracies: acc_baseline, acc_transferred, acc_stage_tuned
2. Compute delta = |acc_transferred - acc_stage_tuned|
3. Primary condition: delta ≤ delta_threshold (0.01)
4. Secondary condition:
   a. acc_transferred > acc_baseline + 0.02
   b. acc_stage_tuned > acc_baseline + 0.02
5. Gate pass: primary AND secondary
6. Return verification results with detailed metrics
```

---

## L-7: End-to-End Pipeline

**Applied**: Sequential pipeline composition

### API Signatures

```python
def run_experiment(
    config: Dict[str, Any],
    output_dir: str = "h-e1/results"
) -> Dict[str, Any]:
    """
    Run full h-e1 experiment.
    
    Args:
        config: {
            "dataset_name": str,
            "model_name": str,
            "variants": ["baseline", "transferred", "stage_tuned"],
            "training": {...},
            "evaluation": {...}
        }
        output_dir: Directory for checkpoints and results
    
    Returns:
        {
            "curation_stats": {...},
            "training_logs": {...},
            "evaluation_results": {...},
            "gate_verification": {...}
        }
    """
    ...
```

### Pseudo-code

```
1. Load Alpaca-52k dataset
2. Create three curation variants:
   a. Baseline: raw dataset
   b. Transferred: apply dedup(0.8) + perplexity(100)
   c. Stage-tuned: tune thresholds, then apply
3. For each variant:
   a. Fine-tune LLaMA-2-7B for 3 epochs
   b. Save checkpoint to output_dir/{variant}/
   c. Log training curves
4. Evaluate each checkpoint on MMLU + HellaSwag
5. Verify gate condition
6. Generate visualizations
7. Save results to output_dir/results.json
8. Return experiment results
```

---

## External Dependencies

None - this is a green-field implementation with no base hypothesis code.

---

## Summary

**Total Logic Components:** 7
- L-1: MinHash LSH deduplication (datasketch)
- L-2: KenLM perplexity filtering (kenlm)
- L-3: Threshold tuning (grid search)
- L-4: Fine-tuning with loss masking (HuggingFace Trainer)
- L-5: Evaluation pipeline (lm-eval-harness)
- L-6: Gate condition verification (threshold comparison)
- L-7: End-to-end pipeline orchestration

**Key Design Decisions:**
1. Use standard libraries (datasketch, kenlm) over custom implementations
2. Response-only loss masking for instruction fine-tuning
3. Coarse grid search (5×5) for threshold tuning
4. 0-shot evaluation only (PoC simplification)
5. Single seed (42) for reproducibility

**Critical Parameters:**
- Deduplication threshold: 0.8 (C4 default)
- Perplexity cutoff: 100 (C4 default)
- Fine-tuning epochs: 3
- Learning rate: 2e-5
- Batch size: 128 (effective)

**Next Phase:** Phase 4 Implementation
