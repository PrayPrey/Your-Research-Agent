# Logic Specification: H-E1

**Hypothesis:** Mamba-130M checkpoint validation  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-08-28  
**Author:** yoon303@ust.ac.kr

Applied: HuggingFace AutoModel pattern, zero-shot log-probability pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation - no existing code to analyze  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - first hypothesis implementation

---

## E1-2: Checkpoint Loading [Complexity: 8, Budget: 3]

Applied: HuggingFace AutoModel pattern

### API Signatures

```python
class CheckpointLoader:
    def __init__(
        self,
        model_name: str = "state-spaces/mamba-130m-hf",
        device: str = "cuda",
        dtype: str = "float16"
    ):
        """Initialize checkpoint loader."""
        self.model_name = model_name
        self.device = device
        self.dtype = getattr(torch, dtype)
    
    def load_model(self) -> AutoModelForCausalLM:
        """Load pretrained model. Returns: model"""
        ...
    
    def load_tokenizer(self) -> AutoTokenizer:
        """Load matching tokenizer. Returns: tokenizer"""
        ...
    
    def get_memory_stats(self) -> dict[str, float]:
        """Get GPU memory usage. Returns: {allocated_gb, reserved_gb, peak_gb}"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| model parameters | ~130M | FP16 = ~260MB |
| tokenizer vocab | ~50k | GPT-2 tokenizer |

### Pseudo-code

```
1. model = AutoModelForCausalLM.from_pretrained(
     model_name,
     torch_dtype=dtype,
     device_map="auto"
   )
2. tokenizer = AutoTokenizer.from_pretrained(model_name)
3. memory = torch.cuda.max_memory_allocated() / 1e9
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | AutoModel integration | Use HuggingFace from_pretrained |
| L-2-2 | Tokenizer loading | Match model checkpoint |
| L-2-3 | Memory tracking | CUDA memory stats |

---

## E1-4: Zero-Shot Evaluator [Complexity: 10, Budget: 3]

Applied: Zero-shot log-probability classification pattern

### API Signatures

```python
class ZeroShotEvaluator:
    def __init__(
        self,
        model: AutoModelForCausalLM,
        tokenizer: AutoTokenizer,
        device: str = "cuda"
    ):
        """Initialize evaluator."""
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
    
    def classify(
        self,
        text: str,
        choices: list[str],
        task_name: str
    ) -> int:
        """Classify single example. text: str, choices: [C] -> int (0..C-1)"""
        ...
    
    def evaluate_task(
        self,
        dataset,
        task_name: str,
        batch_size: int = 16,
        max_samples: int = None
    ) -> dict[str, float]:
        """Evaluate full task. Returns: {accuracy, total, correct}"""
        ...
    
    def _format_prompt(self, text: str, task_name: str) -> str:
        """Format task-specific prompt."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, L] | L ≤ 512 |
| choice_ids | [1, C] | C = choice token length |
| logits | [1, L, V] | V = vocab size ~50k |
| loss | scalar | Negative log-prob |

### Pseudo-code

```
classify(text, choices):
  1. prompt = _format_prompt(text, task_name)
  2. inputs = tokenizer(prompt, return_tensors="pt").to(device)
  3. probs = []
  4. for choice in choices:
       choice_ids = tokenizer(choice).input_ids
       with torch.no_grad():
         outputs = model(**inputs, labels=choice_ids)
         probs.append(-outputs.loss.item())
  5. return argmax(probs)

evaluate_task(dataset, task_name):
  1. correct = 0
  2. for example in dataset[:max_samples]:
       pred = classify(example['text'], example['choices'], task_name)
       if pred == example['label']:
         correct += 1
  3. return {accuracy: correct/len, total: len, correct: correct}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Prompt formatting | Task-specific templates (MNLI/QQP/SST2) |
| L-4-2 | Log-prob computation | Model forward with labels |
| L-4-3 | Batch evaluation | Loop over dataset, aggregate metrics |

---

## E1-5: Experiment Runner [Complexity: 9, Budget: 3]

Applied: PyTorch evaluation loop pattern

### API Signatures

```python
def run_experiment(config: dict) -> dict[str, Any]:
    """Run full evaluation pipeline. Returns: {task_name: metrics, gates: {...}}"""
    ...

def validate_memory(model: AutoModelForCausalLM, threshold_gb: float = 16.0) -> bool:
    """Check GPU memory constraint. Returns: peak_memory < threshold"""
    ...

def save_results(results: dict, output_path: str) -> None:
    """Save results to JSON."""
    ...

def validate_gates(results: dict) -> dict[str, bool]:
    """Check MUST_WORK gates. Returns: {gate_name: pass/fail}"""
    ...
```

### Tensor Shapes

N/A - orchestration logic only

### Pseudo-code

```
run_experiment(config):
  1. loader = CheckpointLoader(config['model'], config['device'], config['dtype'])
  2. model = loader.load_model()
  3. tokenizer = loader.load_tokenizer()
  4. evaluator = ZeroShotEvaluator(model, tokenizer, config['device'])
  5. results = {}
  6. for task in config['tasks']:
       dataset = load_dataset("glue", task, split="validation")
       results[task] = evaluator.evaluate_task(dataset, task, config['batch_size'])
  7. gates = validate_gates(results)
  8. results['gates'] = gates
  9. save_results(results, config['output_path'])
  10. return results

validate_gates(results):
  1. gates = {
       "checkpoint_loads": results is not None,
       "memory_ok": validate_memory(model, 16.0),
       "mnli_acc": results["mnli"]["accuracy"] > 0.333,
       "qqp_acc": results["qqp"]["accuracy"] > 0.50,
       "sst2_acc": results["sst2"]["accuracy"] > 0.50
     }
  2. return gates
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Pipeline orchestration | Load model → data → evaluate |
| L-5-2 | Gate validation | Check all MUST_WORK conditions |
| L-5-3 | Results serialization | Save JSON + memory stats |

---

## Data Structures

### Task Prompts

```python
TASK_PROMPTS = {
    "mnli": "Premise: {premise}\nHypothesis: {hypothesis}\nRelation:",
    "qqp": "Question 1: {question1}\nQuestion 2: {question2}\nDuplicate:",
    "sst2": "Sentence: {sentence}\nSentiment:"
}

TASK_CHOICES = {
    "mnli": ["entailment", "neutral", "contradiction"],
    "qqp": ["no", "yes"],
    "sst2": ["negative", "positive"]
}
```

### Results Schema

```python
{
  "mnli": {
    "accuracy": float,
    "total": int,
    "correct": int,
    "baseline": 0.333
  },
  "qqp": {...},
  "sst2": {...},
  "gates": {
    "checkpoint_loads": bool,
    "memory_ok": bool,
    "mnli_acc": bool,
    "qqp_acc": bool,
    "sst2_acc": bool
  },
  "memory_stats": {
    "peak_gb": float,
    "allocated_gb": float
  }
}
```

---

## Budget Summary

| Epic | Complexity | Allocated | Used | Status |
|------|-----------|-----------|------|--------|
| E1-2 | 8 | 3 | 3 | Full |
| E1-4 | 10 | 3 | 3 | Full |
| E1-5 | 9 | 3 | 3 | Full |

**Total**: 9/9 subtasks allocated

---

## Implementation Notes

**EXISTENCE simplifications:**
- No error retry logic (fail fast)
- Single evaluation pass (no bootstrapping)
- Minimal prompt engineering (task-specific templates only)
- No batch optimization (simple loop)

**Not included:**
- Prompt ablation studies
- Multiple model checkpoints
- Training/fine-tuning logic
- Advanced memory optimization
