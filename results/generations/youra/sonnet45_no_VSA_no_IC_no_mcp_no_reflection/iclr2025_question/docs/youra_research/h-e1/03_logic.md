# Logic Design: h-e1
## API Signatures, Tensor Shapes, and Algorithms

**Date:** 2026-08-28  
**Hypothesis:** h-e1 (EXISTENCE)  
**Subtask Budget:** 4 tasks

---

## Codebase Analysis (Serena)

*MCP unavailable — manual design patterns applied*

**Applied Patterns:**
- Applied: `frozen_model_inference` — Standard HuggingFace forward pass pattern
- Applied: `entropy_computation` — Shannon entropy over softmax distributions
- Applied: `statistical_testing` — SciPy correlation analysis

---

## Module APIs

### 1. Data Module (`data.py`)

#### Function: `load_triviaqa_subset`
```python
def load_triviaqa_subset(split: str = "validation[:1000]") -> Dataset:
    """
    Load TriviaQA unfiltered subset for evaluation.
    
    Args:
        split: Dataset split specification (default: first 1000 validation examples)
    
    Returns:
        Dataset object with question/answer pairs
    
    Raises:
        ConnectionError: If HuggingFace hub unreachable
        ValueError: If split specification invalid
    """
```

**Tensor Shapes:** N/A (returns Dataset object)

**Algorithm:**
1. Call `datasets.load_dataset("trivia_qa", "unfiltered", split=split)`
2. Verify dataset not empty
3. Return dataset handle

---

#### Function: `prepare_example`
```python
def prepare_example(example: dict) -> tuple[str, str]:
    """
    Extract question and answer from TriviaQA example.
    
    Args:
        example: Single TriviaQA example with "question" and "answer" fields
    
    Returns:
        (question_text, answer_value)
    
    Raises:
        KeyError: If required fields missing
    """
```

**Tensor Shapes:** N/A (string processing)

**Algorithm:**
1. Extract `example["question"]`
2. Extract `example["answer"]["value"]`
3. Return tuple

---

### 2. Model Module (`model.py`)

#### Function: `load_llama_model`
```python
def load_llama_model(
    model_name: str = "meta-llama/Llama-2-7b-hf",
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """
    Load frozen Llama-2 model and tokenizer.
    
    Args:
        model_name: HuggingFace model identifier
        device: Target device ("cuda" or "cpu")
    
    Returns:
        (model, tokenizer)
    
    Side Effects:
        - Downloads model to HuggingFace cache (~13GB)
        - Sets model to eval mode (frozen)
    """
```

**Tensor Shapes:** N/A (returns model objects)

**Algorithm:**
1. Load tokenizer: `AutoTokenizer.from_pretrained(model_name)`
2. Load model: `AutoModelForCausalLM.from_pretrained(model_name)`
3. Move model to device: `model.to(device)`
4. Set eval mode: `model.eval()`
5. Return (model, tokenizer)

---

#### Function: `forward_pass`
```python
def forward_pass(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    question: str,
    max_length: int = 512
) -> dict:
    """
    Perform forward pass and extract logits and prediction.
    
    Args:
        model: Frozen Llama-2 model
        tokenizer: Matching tokenizer
        question: Input question text
        max_length: Max tokenization length
    
    Returns:
        {
            "logits": Tensor[vocab_size],  # Next-token logits
            "pred_id": int,                 # Predicted token ID
            "pred_text": str                # Decoded prediction
        }
    """
```

**Tensor Shapes:**
- Input: `inputs["input_ids"]` → `[1, seq_len]`
- Output logits: `outputs.logits[:, -1, :]` → `[1, vocab_size]`
- Squeezed logits: `[vocab_size]` (returned)

**Algorithm:**
1. Tokenize: `inputs = tokenizer(question, return_tensors="pt", truncation=True, max_length=max_length)`
2. Move to device: `inputs = {k: v.to(model.device) for k, v in inputs.items()}`
3. Forward pass (no grad): `with torch.no_grad(): outputs = model(**inputs)`
4. Extract next-token logits: `logits = outputs.logits[:, -1, :].squeeze(0)`
5. Predict: `pred_id = torch.argmax(logits).item()`
6. Decode: `pred_text = tokenizer.decode([pred_id])`
7. Return dict

---

### 3. Metrics Module (`metrics.py`)

#### Function: `compute_entropy`
```python
def compute_entropy(logits: Tensor) -> float:
    """
    Compute Shannon entropy from logits.
    
    Args:
        logits: Raw logits tensor [vocab_size]
    
    Returns:
        Entropy value (scalar)
    
    Algorithm:
        H(p) = -Σ p(x) log p(x)
        where p = softmax(logits)
    """
```

**Tensor Shapes:**
- Input: `logits` → `[vocab_size]`
- Probs: `[vocab_size]`
- Entropy: scalar (float)

**Algorithm (Pseudo-code):**
```python
probs = F.softmax(logits, dim=-1)  # [vocab_size]
log_probs = torch.log(probs + 1e-10)  # Numerical stability
entropy = -torch.sum(probs * log_probs)  # Scalar
return entropy.item()
```

**Numerical Considerations:**
- Add epsilon (1e-10) to avoid log(0)
- Use stable softmax (PyTorch handles internally)

---

#### Function: `compute_spearman`
```python
def compute_spearman(
    entropies: list[float],
    correctness: list[int]
) -> tuple[float, float]:
    """
    Compute Spearman rank correlation between entropy and correctness.
    
    Args:
        entropies: List of entropy values
        correctness: List of binary correctness labels (0/1)
    
    Returns:
        (correlation_coefficient, p_value)
    
    Library: scipy.stats.spearmanr
    """
```

**Tensor Shapes:** N/A (uses lists, not tensors)

**Algorithm:**
1. Call `scipy.stats.spearmanr(entropies, correctness)`
2. Return (ρ, p_value)

---

#### Function: `extraction_rate`
```python
def extraction_rate(entropies: list[float]) -> float:
    """
    Compute fraction of valid entropy extractions.
    
    Args:
        entropies: List with potential None/NaN values
    
    Returns:
        Rate in [0, 1]
    """
```

**Algorithm:**
```python
valid_count = sum(1 for e in entropies if e is not None and not np.isnan(e))
return valid_count / len(entropies)
```

---

#### Function: `quadrant_analysis`
```python
def quadrant_analysis(
    max_probs: list[float],
    entropies: list[float]
) -> dict:
    """
    Compute Q3 (high max-prob, high entropy) population.
    
    Args:
        max_probs: Max probabilities from softmax
        entropies: Entropy values
    
    Returns:
        {
            "median_maxprob": float,
            "median_entropy": float,
            "q3_count": int,
            "q3_fraction": float
        }
    """
```

**Algorithm:**
```python
median_maxprob = np.median(max_probs)
median_entropy = np.median(entropies)

q3_mask = (np.array(max_probs) > median_maxprob) & (np.array(entropies) > median_entropy)
q3_count = np.sum(q3_mask)
q3_fraction = q3_count / len(entropies)

return {"median_maxprob": median_maxprob, "median_entropy": median_entropy, 
        "q3_count": q3_count, "q3_fraction": q3_fraction}
```

---

### 4. Visualization Module (`visualization.py`)

#### Function: `plot_gate_metrics`
```python
def plot_gate_metrics(
    metrics: dict,
    output_path: str,
    thresholds: dict = {"extraction_rate": 0.95, "p_value": 0.05, "q3_fraction": 0.05}
) -> None:
    """
    Generate bar chart comparing metrics to thresholds.
    
    Args:
        metrics: {"extraction_rate": float, "p_value": float, "q3_fraction": float}
        output_path: Save path for figure
        thresholds: Target thresholds for each metric
    """
```

**Algorithm:**
1. Create bar chart with 3 bars (extraction_rate, p_value, q3_fraction)
2. Add horizontal threshold lines
3. Color bars red (below threshold) or green (above threshold)
4. Save to `output_path`

---

#### Function: `plot_scatter`
```python
def plot_scatter(
    entropies: list[float],
    correctness: list[int],
    output_path: str
) -> None:
    """
    Scatter plot with jittered binary correctness and regression line.
    """
```

---

#### Function: `plot_histograms`
```python
def plot_histograms(
    entropies_correct: list[float],
    entropies_incorrect: list[float],
    output_path: str
) -> None:
    """
    Overlaid histograms of entropy distributions.
    """
```

---

#### Function: `plot_quadrant`
```python
def plot_quadrant(
    max_probs: list[float],
    entropies: list[float],
    correctness: list[int],
    output_path: str
) -> None:
    """
    Quadrant plot with median splits and Q3 annotation.
    """
```

---

### 5. Experiment Runner (`main.py`)

#### Main Loop
```python
def run_experiment() -> dict:
    """
    Execute end-to-end experiment.
    
    Returns:
        {
            "extraction_rate": float,
            "correlation": float,
            "p_value": float,
            "q3_fraction": float,
            "gate_pass": bool
        }
    """
```

**Algorithm:**
```python
1. dataset = load_triviaqa_subset()
2. model, tokenizer = load_llama_model()
3. entropies, correctness, max_probs = [], [], []
4. for example in dataset:
    a. question, answer = prepare_example(example)
    b. result = forward_pass(model, tokenizer, question)
    c. entropy = compute_entropy(result["logits"])
    d. is_correct = int(result["pred_text"].strip().lower() == answer.strip().lower())
    e. max_prob = torch.max(F.softmax(result["logits"], dim=-1)).item()
    f. entropies.append(entropy)
    g. correctness.append(is_correct)
    h. max_probs.append(max_prob)
5. extraction_rate = extraction_rate(entropies)
6. correlation, p_value = compute_spearman(entropies, correctness)
7. quad_results = quadrant_analysis(max_probs, entropies)
8. gate_pass = (extraction_rate > 0.95 and p_value < 0.05 and quad_results["q3_fraction"] > 0.05)
9. Generate all 4 figures via visualization module
10. Return metrics
```

---

## Subtask Breakdown

### Subtask L-1: Model Inference API (Epic-2)
**Complexity:** 2/5  
**Description:** Implement `load_llama_model` and `forward_pass` with logits extraction.

**API Surface:**
- `load_llama_model() -> (model, tokenizer)`
- `forward_pass(model, tokenizer, question) -> dict`

**Key Tensor Operations:**
- Tokenization: `[str] → [1, seq_len]`
- Forward: `[1, seq_len] → [1, seq_len, vocab_size]`
- Slice: `[:, -1, :] → [1, vocab_size]`

---

### Subtask L-2: Entropy Computation (Epic-2)
**Complexity:** 1/5  
**Description:** Implement `compute_entropy` with numerical stability.

**API Surface:**
- `compute_entropy(logits: Tensor) -> float`

**Algorithm:**
- Softmax → log(p + ε) → -Σ p log p

---

### Subtask L-3: Main Experiment Loop (Epic-3)
**Complexity:** 2/5  
**Description:** Orchestrate data loading, inference, and collection.

**Flow:**
```
Dataset → prepare_example → forward_pass → compute_entropy → collect
```

---

### Subtask L-4: Statistical Analysis (Epic-4)
**Complexity:** 2/5  
**Description:** Implement Spearman correlation and quadrant analysis.

**API Surface:**
- `compute_spearman(entropies, correctness) -> (ρ, p)`
- `quadrant_analysis(max_probs, entropies) -> dict`

---

## Tensor Shape Reference

| Operation | Input Shape | Output Shape |
|-----------|-------------|--------------|
| Tokenization | `str` | `[1, seq_len]` |
| Model forward | `[1, seq_len]` | `[1, seq_len, vocab_size]` |
| Next-token slice | `[1, seq_len, vocab_size]` | `[1, vocab_size]` |
| Softmax | `[vocab_size]` | `[vocab_size]` |
| Entropy | `[vocab_size]` | scalar |

**Vocab size:** ~32,000 (Llama-2 tokenizer)

---

## Error Handling

### Tokenization Failures
```python
try:
    inputs = tokenizer(question, return_tensors="pt", truncation=True, max_length=512)
except Exception as e:
    log(f"Tokenization failed: {e}")
    return None  # Skip example
```

### NaN Entropy
```python
if torch.isnan(entropy):
    log(f"NaN entropy for example {idx}")
    entropies.append(None)  # Filter later
```

### Model Loading
```python
try:
    model = AutoModelForCausalLM.from_pretrained(model_name)
except Exception as e:
    raise RuntimeError(f"Model loading failed: {e}. Check HuggingFace cache.")
```

---

## External Dependencies API

### HuggingFace Transformers
- `AutoModelForCausalLM.from_pretrained(model_id)` → `PreTrainedModel`
- `AutoTokenizer.from_pretrained(model_id)` → `PreTrainedTokenizer`
- `model(**inputs)` → `CausalLMOutputWithPast` (with `.logits` attribute)

### HuggingFace Datasets
- `load_dataset(name, config, split)` → `Dataset`
- `dataset[idx]` → `dict` with dataset-specific keys

### PyTorch
- `torch.nn.functional.softmax(logits, dim)` → `Tensor`
- `torch.sum(tensor)` → scalar `Tensor`
- `torch.argmax(tensor)` → index

### SciPy
- `scipy.stats.spearmanr(x, y)` → `(correlation, p_value)`

---

**Logic Status:** Ready for implementation (Phase 4)
