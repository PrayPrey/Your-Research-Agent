# Architecture Document: H-M3 Query Complexity Attention Analysis

**Hypothesis ID**: h-m3  
**Type**: MECHANISM (INCREMENTAL)  
**Date**: 2026-08-20  
**Applied Patterns**: Reuse h-e1 attention extraction, entity stratification

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-e1)  
**Status**: h-e1 code not yet implemented (both will be built together)  
**Analyzed Path**: docs/youra_research/h-e1/code (not found - green-field)  
**Findings**: New implementation from scratch with shared infrastructure planning

---

## System Overview

Stratify queries by complexity (entity density + word count), measure query-token attention concentration during generation, test H-M3 (simple > complex via two-sample t-test). Reuses h-e1 attention extraction pipeline.

---

## Module Structure

### ComplexityClassifier (`analysis/complexity.py`)

**Dependencies**: None

```python
class QueryComplexityClassifier:
    def __init__(self, spacy_model: str = "en_core_web_sm"): ...
    def compute_entity_density(self, query: str) -> float: ...  # num_entities / num_tokens
    def classify(self, query: str) -> str: ...  # "simple" | "complex"
```

---

### AttentionAnalyzer (`analysis/attention.py`)

**Dependencies**: ComplexityClassifier

```python
class QueryTokenAttentionExtractor:
    def __init__(self, tokenizer): ...
    def extract_concentration(self, query: str, attentions: tuple) -> float: ...  # query_attn / total_attn
    
class StratifiedAnalyzer:
    def __init__(self, classifier: QueryComplexityClassifier, extractor: QueryTokenAttentionExtractor): ...
    def run(self, dataset, model, tokenizer) -> dict: ...  # {simple_ratios, complex_ratios, t_stat, p_value}
```

---

### Reporter (`analysis/report.py`)

**Dependencies**: AttentionAnalyzer

```python
class ValidationReporter:
    def __init__(self, output_dir: str): ...
    def plot_bar_chart(self, simple_mean: float, complex_mean: float): ...
    def plot_distributions(self, simple_ratios: list, complex_ratios: list): ...
    def plot_scatter(self, entity_densities: list, attentions: list): ...
    def gate_decision(self, p_value: float, simple_mean: float, complex_mean: float) -> str: ...
    def write_report(self, results: dict): ...
```

---

## External Dependencies (Shared with H-E1)

### Shared Infrastructure (Planned)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| LongBenchLoader | `from h_e1.data.dataset import LongBenchLoader` | `h-e1/code/data/dataset.py` |
| LlamaQA | `from h_e1.model.attention import LlamaQA` | `h-e1/code/model/attention.py` |
| AttentionCollector | `from h_e1.model.attention import AttentionCollector` | `h-e1/code/model/attention.py` |

**Note**: h-e1 not yet implemented. Architecture shows planned sharing structure.

---

## Data Flow

1. **Load**: LongBenchLoader (from h-e1) → 600 questions
2. **Classify**: QueryComplexityClassifier → "simple" | "complex" labels
3. **Extract**: LlamaQA + AttentionCollector (from h-e1) → attention weights
4. **Measure**: QueryTokenAttentionExtractor → concentration ratios per stratum
5. **Test**: StratifiedAnalyzer → two-sample t-test
6. **Report**: ValidationReporter → 02d_validation_h-m3.md + gate decision

---

## Storage Strategy

```
h-m3/
├── data/
│   └── query_complexity_labels.csv        # (question_id, complexity, entity_density, word_count)
├── outputs/
│   ├── concentrations/
│   │   ├── simple_ratios.npy              # (300,)
│   │   └── complex_ratios.npy             # (300,)
│   └── results/
│       ├── stratified_statistics.json
│       └── figures/
│           ├── bar_chart.png              # Required figure
│           ├── distributions.png
│           ├── scatter_entity_attention.png
│           └── boxplots.png
└── 02d_validation_h-m3.md
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M1 | Entity Classifier | spaCy NER integration, entity density computation | 8 | 2+2+2+2 (install+compute+classify+validate) |
| M2 | Attention Extraction Reuse | Adapt h-e1 AttentionCollector for query-token tracking | 10 | 3+3+2+2 (locate_query_tokens+aggregate+map+validate) |
| M3 | Stratification Pipeline | Run dataset through classifier, split by complexity | 7 | 2+2+2+1 (label+split+cache+check) |
| M4 | Concentration Metrics | Query-token attention mass vs total mass computation | 9 | 3+2+2+2 (compute+aggregate+per_strata+validate) |
| M5 | Statistical Testing | Two-sample t-test, effect size, bootstrap CI | 11 | 3+3+3+2 (t_test+cohen_d+CI+baselines) |
| M6 | Visualization + Report | 4 figures, statistics table, gate decision | 10 | 3+3+2+2 (4_plots+stats+report+decision) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M2,M4,M5,M6], Low(4-8): [M1,M3]

**Total Complexity**: 55 (6 epics, Tier 2 implementation)

---

## Configuration

### Complexity Config (`config/complexity.yaml`)
```yaml
thresholds:
  simple_word_count: 10
  simple_entity_density: 0.3
spacy_model: en_core_web_sm
stratification:
  min_samples_per_stratum: 100
```

### Attention Config (`config/attention.yaml`)
```yaml
target_layer: -1  # Last decoder layer (from h-e1)
aggregation: mean_heads  # Average across attention heads
query_token_tracking: true
```

### Statistical Config (`config/stats.yaml`)
```yaml
test:
  type: two_sample_t_test
  alternative: greater  # simple > complex
  alpha: 0.05
bootstrap:
  n_samples: 1000
  seed: 42
```

---

## Validation Checklist

### Query Complexity
- [ ] Entity extraction completes for all 600 questions
- [ ] Simple stratum: ≥ 100 samples
- [ ] Complex stratum: ≥ 100 samples
- [ ] No missing labels

### Attention Concentration
- [ ] Concentration ratios in [0, 1]
- [ ] No NaN or Inf values
- [ ] Query token boundaries match tokenization
- [ ] Uniform attention baseline → ρ ≈ random

### Statistical Rigor
- [ ] Two-sample t-test p-value computed
- [ ] Effect size (Cohen's d) computed
- [ ] Bootstrap CI (95%) computed
- [ ] Simple vs complex difference Δ > 0.1

### Gate Decision (SHOULD_WORK)
- [ ] p < 0.05 (statistical significance)
- [ ] simple_mean > complex_mean (directional hypothesis)
- [ ] Validation report written to 02d_validation_h-m3.md

---

## Success Criteria

**Primary**: p < 0.05, simple_mean > complex_mean, Δ > 0.1  
**Fallback (SHOULD_WORK)**: If fails → uniform tiering documented, no blocker for H-M1/H-M4  
**Failure**: No statistical significance → Phase 0 routing (unlikely with SHOULD_WORK gate)

---

## Compute Budget

- **GPU**: 1x A100 40GB (shared with h-e1)
- **Model Memory**: ~14GB (Llama-2-7B FP16, from h-e1)
- **Entity Extraction**: 5 min (spaCy on 600 queries, CPU)
- **Attention Extraction**: Reuse h-e1 outputs (no additional time)
- **Analysis**: 2 min (numpy operations)
- **Time**: 7 min total (assumes h-e1 already ran)

---

## Next Steps (Phase 4)

1. Implement 3 modules (complexity.py, attention.py, report.py)
2. Run stratification + analysis (600 questions)
3. Generate validation report with 4 figures
4. Gate decision: Document tiering strategy regardless of result
