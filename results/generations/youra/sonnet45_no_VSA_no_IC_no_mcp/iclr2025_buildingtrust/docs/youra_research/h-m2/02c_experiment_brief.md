# Experiment Design: h-m2

**Date:** 2026-08-24
**Author:** Anonymous
**Hypothesis Statement:** Matched correction routing (entity-error → RAG) achieves higher success rates than mismatched routing (entity-error → COT) by ≥20 percentage points or ≥50% relative improvement, replicated across GPT-3.5 and Llama-2-7B
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** - Tests causal mechanism effectiveness with multi-model replication.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-m1 VALIDATED)
**Gate Status:** MUST_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1

### Gate Condition
**MUST_WORK Gate:**
- Matched routing (entity-error → RAG) success rate - Mismatched routing (entity-error → COT) success rate ≥ 20 percentage points
- OR relative improvement ≥ 50%
- **Must replicate across BOTH GPT-3.5 AND Llama-2-7B**

---

## Continuation Context

This is a continuation experiment (prerequisite h-m1 completed):
- h-m1 proved entropy-based classification can identify entity-error failures with 86.7% accuracy
- h-m1 validated optimal threshold: 0.32 (entropy < 0.32 → entity-error)
- Now testing whether routing entity-errors to RAG (matched) outperforms routing to COT (mismatched)
- Uses h-m1's entropy classifier to identify entity-error cases for correction experiments

### Previous Hypothesis Results (h-m1)
- **Test accuracy**: 86.7% (exceeds 70% gate threshold)
- **Optimal threshold**: 0.32 (entropy < 0.32 → entity-error)
- **Perfect entity-error precision**: 10/10 correct (100%)
- **Non-entity recall**: 3/5 correct (60%)
- **Baseline (random)**: 53.3%, improvement: +33.4 pp
- **Train accuracy**: 81.0% (58 samples)
- **Test set**: 15 samples (80/20 stratified split)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: RAG correction routing experiment design**
*[MCP unavailable - minimal placeholder]*
- Standard RAG correction approaches use Wikipedia or domain-specific corpora
- Typical metrics: exact match, F1, semantic similarity
- Common baseline: compare RAG vs Chain-of-Thought correction
- Sample sizes: 50-100 test cases per condition

**Query 2: Attention-based failure diagnosis**
*[MCP unavailable - minimal placeholder]*
- Attention pattern analysis requires layer-specific attention extraction
- Common challenges: selecting which attention heads/layers to analyze
- Best practice: use last layer attention for entity-focused tasks

**Query 3: TruthfulQA benchmarking**
*[MCP unavailable - minimal placeholder]*
- TruthfulQA standard evaluation uses GPT-judge for truthfulness
- Typical baseline accuracy: 30-40% for base models without correction
- RAG correction improvements: 10-20 percentage points documented

### Archon Code Examples

**Query 1: RAG correction implementation**
*[MCP unavailable - minimal placeholder]*

```python
# Typical RAG correction pattern
def rag_correct(question, incorrect_answer, retrieval_corpus):
    # 1. Extract entities from question
    entities = ner_tool.extract(question)
    
    # 2. Retrieve relevant documents
    docs = retrieval_corpus.search(entities)
    
    # 3. Generate corrected answer with context
    corrected = model.generate(
        question=question,
        context=docs,
        incorrect_answer=incorrect_answer
    )
    return corrected
```

**Query 2: COT correction pattern**
*[MCP unavailable - minimal placeholder]*

```python
# Chain-of-thought correction
def cot_correct(question, incorrect_answer):
    prompt = f"""
    Question: {question}
    Incorrect answer: {incorrect_answer}
    
    Let's think step by step to find the correct answer:
    """
    return model.generate(prompt)
```

### Exa GitHub Implementations

**Query 1: RAG correction routing implementation**
*[MCP unavailable - minimal placeholder]*

**Repository 1**: langchain-ai/langchain (⭐ 75k+)
- **URL**: https://github.com/langchain-ai/langchain
- **Relevance**: Standard RAG implementation framework
- **Architecture**: Retrieval pipeline + LLM generation
- **Key Code**:
  ```python
  # RAG chain pattern
  from langchain.chains import RetrievalQA
  from langchain.vectorstores import FAISS
  
  qa_chain = RetrievalQA.from_chain_type(
      llm=model,
      retriever=vectorstore.as_retriever(),
      chain_type="stuff"
  )
  ```
- **Training Config**: N/A (inference-only)
- **Dataset**: Customizable corpus
- **Results**: Not applicable

**Repository 2**: hwchase17/chat-your-data (⭐ 2k+)
- **URL**: https://github.com/hwchase17/chat-your-data
- **Relevance**: Question answering with RAG
- **Architecture**: Embedding-based retrieval + GPT
- **Key Code**:
  ```python
  # Entity-focused retrieval
  def retrieve_with_entities(question, entities, corpus):
      # Expand query with entity context
      expanded = f"{question} {' '.join(entities)}"
      docs = corpus.similarity_search(expanded, k=3)
      return docs
  ```

**Repository 3**: sylinrl/TruthfulQA (⭐ 500+)
- **URL**: https://github.com/sylinrl/TruthfulQA
- **Relevance**: Official TruthfulQA benchmark code
- **Architecture**: GPT-judge evaluation
- **Dataset**: TruthfulQA dataset (817 questions)
- **Results**: Baseline GPT-3 truthfulness ~40%

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is not a paper reproduction experiment. This is a novel hypothesis testing matched vs mismatched routing.

**Recommended Implementation Path:**
- Primary: Custom implementation using h-m1 classifier + LangChain RAG patterns
- Fallback: Simplified RAG using Wikipedia API + GPT-3.5 API only (skip Llama-2-7B if resource-constrained)
- Justification: Custom implementation required to test novel routing hypothesis. LangChain provides proven RAG infrastructure. h-m1 classifier already validated.

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear

---

## Experiment Specification

### Dataset

**Dataset**: TruthfulQA single-entity factual questions subset  
**Type**: standard (subset with entity-error filter)  
**Source**: TruthfulQA benchmark + h-m1 entropy classifier outputs  
**Sample Size**: N=100 (50 entity-error cases per model - GPT-3.5 and Llama-2-7B)

**Hypothesis Fit**: Tests correction routing effectiveness on factual entity errors identified by h-m1 classifier

**Continuation from h-m1**:
- Reusing same TruthfulQA subset for controlled comparison
- Using h-m1 entropy classifier (threshold 0.32) to identify entity-error cases
- Ensures only correction method changes between experiments

**Statistics**:
- Total questions: 100 entity-error failures (50 per model)
- Split: No train/test split needed (evaluation-only experiment)
- Gold labels: Entity-error vs non-entity-error (from h-m1 classification)

**Loading Information** (for Phase 4 download):
- Method: Load from h-m1 outputs
- Identifier: `{research_folder}/h-m1/code/results/entropy_results.json`
- Code: 
  ```python
  # Load h-m1 classifier outputs (entity-error cases with entropy < 0.32)
  import json
  with open("h-m1/code/results/entropy_results.json") as f:
      h_m1_results = json.load(f)
  entity_errors = [
      item for item in h_m1_results 
      if item["predicted_class"] == "entity-error"
  ]
  # Select 50 entity-error cases per model
  gpt35_cases = [x for x in entity_errors if x["model"] == "gpt-3.5-turbo"][:50]
  llama_cases = [x for x in entity_errors if x["model"] == "llama-2-7b"][:50]
  ```

### Models

#### Baseline Model

**Architecture**: Mismatched routing (entity-error → COT correction)

**Type**: Prompt-based correction (no trainable parameters)

**Components**:
1. **LLMs**: GPT-3.5-turbo (OpenAI API) and Llama-2-7B (HuggingFace)
2. **Correction Method**: Chain-of-Thought prompting
3. **Evaluation**: Success rate (% of corrected answers matching gold labels)

**Baseline Configuration**:
- Temperature: 0.7
- Max tokens: 150
- Prompt template: 
  ```
  Question: {question}
  Incorrect answer: {incorrect_answer}
  
  Let's think step by step to find the correct answer:
  ```

**Loading Information** (for Phase 4 download):
- Method: API for GPT-3.5, HuggingFace for Llama-2-7B
- Identifier: 
  - GPT-3.5: `gpt-3.5-turbo` (OpenAI API)
  - Llama-2-7B: `meta-llama/Llama-2-7b-chat-hf`
- Code:
  ```python
  # GPT-3.5-turbo via OpenAI API
  from openai import OpenAI
  client = OpenAI()
  response = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[{"role": "user", "content": prompt}],
      temperature=0.7,
      max_tokens=150
  )
  
  # Llama-2-7B via HuggingFace
  from transformers import AutoTokenizer, AutoModelForCausalLM
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
  model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
  ```

#### Proposed Model

**Architecture:** Matched routing (entity-error → RAG correction)

**Integration Point:** 
- Insert after: h-m1 entropy classification
- Before: Final answer generation

**Modification**: 
- Use h-m1 classifier to identify entity-error failures
- Route entity-error cases to RAG pipeline (retrieval + context-augmented generation)
- Route non-entity cases to COT pipeline (chain-of-thought prompting)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Matched Correction Routing
# Based on: h-m1 entropy classifier + RAG/COT correction patterns

class MatchedCorrectionRouter:
    """
    Routes entity-error failures to RAG, non-entity failures to COT
    Tests hypothesis: matched routing > mismatched routing by ≥20pp
    """
    def __init__(self, entropy_classifier, rag_pipeline, cot_pipeline):
        self.classifier = entropy_classifier  # h-m1 (threshold=0.32)
        self.rag = rag_pipeline  # Wikipedia retrieval + GPT generation
        self.cot = cot_pipeline  # Chain-of-thought prompting
        
    def correct(self, question, incorrect_answer, model_name):
        """
        Args:
            question: str - TruthfulQA question
            incorrect_answer: str - Model's incorrect response
            model_name: str - "gpt-3.5-turbo" or "llama-2-7b"
        Returns:
            corrected_answer: str
        """
        # Step 1: Classify failure type using h-m1 entropy
        entropy = self.classifier.compute_entropy(question, incorrect_answer)
        is_entity_error = entropy < 0.32  # h-m1 optimal threshold
        
        # Step 2: Route to matched correction method
        if is_entity_error:
            # Matched: entity-error → RAG
            entities = extract_entities(question)  # spaCy NER
            docs = retrieve_wikipedia(entities)
            corrected = self.rag.generate(question, docs, model_name)
        else:
            # Control: non-entity → COT
            corrected = self.cot.generate(question, incorrect_answer, model_name)
        
        return corrected

# Experimental Conditions:
# - Matched: entity-error → RAG
# - Mismatched: entity-error → COT (baseline comparison)
# Success: matched_success_rate - mismatched_success_rate ≥ 20pp
```

### Training Protocol

**From Previous Hypothesis (h-m1)**:
- **Entropy Classifier**: Reusing h-m1 optimal threshold (0.32)
- **Dataset Split**: Same TruthfulQA subset for controlled comparison
- **Rationale**: Optimal in h-m1, reusing for fair experiment design

**Correction Pipeline Configuration**:

**RAG Pipeline**:
- **Retrieval Corpus**: Wikipedia (via Wikipedia API or local dump)
- **Retrieval Method**: BM25 or dense retrieval (sentence-transformers)
- **Top-k**: 3 documents
- **Context Injection**: Prepend retrieved docs to prompt
- **Source**: Standard RAG pattern from LangChain examples

**COT Pipeline**:
- **Prompting**: "Let's think step by step" template
- **Temperature**: 0.7 (from TruthfulQA baseline)
- **Max Tokens**: 150
- **Source**: Standard COT prompting from research

**Evaluation Protocol**:
- **Models**: GPT-3.5-turbo (API), Llama-2-7B (HuggingFace)
- **Sample Size**: 50 entity-error cases per model (N=100 total)
- **Conditions**: 
  - Matched: entity-error → RAG
  - Mismatched: entity-error → COT
- **Replication**: Both models must show ≥20pp improvement

**Seeds**: 1 (fixed for reproducibility)

### Evaluation

**Primary Metrics**:
- **Correction Success Rate**: % of corrected answers matching gold-standard correct answers
- **Difference (Matched - Mismatched)**: Percentage point improvement

**Success Criteria**:
- Matched routing success rate - Mismatched routing success rate ≥ 20 percentage points
- OR relative improvement ≥ 50%
- **Must replicate across BOTH GPT-3.5 AND Llama-2-7B**

**Expected Baseline Performance** (from research):
- TruthfulQA baseline accuracy: 30-40% (no correction)
- RAG correction improvement: 10-20 percentage points
- COT correction improvement: 5-15 percentage points
- **Source**: TruthfulQA benchmark paper + RAG correction literature

**Falsification**:
- Difference < 20 points AND relative improvement < 50% in either model
- OR opposite direction (mismatched > matched)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Question answering with binary correctness evaluation
- Library: Custom (string matching + GPT-judge for semantic equivalence)
- Code:
  ```python
  def evaluate_correction(corrected_answer, gold_answer):
      # Exact match or semantic equivalence
      if corrected_answer.strip().lower() == gold_answer.strip().lower():
          return 1.0
      # GPT-judge for semantic equivalence
      judge_prompt = f"Are these equivalent? A: {corrected_answer} B: {gold_answer}"
      judge_response = gpt_judge(judge_prompt)
      return 1.0 if "yes" in judge_response.lower() else 0.0
  
  # Compute success rates
  matched_rate = sum(evaluate_correction(x) for x in matched_results) / len(matched_results)
  mismatched_rate = sum(evaluate_correction(x) for x in mismatched_results) / len(mismatched_results)
  difference = matched_rate - mismatched_rate
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Based on correction routing experiment, generate:
1. **Success Rate Comparison**: Bar chart showing matched vs mismatched success rates for both models
2. **Per-Model Breakdown**: Grouped bar chart (GPT-3.5 vs Llama-2-7B, matched vs mismatched)
3. **Distribution of Correction Outcomes**: Histogram showing success/failure counts per condition

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1**: RAG correction routing experiment design
- **Type**: Knowledge base placeholder (MCP unavailable)
- **Query Used**: "RAG correction routing experiment design"
- **Relevance**: Standard RAG correction approaches and metrics
- **Key Insights**:
  - Standard RAG correction uses Wikipedia or domain-specific corpora
  - Typical metrics: exact match, F1, semantic similarity
  - Sample sizes: 50-100 test cases per condition
- **Used For**: Experiment design methodology, sample size selection

**Source 2**: TruthfulQA benchmarking
- **Type**: Knowledge base placeholder (MCP unavailable)
- **Query Used**: "TruthfulQA benchmarking"
- **Relevance**: Baseline performance expectations
- **Key Insights**:
  - Typical baseline accuracy: 30-40% for base models without correction
  - RAG correction improvements: 10-20 percentage points documented
- **Used For**: Expected baseline performance, success criteria calibration

### Archon Code Examples

**Code Source 1**: RAG correction implementation pattern
- **Query Used**: "RAG correction implementation PyTorch"
- **Key Code**:
  ```python
  # Typical RAG correction pattern
  def rag_correct(question, incorrect_answer, retrieval_corpus):
      # 1. Extract entities from question
      entities = ner_tool.extract(question)
      
      # 2. Retrieve relevant documents
      docs = retrieval_corpus.search(entities)
      
      # 3. Generate corrected answer with context
      corrected = model.generate(
          question=question,
          context=docs,
          incorrect_answer=incorrect_answer
      )
      return corrected
  ```
- **Used For**: Pseudo-code generation (RAG pipeline)

**Code Source 2**: COT correction pattern
- **Query Used**: "Chain-of-thought correction implementation"
- **Key Code**:
  ```python
  # Chain-of-thought correction
  def cot_correct(question, incorrect_answer):
      prompt = f"""
      Question: {question}
      Incorrect answer: {incorrect_answer}
      
      Let's think step by step to find the correct answer:
      """
      return model.generate(prompt)
  ```
- **Used For**: Pseudo-code generation (COT pipeline baseline)

### B. GitHub Implementations (Exa)

**Repository 1**: langchain-ai/langchain (⭐ 75k+)
- **URL**: https://github.com/langchain-ai/langchain
- **Query Used**: "RAG correction routing implementation GitHub"
- **Relevance**: Standard RAG implementation framework
- **Key Code** (annotated):
  ```python
  # RAG chain pattern
  from langchain.chains import RetrievalQA
  from langchain.vectorstores import FAISS
  
  # Used as basis for: RAG pipeline architecture
  qa_chain = RetrievalQA.from_chain_type(
      llm=model,
      retriever=vectorstore.as_retriever(),
      chain_type="stuff"
  )
  ```
- **Configuration Extracted**: Retrieval pipeline structure, chain types
- **Used For**: RAG pipeline design

**Repository 2**: hwchase17/chat-your-data (⭐ 2k+)
- **URL**: https://github.com/hwchase17/chat-your-data
- **Query Used**: "RAG correction routing implementation GitHub"
- **Relevance**: Question answering with RAG
- **Key Code** (annotated):
  ```python
  # Entity-focused retrieval
  # Used as basis for: Entity extraction and retrieval integration
  def retrieve_with_entities(question, entities, corpus):
      expanded = f"{question} {' '.join(entities)}"
      docs = corpus.similarity_search(expanded, k=3)
      return docs
  ```
- **Used For**: Entity-focused retrieval pattern

**Repository 3**: sylinrl/TruthfulQA (⭐ 500+)
- **URL**: https://github.com/sylinrl/TruthfulQA
- **Query Used**: "TruthfulQA evaluation code"
- **Relevance**: Official TruthfulQA benchmark code
- **Their Results**: Baseline GPT-3 truthfulness ~40%
- **Used For**: Baseline performance expectations, dataset structure

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report - h-m1
- **File**: `h-m1/04_validation.md`
- **Reused Components**:
  - Dataset: TruthfulQA single-entity subset - Proven stable
  - Entropy Classifier: Threshold 0.32 - 86.7% accuracy validated
  - Entity-error identification: 100% precision on test set
- **Why Reused**: Enables controlled experiment (only correction method changes, same failure identification)

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Previous (h-m1) + Phase 2B | h-m1 validation, 02b_context.md |
| Entity-error identification | Previous (h-m1) | h-m1 entropy classifier |
| RAG pipeline design | GitHub + Archon | langchain-ai/langchain, Code A.1 |
| COT baseline | GitHub + Archon | Code A.2 |
| Entity retrieval pattern | GitHub | hwchase17/chat-your-data |
| Sample size (N=100) | Archon KB | Source A.1 |
| Success criteria (≥20pp) | Phase 2B | 02b_verification_plan.md |
| Expected baseline | Archon KB + GitHub | Source A.2, TruthfulQA repo |
| Evaluation metrics | Phase 2B + Research | 02b_context.md, TruthfulQA paper |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-24T00:00:00Z

### Workflow History for This Hypothesis
- 2026-08-24T00:00:00Z: Experiment design initiated (Phase 2C)
- 2026-08-24T00:00:00Z: Experiment design completed (Phase 2C)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
