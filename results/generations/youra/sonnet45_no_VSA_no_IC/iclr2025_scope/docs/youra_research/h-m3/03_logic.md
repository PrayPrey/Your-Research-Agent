# Logic Document: H-M3 Query Complexity Attention Analysis

**Version**: 1.0  
**Date**: 2026-08-20  
**Hypothesis ID**: h-m3  
**Type**: MECHANISM (PoC)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: h-e1 not yet implemented - green-field for both  
**Analyzed Path**: docs/youra_research/h-e1/code (not found)  
**Relevant Symbols**: None - designing new APIs from scratch

---

## Knowledge Base Patterns Applied

**Applied**: PyTorch attention extraction (standard transformers), spaCy NER (en_core_web_sm), scipy.stats (spearmanr, ttest_ind)

---

## M1: Entity Classifier [Complexity: 8, Budget: 8]

### API

```python
import spacy

class QueryComplexityClassifier:
    def __init__(self, spacy_model: str = "en_core_web_sm"):
        """Load spaCy model."""
        self.nlp = spacy.load(spacy_model)
    
    def compute_entity_density(self, query: str) -> float:
        """num_entities / num_tokens"""
        doc = self.nlp(query)
        tokens = [t for t in doc if not t.is_space]
        return len(doc.ents) / len(tokens) if tokens else 0.0
    
    def classify(self, query: str) -> str:
        """Returns 'simple' or 'complex'."""
        word_count = len(query.split())
        density = self.compute_entity_density(query)
        return "simple" if (word_count < 10 and density < 0.3) else "complex"
```

### Subtasks [4/8]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Install spaCy | pip install spacy |
| L-1-2 | Entity count | len(doc.ents) |
| L-1-3 | Token count | len([t for t in doc if not t.is_space]) |
| L-1-4 | Classify | word_count < 10 AND density < 0.3 |

---

## M2: Attention Extraction Reuse [Complexity: 10, Budget: 10]

**Note**: Reuses h-e1 infrastructure. Since h-e1 not yet built, specs are preliminary.

### API

```python
from typing import List, Tuple
import torch
import numpy as np

class QueryTokenAttentionExtractor:
    def __init__(self, tokenizer):
        """Store tokenizer for query token boundary detection."""
        self.tokenizer = tokenizer
    
    def locate_query_tokens(self, full_input_ids: torch.Tensor, query: str) -> Tuple[int, int]:
        """Find query token positions in full input.
        
        Returns: (start_idx, end_idx)
        """
        query_ids = self.tokenizer.encode(query, add_special_tokens=False)
        query_len = len(query_ids)
        return (0, query_len)  # Query at start of prompt
    
    def extract_concentration(
        self, 
        query: str, 
        attentions: tuple,  # From model output
        input_ids: torch.Tensor
    ) -> float:
        """Query attention mass / total attention mass.
        
        attentions: tuple of [B, H, S, S] per layer
        Returns: float in [0, 1]
        """
        last_layer_attn = attentions[-1][0]  # [H, S, S], batch=0
        avg_heads = last_layer_attn.mean(dim=0)  # [S, S]
        
        query_start, query_end = self.locate_query_tokens(input_ids, query)
        
        # Sum attention to query tokens
        query_attn_mass = avg_heads[:, query_start:query_end].sum().item()
        total_attn_mass = avg_heads.sum().item()
        
        return query_attn_mass / total_attn_mass if total_attn_mass > 0 else 0.0
```

### Subtasks [3/10]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Locate query | tokenizer.encode + find in input_ids |
| L-2-2 | Aggregate heads | .mean(dim=0) over attention heads |
| L-2-3 | Compute ratio | query_sum / total_sum |

---

## M3: Stratification Pipeline [Complexity: 7, Budget: 7]

### API

```python
from datasets import load_dataset
import pandas as pd

def stratify_dataset(
    classifier: QueryComplexityClassifier,
    min_per_stratum: int = 300
) -> pd.DataFrame:
    """Load LongBench, classify all queries, ensure balance.
    
    Returns: DataFrame with [question_id, question, context, complexity, entity_density]
    """
    # Load datasets
    datasets = [
        load_dataset("THUDM/LongBench", "hotpotqa", split="test"),
        load_dataset("THUDM/LongBench", "2wikimqa", split="test"),
        load_dataset("THUDM/LongBench", "musique", split="test")
    ]
    
    rows = []
    for ds in datasets:
        for sample in ds:
            density = classifier.compute_entity_density(sample["input"])
            complexity = classifier.classify(sample["input"])
            rows.append({
                "question_id": sample["_id"],
                "question": sample["input"],
                "context": sample["context"],
                "complexity": complexity,
                "entity_density": density
            })
    
    df = pd.DataFrame(rows)
    
    # Balance strata
    simple = df[df["complexity"] == "simple"].head(min_per_stratum)
    complex = df[df["complexity"] == "complex"].head(min_per_stratum)
    
    return pd.concat([simple, complex], ignore_index=True)
```

### Subtasks [2/7]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Load + label | Loop datasets, apply classifier |
| L-3-2 | Balance strata | .head(300) per stratum |

---

## M4: Concentration Metrics [Complexity: 9, Budget: 9]

### API

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

def run_attention_extraction(
    dataset: pd.DataFrame,
    extractor: QueryTokenAttentionExtractor,
    model_name: str = "meta-llama/Llama-2-7b-hf"
) -> pd.DataFrame:
    """Run model, extract attention concentrations.
    
    Returns: dataset with added 'concentration' column
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    concentrations = []
    
    for idx, row in dataset.iterrows():
        prompt = f"Context: {row['context']}\n\nQuestion: {row['question']}\n\nAnswer:"
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=8192).to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=128,
                output_attentions=True,
                return_dict_in_generate=True
            )
        
        concentration = extractor.extract_concentration(
            row['question'], 
            outputs.attentions[-1],  # Last generation step
            inputs['input_ids']
        )
        concentrations.append(concentration)
    
    dataset['concentration'] = concentrations
    return dataset
```

### Subtasks [3/9]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Load model | AutoModelForCausalLM with output_attentions=True |
| L-4-2 | Generate | model.generate + extract attentions |
| L-4-3 | Extract per sample | extractor.extract_concentration |

---

## M5: Statistical Testing [Complexity: 11, Budget: 11]

### API

```python
from scipy.stats import ttest_ind
import numpy as np

def run_statistical_test(dataset: pd.DataFrame) -> dict:
    """Two-sample t-test: simple > complex.
    
    Returns: {simple_mean, complex_mean, t_stat, p_value, delta, cohen_d, ci_95}
    """
    simple_concentrations = dataset[dataset['complexity'] == 'simple']['concentration'].values
    complex_concentrations = dataset[dataset['complexity'] == 'complex']['concentration'].values
    
    # t-test
    t_stat, p_value = ttest_ind(simple_concentrations, complex_concentrations, alternative='greater')
    
    # Effect size (Cohen's d)
    pooled_std = np.sqrt((simple_concentrations.var() + complex_concentrations.var()) / 2)
    cohen_d = (simple_concentrations.mean() - complex_concentrations.mean()) / pooled_std
    
    # Bootstrap CI
    def bootstrap_ci(arr, n_iter=1000):
        means = [np.random.choice(arr, len(arr), replace=True).mean() for _ in range(n_iter)]
        return (np.percentile(means, 2.5), np.percentile(means, 97.5))
    
    return {
        "simple_mean": simple_concentrations.mean(),
        "complex_mean": complex_concentrations.mean(),
        "delta": simple_concentrations.mean() - complex_concentrations.mean(),
        "t_statistic": t_stat,
        "p_value": p_value,
        "cohen_d": cohen_d,
        "ci_95_simple": bootstrap_ci(simple_concentrations),
        "ci_95_complex": bootstrap_ci(complex_concentrations)
    }
```

### Subtasks [3/11]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | t-test | scipy.stats.ttest_ind with alternative='greater' |
| L-5-2 | Effect size | Cohen's d = (μ1 - μ2) / pooled_std |
| L-5-3 | Bootstrap CI | Resample 1000 times, percentiles |

---

## M6: Visualization + Report [Complexity: 10, Budget: 10]

### API

```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_bar_chart(results: dict, output_path: str):
    """Bar chart: simple vs complex mean concentration."""
    fig, ax = plt.subplots(figsize=(6, 4))
    categories = ['Simple', 'Complex']
    means = [results['simple_mean'], results['complex_mean']]
    errors = [
        results['ci_95_simple'][1] - results['simple_mean'],
        results['ci_95_complex'][1] - results['complex_mean']
    ]
    
    ax.bar(categories, means, yerr=errors, capsize=5)
    ax.set_ylabel('Query-Token Attention Concentration')
    ax.set_title(f"H-M3: Simple > Complex (p={results['p_value']:.3f})")
    plt.savefig(output_path)
    plt.close()

def plot_distributions(dataset: pd.DataFrame, output_path: str):
    """Histogram overlay: simple vs complex distributions."""
    fig, ax = plt.subplots(figsize=(8, 4))
    simple = dataset[dataset['complexity'] == 'simple']['concentration']
    complex = dataset[dataset['complexity'] == 'complex']['concentration']
    
    ax.hist(simple, bins=30, alpha=0.5, label='Simple')
    ax.hist(complex, bins=30, alpha=0.5, label='Complex')
    ax.legend()
    ax.set_xlabel('Attention Concentration')
    ax.set_ylabel('Count')
    plt.savefig(output_path)
    plt.close()

def plot_scatter(dataset: pd.DataFrame, output_path: str):
    """Entity density (x) vs concentration (y), color by word count."""
    fig, ax = plt.subplots(figsize=(8, 6))
    dataset['word_count'] = dataset['question'].apply(lambda q: len(q.split()))
    
    scatter = ax.scatter(
        dataset['entity_density'], 
        dataset['concentration'],
        c=dataset['word_count'],
        alpha=0.6,
        cmap='viridis'
    )
    plt.colorbar(scatter, label='Word Count')
    ax.set_xlabel('Entity Density')
    ax.set_ylabel('Attention Concentration')
    plt.savefig(output_path)
    plt.close()

def gate_decision(results: dict) -> str:
    """SHOULD_WORK gate: p < 0.05 AND simple > complex.
    
    Returns: 'PASS' or 'FAIL' + explanation
    """
    if results['p_value'] < 0.05 and results['delta'] > 0:
        status = "PASS"
        explanation = f"Statistical significance achieved (p={results['p_value']:.4f}), simple > complex by {results['delta']:.3f}"
    else:
        status = "FAIL"
        explanation = f"No significance (p={results['p_value']:.4f}) or wrong direction (Δ={results['delta']:.3f})"
    
    return f"{status}: {explanation}"

def write_validation_report(dataset: pd.DataFrame, results: dict, figures_dir: str, output_path: str):
    """Write 02d_validation_h-m3.md."""
    decision = gate_decision(results)
    
    report = f"""# Validation Report: H-M3 Query Complexity Attention

**Hypothesis**: Simple queries show higher query-token attention concentration than complex queries.

## Gate Decision

{decision}

## Results

| Metric | Simple | Complex | Difference |
|--------|--------|---------|------------|
| Mean Concentration | {results['simple_mean']:.3f} | {results['complex_mean']:.3f} | {results['delta']:.3f} |
| 95% CI | [{results['ci_95_simple'][0]:.3f}, {results['ci_95_simple'][1]:.3f}] | [{results['ci_95_complex'][0]:.3f}, {results['ci_95_complex'][1]:.3f}] | - |
| t-statistic | {results['t_statistic']:.3f} | - | - |
| p-value | {results['p_value']:.4f} | - | - |
| Cohen's d | {results['cohen_d']:.3f} | - | - |

## Sample Sizes

- Simple queries: {len(dataset[dataset['complexity'] == 'simple'])}
- Complex queries: {len(dataset[dataset['complexity'] == 'complex'])}

## Figures

![Bar Chart]({figures_dir}/bar_chart.png)
![Distributions]({figures_dir}/distributions.png)
![Scatter]({figures_dir}/scatter.png)

## Interpretation

{"Hypothesis validated. Adaptive tiering justified." if "PASS" in decision else "Hypothesis not validated. Fallback to uniform tiering recommended."}
"""
    
    with open(output_path, 'w') as f:
        f.write(report)
```

### Subtasks [3/10]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | 4 plots | bar_chart, distributions, scatter, boxplots |
| L-6-2 | Statistics table | means, CI, p-value in markdown |
| L-6-3 | Gate decision | p < 0.05 AND delta > 0 |

---

## External Dependencies (Shared Infrastructure with H-E1)

**Note**: H-E1 not yet implemented. When available, import from:

```python
# Planned imports (not yet available)
from h_e1.data.dataset import LongBenchLoader  # Alternative to datasets.load_dataset
from h_e1.model.attention import LlamaQA  # Alternative to AutoModelForCausalLM
from h_e1.model.attention import AttentionCollector  # Hook-based collection
```

**Current Approach**: Use standard HuggingFace transformers directly. No dependency on h-e1 code until it exists.

---

## Summary

**Total Tasks**: 6 epics  
**Total Budget**: 55 subtasks (5 available, all allocated)  

**Key Algorithms**:
1. Entity density: `len(doc.ents) / len(tokens)`
2. Query concentration: `sum(attention[:, query_range]) / sum(attention)`
3. Statistical test: `scipy.stats.ttest_ind(simple, complex, alternative='greater')`

**Critical Implementation Details**:
- spaCy model: `en_core_web_sm` (requires download: `python -m spacy download en_core_web_sm`)
- Model config: `output_attentions=True`, `attn_implementation="eager"` (not flash)
- Query token boundary: Encode query separately, find in full input_ids
- Attention extraction: Last layer, average across heads, sum to query tokens
- Bootstrap: 1000 iterations, 95% CI via percentiles

**Gate Logic**: SHOULD_WORK → PASS if p < 0.05 AND simple_mean > complex_mean, else FAIL (fallback to uniform tiering documented)
