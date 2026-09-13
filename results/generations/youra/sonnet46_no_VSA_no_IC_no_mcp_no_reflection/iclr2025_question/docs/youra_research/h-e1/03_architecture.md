---
hypothesis: H-E1
type: EXISTENCE (PoC)
tier: LIGHT
date: 2026-08-31
author: yoon303@ust.ac.kr
---

# Architecture: H-E1 — SMC-NLI Existence Proof

Applied: SelfCheckGPT pairwise NLI inference-only pipeline pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing codebase to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; SelfCheckGPT (potsawee/selfcheckgpt) used as reference pattern only

---

## File Organization

```
code/
├── data_pipeline.py    # HaluEval download + stratified sampling
├── llm_sampler.py      # Llama-3-8B-Instruct N=10 sampling
├── scorer.py           # SMC-NLI + SMC-Embed scoring
├── evaluate.py         # AUROC, std check, visualization
├── config.py           # Fixed experiment config
└── run.py              # Entry point: verify → sample → score → eval
```

---

## Module Structure

### DataPipeline (`code/data_pipeline.py`)

**Dependencies**: requests, datasets, json, sklearn.model_selection

```python
def download_halueval(save_path: str = "data/halueval_qa_1000.json") -> list[dict]: ...
# Returns list of {"question": str, "label": int} dicts
# label: 0=correct, 1=hallucinated
# Stratified sample 500+500, seed=42
# Saves to data/halueval_qa_1000.json; skips download if file exists
```

---

### LLMSampler (`code/llm_sampler.py`)

**Dependencies**: transformers, torch

```python
class LLMSampler:
    def __init__(self, model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct", device: str = "auto"): ...
    def generate(self, question: str, n: int = 10) -> list[str]: ...
    # temperature=0.7, top_p=0.9, max_new_tokens=50

def sample_all(questions: list[dict], sampler: LLMSampler,
               save_path: str = "data/llama_samples.json") -> dict[int, list[str]]: ...
    # Returns {question_idx: [sample1, ..., sample10]}
    # Saves intermediate; resumes from existing file if present (skip re-inference)
```

---

### Scorer (`code/scorer.py`)

**Dependencies**: transformers, sentence_transformers, torch, numpy, itertools

```python
class SMCNLIScorer:
    def __init__(self, model_id: str = "cross-encoder/nli-deberta-v3-large", device: str = "cuda"): ...
    def score(self, question: str, samples: list[str], batch_size: int = 16) -> float: ...
    # Returns float in [0,1]: mean (P_ent + P_neut) over C(10,2)=45 pairs
    # Prepends "Q: {question} A: {answer}" to each sample

class SMCEmbedScorer:
    def __init__(self, model_id: str = "sentence-transformers/all-mpnet-base-v2"): ...
    def score(self, samples: list[str]) -> float: ...
    # Returns mean cosine similarity over 45 pairs

def score_all(questions: list[dict], samples: dict[int, list[str]],
              nli_scorer: SMCNLIScorer, embed_scorer: SMCEmbedScorer) -> list[dict]: ...
    # Returns [{question_idx, label, smc_nli, smc_embed}]
    # Logs per question: "SMC-NLI score for question {i}: {score:.4f} | Label: {label}"
```

---

### Evaluate (`code/evaluate.py`)

**Dependencies**: sklearn, numpy, matplotlib, json

```python
def compute_metrics(results: list[dict]) -> dict: ...
# Returns {smc_nli_auroc, smc_embed_auroc, smc_nli_std}

def save_results(results: list[dict], metrics: dict,
                 path: str = "results/h-e1/results.json") -> None: ...

def plot_figures(results: list[dict], metrics: dict,
                 fig_dir: str = "docs/youra_research/h-e1/figures/") -> None: ...
# 4 figures: bar chart (AUROCs), histogram (score dist by label), ROC curve, scatter
```

---

### Config (`code/config.py`)

```python
CFG = {
    "llm_model_id": "meta-llama/Meta-Llama-3-8B-Instruct",
    "nli_model_id": "cross-encoder/nli-deberta-v3-large",
    "embed_model_id": "sentence-transformers/all-mpnet-base-v2",
    "n_samples": 10,
    "temperature": 0.7,
    "top_p": 0.9,
    "max_new_tokens": 50,
    "nli_batch_size": 16,
    "n_questions": 1000,
    "seed": 42,
    "data_path": "data/halueval_qa_1000.json",
    "samples_path": "data/llama_samples.json",
    "results_path": "results/h-e1/results.json",
    "figures_dir": "docs/youra_research/h-e1/figures/",
}
```

---

### Runner (`code/run.py`)

**Dependencies**: all modules above

```python
def verify_mechanism(questions, sampler, nli_scorer, n=5) -> None: ...
# Assert max-min > 0.01, all in [0,1]; raise on fail

def main() -> None: ...
# 1. load config
# 2. download_halueval (skip if exists)
# 3. load LLMSampler, SMCNLIScorer, SMCEmbedScorer
# 4. verify_mechanism on first 5 questions
# 5. sample_all (skip if llama_samples.json exists)
# 6. score_all
# 7. compute_metrics + save_results
# 8. plot_figures
# 9. print gate result: PASS/FAIL
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown | Type |
|----|------|-------------|------------|-----------|------|
| E-1 | Data Pipeline | Download HaluEval, stratified sample 500+500, save JSON | 6 | 1+1+2+2 | data-pipeline |
| E-2 | LLM Sampler | Llama-3-8B-Instruct loader, N=10 sampling per question, intermediate save/resume | 10 | 3+2+2+3 | model |
| E-3 | SMC-NLI Scorer | DeBERTa cross-encoder pairwise scoring, 45 pairs, question-prepend, batched | 12 | 3+3+3+3 | model |
| E-4 | SMC-Embed Scorer | all-mpnet embeddings, mean pairwise cosine similarity | 6 | 2+1+2+1 | model |
| E-5 | Mechanism Verifier + Runner | Sanity check on 5 Qs, main pipeline orchestration, resume logic | 8 | 2+2+2+2 | infrastructure |
| E-6 | Evaluation + Visualization | AUROC, std check, 4 figures, results.json, gate print | 9 | 2+2+2+3 | evaluation |

**Distribution**: High(10-13): [E-3, E-2], Medium(7-9): [E-5, E-6], Low(4-6): [E-1, E-4]

---

## Data Flow

- `run.py` → `data_pipeline.py` → `data/halueval_qa_1000.json`
- `run.py` → `llm_sampler.py` → `data/llama_samples.json`
- `run.py` → `scorer.py` (reads samples JSON) → per-question scores list
- `run.py` → `evaluate.py` → `results/h-e1/results.json` + 4 figures

**Resume logic**: both `halueval_qa_1000.json` and `llama_samples.json` are checked before re-running expensive steps. Scorer always reruns (fast, ~6 min).
