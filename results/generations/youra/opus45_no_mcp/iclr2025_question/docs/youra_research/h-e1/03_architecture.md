# Architecture: H-E1 (EXISTENCE)

**Applied**: Standard sampling-loop + metrics-postprocess pattern for LLM uncertainty estimation.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

## Hypothesis

Under QA task conditions with Llama-2-7B-chat, generating multiple responses per question with logit access allows computing token entropy and semantic consistency for every response.

## System Components

```
data/triviaqa_val.jsonl
        |
        v
[load_data.py] -> list[{question, answer}]
        |
        v
[generate.py] --uses--> Llama-2-7B-chat (HF transformers)
        | produces: 10 responses/question, output_scores=True
        v
responses.jsonl (question_id, response_id, text, token_logits)
        |
        +--> [entropy.py]      -> token_entropy per response
        +--> [consistency.py]  -> semantic_consistency per question (SentenceTransformer)
        |
        v
[checkpoint.py] -> periodic save/resume
        |
        v
results/h-e1_results.jsonl (final merged metrics)
```

Data flow: dataset -> generation (batched, checkpointed) -> raw responses+logits stored -> entropy computed from stored logits -> consistency computed from embeddings of response texts -> merged into final results file.

---

## Modules

### DataLoader (`h-e1/code/load_data.py`)

**Dependencies**: none (uses `datasets` lib)

```python
def load_triviaqa_val(limit: int | None = None) -> list[dict]: ...
# returns [{"qid": str, "question": str, "answer": str}, ...]
```

### Generator (`h-e1/code/generate.py`)

**Dependencies**: DataLoader, transformers, torch

```python
class ResponseGenerator:
    def __init__(self, model_name: str = "meta-llama/Llama-2-7b-chat-hf",
                 temperature: float = 0.7, max_new_tokens: int = 128,
                 num_responses: int = 10): ...
    def generate(self, question: str) -> list[dict]: ...
    # each dict: {"text": str, "token_ids": list[int], "logits": list[Tensor]}
```

### EntropyCalculator (`h-e1/code/entropy.py`)

**Dependencies**: torch

```python
def token_entropy(logits: list[Tensor]) -> list[float]: ...
def mean_response_entropy(logits: list[Tensor]) -> float: ...
```

### ConsistencyCalculator (`h-e1/code/consistency.py`)

**Dependencies**: sentence-transformers

```python
class SemanticConsistency:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"): ...
    def compute(self, responses: list[str]) -> float: ...
    # returns mean pairwise cosine similarity across N responses
```

### CheckpointManager (`h-e1/code/checkpoint.py`)

**Dependencies**: none (stdlib json/os)

```python
class CheckpointManager:
    def __init__(self, path: str, save_every: int = 50): ...
    def load(self) -> dict: ...          # {"last_qid_idx": int, "results": list}
    def save(self, idx: int, results: list): ...
```

### Pipeline (`h-e1/code/run_pipeline.py`)

**Dependencies**: all above

```python
def run(limit: int = 11313) -> None: ...
# orchestrates: load -> generate -> entropy -> consistency -> checkpoint -> write results
```

### Config (`h-e1/code/config.py`)

```python
MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"
NUM_RESPONSES = 10
TEMPERATURE = 0.7
MAX_NEW_TOKENS = 128
SBERT_MODEL = "all-MiniLM-L6-v2"
CHECKPOINT_PATH = "results/checkpoint.json"
OUTPUT_PATH = "results/h-e1_results.jsonl"
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Config | Fixed config module | 3 | 1+1+1+0 |
| E-2 | Data loading | Load TriviaQA val split | 5 | 2+2+1+0 |
| E-3 | Model setup | Load Llama-2-7B-chat, tokenizer, device | 8 | 3+2+2+1 |
| E-4 | Generation loop | Sample 10 responses/question w/ output_scores | 12 | 4+3+3+2 |
| E-5 | Entropy calc | Softmax logits -> per-token entropy | 8 | 3+2+2+1 |
| E-6 | Consistency calc | SentenceTransformer embed + cosine sim | 8 | 3+2+2+1 |
| E-7 | Checkpointing | Save/resume every N questions | 6 | 2+2+1+1 |
| E-8 | Pipeline + smoke test | Wire together, run on small subset, verify outputs | 10 | 3+3+2+2 |

**Total tasks**: 8 (within LIGHT tier max 15, epics 4-8 satisfied)

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [E-4, E-8], Low(4-8): [E-2, E-3, E-5, E-6, E-7], VeryLow(1-3): [E-1]

---

## Notes

- No training pipeline — inference-only, existence test.
- No ablations, no baseline-vs-proposed split — single generation+metrics path.
- Checkpointing at question granularity to survive interruption over 11,313 questions x 10 responses.
