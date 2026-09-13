# Phase 2B Verification Plan: h-e1

**Date:** 2026-08-24  
**Hypothesis ID:** h-e1  
**Hypothesis Statement:** Entity-substitution errors exhibit significantly lower attention entropy over NER-identified entity spans compared to non-entity errors (p < 0.05, entity-error mean < non-entity-error mean)

---

## Verification Approach

**Hypothesis Type:** EXISTENCE (pattern detection)  
**Verification Method:** Statistical comparison of attention entropy distributions  
**No Training Required:** Inference-only experiment on pre-trained Llama-2-7B

---

## Dataset Specification

### Primary Dataset

**Name:** TruthfulQA single-entity factual questions (entity-error vs non-entity-error subset)  
**Type:** Standard benchmark (public)  
**Source:** HuggingFace Datasets (`truthful_qa`, generation split)

**Sample Composition:**
- Total: N=100
- Entity-error samples: 50 (questions where model substitutes wrong entity)
- Non-entity-error samples: 50 (questions with reasoning/other failures)

**Sampling Strategy:**
- Reuse h-c1 annotated subset (gold-labeled error types from pilot)
- Single-entity questions only (filter multi-entity via NER)
- Balanced 50/50 split for statistical power

**Preprocessing:**
1. Load TruthfulQA generation split
2. Filter for single-entity factual questions (NER count = 1)
3. Generate model failures (Llama-2-7B inference)
4. Annotate error type (entity-substitution vs other)
5. Extract entity spans via spaCy en_core_web_lg (h-c1 validated)

**Expected Statistics:**
- Average question length: 10-20 tokens
- Entity span length: 1-3 tokens
- Error type distribution: 50% entity-error, 50% non-entity-error

---

## Model Specification

### Primary Model

**Architecture:** Llama-2-7B (causal language model)  
**Source:** HuggingFace (`meta-llama/Llama-2-7b-hf`)  
**Pre-training:** 2T tokens (general web, books, code)  
**Configuration:**
- 32 layers, 32 attention heads per layer
- Attention extraction: Last layer (layer -1)
- Aggregation: Average across heads
- Precision: float16 (memory efficiency)

**Usage:**
- Inference-only (no fine-tuning)
- Extract attention weights during forward pass
- Calculate entropy over entity spans

**Justification:**
- Open weights (attention accessible, unlike GPT-3.5 API)
- Comparable performance to GPT-3.5 on factual QA
- Established benchmark model for transformer interpretability

### Fallback Model (if Llama-2 unavailable)

**Architecture:** GPT-2 (124M parameters)  
**Source:** HuggingFace (`gpt2`)  
**Limitation:** Smaller model → potentially weaker signal  
**Expected Impact:** Lower effect size, but pattern should still hold

---

## Measurement Protocol

### 1. Attention Extraction

**Method:**
- Set `output_attentions=True` in model config
- Run forward pass on each question
- Extract last-layer attention: `outputs.attentions[-1]`
- Average across heads: `attn.mean(dim=1)`

**Output:** Attention matrix `[seq_len, seq_len]` per sample

### 2. Entity Span Identification

**Method:**
- Run spaCy NER on question text (en_core_web_lg, validated in h-c1)
- Extract character-level entity span (start, end)
- Map to token-level span using tokenizer.char_to_token()

**Output:** Token-level entity span (start_idx, end_idx)

### 3. Entropy Calculation

**Formula:** `H(A) = -Σ(p_i * log(p_i))` over attention distribution

**Implementation:**
```python
def attention_entropy(attn_weights, entity_span):
    start, end = entity_span
    entity_attn = attn_weights[:, start:end]  # attention TO entity tokens
    entropies = []
    for token_attn in entity_attn:
        probs = token_attn / (token_attn.sum() + 1e-10)
        H = -torch.sum(probs * torch.log(probs + 1e-10))
        entropies.append(H.item())
    return np.mean(entropies)
```

**Output:** Single entropy score per sample (float)

### 4. Statistical Comparison

**Test:** Independent samples t-test (one-tailed)  
**Null Hypothesis:** No difference in mean entropy  
**Alternative Hypothesis:** entity_mean < non_entity_mean  
**Significance:** α = 0.05

**Implementation:**
```python
from scipy.stats import ttest_ind

t_stat, p_two_tail = ttest_ind(entity_entropies, non_entity_entropies)
p_value = p_two_tail / 2  # convert to one-tailed
```

**Effect Size:** Cohen's d = (mean_entity - mean_non_entity) / pooled_std

**Output:** p-value, means, Cohen's d, pass/fail determination

---

## Success Criteria

### Gate Condition (MUST_WORK)

**Primary Metrics:**
1. **p-value < 0.05** (statistical significance)
2. **mean_entity_entropy < mean_non_entity_entropy** (directional hypothesis)

**Both conditions MUST be satisfied to pass gate.**

### Secondary Metrics (for interpretation)

1. **Cohen's d > 0.5** (medium effect size, desirable but not required)
2. **Mean entity entropy: 0.3-0.5** (focused attention, expected range)
3. **Mean non-entity entropy: 0.6-0.8** (distributed attention, expected range)

### Pass/Fail Determination

**PASS:** p < 0.05 AND mean_entity < mean_non_entity  
→ Proceed to h-m1 (mechanism hypothesis)

**FAIL:** p ≥ 0.05 OR opposite direction  
→ Blocks h-m1, h-m2 (no attention signature to exploit for routing)

---

## Expected Results

**Predicted Outcome:** PASS

**Reasoning:**
- Entity-substitution errors focus attention on wrong entity (low entropy)
- Non-entity errors distribute attention (high entropy, no clear focus)
- Pattern observed in transformer interpretability literature for entity-centric tasks

**Expected Values:**
- Entity-error mean entropy: 0.35 ± 0.10
- Non-entity-error mean entropy: 0.70 ± 0.15
- Cohen's d: 0.8 (large effect)
- p-value: < 0.01 (highly significant)

**Source:** Transformer attention interpretability research (entity-centric patterns)

---

## Risk Assessment

### Risk 1: Insufficient Effect Size

**Probability:** Low  
**Impact:** High (gate failure blocks downstream work)  
**Mitigation:** Use validated NER tool (h-c1), increase sample size if initial N=100 underpowered  
**Contingency:** Collect larger sample (N=200) if p-value borderline (0.05 < p < 0.10)

### Risk 2: Entity Span Misalignment

**Probability:** Low  
**Impact:** Medium (noisy entropy measurements)  
**Mitigation:** Validate character-to-token mapping on 10 samples before full run  
**Contingency:** Manual alignment check for failed samples

### Risk 3: Model Availability

**Probability:** Low  
**Impact:** Medium (need fallback model)  
**Mitigation:** Test Llama-2-7B download before experiment start  
**Contingency:** Use GPT-2 if Llama-2 unavailable (expect weaker signal)

---

## Validation Checklist

Before experiment execution:

- [ ] h-c1 validation completed (NER tool validated)
- [ ] Llama-2-7B model downloaded and tested
- [ ] TruthfulQA dataset downloaded
- [ ] Entity-error/non-entity-error annotations available (N=100)
- [ ] spaCy en_core_web_lg loaded successfully
- [ ] Attention extraction tested on 1 sample (shape verification)
- [ ] Character-to-token mapping tested on 10 samples

During experiment execution:

- [ ] All 100 samples processed without error
- [ ] Entity spans correctly aligned (spot-check 10 samples)
- [ ] Entropy values in expected range (0.0-1.0)
- [ ] No NaN or inf values in entropy calculations

Post-execution validation:

- [ ] p-value < 0.05 (statistical significance)
- [ ] mean_entity < mean_non_entity (directional hypothesis)
- [ ] Cohen's d calculated and reported
- [ ] Visualization generated (violin plot, histograms)

---

## Output Specification

**Required Outputs:**
1. **Entropy scores:** CSV with columns [sample_id, error_type, entropy]
2. **Statistical results:** JSON with {p_value, mean_entity, mean_non_entity, cohens_d, pass}
3. **Visualization:** Violin plot (entity-error vs non-entity-error distributions)
4. **Validation report:** 04_validation.md with pass/fail determination

**File Locations:**
- Data: `./data/truthfulqa_entity_subset/`
- Results: `./docs/youra_research/h-e1/results/`
- Figures: `./docs/youra_research/h-e1/figures/`
- Validation: `./docs/youra_research/h-e1/04_validation.md`

---

## Traceability

| Specification | Source |
|--------------|--------|
| Dataset | Phase 2A research (TruthfulQA selection) |
| Model | Phase 2A research (Llama-2-7B selection) |
| NER Tool | h-c1 validation (spaCy en_core_web_lg, F1=0.96) |
| Metrics | Phase 2A research (attention entropy, t-test) |
| Success Criteria | Hypothesis statement (p < 0.05, directional) |
| Sample Size | Power analysis (N=100 for d=0.5, α=0.05) |

---

**Next Steps:**  
Phase 2C → Experiment design (concrete implementation specification)  
Phase 3 → Implementation planning (PRD, architecture, Archon tasks)

---

*Verification plan approved for Phase 2C continuation*  
*All specifications grounded in Phase 2A research findings*
