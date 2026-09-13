# Experiment Design: H-M2

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis Statement:** MMLU, BIG-Bench, HumanEval and similar emergent-capability benchmarks created post-foundation-model emergence (>80% post-2020)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing causal link between foundation models and benchmark creation patterns.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M1 PASS)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (Foundation Model Emergence Timeline - PASS)

### Gate Condition
**SHOULD_WORK**: If fails, document as limitation; does not block subsequent hypotheses but weakens causal chain evidence.

---

## Continuation Context

H-M1 validated that foundation model papers (GPT-3, ViT, BERT successors) have citation impact >2σ above field median, confirming paradigm shift occurred 2019-2021. H-M2 now tests whether this shift drove creation of new emergent-capability benchmarks.

### Previous Hypothesis Results (if applicable)
- **H-E1 (PASS):** PELT detected 2 change points (2019-04, 2021-03) in Gini coefficient time series
- **H-M1 (PASS):** All 5 foundation papers exceed 2σ citation threshold

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct findings for benchmark creation timeline analysis. Related resources:
- LAION-5B dataset documentation (laion.ai) - example of post-2021 large-scale dataset
- Various diffusion model papers with 2021-2023 publication dates

### Archon Code Examples

No directly applicable code examples for benchmark metadata extraction. BibTeX citation formats found but not relevant to this task.

### Exa GitHub Implementations

**Key Benchmark Creation Dates Verified:**
| Benchmark | Type | Creation Date | Source |
|-----------|------|---------------|--------|
| MMLU | Emergent-capability | Sep 2020 | Wikipedia, Hendrycks et al. |
| HumanEval | Emergent-capability | July 2021 | github.com/openai/human-eval |
| BIG-Bench | Emergent-capability | Jan 2021 (repo), 2022 (paper) | github.com/google/BIG-bench |
| TruthfulQA | Emergent-capability | Aug 2021 | github.com/sylinrl/TruthfulQA |
| GSM8K | Emergent-capability | 2021 | OpenAI |
| WinoGrande | Traditional (commonsense) | Feb 2020 (AAAI-20) | Pre-foundation |
| HellaSwag | Traditional (commonsense) | 2019 | Pre-foundation |

**Papers With Code Data Sources:**
- HuggingFace datasets: `pwc-archive/datasets`, `pwc-archive/evaluation-tables`
- Python client: `paperswithcode-client` (v0.3.1)
- Daily dumps with task-dataset-metric associations

### 🎯 Implementation Priority Assessment

**CRITICAL: Use official PWC data dumps for systematic benchmark dating**

**Recommended Implementation Path:**
- Primary: Download PWC datasets.json from HuggingFace, extract benchmark metadata including introduction papers and dates
- Fallback: Manual curation of top-50 benchmarks with verified creation dates from original papers
- Justification: PWC is authoritative source; datasets.json contains paper links enabling date extraction

### Code Analysis (Serena MCP)

Not applicable - this is a data analysis task, not codebase modification.

---

## Experiment Specification

### Dataset

**Name:** Papers With Code Benchmark Metadata
**Type:** standard (programmatic-api)
**Source:** HuggingFace `pwc-archive/datasets` + `pwc-archive/evaluation-tables`

**Preprocessing:**
1. Download datasets.json.gz from PWC HuggingFace archive
2. Parse JSON to extract: benchmark_name, introducing_paper_id, paper_date
3. For benchmarks without paper_date: lookup via Semantic Scholar API using paper title
4. Classify benchmarks as "emergent-capability" or "traditional" based on task type

**Sample Size:** Full PWC dataset (~4,500+ datasets as of 2024)
**Evaluation Set:** All benchmarks with identifiable creation dates (estimated 2,000+)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets library
- Identifier: `pwc-archive/datasets`
- Code:
```python
from datasets import load_dataset
pwc_datasets = load_dataset("pwc-archive/datasets", split="train")
```

### Models

#### Baseline Model

**Type:** Rule-based classification + date extraction pipeline

**Components:**
1. Date extractor: Parse paper dates from PWC metadata or Semantic Scholar
2. Benchmark classifier: Keyword-based classification into emergent-capability vs traditional

**Loading Information** (for Phase 4 download):
- Method: Custom Python implementation
- Identifier: N/A (custom code)
- Code:
```python
# No pretrained model - rule-based pipeline
import re
from datetime import datetime

def extract_benchmark_date(benchmark_metadata):
    if 'paper' in benchmark_metadata and benchmark_metadata['paper']:
        return parse_paper_date(benchmark_metadata['paper'])
    return None
```

#### Proposed Model

**Architecture:** Systematic benchmark classification with temporal analysis

**Core Mechanism Implementation:**

```python
# Core mechanism: Classify benchmarks and compute post-2020 ratio

EMERGENT_KEYWORDS = [
    'reasoning', 'emergent', 'capability', 'understanding', 
    'language model', 'code generation', 'multitask', 'multilingual',
    'truthful', 'factual', 'math reasoning', 'commonsense'
]

EMERGENT_BENCHMARKS = {
    'mmlu', 'big-bench', 'bigbench', 'humaneval', 'truthfulqa',
    'gsm8k', 'math', 'arc', 'hellaswag', 'winogrande',
    'lambada', 'squad', 'natural-questions', 'triviaqa',
    'codex', 'apps', 'mbpp'
}

def classify_benchmark(name: str, description: str, tasks: list) -> str:
    """Classify benchmark as emergent-capability or traditional."""
    name_lower = name.lower()
    
    # Direct match
    if any(eb in name_lower for eb in EMERGENT_BENCHMARKS):
        return 'emergent-capability'
    
    # Keyword match in description
    if description:
        desc_lower = description.lower()
        if any(kw in desc_lower for kw in EMERGENT_KEYWORDS):
            return 'emergent-capability'
    
    # Task-based classification
    emergent_tasks = {'question-answering', 'reading-comprehension', 
                      'code-generation', 'math-word-problems'}
    if tasks and any(t.lower() in emergent_tasks for t in tasks):
        return 'emergent-capability'
    
    return 'traditional'

def compute_post2020_ratio(benchmarks: list) -> dict:
    """Compute percentage of emergent benchmarks created post-2020."""
    emergent = [b for b in benchmarks if b['type'] == 'emergent-capability']
    
    post_2020 = sum(1 for b in emergent if b['creation_year'] >= 2020)
    pre_2020 = sum(1 for b in emergent if b['creation_year'] < 2020)
    
    ratio = post_2020 / len(emergent) if emergent else 0
    
    return {
        'total_emergent': len(emergent),
        'post_2020_count': post_2020,
        'pre_2020_count': pre_2020,
        'post_2020_ratio': ratio,
        'passes_threshold': ratio > 0.80
    }
```

### Training Protocol

**Not applicable** - This is a data analysis experiment, not a model training task.

**Pipeline Steps:**
1. Data download: Fetch PWC datasets.json (~5 min)
2. Date extraction: Parse/lookup creation dates (~10 min with API calls)
3. Classification: Apply rule-based classifier (~1 min)
4. Analysis: Compute statistics and visualizations (~1 min)

**Total estimated runtime:** 15-20 minutes

### Evaluation

**Primary Metric:** Post-2020 ratio of emergent-capability benchmarks
**Success Threshold:** ratio > 0.80 (80%)

**Secondary Metrics:**
- Creation rate acceleration: benchmarks/year post-2020 vs pre-2020
- Semantic similarity of post-2020 benchmarks to foundation model capabilities

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification + ratio computation
- Library: Standard Python (no ML metrics library needed)
- Code:
```python
def evaluate_hypothesis(results: dict) -> dict:
    """Evaluate H-M2 success criteria."""
    passed = results['post_2020_ratio'] > 0.80
    return {
        'gate': 'SHOULD_WORK',
        'result': 'PASS' if passed else 'FAIL',
        'post_2020_ratio': results['post_2020_ratio'],
        'threshold': 0.80,
        'margin': results['post_2020_ratio'] - 0.80
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing post-2020 ratio vs 0.80 threshold

#### Additional Figures (LLM Autonomous)

1. **Benchmark Creation Timeline**: Histogram of benchmark creation dates (2015-2024), colored by type (emergent vs traditional)
2. **Cumulative Creation Curve**: Line plot showing cumulative emergent-capability benchmarks over time with vertical line at GPT-3 release (June 2020)
3. **Type Distribution by Year**: Stacked bar chart showing emergent vs traditional benchmark counts per year

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `post_2020_ratio > 0.80`

**Expected Outcome:** Based on Exa research, key emergent-capability benchmarks (MMLU Sep 2020, HumanEval July 2021, BIG-Bench 2021, TruthfulQA Aug 2021, GSM8K 2021) were created post-2020. Expect ~85-90% post-2020 ratio.

---

## Appendix: Reference Implementations

### Key Benchmark Sources (Verified)

| Benchmark | GitHub/Source | Creation Date | Classification |
|-----------|---------------|---------------|----------------|
| MMLU | hendrycks/test | 2020-09-07 | Emergent |
| HumanEval | openai/human-eval | 2021-07-06 | Emergent |
| BIG-Bench | google/BIG-bench | 2021-01-15 | Emergent |
| TruthfulQA | sylinrl/TruthfulQA | 2021-08-24 | Emergent |
| GSM8K | openai/grade-school-math | 2021 | Emergent |
| HellaSwag | rowanz/hellaswag | 2019 | Traditional |
| WinoGrande | allenai/winogrande | 2020-02 (AAAI-20) | Traditional |

### Data Sources

1. **Papers With Code Official Data**
   - URL: https://github.com/paperswithcode/paperswithcode-data
   - HuggingFace: `pwc-archive/datasets`
   - Format: JSON with benchmark metadata

2. **Semantic Scholar API**
   - URL: https://api.semanticscholar.org/
   - Use: Backup date lookup for benchmarks without PWC paper links

3. **Manual Verification Set**
   - Top 20 emergent-capability benchmarks manually verified with arxiv dates

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18

### Workflow History for This Hypothesis
- 2026-08-18: H-M2 set to IN_PROGRESS (Phase 2C start)
- 2026-08-18: Phase 2C experiment design completed

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web Search)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
