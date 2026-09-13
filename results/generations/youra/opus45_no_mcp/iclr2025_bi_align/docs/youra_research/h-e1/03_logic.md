# Logic: H-E1 (Calibration Inversion Clusters Exist Systematically)

**Type:** EXISTENCE (PoC) | Budget: 3 subtasks (A-2, A-6)

Applied: Sequence-logprob calibration scoring pattern (length-normalized)
Applied: K-means + silhouette gate-check pattern (scikit-learn standard)
Applied: Standard PyTorch batched teacher-forcing logprob extraction

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-2: Inference Module [Complexity: 12, Budget: 3]

**Applied**: Batched teacher-forcing logprob extraction (standard PyTorch)

### API Signatures

```python
def load_model(model_id: str) -> tuple[PreTrainedModel, PreTrainedTokenizer]:
    """Load HF model in fp16 on cuda, eval mode."""
    ...

def get_sequence_logprob(model, tokenizer, prompt: str, answer: str) -> float:
    """Sum log P(answer_tok | prompt, prev_answer_toks). Returns scalar."""
    ...

def get_length_normalized_logprob(model, tokenizer, prompt: str, answer: str) -> float:
    """get_sequence_logprob / len(answer_tokens)."""
    ...

def run_inference_on_tasks(
    model, tokenizer, tasks: list[Task], batch_size: int = 8
) -> dict[str, dict]:
    """Returns {task_id: {"correct_logprob_norm": float, "max_wrong_logprob_norm": float}}"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, P+A] | prompt+answer concatenated, single example (no padding batching in v1) |
| logits | [1, P+A, V] | model output |
| answer_logits | [1, A, V] | sliced to answer-token positions |
| token_logprobs | [A] | log_softmax gathered at target ids |

### Pseudo-code (sequence logprob)

```
1. ids_prompt = tokenize(prompt)              # [P]
2. ids_answer = tokenize(answer)              # [A]
3. input_ids = cat(ids_prompt, ids_answer)    # [1, P+A]
4. logits = model(input_ids).logits           # [1, P+A, V]
5. shift: predict token t from logits at position t-1
6. answer_logits = logits[:, P-1:P+A-1, :]    # [1, A, V]
7. logprobs = log_softmax(answer_logits, dim=-1)
8. token_logprobs = gather(logprobs, ids_answer)  # [A]
9. seq_logprob = sum(token_logprobs)
10. norm_logprob = seq_logprob / A
```

### run_inference_on_tasks loop

```
for batch in chunks(tasks, batch_size):       # ponytail: per-example forward, no padding/attn-mask batching; batch_size loops sequentially
    for task in batch:
        correct_lp = get_length_normalized_logprob(model, tok, task.question, task.correct_answer)
        wrong_lps = [get_length_normalized_logprob(model, tok, task.question, w) for w in task.incorrect_answers]
        results[task.task_id] = {
            "correct_logprob_norm": correct_lp,
            "max_wrong_logprob_norm": max(wrong_lps),
        }
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A2-1 | Model loading | `load_model`: fp16, device_map="cuda", eval() |
| L-A2-2 | Logprob extraction | `get_sequence_logprob` + `get_length_normalized_logprob` (teacher forcing) |
| L-A2-3 | Batched task loop | `run_inference_on_tasks`: iterate tasks, compute correct/max-wrong norm logprobs |

---

## A-6: Main Runner + Cross-Model Eval [Complexity: 10, Budget: 3]

**Applied**: Standard sequential orchestration script

### API Signatures

```python
def main() -> None:
    """Entry point: python run_experiment.py"""
    ...
```

### Pseudo-code

```
1. tasks = load_all_tasks()                                   # ~1517 Task dicts
2. results_by_model = {}
3. for model_id in config.MODELS:
     model, tok = load_model(model_id)
     inf = run_inference_on_tasks(model, tok, tasks, config.BATCH_SIZE)
     results_by_model[model_id] = inf
     del model; torch.cuda.empty_cache()

4. primary = config.MODELS[0]
5. X = build_calibration_vectors(results_by_model[primary])   # [N, 1]
6. sil_by_k = evaluate_k_range(X, config.K_RANGE)
7. best_k = select_best_k(sil_by_k)
8. cluster_result = cluster_and_evaluate(X, best_k)
9. gate_passed = cluster_result["silhouette_score"] > config.SILHOUETTE_GATE

10. labels_by_model = {primary: cluster_result["cluster_labels"]}
    for model_id in config.MODELS[1:]:
        Xi = build_calibration_vectors(results_by_model[model_id])
        labels_by_model[model_id] = fit_kmeans(Xi, best_k).labels_

11. plot_gate_metric(...), plot_calibration_histogram(...), plot_cluster_scatter(...),
    plot_cluster_profiles(...), plot_cross_model_agreement(labels_by_model, ...)

12. write results.json: per-task records (FR output format) + aggregate block
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| X | [N, 1] | inversion scores, N≈1517 |
| cluster_labels | [N] | int cluster id per task |
| labels_by_model | {model_id: [N]} | for agreement heatmap |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A6-1 | Multi-model inference loop | Load/run/free each of 3 models sequentially |
| L-A6-2 | Clustering + gate + cross-model labels | k-sweep on primary, cluster secondary/tertiary at best_k |
| L-A6-3 | Figures + results.json | Call all 5 plot fns, assemble/write output JSON |

---

## Other Modules (from architecture, no additional subtasks — low complexity)

APIs unchanged from `03_architecture.md`: `config.py`, `data.py`, `calibration.py`, `clustering.py`, `visualize.py`. See architecture doc for signatures.

### Key Tensor Shapes (cross-module)

| Variable | Shape | Note |
|----------|-------|------|
| calibration vectors X | [N, 1] | input to `fit_kmeans` / silhouette |
| cluster_centers | [k, 1] | from `KMeans.cluster_centers_` |
