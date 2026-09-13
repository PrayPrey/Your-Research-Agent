# Logic Document: H-E1 Attention-Retrieval Correlation

**Version**: 1.0  
**Date**: 2026-08-20  
**Hypothesis ID**: h-e1  
**Type**: EXISTENCE (PoC)

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation - no existing codebase to analyze  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - designing new APIs

---

## Knowledge Base Patterns Applied

**Applied**: PyTorch forward hooks (standard), HuggingFace transformers output_attentions, scipy.stats.spearmanr

---

## Epic 1: Data Preparation (8 tasks)

### A-1: LongBench Download [Complexity: 1, Budget: 1]

**API**:

```python
def download_longbench(tasks: List[str], output_dir: str) -> Dict[str, int]:
    """Download LongBench dataset from HuggingFace.
    
    Returns: {task_name: sample_count}
    """
    from datasets import load_dataset
    dataset = load_dataset("THUDM/LongBench")
    return {task: len(dataset[task]) for task in tasks}
```

**Shapes**: N/A (I/O only)

---

### A-2: Passage Segmentation [Complexity: 2, Budget: 2]

**API**:

```python
def segment_passages(context: str) -> List[str]:
    """Split context on \\n\\n boundaries.
    
    Returns: List of passages (length 10-30)
    """
    return [p.strip() for p in context.split("\n\n") if p.strip()]

def track_passage_boundaries(
    passages: List[str], 
    tokenizer
) -> List[Tuple[int, int]]:
    """Map passages to token positions.
    
    Returns: [(start_idx, end_idx), ...] for each passage
    """
    boundaries = []
    current_pos = 0
    for passage in passages:
        tokens = tokenizer(passage)['input_ids']
        boundaries.append((current_pos, current_pos + len(tokens)))
        current_pos += len(tokens)
    return boundaries
```

**Shapes**: 
- `passages`: List[str] length 10-30
- `boundaries`: List[(int, int)] length N_passages

**Subtasks [2/2]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Split context | Use str.split("\n\n") |
| L-2-2 | Token mapping | Accumulate tokenizer output lengths |

---

### A-3: Query Complexity Labeling [Complexity: 2, Budget: 2]

**API**:

```python
def label_query_complexity(question: str) -> str:
    """Label query as Simple or Complex.
    
    Simple: word_count < 10 AND entity_density < 0.3
    Complex: otherwise
    
    Returns: "simple" or "complex"
    """
    import spacy
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(question)
    word_count = len(question.split())
    entity_density = len(doc.ents) / len(doc)
    
    if word_count < 10 and entity_density < 0.3:
        return "simple"
    return "complex"
```

**Subtasks [2/2]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Word count | len(question.split()) |
| L-3-2 | Entity density | spacy NER count / token count |

---

### A-4: BM25 Retrieval [Complexity: 2, Budget: 2]

**API**:

```python
from rank_bm25 import BM25Okapi
import nltk

def compute_bm25_scores(
    question: str, 
    passages: List[str]
) -> np.ndarray:
    """Compute BM25 scores for passages.
    
    Returns: [N_passages] float array
    """
    tokenized_passages = [nltk.word_tokenize(p.lower()) for p in passages]
    bm25 = BM25Okapi(tokenized_passages)
    tokenized_query = nltk.word_tokenize(question.lower())
    return bm25.get_scores(tokenized_query)  # [N_passages]
```

**Shapes**: `scores: [N_passages]`

**Subtasks [2/2]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Tokenize | nltk.word_tokenize |
| L-4-2 | BM25 scoring | BM25Okapi.get_scores |

---

### A-5: Contriever Retrieval [Complexity: 3, Budget: 3]

**API**:

```python
from transformers import AutoTokenizer, AutoModel
import torch

def compute_contriever_scores(
    question: str,
    passages: List[str],
    model,
    tokenizer,
    device: str = "cuda"
) -> np.ndarray:
    """Compute Contriever cosine similarity scores.
    
    Returns: [N_passages] float array
    """
    with torch.no_grad():
        # Query embedding [1, H]
        query_inputs = tokenizer(question, return_tensors='pt', 
                                 padding=True, truncation=True, 
                                 max_length=512).to(device)
        query_emb = model(**query_inputs).last_hidden_state[:, 0, :]
        
        # Passage embeddings [N_passages, H]
        passage_inputs = tokenizer(passages, return_tensors='pt',
                                   padding=True, truncation=True,
                                   max_length=512).to(device)
        passage_embs = model(**passage_inputs).last_hidden_state[:, 0, :]
        
        # Cosine similarity [N_passages]
        scores = torch.matmul(query_emb, passage_embs.T).squeeze()
    return scores.cpu().numpy()
```

**Shapes**:
- `query_emb`: [1, 768]
- `passage_embs`: [N_passages, 768]
- `scores`: [N_passages]

**Subtasks [3/3]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Load model | AutoModel.from_pretrained("facebook/contriever-msmarco") |
| L-5-2 | Encode | Extract CLS token embeddings |
| L-5-3 | Similarity | torch.matmul(query, passages.T) |

---

### A-6: Store Retrieval Results [Complexity: 1, Budget: 1]

**API**:

```python
def save_retrieval_results(
    question_id: str,
    bm25_scores: np.ndarray,
    contriever_scores: np.ndarray,
    output_dir: str
) -> None:
    """Save retrieval scores to disk."""
    np.save(f"{output_dir}/{question_id}_bm25.npy", bm25_scores)
    np.save(f"{output_dir}/{question_id}_contriever.npy", contriever_scores)
```

**Subtasks [1/1]**: L-6-1: np.save calls

---

### A-7: Data Pipeline Validation [Complexity: 2, Budget: 2]

**API**:

```python
def validate_preprocessing(
    passages: List[str],
    bm25_scores: np.ndarray,
    contriever_scores: np.ndarray
) -> bool:
    """Check data quality.
    
    Returns: True if valid
    """
    assert 10 <= len(passages) <= 50
    assert np.all(bm25_scores >= 0)
    assert np.all((-1 <= contriever_scores) & (contriever_scores <= 1))
    assert len(bm25_scores) == len(passages)
    return True
```

**Subtasks [2/2]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Range checks | Assert score bounds |
| L-7-2 | Length checks | Assert passage count 10-50 |

---

### A-8: Cache Dataset [Complexity: 1, Budget: 1]

**API**:

```python
def cache_dataset(data: Dict, output_path: str) -> None:
    """Serialize preprocessed dataset."""
    import pickle
    with open(output_path, 'wb') as f:
        pickle.dump(data, f)
```

**Subtasks [1/1]**: L-8-1: pickle.dump

---

## Epic 2: Model Setup & Attention Extraction (6 tasks)

### B-1: Load Llama-2-7B [Complexity: 2, Budget: 2]

**API**:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

def load_model(
    model_name: str = "meta-llama/Llama-2-7b-chat-hf",
    device: str = "cuda"
):
    """Load Llama-2 with attention extraction enabled."""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    return model, tokenizer
```

**Subtasks [2/2]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | Load tokenizer | AutoTokenizer.from_pretrained |
| L-9-2 | Load model | AutoModelForCausalLM with FP16 |

---

### B-2: AttentionCollector Hook [Complexity: 3, Budget: 3]

**API**:

```python
class AttentionCollector:
    """Collect attention weights during generation."""
    
    def __init__(self):
        self.attentions = []  # List of [B, H, S, S] tensors
    
    def hook_fn(self, module, input, output):
        """Forward hook to capture attention weights.
        
        output[1] contains attention when output_attentions=True
        Shape: [B, H, S, S]
        """
        if len(output) > 1 and output[1] is not None:
            self.attentions.append(output[1].detach().cpu())
    
    def clear(self):
        """Reset for next question."""
        self.attentions = []
```

**Shapes**:
- Hook output: `[B, H, S, S]` where B=1, H=32 (num_heads), S=seq_len
- `self.attentions`: List of tensors, length = num_generated_tokens

**Subtasks [3/3]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-10-1 | Hook class | Store attention in list |
| L-10-2 | Extract attention | output[1] when available |
| L-10-3 | Detach | .detach().cpu() to save memory |

---

### B-3: Install Hook on Last Layer [Complexity: 1, Budget: 1]

**API**:

```python
def install_attention_hook(
    model,
    collector: AttentionCollector
) -> None:
    """Register hook on last decoder layer."""
    last_layer = model.model.layers[-1].self_attn
    last_layer.register_forward_hook(collector.hook_fn)
```

**Subtasks [1/1]**: L-11-1: register_forward_hook call

---

### B-4: Attention Aggregation [Complexity: 3, Budget: 3]

**API**:

```python
def aggregate_attention(
    attentions: List[torch.Tensor],
    passage_boundaries: List[Tuple[int, int]]
) -> np.ndarray:
    """Aggregate attention to passage level.
    
    attentions: List of [B, H, S, S], length T (num_generated_tokens)
    passage_boundaries: [(start, end), ...] length N_passages
    
    Returns: [N_passages] aggregated attention weights
    """
    # Stack: [T, B, H, S, S]
    stacked = torch.stack(attentions, dim=0)
    
    # Average over heads: [T, B, S, S] -> [T, S, S] (assuming B=1)
    avg_heads = stacked.mean(dim=2).squeeze(1)
    
    # Sum over generated tokens: [S, S] -> [S]
    # For each context token, sum attention from all generated tokens
    context_attn = avg_heads[:, -1, :].sum(dim=0)  # [S]
    
    # Aggregate to passage level: [N_passages]
    passage_attn = np.zeros(len(passage_boundaries))
    for i, (start, end) in enumerate(passage_boundaries):
        passage_attn[i] = context_attn[start:end].sum().item()
    
    return passage_attn
```

**Shapes**:
- Input: `attentions` List[[B, H, S, S]], length T
- After stack: `[T, B, H, S, S]`
- After avg heads: `[T, B, S, S]`
- After sum tokens: `[S]`
- Output: `[N_passages]`

**Pseudo-code**:
```
1. Stack all generation step attentions: [T, B, H, S, S]
2. Average over attention heads: [T, B, S, S]
3. Extract attention from generated tokens to context: avg_heads[:, -1, :]
4. Sum across generated tokens: [S]
5. For each passage boundary:
   - Sum attention weights in [start:end] range
```

**Subtasks [3/3]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-12-1 | Average heads | .mean(dim=2) |
| L-12-2 | Sum tokens | .sum(dim=0) over generated tokens |
| L-12-3 | Passage mapping | Loop over boundaries, sum ranges |

---

### B-5: Save Attention Outputs [Complexity: 1, Budget: 1]

**API**:

```python
def save_attention(
    question_id: str,
    passage_attn: np.ndarray,
    output_dir: str
) -> None:
    """Save passage-level attention weights."""
    np.save(f"{output_dir}/{question_id}_attn.npy", passage_attn)
```

**Subtasks [1/1]**: L-13-1: np.save

---

### B-6: Attention Extraction Validation [Complexity: 2, Budget: 2]

**API**:

```python
def validate_attention(
    attentions: List[torch.Tensor],
    expected_shape: Tuple[int, int, int, int]
) -> bool:
    """Verify attention extraction correctness."""
    for attn in attentions:
        assert attn.shape == expected_shape  # [B, H, S, S]
        assert torch.all(attn >= 0)  # Non-negative
        assert not torch.all(attn == 0)  # Not all zeros
    return True
```

**Subtasks [2/2]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-14-1 | Shape check | Assert [B, H, S, S] |
| L-14-2 | Value check | Assert non-zero, non-negative |

---

## Epic 3: Experiment Execution (5 tasks)

### C-1: Generation Loop [Complexity: 3, Budget: 3]

**API**:

```python
def run_generation(
    model,
    tokenizer,
    question: str,
    passages: List[str],
    collector: AttentionCollector,
    max_new_tokens: int = 128
) -> Tuple[str, List[torch.Tensor]]:
    """Generate answer and collect attention.
    
    Returns: (answer_text, attention_list)
    """
    # Format prompt
    context = "\n\n".join(passages)
    prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    
    # Tokenize
    inputs = tokenizer(prompt, return_tensors='pt', truncation=True, 
                      max_length=8192).to(model.device)
    
    # Generate with attention
    collector.clear()
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            top_p=0.9,
            do_sample=False,
            output_attentions=True
        )
    
    # Decode answer
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return answer, collector.attentions
```

**Subtasks [3/3]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-15-1 | Format prompt | Concatenate context + question |
| L-15-2 | Generate | model.generate with output_attentions=True |
| L-15-3 | Decode | tokenizer.decode |

---

### C-2: Question Batching [Complexity: 1, Budget: 1]

**API**:

```python
def process_questions(
    questions: List[Dict],
    model,
    tokenizer,
    collector: AttentionCollector
) -> List[Dict]:
    """Process questions sequentially (batch_size=1 for stability).
    
    Returns: List of {question_id, answer, attentions}
    """
    results = []
    for q in questions:
        answer, attentions = run_generation(
            model, tokenizer, q['input'], q['passages'], collector
        )
        results.append({
            'question_id': q['_id'],
            'answer': answer,
            'attentions': attentions
        })
    return results
```

**Subtasks [1/1]**: L-16-1: Sequential loop (no actual batching)

---

### C-3: Answer Correctness Labeling [Complexity: 2, Budget: 2]

**API**:

```python
def label_answer_correctness(
    predicted: str,
    ground_truth: List[str]
) -> bool:
    """Check if answer is correct.
    
    Correct if exact_match OR f1 > 0.5
    """
    # Exact match
    pred_lower = predicted.strip().lower()
    if any(pred_lower in gt.strip().lower() for gt in ground_truth):
        return True
    
    # F1 score
    from nltk.metrics import f1_measure
    pred_tokens = set(predicted.split())
    for gt in ground_truth:
        gt_tokens = set(gt.split())
        precision = len(pred_tokens & gt_tokens) / len(pred_tokens) if pred_tokens else 0
        recall = len(pred_tokens & gt_tokens) / len(gt_tokens) if gt_tokens else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        if f1 > 0.5:
            return True
    
    return False
```

**Subtasks [2/2]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-17-1 | Exact match | Case-insensitive substring check |
| L-17-2 | F1 score | Token overlap, threshold 0.5 |

---

### C-4: Checkpoint Intermediate Results [Complexity: 2, Budget: 2]

**API**:

```python
def checkpoint_results(
    results: List[Dict],
    checkpoint_path: str,
    checkpoint_freq: int = 100
) -> None:
    """Save progress every N questions."""
    if len(results) % checkpoint_freq == 0:
        import pickle
        with open(checkpoint_path, 'wb') as f:
            pickle.dump(results, f)

def resume_from_checkpoint(checkpoint_path: str) -> List[Dict]:
    """Load previous results."""
    import pickle
    if os.path.exists(checkpoint_path):
        with open(checkpoint_path, 'rb') as f:
            return pickle.load(f)
    return []
```

**Subtasks [2/2]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-18-1 | Save checkpoint | pickle.dump every 100 questions |
| L-18-2 | Resume | pickle.load if exists |

---

### C-5: Main Experiment Runner [Complexity: 2, Budget: 2]

**API**:

```python
def main_experiment(
    dataset_path: str,
    output_dir: str,
    checkpoint_path: str
) -> None:
    """Run full experiment on 600 questions."""
    # Load data
    dataset = load_preprocessed_dataset(dataset_path)
    
    # Load model
    model, tokenizer = load_model()
    collector = AttentionCollector()
    install_attention_hook(model, collector)
    
    # Resume or start fresh
    results = resume_from_checkpoint(checkpoint_path)
    processed_ids = {r['question_id'] for r in results}
    
    # Process remaining questions
    for q in dataset:
        if q['_id'] in processed_ids:
            continue
        
        answer, attentions = run_generation(
            model, tokenizer, q['input'], q['passages'], collector
        )
        passage_attn = aggregate_attention(attentions, q['boundaries'])
        
        results.append({
            'question_id': q['_id'],
            'answer': answer,
            'passage_attn': passage_attn,
            'correct': label_answer_correctness(answer, q['answers'])
        })
        
        checkpoint_results(results, checkpoint_path)
    
    # Save final results
    save_final_results(results, output_dir)
```

**Subtasks [2/2]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-19-1 | Loop questions | Process 600 questions |
| L-19-2 | Save results | Write final outputs |

---

## Epic 4: Correlation Analysis (6 tasks)

### D-1: Spearman Correlation [Complexity: 2, Budget: 2]

**API**:

```python
from scipy.stats import spearmanr

def compute_correlation(
    retrieval_scores: np.ndarray,  # [N_passages]
    passage_attn: np.ndarray       # [N_passages]
) -> Tuple[float, float]:
    """Compute Spearman correlation.
    
    Returns: (rho, p_value)
    """
    rho, p_value = spearmanr(retrieval_scores, passage_attn)
    return rho, p_value
```

**Subtasks [2/2]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-20-1 | Import scipy | scipy.stats.spearmanr |
| L-20-2 | Compute rho | Call spearmanr(scores, attn) |

---

### D-2: Per-Question Correlation [Complexity: 2, Budget: 2]

**API**:

```python
def analyze_all_questions(
    results: List[Dict],
    retrieval_dir: str
) -> pd.DataFrame:
    """Compute correlation for all 600 questions.
    
    Returns: DataFrame with [question_id, rho_bm25, rho_contriever, 
                            query_complexity, answer_correct]
    """
    rows = []
    for r in results:
        bm25_scores = np.load(f"{retrieval_dir}/{r['question_id']}_bm25.npy")
        contriever_scores = np.load(f"{retrieval_dir}/{r['question_id']}_contriever.npy")
        
        rho_bm25, p_bm25 = compute_correlation(bm25_scores, r['passage_attn'])
        rho_contriever, p_contriever = compute_correlation(contriever_scores, r['passage_attn'])
        
        rows.append({
            'question_id': r['question_id'],
            'rho_bm25': rho_bm25,
            'p_bm25': p_bm25,
            'rho_contriever': rho_contriever,
            'p_contriever': p_contriever,
            'query_complexity': r['complexity'],
            'answer_correct': r['correct']
        })
    
    return pd.DataFrame(rows)
```

**Subtasks [2/2]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-21-1 | Load scores | np.load for BM25/Contriever |
| L-21-2 | Compute per-Q | Loop over questions |

---

### D-3: Stratified Analysis [Complexity: 3, Budget: 3]

**API**:

```python
def stratified_analysis(
    df: pd.DataFrame
) -> Dict[str, Dict[str, float]]:
    """Compute mean rho by stratification dimensions.
    
    Returns: {
        'overall': {'bm25': 0.35, 'contriever': 0.42},
        'simple': {'bm25': 0.38, 'contriever': 0.45},
        'complex': {'bm25': 0.33, 'contriever': 0.40},
        'correct': {'bm25': 0.40, 'contriever': 0.48},
        'incorrect': {'bm25': 0.28, 'contriever': 0.35}
    }
    """
    results = {}
    
    # Overall
    results['overall'] = {
        'bm25': df['rho_bm25'].mean(),
        'contriever': df['rho_contriever'].mean()
    }
    
    # By query complexity
    for complexity in ['simple', 'complex']:
        subset = df[df['query_complexity'] == complexity]
        results[complexity] = {
            'bm25': subset['rho_bm25'].mean(),
            'contriever': subset['rho_contriever'].mean()
        }
    
    # By answer correctness
    for correct in [True, False]:
        label = 'correct' if correct else 'incorrect'
        subset = df[df['answer_correct'] == correct]
        results[label] = {
            'bm25': subset['rho_bm25'].mean(),
            'contriever': subset['rho_contriever'].mean()
        }
    
    return results
```

**Subtasks [3/3]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-22-1 | Overall mean | df.mean() |
| L-22-2 | Group by complexity | Filter + mean |
| L-22-3 | Group by correctness | Filter + mean |

---

### D-4: Bootstrap Confidence Intervals [Complexity: 2, Budget: 2]

**API**:

```python
def bootstrap_ci(
    values: np.ndarray,
    n_resamples: int = 1000,
    alpha: float = 0.05
) -> Tuple[float, float]:
    """Compute 95% CI via bootstrap.
    
    Returns: (ci_lower, ci_upper)
    """
    means = []
    for _ in range(n_resamples):
        sample = np.random.choice(values, size=len(values), replace=True)
        means.append(sample.mean())
    
    ci_lower = np.percentile(means, alpha/2 * 100)
    ci_upper = np.percentile(means, (1 - alpha/2) * 100)
    
    return ci_lower, ci_upper
```

**Subtasks [2/2]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-23-1 | Resample | np.random.choice with replacement |
| L-23-2 | Percentiles | np.percentile at 2.5%, 97.5% |

---

### D-5: Visualization [Complexity: 2, Budget: 2]

**API**:

```python
def plot_scatter(
    retrieval_scores: np.ndarray,
    passage_attn: np.ndarray,
    rho: float,
    p_value: float,
    output_path: str,
    title: str
) -> None:
    """Create scatter plot with correlation annotation."""
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(8, 6))
    plt.scatter(retrieval_scores, passage_attn, alpha=0.5)
    plt.xlabel('Retrieval Score')
    plt.ylabel('Passage Attention Weight')
    plt.title(f'{title}\nρ = {rho:.3f}, p = {p_value:.3e}')
    plt.savefig(output_path)
    plt.close()
```

**Subtasks [2/2]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-24-1 | Scatter plot | plt.scatter |
| L-24-2 | Annotate | Add rho, p-value text |

---

### D-6: Summary Statistics [Complexity: 2, Budget: 2]

**API**:

```python
def generate_summary(
    df: pd.DataFrame,
    stratified: Dict,
    output_path: str
) -> Dict:
    """Write summary statistics to JSON.
    
    Returns: {
        'mean_rho_bm25': 0.35,
        'mean_rho_contriever': 0.42,
        'ci_95_bm25': [0.32, 0.38],
        'ci_95_contriever': [0.39, 0.45],
        'p_bm25': 0.001,
        'p_contriever': 0.0001,
        'stratified': {...}
    }
    """
    from scipy.stats import ttest_1samp
    
    summary = {
        'mean_rho_bm25': df['rho_bm25'].mean(),
        'mean_rho_contriever': df['rho_contriever'].mean(),
        'ci_95_bm25': bootstrap_ci(df['rho_bm25'].values),
        'ci_95_contriever': bootstrap_ci(df['rho_contriever'].values),
        'p_bm25': ttest_1samp(df['rho_bm25'], 0).pvalue,
        'p_contriever': ttest_1samp(df['rho_contriever'], 0).pvalue,
        'stratified': stratified
    }
    
    import json
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    return summary
```

**Subtasks [2/2]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-25-1 | Aggregate stats | Mean, CI, p-value |
| L-25-2 | Write JSON | json.dump |

---

## Epic 5: Baseline Validation (3 tasks)

### E-1: Random Baseline [Complexity: 1, Budget: 1]

**API**:

```python
def random_baseline(
    passage_attn: np.ndarray,
    n_permutations: int = 1000,
    seed: int = 42
) -> float:
    """Compute mean correlation with shuffled scores.
    
    Returns: mean_rho_random
    """
    np.random.seed(seed)
    rhos = []
    for _ in range(n_permutations):
        random_scores = np.random.permutation(passage_attn)
        rho, _ = spearmanr(random_scores, passage_attn)
        rhos.append(rho)
    return np.mean(rhos)
```

**Subtasks [1/1]**: L-26-1: Permute and correlate

---

### E-2: Uniform Attention Baseline [Complexity: 1, Budget: 1]

**API**:

```python
def uniform_baseline(
    retrieval_scores: np.ndarray
) -> float:
    """Correlate retrieval scores with uniform attention.
    
    Returns: rho_uniform (should be ~0)
    """
    uniform_attn = np.ones_like(retrieval_scores) / len(retrieval_scores)
    rho, _ = spearmanr(retrieval_scores, uniform_attn)
    return rho
```

**Subtasks [1/1]**: L-27-1: Create uniform array, correlate

---

### E-3: Position Bias Baseline [Complexity: 2, Budget: 2]

**API**:

```python
def position_baseline(
    passage_attn: np.ndarray
) -> float:
    """Correlate position (U-shaped) with attention.
    
    Returns: rho_position
    """
    n = len(passage_attn)
    position_scores = np.linspace(0, 1, n)
    u_shaped = 1 - 4 * (position_scores - 0.5)**2  # Beginning + end bias
    rho, _ = spearmanr(u_shaped, passage_attn)
    return rho
```

**Subtasks [2/2]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-28-1 | U-shaped scores | 1 - 4*(x-0.5)^2 |
| L-28-2 | Correlate | spearmanr with attention |

---

## Gate Decision Logic

```python
def gate_decision(summary: Dict) -> str:
    """Determine PASS/FAIL for MUST_WORK gate.
    
    Returns: "PASS" or "FAIL"
    """
    rho_bm25 = summary['mean_rho_bm25']
    rho_contriever = summary['mean_rho_contriever']
    
    if rho_bm25 > 0.3 and rho_contriever > 0.3:
        return "PASS"  # Proceed to H-M1
    else:
        return "FAIL"  # Route to Phase 0
```

---

## Summary

**Total Tasks**: 28 across 5 epics  
**Total Budget**: 56 subtasks  
**Key Algorithms**:
1. Attention aggregation: stack → avg heads → sum tokens → map to passages
2. Token-to-passage mapping: accumulate tokenizer lengths
3. Correlation: scipy.stats.spearmanr
4. Bootstrap CI: resample with replacement, percentiles

**Critical Implementation Details**:
- Passage boundaries tracked during tokenization (character positions → token indices)
- Attention extracted from `output[1]` in forward hook when `output_attentions=True`
- Last layer attention: `model.model.layers[-1].self_attn`
- Checkpoint every 100 questions via pickle
- Batch size = 1 for attention extraction stability

**External Dependencies**: None (green-field project)
