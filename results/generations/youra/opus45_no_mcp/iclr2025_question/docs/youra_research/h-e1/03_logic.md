# Logic Specification: H-E1 (EXISTENCE)

**Type:** EXISTENCE (PoC) — minimal API to verify entropy + consistency computable at scale.

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - new API design, no existing code to analyze
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation

---

## A-1: Data Loading [Complexity: 1, Budget: 1]

**Applied:** Standard HuggingFace `datasets` streaming pattern

### API Signatures

```python
def load_triviaqa_questions(split: str = "validation") -> list[dict]:
    """Load TriviaQA rc.nocontext. Returns list of {'question_id': str, 'question': str}."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | load_triviaqa_questions | Load HF dataset, extract id+question only |

---

## A-2: Response Generation [Complexity: 3, Budget: 3]

**Applied:** HuggingFace `generate(output_scores=True, return_dict_in_generate=True)`

### API Signatures

```python
def load_model(
    model_name: str = "meta-llama/Llama-2-7b-chat-hf",
) -> tuple["PreTrainedModel", "PreTrainedTokenizer"]:
    """FP16, device_map='auto'."""
    ...

def generate_responses(
    model: "PreTrainedModel",
    tokenizer: "PreTrainedTokenizer",
    question: str,
    n_samples: int = 10,
    temperature: float = 0.7,
    max_new_tokens: int = 128,
    seed: int = 42,
) -> list[dict]:
    """Generate n_samples responses with per-token logits.

    Returns: list of {'text': str, 'scores': list[Tensor[V]]}  # V = vocab size
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| inputs.input_ids | [1, P] | P = prompt tokens |
| outputs.sequences | [1, P+T] | T <= max_new_tokens |
| outputs.scores[t] | [1, V] | logits at generation step t, V=32000 |

### Pseudo-code

```
prompt = f"[INST] {question} [/INST]"
for i in range(n_samples):
    set_seed(seed + i)  # vary seed per sample for diversity + reproducibility
    out = model.generate(**inputs, max_new_tokens, temperature, do_sample=True,
                          output_scores=True, return_dict_in_generate=True)
    text = decode(out.sequences[0][prompt_len:])
    yield {'text': text, 'scores': out.scores}  # scores: T x [1, V]
```

### Error Handling

- `torch.cuda.OutOfMemoryError` → catch, `torch.cuda.empty_cache()`, log question_id, return `success=False`, skip sample
- Empty generation (T=0) → treat as failed sample, exclude from entropy calc

### Subtasks [1/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | load_model + generate_responses | Model load + per-question sampling loop |

---

## A-3: Entropy Computation [Complexity: 2, Budget: 2]

**Applied:** Shannon entropy over softmax(logits), KB pattern from Kuhn et al. 2023

### API Signatures

```python
def compute_token_entropy(scores: list["Tensor"]) -> float:
    """Mean Shannon entropy across generated tokens.
    scores: T x [1, V] -> float
    """
    ...

def compute_sample_entropies(responses: list[dict]) -> list[float]:
    """Per-response entropy. Returns len(responses) floats (nan for failed samples)."""
    ...
```

### Pseudo-code

```
for score in scores:            # score: [1, V]
    probs = softmax(score, dim=-1)
    log_probs = log_softmax(score, dim=-1)
    h = -sum(probs * log_probs)  # scalar
    token_entropies.append(h)
return mean(token_entropies)
```

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | compute_token_entropy | Per-response + per-question aggregation |

---

## A-4: Semantic Consistency [Complexity: 2, Budget: 2]

**Applied:** SelfCheckGPT pairwise cosine similarity pattern

### API Signatures

```python
def load_embedding_model(
    name: str = "sentence-transformers/all-MiniLM-L6-v2",
) -> "SentenceTransformer":
    ...

def compute_consistency(responses: list[str], embed_model: "SentenceTransformer") -> float:
    """Mean pairwise cosine similarity across responses. -> float in [-1, 1]."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| embeddings | [N, 384] | N=len(responses), MiniLM dim=384 |
| sims | [N*(N-1)/2] | 45 pairs for N=10 |

### Pseudo-code

```
embeddings = embed_model.encode(responses)          # [N, 384]
sims = [cos_sim(embeddings[i], embeddings[j]) for i<j]
return mean(sims) if N >= 2 else nan
```

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | compute_consistency | Pairwise cosine sim over encoded responses |

---

## A-5: Orchestration + Checkpointing [Complexity: 3, Budget: 3]

**Applied:** Standard batch-with-checkpoint pattern

### API Signatures

```python
def process_question(
    question_id: str,
    question: str,
    model, tokenizer, embed_model,
    n_samples: int = 10,
) -> dict:
    """Full pipeline for one question.
    Returns: {'question_id', 'entropy', 'consistency', 'success', 'responses'}
    """
    ...

def run_pipeline(
    questions: list[dict],
    checkpoint_path: str = "h-e1/results.json",
    checkpoint_every: int = 100,
) -> list[dict]:
    """Batch loop over all questions with incremental JSON checkpointing."""
    ...
```

### Pseudo-code

```
results = load_checkpoint_if_exists(checkpoint_path)
done_ids = {r['question_id'] for r in results}
for idx, q in enumerate(questions):
    if q['question_id'] in done_ids: continue
    try:
        r = process_question(q['question_id'], q['question'], model, tokenizer, embed_model)
    except torch.cuda.OutOfMemoryError:
        torch.cuda.empty_cache()
        r = {'question_id': q['question_id'], 'entropy': nan, 'consistency': nan,
             'success': False, 'responses': []}
    results.append(r)
    if (idx + 1) % checkpoint_every == 0:
        save_json(results, checkpoint_path)
save_json(results, checkpoint_path)
return results
```

### Memory Optimization Notes

- Process **one question at a time** (not batched generation) — Llama-2-7B FP16 (~14GB) + activations leaves limited headroom on 24GB GPUs for batched multi-sample generation.
- Free `outputs.scores` (list of T `[1,V]` tensors) after entropy computation per sample — do not retain across questions.
- Call `torch.cuda.empty_cache()` after each OOM catch and optionally every N questions.
- Do not store raw logits in checkpoint JSON (per FR-5.2, `responses` field optional/text-only) — only scalar entropy/consistency persisted to keep `results.json` small (~500MB target for 11K questions).
- Embedding model (`all-MiniLM-L6-v2`, ~90MB) can stay resident on CPU or GPU; negligible memory relative to LLM.

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | process_question | Combine generation + entropy + consistency for 1 question |
| L-5-2 | run_pipeline | Checkpointed loop over ~11,313 questions |
| L-5-3 | evaluate_existence | Success rate + variance stats (per 02c evaluate_existence spec) |

---

## External Dependencies

None — H-E1 is the root hypothesis, no prior code to call.
