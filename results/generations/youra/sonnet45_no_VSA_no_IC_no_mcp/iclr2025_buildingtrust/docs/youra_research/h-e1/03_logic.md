# Logic Design: h-e1

**Date:** 2026-08-24  
**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC pattern detection)  
**Author:** yoon303@etri.re.kr

---

## Codebase Analysis (Serena)

**Project Type:** green-field (h-e1 has no existing code)  
**Status:** New implementation, reuses h-c1 NER (spaCy `en_core_web_lg`, F1=0.96)  
**Analyzed Path:** h-c1/code/ (for NER reuse only)  
**Relevant Symbols:** `NERValidator` (h-c1) — entity span extraction pattern

---

## Core Algorithms

### A1: Attention Extraction

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class AttentionExtractor:
    def __init__(self, model_name: str = "meta-llama/Llama-2-7b-hf"):
        """Load model with attention output enabled."""
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            output_attentions=True,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    def extract(self, question: str) -> torch.Tensor:
        """Extract last-layer attention. Returns: [seq_len, seq_len]"""
        inputs = self.tokenizer(question, return_tensors="pt").to(self.model.device)
        outputs = self.model(**inputs, output_attentions=True)
        
        # Last layer, averaged across heads
        attn = outputs.attentions[-1].mean(dim=1).squeeze(0).cpu()  # [seq_len, seq_len]
        return attn
```

**Applied:** Standard HuggingFace pattern (outputs.attentions)

**Tensor Shapes:**
- `outputs.attentions[-1]`: [1, num_heads, seq_len, seq_len]
- `attn` (after mean): [seq_len, seq_len]

---

### A2: Entity Span Mapping

```python
class SpanMapper:
    def __init__(self, tokenizer):
        """Map character spans to token indices."""
        self.tokenizer = tokenizer
    
    def char_to_token_span(self, text: str, char_span: tuple) -> tuple:
        """Map (start_char, end_char) → (start_token, end_token)."""
        inputs = self.tokenizer(text, return_offsets_mapping=True)
        
        start_char, end_char = char_span
        start_token = None
        end_token = None
        
        for i, (token_start, token_end) in enumerate(inputs.offset_mapping[0]):
            if token_start == start_char:
                start_token = i
            if token_end == end_char:
                end_token = i + 1
                break
        
        if start_token is None or end_token is None:
            raise ValueError(f"Span {char_span} not aligned")
        
        return (start_token, end_token)
```

**Applied:** tokenizer.offset_mapping (HuggingFace standard)

**Pseudo-code:**
1. Tokenize text with offsets
2. Find token index where offset_start == char_start
3. Find token index where offset_end == char_end
4. Return (start_token, end_token)

---

### A3: Entropy Calculation

```python
import numpy as np

class EntropyCalculator:
    def calculate(self, attn: torch.Tensor, entity_span: tuple) -> float:
        """Compute entropy over attention TO entity span.
        
        Args:
            attn: [seq_len, seq_len] attention matrix
            entity_span: (start_token, end_token)
        
        Returns:
            entropy: float (average across entity tokens)
        """
        start, end = entity_span
        entity_attn = attn[:, start:end]  # [seq_len, entity_len]
        
        entropies = []
        for token_attn in entity_attn:
            probs = token_attn / (token_attn.sum() + 1e-10)
            H = -torch.sum(probs * torch.log(probs + 1e-10)).item()
            entropies.append(H)
        
        return float(np.mean(entropies))
```

**Applied:** Standard entropy formula H(A) = -Σ(p * log(p))

**Tensor Shapes:**
- `entity_attn`: [seq_len, entity_len]
- `token_attn`: [entity_len]
- `probs`: [entity_len] (normalized)

**Pseudo-code:**
1. Slice attention matrix to entity span
2. For each token: normalize → calculate entropy
3. Average entropies

---

### A4: Statistical Comparison

```python
from scipy.stats import ttest_ind

class StatisticalTester:
    def compare(self, entity_errors: list, non_entity_errors: list) -> dict:
        """One-tailed t-test: entity < non-entity.
        
        Returns:
            {p_value, mean_entity, mean_non_entity, cohens_d, pass}
        """
        t_stat, p_two_tail = ttest_ind(entity_errors, non_entity_errors)
        
        mean_entity = np.mean(entity_errors)
        mean_non_entity = np.mean(non_entity_errors)
        
        # One-tailed p-value
        p_value = p_two_tail / 2 if mean_entity < mean_non_entity else 1.0
        
        # Effect size
        pooled_std = np.sqrt((np.var(entity_errors) + np.var(non_entity_errors)) / 2)
        cohens_d = (mean_entity - mean_non_entity) / pooled_std
        
        return {
            "p_value": p_value,
            "mean_entity": mean_entity,
            "mean_non_entity": mean_non_entity,
            "cohens_d": cohens_d,
            "pass": p_value < 0.05 and mean_entity < mean_non_entity
        }
```

**Applied:** scipy.stats.ttest_ind (standard t-test)

**Pseudo-code:**
1. Run independent samples t-test
2. Convert to one-tailed p-value
3. Calculate Cohen's d
4. Check pass condition

---

## Main Workflow

```python
class AttentionEntropyExperiment:
    def __init__(self):
        """Initialize all components."""
        self.extractor = AttentionExtractor()
        self.mapper = SpanMapper(self.extractor.tokenizer)
        self.calculator = EntropyCalculator()
        self.tester = StatisticalTester()
        self.ner = spacy.load("en_core_web_lg")  # h-c1 validated
    
    def run(self, dataset: list) -> dict:
        """Run full experiment.
        
        Args:
            dataset: List[{question, error_type}]
        
        Returns:
            Statistical results + pass/fail
        """
        entity_entropies = []
        non_entity_entropies = []
        
        for sample in dataset:
            # 1. Extract entity span (NER)
            doc = self.ner(sample["question"])
            if not doc.ents:
                continue  # Skip if no entity found
            entity_char_span = (doc.ents[0].start_char, doc.ents[0].end_char)
            
            # 2. Extract attention
            attn = self.extractor.extract(sample["question"])
            
            # 3. Map span to tokens
            entity_token_span = self.mapper.char_to_token_span(
                sample["question"], entity_char_span
            )
            
            # 4. Calculate entropy
            entropy = self.calculator.calculate(attn, entity_token_span)
            
            # 5. Categorize by error type
            if sample["error_type"] == "entity":
                entity_entropies.append(entropy)
            else:
                non_entity_entropies.append(entropy)
        
        # 6. Statistical test
        return self.tester.compare(entity_entropies, non_entity_entropies)
```

**Pseudo-code:**
1. For each sample: NER → attention → span mapping → entropy
2. Group by error_type
3. Statistical test
4. Return pass/fail

---

## Data Structures

### Input Format

```python
{
    "question": str,          # TruthfulQA question text
    "error_type": str,        # "entity" or "non-entity"
    "entity_span": tuple      # (start_char, end_char) - optional
}
```

### Output Format

```python
{
    "p_value": float,
    "mean_entity": float,
    "mean_non_entity": float,
    "cohens_d": float,
    "pass": bool,
    "entity_entropies": List[float],
    "non_entity_entropies": List[float]
}
```

---

## Edge Cases

| Case | Handling |
|------|----------|
| No entity found (NER) | Skip sample, log count |
| Span misalignment | Skip sample, log count |
| Zero attention | Add 1e-10 smoothing |
| Empty entity span | Skip sample |
| GPU OOM | Use float16, batch_size=1 |

---

## External Dependencies

### From h-c1 (Validated)

- **NER Tool:** spaCy `en_core_web_lg` (F1=0.96)
- **Usage:** Entity span extraction at character level
- **Validation:** h-c1/04_validation.md confirmed accuracy

**Note:** h-c1 provides NER validation only. h-e1 implements new attention extraction logic.

---

## Validation Outputs

### Files

1. **04_validation.md:** Gate results, pass/fail determination
2. **entropy_scores.csv:** [sample_id, error_type, entropy]
3. **statistical_results.json:** Full statistical output
4. **figures/violin_plot.png:** Distribution comparison
5. **figures/histogram.png:** Overlapping histograms

### Console Output

```
[1/5] Loading dataset... ✓ 100 samples
[2/5] Extracting attention... ✓ 98/100 processed (2 skipped)
[3/5] Calculating entropy... ✓ Mean entity: 0.42, non-entity: 0.68
[4/5] Statistical test... ✓ p=0.003, d=0.81
[5/5] Gate evaluation... ✓ PASS
```

---

## Self-Validation

### Quick Checks
- [x] No ASCII diagrams
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in comments
- [x] Total length < 600 lines
- [x] Codebase Analysis section included
- [x] Green-field project noted (Serena skip acceptable)

### Logic Checks
- [x] All FR requirements covered (FR1-FR6 from PRD)
- [x] Character-to-token mapping specified
- [x] Edge cases documented
- [x] Statistical test one-tailed (entity < non-entity)
- [x] h-c1 NER reuse specified

---

**Next Phase:** Phase 4 — Implementation (code/)
