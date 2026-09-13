# Product Requirements Document: h-m2

**Date:** 2026-08-24  
**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Gate:** MUST_WORK  
**Complexity Tier:** 2 (Medium)  
**Implementation Budget:** 30 tokens

---

## Hypothesis Statement

Matched correction routing (entity-error → RAG) achieves higher success rates than mismatched routing (entity-error → COT) by ≥20 percentage points or ≥50% relative improvement, replicated across GPT-3.5 and Llama-2-7B.

---

## Success Criteria (MUST_WORK Gate)

**Pass Condition:**
- (Matched routing success rate - Mismatched routing success rate) ≥ 20 percentage points
- OR relative improvement ≥ 50%
- **Must replicate across BOTH GPT-3.5 AND Llama-2-7B**

**Fail Condition:**
- Difference < 20 points AND relative improvement < 50% in either model
- OR opposite direction (COT > RAG for entity-errors)

---

## Implementation Requirements

### 1. Prerequisite Integration

**Required from h-m1:**
- Entropy classifier (threshold 0.32)
- Entity-error classification function
- TruthfulQA dataset subset (entity-error cases)
- Gold labels for entity-error vs non-entity-error

**Integration Points:**
- Load h-m1 classifier outputs: `h-m1/code/results/entropy_results.json`
- Filter cases where `predicted_class == "entity-error"` and entropy < 0.32
- Extract 50 entity-error cases per model (GPT-3.5 and Llama-2-7B)

### 2. Dataset Preparation

**Dataset**: TruthfulQA entity-error cases (from h-m1 outputs)

**Requirements:**
- Load entity-error cases identified by h-m1 classifier
- Select 50 entity-error cases for GPT-3.5-turbo
- Select 50 entity-error cases for Llama-2-7B
- Total: N=100 entity-error failures
- No train/test split needed (evaluation-only experiment)

**Data Schema:**
```python
{
    "question": str,           # TruthfulQA question
    "incorrect_answer": str,   # Model's incorrect response
    "gold_answer": str,        # Correct answer
    "entropy": float,          # From h-m1 classifier
    "predicted_class": str,    # "entity-error"
    "model": str              # "gpt-3.5-turbo" or "llama-2-7b"
}
```

### 3. Model Implementation

#### Baseline: Mismatched Routing (entity-error → COT)

**Components:**
- LLMs: GPT-3.5-turbo (OpenAI API) and Llama-2-7B (HuggingFace)
- Correction method: Chain-of-Thought prompting
- Temperature: 0.7
- Max tokens: 150

**Prompt Template:**
```
Question: {question}
Incorrect answer: {incorrect_answer}

Let's think step by step to find the correct answer:
```

**Implementation:**
```python
from openai import OpenAI

def cot_correct(question, incorrect_answer, model_name):
    """Chain-of-thought correction baseline"""
    prompt = f"Question: {question}\nIncorrect answer: {incorrect_answer}\n\nLet's think step by step to find the correct answer:"
    
    if model_name == "gpt-3.5-turbo":
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content
    else:  # llama-2-7b
        # HuggingFace implementation
        pass
```

#### Proposed: Matched Routing (entity-error → RAG)

**Components:**
- Entity extraction: spaCy NER
- Retrieval corpus: Wikipedia (API or local dump)
- Retrieval method: BM25 or dense retrieval (sentence-transformers)
- Top-k: 3 documents
- Context injection: Prepend retrieved docs to prompt
- LLMs: Same as baseline (GPT-3.5-turbo, Llama-2-7B)

**Implementation:**
```python
import spacy
from sentence_transformers import SentenceTransformer
import wikipedia

nlp = spacy.load("en_core_web_sm")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def rag_correct(question, incorrect_answer, model_name):
    """RAG correction with Wikipedia retrieval"""
    # 1. Extract entities
    doc = nlp(question)
    entities = [ent.text for ent in doc.ents]
    
    # 2. Retrieve Wikipedia documents
    docs = []
    for entity in entities[:3]:  # Top 3 entities
        try:
            summary = wikipedia.summary(entity, sentences=2)
            docs.append(summary)
        except:
            continue
    
    # 3. Build context-augmented prompt
    context = "\n".join(docs)
    prompt = f"Context: {context}\n\nQuestion: {question}\nIncorrect answer: {incorrect_answer}\n\nBased on the context, provide the correct answer:"
    
    # 4. Generate corrected answer
    if model_name == "gpt-3.5-turbo":
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content
    else:  # llama-2-7b
        # HuggingFace implementation
        pass
```

### 4. Evaluation Protocol

**Metrics:**
- **Correction Success Rate**: % of corrected answers matching gold-standard correct answers
- **Difference (Matched - Mismatched)**: Percentage point improvement
- **Relative Improvement**: ((matched - mismatched) / mismatched) × 100%

**Evaluation Function:**
```python
def evaluate_correction(corrected_answer, gold_answer):
    """Binary correctness evaluation"""
    # Exact match
    if corrected_answer.strip().lower() == gold_answer.strip().lower():
        return 1.0
    
    # GPT-judge for semantic equivalence
    judge_prompt = f"Are these answers equivalent?\nAnswer A: {corrected_answer}\nAnswer B: {gold_answer}\nRespond 'yes' or 'no'."
    judge_response = gpt_judge(judge_prompt)
    return 1.0 if "yes" in judge_response.lower() else 0.0

# Compute success rates
matched_rate = sum(evaluate_correction(x["corrected"], x["gold"]) for x in matched_results) / len(matched_results)
mismatched_rate = sum(evaluate_correction(x["corrected"], x["gold"]) for x in mismatched_results) / len(mismatched_results)
difference = matched_rate - mismatched_rate
relative_improvement = ((matched_rate - mismatched_rate) / mismatched_rate) * 100 if mismatched_rate > 0 else 0
```

**Gate Check:**
```python
def check_gate(matched_rate, mismatched_rate, model_name):
    """MUST_WORK gate evaluation"""
    difference = matched_rate - mismatched_rate
    relative_improvement = ((matched_rate - mismatched_rate) / mismatched_rate) * 100 if mismatched_rate > 0 else 0
    
    gate_pass = (difference >= 0.20) or (relative_improvement >= 50.0)
    
    return {
        "model": model_name,
        "matched_rate": matched_rate,
        "mismatched_rate": mismatched_rate,
        "difference": difference,
        "relative_improvement": relative_improvement,
        "gate_pass": gate_pass
    }
```

### 5. Replication Requirement

**Models:**
- GPT-3.5-turbo (OpenAI API)
- Llama-2-7B (HuggingFace: `meta-llama/Llama-2-7b-chat-hf`)

**Replication Criterion:**
- BOTH models must show ≥20pp difference OR ≥50% relative improvement
- Experiment fails if only one model meets gate condition

### 6. Visualization Requirements

**Mandatory Figure:**
- Gate metrics comparison: Target vs actual metrics bar chart
  - X-axis: Models (GPT-3.5, Llama-2-7B)
  - Y-axis: Success rate (%)
  - Bars: Matched (green), Mismatched (red), Gate threshold line (dotted)

**Additional Figures:**
1. **Success Rate Comparison**: Bar chart showing matched vs mismatched success rates for both models
2. **Per-Model Breakdown**: Grouped bar chart (GPT-3.5 vs Llama-2-7B, matched vs mismatched)
3. **Distribution of Correction Outcomes**: Histogram showing success/failure counts per condition

**Figure Generation:**
```python
import matplotlib.pyplot as plt

def plot_gate_metrics(results_gpt, results_llama):
    """Gate metrics comparison figure"""
    models = ["GPT-3.5", "Llama-2-7B"]
    matched_rates = [results_gpt["matched_rate"], results_llama["matched_rate"]]
    mismatched_rates = [results_gpt["mismatched_rate"], results_llama["mismatched_rate"]]
    
    x = range(len(models))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar([i - width/2 for i in x], matched_rates, width, label='Matched (RAG)', color='green', alpha=0.7)
    ax.bar([i + width/2 for i in x], mismatched_rates, width, label='Mismatched (COT)', color='red', alpha=0.7)
    
    # Gate threshold line
    ax.axhline(y=0.20, color='black', linestyle='--', label='Gate Threshold (20pp diff)')
    
    ax.set_xlabel('Model')
    ax.set_ylabel('Success Rate')
    ax.set_title('h-m2: Gate Metrics Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend()
    
    plt.savefig("h-m2/figures/gate_metrics_comparison.png")
    plt.close()
```

---

## Outputs

**Required Files:**
- `h-m2/code/matched_routing.py` - Matched routing implementation (RAG)
- `h-m2/code/baseline_routing.py` - Mismatched routing baseline (COT)
- `h-m2/code/evaluate.py` - Evaluation script
- `h-m2/code/requirements.txt` - Python dependencies

**Required Figures:**
- `h-m2/figures/gate_metrics_comparison.png` - Gate metrics comparison (mandatory)
- `h-m2/figures/success_rate_comparison.png` - Success rate comparison
- `h-m2/figures/per_model_breakdown.png` - Per-model breakdown
- `h-m2/figures/correction_outcomes.png` - Distribution of correction outcomes

**Results File:**
- `h-m2/code/results/correction_results.json` - Full results with per-sample outcomes

---

## Dependencies

**Python Packages:**
- openai (OpenAI API)
- transformers (HuggingFace Llama-2-7B)
- spacy (Entity extraction)
- wikipedia-api (Wikipedia retrieval)
- sentence-transformers (Dense retrieval)
- matplotlib (Visualization)
- numpy (Metrics computation)
- scikit-learn (Statistical tests)

**External Resources:**
- OpenAI API key (for GPT-3.5-turbo)
- HuggingFace access token (for Llama-2-7B)
- Wikipedia API access
- spaCy model: `en_core_web_sm`

---

## Risks and Mitigation

**Risk 1: Wikipedia API rate limiting**
- Mitigation: Cache Wikipedia summaries, implement retry logic with exponential backoff

**Risk 2: Entity extraction failures**
- Mitigation: Fallback to keyword-based retrieval if no entities found

**Risk 3: Llama-2-7B memory requirements**
- Mitigation: Use 4-bit quantization (bitsandbytes) if GPU memory insufficient

**Risk 4: GPT-judge semantic equivalence false positives**
- Mitigation: Manual spot-check 10% of GPT-judge decisions, report inter-rater agreement

---

## Budget Allocation (Tier 2: 30 tokens)

**Token Breakdown:**
- Data preparation: 5 tokens
- RAG pipeline implementation: 10 tokens
- COT baseline implementation: 5 tokens
- Evaluation + gate check: 5 tokens
- Visualization: 3 tokens
- Failsafe buffer: 2 tokens

**Total:** 30 tokens

---

## Acceptance Criteria

**Code Requirements:**
1. Code runs without error
2. Loads h-m1 entity-error cases correctly
3. Implements RAG pipeline with Wikipedia retrieval
4. Implements COT baseline with same LLMs
5. Evaluates both conditions on same dataset

**Gate Requirements:**
1. GPT-3.5: (matched - mismatched) ≥ 20pp OR relative improvement ≥ 50%
2. Llama-2-7B: (matched - mismatched) ≥ 20pp OR relative improvement ≥ 50%
3. BOTH models must pass gate condition

**Output Requirements:**
1. All required figures generated and saved
2. Results JSON contains per-sample outcomes
3. Gate check results logged with clear PASS/FAIL status

---

*This PRD guides Phase 4 implementation. Architecture, Logic, and Config documents provide detailed specifications.*
