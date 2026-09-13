# Logic Design: H-E1 Semantic Entropy UQ Comparison (EXISTENCE PoC)

**Hypothesis:** H-E1 | **Type:** EXISTENCE | **Tier:** LIGHT
**Budget:** 7 subtasks (A-3: 4, A-2: 3)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-3: UQ Signal Computation [Complexity: 17, Budget: 4 subtasks]

Applied: Semantic-Entropy-NLI-Clustering pattern (Kuhn 2023, arXiv:2302.09664)

### L-A3-1: Semantic Entropy NLI Clustering

#### API Signatures

```python
def load_nli_pipeline(cfg: ExperimentConfig):
    """Load deberta-large-mnli pipeline on CUDA."""
    # Returns: transformers.Pipeline

def cluster_by_nli(
    samples: List[str],       # N=5 stochastic samples
    nli_pipeline,             # HuggingFace text-classification pipeline
    batch_size: int = 16,
) -> Dict[int, int]:
    """Bidirectional NLI entailment clustering (Kuhn 2023).
    Returns {sample_idx: cluster_id}, cluster_id in [0, N-1].
    """

def compute_semantic_entropy(
    samples: List[str],       # N=5 stochastic samples
    nli_pipeline,
    batch_size: int = 16,
) -> float:
    """Shannon entropy over NLI cluster frequency distribution. Returns scalar >= 0."""
```

#### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| nli_inputs (batch) | [B, 2] strings | premise-hypothesis pairs |
| nli_logits | [B, 3] | entail/neutral/contradict |
| cluster_ids | [N] int | cluster assignment per sample |
| cluster_probs | [K] float | freq/N, K = num unique clusters |

#### Pseudo-code: `cluster_by_nli`

```
# Build all ordered pairs (i, j), i != j → N*(N-1) pairs = 20 for N=5
pairs = [(samples[i], samples[j]) for i in range(N) for j in range(N) if i != j]

# Batch NLI inference
results = nli_pipeline(pairs, batch_size=batch_size)
# results[k]['label'] in {"ENTAILMENT", "NEUTRAL", "CONTRADICTION"}

# Build entailment matrix E[i,j] = 1 if both (i→j) and (j→i) are ENTAILMENT
E = zeros(N, N)
for k, (i, j) in enumerate(ordered_pairs):
    if results[k]['label'] == "ENTAILMENT":
        E[i][j] = 1

bidirectional[i][j] = E[i][j] AND E[j][i]

# Union-Find clustering: merge i,j if bidirectional[i][j]
cluster_ids = union_find_clusters(bidirectional)  # {sample_idx: cluster_id}
return cluster_ids
```

#### Pseudo-code: `compute_semantic_entropy`

```
cluster_ids = cluster_by_nli(samples, nli_pipeline, batch_size)
counts = Counter(cluster_ids.values())       # {cluster_id: count}
probs = [c / N for c in counts.values()]     # [K] normalized frequencies
H = -sum(p * log(p + 1e-9) for p in probs)  # Shannon entropy, scalar
return H
```

---

### L-A3-2: Token Entropy Mean

Applied: Numerically-Stable-Entropy pattern (log-sum-exp base)

#### API Signatures

```python
def compute_token_entropy_mean(
    logits: torch.Tensor,   # [seq_len, vocab_size] float16 or float32
) -> float:
    """Mean Shannon entropy over per-token distributions.
    H_mean = mean over t of: -sum_v( p_tv * log(p_tv + 1e-9) )
    Returns scalar float.
    """

def compute_all_token_entropy(
    outputs_dir: str,
    cfg: ExperimentConfig,
) -> Dict[int, float]:
    """Loads outputs/greedy_logits/example_{id}.pt per example.
    Returns {example_id: token_entropy_mean_float}.
    Saves to outputs/uq_scores/token_entropy_mean.json.
    """
```

#### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| logits | [seq_len, vocab_size] | raw logits from stacked scores |
| probs | [seq_len, vocab_size] | softmax(logits, dim=-1) |
| token_H | [seq_len] | per-token entropy values |
| output | scalar float | mean(token_H) |

#### Pseudo-code

```
probs = softmax(logits.float(), dim=-1)          # [seq_len, vocab_size]
token_H = -sum(probs * log(probs + 1e-9), dim=-1)  # [seq_len]
return token_H.mean().item()                     # scalar
```

---

### L-A3-3: SelfCheckGPT-BERTScore Integration

Applied: SelfCheckGPT-BERTScore pattern (Manakul 2023, arXiv:2303.08896)

#### API Signatures

```python
def compute_selfcheckgpt_bertscore(
    greedy_response: str,           # single greedy response text
    stochastic_samples: List[str],  # N=5 sample strings
) -> float:
    """Segment greedy into sentences, score each vs stochastic_samples.
    Returns mean inconsistency score (higher = more hallucinated).
    Uses SelfCheckBERTScore(rescale_with_baseline=True).
    """

def compute_all_selfcheckgpt(
    outputs_dir: str,
    cfg: ExperimentConfig,
) -> Dict[int, float]:
    """Loads greedy_responses.jsonl + stochastic_samples.jsonl.
    Computes selfcheckgpt_bertscore per example.
    Saves to outputs/uq_scores/selfcheckgpt_bertscore_n5.json.
    Returns {example_id: float}.
    """
```

#### Pseudo-code

```
from selfcheckgpt.modeling_selfcheck import SelfCheckBERTScore
import nltk

checker = SelfCheckBERTScore(rescale_with_baseline=True)

sentences = nltk.sent_tokenize(greedy_response)    # List[str], K sentences
if len(sentences) == 0:
    return 0.0

# scores: [K] float, inconsistency per sentence
scores = checker.predict(
    sentences=sentences,
    sampled_passages=stochastic_samples,  # List[str], N=5
)
return float(np.mean(scores))             # scalar
```

---

### L-A3-4: Batched NLI Inference Optimization

Applied: HuggingFace-Pipeline-Batching pattern

#### API Signatures

```python
def _build_nli_pairs(samples: List[str]) -> List[Dict[str, str]]:
    """Build all ordered (i,j) premise-hypothesis pairs for N samples.
    Returns N*(N-1) dicts: [{'text': premise, 'text_pair': hypothesis}, ...]
    For N=5: returns 20 pairs.
    """

def _run_nli_batch(
    pairs: List[Dict[str, str]],
    nli_pipeline,
    batch_size: int = 16,
) -> List[Dict[str, Any]]:
    """Run NLI pipeline over pairs with batching.
    Returns list of {'label': str, 'score': float} dicts.
    Handles GPU OOM gracefully by halving batch_size once.
    """
```

#### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| pairs | [N*(N-1)] dicts | N=5 → 20 pairs |
| nli_outputs | [N*(N-1)] dicts | label + score per pair |
| E matrix | [N, N] bool | bidirectional entailment |

#### Notes

- N=5 → 20 pairs per example, fits in batch_size=16 in 2 forward passes
- pipeline truncation: max_length=512 (DeBERTa limit), truncation=True
- Cast logits to float32 before softmax to avoid fp16 overflow

---

## A-2: LLM Inference [Complexity: 14, Budget: 3 subtasks]

Applied: HuggingFace-Generate-with-Scores pattern

### L-A2-1: Greedy Inference with Logit Capture

#### API Signatures

```python
def load_llm(cfg: ExperimentConfig) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Load LLaMA-2-7B-chat in cfg.llm_dtype on CUDA. Returns (model, tokenizer)."""

def _build_prompt(question: str, answer: str) -> str:
    """Format question+answer into LLaMA-2 chat prompt template. Returns str."""

def run_greedy_inference(
    examples: List[Dict[str, Any]],   # list of {id, question, answer, hallucination_label}
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    cfg: ExperimentConfig,
    resume: bool = True,
) -> None:
    """Per-example greedy inference with logit capture.
    Saves:
      outputs/greedy_responses.jsonl  — one JSON line per example
      outputs/greedy_logits/example_{id}.pt  — stacked logit tensor
    Skips already-saved examples when resume=True.
    """
```

#### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, prompt_len] | single example, batch=1 |
| output.sequences | [1, prompt_len + seq_len] | generated tokens |
| output.scores | tuple of seq_len tensors | each [1, vocab_size] |
| stacked_logits | [seq_len, vocab_size] | saved as .pt file |

#### Pseudo-code

```
for example in examples:
    if resume and logit_file_exists(example['id']):
        continue

    prompt = _build_prompt(example['question'], example['answer'])
    input_ids = tokenizer(prompt, return_tensors='pt').input_ids.cuda()  # [1, L]

    with torch.no_grad():
        output = model.generate(
            input_ids,
            max_new_tokens=cfg.max_new_tokens,
            do_sample=False,
            temperature=None,        # greedy
            output_scores=True,
            return_dict_in_generate=True,
        )

    # Stack scores: tuple(seq_len × [1, vocab]) → [seq_len, vocab]
    logits = torch.stack(output.scores, dim=0).squeeze(1)   # [seq_len, vocab_size]

    response_ids = output.sequences[0, input_ids.shape[1]:]
    response_text = tokenizer.decode(response_ids, skip_special_tokens=True)

    # Persist
    torch.save(logits.cpu().half(), f"outputs/greedy_logits/example_{example['id']}.pt")
    append_jsonl({"id": example['id'], "response": response_text}, "outputs/greedy_responses.jsonl")
```

---

### L-A2-2: Stochastic Sampling (N=5)

Applied: Multi-Sample-Generation pattern

#### API Signatures

```python
def run_stochastic_inference(
    examples: List[Dict[str, Any]],
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    cfg: ExperimentConfig,             # cfg.n_stochastic_samples=5, cfg.stochastic_temperature=1.0
    resume: bool = True,
) -> None:
    """Per-example: N=5 independent samples with temperature=1.0, do_sample=True.
    Saves outputs/stochastic_samples.jsonl — one JSON line per example:
      {"id": int, "samples": List[str]}
    Skips already-saved examples when resume=True.
    """
```

#### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, prompt_len] | single example |
| output.sequences | [N, prompt_len + seq_len] | N independent samples |

#### Pseudo-code

```
for example in examples:
    if resume and example_in_jsonl(example['id'], "outputs/stochastic_samples.jsonl"):
        continue

    prompt = _build_prompt(example['question'], example['answer'])
    input_ids = tokenizer(prompt, return_tensors='pt').input_ids.cuda()  # [1, L]

    with torch.no_grad():
        output = model.generate(
            input_ids.expand(cfg.n_stochastic_samples, -1),  # [N, L]
            max_new_tokens=cfg.max_new_tokens,
            do_sample=True,
            temperature=cfg.stochastic_temperature,           # 1.0
        )

    # Decode N samples
    gen_ids = output[:, input_ids.shape[1]:]                 # [N, seq_len]
    samples = [tokenizer.decode(gen_ids[i], skip_special_tokens=True)
               for i in range(cfg.n_stochastic_samples)]

    append_jsonl({"id": example['id'], "samples": samples}, "outputs/stochastic_samples.jsonl")
```

---

### L-A2-3: Checkpoint-Resume Pattern

Applied: JSONL-Append-Checkpoint-Resume pattern

#### API Signatures

```python
def _get_completed_ids_jsonl(filepath: str) -> Set[int]:
    """Read JSONL file, return set of already-completed example IDs.
    Returns empty set if file does not exist.
    """

def _get_completed_ids_logits(logits_dir: str) -> Set[int]:
    """Scan outputs/greedy_logits/ for example_{id}.pt files.
    Returns set of int IDs already saved.
    """

def append_jsonl(record: Dict[str, Any], filepath: str) -> None:
    """Append single JSON record as one line to filepath (create if missing)."""

def load_greedy_outputs(outputs_dir: str) -> Dict[int, Dict[str, Any]]:
    """Read greedy_responses.jsonl → {id: {response: str}}."""

def load_stochastic_outputs(outputs_dir: str) -> Dict[int, List[str]]:
    """Read stochastic_samples.jsonl → {id: [sample_0, ..., sample_4]}."""
```

#### Pseudo-code: Resume Logic

```
# In run_greedy_inference:
completed = _get_completed_ids_logits(f"{cfg.outputs_dir}/greedy_logits/")
for example in examples:
    if example['id'] in completed:
        continue
    # ... run inference and save ...

# In run_stochastic_inference:
completed = _get_completed_ids_jsonl(f"{cfg.outputs_dir}/stochastic_samples.jsonl")
for example in examples:
    if example['id'] in completed:
        continue
    # ... run inference and save ...
```

---

## Subtask Summary

| ID | Subtask | Description |
|----|---------|-------------|
| L-A3-1 | NLI Clustering + SE | cluster_by_nli (union-find, bidirectional), compute_semantic_entropy |
| L-A3-2 | Token Entropy Mean | compute_token_entropy_mean with fp16→float32 cast, log(p+1e-9) stability |
| L-A3-3 | SelfCheckGPT Integration | sentence segmentation, SelfCheckBERTScore.predict, mean aggregation |
| L-A3-4 | Batched NLI Optimization | _build_nli_pairs, _run_nli_batch, 20-pair batching for N=5 |
| L-A2-1 | Greedy + Logit Capture | generate(output_scores=True), stack scores → [seq_len, vocab_size] .pt |
| L-A2-2 | Stochastic Sampling | expand input to [N, L], do_sample=True, temperature=1.0, decode N texts |
| L-A2-3 | Checkpoint-Resume | JSONL append, ID-set scan for skip logic, load helpers |

**Total:** 7 subtasks [7/7 used]
