---
hypothesis: H-E1
type: EXISTENCE (PoC)
date: 2026-08-31
author: yoon303@ust.ac.kr
budget: 7 subtasks (Logic Agent)
---

# Logic Design: H-E1 — SMC-NLI Inference Pipeline

Applied: HuggingFace cross-encoder pairwise inference pattern (SelfCheckGPT NLI variant)
Applied: Intermediate-save/resume pattern for long inference loops
Applied: Question-prepend OOD mitigation (SAC3 / SINdex)

---

## Codebase Analysis (Serena)

Green-field project — no existing codebase to analyze. Serena MCP skipped.
All API designs derived from Phase 2C experiment brief and SelfCheckGPT reference implementation.

---

## Module: SMC-NLI Scorer (`code/scorer.py`)

### L-3-1: `SMCNLIScorer.__init__`

```python
def __init__(
    self,
    model_id: str = "cross-encoder/nli-deberta-v3-large",
    device: str = "cuda",
    batch_size: int = 16,
    max_length: int = 512,
) -> None:
```

| Arg | Type | Description |
|-----|------|-------------|
| model_id | str | HuggingFace model ID for NLI cross-encoder |
| device | str | torch device string ("cuda" or "cpu") |
| batch_size | int | Pairs per NLI batch (default 16, fits 16GB VRAM) |
| max_length | int | Max token length for truncation |

**Implementation notes:**
- Label mapping: `{contradiction: 0, entailment: 1, neutral: 2}` — fixed for `cross-encoder/nli-deberta-v3-large`
- Load with `AutoModelForSequenceClassification.from_pretrained(model_id).to(device).eval()`
- Store tokenizer separately: `AutoTokenizer.from_pretrained(model_id)`

### L-3-2: `SMCNLIScorer.score_pairs`

```python
def score_pairs(
    self,
    premises: list[str],
    hypotheses: list[str],
) -> np.ndarray:
```

| Arg | Type | Description |
|-----|------|-------------|
| premises | list[str] | Left-side texts for NLI (length = num_pairs) |
| hypotheses | list[str] | Right-side texts for NLI (length = num_pairs) |

**Returns:** `np.ndarray` shape `(num_pairs,)` — P(entailment) + P(neutral) per pair, values in [0, 1]

**Tensor shapes:**
- Tokenizer output: `input_ids` shape `[batch_size, seq_len]`, `attention_mask` shape `[batch_size, seq_len]`
- Model logits: `[batch_size, 3]` (contradiction=0, entailment=1, neutral=2)
- Softmax probabilities: `[batch_size, 3]`
- Extracted: `probs[:, 1] + probs[:, 2]` → shape `[batch_size]`

**Pseudo-code:**
```python
scores = []
for k in range(0, len(premises), self.batch_size):
    batch_p = premises[k : k + self.batch_size]
    batch_h = hypotheses[k : k + self.batch_size]
    enc = self.tokenizer(
        batch_p, batch_h,
        return_tensors="pt", truncation=True,
        max_length=self.max_length, padding=True
    ).to(self.device)
    with torch.no_grad():
        logits = self.model(**enc).logits          # [B, 3]
    probs = torch.softmax(logits, dim=-1)          # [B, 3]
    ent_neut = (probs[:, 1] + probs[:, 2]).cpu().numpy()  # [B]
    scores.extend(ent_neut.tolist())
return np.array(scores)                            # [num_pairs]
```

### L-3-3: `SMCNLIScorer.score_question`

```python
def score_question(
    self,
    question: str,
    samples: list[str],
) -> float:
```

| Arg | Type | Description |
|-----|------|-------------|
| question | str | The factual QA question (prepended to each answer) |
| samples | list[str] | N=10 generated answers from LLM |

**Returns:** `float` — SMC-NLI score in [0, 1]; higher = more consistent

**Tensor shapes:** N/A (scalar output); internally uses `score_pairs` shapes above

**Pseudo-code:**
```python
# OOD mitigation: prepend question to each answer
prefixed = [f"Q: {question} A: {s}" for s in samples]
# Generate all C(N,2) = 45 pairs
pairs = list(itertools.combinations(range(len(prefixed)), 2))
premises  = [prefixed[i] for i, j in pairs]   # len=45
hypotheses = [prefixed[j] for i, j in pairs]  # len=45
pair_scores = self.score_pairs(premises, hypotheses)  # [45]
return float(np.mean(pair_scores))             # scalar SMC-NLI
```

### L-3-4: `SMCNLIScorer.score_all`

```python
def score_all(
    self,
    questions: list[str],
    all_samples: list[list[str]],
    save_path: str,
    resume: bool = True,
) -> list[float]:
```

| Arg | Type | Description |
|-----|------|-------------|
| questions | list[str] | All 1000 questions |
| all_samples | list[list[str]] | N=10 samples per question, shape (1000, 10) |
| save_path | str | Path to save intermediate scores JSON |
| resume | bool | If True and save_path exists, skip already-scored questions |

**Returns:** `list[float]` — SMC-NLI score per question, length = 1000

**Pseudo-code:**
```python
scores = {}
if resume and os.path.exists(save_path):
    scores = json.load(open(save_path))
for i, (q, samps) in enumerate(zip(questions, all_samples)):
    if str(i) in scores:
        continue
    smc = self.score_question(q, samps)
    scores[str(i)] = smc
    print(f"SMC-NLI score for question {i}: {smc:.4f} | Label: {labels[i]}")
    if i % 50 == 0:
        json.dump(scores, open(save_path, "w"))
json.dump(scores, open(save_path, "w"))
return [scores[str(i)] for i in range(len(questions))]
```

---

## Module: LLM Sampler (`code/llm_sampler.py`)

### L-2-1: `LLMSampler.__init__` + `load_model`

```python
def __init__(
    self,
    model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct",
    torch_dtype: torch.dtype = torch.float16,
    device_map: str = "auto",
) -> None:
```

| Arg | Type | Description |
|-----|------|-------------|
| model_id | str | HuggingFace model ID |
| torch_dtype | torch.dtype | float16 for memory efficiency |
| device_map | str | "auto" for single-GPU placement |

**Implementation notes:**
- `AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch_dtype, device_map=device_map)`
- `AutoTokenizer.from_pretrained(model_id)` — set `padding_side="left"` for batch generation
- Call `.eval()` after loading

### L-2-2: `LLMSampler.sample` + `LLMSampler.sample_all`

```python
def sample(
    self,
    question: str,
    n: int = 10,
    temperature: float = 0.7,
    top_p: float = 0.9,
    max_new_tokens: int = 50,
) -> list[str]:
```

**Returns:** `list[str]` — N decoded answer strings (stripped of prompt prefix)

**Tensor shapes:**
- Input `input_ids`: `[1, prompt_len]`
- Output `sequences`: `[n, prompt_len + max_new_tokens]` (with `num_return_sequences=n`)
- Decoded: `n` strings after slicing `sequences[:, prompt_len:]`

**Pseudo-code:**
```python
messages = [{"role": "user", "content": f"Answer in one short phrase: {question}"}]
prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
with torch.no_grad():
    out = self.model.generate(
        **inputs,
        do_sample=True,
        temperature=temperature,
        top_p=top_p,
        max_new_tokens=max_new_tokens,
        num_return_sequences=n,
    )
prompt_len = inputs["input_ids"].shape[1]
return [self.tokenizer.decode(out[i, prompt_len:], skip_special_tokens=True).strip()
        for i in range(n)]
```

```python
def sample_all(
    self,
    questions: list[str],
    save_path: str,
    resume: bool = True,
    **kwargs,
) -> list[list[str]]:
```

**Returns:** `list[list[str]]` — shape `(num_questions, N)`, intermediate-saved to `save_path`

**Pseudo-code:**
```python
all_samples = {}
if resume and os.path.exists(save_path):
    all_samples = json.load(open(save_path))
for i, q in enumerate(questions):
    if str(i) in all_samples:
        continue
    all_samples[str(i)] = self.sample(q, **kwargs)
    if i % 100 == 0:
        json.dump(all_samples, open(save_path, "w"))
json.dump(all_samples, open(save_path, "w"))
return [all_samples[str(i)] for i in range(len(questions))]
```

---

## Module: Mechanism Verifier (`code/run.py`)

### L-5-1: `verify_mechanism`

```python
def verify_mechanism(
    sampler: LLMSampler,
    scorer: SMCNLIScorer,
    sample_questions: list[dict],
    n: int = 10,
) -> None:
```

| Arg | Type | Description |
|-----|------|-------------|
| sampler | LLMSampler | Initialized LLM sampler |
| scorer | SMCNLIScorer | Initialized NLI scorer |
| sample_questions | list[dict] | First 5 questions with "question" and "label" keys |
| n | int | Number of samples per question |

**Returns:** None (raises AssertionError on failure)

**Pseudo-code:**
```python
scores = []
for q_data in sample_questions[:5]:
    samps = sampler.sample(q_data["question"], n=n)
    smc = scorer.score_question(q_data["question"], samps)
    scores.append(smc)
    print(f"Q: {q_data['question'][:50]} | SMC-NLI: {smc:.4f} | Label: {q_data['label']}")
assert max(scores) - min(scores) > 0.01, "FAIL: SMC-NLI scores degenerate (no variation)"
assert 0.0 <= min(scores) <= max(scores) <= 1.0, "FAIL: SMC-NLI scores out of [0,1]"
print("✅ Mechanism verification PASSED")
```

---

## Subtask Summary

| ID | Parent Epic | Description | Agent |
|----|-------------|-------------|-------|
| L-3-1 | E-3 (NLI Scorer) | `__init__`: model loading, device, label map | Logic |
| L-3-2 | E-3 (NLI Scorer) | `score_pairs`: batched NLI → P(ent+neut) | Logic |
| L-3-3 | E-3 (NLI Scorer) | `score_question`: pair gen, prepend, aggregate | Logic |
| L-3-4 | E-3 (NLI Scorer) | `score_all`: full loop, save/resume | Logic |
| L-2-1 | E-2 (LLM Sampler) | `__init__` + `load_model`: HF loading | Logic |
| L-2-2 | E-2 (LLM Sampler) | `sample` + `sample_all`: generation, save/resume | Logic |
| L-5-1 | E-5 (Verifier) | `verify_mechanism`: 5-question sanity check | Logic |
