# Logic Specification: h-m2

**Hypothesis:** h-m2  
**Type:** MECHANISM  
**Gate:** MUST_WORK (≥20pp difference OR ≥50% relative improvement, BOTH models)  
**Date:** 2026-08-24  
**Budget:** 30 tokens  

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation - consumes h-m1 validated classifier (threshold 0.32)  
**Analyzed Path**: N/A (new correction routing experiment)  
**Relevant Symbols**: None - baseline correction implementation  

**Note**: h-m2 is a standalone correction experiment. h-m1 classifier already validated (86.7% test accuracy, threshold 0.32).

---

## External Dependencies (h-m1)

### Classifier Output Format (Verified from Actual Code)

```python
# From: docs/youra_research/h-m1/code/src/classifier.py
class ThresholdClassifier:
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.best_threshold: float = 0.5  # h-m1 validated: 0.32
        self.train_accuracy: float = 0.0
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """X: (N,) entropy -> (N,) binary (0=entity-error, 1=non-entity)"""
        return (X >= self.best_threshold).astype(int)
```

**Optimal Threshold**: 0.32 (from h-m1 validation)  
**Rule**: `entropy < 0.32 → entity-error (label 0)`

---

## M2-1: Entity Extraction [Complexity: 3, Budget: 3]

**Applied**: spaCy NER standard pattern

### API Signatures

```python
# src/entity_extractor.py
import spacy
from typing import List

class EntityExtractor:
    """Extract named entities using spaCy."""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        self.nlp = spacy.load(model_name)
    
    def extract(self, text: str) -> List[str]:
        """Extract entities. Returns unique entity texts."""
        doc = self.nlp(text)
        return list(set(ent.text for ent in doc.ents))
```

### Pseudo-code

```
1. doc = nlp(question)
2. entities = [ent.text for ent in doc.ents]
3. return unique(entities)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Load spaCy | Initialize `en_core_web_sm` |
| L-1-2 | NER | Extract entities from question |
| L-1-3 | Dedupe | Return unique entity list |

---

## M2-2: Wikipedia Retrieval [Complexity: 5, Budget: 5]

**Applied**: Wikipedia API with fallback handling

### API Signatures

```python
# src/retriever.py
import wikipedia
from typing import List, Optional

class WikipediaRetriever:
    """Retrieve Wikipedia summaries for entities."""
    
    def __init__(self, top_k: int = 3, sentences: int = 2):
        self.top_k = top_k
        self.sentences = sentences
    
    def retrieve(self, entities: List[str]) -> List[str]:
        """
        Retrieve Wikipedia summaries. 
        Returns: List of summary strings (max top_k).
        """
        ...
    
    def _fetch_summary(self, entity: str) -> Optional[str]:
        """Fetch single summary with error handling."""
        ...
```

### Edge Cases

| Case | Handling |
|------|----------|
| No entities | Return empty list → COT fallback |
| Wikipedia API failure | Skip entity, continue with others |
| Disambiguation error | Use `wikipedia.search(entity)[0]` |
| Timeout | Skip entity (3s timeout per request) |

### Pseudo-code

```
1. docs = []
2. For entity in entities[:top_k]:
       try:
           summary = wikipedia.summary(entity, sentences=sentences, auto_suggest=False)
           docs.append(summary)
       except DisambiguationError:
           # Use first search result
           page = wikipedia.search(entity)[0]
           summary = wikipedia.summary(page, sentences=sentences)
           docs.append(summary)
       except (PageError, Timeout):
           continue
3. return docs
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | API Call | Query Wikipedia API per entity |
| L-2-2 | Disambiguation | Handle ambiguous entities |
| L-2-3 | Error Handling | Skip PageError/Timeout |
| L-2-4 | Top-k Selection | Limit to 3 entities |
| L-2-5 | Summary Extraction | Extract 2 sentences per doc |

---

## M2-3: RAG Correction [Complexity: 7, Budget: 7]

**Applied**: Context-augmented prompt generation

### API Signatures

```python
# src/rag_corrector.py
from typing import List
from openai import OpenAI
from transformers import AutoTokenizer, AutoModelForCausalLM

class RAGCorrector:
    """Matched routing: entity-error → RAG."""
    
    def __init__(self, model_name: str, temperature: float = 0.7, max_tokens: int = 150):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        if model_name == "gpt-3.5-turbo":
            self.client = OpenAI()
        else:  # llama-2-7b
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
    
    def correct(self, question: str, incorrect_answer: str, context_docs: List[str]) -> str:
        """
        Generate corrected answer with context.
        question: TruthfulQA question
        incorrect_answer: Model's wrong response
        context_docs: Retrieved Wikipedia summaries
        Returns: Corrected answer string
        """
        ...
```

### Prompt Template

```
Context: {doc1}\n{doc2}\n{doc3}

Question: {question}
Incorrect answer: {incorrect_answer}

Based on the context, provide the correct answer:
```

### Pseudo-code

```
1. context = "\n".join(context_docs)
2. prompt = f"Context: {context}\n\nQuestion: {question}\nIncorrect answer: {incorrect_answer}\n\nBased on the context, provide the correct answer:"
3. If model == "gpt-3.5-turbo":
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": prompt}],
           temperature=0.7,
           max_tokens=150
       )
       return response.choices[0].message.content
4. Else (llama-2-7b):
       inputs = tokenizer(prompt, return_tensors="pt")
       outputs = model.generate(inputs, max_new_tokens=150, temperature=0.7)
       return tokenizer.decode(outputs[0])
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Prompt Build | Construct context-augmented prompt |
| L-3-2 | GPT-3.5 API | OpenAI API call |
| L-3-3 | Llama-2 Generate | HuggingFace generation |
| L-3-4 | Temperature Control | Set to 0.7 |
| L-3-5 | Token Limit | Max 150 tokens |
| L-3-6 | Response Parse | Extract generated text |
| L-3-7 | Fallback | If no context → COT |

---

## M2-4: COT Correction [Complexity: 4, Budget: 4]

**Applied**: Chain-of-thought prompting

### API Signatures

```python
# src/cot_corrector.py
from openai import OpenAI
from transformers import AutoTokenizer, AutoModelForCausalLM

class COTCorrector:
    """Mismatched routing baseline: entity-error → COT."""
    
    def __init__(self, model_name: str, temperature: float = 0.7, max_tokens: int = 150):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        if model_name == "gpt-3.5-turbo":
            self.client = OpenAI()
        else:  # llama-2-7b
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
    
    def correct(self, question: str, incorrect_answer: str) -> str:
        """Chain-of-thought correction (no context)."""
        ...
```

### Prompt Template

```
Question: {question}
Incorrect answer: {incorrect_answer}

Let's think step by step to find the correct answer:
```

### Pseudo-code

```
1. prompt = f"Question: {question}\nIncorrect answer: {incorrect_answer}\n\nLet's think step by step to find the correct answer:"
2. # Same generation logic as RAG (no context)
3. return corrected_answer
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Prompt Build | COT template |
| L-4-2 | GPT-3.5 API | OpenAI call |
| L-4-3 | Llama-2 Generate | HuggingFace generation |
| L-4-4 | Response Parse | Extract text |

---

## M2-5: Success Evaluation [Complexity: 6, Budget: 6]

**Applied**: Exact match + GPT-judge semantic equivalence

### API Signatures

```python
# src/evaluator.py
from openai import OpenAI
from typing import Dict

class SuccessEvaluator:
    """Binary correctness evaluation."""
    
    def __init__(self):
        self.client = OpenAI()
    
    def evaluate(self, corrected_answer: str, gold_answer: str) -> float:
        """Returns 1.0 if correct, 0.0 if incorrect."""
        ...
    
    def _exact_match(self, corrected: str, gold: str) -> bool:
        """Case-insensitive exact match."""
        return corrected.strip().lower() == gold.strip().lower()
    
    def _gpt_judge(self, corrected: str, gold: str) -> bool:
        """Semantic equivalence via GPT-3.5."""
        ...
```

### GPT-Judge Prompt

```
Are these answers equivalent in meaning?
Answer A: {corrected_answer}
Answer B: {gold_answer}

Respond 'yes' or 'no'.
```

### Pseudo-code

```
1. If exact_match(corrected, gold):
       return 1.0
2. Else:
       judge_prompt = f"Are these equivalent?\nA: {corrected}\nB: {gold}\nRespond 'yes' or 'no'."
       response = gpt_judge(judge_prompt)
       return 1.0 if "yes" in response.lower() else 0.0
```

### Edge Cases

| Case | Handling |
|------|----------|
| GPT-judge timeout | Retry once, then return 0.0 |
| Ambiguous response | Default to 0.0 (conservative) |
| Empty corrected answer | Return 0.0 |

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Exact Match | Case-insensitive string compare |
| L-5-2 | Judge Prompt | Build equivalence check prompt |
| L-5-3 | GPT-3.5 Judge | API call for semantic check |
| L-5-4 | Response Parse | Extract yes/no |
| L-5-5 | Retry Logic | 1 retry on timeout |
| L-5-6 | Score | Return 1.0 or 0.0 |

---

## M2-6: Gate Check [Complexity: 5, Budget: 5]

**Applied**: Dual-condition check across two models

### API Signatures

```python
# src/gate_checker.py
from typing import Dict, List

class GateChecker:
    """MUST_WORK gate evaluation."""
    
    def check_gate(self, results: List[Dict]) -> Dict:
        """
        Check gate across both models.
        results: [
            {"model": "gpt-3.5-turbo", "matched_rate": float, "mismatched_rate": float},
            {"model": "llama-2-7b", "matched_rate": float, "mismatched_rate": float}
        ]
        Returns: {
            "gpt35_pass": bool,
            "llama_pass": bool,
            "overall_pass": bool,
            "gpt35_diff": float,
            "llama_diff": float,
            "gpt35_rel_improvement": float,
            "llama_rel_improvement": float
        }
        """
        ...
    
    def _compute_metrics(self, matched: float, mismatched: float) -> Dict:
        """
        Compute difference and relative improvement.
        Returns: {"diff": float, "rel_improvement": float}
        """
        diff = matched - mismatched
        rel_improvement = ((matched - mismatched) / mismatched * 100) if mismatched > 0 else 0.0
        return {"diff": diff, "rel_improvement": rel_improvement}
    
    def _check_condition(self, diff: float, rel_improvement: float) -> bool:
        """Return True if (diff >= 0.20) OR (rel_improvement >= 50.0)"""
        return (diff >= 0.20) or (rel_improvement >= 50.0)
```

### Gate Logic

```
1. For each model in [gpt-3.5, llama-2-7b]:
       diff = matched_rate - mismatched_rate
       rel_improvement = (matched - mismatched) / mismatched * 100
       pass = (diff >= 0.20) OR (rel_improvement >= 50.0)
2. overall_pass = (gpt35_pass AND llama_pass)
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Difference | matched - mismatched |
| L-6-2 | Relative Improvement | ((matched - mismatched) / mismatched) × 100 |
| L-6-3 | Condition Check | (≥20pp) OR (≥50%) |
| L-6-4 | Per-Model Check | GPT-3.5 and Llama-2-7B |
| L-6-5 | Overall Gate | BOTH must pass |

---

## Configuration API

```python
# config.py
CONFIG = {
    "data": {
        "h_m1_threshold": 0.32,  # From h-m1 validation
        "sample_size_per_model": 50,
        "models": ["gpt-3.5-turbo", "llama-2-7b"]
    },
    "retrieval": {
        "top_k_entities": 3,
        "summary_sentences": 2,
        "timeout_seconds": 3
    },
    "generation": {
        "temperature": 0.7,
        "max_tokens": 150
    },
    "evaluation": {
        "judge_model": "gpt-3.5-turbo",
        "judge_retry": 1
    },
    "gate": {
        "min_diff": 0.20,
        "min_rel_improvement": 50.0
    },
    "output": {
        "results_file": "./results/correction_results.json",
        "figures_dir": "./figures/"
    },
    "seed": 42
}
```

---

## Output Schema

```python
# results/correction_results.json
{
    "gpt-3.5-turbo": {
        "matched_rate": float,  # RAG success rate
        "mismatched_rate": float,  # COT success rate
        "difference": float,
        "relative_improvement": float,
        "gate_pass": bool,
        "per_sample": [
            {
                "question": str,
                "incorrect_answer": str,
                "gold_answer": str,
                "matched_corrected": str,
                "mismatched_corrected": str,
                "matched_correct": bool,
                "mismatched_correct": bool
            }
        ]
    },
    "llama-2-7b": {
        # Same structure
    },
    "overall_gate_pass": bool
}
```

---

## Budget Summary

| Task ID | Name | Complexity | Budget | Subtasks |
|---------|------|------------|--------|----------|
| M2-1 | Entity Extraction | 3 | 3 | 3 |
| M2-2 | Wikipedia Retrieval | 5 | 5 | 5 |
| M2-3 | RAG Correction | 7 | 7 | 7 |
| M2-4 | COT Correction | 4 | 4 | 4 |
| M2-5 | Success Evaluation | 6 | 6 | 6 |
| M2-6 | Gate Check | 5 | 5 | 5 |
| **Total** | | **30** | **30** | **30** |

---

## Validation Checklist

- [x] No ASCII diagrams
- [x] No KB search logs (Applied: spaCy NER, Wikipedia API, GPT prompting)
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes N/A (string-based experiment)
- [x] Subtask count = 30 (within budget)
- [x] Total length < 600 lines
- [x] Codebase Analysis section included
- [x] Green-field project noted
- [x] External Dependencies from h-m1 verified

---

**Logic Version:** 1.0  
**Status:** Ready for Phase 4 Implementation
