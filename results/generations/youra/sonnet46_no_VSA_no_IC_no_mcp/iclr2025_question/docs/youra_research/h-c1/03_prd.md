# Product Requirements Document: h-c1
# Cross-Benchmark Generalization of Four-Way AUROC Ranking (TruthfulQA)

**Hypothesis:** h-c1
**Type:** CONDITION
**Date:** 2026-08-25
**Status:** Phase 3 Implementation Planning
**Base Hypothesis:** h-m4

---

## 1. Executive Summary

This experiment tests whether the four-method uncertainty proxy ranking (SE >= SCG > TE > VC) generalizes from TriviaQA (H-M4) to TruthfulQA (adversarial yes/no questions, N=200). The primary gate condition is SE AUROC > TE AUROC on TruthfulQA, validating that the noise-filtering advantage of semantic entropy is domain-general rather than TriviaQA-specific.

The experiment is a controlled extension of H-M4: only the benchmark changes; all method implementations, models, and hyperparameters are identical. A full four-method inference pass is required (SE, SCG, TE, VC) on 200 TruthfulQA yes/no questions.

**Gate:** SHOULD_WORK — SE AUROC > TE AUROC on TruthfulQA (primary condition)

---

## 2. Problem Statement

H-M4 established the four-method AUROC ranking on TriviaQA (SE=0.286, TE=0.4381, VC=0.4463). Notably, the H-M4 gate FAILED: VC did not underperform TE. H-C1 asks whether the SE vs TE direction (SE > TE in uncertainty quality) holds under a qualitatively different benchmark — TruthfulQA adversarial misconceptions.

The core question: **Is the noise-filtering advantage of SE (NLI clustering) over TE (per-token entropy) robust across benchmark types, or is it TriviaQA-specific?**

Secondary: Is VC scale-degradation at 7B a model property (benchmark-agnostic) or a benchmark-specific effect?

---

## 3. Scope

### In Scope
- All four uncertainty methods: SE (DeBERTa NLI), SCG (BERTScore), TE (greedy logits), VC (Llama-2-7B-Chat)
- TruthfulQA yes/no subset: N=200, generation split, binary labels
- Full generation + inference: K=10 stochastic samples per question (Llama-2-7B-hf)
- VC inference: single greedy pass (Llama-2-7B-Chat)
- Bootstrap AUROC (1000 iterations, seed=42) for all four methods
- Cross-benchmark comparison figures: TriviaQA (H-M4) vs TruthfulQA (H-C1)
- All figures saved to `docs/youra_research/h-c1/figures/`

### Out of Scope
- Re-implementing SE/SCG/TE from scratch (reuse h-m4 code patterns; h-e2-v2 codebase)
- Fine-tuning or RLHF
- Models other than Llama-2-7B-hf and Llama-2-7B-Chat
- TriviaQA re-computation (H-M4 results are the comparison baseline)

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| Name | TruthfulQA (yes/no subset) |
| Source | HuggingFace: `load_dataset("truthful_qa", "generation")` |
| Split | generation split, filtered to yes/no questions |
| N | 200 (all yes/no questions; use seed=42 for reproducibility) |
| Labels | Binary EM — answer matches gold best_answer (yes/no normalization) |
| Download | Auto (HuggingFace datasets) — no manual step |

**Loading code:**
```python
from datasets import load_dataset

def load_truthfulqa_yesno(seed=42, max_n=200):
    """Load TruthfulQA yes/no subset. Returns (questions, gold_answers, labels_placeholder)."""
    dataset = load_dataset("truthful_qa", "generation")["validation"]

    # Filter for yes/no questions
    yesno_set = {"yes", "no"}
    yesno_examples = [
        ex for ex in dataset
        if ex.get("best_answer", "").strip().lower() in yesno_set
    ]

    # Sample with seed for reproducibility
    import random
    rng = random.Random(seed)
    if len(yesno_examples) > max_n:
        yesno_examples = rng.sample(yesno_examples, max_n)

    questions = [ex["question"] for ex in yesno_examples]
    gold_answers = [ex["best_answer"] for ex in yesno_examples]
    return questions, gold_answers
```

**Label computation:**
```python
def compute_em_label(generated_answer: str, gold_answer: str) -> int:
    """Binary EM: 1 if normalized generated answer matches normalized gold."""
    normalize = lambda s: s.strip().lower()
    return int(normalize(generated_answer) == normalize(gold_answer))
```

### 4.2 Preprocessing

- Filter generation split for yes/no questions (best_answer in {"yes", "no"})
- Sample N=200 with seed=42 (use all if fewer than 200)
- Tokenize with Llama-2 tokenizer (max_length=512, truncation=True)
- Binary label: `int(normalize(generated_answer) == normalize(gold_answer))`

### 4.3 Inherited Baselines (Cross-Benchmark Reference)

From H-M4 (TriviaQA, N=98):

| Method | AUROC | Source |
|--------|-------|--------|
| SE | 0.286 | H-M4 results.json |
| TE | 0.4381 | H-M4 results.json |
| VC | 0.4463 | H-M4 results.json |
| SCG | N/A | Not computed in H-M4 |

These baselines are used for cross-benchmark comparison figures only — not for gating H-C1.

---

## 5. Functional Requirements

### FR-1: Data Loading and Label Preparation

**Priority:** P0

- Load TruthfulQA generation split from HuggingFace
- Filter to yes/no questions, sample N=200 with seed=42
- Compute binary EM labels against gold best_answer (yes/no normalization)
- Validate: N >= 200 questions loaded; labels are binary {0, 1}

**Acceptance:** All N questions loaded; EM labels computed; N >= 200 assertion passes.

---

### FR-2: Llama-2-7B Generation (SE, SCG, TE)

**Priority:** P0

- Load Llama-2-7B-hf (`meta-llama/Llama-2-7b-hf`) in float16, device_map="auto"
- Stochastic generation: temperature=0.7, K=10 samples per question (for SE, SCG)
- Greedy generation: temperature=0.0 / do_sample=False (for TE logit extraction)
- Batch size: 8 questions for throughput
- max_new_tokens: 50 (short answer)

**Acceptance:** K=10 stochastic samples and greedy logits generated for all N questions; shapes verified.

---

### FR-3: Token Entropy (TE) Computation

**Priority:** P0

- Compute mean per-token Shannon entropy from greedy logits
- TE = mean(-sum(p * log(p + eps)) for each token position)
- Reuse `compute_te()` pattern from h-m4/h-e2-v2

**Acceptance:** TE scores [N] computed; values in reasonable range (>0).

---

### FR-4: Semantic Entropy (SE) Computation

**Priority:** P0

- NLI clustering with DeBERTa cross-encoder (`cross-encoder/nli-deberta-v3-small`)
- Cluster entropy: se = -sum(p * log(p + eps)) over cluster probabilities
- Reuse `compute_se()` pattern from h-e2-v2 codebase

**Acceptance:** SE scores [N] computed; all values >= 0.

---

### FR-5: SelfCheckGPT-BERTScore (SCG) Computation

**Priority:** P0

- BERTScore pairwise consistency across K=10 samples
- SCG uncertainty: `1.0 - mean_pairwise_bertscore(samples, rescale_with_baseline=True)`
- Library: `bert-score`, lang="en"

**Acceptance:** SCG scores [N] computed; values in [0, 1].

---

### FR-6: Verbalized Confidence (VC) Inference

**Priority:** P0

- Load Llama-2-7B-Chat (`meta-llama/Llama-2-7b-chat-hf`) in float16, device_map="auto"
- Apply same Llama-2-Chat [INST]...[/INST] prompt template as H-M4
- Greedy decoding, max_new_tokens=80
- 3-pattern regex confidence extraction (same as H-M4 `extract_confidence()`)
- VC uncertainty = 1.0 - confidence; fallback = 0.5

**Acceptance:** VC scores [N] computed; parse_rate >= 0.70 (TruthfulQA may be lower).

---

### FR-7: Bootstrap AUROC Computation (All Four Methods)

**Priority:** P0

- Bootstrap AUROC (1000 iterations, seed=42) for: SE, SCG, TE, VC
- Report: mean AUROC ± 95% CI for each method
- Gate evaluation: SE AUROC > TE AUROC (primary)
- Secondary: VC AUROC < TE AUROC; Tertiary: full ranking SE >= SCG > TE > VC

**Acceptance:** 4 AUROC values with CI computed; gate verdict logged (PASS/FAIL); ranking documented.

---

### FR-8: Gate Verification and Logging

**Priority:** P0

```python
gate_primary = auroc_se > auroc_te        # SE > TE (direction preserved)
gate_secondary = auroc_vc < auroc_te      # VC < TE (scale-degradation agnostic)
gate_tertiary = (auroc_se >= auroc_scg and auroc_scg > auroc_te and auroc_te > auroc_vc)

print(f"H-C1 TruthfulQA results: SE={auroc_se:.4f}, SCG={auroc_scg:.4f}, "
      f"TE={auroc_te:.4f}, VC={auroc_vc:.4f}")
print(f"Gate primary (SE>TE): {gate_primary}")
print(f"Gate secondary (VC<TE): {gate_secondary}")
print(f"Gate tertiary (full ranking): {gate_tertiary}")
```

**Acceptance:** Gate fields populated in results.json; mechanism log message printed.

---

### FR-9: Figure Generation

**Priority:** P1 (mandatory per experiment brief)

All figures saved to `docs/youra_research/h-c1/figures/`:

| Figure | Type | Description |
|--------|------|-------------|
| `auroc_comparison.png` | Bar chart | SE, SCG, TE, VC AUROC on TruthfulQA with 95% CI error bars |
| `cross_benchmark_comparison.png` | Grouped bar | TriviaQA (H-M4) vs TruthfulQA (H-C1) AUROC for all methods |
| `rank_ordering.png` | Point + CI | Method ranking with CI overlap analysis |
| `vc_confidence_distribution.png` | Histogram | VC score distribution on TruthfulQA vs TriviaQA |
| `bootstrap_distributions.png` | Violin | Bootstrap AUROC distributions per method |

**Acceptance:** All 5 figures generated and saved.

---

### FR-10: Results Persistence

**Priority:** P0

Save to `docs/youra_research/h-c1/results.json`:
```json
{
  "hypothesis": "h-c1",
  "n_questions": 200,
  "benchmark": "truthfulqa_yesno",
  "auroc_se": <float>, "auroc_se_ci": [<lower>, <upper>],
  "auroc_scg": <float>, "auroc_scg_ci": [<lower>, <upper>],
  "auroc_te": <float>, "auroc_te_ci": [<lower>, <upper>],
  "auroc_vc": <float>, "auroc_vc_ci": [<lower>, <upper>],
  "gate_primary": <bool>,
  "gate_secondary": <bool>,
  "gate_tertiary": <bool>,
  "gate_passed": <bool>,
  "ranking": "<string>",
  "parse_rate_vc": <float>,
  "seed": 42,
  "hm4_baselines": {
    "auroc_se": 0.286, "auroc_te": 0.4381, "auroc_vc": 0.4463, "n": 98
  }
}
```

**Acceptance:** results.json created; all gate fields populated; H-M4 baselines recorded for cross-benchmark comparison.

---

### FR-11: Ablation — Sample Size Sensitivity

**Priority:** P2

- Re-compute AUROC on full yes/no subset (all N, not capped at 200)
- Compare AUROC estimates: N=200 vs N_full
- Report: CI width comparison; check if ranking changes

**Acceptance:** Ablation AUROC values computed and logged.

---

### FR-12: Ablation — VC Prompt Format Sensitivity

**Priority:** P2

- Test alternative VC prompt for TruthfulQA-specific yes/no format if standard H-M4 prompt yields degenerate VC (parse_rate < 0.70)
- Alternative: `"Is this statement true or false? {question} Confidence (0-100%):"`

**Acceptance:** If triggered, alternative prompt AUROC reported and compared to standard.

---

## 6. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Reproducibility | Seed=42 fixed; all random ops seeded |
| Performance | 200 questions × K=10 × 2 models; ~3-4 hours GPU (single A100) |
| Precision | float16 for all model loading |
| Memory | ~14GB VRAM peak (Llama-2-7B models in float16); models loaded sequentially if needed |
| Compatibility | Python 3.10+, transformers>=4.31, datasets>=2.14, sklearn, bert-score |

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
transformers>=4.31.0
datasets>=2.14.0
scikit-learn>=1.3.0
numpy>=1.24.0
matplotlib>=3.7.0
scipy>=1.11.0
tqdm>=4.65.0
bert-score>=0.3.13
```

### 7.2 External Model Access

- HuggingFace Hub access required for:
  - `meta-llama/Llama-2-7b-hf`
  - `meta-llama/Llama-2-7b-chat-hf`
  - `cross-encoder/nli-deberta-v3-small`
- HuggingFace token with Llama-2 access granted
- Dataset: `truthful_qa` (public, no token needed)

### 7.3 Internal Dependencies

- H-M4 code patterns: `docs/youra_research/h-m4/code/` (VC elicitation, regex extraction)
- H-M4 results: `docs/youra_research/h-m4/results.json` (TriviaQA baselines for comparison)
- h-e2-v2 code patterns: SE/SCG/TE pipeline (generation, NLI clustering, BERTScore)
- Bootstrap AUROC: reuse pattern from h-m2/code/evaluate.py or implement inline

---

## 8. Success Criteria

| Criterion | Threshold | Status |
|-----------|-----------|--------|
| SE AUROC > TE AUROC | Required (primary gate) | Gate condition |
| VC AUROC < TE AUROC | Informative (secondary) | Not gate-blocking |
| Full ranking SE>=SCG>TE>VC | Informative (tertiary) | Not gate-blocking |
| parse_rate_vc >= 0.70 | Required | Mechanism activation |
| N >= 200 questions | Required | Dataset validation |
| All 5 figures generated | Required | Visualization |
| results.json saved | Required | Persistence |

**Gate:** SHOULD_WORK — primary condition (SE > TE) must hold for PASS.

---

## 9. Risk Assessment

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| SE AUROC <= TE AUROC on TruthfulQA | Medium | Adversarial benchmark may compress AUROC gaps; log narrowing scope claim |
| Low VC parse rate (<70%) | Medium | Alternative prompt format (FR-12 ablation); log degenerate VC |
| VC AUROC > TE AUROC (repeated) | High (given H-M4) | Expected; document as consistent finding |
| OOM with two 7B models | Low | Load Llama-2-7B-Chat only after 7B-hf computation; sequential loading |
| TruthfulQA yes/no subset < 200 | Low | Use all available; document actual N |

---

*PRD generated for Phase 3 implementation planning. All specifications grounded in 02c_experiment_brief.md.*
