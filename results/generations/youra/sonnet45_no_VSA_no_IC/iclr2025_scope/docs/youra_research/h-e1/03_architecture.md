# Architecture Document: H-E1 Attention-Retrieval Correlation

**Hypothesis ID**: h-e1  
**Type**: EXISTENCE (PoC validation)  
**Date**: 2026-08-20  
**Applied Patterns**: PyTorch hooks, dual-retrieval validation

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: No existing code to analyze  
**Findings**: New implementation from scratch (correlation analysis experiment)

---

## System Overview

Validate Spearman ρ > 0.3 between retrieval scores (BM25, Contriever) and LLM attention weights during RAG-based QA. Five module pipeline: data prep → retrieval → attention extraction → correlation → reporting.

---

## Module Structure

### DataPrep (`data/dataset.py`)

**Dependencies**: None

```python
class LongBenchLoader:
    def __init__(self, tasks: list[str]): ...
    def load_raw(self) -> list[dict]: ...
    def segment_passages(self, context: str) -> list[str]: ...
    def label_query_complexity(self, question: str) -> str: ...  # "simple" | "complex"
```

---

### Retrieval (`retrieval/scorer.py`)

**Dependencies**: DataPrep

```python
class BM25Scorer:
    def __init__(self, k1: float = 1.5, b: float = 0.75): ...
    def index_passages(self, passages: list[str]): ...
    def score(self, question: str) -> np.ndarray: ...  # (num_passages,)

class ContrieverScorer:
    def __init__(self, model_name: str = "facebook/contriever-msmarco"): ...
    def encode_batch(self, texts: list[str]) -> torch.Tensor: ...
    def score(self, question: str, passages: list[str]) -> np.ndarray: ...
```

---

### AttentionExtractor (`model/attention.py`)

**Dependencies**: None

```python
class AttentionCollector:
    def __init__(self): ...
    def hook_fn(self, module, input, output): ...  # Store attention weights
    def get_passage_attention(self, passage_boundaries: list[tuple]) -> np.ndarray: ...
    def clear(self): ...

class LlamaQA:
    def __init__(self, model_name: str = "meta-llama/Llama-2-7b-chat-hf"): ...
    def install_hooks(self, collector: AttentionCollector): ...
    def generate(self, question: str, passages: list[str]) -> tuple[str, np.ndarray]: ...
```

---

### Correlator (`analysis/correlation.py`)

**Dependencies**: AttentionExtractor, Retrieval

```python
class SpearmanAnalyzer:
    def __init__(self): ...
    def compute_rho(self, retrieval_scores: np.ndarray, attention: np.ndarray) -> tuple[float, float]: ...
    def stratify(self, results: list[dict], dimension: str) -> dict: ...
    def bootstrap_ci(self, rho_values: list[float], n_samples: int = 1000) -> tuple[float, float]: ...

class BaselineComputer:
    def random_baseline(self, retrieval_scores: np.ndarray, attention: np.ndarray) -> float: ...
    def position_bias(self, attention: np.ndarray) -> float: ...
```

---

### Reporter (`analysis/report.py`)

**Dependencies**: Correlator

```python
class ValidationReporter:
    def __init__(self, output_dir: str): ...
    def plot_scatter(self, scores: np.ndarray, attention: np.ndarray, title: str): ...
    def compute_statistics(self, correlations: list[dict]) -> dict: ...
    def gate_decision(self, mean_rho_bm25: float, mean_rho_contriever: float) -> str: ...  # "PASS" | "FAIL"
    def write_report(self, results: dict): ...
```

---

## Data Flow

1. **Load**: LongBenchLoader → 600 questions + passages
2. **Retrieve**: BM25Scorer + ContrieverScorer → (600, num_passages, 2) scores
3. **Extract**: LlamaQA + AttentionCollector → (600, num_passages) attention
4. **Analyze**: SpearmanAnalyzer → per-question ρ, stratified analysis
5. **Report**: ValidationReporter → 02d_validation_h-e1.md + gate decision

---

## Storage Strategy

```
h-e1/
├── data/
│   ├── preprocessed_longbench.pkl         # 600 questions (100MB)
│   ├── bm25_scores.npy                    # (600, max_passages)
│   └── contriever_scores.npy              # (600, max_passages)
├── outputs/
│   ├── attentions/                        # question_{id}.npy (3GB total)
│   ├── answers/                           # question_{id}.txt
│   └── results/
│       ├── per_question_correlations.csv
│       ├── summary_statistics.json
│       └── plots/                         # scatter_bm25.png, scatter_contriever.png
└── 02d_validation_h-e1.md                 # Final report
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1 | Data Pipeline | Download LongBench, segment passages, label complexity | 8 | 2+2+2+2 (load+segment+label+cache) |
| E2 | Dual Retrieval | Implement BM25 + Contriever scoring | 10 | 3+3+2+2 (BM25+Contriever+index+validate) |
| E3 | Attention Extraction | Llama-2-7B hooks, token→passage mapping | 12 | 3+3+3+3 (model+hook+aggregate+map) |
| E4 | Correlation Analysis | Spearman ρ, stratification, bootstrap CI | 11 | 3+3+3+2 (compute+stratify+CI+baselines) |
| E5 | Validation Report | Plots, statistics, gate decision | 9 | 3+3+3 (plots+stats+report) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [E2,E3,E4,E5], Low(4-8): [E1]

**Total Complexity**: 50 (5 epics, Tier 2 implementation)

---

## Configuration

### Model Config (`config/model.yaml`)
```yaml
model_name: meta-llama/Llama-2-7b-chat-hf
device: cuda
dtype: float16
generation:
  max_new_tokens: 128
  temperature: 0.7
  top_p: 0.9
  do_sample: false
  output_attentions: true
attention:
  target_layer: -1  # Last decoder layer
  aggregation: mean_heads_sum_tokens
```

### Retrieval Config (`config/retrieval.yaml`)
```yaml
bm25:
  k1: 1.5
  b: 0.75
  top_k: 10
contriever:
  model: facebook/contriever-msmarco
  max_length: 512
  batch_size: 64
  top_k: 10
```

### Dataset Config (`config/dataset.yaml`)
```yaml
tasks: [hotpotqa, 2wikimqa, musique]
samples_per_task: 200
total_samples: 600
complexity_thresholds:
  simple_word_count: 10
  simple_entity_density: 0.3
```

---

## Validation Checklist

### Data Quality
- [ ] Passage count per question: 10-30 range
- [ ] BM25 scores > 0
- [ ] Contriever scores in [-1, 1]
- [ ] No missing fields (question, context, answers)

### Attention Extraction
- [ ] Attention shape: (num_generated_tokens, num_heads, seq_len, seq_len)
- [ ] Non-zero attention weights
- [ ] Passage boundaries match tokenization
- [ ] Uniform attention baseline → ρ ≈ 0

### Statistical Rigor
- [ ] 600 samples processed (100% coverage)
- [ ] Bootstrap CI computed (1000 resamples)
- [ ] p-values < 0.05 for observed ρ
- [ ] Random baseline ρ ≈ 0

### Gate Decision
- [ ] Mean ρ_BM25 > 0.3
- [ ] Mean ρ_Contriever > 0.3
- [ ] No negative correlation in subgroups
- [ ] Validation report written to 02d_validation_h-e1.md

---

## Risk Mitigation

**Risk**: Correlation below threshold (ρ ≤ 0.3)  
**Mitigation**: Dual-retriever validation (BM25 + Contriever)  
**Fallback**: If only Contriever succeeds → pivot to semantic-only metadata

**Risk**: Attention extraction bugs  
**Mitigation**: Unit tests (shape verification), uniform baseline (ρ ≈ 0)  
**Fallback**: Use `output_attentions=True` direct output

**Risk**: Passage parsing errors  
**Mitigation**: Manual inspection (10 samples), cross-check LongBench source  
**Fallback**: Character-based boundaries (500-char windows)

---

## Success Criteria

**Primary**: Spearman ρ > 0.3 for both BM25 and Contriever (p < 0.05)  
**Secondary**: Simple queries show higher query-token attention (t-test p < 0.05)  
**Failure**: ρ ≤ 0.3 for either retriever → Phase 0 routing

---

## Compute Budget

- **GPU**: 1x A100 40GB
- **Model Memory**: ~14GB (Llama-2-7B FP16)
- **Attention Storage**: ~3GB (600 questions)
- **Time**: 2.5 hours (30min data prep + 2h extraction + 10min analysis)

---

## Next Steps (Phase 4)

1. Implement 5 modules (dataset.py, scorer.py, attention.py, correlation.py, report.py)
2. Run experiment (600 questions)
3. Generate validation report
4. Gate decision: PASS to H-M1 or FAIL to Phase 0
