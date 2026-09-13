# Product Requirements Document: h-m2 Semantic NLP Extraction Validation

**Date:** 2026-07-14
**Author:** Anonymous
**Hypothesis:** h-m2 (Semantic NLP Extraction Effectiveness)
**Type:** MECHANISM (Causal Step 2)
**Gate:** MUST_WORK (Recall ≥80%, Precision ≥70%, Kappa ≥0.70)

---

## Executive Summary

### Purpose

Validate that LLM-based semantic extraction can reliably extract assumptions (from MCP tool query parameters) and claims (from tool result content) with ≥80% recall and ≥70% precision compared to human gold standard annotations.

### Success Criteria

**Primary Gate (MUST_WORK):**
1. Extraction recall ≥80% (LLM finds most human-identified items)
2. Extraction precision ≥70% (low hallucination rate)
3. Inter-rater agreement ≥70% Cohen's Kappa (validates gold standard)

**If Gate Fails:** Workflow STOPS → Iterate prompts OR switch to hybrid (LLM + human review)

### Context

- **Prerequisites:** h-m1 COMPLETED (97.48% NL content validated)
- **Dataset:** Reuse h-m1 MCP traces (50-sample subset: 25 queries, 25 results)
- **Continuation:** Builds on h-m1's validated dataset
- **Critical Path:** h-m2 is bottleneck (2-3 weeks, Risk R2: LLM unreliability 40%)

---

## Problem Statement

### Core Challenge

Research pipelines using MCP tool architecture generate trace logs with natural language content in both query parameters (assumptions/requirements) and result content (claims/evidence). Validating constraint violations requires extracting these semantic elements reliably.

**Current State:** h-m1 validated that 97.48% of tool calls contain ≥10 words of natural language text.

**Required:** Prove that LLM-based extraction can recover ≥80% of assumptions/claims with ≥70% precision (vs human gold standard).

### Why This Matters

- h-m3 (constraint inference) depends on reliable extraction
- Without ≥80% recall, too many violations missed
- Without ≥70% precision, too many false positives
- Gate failure blocks entire pipeline validation hypothesis

---

## Functional Requirements

### FR-1: Dataset Preparation

**Priority:** P0 (MUST_WORK gate)

**Description:** Load and sample 50 tool calls from h-m1 validated MCP traces.

**Acceptance Criteria:**
- 25 query-text samples (for assumption extraction, Layer 2)
- 25 result-text samples (for claim extraction, Layer 3)
- All samples have ≥10 words NL content (h-m1 threshold)
- Stratified sampling by: pipeline outcome (success/fail), tool type (research/data processing)
- Sensitive content anonymized (paths, usernames)

**Dependencies:** h-m1 MCP trace dataset (`{research_folder}/mcp_traces/*.jsonl`)

**Implementation Notes:**
```python
# Use h-m1 trace loading infrastructure
def load_mcp_traces(trace_folder, sample_size=50):
    # Filter for NL content (≥10 words, h-m1 validated)
    # Stratified sample: 25 queries, 25 results
    return {"queries": queries, "results": results}
```

---

### FR-2: LLM Extraction System

**Priority:** P0 (MUST_WORK gate)

**Description:** Implement LLM-based semantic extraction with multi-vote consistency.

**Acceptance Criteria:**
- Support Claude Sonnet 4.5 or GPT-4 API
- Temperature 0.0 (deterministic extraction)
- Few-shot prompt template (3-5 examples)
- Multi-vote consensus (3 independent calls, ≥2/3 agreement)
- Extract assumptions from query text OR claims from result text
- Output format: List[Dict] with `{text, span, confidence}`

**Dependencies:** Anthropic/OpenAI API credentials

**Implementation Notes:**
```python
class LLMExtractor:
    def extract_assumptions(self, query_text):
        # Few-shot prompt with examples
        # Multi-vote: 3 calls, majority consensus
        pass
    
    def extract_claims(self, result_text):
        # Few-shot prompt with examples
        # Multi-vote: 3 calls, majority consensus
        pass
```

---

### FR-3: Human Annotation Gold Standard

**Priority:** P0 (MUST_WORK gate)

**Description:** Collect manual human annotations as ground truth.

**Acceptance Criteria:**
- 2 independent human annotators with research pipeline domain expertise
- Annotation guidelines: Extract ALL assumptions (queries) or claims (results)
- Annotation format: List of (text span, label, confidence)
- Inter-rater agreement ≥70% Cohen's Kappa
- Consensus annotations via discussion (gold standard)

**Dependencies:** 2 domain expert annotators (4-6 hours each)

**Implementation Notes:**
```python
# Annotation template generation
def create_annotation_template(tool_call):
    return {
        "tool_call_id": call["id"],
        "text_source": call["parameters"] or call["result"],
        "annotations": [],  # Manual fill: [(span, label, confidence)]
        "annotator_id": "",
        "timestamp": ""
    }
```

---

### FR-4: Evaluation Metrics Computation

**Priority:** P0 (MUST_WORK gate)

**Description:** Compare LLM extracts vs human gold standard.

**Acceptance Criteria:**
- Precision = (LLM ∩ Human) / |LLM| ≥0.70
- Recall = (LLM ∩ Human) / |Human| ≥0.80
- F1 score = harmonic mean of precision/recall
- Inter-rater Kappa between 2 annotators ≥0.70
- Per-category breakdown (assumptions vs claims)
- Error analysis: hallucinations (false positives) vs misses (false negatives)

**Dependencies:** sklearn.metrics library

**Implementation Notes:**
```python
from sklearn.metrics import cohen_kappa_score

def evaluate_extraction(llm_items, human_items):
    tp = len(set(llm_items) & set(human_items))
    fp = len(set(llm_items) - set(human_items))
    fn = len(set(human_items) - set(llm_items))
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0  # ≥0.70
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0     # ≥0.80
    return {"precision": precision, "recall": recall}
```

---

### FR-5: Visualization Generation

**Priority:** P1

**Description:** Generate figures for validation report.

**Acceptance Criteria:**
- **Mandatory:** Precision-Recall bar chart with threshold lines (0.70, 0.80, 0.70 for Kappa)
- **Recommended:** Confusion matrix heatmap (TP/FP/FN/TN)
- **Recommended:** Per-category performance (assumptions vs claims)
- **Recommended:** Error analysis examples (sample false positives/negatives)
- All figures saved to `{hypothesis_folder}/figures/`

**Dependencies:** matplotlib or plotly

**Implementation Notes:**
```python
# Gate metrics comparison (mandatory)
import matplotlib.pyplot as plt

def plot_gate_metrics(precision, recall, kappa):
    metrics = ["Precision", "Recall", "Kappa"]
    scores = [precision, recall, kappa]
    thresholds = [0.70, 0.80, 0.70]
    
    fig, ax = plt.subplots()
    ax.bar(metrics, scores, alpha=0.7)
    ax.axhline(y=0.70, color='r', linestyle='--', label='Min Threshold')
    ax.axhline(y=0.80, color='orange', linestyle='--')
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title("h-m2 Gate Metrics (MUST_WORK)")
    plt.savefig(f"{hypothesis_folder}/figures/gate_metrics.png")
```

---

### FR-6: Validation Report Generation

**Priority:** P0 (MUST_WORK gate)

**Description:** Generate 04_validation.md with gate pass/fail decision.

**Acceptance Criteria:**
- Summary: Precision, Recall, Kappa scores
- Gate Decision: PASS (all ≥ thresholds) or FAIL (any < threshold)
- Error Analysis: Sample false positives and false negatives
- Next Actions: If PASS → proceed to h-m3; If FAIL → iterate prompts
- References to generated figures

**Dependencies:** All FRs complete

**Implementation Notes:**
```python
def generate_validation_report(results, figures_path):
    gate_pass = (
        results["precision"] >= 0.70 and
        results["recall"] >= 0.80 and
        results["kappa"] >= 0.70
    )
    
    with open(f"{hypothesis_folder}/04_validation.md", "w") as f:
        f.write(f"# Validation Report: h-m2\n")
        f.write(f"Gate: {'PASS' if gate_pass else 'FAIL'}\n")
        f.write(f"Precision: {results['precision']:.4f} (≥0.70)\n")
        f.write(f"Recall: {results['recall']:.4f} (≥0.80)\n")
        # ...
```

---

## Data Requirements

### Primary Dataset

**Name:** YouRA MCP Traces (50-sample validation subset)

**Source:** h-m1 validated dataset (`{research_folder}/mcp_traces/*.jsonl`)

**Statistics:**
- Total tool calls in full dataset: 596 (from h-m1)
- Sample size: 50 (25 queries, 25 results)
- NL content: ≥10 words per call (h-m1 validated: 97.48%)
- Source pipelines: 20 executions (10 success, 10 fail)

**Preprocessing:**
1. Load JSONL trace files
2. Extract tool call records (tool_name, parameters, results)
3. Filter for NL content ≥10 words
4. Stratified sampling (query/result, success/fail, tool type)
5. Anonymize sensitive content

**Access:** Local files (no download required, reuse h-m1 dataset)

---

### Ground Truth Annotations

**Type:** Human-annotated gold standard

**Format:** JSON files with annotated items per tool call

**Annotators:** 2 domain experts (research pipeline background)

**Annotation Process:**
1. Extract ALL assumptions (from queries) or claims (from results)
2. Annotation format: `[{text, span, label, confidence}, ...]`
3. Independent annotation (no communication)
4. Compute inter-rater agreement (Cohen's Kappa)
5. Resolve disagreements via discussion → Consensus gold standard

**Quality Threshold:** Kappa ≥0.70 (validates annotation reliability)

---

## Environment Requirements

### Dependencies

**Core Libraries:**
- Python 3.9+
- anthropic or openai (LLM API client)
- sklearn (metrics computation)
- matplotlib or plotly (visualization)
- jsonlines (trace file loading)

**Optional:**
- pandas (data manipulation)
- numpy (numerical operations)

**Installation:**
```bash
pip install anthropic openai scikit-learn matplotlib jsonlines pandas numpy
```

---

### Configuration

**LLM API:**
- Model: Claude Sonnet 4.5 (`claude-sonnet-4-5`) or GPT-4
- API Key: Set via environment variable `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
- Temperature: 0.0 (deterministic)
- Max tokens: 2000

**Paths:**
- Trace folder: `{research_folder}/mcp_traces/`
- Output folder: `{hypothesis_folder}` (h-m2/)
- Figures folder: `{hypothesis_folder}/figures/`

**Execution Cost:**
- API calls: 150 (50 samples × 3 votes)
- Tokens: ~75k total (~500 per call)
- Cost estimate: ~$1.50 (Claude Sonnet pricing)

---

## Non-Functional Requirements

### NFR-1: Reproducibility

**Requirement:** All experiments must be fully reproducible.

**Implementation:**
- Set random seed for sampling: `random.seed(42)`
- LLM temperature 0.0 (deterministic extraction)
- Save LLM prompts and responses
- Version all dependencies in requirements.txt
- Save git commit hash in validation report

---

### NFR-2: Transparency

**Requirement:** All design decisions must be traceable to sources.

**Implementation:**
- Reference all Archon KB queries in experiment brief
- Cite sklearn documentation for metrics
- Note Exa MCP unavailability (fallback to literature patterns)
- Traceability matrix in experiment brief Appendix E

---

### NFR-3: Performance

**Requirement:** Execution time reasonable for interactive workflow.

**Targets:**
- LLM extraction: ≤1 hour (automated, 150 API calls)
- Human annotation: 4-6 hours (2 annotators, manual)
- Evaluation: ≤30 minutes (automated metrics computation)
- Total: ~6-8 hours (mostly human annotation)

---

### NFR-4: Error Handling

**Requirement:** Graceful handling of API failures and edge cases.

**Implementation:**
- Retry LLM API calls with exponential backoff (max 3 retries)
- Handle empty extraction results (log warning, precision/recall = 0)
- Validate annotation files exist before loading
- Check inter-rater Kappa threshold before using gold standard

---

## Success Metrics

### Primary Success (MUST_WORK Gate)

1. **Extraction Recall ≥80%**
   - Metric: (LLM ∩ Human) / |Human|
   - Threshold: 0.80
   - Interpretation: LLM finds ≥80% of human-identified items

2. **Extraction Precision ≥70%**
   - Metric: (LLM ∩ Human) / |LLM|
   - Threshold: 0.70
   - Interpretation: ≤30% hallucination rate

3. **Inter-Rater Agreement ≥70%**
   - Metric: Cohen's Kappa between 2 annotators
   - Threshold: 0.70
   - Interpretation: Gold standard is reliable

**Gate Decision:** PASS if ALL three thresholds met, FAIL if ANY threshold missed.

---

### Secondary Metrics

- **F1 Score:** Harmonic mean of precision/recall (target: ≥0.75)
- **Per-Category Performance:** Separate precision/recall for assumptions vs claims
- **Error Patterns:** Hallucination types (invented items) vs miss types (overlooked items)

---

## Dependencies

### Prerequisites

**Hypothesis h-m1:**
- Status: COMPLETED
- NL presence validated: 97.48% (≥90% threshold)
- Dataset: 596 tool calls across 20 pipeline traces
- Validation report: `h-m1/04_validation.md`

**Critical Dependency:** h-m1 must be COMPLETED before h-m2 can proceed. Dataset quality confirmed (high NL content enables extraction).

---

### External Services

**LLM API (Anthropic or OpenAI):**
- Required for LLM extraction
- API key must be configured
- Cost: ~$1.50 for 150 API calls

**Human Annotators:**
- 2 domain experts with research pipeline background
- Availability: 4-6 hours each
- Training: 30 minutes on annotation guidelines

---

## Risks & Mitigations

### Risk R2: LLM Extraction Unreliability (HIGH, 40% probability)

**Impact:** Precision or recall below thresholds → Gate FAIL → Workflow STOP

**Mitigation M2:**
1. Prompt engineering: Few-shot examples (3-5 per task)
2. Multi-vote consistency: 3 independent extractions, majority consensus
3. Fallback: Iterate prompt design OR switch to hybrid (LLM + human review)

**Residual Risk:** 20% (after mitigation)

---

### Risk: Inter-Rater Disagreement (MEDIUM, 25% probability)

**Impact:** Kappa <0.70 → Gold standard unreliable → Cannot validate LLM

**Mitigation:**
1. Annotation guidelines: Clear definitions for assumptions/claims
2. Training session: 30 minutes with examples
3. Disagreement resolution: Discussion to consensus
4. If Kappa still <0.70: Add 3rd annotator OR refine guidelines

---

### Risk: API Rate Limits or Failures (LOW, 10% probability)

**Impact:** Experiment cannot complete extraction phase

**Mitigation:**
1. Exponential backoff with retries (max 3 attempts)
2. Save intermediate results after each sample
3. Resume from checkpoint if interrupted
4. Fallback model: Switch from Claude to GPT-4 or vice versa

---

## Timeline Estimate

**Total Duration:** ~6-8 hours (within 1 day)

**Breakdown:**
1. Dataset preparation: 30 minutes (reuse h-m1 infrastructure)
2. LLM extraction: 1 hour (automated, 150 API calls)
3. Human annotation: 4-6 hours (2 annotators × 2-3 hours each, parallel)
4. Evaluation metrics: 30 minutes (automated)
5. Visualization: 30 minutes (automated figure generation)
6. Validation report: 30 minutes (write 04_validation.md)

**Critical Path:** Human annotation (4-6 hours, cannot be automated)

---

## Appendix: Traceability Matrix

| Requirement | Source | Reference |
|------------|--------|-----------|
| Sample size (50 calls) | Phase 2B | h-m2 verification protocol |
| NL content threshold (≥10 words) | h-m1 validation | h-m1/04_validation.md |
| LLM extraction method | First principles | Anthropic/OpenAI API best practices |
| Few-shot prompt template | Literature | Chen et al. NLP research |
| Multi-vote consistency (N=3) | First principles | Consensus-based extraction |
| Inter-rater Kappa ≥0.70 | Archon KB | OpenReview M3Y74vmsMcY |
| Precision ≥0.70, Recall ≥0.80 | Phase 2B | h-m2 success criteria |
| sklearn metrics | sklearn docs | sklearn.metrics documentation |
| Confusion matrix visualization | Standard practice | NLP evaluation best practices |

---

## Notes

**Transparency:** Due to Exa MCP unavailability (402 error), GitHub implementation search was limited. Experiment design relies on:
1. Established NLP evaluation patterns from literature
2. h-m1 validated dataset (continuation experiment)
3. Standard libraries (sklearn, Anthropic/OpenAI SDKs)
4. Phase 2B hypothesis success criteria

**Next Phase:** Phase 3 Implementation Planning → Architecture, Logic, Config design
