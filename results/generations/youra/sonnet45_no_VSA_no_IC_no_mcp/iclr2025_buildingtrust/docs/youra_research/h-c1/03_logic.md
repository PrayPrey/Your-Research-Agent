# Logic Design: h-c1

**Date:** 2026-08-24  
**Hypothesis:** NER ≥90% F1, Wikipedia coverage ≥90%  
**Type:** CONDITION (pure evaluation, no training)  
**Author:** Logic Agent

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation - no existing code to analyze  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - validation script from scratch

---

## Component Overview

Five main functions:
1. Data loading (TruthfulQA subset + gold annotations)
2. NER validation (spaCy scorer)
3. Wikipedia coverage check (API query)
4. Gate evaluation (threshold comparison)
5. Figure generation (4 plots)

**Applied**: Standard library patterns (spaCy Scorer, Wikipedia API)

---

## L-1: Data Loading [Complexity: 2, Budget: 5]

### API Signatures

```python
from typing import List, Tuple, Dict
from dataclasses import dataclass

@dataclass
class EntitySample:
    """Single TruthfulQA sample with entity annotation."""
    question: str
    gold_entities: List[Tuple[int, int, str]]  # [(start, end, label)]
    correct_entity: str  # For Wikipedia lookup

def load_truthfulqa_subset(data_path: str) -> Tuple[List[EntitySample], List[str]]:
    """
    Load gold-annotated TruthfulQA samples.
    
    Args:
        data_path: Path to truthfulqa_entity_subset/
    
    Returns:
        all_samples: 100 samples with gold annotations
        entities_for_coverage: 50 entity names for Wikipedia check
    """
    ...
```

### Pseudo-code

```
1. Load gold_annotations.jsonl → parse into EntitySample objects
2. Load entity_errors.json → extract correct_entity field
3. Return (samples, entities)
```

### Subtasks [2/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Parse JSONL | Read gold annotations line by line |
| L-1-2 | Extract entities | Filter correct entities from entity_errors.json |

---

## L-2: NER Validation [Complexity: 3, Budget: 8]

### API Signatures

```python
import spacy
from spacy.training import Example
from spacy.scorer import Scorer
from typing import List

def validate_ner(
    samples: List[EntitySample],
    model_name: str = "en_core_web_lg"
) -> Dict[str, float]:
    """
    Evaluate spaCy NER against gold annotations.
    
    Args:
        samples: Gold-labeled samples
        model_name: spaCy model identifier
    
    Returns:
        {
            "ents_f": 0.XX,  # F1 score (target metric)
            "ents_p": 0.XX,  # Precision
            "ents_r": 0.XX   # Recall
        }
    """
    ...
```

**Applied**: spaCy Scorer pattern (from Archon KB)

### Pseudo-code

```
1. nlp = spacy.load(model_name)
2. for each sample:
   - doc = nlp.make_doc(sample.question)
   - example = Example.from_dict(doc, {"entities": sample.gold_entities})
   - examples.append(example)
3. scorer = Scorer()
4. scores = scorer.score(examples)
5. return scores (contains ents_f, ents_p, ents_r)
```

### Subtasks [3/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Load model | spacy.load("en_core_web_lg") |
| L-2-2 | Create examples | Convert gold annotations to Example objects |
| L-2-3 | Score predictions | Use Scorer.score() for entity F1 |

---

## L-3: Wikipedia Coverage [Complexity: 3, Budget: 8]

### API Signatures

```python
import wikipediaapi
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict

def validate_wikipedia_coverage(
    entities: List[str],
    min_content_length: int = 100,
    max_workers: int = 10
) -> Dict[str, float]:
    """
    Check Wikipedia coverage for entity list.
    
    Args:
        entities: Entity names to check
        min_content_length: Non-stub threshold (chars)
        max_workers: Concurrent API threads
    
    Returns:
        {
            "coverage": 0.XX,  # Percentage covered
            "covered_count": N,
            "total_count": N
        }
    """
    ...

def _check_entity(entity: str, wiki: wikipediaapi.Wikipedia, min_len: int) -> bool:
    """Single entity coverage check. Returns True if exists + non-stub."""
    ...
```

**Applied**: Wikipedia API pattern + ThreadPoolExecutor for concurrency

### Pseudo-code

```
1. wiki = wikipediaapi.Wikipedia('en')
2. with ThreadPoolExecutor(max_workers) as executor:
   - results = executor.map(_check_entity, entities)
3. covered = sum(results)
4. coverage = covered / len(entities)
5. return {"coverage": coverage, "covered_count": covered, "total_count": len(entities)}

# _check_entity helper:
1. page = wiki.page(entity)
2. return page.exists() and len(page.text) > min_len
```

### Subtasks [3/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Query API | wikipediaapi.Wikipedia.page() |
| L-3-2 | Filter stubs | Check page.text length >100 chars |
| L-3-3 | Parallel execution | ThreadPoolExecutor for rate limit compliance |

---

## L-4: Gate Evaluation [Complexity: 1, Budget: 3]

### API Signatures

```python
from typing import Dict, Literal

GateStatus = Literal["PASS", "FAIL"]

def evaluate_gate(
    ner_f1: float,
    wiki_coverage: float,
    ner_threshold: float = 0.90,
    coverage_threshold: float = 0.90
) -> Dict[str, any]:
    """
    Evaluate MUST_WORK gate condition.
    
    Args:
        ner_f1: NER F1 score (0.0-1.0)
        wiki_coverage: Wikipedia coverage (0.0-1.0)
        ner_threshold: Minimum NER F1 required
        coverage_threshold: Minimum coverage required
    
    Returns:
        {
            "status": "PASS" | "FAIL",
            "ner_pass": bool,
            "coverage_pass": bool,
            "message": str
        }
    """
    ...
```

### Pseudo-code

```
1. ner_pass = ner_f1 >= ner_threshold
2. coverage_pass = wiki_coverage >= coverage_threshold
3. gate_pass = ner_pass and coverage_pass
4. status = "PASS" if gate_pass else "FAIL"
5. message = f"NER: {ner_f1:.3f} ({'✓' if ner_pass else '✗'}), Coverage: {wiki_coverage:.3f} ({'✓' if coverage_pass else '✗'})"
6. return result dict
```

### Subtasks [1/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Threshold comparison | Boolean checks for both metrics |

---

## L-5: Figure Generation [Complexity: 2, Budget: 6]

### API Signatures

```python
import matplotlib.pyplot as plt
from typing import Dict, List
from pathlib import Path

def generate_figures(
    ner_scores: Dict[str, float],
    wiki_results: Dict[str, float],
    samples: List[EntitySample],
    output_dir: Path
) -> None:
    """
    Generate 4 required figures.
    
    Args:
        ner_scores: NER validation results (from L-2)
        wiki_results: Wikipedia coverage results (from L-3)
        samples: Gold samples (for per-entity analysis)
        output_dir: figures/ directory path
    
    Saves:
        - gate_metrics.png (target vs actual bar chart)
        - ner_confusion.png (entity type breakdown)
        - coverage_by_type.png (PERSON/ORG/GPE coverage)
        - ner_distribution.png (per-sample F1 histogram)
    """
    ...
```

**Applied**: matplotlib basic patterns

### Pseudo-code

```
1. Fig 1 - Gate metrics bar chart:
   - x = ["NER F1", "Wiki Coverage"]
   - target = [0.90, 0.90]
   - actual = [ner_scores["ents_f"], wiki_results["coverage"]]
   - plt.bar() with grouped bars

2. Fig 2 - NER confusion matrix:
   - Extract per-entity-type precision/recall from samples
   - plt.imshow() heatmap

3. Fig 3 - Coverage by entity type:
   - Group entities by type (PERSON/ORG/GPE)
   - Check Wikipedia coverage per group
   - plt.bar()

4. Fig 4 - NER F1 distribution:
   - Compute per-sample F1 scores
   - plt.hist()

5. Save all to output_dir/
```

### Subtasks [2/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Bar charts | Gate metrics + coverage by type |
| L-5-2 | Histogram | Per-sample NER F1 distribution |

---

## Control Flow

```
main():
1. samples, entities = load_truthfulqa_subset("data/truthfulqa_entity_subset/")
2. ner_scores = validate_ner(samples)
3. wiki_results = validate_wikipedia_coverage(entities)
4. gate_result = evaluate_gate(ner_scores["ents_f"], wiki_results["coverage"])
5. generate_figures(ner_scores, wiki_results, samples, "figures/")
6. print(gate_result["status"])  # PASS/FAIL
7. exit(0 if gate_result["status"] == "PASS" else 1)
```

**Total execution**: <5 minutes (100 samples, 50 Wikipedia queries)

---

## Error Handling

### Wikipedia API Failures
```python
def _check_entity_with_retry(entity: str, wiki: wikipediaapi.Wikipedia, retries: int = 1) -> bool:
    for attempt in range(retries + 1):
        try:
            page = wiki.page(entity)
            return page.exists() and len(page.text) > 100
        except Exception as e:
            if attempt == retries:
                logging.warning(f"Wikipedia API failed for '{entity}': {e}")
                return False  # Count as not covered
            time.sleep(1)  # Exponential backoff
    return False
```

### spaCy Scorer Errors
```python
try:
    scores = scorer.score(examples)
except Exception as e:
    raise RuntimeError(f"spaCy scorer failed: {e}\nCheck gold annotation format") from e
```

**Strategy**: Fail fast for critical errors (bad annotations), retry once for transient API errors.

---

## Budget Summary

| Component | Budget | Used |
|-----------|--------|------|
| L-1: Data loading | 5 | 2 |
| L-2: NER validation | 8 | 3 |
| L-3: Wikipedia coverage | 8 | 3 |
| L-4: Gate evaluation | 3 | 1 |
| L-5: Figure generation | 6 | 2 |
| **Total** | **30** | **11** |

**Remaining budget**: 19 subtasks (available for Phase 4 adjustments)

---

## Dependencies

**External Libraries:**
- `spacy` (3.x) - NER model + Scorer
- `wikipediaapi` - Wikipedia API client
- `matplotlib` - Figure generation
- `datasets` - HuggingFace TruthfulQA loading

**Pre-trained Models:**
- `en_core_web_lg` (~800MB download via `python -m spacy download en_core_web_lg`)

**No base hypothesis dependencies** - root CONDITION hypothesis.

---

*Logic design complete. Phase 4 Coder: Match signatures exactly. All parameter names verified from stdlib docs.*
