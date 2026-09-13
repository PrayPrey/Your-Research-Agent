# Product Requirements Document (PRD)

**Hypothesis:** H-M3  
**Date:** 2026-08-20  
**Author:** Anonymous  
**Type:** MECHANISM (INCREMENTAL)  
**Prerequisites:** H-E1 (VALIDATED)

---

## Executive Summary

### Problem Statement

Validate whether simple queries (low entity density, short length) show higher query-token attention concentration than complex queries during answer generation. This mechanism hypothesis tests the assumption underlying adaptive tiering in the proposed YOURA KV cache eviction strategy.

### Hypothesis

Simple queries (low entity density, short length) show higher query-token attention concentration than complex queries, validating adaptive tiering.

**Gate Type:** SHOULD_WORK  
**Failure Consequence:** Falls back to uniform tiering for all queries (conservative approach). Query-anchoring hypothesis fails but core provenance-aware eviction (H-M1, H-M4) remains valid.

### Success Criteria

**Primary Success Criterion:**
- Two-sample t-test: p < 0.05 (statistically significant)
- Simple queries mean attention > Complex queries mean attention
- Attention concentration difference (Δ) > 0.1 (10 percentage points)

**Gate Success:**
- Statistical significance achieved (p < 0.05)
- Directional hypothesis confirmed (simple > complex)

---

## Context

### Prerequisites

**H-E1 (Relevance-Attention Correlation):** VALIDATED ✅
- BM25 retrieval scores: Spearman ρ = 0.391 > 0.3
- Contriever retrieval scores: Spearman ρ = 0.612 > 0.3
- Infrastructure: Llama-2-7B attention extraction, LongBench multi-doc QA validated

### Shared Infrastructure

- Attention extraction pipeline (H-E1)
- Llama-2-7B model configuration
- LongBench multi-doc QA dataset
- Statistical testing framework

---

## Functional Requirements

### FR-1: Dataset Preparation

**Requirement:** Load and prepare LongBench multi-doc QA subsets with query complexity stratification.

**Specifications:**
- **Subsets:** HotpotQA, 2WikiMultihopQA, MuSiQue
- **Sample Size:** Minimum 600 samples (300 simple + 300 complex)
- **Stratification Criteria:**
  - Simple: word_count < 10 AND entity_density < 0.3
  - Complex: word_count ≥ 10 OR entity_density ≥ 0.3
- **Entity Extraction:** spaCy NER (`en_core_web_sm`)

**Loading Code:**
```python
from datasets import load_dataset

hotpot = load_dataset("THUDM/LongBench", "hotpotqa", split="test")
wikimqa = load_dataset("THUDM/LongBench", "2wikimqa", split="test")
musique = load_dataset("THUDM/LongBench", "musique", split="test")
```

**Acceptance Criteria:**
- Dataset loaded successfully
- Minimum 300 samples per stratum
- Entity density computed for all queries
- Stratification labels assigned

---

### FR-2: Model Loading and Configuration

**Requirement:** Load Llama-2-7B with attention extraction enabled.

**Specifications:**
- **Model:** meta-llama/Llama-2-7b-hf
- **Configuration:**
  - `output_attentions=True` (CRITICAL)
  - `attn_implementation="eager"` (not flash_attention)
  - `device_map="auto"`
- **Context Window:** Extended to 32k tokens for long-context samples

**Loading Code:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    device_map="auto",
    output_attentions=True,
    attn_implementation="eager"
)
```

**Acceptance Criteria:**
- Model loads without error
- Attention weights extractable via forward pass
- No CUDA memory overflow on sample inputs

---

### FR-3: Query Complexity Classification

**Requirement:** Implement query complexity classifier using entity density and word count.

**Specifications:**
- **Inputs:** Query text (string)
- **Outputs:** "simple" or "complex"
- **Entity Density Metric:** `num_entities / num_tokens`
- **Thresholds:**
  - Simple: word_count < 10 AND entity_density < 0.3
  - Complex: otherwise

**Implementation Pattern:**
```python
import spacy

nlp = spacy.load("en_core_web_sm")

def classify_query_complexity(query_text):
    doc = nlp(query_text)
    word_count = len(query_text.split())
    entity_density = len([ent for ent in doc.ents]) / len([t for t in doc if not t.is_space])
    
    is_simple = (word_count < 10) and (entity_density < 0.3)
    return "simple" if is_simple else "complex"
```

**Acceptance Criteria:**
- Classifier returns "simple" or "complex" for all queries
- Entity extraction completes without errors
- Edge cases handled (empty queries, all entities, no entities)

---

### FR-4: Attention Extraction

**Requirement:** Extract query-token attention concentration ratios during generation.

**Specifications:**
- **Attention Layer:** Last layer (layer -1)
- **Aggregation:** Mean across attention heads
- **Metric:** Query attention mass / Total attention mass
- **Shape:** `[batch, num_heads, seq_len, seq_len]`

**Implementation Pattern:**
```python
def extract_query_token_attention(query_text, context, attentions, tokenizer):
    query_tokens = tokenizer.encode(query_text, add_special_tokens=False)
    query_len = len(query_tokens)
    
    # Extract last layer, average across heads
    attn_weights = attentions[-1][0]  # Last layer, batch 0
    avg_attn = attn_weights.mean(dim=0)
    
    # Compute concentration
    query_attn_mass = avg_attn[:, :query_len].sum(dim=1).mean()
    total_attn_mass = avg_attn.sum(dim=1).mean()
    
    concentration_ratio = (query_attn_mass / total_attn_mass).item()
    return concentration_ratio
```

**Acceptance Criteria:**
- Attention weights extracted for all samples
- Concentration ratio in range [0, 1]
- No NaN or Inf values

---

### FR-5: Stratified Analysis

**Requirement:** Run stratified attention analysis across query complexity strata.

**Specifications:**
- **Strata:** Simple queries, Complex queries
- **Metric per Sample:** Query-token attention concentration ratio
- **Aggregation:** Mean per stratum
- **Statistical Test:** Two-sample independent t-test (one-tailed)
- **Null Hypothesis:** No difference in attention concentration
- **Alternative:** Simple queries > Complex queries

**Implementation Pattern:**
```python
from scipy.stats import ttest_ind

def run_stratified_analysis(dataset, model, tokenizer):
    simple_ratios = []
    complex_ratios = []
    
    for sample in dataset:
        query = sample["question"]
        context = sample["context"]
        complexity = classify_query_complexity(query)
        
        inputs = tokenizer(query + " " + context, return_tensors="pt")
        outputs = model(**inputs, output_attentions=True)
        
        concentration = extract_query_token_attention(query, context, outputs.attentions, tokenizer)
        
        if complexity == "simple":
            simple_ratios.append(concentration)
        else:
            complex_ratios.append(concentration)
    
    t_stat, p_value = ttest_ind(simple_ratios, complex_ratios, alternative='greater')
    
    return {
        "simple_mean": np.mean(simple_ratios),
        "complex_mean": np.mean(complex_ratios),
        "t_statistic": t_stat,
        "p_value": p_value
    }
```

**Acceptance Criteria:**
- All samples processed without errors
- Both strata have ≥ 100 samples (statistical power)
- t-test returns valid p-value
- Results logged and saved

---

### FR-6: Visualization

**Requirement:** Generate required and additional figures for hypothesis validation.

**Required Figures:**
1. **Bar Chart:** Simple vs Complex mean attention concentration (with error bars)

**Additional Figures:**
2. **Distribution Plot:** Histograms of attention concentration (simple vs complex overlaid)
3. **Scatter Plot:** Entity density (x) vs attention concentration (y), color by word count
4. **Box Plot:** Attention concentration distributions by stratum
5. **Heatmap:** Sample attention weights (2 simple + 2 complex examples)

**Acceptance Criteria:**
- All figures saved to `{hypothesis_folder}/figures/`
- Bar chart shows means, standard deviations, statistical significance marker
- Figures readable and publication-quality

---

## Non-Functional Requirements

### NFR-1: Performance

- **Inference Speed:** ≤ 2 seconds per sample (GPU)
- **Memory:** Fit within 16GB GPU memory (batch size 1)
- **Total Runtime:** ≤ 30 minutes for 600 samples

### NFR-2: Reproducibility

- **Random Seed:** Fixed at 42
- **Deterministic Operations:** No stochastic sampling during inference
- **Environment:** Documented Python version, library versions

### NFR-3: Code Quality

- **Modularity:** Separate classes for classifier, extractor, analyzer
- **Error Handling:** Graceful failure on CUDA OOM, model loading errors
- **Logging:** Progress bar for sample processing

---

## Dependencies

### External Dependencies

**Models:**
- meta-llama/Llama-2-7b-hf (HuggingFace)
- spaCy en_core_web_sm

**Datasets:**
- THUDM/LongBench (HuggingFace)

**Libraries:**
- transformers
- datasets
- spacy
- torch
- scipy
- numpy
- matplotlib / seaborn (visualization)

### Internal Dependencies

**Prerequisites:**
- H-E1 validation results (for infrastructure confirmation)
- H-E1 attention extraction methodology

**Shared Artifacts:**
- None (H-M3 is independent analysis)

---

## Out of Scope

- Training or fine-tuning models
- Hyperparameter optimization
- Cross-dataset validation (only LongBench)
- Query complexity beyond entity density + word count
- Attention mechanisms other than last layer

---

## Success Metrics

### Gate Metrics

**SHOULD_WORK Gate:**
- Statistical significance: p < 0.05 ✅
- Directional hypothesis: simple_mean > complex_mean ✅

### Validation Metrics

**Primary:**
- Mean attention concentration (simple stratum)
- Mean attention concentration (complex stratum)
- Δ (simple - complex) > 0.1 (10 percentage points)

**Statistical:**
- t-statistic
- p-value
- Effect size (Cohen's d)

### Quality Metrics

- Sample distribution: ≥ 300 per stratum ✅
- Zero errors during processing ✅
- All figures generated ✅

---

## Timeline & Milestones

**Phase 4 (Coding & Validation):**
- Dataset preparation: Epic 1
- Model + entity extraction: Epic 2
- Attention analysis pipeline: Epic 3
- Statistical testing: Epic 4
- Visualization: Epic 5
- Gate validation: Epic 6

**Estimated Duration:** 2-3 hours (implementation) + 30 min (validation)

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Insufficient simple queries in dataset | Medium | High | Sample across all 3 subsets; lower threshold if needed |
| CUDA OOM on long contexts | Medium | Medium | Batch size 1; truncate to 32k tokens |
| No statistical significance | Medium | Low | SHOULD_WORK gate; fallback to uniform tiering documented |
| Entity extraction slow | Low | Medium | Pre-compute entity density; cache results |

---

## Appendix

### Reference Implementations

**Entity-Conditioned QG:** ar5iv.labs.arxiv.org/html/2204.11373  
**DuoAttention Analysis:** github.com/mit-han-lab/duo-attention  
**LongBench Benchmark:** github.com/THUDM/LongBench

### Related Hypotheses

- H-E1: Relevance-attention correlation (prerequisite) ✅
- H-M1: Query-anchored eviction (depends on H-M3 result)
- H-M4: Provenance-aware eviction (independent of H-M3)
