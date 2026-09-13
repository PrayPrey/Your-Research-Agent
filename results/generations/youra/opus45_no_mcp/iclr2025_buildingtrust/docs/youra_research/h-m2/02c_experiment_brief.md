# Experiment Design: H-M2

**Date:** 2026-08-19
**Author:** YouRA Research Pipeline
**Hypothesis Statement:** Under CoT+confidence conditions, if reasoning chains are generated, then outputs will contain uncertainty indicators (hedging words, qualifications, alternatives), because complex reasoning surfaces epistemic uncertainty.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Template** - Tests causal mechanism step 2: reasoning chains surface uncertainty markers.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (VALIDATED), H-M1 (VALIDATED)
**Gate Status:** SHOULD_WORK (failure triggers EXPLORE, not STOP)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (CoT forces explicit reasoning articulation)

### Gate Condition
**SHOULD_WORK Gate:**
- Pass: Hedging markers present in >30% of CoT outputs
- Pass: Marker frequency correlates with item difficulty (optional secondary)
- Fail Action: EXPLORE (expand hedging marker dictionary)

---

## Continuation Context

H-M1 validated that CoT prompting reliably produces multi-step reasoning chains (100% rate, mean 2.61 steps). H-M2 tests whether these chains contain epistemic uncertainty signals.

### Previous Hypothesis Results (H-M1)
- CoT reasoning rate: 1.0 (all outputs contain reasoning)
- Mean step count: 2.61
- Baseline reasoning rate: 0.0
- All gates passed

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP Archon unavailable - using literature-grounded design*

**Hedging Language in LLM Outputs:**
- Linguistic hedging markers well-established in NLP literature (Hyland 1998, Lakoff 1973)
- Categories: epistemic adverbs (possibly, perhaps), modal verbs (might, could), approximators (about, around)
- LLM uncertainty verbalization studied in Tian et al. 2023, Xiong et al. 2023

### Archon Code Examples

*MCP unavailable - using standard NLP patterns*

**Hedging Detection Pattern:**
```python
HEDGING_MARKERS = [
    'might', 'may', 'could', 'possibly', 'perhaps',
    'uncertain', 'unsure', 'alternatively', 'however',
    'although', 'but', 'probably', 'likely', 'unlikely'
]
```

### Exa GitHub Implementations

*MCP Exa unavailable - using established patterns*

**Reference implementations for hedging detection:**
1. spaCy + regex for hedging marker extraction
2. NLTK sentence tokenization for context windows
3. Simple keyword counting for PoC

### Implementation Priority Assessment

**CRITICAL: For hedging detection, simple keyword matching sufficient for PoC**

**Recommended Implementation Path:**
- Primary: Regex-based keyword matching (fast, interpretable)
- Fallback: spaCy NER + dependency parsing (if keyword matching insufficient)
- Justification: H-M1 validated reasoning chain presence; H-M2 needs only marker presence/count

### Code Analysis (Serena MCP)

*MCP Serena unavailable - not needed for this PoC*

No existing codebase to analyze. This is new experiment code.

---

## Experiment Specification

### Dataset

**Name:** TruthfulQA (Generation)
**Version:** Latest from HuggingFace
**Source:** HuggingFace datasets hub
**Type:** standard

| Split | Size | Usage |
|-------|------|-------|
| Validation | 817 items | Full evaluation |

**Preprocessing:**
1. Load truthful_qa generation subset
2. Extract question field
3. No filtering (use all 817 items)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: truthful_qa (generation config)
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("truthful_qa", "generation")
questions = dataset["validation"]["question"]  # 817 items
```

### Models

#### Baseline Model

**Name:** GPT-3.5-turbo
**Source:** OpenAI API
**Type:** Instruction-tuned chat model

**Loading Information** (for Phase 4 download):
- Method: OpenAI API
- Identifier: gpt-3.5-turbo
- Code:
```python
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    temperature=0
)
```

#### Proposed Model

**Architecture:** Same model, CoT+confidence prompting condition

**Core Mechanism Implementation:**

```python
# H-M2 Core: Hedging Marker Detection in CoT Outputs
# 10-30 lines as specified

HEDGING_MARKERS = [
    'might', 'may', 'could', 'possibly', 'perhaps',
    'uncertain', 'unsure', 'alternatively', 'however',
    'although', 'probably', 'likely', 'unlikely',
    'but', 'not sure', 'hard to say', 'difficult to determine'
]

def count_hedging_markers(text: str) -> dict:
    """Count hedging markers in CoT reasoning chain."""
    text_lower = text.lower()
    counts = {}
    total = 0
    for marker in HEDGING_MARKERS:
        count = text_lower.count(marker)
        if count > 0:
            counts[marker] = count
            total += count
    return {
        'markers_found': counts,
        'total_count': total,
        'has_hedging': total > 0
    }

def extract_reasoning_chain(output: str) -> str:
    """Extract reasoning portion before confidence statement."""
    # Split at confidence marker
    confidence_markers = ['confidence:', 'my confidence', 'i am confident']
    text_lower = output.lower()
    for marker in confidence_markers:
        if marker in text_lower:
            idx = text_lower.find(marker)
            return output[:idx]
    return output  # No confidence marker found

def analyze_hedging(cot_output: str) -> dict:
    """Main analysis function for H-M2."""
    reasoning = extract_reasoning_chain(cot_output)
    hedging_result = count_hedging_markers(reasoning)
    return {
        'reasoning_text': reasoning,
        **hedging_result
    }
```

### Training Protocol

**Not applicable for this PoC** - No model training required.

This is an inference-only experiment:
1. Generate CoT+confidence outputs for all 817 TruthfulQA items
2. Analyze outputs for hedging markers
3. Compute metrics

**Generation Parameters:**
- Temperature: 0 (deterministic)
- Max tokens: 500 (sufficient for CoT reasoning)
- Model: gpt-3.5-turbo (or mock mode for validation)

### Evaluation

**Primary Metric:** Hedging presence rate
- Definition: Fraction of CoT outputs containing at least one hedging marker
- Formula: `sum(has_hedging) / total_outputs`
- Threshold: >30% for SHOULD_WORK gate

**Secondary Metric:** Mean hedging count per output
- Definition: Average number of hedging markers per CoT output
- Formula: `sum(total_count) / total_outputs`

**Tertiary Metric (optional):** Hedging-difficulty correlation
- Definition: Correlation between hedging count and item difficulty
- Note: Requires difficulty labels (may use answer entropy as proxy)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Text analysis (no ML metrics needed)
- Library: Python stdlib (collections.Counter)
- Code:
```python
def compute_metrics(results: list[dict]) -> dict:
    """Compute H-M2 metrics from analysis results."""
    n = len(results)
    hedging_present = sum(1 for r in results if r['has_hedging'])
    total_markers = sum(r['total_count'] for r in results)
    
    return {
        'hedging_presence_rate': hedging_present / n,
        'mean_hedging_count': total_markers / n,
        'n_samples': n,
        'gate_pass': (hedging_present / n) > 0.30
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing hedging presence rate vs 30% threshold

#### Additional Figures (LLM Autonomous)

1. **Hedging Marker Distribution**: Horizontal bar chart of marker frequencies
2. **Hedging Count Histogram**: Distribution of marker counts per output
3. **Top Hedging Markers**: Pie chart or bar chart of most common markers

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `hedging_presence_rate > 0.30` (>30% of outputs have hedging)

**SHOULD_WORK Gate Logic:**
- Pass: Proceed to H-M3
- Fail: EXPLORE alternative hedging dictionaries, do not STOP pipeline

---

## Appendix: Reference Implementations

### A. Hedging Marker Literature

**Hyland (1998):** Hedging in Scientific Research Articles
- Categories: shields, approximators, author involvement markers

**Lakoff (1973):** Hedges: A Study in Meaning Criteria
- Foundational work on hedging language

**Tian et al. (2023):** Just Ask for Calibration
- LLM confidence verbalization patterns

### B. Extended Hedging Dictionary (for EXPLORE if fail)

```python
EXTENDED_HEDGING = HEDGING_MARKERS + [
    'seem', 'appears', 'tends', 'generally', 'typically',
    'in some cases', 'it depends', 'not always', 'sometimes',
    'often', 'rarely', 'approximately', 'roughly', 'around',
    'i think', 'i believe', 'in my opinion', 'arguably'
]
```

### C. Sample Analysis Code

```python
# End-to-end H-M2 validation script structure
def run_hm2_validation(outputs: list[str]) -> dict:
    """Run full H-M2 validation on CoT outputs."""
    results = [analyze_hedging(output) for output in outputs]
    metrics = compute_metrics(results)
    
    # Gate check
    gate_status = "PASS" if metrics['gate_pass'] else "FAIL"
    
    return {
        'metrics': metrics,
        'gate_status': gate_status,
        'individual_results': results
    }
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- H-E1: VALIDATED (extraction >95%, ECE computable)
- H-M1: VALIDATED (CoT reasoning rate 1.0, mean steps 2.61)
- H-M2: IN_PROGRESS (current experiment design)

---

*MCP Tools Used: None available (Archon, Exa, Serena unavailable)*
*Specifications grounded in linguistics literature and prior LLM calibration research*
*Next Phase: Phase 3 - Implementation Planning*
