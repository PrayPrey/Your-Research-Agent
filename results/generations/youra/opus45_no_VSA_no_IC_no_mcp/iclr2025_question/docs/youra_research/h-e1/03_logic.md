# Logic: H-E1 (EXISTENCE)

Applied: uncertainty-quantification-pipeline (Shannon entropy over softmax logits + pairwise embedding cosine consistency)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-3: Token Entropy [Complexity: 9, Budget: 3+2+3+1]

**Applied**: uncertainty-quantification-pipeline (greedy decode + per-token Shannon entropy)

### API Signatures

```python
def generate_greedy(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    question: str,
) -> tuple[str, torch.Tensor]:
    """Greedy-generate answer. Returns (text, logits [T, V])."""
    ...

def compute_token_entropy(logits: torch.Tensor) -> float:
    """Mean Shannon entropy over generated tokens. logits: [T, V] -> scalar."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| logits | [T, V] | T=generated tokens, V=vocab size |
| probs | [T, V] | softmax(logits, dim=-1) |
| token_entropy | [T] | -sum(probs * log(probs), dim=-1) |
| mean_entropy | scalar | token_entropy.mean().item() |

### Pseudo-code

```
1. output = model.generate(input_ids, do_sample=False, output_scores=True, return_dict_in_generate=True)
2. logits = stack(output.scores, dim=0)  # [T, V]
3. text = tokenizer.decode(output.sequences[0, input_len:], skip_special_tokens=True)
4. probs = softmax(logits, dim=-1)  # [T, V]
5. token_entropy = -(probs * log(probs + eps)).sum(dim=-1)  # [T]
6. return text, logits  # entropy computed separately via compute_token_entropy(logits)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | generate_greedy setup | Tokenize question, call model.generate with output_scores=True |
| L-3-2 | logits stacking | Stack per-step scores into [T, V] tensor, decode text |
| L-3-3 | compute_token_entropy | Softmax + Shannon entropy formula, mean-aggregate |
| L-3-4 | Edge case guard | Handle T=0 (empty generation) -> return 0.0 |

---

## A-4: N-Sample Consistency [Complexity: 9, Budget: 3+3+2+1]

**Applied**: uncertainty-quantification-pipeline (temperature sampling + sentence-embedding pairwise cosine)

### API Signatures

```python
def generate_n_samples(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    question: str,
    n: int,
    temperature: float,
) -> list[str]:
    """Sample n responses with temperature. Returns list of n decoded strings."""
    ...

def compute_consistency(
    responses: list[str],
    encoder: SentenceTransformer,
) -> float:
    """Mean pairwise cosine similarity across responses. -> scalar in [-1, 1]."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| embeddings | [N, D] | N=n_samples (5), D=384 (MiniLM-L6) |
| sim_matrix | [N, N] | cosine_similarity(embeddings, embeddings) |
| consistency | scalar | mean of upper-triangle (excl. diagonal) of sim_matrix |

### Pseudo-code

```
1. outputs = model.generate(input_ids, do_sample=True, temperature=T,
              num_return_sequences=n)
2. responses = [tokenizer.decode(seq[input_len:], skip_special_tokens=True) for seq in outputs]
3. embeddings = encoder.encode(responses, convert_to_tensor=True)  # [N, D]
4. sim_matrix = cosine_similarity(embeddings.unsqueeze(1), embeddings.unsqueeze(0), dim=-1)  # [N, N]
5. iu = triu_indices(N, k=1)
6. consistency = sim_matrix[iu].mean().item()
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | generate_n_samples | Sampling generate call with num_return_sequences=n, temperature |
| L-4-2 | Batch decode | Decode each of n sequences, strip prompt prefix |
| L-4-3 | compute_consistency | Encode with MiniLM, pairwise cosine, upper-triangle mean |
| L-4-4 | Edge case guard | Handle n=1 (undefined pairwise) -> return 1.0 |

---

## Out of Budget (Reference Only, No Subtasks Allocated)

A-1, A-2, A-5, A-6, A-7, A-8 signatures already fixed in `03_architecture.md` (Low/Medium complexity, no additional breakdown needed here per task allocation).
